"""T004/T007/T008/T009 — the adapter's binding contract
(contracts/ros2-adapter.md C2–C4, C6): Body/EventSource conformance, the tick
ordering, the staleness policy, the startup gate, episode-mode pairings, and
every rejection path — the missing-rclpy path via monkeypatching, never a
skip. All of it over the fake transport's journal (FR-008)."""

from __future__ import annotations

from types import SimpleNamespace as NS

import numpy as np
import pytest

import pra.anatomy.ros2.transport as transport_mod
from pra.anatomy.body import AnatomyError, Body
from pra.anatomy.ros2 import (
    ActuatorSpec,
    FakeTransport,
    RclpyTransport,
    Ros2Body,
    SensorSpec,
    TopicSensor,
    Transport,
)
from pra.config import Config
from pra.world.event_source import EventSource

LIDAR = SensorSpec(id="lidar", topic="/scan", width=2, extract="ranges")
HEADING = SensorSpec(id="heading", topic="/heading", width=1, extract="data")
DRIVE = ActuatorSpec(
    id="drive",
    topic="/cmd_vel",
    presets=({"linear.x": 0.2}, {"angular.z": 0.6}, {"angular.z": -0.6}, {}),
)


def _scan(value: float):
    return NS(ranges=np.array([value, value + 0.5]))


def _script(n: int = 200, every: int = 1) -> dict:
    return {
        "/scan": {k: [_scan(float(k))] for k in range(n)},
        "/heading": {k: [NS(data=0.1 * k)] for k in range(0, n, every)},
    }


def _body(script=None, **kw) -> tuple[Ros2Body, FakeTransport]:
    transport = FakeTransport(script=script if script is not None else _script())
    return Ros2Body([LIDAR, HEADING], [DRIVE], transport, **kw), transport


# ---- conformance (C2.1/C2.2) ---------------------------------------------------------


def test_body_is_a_doc02_body_and_an_event_source():
    body, transport = _body()
    assert isinstance(body, Body) and isinstance(body, EventSource)
    assert isinstance(transport, Transport)
    assert (body.obs_dim, body.n_actions) == (3, 4)
    obs = body.reset()
    assert obs.dtype == np.float64 and obs.shape == (3,)
    nxt = body.step(1)
    assert isinstance(nxt, np.ndarray) and nxt.shape == (3,)


def test_action_i_publishes_exactly_preset_i_once():
    body, transport = _body()
    body.reset()
    body.step(2)
    publishes = [e for e in transport.journal if e[0] == "publish"]
    assert publishes == [("publish", "/cmd_vel", {"angular.z": -0.6})]


def test_telemetry_lives_outside_the_learning_surface():
    body, _ = _body()
    body.reset()
    body.step(0)
    telemetry = body.telemetry()
    assert set(telemetry) == {"ticks", "overruns", "sensors", "actuators"}
    assert telemetry["actuators"]["drive"]["published"] == 1
    assert telemetry["sensors"]["lidar"]["deliveries"] >= 1
    for name in ("ticks", "telemetry", "overruns"):
        assert not hasattr(EventSource, name)  # the engine's seam never sees them


# ---- the tick discipline (C2.3, the named decision) --------------------------------------


def test_journal_shows_publish_before_tick_and_the_sample_reflects_it():
    body, transport = _body()
    body.reset()
    gate_ticks = body.ticks
    obs = body.step(0)
    events = [e for e in transport.journal if e[0] in ("publish", "tick")]
    assert events[-2][0] == "publish" and events[-1] == ("tick", gate_ticks)
    # the sample happens after the tick: the observation carries this tick's
    # scripted lidar payload, not the previous one
    assert obs[0] == float(gate_ticks)


def test_exactly_one_tick_per_step_regardless_of_which_actuator_routes():
    class InertActuator:  # a registered non-ROS tool: applies, publishes nothing
        def id(self):
            return "inert"

        def action_count(self):
            return 1

        def apply(self, local_action_index):
            pass

    body, transport = _body()
    body.reset()
    body.register_actuator(InertActuator())
    body.apply_pending_tools()
    before = body.ticks
    body.step(4)  # the inert actuator's global index (after drive's 4)
    assert body.ticks == before + 1
    assert [e for e in transport.journal if e[0] == "tick"][-1] == ("tick", before)
    assert [e for e in transport.journal if e[0] == "publish"] == []  # nothing published


# ---- the staleness policy (C2.4) -----------------------------------------------------


def test_silent_tick_holds_the_last_value_and_counts():
    body, _ = _body(script=_script(every=3))  # heading publishes at ticks 0, 3, 6, ...
    body.reset()  # gate consumes tick 0 (both topics speak there)
    values = [body.step(0)[2] for _ in range(6)]  # samples after ticks 1..6
    telemetry = body.telemetry()["sensors"]["heading"]
    assert telemetry["staleness_total"] == 4  # 2 of every 3 samples were held
    assert telemetry["staleness_streak"] <= 2
    # held values repeat exactly — never zero-filled, never invented
    assert values == pytest.approx([0.0, 0.0, 0.3, 0.3, 0.3, 0.6])


def test_latest_wins_within_a_tick_and_overwrites_are_counted():
    script = {"/scan": {0: [_scan(1.0), _scan(2.0)], 1: [_scan(3.0)]}}
    transport = FakeTransport(script=script)
    body = Ros2Body([LIDAR], [DRIVE], transport)
    obs = body.reset()
    assert obs[0] == 2.0  # the second payload of tick 0 won
    assert body.telemetry()["sensors"]["lidar"]["overwritten"] == 1


