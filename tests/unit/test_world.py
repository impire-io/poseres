"""T020 — SensorimotorWorld: nonlinear emission, hidden latent, determinism."""

from __future__ import annotations

import numpy as np

from pra.config import Config
from pra.world.event_source import SensorimotorWorld


def _stream(seed, n_steps=50, **cfg_kw):
    cfg = Config(**cfg_kw)
    rng = np.random.default_rng(seed)
    world = SensorimotorWorld(cfg, rng)
    out = [world.reset()]
    for _ in range(n_steps):
        out.append(world.step(int(rng.integers(world.n_actions))))
    return np.array(out)


def test_emission_is_nonlinear_and_bounded():
    # With zero sensor noise the clean emission is tanh(...) and must lie in [-1, 1],
    # even for latents driven far from the origin — a linear map would not saturate.
    cfg = Config(sensor_noise_std=0.0, action_scale=5.0)
    rng = np.random.default_rng(0)
    world = SensorimotorWorld(cfg, rng)
    obs = [world.reset()]
    for _ in range(40):
        obs.append(world.step(int(rng.integers(world.n_actions))))
    arr = np.array(obs)
    assert np.all(np.abs(arr) <= 1.0 + 1e-9)
    assert np.max(np.abs(arr)) > 0.9  # actually approaches saturation (genuinely nonlinear)


def test_identical_seed_identical_stream():
    a = _stream(123)
    b = _stream(123)
    assert np.array_equal(a, b)


def test_different_seed_differs():
    a = _stream(1)
    b = _stream(2)
    assert not np.array_equal(a, b)


def test_hidden_state_never_exposed():
    cfg = Config()
    world = SensorimotorWorld(cfg, np.random.default_rng(0))
    world.reset()
    # No public attribute leaks the latent dimensionality, latents, or matrices.
    public = [n for n in vars(world) if not n.startswith("_")]
    assert public == []
    assert not hasattr(world, "true_dim")
    # The action/observation-space sizes ARE legitimately known to the agent.
    assert world.obs_dim == cfg.obs_dim
    assert world.n_actions == cfg.n_actions


def test_observation_dimension():
    obs = _stream(7, n_steps=1)
    assert obs.shape[1] == Config().obs_dim
