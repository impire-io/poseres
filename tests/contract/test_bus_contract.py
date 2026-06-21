"""T013 — Bus seam: ascending-frame_id delivery, delivery-only, substitutable."""

from __future__ import annotations

import numpy as np

from pra.config import Config
from pra.core.bus import Bus, InMemorySyncBus
from pra.core.contracts import FrameResult, SensorimotorEvent
from pra.core.engine import Engine
from pra.core.frame import FrameStore


def _store_with_frames(dims, seed=0):
    store = FrameStore(Config(), np.random.default_rng(seed))
    for d in dims:
        store.birth(dim=d, ema_init=1.0)
    return store


def test_publish_returns_results_in_ascending_frame_id_order():
    store = _store_with_frames([3, 5, 3, 4])  # frame_ids 0..3 across dims
    bus = InMemorySyncBus(store)
    for fid in store_frame_ids(store):
        bus.register(fid)
    obs = np.random.default_rng(1).standard_normal(Config().obs_dim)
    results = bus.publish(SensorimotorEvent(observation=obs))
    ids = [r.frame_id for r in results]
    assert ids == sorted(ids)
    assert ids == store_frame_ids(store)
    assert all(isinstance(r, FrameResult) for r in results)


def test_register_unregister_maintain_order_and_exactly_once():
    store = _store_with_frames([3, 3, 3])
    bus = InMemorySyncBus(store)
    bus.register(2)
    bus.register(0)
    bus.register(1)
    assert bus.subscribers() == [0, 1, 2]
    bus.unregister(1)
    assert bus.subscribers() == [0, 2]


def test_publish_delivers_to_every_subscriber_exactly_once():
    store = _store_with_frames([3, 4])
    bus = InMemorySyncBus(store)
    for fid in store_frame_ids(store):
        bus.register(fid)
    obs = np.random.default_rng(2).standard_normal(Config().obs_dim)
    results = bus.publish(SensorimotorEvent(observation=obs))
    assert [r.frame_id for r in results] == store_frame_ids(store)


def test_recording_double_substitutes_for_the_bus_in_the_engine():
    """A custom Bus implementation is accepted by the Engine unchanged (delivery
    is delegated to the batched FrameStore; the Bus only orders/records)."""
    registrations: list[int] = []

    class RecordingBus(InMemorySyncBus):
        def register(self, frame_id: int) -> int:
            registrations.append(frame_id)
            return super().register(frame_id)

    cfg = Config(
        warmup_episodes=3,
        n_cycles=2,
        episodes_per_cycle=1,
        steps_per_episode=10,
        horizon_checkpoints=(1, 2),
    )
    engine = Engine(cfg, bus_factory=RecordingBus)
    summary = engine.run(1)
    assert summary.final_population > 0
    # Every frame was registered through the substitute bus; births >= survivors.
    assert len(registrations) >= summary.final_population
    # The substitute satisfies the Bus protocol.
    assert isinstance(RecordingBus(_store_with_frames([3])), Bus)


def test_identical_seed_identical_published_results():
    cfg = Config()
    obs = np.random.default_rng(9).standard_normal(cfg.obs_dim)
    event = SensorimotorEvent(observation=obs)
    out = []
    for _ in range(2):
        store = _store_with_frames([3, 4, 5], seed=42)
        bus = InMemorySyncBus(store)
        for fid in store_frame_ids(store):
            bus.register(fid)
        out.append([(r.frame_id, r.mapped, r.recon_error) for r in bus.publish(event)])
    assert out[0] == out[1]


# --- helpers ---------------------------------------------------------------
def store_frame_ids(store: FrameStore) -> list[int]:
    return [s.frame_id for s in store.frame_states()]
