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
from pra.anatomy.minecraft.fake import item_signature
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
    # the property body (feature 033) is the C1 default
    assert C1_OBS_DIM == 32
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
        assert obs.shape == (32,)
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
        body.step(5)
        mid = body.step(5)  # digging is a held intention now
        assert mid[14] == pytest.approx(2 / 3)  # sensed progress (mining)
        body.step(5)  # third dig: the mineral breaks
        opened = body.step(0)  # now the way is open
        assert opened[0] > obs[0]
        body.close()


def test_hold_next_cycles_the_pockets_kinds():
    # feature 033: the cycle is nothing -> distinct pocket kinds (sorted by
    # name) -> nothing; an empty pocket means there is nothing to hold
    with FakeBridge() as bridge:
        body = _body(bridge)
        body.reset()
        empty = body.step(8)  # hold_next with an empty pocket: still nothing
        assert list(empty[19:25]) == [0.0] * 6
        # dig the starter wood (12 ticks) then the wall (3 of mineral)
        body.step(2)
        body.step(2)  # face the starter wood at (-1, 0)
        for _ in range(12):
            body.step(5)  # oak_log in the pocket
        for _ in range(4):
            body.step(3)  # 180 deg: face +x
        body.step(0)
        body.step(0)  # x=2; the wall at (3, 0) ahead
        for _ in range(3):
            body.step(5)  # cobblestone in the pocket
        held1 = body.step(8)  # -> cobblestone (first sorted kind)
        assert held1[19] == 1.0 and held1[20] == 1.0  # present, placeable
        assert list(held1[22:25]) == list(item_signature("cobblestone"))
        held2 = body.step(8)  # -> oak_log
        assert list(held2[22:25]) == list(item_signature("oak_log"))
        assert held2[20] == 1.0  # logs ARE placeable (the game's own fact)
        cleared = body.step(8)  # -> nothing again
        assert list(cleared[19:25]) == [0.0] * 6
        body.close()


def test_place_ahead_is_held_based_and_materially_honest():
    # feature 033: place acts on the held kind - selection is the brain's;
    # an empty hand no-ops, and what you place is what you dug
    with FakeBridge() as bridge:
        body = _body(bridge)
        body.reset()
        noop = body.step(6)  # nothing held: nothing happens
        assert noop[11] == 0.0 and noop[15] == 0.0
        body.step(3)
        body.step(3)  # face +x
        body.step(0)
        body.step(0)  # x=2; the wall at (3, 0) is ahead
        for _ in range(3):
            body.step(5)  # dig through the mineral: one cobblestone pocketed
        dug = body.step(7)
        assert dug[15] == pytest.approx(1 / 64)  # pocket total
        assert dug[17] == pytest.approx(1 / 64)  # and it is placeable
        unheld = body.step(6)  # pocket full but hand empty: no-op
        assert unheld[11] == 0.0 and unheld[15] == pytest.approx(1 / 64)
        held = body.step(8)  # hold_next -> cobblestone
        assert held[19] == 1.0 and held[20] == 1.0
        placed = body.step(6)  # place_ahead: the wall is back, pocket empty
        assert placed[11] == 1.0
        assert placed[15] == 0.0
        assert list(placed[19:25]) == [0.0] * 6  # the held kind ran out - sensed
        body.close()


