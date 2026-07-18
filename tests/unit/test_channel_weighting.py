"""Learned channel weighting (feature 016) — estimator math, weighted-path
identities, readiness/resize behavior, and the no-RNG twin proof
(contracts/channel-weighting.md C1–C3, C6)."""

from __future__ import annotations

import numpy as np

from pra.config import Config
from pra.core.frame import FrameGroup, FrameStore
from pra.world.event_source import SensorimotorWorld

ON = dict(channel_weight_floor=0.2, channel_stats_decay=0.99)  # ready at 100 steps


def _store(obs_dim: int = 4, **kw) -> FrameStore:
    cfg = Config(obs_dim=obs_dim, **kw)
    return FrameStore(cfg, np.random.default_rng(0))


def _drive(store: FrameStore, obs_seq: np.ndarray, steps_per_episode: int = 40) -> None:
    """Feed a stream through online_step the way the engine does (prev_obs
    None at episode starts; the store may hold zero frames)."""
    prev = None
    for t, obs in enumerate(obs_seq):
        if t % steps_per_episode == 0:
            prev = None
        store.online_step(obs, prev, 0 if prev is not None else None, "predictive")
        prev = obs


def test_estimator_separates_structured_from_white_channels():
    rng = np.random.default_rng(7)
    n = 600
    t = np.arange(n)
    obs_seq = np.stack(
        [
            np.sin(t / 10.0),  # strongly autocorrelated
            0.5 * np.cos(t / 7.0) + 0.01 * rng.standard_normal(n),  # structured + jitter
            rng.standard_normal(n),  # white
            rng.standard_normal(n) * 3.0,  # white, larger amplitude (invariance)
        ],
        axis=1,
    )
    store = _store(**ON)
    _drive(store, obs_seq)
    store._cw_recompute()
    w = store.channel_weights
    assert w is not None
    assert w[0] > 0.9 and w[1] > 0.9
    assert w[2] == 0.2 and w[3] == 0.2  # clipped to the floor, amplitude-invariant


def test_weights_stay_full_until_ready():
    store = _store(**ON)
    rng = np.random.default_rng(3)
    _drive(store, rng.standard_normal((50, 4)))  # 50 < ready_at = 100
    store._cw_recompute()
    assert np.array_equal(store.channel_weights, np.ones(4))


def test_all_ones_weights_are_bit_equal_to_the_unweighted_path():
    rng = np.random.default_rng(1)
    g = FrameGroup(3, 6, 8, 2)
    g.add_frame(0, ema_init=1.0, scale=0.1, rng=rng)
    obs, prev = rng.standard_normal(6), rng.standard_normal(6)
    ones = np.ones(6)
    for a, b in zip(g.fit_quality(obs), g.fit_quality(obs, ones), strict=True):
        np.testing.assert_array_equal(a, b)
    np.testing.assert_array_equal(
        g.honest_pred_err(prev, 1, obs), g.honest_pred_err(prev, 1, obs, ones)
    )
    np.testing.assert_array_equal(g.encode(obs)[0], g.encode(obs, ones)[0])


def test_zero_weight_removes_exactly_that_channel_from_both_norms():
    rng = np.random.default_rng(2)
    g = FrameGroup(2, 5, 8, 2)
    g.add_frame(0, ema_init=1.0, scale=0.1, rng=rng)
    obs = rng.standard_normal(5)
    w = np.ones(5)
    w[3] = 0.0
    fit, pose, _, recon, _ = g.fit_quality(obs, w)
    keep = [0, 1, 2, 4]
    expected = np.linalg.norm((recon - obs)[:, keep], axis=1) / (np.linalg.norm(obs[keep]) + 1e-6)
    np.testing.assert_allclose(fit, expected, rtol=1e-12)


