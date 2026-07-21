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
    # the builder's body (feature 030 amendment) is the C1 default
    assert C1_OBS_DIM == 19
    assert C1_N_ACTIONS == 10
    # the feature-027 body remains one flag away (the recorded reversal path)
    legacy_sensors, legacy_actuators = c1_anatomy(crafting=False)
    assert sum(s.width for s in legacy_sensors) == 14
    assert sum(len(a.presets) for a in legacy_actuators) == 8


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
        assert obs.shape == (19,)
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


def test_place_ahead_is_materially_honest():
    # feature 030: place consumes from the pocket and no-ops when it is empty
    with FakeBridge() as bridge:
        body = _body(bridge)
        body.reset()
        noop = body.step(6)  # place with an empty pocket: nothing happens
        assert noop[11] == 0.0 and noop[18] == 0.0
        # walk to the wall, dig one block into the pocket, put it back
        body.step(3)
        body.step(3)  # face +x
        body.step(0)
        body.step(0)  # x=2; the wall at (3, 0) is ahead
        dug = body.step(5)  # dig_ahead: the pocket fills
        assert dug[14] == pytest.approx(1 / 64)  # one placeable block
        assert dug[18] == 1.0  # place now has material
        placed = body.step(6)  # place_ahead: the wall is back, pocket empty
        assert placed[11] == 1.0
        assert placed[14] == 0.0 and placed[18] == 0.0
        stuck = body.step(0)  # forward is blocked again
        assert stuck[0] == placed[0]
        body.close()


def test_the_full_material_chain_is_visible_step_by_step():
    # feature 030 SC-001: dig wood -> craft planks -> craft sticks -> place,
    # every intermediate visible in the channels on the next tick
    with FakeBridge() as bridge:
        body = _body(bridge)
        body.reset()
        body.step(0)
        body.step(0)  # (0, 2), facing +z
        body.step(2)  # turn_left: 45 deg
        body.step(0)  # the (-1, 3) diagonal
        faced = body.step(2)  # turn_left: 90 deg — the wood column (-2, 3) ahead
        assert faced[11] == 1.0  # feet-level solid ahead (the wood)
        assert list(faced[14:19]) == [0.0, 0.0, 0.0, 0.0, 0.0]  # empty pocket
        dug = body.step(5)  # dig the wood: one log
        assert dug[15] == pytest.approx(1 / 64)
        assert dug[18] == 0.0  # a log is not placeable
        planked = body.step(8)  # craft_planks: 1 log -> 4 planks
        assert planked[15] == 0.0
        assert planked[16] == pytest.approx(4 / 64)
        assert planked[18] == 1.0  # planks are placeable
        sticked = body.step(9)  # craft_sticks: 2 planks -> 4 sticks
        assert sticked[16] == pytest.approx(2 / 64)
        assert sticked[17] == pytest.approx(4 / 64)
        placed = body.step(6)  # place a plank where the wood stood
        assert placed[11] == 1.0
        assert placed[16] == pytest.approx(1 / 64)
        empty_craft = body.step(8)  # craft with no logs: byte-honest no-op
        assert list(empty_craft[14:18]) == list(placed[14:18])
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


def test_state_round_trip_carries_the_pocket_mid_chain():
    # feature 030 US3: a snapshot taken mid-material-chain restores exactly
    with FakeBridge() as bridge:
        body = _body(bridge)
        body.reset()
        body.step(0)
        body.step(0)
        body.step(2)
        body.step(0)
        body.step(2)  # the wood column ahead
        body.step(5)  # a log in the pocket
        body.step(8)  # crafted: 4 planks
        saved = body.state_dict()
        obs_at_save = body.step(7)
        body.close()
    with FakeBridge() as fresh:
        body = _body(fresh)
        body.reset()
        body.load_state_dict(saved)
        restored = body.step(7)
        assert restored.tolist() == obs_at_save.tolist()
        assert restored[16] == pytest.approx(4 / 64)  # the planks came along
        body.close()
