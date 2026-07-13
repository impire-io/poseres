"""Rover world unit tests (feature 006) — geometry, collision, spawn
sampling, channel semantics, draw-order determinism, and mount validation.
"""

from __future__ import annotations

import math

import numpy as np
import pytest

from pra.anatomy.body import AnatomyError
from pra.config import Config
from pra.examples.rover.world import (
    ARENA_HALF,
    MOVE_STEP,
    RAY_MAX,
    ROVER_RADIUS,
    TURN_STEP,
    RoverSensor,
    RoverWorld,
    _collides,
    _draw_spawns,
    _ray_distance,
    _wrap_angle,
    make_rover_body,
)


def _quiet_world(seed: int = 1, *, clear_obstacles: bool = True) -> RoverWorld:
    """A noise-free world; obstacles cleared so channel math is hand-computable."""
    world = RoverWorld(Config(sensor_noise_std=0.0), np.random.default_rng(seed))
    if clear_obstacles:
        world._obstacles = []
    world._x, world._y, world._theta, world._bump = 0.0, 0.0, 0.0, 0
    world._emit()
    return world


# --- pure geometry -------------------------------------------------------------


def test_ray_hits_wall_from_center():
    assert _ray_distance(0.0, 0.0, 1.0, 0.0, []) == pytest.approx(ARENA_HALF)
    assert _ray_distance(0.5, 0.0, 1.0, 0.0, []) == pytest.approx(0.5)
    assert _ray_distance(0.0, 0.0, -1.0, 0.0, []) == pytest.approx(ARENA_HALF)
    assert _ray_distance(0.0, 0.0, 0.0, -1.0, []) == pytest.approx(ARENA_HALF)


def test_ray_hits_obstacle_front_face():
    assert _ray_distance(0.0, 0.0, 1.0, 0.0, [(0.5, 0.0, 0.2)]) == pytest.approx(0.3)


def test_ray_ignores_misses_and_behind():
    # perpendicular offset 0.5 > radius 0.2: miss, wall wins
    assert _ray_distance(0.0, 0.0, 1.0, 0.0, [(0.5, 0.5, 0.2)]) == pytest.approx(ARENA_HALF)
    # obstacle behind the ray: ignored
    assert _ray_distance(0.0, 0.0, 1.0, 0.0, [(-0.5, 0.0, 0.2)]) == pytest.approx(ARENA_HALF)


def test_ray_is_capped():
    assert _ray_distance(0.0, 0.0, 1.0, 0.0, [], cap=0.25) == pytest.approx(0.25)


def test_collision_with_wall_and_obstacle():
    assert _collides(ARENA_HALF - ROVER_RADIUS + 0.01, 0.0, [])
    assert not _collides(ARENA_HALF - ROVER_RADIUS - 0.01, 0.0, [])
    assert _collides(0.25, 0.0, [(0.0, 0.0, 0.2)])  # 0.25 < 0.2 + 0.06
    assert not _collides(0.3, 0.0, [(0.0, 0.0, 0.2)])


def test_spawn_sampling_is_collision_free_and_bounded():
    rng = np.random.default_rng(1)
    obstacles = [(0.0, 0.0, 0.3)]
    spawns = _draw_spawns(rng, obstacles)
    assert len(spawns) == 8
    for x, y, _theta in spawns:
        assert not _collides(x, y, obstacles)
    with pytest.raises(ValueError, match="spawn"):
        _draw_spawns(np.random.default_rng(1), [(0.0, 0.0, 5.0)])


def test_wrap_angle_stays_in_range():
    for k in range(-8, 9):
        theta = _wrap_angle(k * 0.9 * math.pi)
        assert -math.pi <= theta < math.pi


# --- channel semantics (noise-free, hand-computable) ----------------------------


