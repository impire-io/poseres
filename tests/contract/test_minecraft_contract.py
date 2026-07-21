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
    # the builder's body (features 030/031) is the C1 default
    assert C1_OBS_DIM == 28
    assert C1_N_ACTIONS == 12
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
        assert obs.shape == (28,)
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


def test_hold_next_cycles_every_class_regardless_of_counts():
    # feature 031: holding an empty class is a valid, sensed state
    with FakeBridge() as bridge:
        body = _body(bridge)
        body.reset()
        expected = [
            [1.0, 0.0, 0.0, 0.0],  # blocks (pocket empty - still holdable)
            [0.0, 1.0, 0.0, 0.0],  # logs
            [0.0, 0.0, 1.0, 0.0],  # planks
            [0.0, 0.0, 0.0, 1.0],  # sticks
            [0.0, 0.0, 0.0, 0.0],  # back to nothing
        ]
        for hand in expected:
            obs = body.step(8)  # hold_next
            assert list(obs[19:23]) == hand
        body.close()


def test_place_ahead_is_held_based_and_materially_honest():
    # feature 031: place acts on the held class only - selection is the
    # brain's; an empty hand or an unplaceable class no-ops
    with FakeBridge() as bridge:
        body = _body(bridge)
        body.reset()
        noop = body.step(6)  # nothing held: nothing happens
        assert noop[11] == 0.0 and noop[18] == 0.0
        # walk to the wall, dig one block, hold it, put it back
        body.step(3)
        body.step(3)  # face +x
        body.step(0)
        body.step(0)  # x=2; the wall at (3, 0) is ahead
        dug = body.step(5)  # dig_ahead: the pocket fills, the hand is empty
        assert dug[14] == pytest.approx(1 / 64)
        assert dug[18] == 0.0  # nothing held yet - place would no-op
        unheld = body.step(6)  # place with pocket full but hand empty: no-op
        assert unheld[11] == 0.0 and unheld[14] == pytest.approx(1 / 64)
        held = body.step(8)  # hold_next -> blocks
        assert held[18] == 1.0  # the held class is placeable
        placed = body.step(6)  # place_ahead: the wall is back, pocket empty
        assert placed[11] == 1.0
        assert placed[14] == 0.0
        assert placed[18] == 1.0  # still *holding* blocks (a class, not a count)
        body.close()


def test_the_honest_ladder_every_rung_sensed():
    # feature 031 FR-008/SC-001: dig wood -> hold -> stage -> observe the
    # offer -> take -> re-stage -> sticks -> place; and the vanilla
    # exact-match rule (a wrong staging kills the offer)
    with FakeBridge() as bridge:
        body = _body(bridge)
        body.reset()
        body.step(2)
        faced = body.step(2)  # two turn_lefts: the starter wood (-1, 0) ahead
        assert faced[11] == 1.0
        dug = body.step(5)  # dig the wood: one log in the pocket
        assert dug[15] == pytest.approx(1 / 64)
        body.step(8)  # hold_next -> blocks
        held_logs = body.step(8)  # hold_next -> logs
        assert list(held_logs[19:23]) == [0.0, 1.0, 0.0, 0.0]
        staged = body.step(9)  # grid_put: one log staged
        assert staged[15] == 0.0  # left the pocket
        assert staged[23] == pytest.approx(1 / 4)  # staged count
        assert staged[24] == pytest.approx(1 / 4)  # staged logs
        assert staged[26] == 1.0  # the offer: planks - before any craft
        taken = body.step(11)  # take_result: the real rung
        assert taken[16] == pytest.approx(4 / 64)  # 4 planks in the pocket
        assert taken[23] == 0.0 and taken[26] == 0.0  # grid and offer cleared
        body.step(8)  # hold_next -> planks
        one = body.step(9)  # one plank staged: a lone plank offers nothing
        assert one[26] == 0.0 and one[27] == 0.0
        two = body.step(9)  # two planks, column-adjacent: sticks offered
        assert two[27] == 1.0
        three = body.step(9)  # a third plank: exact-match rule kills the offer
        assert three[27] == 0.0
        returned = body.step(10)  # grid_take: everything back to the pocket
        assert returned[16] == pytest.approx(4 / 64)
        assert returned[23] == 0.0
        body.step(9)
        body.step(9)  # stage the pair again
        sticks = body.step(11)  # take_result: 4 sticks for 2 planks
        assert sticks[17] == pytest.approx(4 / 64)
        assert sticks[16] == pytest.approx(2 / 64)
        placed = body.step(6)  # still holding planks: place one where wood stood
        assert placed[11] == 1.0
        assert placed[16] == pytest.approx(1 / 64)
        idle = body.step(11)  # take_result on an empty grid: honest no-op
        assert list(idle[14:28]) == list(placed[14:28])
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


def test_state_round_trip_carries_the_pocket_mid_staging():
    # feature 031 US3: a snapshot taken mid-staging (held class + grid
    # contents + a live offer) restores byte-exactly
    with FakeBridge() as bridge:
        body = _body(bridge)
        body.reset()
        body.step(2)
        body.step(2)  # the starter wood ahead
        body.step(5)  # a log in the pocket
        body.step(8)
        body.step(8)  # hold logs
        body.step(9)  # staged: the planks offer is live
        saved = body.state_dict()
        obs_at_save = body.step(7)
        body.close()
    with FakeBridge() as fresh:
        body = _body(fresh)
        body.reset()
        body.load_state_dict(saved)
        restored = body.step(7)
        assert restored.tolist() == obs_at_save.tolist()
        assert restored[26] == 1.0  # the offer survived the snapshot
        taken = body.step(11)  # and it is still takeable after resume
        assert taken[16] == pytest.approx(4 / 64)
        body.close()