def test_a_streak_over_the_bound_is_loud_naming_the_topic():
    script = {"/scan": {0: [_scan(1.0)]}}  # one message, then silence
    body = Ros2Body([LIDAR], [DRIVE], FakeTransport(script=script), stale_limit_ticks=3)
    body.reset()
    for _ in range(3):
        body.step(0)  # streak 1, 2, 3 — at the bound, still allowed
    with pytest.raises(AnatomyError, match=r"'/scan'.*4 consecutive.*stale_limit_ticks=3"):
        body.step(0)


def test_read_before_first_message_is_a_contract_error():
    sensor = TopicSensor(LIDAR)
    with pytest.raises(AnatomyError, match="before its first message"):
        sensor.read()


def test_delivery_width_violation_is_loud_naming_topic_and_shapes():
    body, _ = _body(
        script={"/scan": {0: [NS(ranges=np.zeros(7))]}, "/heading": {0: [NS(data=0.0)]}}
    )
    with pytest.raises(AnatomyError, match=r"'/scan' declared width 2 .* 7 value"):
        body.reset()


# ---- the startup gate (C2.5) -----------------------------------------------------------


def test_gate_ticks_until_the_first_messages_arrive():
    script = {"/scan": {5: [_scan(9.0)]}, "/heading": {2: [NS(data=1.0)]}}
    body, transport = _body(script=script)
    obs = body.reset()
    assert body.ticks == 6  # ticks 0..5 ran; the last one delivered the lidar
    assert obs[0] == 9.0 and obs[2] == 1.0
    assert [e for e in transport.journal if e[0] == "publish"] == []  # gate never publishes


def test_gate_expiry_names_every_silent_topic():
    body, _ = _body(script={"/scan": {0: [_scan(1.0)]}}, startup_timeout_ticks=4)
    with pytest.raises(AnatomyError, match=r"4 tick\(s\).*(/heading)"):
        body.reset()


# ---- mount rejections (C3) ---------------------------------------------------------------


def test_factory_config_mismatch_names_both_number_pairs():
    factory = Ros2Body.factory([LIDAR, HEADING], [DRIVE], transport=FakeTransport)
    with pytest.raises(AnatomyError) as err:
        factory(Config(obs_dim=10, n_actions=2), np.random.default_rng(1))
    message = str(err.value)
    assert "obs_dim=10" in message and "n_actions=2" in message  # the config side
    assert "obs_dim=3" in message and "n_actions=4" in message  # the anatomy side


def test_factory_rejects_episodic_over_a_resetless_transport():
    factory = Ros2Body.factory([LIDAR, HEADING], [DRIVE], transport=FakeTransport)
    cfg = Config(obs_dim=3, n_actions=4, episode_mode="episodic")
    with pytest.raises(AnatomyError, match="reset mechanism.*continuous"):
        factory(cfg, np.random.default_rng(1))


def test_factory_never_touches_the_engine_generator():
    rng = np.random.default_rng(1)
    state_before = rng.bit_generator.state
    Ros2Body.factory([LIDAR, HEADING], [DRIVE], transport=FakeTransport)(
        Config(obs_dim=3, n_actions=4, episode_mode="continuous"), rng
    )
    assert rng.bit_generator.state == state_before  # research R4: zero draws, zero reads-that-write


def test_mid_run_reset_without_a_mechanism_is_loud():
    body, _ = _body()
    body.reset()
    with pytest.raises(AnatomyError, match="cannot reset mid-run.*continuous"):
        body.reset()


# ---- episodic mode over a resettable transport (C4.2) -------------------------------------


def test_episodic_reset_uses_the_mechanism_and_regates():
    transport = FakeTransport(script={"/scan": {0: [_scan(4.0)]}}, resettable=True)
    body = Ros2Body([LIDAR], [DRIVE], transport)
    first = body.reset()
    body.step(0)
    second = body.reset()  # episode 2: reset_world + fresh gate on the rewound script
    assert ("reset",) in transport.journal
    assert first[0] == second[0] == 4.0


def test_a_failing_reset_mechanism_fails_the_run_loudly():
    transport = FakeTransport(script={"/scan": {0: [_scan(1.0)]}}, resettable=True, fail_reset=True)
    body = Ros2Body([LIDAR], [DRIVE], transport)
    body.reset()
    with pytest.raises(AnatomyError, match="reset mechanism failed"):
        body.reset()


# ---- growing the anatomy (Doc 02 §5 through the adapter) -----------------------------------


def test_registering_a_topic_sensor_subscribes_now_applies_at_the_boundary():
    body, transport = _body()
    body.reset()
    body.register_topic_sensor(SensorSpec(id="bumper", topic="/bumper", width=1, extract="data"))
    assert ("subscribe", "/bumper") in transport.journal  # warming immediately
    assert body.obs_dim == 3  # not yet applied
    assert body.apply_pending_tools() == (4, 4)  # the slow-loop boundary


# ---- the real transport's honest failure (C6) ----------------------------------------------


def test_missing_rclpy_explains_the_distro_and_points_at_the_example(monkeypatch):
    monkeypatch.setattr(transport_mod, "_rclpy", None)
    with pytest.raises(ImportError, match=r"ROS 2 distribution.*examples/ros2"):
        RclpyTransport()


def test_rclpy_transport_validates_its_arguments_before_any_ros_work(monkeypatch):
    monkeypatch.setattr(transport_mod, "_rclpy", object())  # present, never used in __init__
    with pytest.raises(AnatomyError, match="unknown mode"):
        RclpyTransport(mode="warp")
    with pytest.raises(AnatomyError, match="step_service"):
        RclpyTransport(mode="stepped")
    with pytest.raises(AnatomyError, match="come together"):
        RclpyTransport(reset_service="/reset")
    with pytest.raises(AnatomyError, match="tick_period"):
        RclpyTransport(tick_period=0.0)
