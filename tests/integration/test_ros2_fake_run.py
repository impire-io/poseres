"""T005/T008 — the engine on a scripted ROS2 world (contracts C4, C5).

Full engine runs over the fake transport: normal summaries, byte-identity,
the continuous single-boot contract, and the honest snapshot failure for a
world whose state is a physical room (Doc 06 §5b class 4). Small budgets
throughout — these check contracts, never the science."""

from __future__ import annotations

from types import SimpleNamespace as NS

import numpy as np
import pytest

from pra.anatomy.ros2 import ActuatorSpec, FakeTransport, Ros2Body, SensorSpec
from pra.config import Config
from pra.core.engine import Engine
from pra.persistence.store import InMemorySnapshotStore

SMALL = dict(
    warmup_episodes=2,
    n_cycles=3,
    episodes_per_cycle=2,
    steps_per_episode=10,
    horizon_checkpoints=(1, 3),
)

SENSORS = [
    SensorSpec(id="lidar", topic="/scan", width=5, extract="ranges"),
    SensorSpec(id="heading", topic="/heading", width=1, extract="data"),
]
ACTUATORS = [
    ActuatorSpec(
        id="drive",
        topic="/cmd_vel",
        presets=({"linear.x": 0.2}, {"angular.z": 0.6}, {"angular.z": -0.6}, {}),
    )
]


def _script(n: int = 2000, lidar_scale: float = 1.0) -> dict:
    # Deterministic, structured, non-constant streams — enough for the brain
    # to chew on, cheap to regenerate identically for a second transport.
    return {
        "/scan": {
            k: [NS(ranges=lidar_scale * (1.0 + 0.1 * np.sin(0.05 * k + np.arange(5.0))))]
            for k in range(n)
        },
        "/heading": {k: [NS(data=np.sin(0.02 * k))] for k in range(0, n, 3)},
    }


def _factory(**script_kw):
    return Ros2Body.factory(
        SENSORS, ACTUATORS, transport=lambda: FakeTransport(_script(**script_kw))
    )


def _cfg(**overrides) -> Config:
    return Config(obs_dim=6, n_actions=4, episode_mode="continuous", **SMALL, **overrides)


# ---- a normal run, reproduced byte-for-byte (C5.1) ------------------------------------


def test_full_run_completes_and_reproduces_byte_identically():
    first = Engine(_cfg(), world_factory=_factory()).run(1).serialize()
    again = Engine(_cfg(), world_factory=_factory()).run(1).serialize()
    assert first == again  # same script, config, seed -> byte-identical
    summary = Engine(_cfg(), world_factory=_factory()).run(1)
    assert summary.observation_steps > 0


def test_a_different_world_reaches_the_brain():
    base = Engine(_cfg(), world_factory=_factory()).run(1).serialize()
    other = Engine(_cfg(), world_factory=_factory(lidar_scale=2.0)).run(1).serialize()
    assert base != other  # the script is the world; changing it changes the run


def test_different_seeds_differ_on_the_same_world():
    a = Engine(_cfg(), world_factory=_factory()).run(1).serialize()
    b = Engine(_cfg(), world_factory=_factory()).run(2).serialize()
    assert a != b


# ---- the continuous single-boot contract (C4.1) -----------------------------------------


def test_continuous_run_boots_exactly_once_with_no_reset_traffic():
    mounted: list[Ros2Body] = []
    transport = FakeTransport(_script())
    inner = Ros2Body.factory(SENSORS, ACTUATORS, transport=transport)

    def factory(cfg, rng):
        body = inner(cfg, rng)
        mounted.append(body)
        return body

    summary = Engine(_cfg(), world_factory=factory).run(1)
    journal = transport.journal
    assert journal.count(("start",)) == 1  # a second start() would have raised
    assert ("reset",) not in journal
    assert summary.observation_steps > 0
    telemetry = mounted[0].telemetry()
    assert telemetry["ticks"] > 0
    assert telemetry["sensors"]["heading"]["staleness_total"] > 0  # the 1-in-3 topic, measured


def test_episodic_mode_works_when_the_transport_can_reset():
    factory = Ros2Body.factory(
        SENSORS, ACTUATORS, transport=lambda: FakeTransport(_script(), resettable=True)
    )
    cfg = Config(obs_dim=6, n_actions=4, episode_mode="episodic", **SMALL)
    assert (
        Engine(cfg, world_factory=factory).run(1).serialize()
        == Engine(cfg, world_factory=factory).run(1).serialize()
    )


# ---- persistence honesty (C5.4, Doc 06 §5b class 4) ---------------------------------------


def test_continuous_snapshotting_hits_the_engine_capture_required_error():
    cfg = _cfg(snapshot_every_n_cycles=1)
    engine = Engine(cfg, world_factory=_factory(), snapshot_store=InMemorySnapshotStore())
    with pytest.raises(RuntimeError, match="state_dict"):
        engine.run(1)


def test_the_adapter_declares_no_capture_and_no_marker():
    body = _factory()(_cfg(), np.random.default_rng(1))
    assert not hasattr(body, "state_dict")  # Body forwards capture iff the world has it
    assert body.snapshot_needs_state is False
