"""T001/T002 — the declaration layer and the fake transport (contracts C1).

Everything here runs with duck-typed message objects (`SimpleNamespace`): the
declaration layer must never need ROS2 (research R5), and the fake transport
is the journaling instrument every later contract test reads.
"""

from __future__ import annotations

from types import SimpleNamespace as NS

import numpy as np
import pytest

from pra.anatomy.body import AnatomyError
from pra.anatomy.ros2 import ActuatorSpec, FakeTransport, SensorSpec, apply_fields, extract_vector

# ---- declaration validation (C1.1) ------------------------------------------------


def test_sensor_spec_rejects_empty_and_malformed_fields():
    with pytest.raises(AnatomyError, match="non-empty"):
        SensorSpec(id="", topic="/scan", width=5)
    with pytest.raises(AnatomyError, match="topic"):
        SensorSpec(id="lidar", topic="", width=5)
    with pytest.raises(AnatomyError, match="width"):
        SensorSpec(id="lidar", topic="/scan", width=0)
    with pytest.raises(AnatomyError, match="dotted attribute path"):
        SensorSpec(id="lidar", topic="/scan", width=5, extract="ranges..bad")


def test_actuator_spec_rejects_empty_and_malformed_presets():
    with pytest.raises(AnatomyError, match="at least one preset"):
        ActuatorSpec(id="drive", topic="/cmd_vel", presets=())
    with pytest.raises(AnatomyError, match="dotted field path"):
        ActuatorSpec(id="drive", topic="/cmd_vel", presets=({"linear..x": 1.0},))
    with pytest.raises(AnatomyError, match="numeric"):
        ActuatorSpec(id="drive", topic="/cmd_vel", presets=({"linear.x": "fast"},))
    with pytest.raises(AnatomyError, match="numeric"):
        ActuatorSpec(id="drive", topic="/cmd_vel", presets=({"linear.x": True},))


def test_empty_preset_is_a_valid_all_defaults_command():
    spec = ActuatorSpec(id="drive", topic="/cmd_vel", presets=({},))
    assert spec.presets == ({},)


# ---- extraction and flattening (C1.2) ------------------------------------------------


def _spec(width: int, extract="") -> SensorSpec:
    return SensorSpec(id="s", topic="/t", width=width, extract=extract)


def test_whole_payload_array_extracts_c_order_float64():
    vec = extract_vector(np.arange(6, dtype=np.float32).reshape(2, 3), _spec(6))
    assert vec.dtype == np.float64
    assert vec.tolist() == [0.0, 1.0, 2.0, 3.0, 4.0, 5.0]  # C-order


def test_dotted_path_reaches_nested_attributes():
    msg = NS(pose=NS(pose=NS(position=NS(x=1.0, y=2.0, z=3.0))))
    assert extract_vector(msg, _spec(1, "pose.pose.position.x")).tolist() == [1.0]
    vec = extract_vector(msg, _spec(3, "pose.pose.position"))
    assert vec.tolist() == [1.0, 2.0, 3.0]


def test_compound_table_quaternion_pose_and_twist():
    quat = NS(x=0.0, y=0.0, z=0.7, w=0.7)
    assert extract_vector(quat, _spec(4)).tolist() == [0.0, 0.0, 0.7, 0.7]
    pose = NS(position=NS(x=1.0, y=2.0, z=0.0), orientation=quat)
    assert extract_vector(pose, _spec(7)).tolist() == [1.0, 2.0, 0.0, 0.0, 0.0, 0.7, 0.7]
    twist = NS(linear=NS(x=0.2, y=0.0, z=0.0), angular=NS(x=0.0, y=0.0, z=0.5))
    assert extract_vector(twist, _spec(6)).tolist() == [0.2, 0.0, 0.0, 0.0, 0.0, 0.5]


def test_scalar_and_sequence_payloads_flatten():
    assert extract_vector(NS(data=3.5), _spec(1, "data")).tolist() == [3.5]
    assert extract_vector([1.0, (2.0, 3.0)], _spec(3)).tolist() == [1.0, 2.0, 3.0]


def test_callable_extract_is_the_escape_hatch():
    vec = extract_vector(NS(a=1.0, b=2.0), _spec(2, extract=lambda m: [m.a, m.b]))
    assert vec.tolist() == [1.0, 2.0]


def test_width_mismatch_names_topic_and_both_shapes():
    with pytest.raises(AnatomyError, match=r"'/t'.*width 5.*3 value"):
        extract_vector(np.zeros(3), _spec(5))


def test_missing_attribute_path_names_the_failure_point():
    with pytest.raises(AnatomyError, match=r"no attribute path 'ranges'"):
        extract_vector(NS(data=1.0), _spec(5, "ranges"))


