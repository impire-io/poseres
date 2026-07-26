"""Feature 037 — shareable brains: the roadmap Phase D exit criterion.

A snapshot published by one person loads and runs for another —
verified end to end through the ``pra-brain`` CLI with the repo's
resume-exactness pattern (byte-identical serialized summary). Plus the
trust checks: tampered blob refused, unknown versions refused, inspect
answers from the manifest alone (proven on a corrupt-blob file).
"""

from __future__ import annotations

import json
import zipfile

import pytest

import pra
from pra.config import Config
from pra.core.engine import Engine
from pra.persistence import brain_cli
from pra.persistence.portable import (
    PortableIntegrityError,
    PortableVersionError,
    export_brain,
    import_brain,
    inspect_brain,
)
from pra.persistence.store import FileSnapshotStore

SMALL = dict(
    warmup_episodes=2,
    n_cycles=3,
    episodes_per_cycle=2,
    steps_per_episode=10,
    horizon_checkpoints=(1, 3),
    snapshot_every_n_cycles=2,
)
CREATED_AT = "2026-07-27T00:00:00+00:00"


def _cfg(**overrides) -> Config:
    base = dict(SMALL)
    base.update(overrides)
    return Config(**base)


def _person_a_store(tmp_path, seed=7):
    """Run person A's engine with a file store; return (store, uninterrupted)."""
    cfg = _cfg()
    uninterrupted = Engine(cfg).run(seed).serialize()
    store = FileSnapshotStore(tmp_path / "person-a")
    Engine(cfg, snapshot_store=store).run(seed)
    return store, uninterrupted


def _artifact(tmp_path, note="a brain"):
    """One exported artifact + its manifest + the source store facts."""
    store, uninterrupted = _person_a_store(tmp_path)
    path = tmp_path / "shared.brain"
    manifest = export_brain(path, store=store, note=note, created_at=CREATED_AT)
    return path, manifest, store, uninterrupted


def _rewrite(src, dst, mutate):
    """Copy a portable file with ``mutate(members)`` applied to its members."""
    with zipfile.ZipFile(src) as archive:
        members = {name: archive.read(name) for name in archive.namelist()}
    mutate(members)
    with zipfile.ZipFile(dst, "w") as archive:
        for name, data in members.items():
            archive.writestr(name, data)
    return dst


# --- US1/US3: the exit criterion, driven through the shipped CLI -------------


def test_published_brain_loads_and_runs_for_another_person(tmp_path, capsys):
    store_a, uninterrupted = _person_a_store(tmp_path)
    source_id, _ = store_a.list()[0]
    artifact = tmp_path / "rover.brain"

    # person A publishes the newest snapshot as one file
    code = brain_cli.main(
        ["export", "--store", str(tmp_path / "person-a"), "--out", str(artifact), "--note", "hi B"]
    )
    assert code == 0 and artifact.is_file()

    # person B imports it into their own, separate store directory ...
    store_b_dir = tmp_path / "person-b"
    assert brain_cli.main(["import", str(artifact), "--store", str(store_b_dir)]) == 0
    store_b = FileSnapshotStore(store_b_dir)
    snapshot_id, _meta = store_b.list()[0]
    assert snapshot_id == source_id  # same snapshot, same id
    assert store_b.read(snapshot_id) == store_a.read(source_id)  # blob byte-untouched

    # ... and resumes through the existing resume path: byte-identical run
    resumed = Engine(_cfg()).run(7, resume_from=store_b.read(snapshot_id)).serialize()
    assert resumed == uninterrupted
    capsys.readouterr()  # keep CLI prints out of the test log


def test_library_export_import_round_trip_is_exact(tmp_path):
    path, manifest, store, uninterrupted = _artifact(tmp_path)
    blob, imported_manifest = import_brain(path)
    assert blob == store.read(store.list()[0][0])
    assert imported_manifest == manifest
    resumed = Engine(_cfg()).run(7, resume_from=blob).serialize()
    assert resumed == uninterrupted


def test_blob_and_store_exports_are_byte_identical(tmp_path):
    # the artifact's bytes are a pure function of (blob, manifest)
    store, _ = _person_a_store(tmp_path)
    blob = store.read(store.list()[0][0])
    a, b = tmp_path / "a.brain", tmp_path / "b.brain"
    export_brain(a, store=store, note="n", created_at=CREATED_AT)
    export_brain(b, blob=blob, note="n", created_at=CREATED_AT)
    assert a.read_bytes() == b.read_bytes()


def test_export_argument_misuse_is_refused(tmp_path):
    store, _ = _person_a_store(tmp_path)
    blob = store.read(store.list()[0][0])
    with pytest.raises(ValueError, match="exactly one"):
        export_brain(tmp_path / "x.brain", note="", created_at=CREATED_AT)
    with pytest.raises(ValueError, match="exactly one"):
        export_brain(tmp_path / "x.brain", blob=blob, store=store, created_at=CREATED_AT)
    with pytest.raises(ValueError, match="snapshot_id"):
        export_brain(tmp_path / "x.brain", blob=blob, snapshot_id="snap-x", created_at=CREATED_AT)
    with pytest.raises(ValueError, match="no committed snapshot"):
        export_brain(
            tmp_path / "x.brain", store=FileSnapshotStore(tmp_path / "empty"), created_at=CREATED_AT
        )


