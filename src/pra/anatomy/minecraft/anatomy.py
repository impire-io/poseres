"""The C1 anatomy declaration (features 027 + 030, research R3/R4).

Declaration is configuration (013 SC-006): the body is these lists, and
the channel contract in specs/027-minecraft-body/contracts/ (as amended
by feature 030) is the meaning of every dimension. The default is the
builder's body — obs_dim 19, n_actions 10: the feature-027 channels
plus the width-5 inventory sense and the two pocket-craft actions.
``crafting=False`` is the exact feature-027 body (obs_dim 14,
n_actions 8) — the recorded reversal path (spec 030, Assumptions).
"""

from __future__ import annotations

from pra.anatomy.ros2.specs import ActuatorSpec, SensorSpec

__all__ = ["C1_ACTUATORS", "C1_N_ACTIONS", "C1_OBS_DIM", "C1_SENSORS", "c1_anatomy"]

_BASE_SENSORS: tuple[SensorSpec, ...] = (
    SensorSpec(id="pose", topic="pose", width=5),
    SensorSpec(id="vitals", topic="vitals", width=2),
    SensorSpec(id="env", topic="env", width=4),
    SensorSpec(id="blocks", topic="blocks", width=3),
)

_INVENTORY_SENSOR = SensorSpec(id="inventory", topic="inventory", width=5)

_BASE_PRESETS: tuple[dict, ...] = (
    {"forward": 1.0},
    {"back": 1.0},
    {"turn_left": 1.0},
    {"turn_right": 1.0},
    {"jump_forward": 1.0},
    {"dig_ahead": 1.0},
    {"place_ahead": 1.0},
    {},  # idle: the all-defaults command
)

_CRAFT_PRESETS: tuple[dict, ...] = (
    {"craft_planks": 1.0},
    {"craft_sticks": 1.0},
)


def c1_anatomy(crafting: bool = True) -> tuple[list[SensorSpec], list[ActuatorSpec]]:
    """The (sensors, actuators) lists `Ros2Body.factory` expects.

    ``crafting=True`` (default): the builder's body — inventory sense +
    craft actions. ``crafting=False``: the exact feature-027 body.
    """
    sensors = list(_BASE_SENSORS) + ([_INVENTORY_SENSOR] if crafting else [])
    presets = _BASE_PRESETS + (_CRAFT_PRESETS if crafting else ())
    return sensors, [ActuatorSpec(id="control", topic="control", presets=presets)]


C1_SENSORS: tuple[SensorSpec, ...] = tuple(c1_anatomy()[0])
C1_ACTUATORS: tuple[ActuatorSpec, ...] = tuple(c1_anatomy()[1])
C1_OBS_DIM = sum(s.width for s in C1_SENSORS)
C1_N_ACTIONS = sum(len(a.presets) for a in C1_ACTUATORS)
