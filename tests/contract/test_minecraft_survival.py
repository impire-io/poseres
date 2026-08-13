"""Native-survival instrument (research topic native-survival, 2026-08-11) —
the mouth and the metabolism over the in-repo FakeBridge.

Survival mode is opt-in on every surface and ships only on promotion;
these assertions run the REAL transport code against a real localhost
socket, exactly like the 027 contract suite. The shipped 32/12 body is
proven untouched by the mode staying off everywhere else."""

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
from pra.anatomy.ros2.specs import ActuatorSpec

SENSORS, ACTUATORS = c1_anatomy(survival=True)

# survival ids: 0-11 are the shipped set unchanged, 12 is the mouth
FORWARD, TURN_LEFT, TURN_RIGHT, DIG, IDLE, HOLD, USE = 0, 2, 3, 5, 7, 8, 12


def _transport(bridge: FakeBridge, **kw) -> MinecraftTransport:
    kw.setdefault("tick_ms", 1)
    kw.setdefault("tick_budget", 60.0)
    kw.setdefault("connect_timeout", 5.0)
    return MinecraftTransport(port=bridge.port, **kw)


def _body(bridge: FakeBridge, **kw) -> Ros2Body:
    return Ros2Body(SENSORS, ACTUATORS, _transport(bridge, **kw))


def _pocket_a_melon(body: Ros2Body) -> None:
    """From spawn: face the melon column at (0, -2), break it, hold a slice."""
    for _ in range(4):
        body.step(TURN_LEFT)  # 180 deg: ahead is (0, -1)
    body.step(FORWARD)  # to (0, -1); the melon column is ahead
    for _ in range(6):
        body.step(DIG)  # the melon breaks: three slices pocketed
    body.step(HOLD)  # hold_next -> melon_slice (the only kind)


def _idle_to_drain_edge(body: Ros2Body) -> None:
    """Idle until food first reads 18/20 — the tick IS a drain edge, so the
    next interval leaves ~39 ticks of slack for exact eat arithmetic."""
    for _ in range(120):
        if body.step(IDLE)[6] == pytest.approx(0.90):
            return
    raise AssertionError("the food bar never reached 18/20 — the drain is broken")


# ---- anatomy arithmetic ------------------------------------------------------------


def test_survival_anatomy_matches_the_amendment():
    assert sum(s.width for s in SENSORS) == 33
    assert sum(len(a.presets) for a in ACTUATORS) == 13
    # the shipped default is byte-identical with the mode off
    assert C1_OBS_DIM == 32
    assert C1_N_ACTIONS == 12
    # the mouth is appended: ids 0..11 keep their shipped meaning
    assert ACTUATORS[0].presets[:12] == c1_anatomy()[1][0].presets
    assert ACTUATORS[0].presets[12] == {"use_held": 1.0}
    hand = next(s for s in SENSORS if s.id == "hand")
    assert hand.labels == ("present", "placeable", "edible", "count", "sig0", "sig1", "sig2")


def test_survival_needs_the_property_body():
    with pytest.raises(ValueError, match="property body"):
        c1_anatomy(crafting=False, survival=True)


# ---- mode mismatches are loud ------------------------------------------------------


def test_shipped_body_on_a_survival_bridge_is_loud_at_start():
    with FakeBridge(survival=True) as bridge:
        body = Ros2Body(*c1_anatomy(), _transport(bridge))
        with pytest.raises(AnatomyError, match="width 7, the spec declares 6"):
            body.reset()


def test_use_held_without_survival_is_a_loud_bridge_error():
    with FakeBridge() as bridge:
        mouth = ActuatorSpec(id="mouth", topic="control", presets=({"use_held": 1.0},))
        body = Ros2Body(c1_anatomy()[0], [mouth], _transport(bridge))
        body.reset()
        with pytest.raises(AnatomyError, match="unknown command 'use_held'"):
            body.step(0)
        body.close()


# ---- the edible affordance (the widened hand) ---------------------------------------


def test_hand_senses_edibility_beside_placeability():
    with FakeBridge(survival=True) as bridge:
        body = _body(bridge)
        obs = body.reset()
        assert obs.shape == (33,)
        _pocket_a_melon(body)
        held = body.step(IDLE)
        assert held[19] == 1.0  # present
        assert held[20] == 0.0  # a slice is NOT placeable
        assert held[21] == 1.0  # and IS edible — the new affordance
        assert held[22] == pytest.approx(3 / 64)
        assert list(held[23:26]) == list(item_signature("melon_slice"))
        assert held[17] == 0.0  # pocket: nothing placeable
        assert held[18] == pytest.approx(3 / 64)  # the slices count as other
        # the wood contrast: placeable, not edible
        body.step(TURN_RIGHT)
        body.step(TURN_RIGHT)  # face -x
        body.step(FORWARD)  # to (-1, -1)
        body.step(TURN_RIGHT)
        body.step(TURN_RIGHT)  # face +z: the starter wood at (-1, 0) ahead
        for _ in range(12):
            body.step(DIG)
        wood = body.step(HOLD)  # hold_next -> oak_log
        assert list(wood[23:26]) == list(item_signature("oak_log"))
        assert wood[20] == 1.0  # placeable (the game's own fact)
        assert wood[21] == 0.0  # and not edible
        body.close()


