"""Ladder worlds — dials, validation, draw order, and rung math (feature 005)."""

from __future__ import annotations

import numpy as np
import pytest

from pra.config import Config
from pra.world.event_source import SensorimotorWorld
from pra.world.ladder import (
    CompositionalWorld,
    DistractorWorld,
    NonUniformWorld,
    make_world,
)


def _stream(world, seed_actions: list[int]) -> list[np.ndarray]:
    obs = [world.reset()]
    obs.extend(world.step(a) for a in seed_actions)
    return obs


ACTIONS = [0, 1, 2, 3, 0, 1, 2, 3, 0, 1]


# --- config validation (FR-011) ---------------------------------------------


def test_dials_require_their_world():
    with pytest.raises(ValueError, match="region_noise_std > 0 requires"):
        Config(region_noise_std=0.5)
    with pytest.raises(ValueError, match="factor_dims requires"):
        Config(factor_dims=(2, 1))
    with pytest.raises(ValueError, match="distractor_channels > 0 requires"):
        Config(distractor_channels=3)


def test_factor_dims_must_sum_to_true_dim():
    with pytest.raises(ValueError, match="must sum to true_dim"):
        Config(world="compositional", true_dim=3, factor_dims=(2, 2))


def test_distractor_needs_latent_and_a_controllable_channel():
    with pytest.raises(ValueError, match="requires distractor_dim"):
        Config(world="distractor", distractor_channels=3)
    with pytest.raises(ValueError, match="at least one controllable"):
        Config(world="distractor", obs_dim=4, distractor_dim=2, distractor_channels=4)


def test_world_kind_is_validated():
    with pytest.raises(ValueError, match="world must be"):
        Config(world="minecraft")


# --- factory routing ---------------------------------------------------------


def test_make_world_routes_by_config():
    rng = np.random.default_rng(1)
    assert isinstance(make_world(Config(), rng), SensorimotorWorld)
    assert isinstance(
        make_world(Config(world="nonuniform", region_noise_std=0.5), rng), NonUniformWorld
    )
    assert isinstance(
        make_world(Config(world="compositional", factor_dims=(2, 1)), rng), CompositionalWorld
    )
    assert isinstance(
        make_world(
            Config(world="distractor", obs_dim=12, distractor_dim=2, distractor_channels=2), rng
        ),
        DistractorWorld,
    )


# --- degenerate dials reproduce the reference stream (world level) ----------


@pytest.mark.parametrize(
    "cfg",
    [
        Config(world="nonuniform"),
        Config(world="compositional"),
        Config(world="compositional", factor_dims=(3,)),
        Config(world="distractor"),
    ],
    ids=["l1-sigma0", "l2-nogroups", "l2-onegroup", "l3-nochannels"],
)
def test_degenerate_dial_matches_reference_stream(cfg):
    ref = _stream(SensorimotorWorld(Config(), np.random.default_rng(7)), ACTIONS)
    lad = _stream(make_world(cfg, np.random.default_rng(7)), ACTIONS)
    for a, b in zip(ref, lad, strict=True):
        np.testing.assert_array_equal(a, b)


# --- L1: region math, draw order, occupancy ---------------------------------


def test_l1_noise_draw_only_from_in_region_states():
    cfg = Config(world="nonuniform", region_noise_std=0.9)
    w_in = NonUniformWorld(cfg, np.random.default_rng(3))
    w_out = NonUniformWorld(cfg, np.random.default_rng(3))
    w_in.reset(), w_out.reset()

    # Force known pre-step latents: in-region adds noise on top of the
    # displacement; out-of-region is exactly the displacement.
    base = np.zeros(cfg.true_dim)
    w_out._latent = base.copy()
    w_out._latent[0] = -1.0
    before_out = w_out._latent.copy()
    w_out.step(0)
    disp = w_out._latent - before_out  # pure displacement (no noise drawn)

    w_in._latent = base.copy()
    w_in._latent[0] = +1.0
    before_in = w_in._latent.copy()
    w_in.step(0)
    moved = w_in._latent - before_in
    assert not np.allclose(moved, disp)  # noise was added in-region


