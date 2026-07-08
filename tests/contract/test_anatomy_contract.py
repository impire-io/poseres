"""T006 — anatomy seams: substitutability, EventSource compatibility, feedback rule."""

from __future__ import annotations

import numpy as np

from pra.anatomy.body import Actuator, Body, ConstantSensor, Sensor, WorldActuator, WorldSensor
from pra.config import Config
from pra.core.engine import Engine
from pra.world.event_source import EventSource, SensorimotorWorld


class SineSensor:
    """A substitute sensor implementation — accepted unchanged."""

    def __init__(self):
        self._t = 0

    def id(self):
        return "sine"

    def width(self):
        return 2

    def read(self):
        self._t += 1
        return np.array([np.sin(self._t / 10.0), np.cos(self._t / 10.0)])


class CounterActuator:
    def __init__(self):
        self.count = 0

    def id(self):
        return "counter"

    def action_count(self):
        return 2

    def apply(self, local):
        self.count += 1  # note: returns None — no feedback channel (Doc 02 §4.2)


def _mounted_body(config, rng):
    world = SensorimotorWorld(config, rng)
    ws = WorldSensor(world)
    return Body(world, sensors=[ws], actuators=[WorldActuator(world, ws)])


def test_substitute_parts_satisfy_the_protocols():
    assert isinstance(SineSensor(), Sensor)
    assert isinstance(CounterActuator(), Actuator)
    assert isinstance(ConstantSensor("c", [0.0]), Sensor)


def test_body_satisfies_the_event_source_seam():
    body = _mounted_body(Config(), np.random.default_rng(0))
    assert isinstance(body, EventSource)


def test_engine_accepts_a_body_with_substitute_parts():
    cfg = Config(
        warmup_episodes=3,
        n_cycles=2,
        episodes_per_cycle=1,
        steps_per_episode=10,
        horizon_checkpoints=(1, 2),
        obs_dim=12,  # world 10 + sine 2
        n_actions=6,  # world 4 + counter 2
    )
    counters = []

    def factory(config, rng):
        world_cfg = config.replace(obs_dim=10, n_actions=4)
        world = SensorimotorWorld(world_cfg, rng)
        ws = WorldSensor(world)
        actuator = CounterActuator()
        counters.append(actuator)
        return Body(
            world,
            sensors=[ws, SineSensor()],
            actuators=[WorldActuator(world, ws), actuator],
        )

    summary = Engine(cfg, world_factory=factory).run(1)
    assert summary.final_population > 0  # ran end-to-end on the composed body
    assert counters[0].count > 0  # the substitute actuator was actually driven


def test_actuator_apply_returns_nothing():
    a = CounterActuator()
    assert a.apply(0) is None  # the only feedback path is subsequent observations
