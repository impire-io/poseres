"""The C1 anatomy declaration (features 027 + 030 + 031, research R3/R4).

Declaration is configuration (013 SC-006): the body is these lists, and
the channel contract in specs/027-minecraft-body/contracts/ (as amended
by features 030/031) is the meaning of every dimension. The default is
the builder's body — obs_dim 28, n_actions 12: the feature-027 channels
plus the pocket (inventory), the held class (hand), and the sensed 2x2
staging grid, with **honest primitives** — held-class selection and
grid staging — instead of macro craft actions (feature 031: crafting is
a ladder the brain may climb, not a button). ``crafting=False`` is the
exact feature-027 body (obs_dim 14, n_actions 8) — the recorded
reversal path (spec 031, Assumptions).
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

_BUILDER_SENSORS: tuple[SensorSpec, ...] = (
    SensorSpec(id="inventory", topic="inventory", width=5),
    SensorSpec(id="hand", topic="hand", width=4),
    SensorSpec(id="grid", topic="grid", width=5),
)

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

_GRID_PRESETS: tuple[dict, ...] = (
    {"hold_next": 1.0},
    {"grid_put": 1.0},
    {"grid_take": 1.0},
    {"take_result": 1.0},
)


def c1_anatomy(crafting: bool = True) -> tuple[list[SensorSpec], list[ActuatorSpec]]:
    """The (sensors, actuators) lists `Ros2Body.factory` expects.

    ``crafting=True`` (default): the builder's body — pocket, hand, and
    staging-grid senses with the honest grid primitives.
    ``crafting=False``: the exact feature-027 body.
    """
    sensors = list(_BASE_SENSORS) + (list(_BUILDER_SENSORS) if crafting else [])
    presets = _BASE_PRESETS + (_GRID_PRESETS if crafting else ())
    return sensors, [ActuatorSpec(id="control", topic="control", presets=presets)]


C1_SENSORS: tuple[SensorSpec, ...] = tuple(c1_anatomy()[0])
C1_ACTUATORS: tuple[ActuatorSpec, ...] = tuple(c1_anatomy()[1])
C1_OBS_DIM = sum(s.width for s in C1_SENSORS)
C1_N_ACTIONS = sum(len(a.presets) for a in C1_ACTUATORS)
