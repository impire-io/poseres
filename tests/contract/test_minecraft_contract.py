"""Feature 027 T5 — the adapter contract over the in-repo FakeBridge.

Every assertion here runs the REAL transport code (framing, handshake,
tick round-trip, delivery, the state seam) against a real localhost
socket — no Minecraft, Node, or Docker anywhere (FR-005)."""

from __future__ import annotations

import pytest

from pra.anatomy.body import AnatomyError
from pra.anatomy.minecraft import (
    C1_N_ACTIONS,
    C1_OBS_DIM,
    FakeBridge,
    MinecraftTransport,
    c1_anatomy,
)
from pra.anatomy.ros2 import Ros2Body
from pra.anatomy.ros2.specs import ActuatorSpec, SensorSpec

SENSORS, ACTUATORS = c1_anatomy()


def _transport(bridge: FakeBridge, **kw) -> MinecraftTransport:
    kw.setdefault("tick_ms", 1)
    kw.setdefault("tick_budget", 60.0)
    kw.setdefault("connect_timeout", 5.0)
    return MinecraftTransport(port=bridge.port, **kw)


def _body(bridge: FakeBridge, **kw) -> Ros2Body:
    return Ros2Body(SENSORS, ACTUATORS, _transport(bridge, **kw))


# ---- anatomy arithmetic ------------------------------------------------------------


def test_declared_anatomy_matches_the_contract_table():
    assert C1_OBS_DIM == 14
    assert C1_N_ACTIONS == 8


# ---- handshake honesty (FR-002) ----------------------------------------------------


def test_unknown_channel_is_loud_at_start():
    with FakeBridge() as bridge:
        body = Ros2Body(
            SENSORS + [SensorSpec(id="ghost", topic="nope", width=1)],
            ACTUATORS,
            _transport(bridge),
        )
        with pytest.raises(AnatomyError, match="no channel 'nope'"):
            body.reset()


def test_width_mismatch_is_loud_at_start():
    with FakeBridge() as bridge:
        body = Ros2Body(
            [SensorSpec(id="pose", topic="pose", width=4)],
            ACTUATORS,
            _transport(bridge),
        )
        with pytest.raises(AnatomyError, match="width 5, the spec declares 4"):
            body.reset()


def test_second_concurrent_client_is_refused():
    with FakeBridge() as bridge:
        first = _body(bridge)
        first.reset()
        with pytest.raises(AnatomyError, match="one client at a time"):
            _body(bridge).reset()
        first.close()


# ---- transport lifecycle ------------------------------------------------------------


def test_single_boot_lazy_boot_and_reset_refusal():
    with FakeBridge() as bridge:
        transport = _transport(bridge)
        # first use lazy-boots (the resumed-continuous path, feature 008):
        transport.publish(ACTUATORS[0], 0)
        assert bridge.requests.count("hello") == 1
        transport.tick()
        # an explicit second start is still loud (the single-boot contract):
        with pytest.raises(AnatomyError, match="exactly once"):
            transport.start()
        assert transport.can_reset is False
        with pytest.raises(AnatomyError, match="continuous"):
            transport.reset_world()
        transport.close()
        transport.close()  # idempotent
        assert bridge.requests.count("bye") == 1


def test_no_bridge_is_a_named_connection_error():
    transport = MinecraftTransport(port=9, connect_timeout=0.3)  # port 9: discard, closed
    with pytest.raises(AnatomyError, match="no bridge at"):
        transport.start()


# ---- the step semantics (FR-003) ----------------------------------------------------


def test_one_tick_op_per_engine_step_after_the_startup_gate():
    with FakeBridge() as bridge:
        body = _body(bridge)
        body.reset()
        ticks_after_reset = bridge.requests.count("tick")
        assert ticks_after_reset >= 1  # the startup gate ticks until first delivery
        for action in range(C1_N_ACTIONS):
            body.step(action)
        assert bridge.requests.count("tick") == ticks_after_reset + C1_N_ACTIONS
        assert bridge.requests[0] == "hello"
        body.close()


def test_unknown_command_is_a_loud_bridge_error():
    with FakeBridge() as bridge:
        bad = ActuatorSpec(id="wings", topic="control", presets=({"fly": 1.0},))
        body = Ros2Body(SENSORS, [bad], _transport(bridge))
        body.reset()
        with pytest.raises(AnatomyError, match="unknown command 'fly'"):
            body.step(0)
        body.close()


def test_every_channel_delivers_every_tick_so_nothing_goes_stale():
    with FakeBridge() as bridge:
        body = _body(bridge)
        body.reset()
        for _ in range(20):
            body.step(7)  # idle
        telemetry = body.telemetry()
        assert all(s["staleness_total"] == 0 for s in telemetry["sensors"].values())
        assert telemetry["sensors"]["pose"]["deliveries"] >= 21
        body.close()


# ---- the fake world honors the channel contract --------------------------------------


def test_walls_block_turns_turn_and_dig_opens_the_way():
    with FakeBridge() as bridge:
        body = _body(bridge)
        obs = body.reset()
        assert obs.shape == (14,)
        # face +x (the wall at x=3): turn_right once from +z takes yaw to -45deg
        # -> ahead is the (1, 1) diagonal; instead steer by turning to face the
        # wall column directly: two turn_rights = -90deg -> ahead (1, 0).
        body.step(3)
        obs = body.step(3)
        pose = obs[:5]
        assert pose[3] == pytest.approx(-1.0)  # sin(-90deg)
        blocks_before = obs[11:14]
        assert blocks_before[0] == 0.0  # nothing at (1, 0)
        body.step(0)  # forward to x=1
        obs = body.step(0)  # forward to x=2; ahead is now the wall at (3, 0)
        assert obs[11] == 1.0  # feet-level solid ahead
        blocked = body.step(0)  # walking into the wall does not move
        assert blocked[0] == obs[0]
        body.step(5)  # dig_ahead
        opened = body.step(0)  # now the way is open
        assert opened[0] > obs[0]
        body.close()


def test_place_ahead_creates_a_wall_where_none_was():
    with FakeBridge() as bridge:
        body = _body(bridge)
        body.reset()
        assert body.step(7)[11] == 0.0  # ahead of spawn (facing +z) is open
        obs = body.step(6)  # place_ahead
        assert obs[11] == 1.0
        stuck = body.step(0)  # forward is now blocked
        assert stuck[1] == obs[1]
        body.close()


# ---- the state seam (FR-007, fake mode = class 1) ------------------------------------


def test_state_round_trip_restores_the_edited_world_exactly():
    with FakeBridge() as bridge:
        body = _body(bridge)
        body.reset()
        body.step(3)
        body.step(3)
        body.step(5)  # dig the wall column
        saved = body.state_dict()
        obs_at_save = body.step(7)
        body.close()
    with FakeBridge() as fresh:
        body = _body(fresh)
        body.reset()
        body.load_state_dict(saved)
        assert body.step(7).tolist() == obs_at_save.tolist()
        body.close()
