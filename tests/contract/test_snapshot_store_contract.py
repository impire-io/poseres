"""T010 — SnapshotStore seam: substitutability, shared semantics, opacity."""

from __future__ import annotations

import pytest

from pra.config import Config
from pra.core.engine import Engine
from pra.persistence.snapshot import FORMAT_VERSION
from pra.persistence.store import FileSnapshotStore, InMemorySnapshotStore, SnapshotStore


def _metadata(step, cycle):
    return {
        "timestamp": 1.0,
        "step": step,
        "cycle": cycle,
        "population": 3,
        "format_version": FORMAT_VERSION,
    }


@pytest.fixture(params=["memory", "file"])
def store(request, tmp_path):
    return InMemorySnapshotStore() if request.param == "memory" else FileSnapshotStore(tmp_path)


def test_both_backends_satisfy_identical_semantics(store):
    assert isinstance(store, SnapshotStore)
    id1 = store.write(b"one", _metadata(10, 1))
    id2 = store.write(b"two", _metadata(20, 2))
    assert [i for i, _ in store.list()] == [id2, id1]  # newest first
    assert store.read(id1) == b"one"  # blobs opaque: bytes back verbatim
    store.delete(id2)
    assert [i for i, _ in store.list()] == [id1]


def test_engine_accepts_a_substitute_store_unchanged():
    cfg = Config(
        warmup_episodes=3,
        n_cycles=2,
        episodes_per_cycle=1,
        steps_per_episode=10,
        horizon_checkpoints=(1, 2),
        snapshot_every_n_cycles=1,
    )

    class RecordingStore(InMemorySnapshotStore):
        writes = 0

        def write(self, blob, metadata):
            RecordingStore.writes += 1
            return super().write(blob, metadata)

    substitute = RecordingStore()
    baseline = Engine(cfg).run(1)
    with_store = Engine(cfg, snapshot_store=substitute).run(1)
    assert RecordingStore.writes == 2  # one per cycle
    # taking snapshots perturbs nothing: summaries identical
    assert with_store.serialize() == baseline.serialize()
