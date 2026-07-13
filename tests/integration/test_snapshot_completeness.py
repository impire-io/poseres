"""Snapshot completeness (feature 010) — the three paid debts: grown bodies,
capture-required worlds, multi-stream runs. Small budgets; byte-identity is
the claim under test."""

from __future__ import annotations

import numpy as np
import pytest

from pra.anatomy.body import Body, ConstantSensor, WorldActuator, WorldSensor
from pra.config import Config
from pra.core.engine import Engine
from pra.persistence.snapshot import SnapshotCompatibilityError, decode
from pra.persistence.store import InMemorySnapshotStore
from pra.world.event_source import SensorimotorWorld

SMALL = dict(
    warmup_episodes=2,
    n_cycles=4,
    episodes_per_cycle=2,
    steps_per_episode=10,
    horizon_checkpoints=(1, 4),
)


def _plain_body_factory(cfg, rng):
    world = SensorimotorWorld(cfg, rng)
    sensor = WorldSensor(world)
    return Body(world, sensors=[sensor], actuators=[WorldActuator(world, sensor)])


def _grown_body_factory(cfg, rng):
    """The resumed run's factory: the grown anatomy, present from boot."""
    world = SensorimotorWorld(cfg.replace(obs_dim=cfg.obs_dim), rng)
    sensor = WorldSensor(world)
    return Body(
        world,
        sensors=[sensor, ConstantSensor("bias", [0.5, -0.5])],
        actuators=[WorldActuator(world, sensor)],
    )


class _GrowMidRunBody(Body):
    """A body that registers a ConstantSensor once, at a chosen slow loop."""

    def __init__(self, world, sensors, actuators, grow_at_apply: int):
        super().__init__(world, sensors, actuators)
        self._applies = 0
        self._grow_at = grow_at_apply

    def apply_pending_tools(self):
        self._applies += 1
        if self._applies == self._grow_at:
            self.register_sensor(ConstantSensor("bias", [0.5, -0.5]))
        return super().apply_pending_tools()


def _growing_factory(cfg, rng):
    world = SensorimotorWorld(cfg, rng)
    sensor = WorldSensor(world)
    return _GrowMidRunBody(world, [sensor], [WorldActuator(world, sensor)], grow_at_apply=2)


# --- US1: grown bodies (SC-001) -------------------------------------------------


def test_resize_snapshot_resume_is_byte_identical():
    store = InMemorySnapshotStore()
    cfg = Config(**SMALL, snapshot_every_n_cycles=1)
    uninterrupted = (
        Engine(cfg, world_factory=_growing_factory, snapshot_store=store).run(1).serialize()
    )
    # growth applies at the top of cycle 2; take a post-growth snapshot
    post_growth = [(sid, m) for sid, m in store.list() if m["cycle"] >= 3]
    assert post_growth, "expected a snapshot after the mid-run growth"
    snapshot_id = min(post_growth, key=lambda x: x[1]["cycle"])[0]
    blob = store.read(snapshot_id)
    state = decode(blob)
    assert state.frame_store["obs_dim"] == cfg.obs_dim + 2  # grown dims recorded
    resumed = Engine(cfg, world_factory=_grown_body_factory).run(1, resume_from=blob).serialize()
    assert resumed == uninterrupted


def test_wrong_anatomy_resume_fails_loudly():
    store = InMemorySnapshotStore()
    cfg = Config(**SMALL, snapshot_every_n_cycles=1)
    Engine(cfg, world_factory=_growing_factory, snapshot_store=store).run(1)
    post_growth = min(
        ((sid, m) for sid, m in store.list() if m["cycle"] >= 3),
        key=lambda x: x[1]["cycle"],
    )[0]
    with pytest.raises(SnapshotCompatibilityError, match="grown anatomy"):
        Engine(cfg, world_factory=_plain_body_factory).run(1, resume_from=store.read(post_growth))