def test_weighted_learning_uses_weighted_error_and_input():
    """A channel with weight 0 must contribute nothing to any gradient: its
    decoder row bias never moves, and learning is identical whatever value
    that channel carries."""
    w = np.ones(5)
    w[2] = 0.0

    def learned_weights(channel2_value: float):
        g = FrameGroup(2, 5, 8, 2)
        g.add_frame(0, ema_init=1.0, scale=0.1, rng=np.random.default_rng(11))
        obs = rng2.standard_normal(5)
        obs[2] = channel2_value
        elect = np.ones(1, dtype=bool)
        fit, pose, h, recon, hd = g.fit_quality(obs, w)
        g.learn_placement(obs, pose, h, recon, hd, elect, 0.05, 1.0, w)
        return g

    rng2 = np.random.default_rng(5)
    a = learned_weights(0.0)
    rng2 = np.random.default_rng(5)
    b = learned_weights(123.0)
    for name in ("W1", "b1", "W2", "b2", "Dc1", "dc1", "Dc2", "dc2"):
        np.testing.assert_array_equal(getattr(a, name), getattr(b, name))
    assert a.dc2[0, 2] == 0.0  # the silenced channel's decoder bias never moved


def test_resize_extends_stats_with_full_weight_and_truncates_on_shrink():
    store = _store(**ON)
    rng = np.random.default_rng(6)
    _drive(store, rng.standard_normal((200, 4)))
    store._cw_recompute()
    assert store.channel_weights[2] == 0.2  # white channel at the floor
    store.resize(6, 2, np.random.default_rng(9))
    w = store.channel_weights
    assert len(w) == 6 and w[4] == 1.0 and w[5] == 1.0  # new channels: full voice
    assert store._cw_n[4] == 0.0
    store.resize(3, 2, np.random.default_rng(9))
    assert len(store.channel_weights) == 3


def test_state_dict_roundtrip_carries_estimator_state_and_refills_when_absent():
    store = _store(**ON)
    rng = np.random.default_rng(8)
    _drive(store, rng.standard_normal((150, 4)))
    state = store.state_dict()
    assert "channel_stats" in state
    twin = _store(**ON)
    twin.load_state_dict(state)
    np.testing.assert_array_equal(twin.channel_weights, store.channel_weights)
    np.testing.assert_array_equal(twin._cw_n, store._cw_n)
    # a pre-016-shaped state (no channel_stats) → stated refill: fresh init
    state.pop("channel_stats")
    twin.load_state_dict(state)
    np.testing.assert_array_equal(twin.channel_weights, np.ones(4))
    assert twin._cw_n.sum() == 0.0


def test_off_store_allocates_nothing_and_serializes_nothing():
    store = _store()  # default: floor 0.0 = off
    assert store.channel_weights is None
    assert store.channel_weighting_summary() is None
    assert "channel_stats" not in store.state_dict()
    assert not hasattr(store, "_cw_m")


class _RecordingWorld:
    """Reference world wrapper recording every emitted observation."""

    def __init__(self, cfg, rng, log):
        self._w = SensorimotorWorld(cfg, rng)
        self._log = log

    @property
    def n_actions(self):
        return self._w.n_actions

    @property
    def obs_dim(self):
        return self._w.obs_dim

    def reset(self):
        obs = self._w.reset()
        self._log.append(obs.copy())
        return obs

    def step(self, action):
        obs = self._w.step(action)
        self._log.append(obs.copy())
        return obs


def test_twin_engines_on_vs_off_see_identical_world_streams():
    """The no-RNG contract (C3): the feature consumes zero random draws, so
    the ON run's world emissions — every draw the shared generator makes —
    are bit-identical to the OFF run's for the whole life of the run."""
    from pra.core.engine import Engine

    small = dict(
        warmup_episodes=2,
        n_cycles=3,
        episodes_per_cycle=2,
        steps_per_episode=10,
        horizon_checkpoints=(1, 3),
    )
    streams: dict[str, list] = {"on": [], "off": []}

    def factory_for(key):
        def factory(cfg, rng):
            return _RecordingWorld(cfg, rng, streams[key])

        return factory

    Engine(Config(**small, **ON), world_factory=factory_for("on")).run(1)
    Engine(Config(**small), world_factory=factory_for("off")).run(1)
    assert len(streams["on"]) == len(streams["off"])
    for a, b in zip(streams["on"], streams["off"], strict=True):
        np.testing.assert_array_equal(a, b)
