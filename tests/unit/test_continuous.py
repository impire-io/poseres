"""Continuous operation — config validation, the SingleBootWorld instrument,
and world-state capture round-trips (feature 008)."""

from __future__ import annotations

import numpy as np
import pytest

from pra.config import Config
from pra.world.event_source import SensorimotorWorld
from pra.world.ladder import make_world


class SingleBootWorld:
    """A world that genuinely cannot restart: exactly one reset() (the boot)
    is permitted; any second call raises. The feature-008 guard instrument
    (research R8) — wraps any EventSource."""

    def __init__(self, inner):
        self._inner = inner
        self.boots = 0

    @property
    def n_actions(self) -> int:
        return self._inner.n_actions

    @property
    def obs_dim(self) -> int:
        return self._inner.obs_dim

    def reset(self) -> np.ndarray:
        if self.boots:
            raise RuntimeError("SingleBootWorld: already booted")
        self.boots += 1
        return self._inner.reset()

    def step(self, action: int) -> np.ndarray:
        return self._inner.step(action)

    def state_dict(self) -> dict:
        return {"inner": self._inner.state_dict(), "boots": self.boots}

    def load_state_dict(self, state: dict) -> None:
        self._inner.load_state_dict(state["inner"])
        self.boots = int(state["boots"])


def single_boot_factory(cfg: Config, rng: np.random.Generator) -> SingleBootWorld:
    return SingleBootWorld(SensorimotorWorld(cfg, rng))


def test_episode_mode_is_validated():
    with pytest.raises(ValueError, match="episode_mode must be"):
        Config(episode_mode="perpetual")
    assert Config().episode_mode == "episodic"  # the pinned validated default


def test_single_boot_world_permits_exactly_one_reset():
    world = SingleBootWorld(SensorimotorWorld(Config(), np.random.default_rng(1)))
    world.reset()
    assert world.boots == 1
    with pytest.raises(RuntimeError, match="already booted"):
        world.reset()


@pytest.mark.parametrize(
    "cfg",
    [
        Config(),
        Config(world="nonuniform", region_noise_std=0.5),
        Config(world="compositional", true_dim=6, obs_dim=18, factor_dims=(3, 3)),
        Config(world="distractor", obs_dim=14, distractor_dim=2, distractor_channels=4),
    ],
    ids=["reference", "l1", "l2", "l3"],
)
def test_world_state_capture_round_trip(cfg):
    """state_dict/load_state_dict restores the world exactly: two copies with
    the same rng that diverge (one stepped further) reconverge when the state
    is loaded — subsequent streams identical given identical rng states."""
    rng_a = np.random.default_rng(7)
    a = make_world(cfg, rng_a)
    a.reset()
    for action in (0, 1, 2, 3, 0):
        a.step(action)

    rng_b = np.random.default_rng(7)
    b = make_world(cfg, rng_b)
    b.reset()  # different point in its trajectory

    b.load_state_dict(a.state_dict())
    rng_b.bit_generator.state = rng_a.bit_generator.state  # align the streams

    for action in (2, 3, 1):
        np.testing.assert_array_equal(a.step(action), b.step(action))