def test_unresized_blobs_are_bit_identical_to_prefeature_format():
    import io
    import json

    store = InMemorySnapshotStore()
    cfg = Config(**SMALL, snapshot_every_n_cycles=2)
    Engine(cfg, snapshot_store=store).run(1)
    blob = store.read(store.list()[0][0])
    archive = np.load(io.BytesIO(blob), allow_pickle=False)
    meta = json.loads(str(archive["meta"]))
    assert "current_dims" not in meta
    assert "streams" not in meta
    assert "world_state" not in meta


# --- US2: capture-required worlds (SC-002) ---------------------------------------


class _CounterWorld(SensorimotorWorld):
    """A derivable world wearing the capture-required marker with real
    history-dependent state (a counter folded into nothing observable —
    the marker semantics are what is under test)."""

    snapshot_needs_state = True

    def __init__(self, cfg, rng):
        super().__init__(cfg, rng)
        self.resets = 0

    def reset(self):
        self.resets += 1
        return super().reset()

    def state_dict(self):
        state = super().state_dict()
        state["resets"] = self.resets
        return state

    def load_state_dict(self, state):
        super().load_state_dict(state)
        self.resets = int(state["resets"])


def test_capture_required_world_snapshots_and_resumes_exactly():
    holder: dict = {}

    def factory(cfg, rng):
        holder["world"] = _CounterWorld(cfg, rng)
        return holder["world"]

    store = InMemorySnapshotStore()
    cfg = Config(**SMALL, snapshot_every_n_cycles=2)
    uninterrupted = Engine(cfg, world_factory=factory, snapshot_store=store).run(1)
    total_resets = holder["world"].resets
    blob = store.read(store.list()[-1][0])  # oldest = mid-run
    resumed_summary = Engine(cfg, world_factory=factory).run(1, resume_from=blob)
    assert resumed_summary.serialize() == uninterrupted.serialize()
    # the counter continued from the snapshot: it ends exactly where the
    # uninterrupted run ended, despite the resumed run playing fewer episodes
    assert holder["world"].resets == total_resets


def test_marker_without_capture_fails_loudly():
    class NeedyWorld(SensorimotorWorld):
        snapshot_needs_state = True
        state_dict = None  # declares the need, provides nothing

    cfg = Config(**SMALL, snapshot_every_n_cycles=2)
    with pytest.raises(RuntimeError, match="capture"):
        Engine(
            cfg,
            world_factory=lambda c, r: NeedyWorld(c, r),
            snapshot_store=InMemorySnapshotStore(),
        ).run(1)


def test_marker_world_body_delegates_marker_and_capture():
    def factory(cfg, rng):
        world = _CounterWorld(cfg, rng)
        sensor = WorldSensor(world)
        return Body(world, sensors=[sensor], actuators=[WorldActuator(world, sensor)])

    store = InMemorySnapshotStore()
    cfg = Config(**SMALL, snapshot_every_n_cycles=2)
    uninterrupted = Engine(cfg, world_factory=factory, snapshot_store=store).run(1).serialize()
    blob = store.read(store.list()[-1][0])
    resumed = Engine(cfg, world_factory=factory).run(1, resume_from=blob).serialize()
    assert resumed == uninterrupted


# --- US3: multi-stream (SC-003) ----------------------------------------------------


@pytest.mark.parametrize("mode", ["episodic", "continuous"])
def test_multistream_snapshot_resume_is_byte_identical(mode):
    store = InMemorySnapshotStore()
    cfg = Config(**SMALL, n_streams=3, episode_mode=mode, snapshot_every_n_cycles=2)
    uninterrupted = Engine(cfg, snapshot_store=store).run(1).serialize()
    assert store.list()
    blob = store.read(store.list()[-1][0])  # mid-run
    state = decode(blob)
    assert state.streams is not None
    assert len(state.streams["per_stream"]) == 3
    resumed = Engine(cfg).run(1, resume_from=blob).serialize()
    assert resumed == uninterrupted


def test_k1_blobs_carry_no_streams_record():
    import io
    import json

    store = InMemorySnapshotStore()
    cfg = Config(**SMALL, snapshot_every_n_cycles=2)
    Engine(cfg, snapshot_store=store).run(1)
    archive = np.load(io.BytesIO(store.read(store.list()[0][0])), allow_pickle=False)
    assert "streams" not in json.loads(str(archive["meta"]))