# ---- the mouth (use_held) and the world's own metabolism ----------------------------


def test_food_drains_and_eating_pays_from_the_pocket():
    with FakeBridge(survival=True) as bridge:
        body = _body(bridge)
        obs = body.reset()
        assert obs[5] == 1.0 and obs[6] == 1.0  # full health, full food
        _pocket_a_melon(body)
        for _ in range(8):
            full = body.step(USE)  # a full body cannot eat — world fact
        assert full[22] == pytest.approx(3 / 64)  # nothing consumed
        assert full[6] == 1.0
        _idle_to_drain_edge(body)  # the world's own clock drains the bar
        for _ in range(5):
            mid = body.step(USE)  # five held ticks: still chewing
        assert mid[22] == pytest.approx(3 / 64)
        assert mid[6] == pytest.approx(0.90)
        done = body.step(USE)  # the sixth completes the consume
        assert done[22] == pytest.approx(2 / 64)  # one slice left the pocket
        assert done[15] == pytest.approx(2 / 64)  # sensed in the aggregate too
        assert done[6] == pytest.approx(1.0)  # and the world paid 2/20
        body.close()


def test_the_chew_has_cracks_the_progress_channel_senses_the_use():
    # arms amendment 1: the progress channel senses the held intention,
    # whatever it is — the itch can hold the eat only if the chew is sensed
    with FakeBridge(survival=True) as bridge:
        body = _body(bridge)
        body.reset()
        _pocket_a_melon(body)
        _idle_to_drain_edge(body)
        for i in range(5):
            mid = body.step(USE)
            assert mid[14] == pytest.approx((i + 1) / 6)  # the chew, sensed
        done = body.step(USE)  # the sixth completes the consume
        assert done[14] == 0.0  # progress clears with the intention
        assert done[6] == pytest.approx(1.0)
        released = body.step(IDLE)
        assert released[14] == 0.0
        body.close()


def test_use_is_a_held_intention_released_by_any_other_command():
    with FakeBridge(survival=True) as bridge:
        body = _body(bridge)
        body.reset()
        _pocket_a_melon(body)
        _idle_to_drain_edge(body)
        for _ in range(5):
            body.step(USE)  # one tick short of the consume
        released = body.step(IDLE)  # idle releases the intention
        assert released[22] == pytest.approx(3 / 64)
        for _ in range(5):
            again = body.step(USE)  # starting over starts from zero
        assert again[22] == pytest.approx(3 / 64)  # five ticks: still nothing
        done = body.step(USE)
        assert done[22] == pytest.approx(2 / 64)  # the sixth of the NEW hold
        assert done[6] == pytest.approx(1.0)
        body.close()


def test_health_follows_once_the_food_runs_out():
    # the N1 shape, rehearsed in the fake: a body that works but never eats
    # empties its bar under the world's own clock, then health follows down
    # to the normal-difficulty floor (half a heart) and no further
    with FakeBridge(survival=True) as bridge:
        body = _body(bridge)
        body.reset()
        for _ in range(1700):
            obs = body.step(IDLE)
        assert obs[6] == 0.0  # the bar is empty
        assert obs[5] == pytest.approx(1 / 20)  # health followed to the floor
        for _ in range(80):
            obs = body.step(IDLE)
        assert obs[5] == pytest.approx(1 / 20)  # and starvation stops there
        body.close()


# ---- the state seam (survival mode stays class 1) -----------------------------------


def test_survival_state_seam_round_trips_mid_use():
    with FakeBridge(survival=True) as bridge:
        body = _body(bridge)
        body.reset()
        _pocket_a_melon(body)
        _idle_to_drain_edge(body)
        for _ in range(3):
            body.step(USE)  # mid-chew: the intention is world state
        saved = body.state_dict()
        assert saved["food"] == 18 and saved["using"] == 3
        obs_at_save = body.step(USE)
        body.close()
    with FakeBridge(survival=True) as fresh:
        body = _body(fresh)
        body.reset()
        body.load_state_dict(saved)
        restored = body.step(USE)
        assert restored.tolist() == obs_at_save.tolist()
        body.step(USE)
        done = body.step(USE)  # the held intention completes after resume
        assert done[22] == pytest.approx(2 / 64)
        assert done[6] == pytest.approx(1.0)
        body.close()


def test_snapshot_from_the_wrong_mode_is_loud():
    with FakeBridge() as bridge:
        body = Ros2Body(*c1_anatomy(), _transport(bridge))
        body.reset()
        saved = body.state_dict()
        body.close()
    with FakeBridge(survival=True) as fresh:
        body = _body(fresh)
        body.reset()
        with pytest.raises(AnatomyError, match="food"):
            body.load_state_dict(saved)
        body.close()
