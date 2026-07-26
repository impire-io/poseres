"""Portable brain artifacts (feature 037, Doc 0006 wrap): one shareable file.

A *portable brain* is a snapshot a person can publish and another can
load: a plain zip archive with exactly two members —

* ``manifest.json`` — UTF-8 JSON, sorted keys, the facts about the
  enclosed snapshot (:data:`MANIFEST_KEYS`): the container's own format
  version, the sha256 of the blob, the snapshot format version, the
  exporting pra version, the body dimensions (``obs_dim``/``n_actions``),
  the run position (``step``/``cycle``/``population``), a free-text
  provenance ``note``, and a ``created_at`` string injected by the caller
  (this module never reads the clock).
* ``snapshot.bin`` — the snapshot blob exactly as the
  :class:`~pra.persistence.store.SnapshotStore` holds it, byte-untouched.

Constitution I: this module WRAPS the existing wire format — manifest
facts are derived through :func:`pra.persistence.snapshot.decode`, the
blob is never re-encoded, and ``FORMAT_VERSION`` is read, not redefined.
Member timestamps are pinned to the zip epoch, so the artifact's bytes
are a pure function of (blob, manifest): same brain + same manifest =
byte-identical file.

Import refuses loudly — :class:`PortableVersionError` for an unknown
container version or an unsupported snapshot format version,
:class:`PortableIntegrityError` for a damaged archive or a sha256
mismatch — and never writes anything. Inspect reads only the manifest
member and never deserializes the brain (so it answers on damaged files
too); it refuses only an unknown *container* version. The sha256 is an
integrity check against damage, not a signature against a forger.
"""

from __future__ import annotations

import hashlib
import json
import os
import zipfile
from pathlib import Path

from pra.persistence.snapshot import FORMAT_VERSION, decode
from pra.persistence.store import SnapshotStore

__all__ = [
    "PORTABLE_FORMAT_VERSION",
    "MANIFEST_KEYS",
    "PortableIntegrityError",
    "PortableVersionError",
    "export_brain",
    "import_brain",
    "inspect_brain",
]

PORTABLE_FORMAT_VERSION = "1"

MANIFEST_KEYS = (
    "portable_format_version",
    "blob_sha256",
    "snapshot_format_version",
    "pra_version",
    "obs_dim",
    "n_actions",
    "step",
    "cycle",
    "population",
    "note",
    "created_at",
)

_MANIFEST_MEMBER = "manifest.json"
_BLOB_MEMBER = "snapshot.bin"
# Pinned member timestamp (the zip epoch): the archive's bytes depend only
# on its contents, never on when it was written.
_ZIP_EPOCH = (1980, 1, 1, 0, 0, 0)


class PortableIntegrityError(ValueError):
    """The artifact is damaged: bad archive, missing member, or sha256 mismatch."""


class PortableVersionError(ValueError):
    """The artifact's container or snapshot format version is not supported."""


def export_brain(
    path: str | Path,
    *,
    blob: bytes | None = None,
    store: SnapshotStore | None = None,
    snapshot_id: str | None = None,
    note: str = "",
    created_at: str,
) -> dict:
    """Publish one snapshot as a portable file; return its manifest.

    Exactly one of ``blob`` or ``store`` must be given; with ``store``,
    ``snapshot_id`` selects the snapshot (default: newest). The blob is
    decoded through the existing snapshot decoder to derive the manifest
    facts — export cannot publish a blob this library could not load —
    and is written into the archive byte-untouched. ``created_at`` is
    the caller's timestamp string (e.g. ISO 8601 UTC).
    """
    if (blob is None) == (store is None):
        raise ValueError("export_brain needs exactly one of blob= or store=")
    if store is not None:
        if snapshot_id is None:
            listed = store.list()
            if not listed:
                raise ValueError("the store has no committed snapshot to export")
            snapshot_id = listed[0][0]  # newest first (store contract)
        blob = store.read(snapshot_id)
    elif snapshot_id is not None:
        raise ValueError("snapshot_id= is only meaningful with store=")
    assert blob is not None

    # The wrap, not a reimplementation: the existing decoder both proves
    # the blob is a supported, well-formed snapshot and yields the facts.
    state = decode(blob)
    import pra  # local: keep module import free of package-version lookup

    manifest = {
        "portable_format_version": PORTABLE_FORMAT_VERSION,
        "blob_sha256": hashlib.sha256(blob).hexdigest(),
        "snapshot_format_version": FORMAT_VERSION,  # proven by the decode above
        "pra_version": pra.__version__,
        "obs_dim": int(state.frame_store["obs_dim"]),
        "n_actions": int(state.frame_store["n_actions"]),
        "step": int(state.obs_steps),
        "cycle": int(state.cycles_done),
        # appended at the same C4 safe point that wrote the snapshot, so it
        # equals the store metadata's population reading
        "population": int(state.population_by_cycle[-1]) if state.population_by_cycle else 0,
        "note": str(note),
        "created_at": str(created_at),
    }

    target = Path(path)
    tmp = target.with_name(f".{target.name}.tmp")
    with zipfile.ZipFile(tmp, "w", compression=zipfile.ZIP_STORED) as archive:
        archive.writestr(
            _member(_MANIFEST_MEMBER), json.dumps(manifest, sort_keys=True, indent=2) + "\n"
        )
        archive.writestr(_member(_BLOB_MEMBER), blob)
    os.replace(tmp, target)  # atomic: a partial artifact is never in place
    return manifest


