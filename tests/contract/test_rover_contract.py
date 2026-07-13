"""Rover contracts (feature 006, contracts/rover.md §§1–3) — EventSource
conformance, ground-truth hiding, and tap coherence outside a run.
"""

from __future__ import annotations

import numpy as np

from pra.config import Config
from pra.examples.rover.viewer import RoverTelemetry
from pra.examples.rover.world import RoverWorld, make_rover_body
from pra.world.event_source import EventSource


def test_rover_body_satisfies_event_source():
    body = make_rover_body(Config(), np.random.default_rng(1))
    assert isinstance(body, EventSource)
    obs = body.reset()
    assert obs.shape == (10,) and obs.dtype == np.float64
    nxt = body.step(0)
    assert nxt.shape == (10,) and nxt.dtype == np.float64


def test_system_surface_hides_ground_truth():
    """The engine holds only the Body — nothing on it exposes pose, map, or
    layout (FR-005); the world's `layout()` accessor is harness/viewer-only."""
    body = make_rover_body(Config(), np.random.default_rng(1))
    for name in ("layout", "pose", "sense", "apply"):
        assert not hasattr(body, name)
    world = RoverWorld(Config(), np.random.default_rng(1))
    layout = world.layout()
    assert set(layout) >= {"arena_half", "obstacles", "spawns", "actions", "sensors"}


def test_tap_snapshot_is_coherent_before_any_run():
    tap = RoverTelemetry(Config())
    snap = tap.snapshot()
    assert snap == {
        "step": 0,
        "episode": 0,
        "pose": None,
        "bump": 0,
        "trail": [],
        "done": False,
        "final": None,
        "learning": None,
    }
    assert tap.snapshot() == snap  # snapshotting never mutates the tap


def test_tap_records_are_plain_value_copies():
    tap = RoverTelemetry(Config())
    tap.record_reset(0.1, 0.2, 0.3)
    tap.record_step(0.15, 0.2, 0.3, 1)
    snap = tap.snapshot()
    assert snap["episode"] == 1 and snap["step"] == 1
    assert snap["pose"] == [0.15, 0.2, 0.3] and snap["bump"] == 1
    assert snap["trail"] == [[0.1, 0.2], [0.15, 0.2]]
    tap.record_reset(0.5, 0.5, 0.0)  # a new episode clears the trail
    assert tap.snapshot()["trail"] == [[0.5, 0.5]]


def test_bus_factory_returns_the_stock_bus():
    from pra.core.bus import InMemorySyncBus
    from pra.core.frame import FrameStore

    tap = RoverTelemetry(Config())
    store = FrameStore(Config(), np.random.default_rng(1))
    bus = tap.bus_factory(store)
    assert type(bus) is InMemorySyncBus  # pass-through capture: no wrapper, no drift
    assert tap._store is store