def test_non_numeric_payload_is_loud_never_a_silent_cast():
    with pytest.raises(AnatomyError, match="not a fixed-width numeric vector"):
        extract_vector(NS(data="fast"), _spec(1, "data"))
    with pytest.raises(AnatomyError, match="not a fixed-width numeric vector"):
        extract_vector(NS(data=None), _spec(1, "data"))


def test_non_finite_values_are_loud_pointing_at_the_escape_hatch():
    # A real lidar's no-hit beams are +inf, below-min-range beams are -inf,
    # invalid returns are NaN — the learning surface has no missing-data
    # semantics, so all three are delivery errors naming the fix (found by
    # the Gazebo worked example, hq/04-JOURNEY/0026).
    for bad in (np.inf, -np.inf, np.nan):
        with pytest.raises(AnatomyError, match=r"non-finite.*callable extract="):
            extract_vector(np.array([1.0, bad, 3.0]), _spec(3))
    # sanitized in a callable extract: fine — the choice is declared
    vec = extract_vector(
        np.array([1.0, np.inf, 3.0]),
        _spec(3, extract=lambda m: np.clip(m, 0.0, 10.0)),
    )
    assert vec.tolist() == [1.0, 10.0, 3.0]


# ---- preset building (C1.2) -----------------------------------------------------------


def test_apply_fields_sets_nested_fields_and_keeps_target_types():
    msg = NS(linear=NS(x=0.0, y=0.0, z=0.0), angular=NS(x=0.0, y=0.0, z=0.0))
    apply_fields(msg, {"linear.x": 1, "angular.z": -0.5})
    assert msg.linear.x == 1.0 and isinstance(msg.linear.x, float)  # int coerced to field type
    assert msg.angular.z == -0.5


def test_apply_fields_rejects_a_field_the_message_lacks():
    with pytest.raises(AnatomyError, match=r"'linear\.q' does not exist"):
        apply_fields(NS(linear=NS(x=0.0)), {"linear.q": 1.0})


# ---- the fake transport (T002: journal, guards, reset mechanics) -------------------------


def _scan(width=2, value=1.0):
    return NS(ranges=np.full(width, value))


def test_fake_transport_delivers_scripted_payloads_per_tick_in_order():
    got: list[float] = []
    spec = SensorSpec(id="lidar", topic="/scan", width=2, extract="ranges")
    transport = FakeTransport(script={"/scan": {0: [_scan(value=1.0)], 2: [_scan(value=3.0)]}})
    transport.subscribe(spec, lambda m: got.append(float(m.ranges[0])))
    transport.start()
    for _ in range(3):
        transport.tick()
    assert got == [1.0, 3.0]  # tick 0 and tick 2; tick 1 silent
    assert [e for e in transport.journal if e[0] == "tick"] == [
        ("tick", 0),
        ("tick", 1),
        ("tick", 2),
    ]
    assert transport.journal.count(("deliver", "/scan")) == 2


def test_fake_transport_delivers_only_to_subscribed_topics():
    transport = FakeTransport(script={"/noise": {0: [_scan()]}})
    transport.start()
    transport.tick()  # nothing subscribed: no delivery, no error — like a real graph
    assert ("deliver", "/noise") not in transport.journal


def test_second_start_raises_the_single_boot_contract():
    transport = FakeTransport()
    transport.start()
    with pytest.raises(AnatomyError, match="boots exactly once"):
        transport.start()


def test_publish_and_tick_before_start_are_loud():
    transport = FakeTransport()
    drive = ActuatorSpec(id="drive", topic="/cmd_vel", presets=({},))
    with pytest.raises(AnatomyError, match="before start"):
        transport.publish(drive, 0)
    with pytest.raises(AnatomyError, match="before start"):
        transport.tick()


def test_reset_requires_a_declared_mechanism_and_rewinds_the_script():
    plain = FakeTransport()
    assert not plain.can_reset
    with pytest.raises(AnatomyError, match="no reset mechanism"):
        plain.reset_world()

    got: list[float] = []
    spec = SensorSpec(id="lidar", topic="/scan", width=2, extract="ranges")
    transport = FakeTransport(script={"/scan": {0: [_scan(value=7.0)]}}, resettable=True)
    assert transport.can_reset
    transport.subscribe(spec, lambda m: got.append(float(m.ranges[0])))
    transport.start()
    transport.tick()
    transport.reset_world()  # the world restarts its script
    transport.tick()
    assert got == [7.0, 7.0] and ("reset",) in transport.journal


def test_scripted_reset_failure_is_loud():
    transport = FakeTransport(resettable=True, fail_reset=True)
    transport.start()
    assert transport.can_reset  # declared -> discovered broken only when used
    with pytest.raises(AnatomyError, match="reset mechanism failed"):
        transport.reset_world()


def test_close_is_idempotent_and_journaled_once():
    transport = FakeTransport()
    transport.start()
    transport.close()
    transport.close()
    assert transport.journal.count(("close",)) == 1
