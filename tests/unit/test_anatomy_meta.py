"""Feature 029 contract §3 — every body's self-description: groups cover the
observation vector contiguously in composition order, actuators name every
global action id, and the declaration tracks the *live* anatomy."""

from __future__ import annotations

import gymnasium
import numpy as np
import pytest

from pra.anatomy.gymnasium_body import GymnasiumWorld
from pra.anatomy.minecraft import c1_anatomy
from pra.anatomy.ros2 import Ros2Body
from pra.anatomy.ros2.fake import FakeTransport
from pra.anatomy.ros2.specs import ActuatorSpec, SensorSpec
from pra.config import Config
from pra.examples.rover.world import ACTION_NAMES, SENSOR_PARTS, make_rover_body

LIDAR = SensorSpec(id="lidar", topic="/scan", width=2, extract="ranges")
HEADING = SensorSpec(id="heading", topic="/heading", width=1, extract="data")
DRIVE = ActuatorSpec(
    id="drive", topic="/cmd", presets=({"fwd": 1.0}, {"rev": 1.0}, {"fwd": 1.0, "spin": 2.0}, {})
)


def _assert_invariants(meta: dict) -> None:
    start = 0
    for g in meta["groups"]:
        assert g["start"] == start, "groups must be contiguous in composition order"
        assert g["width"] >= 1
        start += g["width"]
    assert start == meta["obs_dim"], "groups must cover the observation vector"
    assert [a["action"] for a in meta["actuators"]] == list(range(meta["n_actions"]))


def test_ros2_body_meta_groups_and_preset_labels():
    body = Ros2Body([LIDAR, HEADING], [DRIVE], FakeTransport(script={}))
    meta = body.anatomy_meta()
    _assert_invariants(meta)
    assert [(g["id"], g["start"], g["width"]) for g in meta["groups"]] == [
        ("lidar", 0, 2),
        ("heading", 2, 1),
    ]
    assert [a["label"] for a in meta["actuators"]] == ["fwd", "rev", "fwd+spin", "idle"]
    assert all(a["id"] == "drive" for a in meta["actuators"])


def test_c1_minecraft_meta_matches_the_channel_contract():
    # the property body (feature 033) is the C1 default: 32 / 12, labeled
    sensors, actuators = c1_anatomy()
    body = Ros2Body(sensors, actuators, FakeTransport(script={}))
    meta = body.anatomy_meta()
    _assert_invariants(meta)
    assert (meta["obs_dim"], meta["n_actions"]) == (32, 12)
    assert [(g["id"], g["start"], g["width"]) for g in meta["groups"]] == [
        ("pose", 0, 5),
        ("vitals", 5, 2),
        ("env", 7, 4),
        ("blocks", 11, 3),
        ("mining", 14, 1),
        ("pocket", 15, 4),
        ("hand", 19, 6),
        ("grid", 25, 7),
    ]
    labels = {g["id"]: g.get("labels") for g in meta["groups"]}
    assert labels["pose"] == ["x", "z", "y", "sin_yaw", "cos_yaw"]
    assert labels["env"] == ["light", "sin_time", "cos_time", "rain"]
    assert labels["hand"] == ["present", "placeable", "count", "sig0", "sig1", "sig2"]
    assert labels["grid"][:4] == ["staged", "offer", "offer_placeable", "offer_count"]
    assert [a["label"] for a in meta["actuators"]] == [
        "forward",
        "back",
        "turn_left",
        "turn_right",
        "jump_forward",
        "dig_ahead",
        "place_ahead",
        "idle",
        "hold_next",
        "grid_put",
        "grid_take",
        "take_result",
    ]


def test_c1_legacy_flag_is_the_exact_feature_027_body():
    sensors, actuators = c1_anatomy(crafting=False)
    body = Ros2Body(sensors, actuators, FakeTransport(script={}))
    meta = body.anatomy_meta()
    _assert_invariants(meta)
    assert (meta["obs_dim"], meta["n_actions"]) == (14, 8)
    assert [g["id"] for g in meta["groups"]] == ["pose", "vitals", "env", "blocks"]
    assert meta["actuators"][-1]["label"] == "idle"


