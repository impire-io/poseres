"""T007/T009/T010 — mounting byte-identity, mid-run growth, baseline (feature 004)."""

from __future__ import annotations

import numpy as np

from pra.anatomy.body import Body, ConstantSensor, WorldActuator, WorldSensor
from pra.config import Config
from pra.core.engine import Engine
from pra.world.event_source import SensorimotorWorld


def _cfg(**overrides):
    base = dict(
        warmup_episodes=5,
        n_cycles=6,
        episodes_per_cycle=2,
        steps_per_episode=20,
        horizon_checkpoints=(3, 6),
    )
    base.update(overrides)
    return Config(**base)


def _body_factory(config, rng):
    world = SensorimotorWorld(config, rng)
    ws = WorldSensor(world)
    return Body(world, sensors=[ws], actuators=[WorldActuator(world, ws)])


class NoopActuator:
    def __init__(self, actuator_id="noop", count=2):
        self._id = actuator_id
        self._count = count

    def id(self):
        return self._id

    def action_count(self):
        return self._count

    def apply(self, local):
        return None  # acts on nothing; feedback only via sensors regardless


# --- US1: byte-identity of the mounted world ---------------------------------


def test_world_through_body_is_byte_identical():
    cfg = _cfg()
    direct = Engine(cfg).run(7)
    mounted = Engine(cfg, world_factory=_body_factory).run(7)
    assert mounted.serialize() == direct.serialize()  # SC-001


# --- US2: growth without forgetting -------------------------------------------


def test_midrun_growth_preserves_learning_and_determinism():
    cfg = _cfg()
    bodies = []

    def growing_factory(config, rng):
        body = _body_factory(config, rng)
        body.register_sensor(ConstantSensor("thermo", [0.5, -0.5, 0.25]))
        body.register_actuator(NoopActuator())
        bodies.append(body)
        return body

    grown = Engine(cfg, world_factory=growing_factory).run(7)
    body = bodies[0]
    assert body.obs_dim == 13 and body.n_actions == 6  # both dims grew
    assert grown.final_population > 0
    assert grown.loss_fraction < 0.15  # growth did not break the no-loss guard

    # byte-identical re-run of the whole growth schedule (SC-002)
    grown2 = Engine(cfg, world_factory=growing_factory).run(7)
    assert grown.serialize() == grown2.serialize()


def test_growth_preserves_existing_weights_bitwise():
    cfg = _cfg(n_cycles=2, horizon_checkpoints=(1, 2))
    world = SensorimotorWorld(cfg, np.random.default_rng(0))
    ws = WorldSensor(world)
    body = Body(world, sensors=[ws], actuators=[WorldActuator(world, ws)])

    # drive a real store to a learned state, snapshot a tensor, then grow
    from pra.core.frame import FrameStore

    store = FrameStore(cfg, np.random.default_rng(0))
    store.birth(dim=3, ema_init=1.0)
    obs = np.random.default_rng(1).standard_normal(10)
    fit, pose, h, recon, hd = store._groups[3].fit_quality(obs)
    store._groups[3].learn_placement(obs, pose, h, recon, hd, np.ones(1, bool), 0.03, 1.0)
    w1_learned = np.array(store._groups[3].W1, copy=True)

    body.register_sensor(ConstantSensor("extra", [1.0]))
    new_obs, new_act = body.apply_pending_tools()
    store.resize(new_obs, new_act, np.random.default_rng(2))

    assert store._groups[3].W1.shape[2] == 11
    assert np.array_equal(store._groups[3].W1[:, :, :10], w1_learned)  # nothing forgotten


def test_registration_mid_episode_defers_to_slow_loop():
    cfg = _cfg()
    world = SensorimotorWorld(cfg, np.random.default_rng(0))
    ws = WorldSensor(world)
    body = Body(world, sensors=[ws], actuators=[WorldActuator(world, ws)])
    body.reset()
    body.register_sensor(ConstantSensor("late", [9.0]))
    obs = body.step(0)  # mid-episode: still the old width (SC-005)
    assert obs.shape == (10,)
    body.apply_pending_tools()  # the slow-loop boundary
    assert body.step(0).shape == (11,)


# --- US3: baseline untouched ----------------------------------------------------


def test_baseline_unchanged():
    s = Engine(Config()).run(1)
    assert round(s.pred_error_early, 4) == 0.4465
    assert round(s.pred_error_late, 4) == 0.1574
    readings = {c: (r.best_dim, r.population_size) for c, r in s.checkpoints.items()}
    assert readings == {18: (3, 19), 30: (3, 24), 50: (4, 27)}  # SC-003
