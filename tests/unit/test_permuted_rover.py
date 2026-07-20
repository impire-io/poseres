"""Permuted-rover unit tests (feature 028, FR-002): the maturity control's
world is fully learnable but structurally unrelated (a fixed construction-time
permutation of actions + sensor channels); permute=False is byte-identical to
the plain rover."""

from __future__ import annotations

import numpy as np

from pra.config import Config
from pra.core.engine import Engine
from pra.examples.rover.world import (
    ROVER_N_ACTIONS,
    ROVER_OBS_DIM,
    RoverWorld,
    make_rover_body,
)

_FAST = Config(warmup_episodes=10, n_cycles=6, horizon_checkpoints=(6,))


def _run(factory, seed=1):
    return Engine(_FAST, world_factory=factory).run(seed)


def test_permute_false_is_byte_identical_to_plain_rover():
    plain = _run(lambda c, r: make_rover_body(c, r))
    explicit = _run(lambda c, r: make_rover_body(c, r, permute=False))
    assert plain.serialize() == explicit.serialize()


def test_permutation_vectors_are_valid_permutations():
    w = RoverWorld(_FAST, np.random.default_rng(1), permute=True, permute_seed=5)
    assert sorted(w._action_perm.tolist()) == list(range(ROVER_N_ACTIONS))
    assert sorted(w._sensor_perm.tolist()) == list(range(ROVER_OBS_DIM))


def test_permuted_world_is_learnable_and_distinct():
    seeded = _run(lambda c, r: make_rover_body(c, r, layout_seed=1001))
    permuted = _run(
        lambda c, r: make_rover_body(c, r, layout_seed=1001, permute=True, permute_seed=7)
    )
    # learnable: prediction error falls over the run
    assert permuted.pred_error_late is not None
    assert permuted.pred_error_late < permuted.pred_error_early
    # unrelated: the permuted run is not byte-identical to the un-permuted map
    assert permuted.serialize() != seeded.serialize()


def test_permute_consumes_no_run_stream_draws():
    # A permuted world draws its permutation from an independent generator, so
    # the run/brain stream (obstacles from the same engine rng, then reset/emit)
    # is untouched EXCEPT for the permutation's effect on observations. The map
    # itself (obstacles) must be identical to the un-permuted world at the same
    # layout seed — the permutation reindexes senses, it does not redraw the map.
    plain = RoverWorld(_FAST, np.random.default_rng(1), layout_seed=1001)
    permuted = RoverWorld(
        _FAST, np.random.default_rng(1), layout_seed=1001, permute=True, permute_seed=7
    )
    assert plain._obstacles == permuted._obstacles