def test_c1_survival_flag_is_the_native_survival_instrument():
    # the mouth and the edible affordance (research topic native-survival);
    # every shipped id and offset before the hand is unchanged
    sensors, actuators = c1_anatomy(survival=True)
    body = Ros2Body(sensors, actuators, FakeTransport(script={}))
    meta = body.anatomy_meta()
    _assert_invariants(meta)
    assert (meta["obs_dim"], meta["n_actions"]) == (73, 13)
    groups = {g["id"]: (g["start"], g["width"]) for g in meta["groups"]}
    assert groups["hand"] == (19, 7)
    assert groups["grid"] == (26, 7)
    # the distal senses append after grid: every prior offset unchanged
    assert groups["drops"] == (33, 8)
    assert groups["glance"] == (41, 32)
    labels = {g["id"]: g.get("labels") for g in meta["groups"]}
    assert labels["hand"] == ["present", "placeable", "edible", "count", "sig0", "sig1", "sig2"]
    assert labels["drops"][:5] == ["present", "sin_b", "cos_b", "dist", "count"]
    assert labels["glance"][:4] == ["s0_dist", "s0_sig0", "s0_sig1", "s0_sig2"]
    assert [a["label"] for a in meta["actuators"][12:]] == ["use_held"]


def test_c1_aim_worth_form_appends_last_and_salience_changes_nothing():
    # the-aim (research topic, 2026-08-15): only the worth form widens
    # the declaration — 9 relative prices appended LAST; the salience
    # form is bridge behavior on the byte-identical declaration
    sensors, actuators = c1_anatomy(survival=True, flood=True, aim="worth")
    body = Ros2Body(sensors, actuators, FakeTransport(script={}))
    meta = body.anatomy_meta()
    _assert_invariants(meta)
    assert (meta["obs_dim"], meta["n_actions"]) == (86, 13)
    groups = {g["id"]: (g["start"], g["width"]) for g in meta["groups"]}
    assert groups["flood"] == (73, 4)  # every prior offset unchanged
    assert groups["aim"] == (77, 9)
    labels = {g["id"]: g.get("labels") for g in meta["groups"]}
    assert labels["aim"] == [f"s{k}" for k in range(8)] + ["drop"]
    plain = c1_anatomy(survival=True)
    assert c1_anatomy(survival=True, aim="salience") == plain
    assert sum(s.width for s in c1_anatomy(survival=True, aim="worth")[0]) == 82
    with pytest.raises(ValueError):
        c1_anatomy(aim="worth")  # the aim needs the distal body
    with pytest.raises(ValueError):
        c1_anatomy(survival=True, aim="wish")  # unknown form fails loud


def test_rover_meta_names_parts_and_actions():
    body = make_rover_body(Config(), np.random.default_rng(1))
    meta = body.anatomy_meta()
    _assert_invariants(meta)
    assert [g["id"] for g in meta["groups"]] == [part for part, _ in SENSOR_PARTS]
    assert [a["label"] for a in meta["actuators"]] == list(ACTION_NAMES)


def test_rover_meta_tracks_a_grown_sensor():
    body = make_rover_body(
        Config(obs_dim=11), np.random.default_rng(1), extra_ray=True, layout_seed=7
    )
    meta = body.anatomy_meta()
    _assert_invariants(meta)
    assert meta["obs_dim"] == 11
    assert meta["groups"][-1] == {"id": "ray_back", "start": 10, "width": 1}


def test_gymnasium_meta_is_structural():
    world = GymnasiumWorld(gymnasium.make("CartPole-v1"), seed=1)
    meta = world.anatomy_meta()
    _assert_invariants(meta)
    assert meta["groups"] == [{"id": "obs", "start": 0, "width": 4}]
    assert [a["label"] for a in meta["actuators"]] == ["a0", "a1"]
