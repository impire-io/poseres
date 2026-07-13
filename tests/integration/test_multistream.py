"""Multi-stream — determinism, structure sharing, cadence invariance, and
composition (feature 009). Small budgets: contracts, never science — the
recorded readings live in specs/009-multi-stream/reading.md."""

from __future__ import annotations

import numpy as np

from pra.config import Config
from pra.core.engine import Engine
from pra.world.ladder import make_world
from tests.unit.test_continuous import SingleBootWorld

SMALL = dict(
    warmup_episodes=2,
    n_cycles=3,
    episodes_per_cycle=2,
    steps_per_episode=10,
    horizon_checkpoints=(1, 3),
)


def _run(cfg: Config, seed: int = 1, **kw) -> str:
    return Engine(cfg, **kw).run(seed).serialize()


# --- determinism (FR-002, SC-001) ---------------------------------------------


def test_k4_runs_are_deterministic_in_both_modes():
    for mode in ("episodic", "continuous"):
        cfg = Config(**SMALL, n_streams=4, episode_mode=mode)
        assert _run(cfg) == _run(cfg), mode


def test_k4_differs_from_k1():
    # the streams actually do something: merged experience is a different run
    assert _run(Config(**SMALL, n_streams=4)) != _run(Config(**SMALL))


# --- structure sharing (FR-001, research R2) ------------------------------------


def test_streams_share_construction_and_diverge_in_exploration():
    pre_states: list = []
    instances: list = []

    def factory(cfg, rng):
        pre_states.append(str(rng.bit_generator.state))  # state BEFORE construction
        world = make_world(cfg, rng)
        instances.append(world)
        return world

    cfg = Config(**SMALL, n_streams=2, episode_mode="continuous")
    Engine(cfg, world_factory=factory).run(1)
    assert len(instances) == 2
    # identical construction seeding -> identical hidden structure
    assert pre_states[0] == pre_states[1]
    # ...but the explorations diverged (continuous mode: each world's mutable
    # state is where its own stream carried it)
    a, b = instances[0].state_dict(), instances[1].state_dict()
    assert not np.allclose(a["latent"], b["latent"])


# --- cadence in total experience (FR-005, SC-003) -------------------------------


def test_consolidation_positions_are_k_invariant():
    s1 = Engine(Config(**SMALL, n_streams=1)).run(1)
    s4 = Engine(Config(**SMALL, n_streams=4)).run(1)
    # same schedule -> same total experience and same number of cycles,
    # at identical observation-count positions (cycle = episodes_per_cycle
    # merged episodes regardless of K)
    assert s1.observation_steps == s4.observation_steps
    assert len(s1.population_by_cycle) == len(s4.population_by_cycle)
    assert set(s1.checkpoints) == set(s4.checkpoints)


# --- composition (SC-005) --------------------------------------------------------


def test_each_of_k_streams_boots_exactly_once_in_continuous_mode():
    instances: list = []

    def factory(cfg, rng):
        world = SingleBootWorld(make_world(cfg, rng))
        instances.append(world)
        return world

    cfg = Config(**SMALL, n_streams=3, episode_mode="continuous")
    Engine(cfg, world_factory=factory).run(1)
    assert len(instances) == 3
    assert [w.boots for w in instances] == [1, 1, 1]


def test_multistream_composes_with_drives():
    cfg = Config(
        **SMALL,
        n_streams=2,
        policy_mode="curiosity",
        drive_weights=(("competence", 1.0),),
    )
    assert _run(cfg) == _run(cfg)