def test_channel_order_and_values_at_center():
    world = _quiet_world()
    obs = np.concatenate([world.sense(p) for p in ("rays", "compass", "gps", "bump")])
    assert obs.shape == (10,)
    # empty arena from the center: every ray >= ARENA_HALF, capped to RAY_MAX -> 1.0
    assert obs[0:5] == pytest.approx(np.ones(5) * (min(ARENA_HALF, RAY_MAX) / RAY_MAX))
    assert obs[5:7] == pytest.approx([1.0, 0.0])  # cos 0, sin 0
    assert obs[7:9] == pytest.approx([0.0, 0.0])
    assert obs[9] == 0.0


def test_forward_moves_gps_along_heading():
    world = _quiet_world()
    world.apply(0)
    assert world.sense("gps")[0] == pytest.approx(MOVE_STEP / ARENA_HALF)
    assert world.sense("gps")[1] == pytest.approx(0.0)
    assert world.sense("bump")[0] == 0.0


def test_blocked_move_sets_bump_and_holds_pose():
    world = _quiet_world()
    world._x = ARENA_HALF - ROVER_RADIUS - 0.01  # one forward step would cross the wall
    world._emit()
    world.apply(0)
    assert world.sense("bump")[0] == 1.0
    assert world._x == pytest.approx(ARENA_HALF - ROVER_RADIUS - 0.01)  # pose held
    world.apply(2)  # turning never bumps and clears the flag
    assert world.sense("bump")[0] == 0.0
    assert world._theta == pytest.approx(TURN_STEP)


def test_reverse_moves_backward_at_half_speed():
    world = _quiet_world()
    world.apply(1)
    assert world.sense("gps")[0] == pytest.approx(-0.5 * MOVE_STEP / ARENA_HALF)


def test_apply_rejects_unknown_action_and_pre_reset_use():
    world = _quiet_world()
    with pytest.raises(ValueError, match="action"):
        world.apply(4)
    fresh = RoverWorld(Config(), np.random.default_rng(2))
    with pytest.raises(RuntimeError, match="reset"):
        fresh.apply(0)


def test_sensor_read_before_first_emission_raises():
    world = RoverWorld(Config(), np.random.default_rng(3))
    with pytest.raises(AnatomyError, match="rays"):
        RoverSensor(world, "rays", 5).read()


# --- determinism (research R4) ---------------------------------------------------


def test_construction_and_observation_sequence_deterministic():
    def observations(seed: int) -> np.ndarray:
        body = make_rover_body(Config(), np.random.default_rng(seed))
        seq = [body.reset()]
        for action in (0, 2, 0, 1, 3, 0, 0, 2):
            seq.append(body.step(action))
        return np.stack(seq)

    a, b = observations(7), observations(7)
    assert np.array_equal(a, b)
    w1 = RoverWorld(Config(), np.random.default_rng(7))
    w2 = RoverWorld(Config(), np.random.default_rng(7))
    assert w1.layout() == w2.layout()


def test_reset_draws_fresh_spawn_per_episode():
    body = make_rover_body(Config(sensor_noise_std=0.0), np.random.default_rng(5))
    first = {tuple(np.round(body.reset()[7:9], 6)) for _ in range(12)}
    assert len(first) > 1  # multiple distinct start positions across episodes


# --- anatomy / mount (research R2, FR-011) ---------------------------------------


def test_body_composition_matches_the_documented_anatomy():
    body = make_rover_body(Config(), np.random.default_rng(1))
    assert body.obs_dim == 10
    assert body.n_actions == 4
    assert body.list_tools() == [
        ("rays", "sensor"),
        ("compass", "sensor"),
        ("gps", "sensor"),
        ("bump", "sensor"),
        ("drive", "actuator"),
    ]
    obs = body.reset()
    assert obs.shape == (10,) and obs.dtype == np.float64


@pytest.mark.parametrize("overrides", [{"obs_dim": 12}, {"n_actions": 5}])
def test_mount_rejects_mismatched_widths(overrides):
    with pytest.raises(AnatomyError, match="obs_dim"):
        make_rover_body(Config(**overrides), np.random.default_rng(1))
