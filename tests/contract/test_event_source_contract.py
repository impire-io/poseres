"""T016 — EventSource seam: determinism, substitutability, no hidden-state leak."""

from __future__ import annotations

import numpy as np

from pra.config import Config
from pra.core.bus import InMemorySyncBus
from pra.core.contracts import SensorimotorEvent
from pra.core.engine import Engine
from pra.core.frame import FrameStore
from pra.world.event_source import EventSource, SensorimotorWorld


def test_identical_seed_identical_observation_stream():
    cfg = Config()

    def stream(seed):
        rng = np.random.default_rng(seed)
        w = SensorimotorWorld(cfg, rng)
        seq = [w.reset()]
        for _ in range(30):
            seq.append(w.step(int(rng.integers(w.n_actions))))
        return np.array(seq)

    assert np.array_equal(stream(5), stream(5))


def test_world_satisfies_protocol():
    w = SensorimotorWorld(Config(), np.random.default_rng(0))
    assert isinstance(w, EventSource)


class ConstantWorld:
    """A trivial substitute EventSource: a fixed observation, fixed action space."""

    def __init__(self, config, rng):
        self._obs = rng.standard_normal(config.obs_dim)
        self._n_actions = config.n_actions

    @property
    def n_actions(self):
        return self._n_actions

    @property
    def obs_dim(self):
        return self._obs.shape[0]

    def reset(self):
        return self._obs.copy()

    def step(self, action):
        return self._obs.copy()


def test_substitute_source_accepted_by_engine_unchanged():
    cfg = Config(
        warmup_episodes=3,
        n_cycles=2,
        episodes_per_cycle=1,
        steps_per_episode=8,
        horizon_checkpoints=(1, 2),
    )
    engine = Engine(cfg, world_factory=ConstantWorld)
    summary = engine.run(1)
    assert summary.final_population > 0  # engine ran end-to-end on the substitute


def test_no_hidden_state_leaks_into_frame_results():
    cfg = Config()
    store = FrameStore(cfg, np.random.default_rng(0))
    for d in (3, 4):
        store.birth(dim=d, ema_init=1.0)
    bus = InMemorySyncBus(store)
    for s in store.frame_states():
        bus.register(s.frame_id)
    rng = np.random.default_rng(1)
    prev = rng.standard_normal(cfg.obs_dim)
    obs = rng.standard_normal(cfg.obs_dim)
    results = bus.publish(SensorimotorEvent(observation=obs, previous_observation=prev, action=0))
    # FrameResult carries only the contract fields — no true_dim/latent/matrix.
    allowed = {"frame_id", "mapped", "local_pose", "recon_error", "pred_error", "effort"}
    for r in results:
        assert set(vars(r)) == allowed
