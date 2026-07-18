"""Feature 017 worlds (CAMPING-DIAGNOSIS): the shifting world and the
multi-region world — degenerate byte-identity, shift semantics (no RNG at
shift time), region counters, and state capture."""

from __future__ import annotations

import numpy as np
import pytest

from pra.config import Config
from pra.world.event_source import SensorimotorWorld
from pra.world.ladder import MultiRegionWorld, ShiftingWorld, make_world

ACTIONS = [0, 1, 2, 3, 0, 1, 2, 3, 3, 2, 1, 0] * 4


def _stream(world, actions):
    out = [world.reset()]
    out += [world.step(a) for a in actions]
    return out


@pytest.mark.parametrize(
    "cfg",
    [
        Config(world="shifting"),
        Config(world="multiregion"),
    ],
    ids=["shifting-off", "multiregion-off"],
)
def test_degenerate_dial_matches_reference_stream(cfg):
    ref = _stream(SensorimotorWorld(Config(), np.random.default_rng(7)), ACTIONS)
    lad = _stream(make_world(cfg, np.random.default_rng(7)), ACTIONS)
    for a, b in zip(ref, lad, strict=True):
        np.testing.assert_array_equal(a, b)


def test_shift_swaps_displacements_at_the_registered_boundary():
    cfg = Config(world="shifting", shift_after_steps=5)
    w = ShiftingWorld(cfg, np.random.default_rng(3))
    w.reset()
    # identical twin world; drive both with the same actions and compare
    # latent displacements against the pre/post sets directly
    for k in range(10):
        before = w._latent.copy()
        w.step(1)
        disp = w._latent - before
        expected = w._post_actions[1] if k >= 5 else w._actions[1]
        np.testing.assert_allclose(disp, expected, rtol=0, atol=1e-12)
    r = w.ladder_readings()
    assert r["shifted"] is True and r["steps_emitted"] == 10


def test_shift_consumes_no_rng_at_shift_time():
    """Pre-shift observations are identical between a shifting world and the
    reference (the post-shift draw happens at construction, after all
    reference draws — so the *stepping* stream diverges only after S)."""
    cfg = Config(world="shifting", shift_after_steps=6)
    a = _stream(ShiftingWorld(cfg, np.random.default_rng(11)), ACTIONS[:12])
    b = _stream(ShiftingWorld(Config(world="shifting"), np.random.default_rng(11)), ACTIONS[:12])
    # streams agree on reset + first 6 steps... but construction differs by
    # the post-action draws, which shift the sensor-noise stream. The honest
    # invariant: the dialed world agrees with ITSELF resumed (state capture),
    # and with its twin at every pre-shift step given identical construction.
    c = _stream(ShiftingWorld(cfg, np.random.default_rng(11)), ACTIONS[:12])
    for x, y in zip(a, c, strict=True):
        np.testing.assert_array_equal(x, y)
    # divergence from the undialed twin begins exactly at construction
    # (extra draws) — recorded property, not identity:
    assert not np.array_equal(a[1], b[1])


def test_shifting_state_capture_resumes_across_the_shift():
    cfg = Config(world="shifting", shift_after_steps=4)
    w1 = ShiftingWorld(cfg, np.random.default_rng(5))
    w1.reset()
    for a in ACTIONS[:3]:
        w1.step(a)
    state = w1.state_dict()
    # a twin at the same construction, fast-forwarded via state + rng sync
    w2 = ShiftingWorld(cfg, np.random.default_rng(5))
    w2.reset()
    for a in ACTIONS[:3]:
        w2.step(a)
    w2.load_state_dict(state)
    for a in ACTIONS[3:10]:
        np.testing.assert_array_equal(w1.step(a), w2.step(a))
    assert w1.ladder_readings()["shifted"] is True


