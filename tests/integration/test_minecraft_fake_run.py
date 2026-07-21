"""Feature 027 T5 — the engine on the FakeBridge world (SC-002).

Full engine runs through the real transport against the in-repo bridge:
byte-identity, the continuous-only contract, and snapshot + exact
resume (fake mode is Doc 06 §5b class 1; the live server is class 4 and
says so). Small budgets — contracts, never science."""

from __future__ import annotations

import pytest

from pra.anatomy.body import AnatomyError
from pra.anatomy.minecraft import (
    C1_N_ACTIONS,
    C1_OBS_DIM,
    FakeBridge,
    MinecraftTransport,
    c1_anatomy,
)
from pra.anatomy.ros2 import Ros2Body
from pra.config import Config
from pra.core.engine import Engine
from pra.persistence.store import InMemorySnapshotStore

SENSORS, ACTUATORS = c1_anatomy()

SMALL = dict(
    warmup_episodes=2,
    n_cycles=3,
    episodes_per_cycle=2,
    steps_per_episode=10,
    horizon_checkpoints=(1, 3),
)


def _cfg(**overrides) -> Config:
    # the builder's body (feature 030): 19/10 is the C1 default
    return Config(
        obs_dim=C1_OBS_DIM, n_actions=C1_N_ACTIONS, episode_mode="continuous", **SMALL, **overrides
    )


def _run(seed: int, cfg: Config | None = None, store=None, resume=None):
    with FakeBridge() as bridge:
        inner = Ros2Body.factory(
            SENSORS,
            ACTUATORS,
            transport=lambda: MinecraftTransport(port=bridge.port, tick_ms=1, tick_budget=60.0),
        )
        mounted: list[Ros2Body] = []

        def factory(cfg_, rng):
            body = inner(cfg_, rng)
            mounted.append(body)
            return body

        engine = Engine(cfg or _cfg(), world_factory=factory, snapshot_store=store)
        try:
            return engine.run(seed, resume_from=resume)
        finally:
            for body in mounted:
                body.close()


def test_same_seed_runs_are_byte_identical():
    assert _run(1).serialize() == _run(1).serialize()


def test_different_seeds_differ():
    assert _run(1).serialize() != _run(2).serialize()


def test_episodic_mounting_is_loud():
    cfg = Config(obs_dim=C1_OBS_DIM, n_actions=C1_N_ACTIONS, episode_mode="episodic", **SMALL)
    with pytest.raises(AnatomyError, match="continuous"):
        _run(1, cfg=cfg)


def test_snapshot_and_resume_reproduce_the_uninterrupted_run_exactly():
    cfg = _cfg(snapshot_every_n_cycles=1)
    unbroken = InMemorySnapshotStore()
    _run(1, cfg=cfg, store=unbroken)
    snaps = unbroken.list()  # newest first
    final_id, first_id = snaps[0][0], snaps[-1][0]
    resumed = InMemorySnapshotStore()
    _run(1, cfg=cfg, store=resumed, resume=unbroken.read(first_id))
    assert resumed.list()[0][0] == final_id
    assert resumed.read(final_id) == unbroken.read(final_id)
