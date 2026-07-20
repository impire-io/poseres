"""Rover resize-hop unit tests (feature 028 US2): the +1-sensor back-ray grows
the body — native 11-dim (fresh-C) and pending 10→11 (the seeded chain's resize)
— while the un-grown path stays byte-identical (the back-ray is RNG-free)."""

from __future__ import annotations

import numpy as np

from pra.anatomy.body import AnatomyError
from pra.config import Config
from pra.core.engine import Engine
from pra.examples.rover.world import make_rover_body
from pra.persistence.snapshot import decode
from pra.persistence.store import InMemorySnapshotStore

_FAST10 = Config(warmup_episodes=6, n_cycles=4, horizon_checkpoints=(4,), snapshot_every_n_cycles=4)
_FAST11 = Config(
    obs_dim=11, warmup_episodes=6, n_cycles=4, horizon_checkpoints=(4,), snapshot_every_n_cycles=4
)


def _final(factory, cfg, seed=1):
    store = InMemorySnapshotStore()
    Engine(cfg, world_factory=factory, snapshot_store=store).run(seed)
    return decode(store.read(store.list()[0][0]))


def test_native_11dim_rover_runs_at_obs_dim_11():
    st = _final(lambda c, r: make_rover_body(c, r, layout_seed=5, extra_ray=True), _FAST11)
    assert st.frame_store["obs_dim"] == 11


def test_pending_growth_resizes_10_to_11():
    st = _final(lambda c, r: make_rover_body(c, r, layout_seed=5, extra_ray_pending=True), _FAST10)
    assert st.frame_store["obs_dim"] == 11


def test_native_11dim_requires_obs_dim_11():
    # extra_ray active needs obs_dim 11; a 10-dim config is rejected at mount.
    try:
        make_rover_body(_FAST10, np.random.default_rng(1), extra_ray=True)
    except AnatomyError:
        return
    raise AssertionError("expected AnatomyError for extra_ray with obs_dim=10")


def test_ungrown_default_is_byte_identical():
    plain = _final(lambda c, r: make_rover_body(c, r, layout_seed=5), _FAST10)
    # a run with the grow machinery present but off (defaults) is identical
    off = _final(
        lambda c, r: make_rover_body(c, r, layout_seed=5, extra_ray=False, extra_ray_pending=False),
        _FAST10,
    )
    assert plain.pred_errors == off.pred_errors


def test_pending_growth_run_is_deterministic():
    f = lambda c, r: make_rover_body(c, r, layout_seed=9, extra_ray_pending=True)  # noqa: E731
    assert _final(f, _FAST10).pred_errors == _final(f, _FAST10).pred_errors