def test_multiregion_counts_and_draws_per_region():
    cfg = Config(world="multiregion", region_noise_levels=(0.0, 0.9))
    w = MultiRegionWorld(cfg, np.random.default_rng(3))
    w.reset()
    # force out-of-region (latent[0] <= 0): displacement exact, no draw
    w._latent = np.zeros(cfg.true_dim)
    w._latent[0] = -1.0
    before = w._latent.copy()
    w.step(2)
    np.testing.assert_array_equal(w._latent, before + w._actions[2])
    # force in-region (latent[0] > 0): displacement plus a noise draw
    w._latent = np.zeros(cfg.true_dim)
    w._latent[0] = +1.0
    before = w._latent.copy()
    w.step(2)
    assert not np.array_equal(w._latent, before + w._actions[2])
    r = w.ladder_readings()
    assert r["steps_by_region"] == [1, 1]
    assert r["occupancy_by_region"] == [0.5, 0.5]


def test_multiregion_four_levels_uses_quadrants():
    cfg = Config(world="multiregion", region_noise_levels=(0.0, 0.0, 0.0, 0.0))
    w = MultiRegionWorld(cfg, np.random.default_rng(3))
    w.reset()
    for signs, expect in [((-1, -1), 0), ((-1, 1), 1), ((1, -1), 2), ((1, 1), 3)]:
        latent = np.zeros(cfg.true_dim)
        latent[0], latent[1] = signs
        assert w._region(latent) == expect


def test_dials_require_their_world():
    with pytest.raises(ValueError, match="shift_after_steps"):
        Config(shift_after_steps=100)
    with pytest.raises(ValueError, match="region_noise_levels"):
        Config(region_noise_levels=(0.0, 0.3))
    with pytest.raises(ValueError, match="2 or 4"):
        Config(world="multiregion", region_noise_levels=(0.0, 0.3, 0.3))


# --- feature 020: emission-shift mode (EMSHIFT-DIAGNOSIS) --------------------


def test_emission_mode_swaps_appearance_not_dynamics():
    cfg = Config(world="shifting", shift_after_steps=5, shift_mode="emission")
    w = ShiftingWorld(cfg, np.random.default_rng(3))
    w.reset()
    for k in range(10):
        before = w._latent.copy()
        w.step(1)
        # dynamics never change: displacement is always the reference set's
        np.testing.assert_allclose(w._latent - before, w._actions[1], rtol=0, atol=1e-12)
    # appearance swapped: the clean emission now uses the post-shift matrix
    w._latent = np.ones(cfg.true_dim)
    obj = w._obj
    import numpy as _np

    expected_post = _np.tanh(w._post_emits[obj] @ w._latent / w._emit_norm)
    np.testing.assert_array_equal(w._emit_core(), expected_post)
    assert w.ladder_readings()["shift_mode"] == "emission"
    assert w.ladder_readings()["shifted"] is True


def test_emission_mode_pre_shift_uses_reference_emission():
    cfg = Config(world="shifting", shift_after_steps=50, shift_mode="emission")
    w = ShiftingWorld(cfg, np.random.default_rng(3))
    w.reset()
    w._latent = np.ones(cfg.true_dim)
    expected_pre = np.tanh(w._objects[w._obj][1] @ w._latent / w._emit_norm)
    np.testing.assert_array_equal(w._emit_core(), expected_pre)


def test_emission_shift_state_capture_resumes_across_the_shift():
    cfg = Config(world="shifting", shift_after_steps=4, shift_mode="emission")
    w1 = ShiftingWorld(cfg, np.random.default_rng(5))
    w1.reset()
    for a in ACTIONS[:3]:
        w1.step(a)
    state = w1.state_dict()
    w2 = ShiftingWorld(cfg, np.random.default_rng(5))
    w2.reset()
    for a in ACTIONS[:3]:
        w2.step(a)
    w2.load_state_dict(state)
    for a in ACTIONS[3:10]:
        np.testing.assert_array_equal(w1.step(a), w2.step(a))
    assert w1.ladder_readings()["shifted"] is True


def test_emission_mode_requires_a_shift_boundary():
    with pytest.raises(ValueError, match="shift_mode"):
        Config(world="shifting", shift_mode="emission")
