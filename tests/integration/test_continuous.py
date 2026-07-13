"""Continuous operation — mode equivalence, single boot, determinism,
boundary placements, snapshot/resume, and composition (feature 008).

Small budgets throughout: these tests check contracts, never the science —
the recorded reading lives in specs/008-continuous-operation/reading.md.
"""

from __future__ import annotations

import numpy as np
import pytest

from pra.config import Config
from pra.core.engine import Engine
from pra.persistence.snapshot import decode
from pra.persistence.store import InMemorySnapshotStore
from pra.world.ladder import make_world
from tests.unit.test_continuous import SingleBootWorld, single_boot_factory

SMALL = dict(
    warmup_episodes=2,
    n_cycles=3,
    episodes_per_cycle=2,
    steps_per_episode=10,
    horizon_checkpoints=(1, 3),
)


def _run(cfg: Config, seed: int = 1, **engine_kw) -> str:
    return Engine(cfg, **engine_kw).run(seed).serialize()


# --- mode contract (FR-001/002) ----------------------------------------------


def test_default_mode_is_byte_identical_to_prefeature_behavior():
    # episodic is the default; an explicit episodic selection changes nothing
    assert _run(Config(**SMALL)) == _run(Config(**SMALL, episode_mode="episodic"))


def test_continuous_boots_exactly_once_for_a_full_schedule():
    booted: dict = {}

    def factory(cfg, rng):
        world = SingleBootWorld(make_world(cfg, rng))
        booted["world"] = world
        return world

    cfg = Config(**SMALL, episode_mode="continuous")
    summary = Engine(cfg, world_factory=factory).run(1)
    assert booted["world"].boots == 1
    assert summary.observation_steps > 0


def test_episodic_mode_on_a_single_boot_world_still_fails():
    # the reverse direction keeps failing, with the world's own error surfacing
    cfg = Config(**SMALL)
    with pytest.raises(RuntimeError, match="already booted"):
        Engine(cfg, world_factory=single_boot_factory).run(1)


# --- determinism (FR-005) ------------------------------------------------------


def test_continuous_runs_are_deterministic():
    cfg = Config(**SMALL, episode_mode="continuous")
    assert _run(cfg) == _run(cfg)


def test_continuous_composes_with_drives_and_ladder_worlds():
    cfg = Config(
        **SMALL,
        episode_mode="continuous",
        world="nonuniform",
        region_noise_std=0.5,
        policy_mode="curiosity",
        drive_weights=(("competence", 1.0),),
    )
    a = Engine(cfg, world_factory=make_world).run(1).serialize()
    b = Engine(cfg, world_factory=make_world).run(1).serialize()
    assert a == b


# --- stream contract (FR-003/004, SC-004) --------------------------------------


class _CountingWorld(SingleBootWorld):
    """Counts every observation the world produced (boot + steps)."""

    def __init__(self, inner):
        super().__init__(inner)
        self.produced = 0

    def reset(self) -> np.ndarray:
        obs = super().reset()
        self.produced += 1
        return obs

    def step(self, action: int) -> np.ndarray:
        obs = super().step(action)
        self.produced += 1
        return obs


def test_stream_is_gap_free_and_duplication_free():
    """Every observation the engine processes is one the world produced, in
    order, none skipped and none twice: engine-processed count == produced
    count minus the single not-yet-processed trailing observation."""
    holder: dict = {}

    def factory(cfg, rng):
        world = _CountingWorld(make_world(cfg, rng))
        holder["world"] = world
        return world

    cfg = Config(**SMALL, episode_mode="continuous")
    summary = Engine(cfg, world_factory=factory).run(1)
    world = holder["world"]
    # engine processes exactly steps_per_episode observations per span; the
    # world produced one boot obs + one per step; the trailing obs of the
    # final span is carried but never processed.
    assert world.produced == summary.observation_steps + 1


