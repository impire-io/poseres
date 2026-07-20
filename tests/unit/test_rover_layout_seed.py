"""Rover layout-seed unit tests (feature 028, FR-001): the harness-owned
layout seed makes maps addressable independently of the brain seed, and the
degenerate path (layout_seed=None) is byte-identical to feature 006."""

from __future__ import annotations

import numpy as np

from pra.config import Config
from pra.core.engine import Engine
from pra.examples.rover.world import RoverWorld, make_rover_body

_FAST = Config(warmup_episodes=6, n_cycles=4, horizon_checkpoints=(4,), episodes_per_cycle=3)


def _run(factory, seed=1):
    return Engine(_FAST, world_factory=factory).run(seed)


def test_layout_seed_none_is_byte_identical_to_plain_rover():
    plain = _run(lambda c, r: make_rover_body(c, r))
    explicit = _run(lambda c, r: make_rover_body(c, r, layout_seed=None, permute=False))
    assert plain.serialize() == explicit.serialize()


def test_same_layout_seed_gives_same_map_regardless_of_run_rng():
    a = RoverWorld(_FAST, np.random.default_rng(1), layout_seed=4242)
    b = RoverWorld(_FAST, np.random.default_rng(999), layout_seed=4242)
    assert a._obstacles == b._obstacles
    assert a._spawns == b._spawns


def test_distinct_layout_seeds_give_distinct_maps():
    a = RoverWorld(_FAST, np.random.default_rng(1), layout_seed=1)
    b = RoverWorld(_FAST, np.random.default_rng(1), layout_seed=2)
    assert a._obstacles != b._obstacles


def test_layout_seed_run_is_deterministic():
    f = lambda c, r: make_rover_body(c, r, layout_seed=777)  # noqa: E731
    assert _run(f).serialize() == _run(f).serialize()
