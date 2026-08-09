"""The C1 anatomy declaration (features 027 + 030 + 031 + 033).

Declaration is configuration (013 SC-006): the body is these lists, and
the channel contract in specs/027-minecraft-body/contracts/ (as amended
by 030/031/033) is the meaning of every dimension. The default is the
**property body** — obs_dim 32, n_actions 12: no material classifiers
anywhere (owner's argument, feature 033) — the pocket senses aggregates,
the hand and the grid's offer sense world-mechanical *properties*
(placeable, counts) plus a stable *appearance signature* (sha256-derived;
things look different, nobody names them), digging progress is sensed
(`mining`), and every channel carries its label. Categories are the
brain's to form. ``crafting=False`` is the exact feature-027 body
(obs_dim 14, n_actions 8) — the recorded reversal path.
"""

from __future__ import annotations

from pra.anatomy.ros2.specs import ActuatorSpec, SensorSpec

__all__ = [
    "C1_ACTUATORS",
    "C1_MINING_INDEX",
    "C1_N_ACTIONS",
    "C1_OBS_DIM",
    "C1_POCKET_TOTAL_INDEX",
    "C1_SENSORS",
    "c1_anatomy",
]

_BASE_SENSORS: tuple[SensorSpec, ...] = (
    SensorSpec(id="pose", topic="pose", width=5, labels=("x", "z", "y", "sin_yaw", "cos_yaw")),
    SensorSpec(id="vitals", topic="vitals", width=2, labels=("health", "food")),
    SensorSpec(id="env", topic="env", width=4, labels=("light", "sin_time", "cos_time", "rain")),
    SensorSpec(
        id="blocks", topic="blocks", width=3, labels=("solid_ahead", "solid_eye", "drop_ahead")
    ),
)

_PROPERTY_SENSORS: tuple[SensorSpec, ...] = (
    SensorSpec(id="mining", topic="mining", width=1, labels=("progress",)),
    SensorSpec(
        id="pocket", topic="pocket", width=4, labels=("total", "kinds", "placeable", "other")
    ),
    SensorSpec(
        id="hand",
        topic="hand",
        width=6,
        labels=("present", "placeable", "count", "sig0", "sig1", "sig2"),
    ),
    SensorSpec(
        id="grid",
        topic="grid",
        width=7,
        labels=(
            "staged",
            "offer",
            "offer_placeable",
            "offer_count",
            "offer_sig0",
            "offer_sig1",
            "offer_sig2",
        ),
    ),
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

    ``crafting=True`` (default): the property body — classifier-free
    senses, held intentions, the sensed staging grid.
    ``crafting=False``: the exact feature-027 body.
    """
    sensors = list(_BASE_SENSORS) + (list(_PROPERTY_SENSORS) if crafting else [])
    presets = _BASE_PRESETS + (_GRID_PRESETS if crafting else ())
    return sensors, [ActuatorSpec(id="control", topic="control", presets=presets)]


C1_SENSORS: tuple[SensorSpec, ...] = tuple(c1_anatomy()[0])
C1_ACTUATORS: tuple[ActuatorSpec, ...] = tuple(c1_anatomy()[1])
C1_OBS_DIM = sum(s.width for s in C1_SENSORS)
C1_N_ACTIONS = sum(len(a.presets) for a in C1_ACTUATORS)


def _channel_index(sensor_id: str, label: str) -> int:
    """The flat observation index of one labeled channel, derived from the
    sensor specs in declaration order — never a hard-coded literal, so a
    spec change moves the constants with it (feature 040 FR-010)."""
    offset = 0
    for spec in C1_SENSORS:
        if spec.id == sensor_id:
            return offset + spec.labels.index(label)
        offset += spec.width
    raise ValueError(f"unknown sensor {sensor_id!r}")


# The completion-itch policy's anatomy knowledge (feature 040): the sensed
# dig-progress channel and the pocket-total channel (one item = 1/64).
C1_MINING_INDEX = _channel_index("mining", "progress")
C1_POCKET_TOTAL_INDEX = _channel_index("pocket", "total")
