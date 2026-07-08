"""T005 — body composition: order, widths, routing, rejections (Doc 02 §3-§5)."""

from __future__ import annotations

import numpy as np
import pytest

from pra.anatomy.body import AnatomyError, Body, ConstantSensor


class SpyActuator:
    def __init__(self, actuator_id, count):
        self._id = actuator_id
        self._count = count
        self.applied: list[int] = []

    def id(self):
        return self._id

    def action_count(self):
        return self._count

    def apply(self, local):
        self.applied.append(local)


class NullEnvironment:
    def reset(self):
        return None


def _body(sensors=None, actuators=None):
    sensors = sensors or [ConstantSensor("a", [1.0, 2.0]), ConstantSensor("b", [3.0])]
    actuators = actuators or [SpyActuator("m1", 2), SpyActuator("m2", 3)]
    return Body(NullEnvironment(), sensors, actuators), sensors, actuators


def test_observation_is_fixed_order_concatenation():
    body, _, _ = _body()
    assert body.obs_dim == 3
    obs = body.reset()
    assert np.array_equal(obs, [1.0, 2.0, 3.0])  # declared order, exact widths


def test_action_space_is_fixed_order_disjoint_union():
    body, _, actuators = _body()
    m1, m2 = actuators
    assert body.n_actions == 5
    # routing table: 0,1 -> m1 local 0,1 ; 2,3,4 -> m2 local 0,1,2
    for global_a, (target, local) in enumerate([(m1, 0), (m1, 1), (m2, 0), (m2, 1), (m2, 2)]):
        actuator, routed = body.route(global_a)
        assert actuator is target and routed == local
    body.step(3)
    assert m2.applied == [1] and m1.applied == []


def test_out_of_range_action_rejected():
    body, _, _ = _body()
    with pytest.raises(AnatomyError, match="outside"):
        body.route(5)


def test_wrong_width_read_fails_naming_the_sensor():
    class LyingSensor:
        def id(self):
            return "liar"

        def width(self):
            return 3

        def read(self):
            return np.zeros(2)  # narrower than declared

    body = Body(NullEnvironment(), [LyingSensor()], [SpyActuator("m", 1)])
    with pytest.raises(AnatomyError, match="liar"):
        body.reset()


def test_duplicate_tool_id_rejected():
    body, _, _ = _body()
    with pytest.raises(AnatomyError, match="duplicate"):
        body.register_sensor(ConstantSensor("a", [0.0]))  # active id
    body.register_sensor(ConstantSensor("new", [0.0]))
    with pytest.raises(AnatomyError, match="duplicate"):
        body.register_sensor(ConstantSensor("new", [1.0]))  # queued id


def test_last_sensor_and_actuator_protected():
    body = Body(NullEnvironment(), [ConstantSensor("only", [0.0])], [SpyActuator("m", 1)])
    body.deregister("only")
    with pytest.raises(AnatomyError, match="last sensor"):
        body.apply_pending_tools()


def test_registration_is_deferred_to_apply():  # SC-005
    body, _, _ = _body()
    before = body.obs_dim
    body.register_sensor(ConstantSensor("late", [9.0, 9.0]))
    assert body.obs_dim == before  # queued, not applied (C4)
    changed = body.apply_pending_tools()
    assert changed == (before + 2, body.n_actions)
    assert body.apply_pending_tools() is None  # queue drained


def test_deregister_shrinks_and_lists():
    body, sensors, _ = _body()
    body.deregister("b")
    body.apply_pending_tools()
    assert body.obs_dim == 2
    assert ("b", "sensor") not in body.list_tools()
    assert np.array_equal(body.reset(), [1.0, 2.0])
