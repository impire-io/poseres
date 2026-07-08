"""T007 — blob round-trip fidelity, versioning, store semantics (feature 003 US2)."""

from __future__ import annotations

import io
import json

import numpy as np
import pytest

from pra.config import Config
from pra.core.frame import FrameStore
from pra.persistence.snapshot import (
    FORMAT_VERSION,
    SnapshotVersionError,
    SystemState,
    decode,
    encode,
)
from pra.persistence.store import FileSnapshotStore, InMemorySnapshotStore


def _state(agency=None) -> SystemState:
    cfg = Config()
    store = FrameStore(cfg, np.random.default_rng(3))
    for d in (2, 3, 3):
        store.birth(dim=d, ema_init=1.0)
    rng = np.random.default_rng(9)
    rng.random(5)  # advance so the state is non-initial
    return SystemState(
        config=cfg,
        seed=3,
        scoring_mode="predictive",
        policy_mode="random" if agency is None else "curiosity",
        cycles_done=4,
        obs_steps=123,
        obs_after_warm=80,
        lost_after_warm=1,
        pop_sum=456,
        warmed=True,
        pred_error_early=0.5321,
        map_fractions=[0.5, 0.75, 1.0],
        pred_errors=[0.9, 0.8, 0.7],
        population_by_cycle=[2, 3, 3, 3],
        checkpoints={4: (3, 3)},
        frame_store=store.state_dict(),
        agency=agency,
        rng_state=rng.bit_generator.state,
    )


def test_round_trip_is_exact():
    original = _state()
    restored = decode(encode(original))
    assert restored.config == original.config
    assert restored.seed == original.seed
    assert restored.cycles_done == 4
    assert restored.pred_error_early == original.pred_error_early
    assert restored.map_fractions == original.map_fractions
    assert restored.checkpoints == {4: (3, 3)}
    assert restored.rng_state == original.rng_state
    assert restored.frame_store["next_id"] == original.frame_store["next_id"]
    for dim, tensors in original.frame_store["groups"].items():
        for name, arr in tensors.items():
            assert np.array_equal(restored.frame_store["groups"][dim][name], arr), (dim, name)


def test_round_trip_preserves_agency_bookkeeping():
    agency = {
        "pred_error_history": [0.4, 0.3],
        "observation_memory": [np.ones(10), np.zeros(10)],
        "values": [0.9, 0.8],
        "lp_terms": [0.0, 0.1],
        "novelty_terms": [1.0, 0.5],
        "directed_steps": 7,
        "total_steps": 20,
    }
    restored = decode(encode(_state(agency=agency))).agency
    assert restored["pred_error_history"] == [0.4, 0.3]
    assert np.array_equal(restored["observation_memory"][0], np.ones(10))
    assert restored["directed_steps"] == 7 and restored["total_steps"] == 20


def test_unsupported_version_is_rejected_by_name():
    blob = encode(_state())
    # doctor the version inside the archive's meta entry
    with np.load(io.BytesIO(blob), allow_pickle=False) as archive:
        entries = {k: archive[k] for k in archive.files}
    meta = json.loads(str(entries["meta"]))
    meta["format_version"] = "99"
    entries["meta"] = np.array(json.dumps(meta))
    buf = io.BytesIO()
    np.savez_compressed(buf, **entries)
    with pytest.raises(SnapshotVersionError, match="'99'"):
        decode(buf.getvalue())


def _metadata(step=100, cycle=2):
    return {
        "timestamp": 1234.5,
        "step": step,
        "cycle": cycle,
        "population": 5,
        "format_version": FORMAT_VERSION,
    }


def test_file_store_atomicity_and_semantics(tmp_path):
    store = FileSnapshotStore(tmp_path)
    # a stray temp file (simulated interrupted write) is never listed or readable
    (tmp_path / ".snap-000000000001-00001.npz.tmp").write_bytes(b"partial")
    # a blob without its commit marker is invisible too
    (tmp_path / "snap-000000000002-00001.npz").write_bytes(b"uncommitted")
    assert store.list() == []
    with pytest.raises(KeyError):
        store.read("snap-000000000002-00001")

    id_a = store.write(b"blob-a", _metadata(step=100, cycle=2))
    id_b = store.write(b"blob-b", _metadata(step=200, cycle=4))
    listed = store.list()
    assert [i for i, _ in listed] == [id_b, id_a]  # newest first
    meta = listed[0][1]
    for field in ("timestamp", "step", "cycle", "population", "format_version"):
        assert field in meta
    assert store.read(id_a) == b"blob-a"

    store.delete(id_a)
    assert [i for i, _ in store.list()] == [id_b]  # exactly one removed
    with pytest.raises(KeyError):
        store.read(id_a)


def test_metadata_missing_fields_rejected(tmp_path):
    store = InMemorySnapshotStore()
    with pytest.raises(ValueError, match="missing required"):
        store.write(b"x", {"step": 1, "cycle": 1})
