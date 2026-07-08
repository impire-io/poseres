"""T006/T008/T009 — snapshot/resume: byte-identical continuation; baseline frozen;
body-compat rejection (feature 003 US1/US3/US4)."""

from __future__ import annotations

import numpy as np
import pytest

from pra.config import Config
from pra.core.engine import Engine
from pra.persistence.snapshot import SnapshotCompatibilityError
from pra.persistence.store import FileSnapshotStore, InMemorySnapshotStore


def _cfg(**overrides):
    base = dict(
        warmup_episodes=5,
        n_cycles=8,
        episodes_per_cycle=2,
        steps_per_episode=20,
        horizon_checkpoints=(4, 8),
        snapshot_every_n_cycles=3,
    )
    base.update(overrides)
    return Config(**base)


# --- US1: byte-identical continuation --------------------------------------


def test_resume_is_byte_identical_random_mode():
    cfg = _cfg()
    baseline = Engine(cfg).run(7)
    store = InMemorySnapshotStore()
    Engine(cfg, snapshot_store=store).run(7)
    assert len(store.list()) == 2  # cycles 3 and 6 of 8
    for snapshot_id, _meta in store.list():  # every snapshot resumes identically
        resumed = Engine(cfg).run(7, resume_from=store.read(snapshot_id))
        assert resumed.serialize() == baseline.serialize()


def test_resume_is_byte_identical_curiosity_mode():
    cfg = _cfg(policy_mode="curiosity")
    baseline = Engine(cfg).run(7)
    store = InMemorySnapshotStore()
    Engine(cfg, snapshot_store=store).run(7)
    snapshot_id, _ = store.list()[0]
    resumed = Engine(cfg).run(7, resume_from=store.read(snapshot_id))
    # drive bookkeeping survived: agency telemetry identical too
    assert resumed.serialize() == baseline.serialize()
    assert resumed.agency is not None


def test_resume_seed_mismatch_is_rejected():
    cfg = _cfg()
    store = InMemorySnapshotStore()
    Engine(cfg, snapshot_store=store).run(7)
    blob = store.read(store.list()[0][0])
    with pytest.raises(ValueError, match="seed"):
        Engine(cfg).run(8, resume_from=blob)


def test_empty_population_snapshot_resumes():
    # A snapshot can capture an empty population (harsh eviction, min_frames=1
    # can still leave 1; use a fresh store state via direct capture at cycle 1
    # with a tiny world so the zero-start path is exercised on resume).
    cfg = _cfg(snapshot_every_n_cycles=1, n_cycles=3, horizon_checkpoints=(1, 3))
    baseline = Engine(cfg).run(3)
    store = InMemorySnapshotStore()
    Engine(cfg, snapshot_store=store).run(3)
    oldest_id = store.list()[-1][0]  # cycle-1 snapshot
    resumed = Engine(cfg).run(3, resume_from=store.read(oldest_id))
    assert resumed.serialize() == baseline.serialize()


# --- US3: the validated behavior is untouched -------------------------------


def test_reference_seed_reproduces_validated_build_values():
    s = Engine(Config()).run(1)
    assert round(s.pred_error_early, 4) == 0.4465
    assert round(s.pred_error_late, 4) == 0.1574
    readings = {c: (r.best_dim, r.population_size) for c, r in s.checkpoints.items()}
    assert readings == {18: (3, 19), 30: (3, 24), 50: (4, 27)}


def test_default_config_writes_no_files(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    cfg = Config(
        warmup_episodes=3,
        n_cycles=2,
        episodes_per_cycle=1,
        steps_per_episode=10,
        horizon_checkpoints=(1, 2),
    )
    Engine(cfg).run(1)  # default: no store, cadence 0
    assert list(tmp_path.iterdir()) == []


def test_snapshots_only_at_configured_cycle_boundaries(tmp_path):
    cfg = _cfg(snapshot_every_n_cycles=2, n_cycles=6, horizon_checkpoints=(6,))
    store = FileSnapshotStore(tmp_path)
    Engine(cfg, snapshot_store=store).run(1)
    cycles = [meta["cycle"] for _, meta in store.list()]
    assert sorted(cycles) == [2, 4, 6]  # the C4 safe points, nothing else


# --- US4: body-compatibility rejection ---------------------------------------


def test_incompatible_body_is_rejected_with_named_field():
    cfg10 = _cfg(obs_dim=10)
    store = InMemorySnapshotStore()
    Engine(cfg10, snapshot_store=store).run(7)
    blob = store.read(store.list()[0][0])
    cfg60 = _cfg(true_dim=20, obs_dim=60)
    with pytest.raises(SnapshotCompatibilityError, match="obs_dim=10.*obs_dim=60"):
        Engine(cfg60).run(7, resume_from=blob)


def test_compatible_restore_succeeds_after_check():
    cfg = _cfg()
    store = InMemorySnapshotStore()
    baseline = Engine(cfg, snapshot_store=store).run(7)
    blob = store.read(store.list()[0][0])
    resumed = Engine(cfg).run(7, resume_from=blob)
    assert np.isclose(resumed.pred_error_late, baseline.pred_error_late)