def test_cap_projection_fires_at_virtual_boundaries():
    """The norm-cap projection triggers on the chain break (prev_obs is None),
    i.e. once per virtual episode — same placement as episodic mode. Proxy
    assertion with a cap tight enough to bind from birth (0.5 of the expected
    init norm — at tiny budgets 1.2 never binds): capped continuous run
    differs from uncapped (the projection acted), and both are deterministic."""
    base = dict(**SMALL, episode_mode="continuous")
    capped = Config(**base, weight_norm_cap=0.5)
    uncapped = Config(**base)
    assert _run(capped) == _run(capped)
    assert _run(capped) != _run(uncapped)


def test_fair_judge_window_restarts_at_virtual_boundaries():
    """score_window_steps > 0 must change survival scoring in continuous mode
    exactly as in episodic mode (the window is keyed on the within-span index)."""
    base = dict(**SMALL, episode_mode="continuous")
    judged = Config(**base, score_window_steps=5)
    unjudged = Config(**base)
    assert _run(judged) == _run(judged)
    assert _run(judged) != _run(unjudged)


# --- snapshots (FR-005, SC-003) -------------------------------------------------


def test_continuous_resume_is_byte_identical():
    store = InMemorySnapshotStore()
    cfg = Config(**SMALL, episode_mode="continuous", snapshot_every_n_cycles=2)
    uninterrupted = Engine(cfg, snapshot_store=store).run(1).serialize()
    assert store.list(), "expected at least one snapshot"
    snapshot_id, _meta = store.list()[-1]  # oldest = mid-run
    resumed = (
        Engine(cfg, snapshot_store=InMemorySnapshotStore())
        .run(1, resume_from=store.read(snapshot_id))
        .serialize()
    )
    assert resumed == uninterrupted


def test_episodic_snapshot_blobs_carry_no_trace_of_feature_008():
    """The world_state meta key and world__ arrays are written only in
    continuous mode: episodic blobs are format-identical to pre-feature ones
    (the key is simply absent), and decode reads them as world_state None."""
    import io
    import json

    store = InMemorySnapshotStore()
    cfg = Config(**SMALL, snapshot_every_n_cycles=2)
    Engine(cfg, snapshot_store=store).run(1)
    blob = store.read(store.list()[0][0])
    assert decode(blob).world_state is None
    archive = np.load(io.BytesIO(blob), allow_pickle=False)
    assert not [k for k in archive.files if k.startswith("world__")]
    assert "world_state" not in json.loads(str(archive["meta"]))


def test_continuous_snapshot_requires_capture_protocol():
    class NoCaptureWorld:
        def __init__(self, inner):
            self._inner = inner

        @property
        def n_actions(self):
            return self._inner.n_actions

        @property
        def obs_dim(self):
            return self._inner.obs_dim

        def reset(self):
            return self._inner.reset()

        def step(self, action):
            return self._inner.step(action)

    def factory(cfg, rng):
        return NoCaptureWorld(make_world(cfg, rng))

    cfg = Config(**SMALL, episode_mode="continuous", snapshot_every_n_cycles=2)
    with pytest.raises(RuntimeError, match="state_dict"):
        Engine(cfg, world_factory=factory, snapshot_store=InMemorySnapshotStore()).run(1)


# --- composition with the body (research R7) ------------------------------------


def test_continuous_through_a_body_is_deterministic_and_capturable():
    from pra.anatomy.body import Body, WorldActuator, WorldSensor
    from pra.world.event_source import SensorimotorWorld

    def body_factory(cfg, rng):
        world = SensorimotorWorld(cfg, rng)
        sensor = WorldSensor(world)
        return Body(world, sensors=[sensor], actuators=[WorldActuator(world, sensor)])

    store = InMemorySnapshotStore()
    cfg = Config(**SMALL, episode_mode="continuous", snapshot_every_n_cycles=2)
    a = Engine(cfg, world_factory=body_factory, snapshot_store=store).run(1).serialize()
    b = Engine(cfg, world_factory=body_factory).run(1).serialize()
    assert a == b  # snapshot capture perturbed nothing
    assert store.list()  # and the body delegated capture to its environment