# --- US2: a recipient can trust what they load -------------------------------


def test_manifest_states_the_facts(tmp_path):
    path, manifest, store, _ = _artifact(tmp_path, note="rover, 3 cycles, seed 7")
    _snapshot_id, meta = store.list()[0]
    assert inspect_brain(path) == manifest
    assert manifest["step"] == meta["step"]
    assert manifest["cycle"] == meta["cycle"]
    assert manifest["population"] == meta["population"]
    assert manifest["snapshot_format_version"] == meta["format_version"]
    assert (manifest["obs_dim"], manifest["n_actions"]) == (Config().obs_dim, Config().n_actions)
    assert manifest["pra_version"] == pra.__version__
    assert manifest["note"] == "rover, 3 cycles, seed 7"
    assert manifest["created_at"] == CREATED_AT


def test_tampered_blob_is_refused_and_nothing_written(tmp_path, capsys):
    path, manifest, _store, _ = _artifact(tmp_path)

    def flip_a_byte(members):
        blob = bytearray(members["snapshot.bin"])
        blob[len(blob) // 2] ^= 0xFF
        members["snapshot.bin"] = bytes(blob)

    tampered = _rewrite(path, tmp_path / "tampered.brain", flip_a_byte)
    with pytest.raises(PortableIntegrityError, match="sha256 mismatch"):
        import_brain(tampered)
    # inspect never reads the blob: it still answers on the damaged file
    assert inspect_brain(tampered) == manifest

    # the CLI refuses loudly and the target store stays empty
    target = tmp_path / "person-b"
    assert brain_cli.main(["import", str(tampered), "--store", str(target)]) == 1
    assert "sha256 mismatch" in capsys.readouterr().err
    assert FileSnapshotStore(target).list() == []


def test_unknown_portable_format_version_is_refused(tmp_path):
    path, _manifest, _store, _ = _artifact(tmp_path)

    def future_container(members):
        manifest = json.loads(members["manifest.json"])
        manifest["portable_format_version"] = "999"
        members["manifest.json"] = json.dumps(manifest, sort_keys=True)

    alien = _rewrite(path, tmp_path / "alien.brain", future_container)
    with pytest.raises(PortableVersionError, match="portable format version '999'"):
        import_brain(alien)
    with pytest.raises(PortableVersionError, match="portable format version '999'"):
        inspect_brain(alien)  # an unknown container is unreadable, even for inspect


def test_unsupported_snapshot_format_version_is_refused(tmp_path):
    path, _manifest, _store, _ = _artifact(tmp_path)

    def future_snapshot(members):
        manifest = json.loads(members["manifest.json"])
        manifest["snapshot_format_version"] = "999"
        members["manifest.json"] = json.dumps(manifest, sort_keys=True)

    future = _rewrite(path, tmp_path / "future.brain", future_snapshot)
    with pytest.raises(PortableVersionError, match="snapshot format version '999'"):
        import_brain(future)
    # inspect's whole point: you may still read what the file claims to be
    assert inspect_brain(future)["snapshot_format_version"] == "999"


def test_damaged_containers_are_refused(tmp_path):
    path, _manifest, _store, _ = _artifact(tmp_path)
    not_a_zip = tmp_path / "noise.brain"
    not_a_zip.write_bytes(b"this is not a zip archive")
    with pytest.raises(PortableIntegrityError, match="not a zip"):
        import_brain(not_a_zip)
    with pytest.raises(PortableIntegrityError, match="not a zip"):
        inspect_brain(not_a_zip)

    def drop_blob(members):
        del members["snapshot.bin"]

    headless = _rewrite(path, tmp_path / "headless.brain", drop_blob)
    with pytest.raises(PortableIntegrityError, match="missing 'snapshot.bin'"):
        import_brain(headless)

    def drop_manifest(members):
        del members["manifest.json"]

    blind = _rewrite(path, tmp_path / "blind.brain", drop_manifest)
    with pytest.raises(PortableIntegrityError, match="missing 'manifest.json'"):
        inspect_brain(blind)


# --- US3: the CLI shell ------------------------------------------------------


def test_cli_inspect_prints_the_manifest_as_json(tmp_path, capsys):
    path, manifest, _store, _ = _artifact(tmp_path)
    assert brain_cli.main(["inspect", str(path)]) == 0
    assert json.loads(capsys.readouterr().out) == manifest


def test_cli_export_injects_created_at_and_reports(tmp_path, capsys):
    store, _ = _person_a_store(tmp_path)
    out = tmp_path / "cli.brain"
    assert brain_cli.main(["export", "--store", str(tmp_path / "person-a"), "--out", str(out)]) == 0
    manifest = inspect_brain(out)
    assert manifest["created_at"]  # the CLI injects the clock; the library never does
    step, cycle = manifest["step"], manifest["cycle"]
    assert f"step {step} / cycle {cycle}" in capsys.readouterr().out


def test_cli_export_missing_snapshot_id_fails_loudly(tmp_path, capsys):
    _store, _ = _person_a_store(tmp_path)
    code = brain_cli.main(
        [
            "export",
            "--store",
            str(tmp_path / "person-a"),
            "--out",
            str(tmp_path / "x.brain"),
            "--snapshot",
            "snap-does-not-exist",
        ]
    )
    assert code == 1
    assert "snap-does-not-exist" in capsys.readouterr().err