def _member(name: str) -> zipfile.ZipInfo:
    """Deterministic member: epoch-pinned time, plain 0644 file mode."""
    info = zipfile.ZipInfo(name, date_time=_ZIP_EPOCH)
    info.external_attr = 0o644 << 16
    return info


def _read_manifest(archive: zipfile.ZipFile, path: Path) -> dict:
    try:
        raw = archive.read(_MANIFEST_MEMBER)
    except KeyError:
        raise PortableIntegrityError(
            f"{path} is not a portable brain: missing {_MANIFEST_MEMBER!r}"
        ) from None
    try:
        manifest = json.loads(raw)
    except ValueError as exc:
        raise PortableIntegrityError(f"{path}: {_MANIFEST_MEMBER} is not valid JSON") from exc
    version = manifest.get("portable_format_version")
    if version != PORTABLE_FORMAT_VERSION:
        raise PortableVersionError(
            f"{path}: unknown portable format version {version!r} "
            f"(supported: {PORTABLE_FORMAT_VERSION!r}) — refusing to interpret it"
        )
    missing = [key for key in MANIFEST_KEYS if key not in manifest]
    if missing:
        raise PortableIntegrityError(f"{path}: manifest is missing required keys {missing}")
    return manifest


def inspect_brain(path: str | Path) -> dict:
    """Return the manifest. Never reads — let alone deserializes — the brain."""
    path = Path(path)
    try:
        with zipfile.ZipFile(path) as archive:
            return _read_manifest(archive, path)
    except zipfile.BadZipFile as exc:
        raise PortableIntegrityError(f"{path} is not a portable brain (not a zip)") from exc


def import_brain(path: str | Path) -> tuple[bytes, dict]:
    """Verify and return ``(blob, manifest)``; refuse loudly, write nothing.

    Verification order: container format version, snapshot format
    version against this library's supported one, then the sha256 of the
    enclosed blob against the manifest. Only a fully verified blob is
    returned — byte-identical to what the publisher's store held.
    """
    path = Path(path)
    try:
        with zipfile.ZipFile(path) as archive:
            manifest = _read_manifest(archive, path)
            snap_version = manifest["snapshot_format_version"]
            if snap_version != FORMAT_VERSION:
                raise PortableVersionError(
                    f"{path}: snapshot format version {snap_version!r} is not supported "
                    f"by this library (supported: {FORMAT_VERSION!r}) — refusing to load"
                )
            try:
                blob = archive.read(_BLOB_MEMBER)
            except KeyError:
                raise PortableIntegrityError(
                    f"{path} is not a portable brain: missing {_BLOB_MEMBER!r}"
                ) from None
    except zipfile.BadZipFile as exc:
        raise PortableIntegrityError(f"{path} is not a portable brain (not a zip)") from exc
    digest = hashlib.sha256(blob).hexdigest()
    if digest != manifest["blob_sha256"]:
        raise PortableIntegrityError(
            f"{path}: blob sha256 mismatch — manifest says {manifest['blob_sha256']}, "
            f"the enclosed blob hashes to {digest}; the file is damaged or was "
            "tampered with — refusing to load"
        )
    return blob, manifest