def test_l1_occupancy_counts_every_step_once():
    cfg = Config(world="nonuniform", region_noise_std=0.5)
    world = NonUniformWorld(cfg, np.random.default_rng(5))
    world.reset()
    for a in ACTIONS:
        world.step(a)
    readings = world.ladder_readings()
    assert readings["steps_total"] == len(ACTIONS)
    assert 0 <= readings["steps_in_region"] <= readings["steps_total"]
    assert readings["occupancy"] == readings["steps_in_region"] / readings["steps_total"]


# --- L2: group masking -------------------------------------------------------


def test_l2_actions_move_only_their_group():
    cfg = Config(world="compositional", true_dim=6, obs_dim=18, factor_dims=(2, 2, 2))
    world = CompositionalWorld(cfg, np.random.default_rng(11))
    world.reset()
    slices = [slice(0, 2), slice(2, 4), slice(4, 6)]
    for action in range(cfg.n_actions):
        group = action % 3
        before = world._latent.copy()
        world.step(action)
        delta = world._latent - before
        for k, sl in enumerate(slices):
            if k == group:
                assert np.any(delta[sl] != 0)
            else:
                np.testing.assert_array_equal(delta[sl], np.zeros(2))


# --- L3: appended channels ---------------------------------------------------


def test_l3_total_width_and_controllable_core():
    cfg = Config(world="distractor", obs_dim=14, distractor_dim=2, distractor_channels=4)
    world = DistractorWorld(cfg, np.random.default_rng(13))
    assert world.obs_dim == 14  # Config.obs_dim is the system-visible total
    assert world.ladder_readings()["controllable_obs_dim"] == 10
    assert world.reset().shape == (14,)
    assert world.step(0).shape == (14,)


def test_l3_distractor_channels_carry_no_action_information():
    cfg = Config(world="distractor", obs_dim=14, distractor_dim=2, distractor_channels=4)
    a = DistractorWorld(cfg, np.random.default_rng(17))
    b = DistractorWorld(cfg, np.random.default_rng(17))
    a.reset(), b.reset()
    obs_a = a.step(0)
    obs_b = b.step(3)  # different action, same stream
    np.testing.assert_array_equal(obs_a[10:], obs_b[10:])  # distractor identical
    assert not np.allclose(obs_a[:10], obs_b[:10])  # controllable differs


def test_l3_noise_std_scales_the_same_draws_exactly():
    """distractor_noise_std (CHANNELNOISE-DIAGNOSIS dial): same RNG stream,
    static channels scaled bit-exactly, core channels untouched — so the
    default (1.0) IS the original unit-normal behavior."""
    base = dict(
        world="distractor",
        obs_dim=14,
        distractor_dim=2,
        distractor_channels=4,
        distractor_mode="noise",
    )
    unit = _stream(DistractorWorld(Config(**base), np.random.default_rng(23)), ACTIONS)
    half = _stream(
        DistractorWorld(Config(**base, distractor_noise_std=0.5), np.random.default_rng(23)),
        ACTIONS,
    )
    for u, h in zip(unit, half, strict=True):
        np.testing.assert_array_equal(u[:10], h[:10])  # core identical
        np.testing.assert_array_equal(u[10:] * 0.5, h[10:])  # static exactly scaled


def test_l3_noise_std_ignored_by_structured_mode():
    cfg = dict(world="distractor", obs_dim=14, distractor_dim=2, distractor_channels=4)
    a = _stream(DistractorWorld(Config(**cfg), np.random.default_rng(29)), ACTIONS)
    b = _stream(
        DistractorWorld(Config(**cfg, distractor_noise_std=0.2), np.random.default_rng(29)),
        ACTIONS,
    )
    for x, y in zip(a, b, strict=True):
        np.testing.assert_array_equal(x, y)


def test_l3_noise_std_must_be_nonnegative():
    with pytest.raises(ValueError, match="distractor_noise_std must be >= 0"):
        Config(distractor_noise_std=-0.1)


def test_l3_noise_mode_is_deterministic_per_seed():
    cfg = Config(
        world="distractor",
        obs_dim=14,
        distractor_dim=2,
        distractor_channels=4,
        distractor_mode="noise",
    )
    s1 = _stream(DistractorWorld(cfg, np.random.default_rng(19)), ACTIONS)
    s2 = _stream(DistractorWorld(cfg, np.random.default_rng(19)), ACTIONS)
    for x, y in zip(s1, s2, strict=True):
        np.testing.assert_array_equal(x, y)
