"""Feature 040 — the event head: per-action NLMS delta models owned by the
FrameStore (motivation-stack G3, episode 0071). Math, cold start, per-action
separation, resize, persistence keys, and the off-path's total absence."""

from __future__ import annotations

import copy

import numpy as np

from pra.config import Config
from pra.core.frame import FrameStore


def _store(eta: float = 0.5, obs_dim: int = 6, n_actions: int = 3) -> FrameStore:
    cfg = Config(obs_dim=obs_dim, n_actions=n_actions, event_head_eta=eta)
    return FrameStore(cfg, np.random.default_rng(0))


def test_off_store_has_no_head_state():
    store = _store(eta=0.0)
    assert store.event_head_on is False
    assert not hasattr(store, "_eh_W")
    assert "event_head" not in store.state_dict()


def test_cold_start_predicts_zero_delta():
    store = _store()
    obs = np.random.default_rng(1).standard_normal(6)
    for a in range(3):
        assert np.array_equal(store.event_predict(obs, a), np.zeros(6))


def test_update_matches_the_g3_prototype_arithmetic():
    # One hand-computed NLMS step: W += eta * outer(err, x) / (x @ x).
    store = _store(eta=0.5, obs_dim=2, n_actions=1)
    prev = np.array([1.0, 2.0])
    obs = np.array([1.5, 1.0])
    store.event_learn(prev, 0, obs)
    x = np.array([1.0, 2.0, 1.0])
    err = (obs - prev) - np.zeros(2)  # cold-start prediction is zero
    expected = 0.5 * np.outer(err, x) / float(x @ x)
    assert np.allclose(store._eh_W[0], expected)
    assert store.state_dict()["event_head"]["updates"] == 1


def test_nlms_converges_on_linear_per_action_dynamics():
    # Ground truth: action a adds a fixed delta vector; the head must learn it.
    rng = np.random.default_rng(2)
    store = _store(eta=0.5, obs_dim=4, n_actions=2)
    true_delta = {0: np.array([0.1, 0.0, -0.2, 0.0]), 1: np.array([0.0, 0.3, 0.0, 0.0])}
    for _ in range(300):
        a = int(rng.integers(2))
        prev = rng.standard_normal(4)
        store.event_learn(prev, a, prev + true_delta[a])
    probe = rng.standard_normal(4)
    for a in range(2):
        assert np.allclose(store.event_predict(probe, a), true_delta[a], atol=1e-3)


def test_per_action_separation():
    store = _store(eta=0.5, obs_dim=3, n_actions=2)
    rng = np.random.default_rng(3)
    for _ in range(50):
        prev = rng.standard_normal(3)
        store.event_learn(prev, 0, prev + 1.0)
    # action 1 never learned: still the cold-start zero predictor
    assert np.array_equal(store._eh_W[1], np.zeros_like(store._eh_W[1]))
    assert np.array_equal(store.event_predict(np.ones(3), 1), np.zeros(3))


def test_resize_preserves_entries_zero_inits_growth_and_draws_no_rng():
    store = _store(eta=0.5, obs_dim=3, n_actions=2)
    rng_learn = np.random.default_rng(4)
    for _ in range(20):
        prev = rng_learn.standard_normal(3)
        store.event_learn(prev, 0, prev + 0.5)
    old = np.array(store._eh_W, copy=True)
    state_before = copy.deepcopy(store.rng.bit_generator.state)
    store.resize(5, 3, store.rng)  # grow both axes (no frames alive: no draws)
    assert store.rng.bit_generator.state == state_before  # the head drew nothing
    assert store._eh_W.shape == (3, 5, 6)
    assert np.array_equal(store._eh_W[:2, :3, :3], old[:, :, :3])  # entries bit-for-bit
    assert np.array_equal(store._eh_W[:2, :3, 5], old[:, :, 3])  # bias column travels
    assert np.array_equal(store._eh_W[2], np.zeros((5, 6)))  # new action zero-init
    assert np.array_equal(store._eh_W[:, 3:5, :], np.zeros((3, 2, 6)))  # new rows zero
    grown = np.array(store._eh_W, copy=True)
    store.resize(3, 2, store.rng)  # shrink back: truncate
    assert store._eh_W.shape == (2, 3, 4)
    assert np.array_equal(store._eh_W[:, :, :3], grown[:2, :3, :3])
    assert np.array_equal(store._eh_W[:, :, 3], grown[:2, :3, 5])


def test_state_dict_roundtrip_and_cold_start_on_absent_key():
    store = _store(eta=0.5, obs_dim=3, n_actions=2)
    prev = np.array([1.0, 0.0, -1.0])
    store.event_learn(prev, 1, prev + 0.25)
    state = store.state_dict()
    fresh = _store(eta=0.5, obs_dim=3, n_actions=2)
    fresh.load_state_dict(state)
    assert np.array_equal(fresh._eh_W, store._eh_W)
    assert fresh._eh_updates == 1
    # absent key (pre-040 / head-off blob) with the head enabled: cold start
    state.pop("event_head")
    refilled = _store(eta=0.5, obs_dim=3, n_actions=2)
    refilled.load_state_dict(state)
    assert np.array_equal(refilled._eh_W, np.zeros((2, 3, 4)))
    assert refilled._eh_updates == 0