def test_the_honest_ladder_every_rung_sensed():
    # feature 033 US1+US2: persistence -> pocket -> hold -> stage -> observe
    # the offer (properties + signature only) -> take -> place; and the
    # vanilla exact-match rule
    with FakeBridge() as bridge:
        body = _body(bridge)
        body.reset()
        body.step(2)
        faced = body.step(2)  # the starter wood (-1, 0) ahead
        assert faced[11] == 1.0
        for i in range(11):
            mid = body.step(5)
            assert mid[14] == pytest.approx((i + 1) / 12)  # the cracks, sensed
        assert mid[15] == 0.0  # nothing pocketed yet
        broke = body.step(5)  # the twelfth dig breaks the wood
        assert broke[14] == 0.0  # progress cleared
        assert broke[15] == pytest.approx(1 / 64)  # pocket total
        assert broke[17] == pytest.approx(1 / 64)  # a log is placeable (game fact)
        held = body.step(8)  # hold_next -> oak_log (the only kind)
        assert held[19] == 1.0 and held[20] == 1.0
        assert list(held[22:25]) == list(item_signature("oak_log"))
        staged = body.step(9)  # grid_put: the offer appears, pre-craft
        assert staged[25] == pytest.approx(1 / 4)
        assert staged[26] == 1.0  # something is offered
        assert staged[27] == 1.0  # and it is placeable (planks)
        assert staged[28] == pytest.approx(4 / 64)  # four per craft
        assert list(staged[29:32]) == list(item_signature("oak_planks"))
        assert staged[15] == 0.0  # the log left the pocket
        taken = body.step(11)  # take_result: 4 planks
        assert taken[15] == pytest.approx(4 / 64)
        assert taken[25] == 0.0 and taken[26] == 0.0
        assert list(taken[19:25]) == [0.0] * 6  # held kind ran out - sensed
        planks = body.step(8)  # hold_next: a ran-out kind acts as nothing -> oak_planks
        assert list(planks[22:25]) == list(item_signature("oak_planks"))
        one = body.step(9)  # a lone plank offers nothing
        assert one[26] == 0.0
        two = body.step(9)  # a same-species pair offers sticks
        assert two[26] == 1.0
        assert two[27] == 0.0  # sticks are NOT placeable - the property split
        assert list(two[29:32]) == list(item_signature("stick"))
        three = body.step(9)  # a third plank: exact-match kills the offer
        assert three[26] == 0.0
        returned = body.step(10)  # grid_take: everything back
        assert returned[15] == pytest.approx(4 / 64)
        body.step(9)
        body.step(9)  # stage the pair again
        sticks = body.step(11)  # 4 sticks for 2 planks
        assert sticks[15] == pytest.approx(6 / 64)  # 2 planks + 4 sticks
        assert sticks[17] == pytest.approx(2 / 64)  # placeable: the planks
        assert sticks[18] == pytest.approx(4 / 64)  # other: the sticks
        placed = body.step(6)  # still holding planks: place one
        assert placed[11] == 1.0
        assert placed[15] == pytest.approx(5 / 64)
        idle = body.step(11)  # take_result on an empty grid: honest no-op
        assert list(idle[15:32]) == list(placed[15:32])
        body.close()


def test_signatures_distinguish_and_are_stable():
    a, b, c = item_signature("oak_log"), item_signature("oak_planks"), item_signature("stick")
    assert a != b != c and a != c
    assert a == item_signature("oak_log")  # stable across calls
    assert all(-1.0 <= v <= 1.0 for v in a + b + c)


def test_interruption_resets_the_dig():
    with FakeBridge() as bridge:
        body = _body(bridge)
        body.reset()
        body.step(2)
        body.step(2)  # the starter wood ahead
        body.step(5)
        mid = body.step(5)
        assert mid[14] == pytest.approx(2 / 12)
        released = body.step(7)  # idle releases the intention
        assert released[14] == 0.0
        restart = body.step(5)  # starting over starts from zero
        assert restart[14] == pytest.approx(1 / 12)
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


def test_state_round_trip_carries_pocket_staging_and_mid_dig():
    # feature 033: a snapshot mid-dig AND mid-staging restores byte-exactly,
    # including the accumulated cracks
    with FakeBridge() as bridge:
        body = _body(bridge)
        body.reset()
        body.step(2)
        body.step(2)  # the starter wood ahead
        for _ in range(12):
            body.step(5)  # oak_log pocketed
        body.step(8)  # hold the log
        body.step(9)  # staged: the planks offer is live
        body.step(3)
        body.step(3)
        body.step(3)
        body.step(3)  # 180: face +x toward the wall
        body.step(0)
        body.step(0)
        body.step(5)
        mid = body.step(5)  # two ticks into the wall
        assert mid[14] == pytest.approx(2 / 3)
        saved = body.state_dict()
        obs_at_save = body.step(7)  # idle: releases the dig post-save
        body.close()
    with FakeBridge() as fresh:
        body = _body(fresh)
        body.reset()
        body.load_state_dict(saved)
        restored = body.step(7)
        assert restored.tolist() == obs_at_save.tolist()
        assert restored[26] == 1.0  # the offer survived the snapshot
        taken = body.step(11)  # and it is still takeable after resume
        assert taken[15] == pytest.approx(4 / 64)
        body.close()
