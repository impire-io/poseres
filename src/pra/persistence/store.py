"""SnapshotStore seam (Doc 06 §3.1/§4.1, feature 003 research R5).

Stores are durable and treat blobs as opaque — they never parse frame contents.
Atomicity (FR-004): the filesystem backend writes the blob to a temporary name,
commits it with ``os.replace``, and only then commits the small metadata sidecar
— the sidecar is the commit marker, so ``read``/``list`` can never observe a
partially written snapshot. The event-log and pose-index seams of Doc 06 §4.2
are deliberately NOT implemented (and must never be collapsed into this store).
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Protocol, runtime_checkable

__all__ = ["SnapshotStore", "FileSnapshotStore", "InMemorySnapshotStore", "snapshot_id_for"]

REQUIRED_METADATA = ("timestamp", "step", "cycle", "population", "format_version")


def snapshot_id_for(metadata: dict) -> str:
    """Unique per safe point and sortable (newest = greatest step, then cycle)."""
    return f"snap-{int(metadata['step']):012d}-{int(metadata['cycle']):05d}"


def _check_metadata(metadata: dict) -> None:
    missing = [k for k in REQUIRED_METADATA if k not in metadata]
    if missing:
        raise ValueError(f"snapshot metadata missing required fields: {missing}")


@runtime_checkable
class SnapshotStore(Protocol):
    def write(self, blob: bytes, metadata: dict) -> str: ...
    def read(self, snapshot_id: str) -> bytes: ...
    def list(self) -> list[tuple[str, dict]]: ...  # newest first
    def delete(self, snapshot_id: str) -> None: ...


class FileSnapshotStore:
    """Durable filesystem backend: ``<id>.npz`` blob + ``<id>.json`` metadata
    (the metadata file is the commit marker; blob is committed first)."""

    def __init__(self, directory: str | Path):
        self._dir = Path(directory)
        self._dir.mkdir(parents=True, exist_ok=True)

    def write(self, blob: bytes, metadata: dict) -> str:
        _check_metadata(metadata)
        snapshot_id = snapshot_id_for(metadata)
        blob_path = self._dir / f"{snapshot_id}.npz"
        meta_path = self._dir / f"{snapshot_id}.json"
        tmp_blob = self._dir / f".{snapshot_id}.npz.tmp"
        tmp_meta = self._dir / f".{snapshot_id}.json.tmp"
        tmp_blob.write_bytes(blob)
        os.replace(tmp_blob, blob_path)  # blob committed, still invisible to list()
        tmp_meta.write_text(json.dumps(metadata, sort_keys=True))
        os.replace(tmp_meta, meta_path)  # commit marker: snapshot now visible
        return snapshot_id

    def read(self, snapshot_id: str) -> bytes:
        if not (self._dir / f"{snapshot_id}.json").exists():
            raise KeyError(f"no committed snapshot {snapshot_id!r}")
        return (self._dir / f"{snapshot_id}.npz").read_bytes()

    def list(self) -> list[tuple[str, dict]]:
        out = []
        for meta_path in self._dir.glob("snap-*.json"):
            snapshot_id = meta_path.stem
            if (self._dir / f"{snapshot_id}.npz").exists():
                out.append((snapshot_id, json.loads(meta_path.read_text())))
        out.sort(key=lambda pair: pair[0], reverse=True)  # id is step-sortable
        return out

    def delete(self, snapshot_id: str) -> None:
        # remove the commit marker first so the snapshot is never half-visible
        (self._dir / f"{snapshot_id}.json").unlink(missing_ok=True)
        (self._dir / f"{snapshot_id}.npz").unlink(missing_ok=True)


class InMemorySnapshotStore:
    """Dict-backed substitute (contract tests, embedding)."""

    def __init__(self) -> None:
        self._items: dict[str, tuple[bytes, dict]] = {}

    def write(self, blob: bytes, metadata: dict) -> str:
        _check_metadata(metadata)
        snapshot_id = snapshot_id_for(metadata)
        self._items[snapshot_id] = (bytes(blob), dict(metadata))
        return snapshot_id

    def read(self, snapshot_id: str) -> bytes:
        return self._items[snapshot_id][0]

    def list(self) -> list[tuple[str, dict]]:
        return sorted(
            ((sid, dict(meta)) for sid, (_, meta) in self._items.items()),
            key=lambda pair: pair[0],
            reverse=True,
        )

    def delete(self, snapshot_id: str) -> None:
        self._items.pop(snapshot_id, None)
