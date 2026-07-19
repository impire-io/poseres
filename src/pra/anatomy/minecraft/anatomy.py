"""The C1 anatomy declaration (feature 027, research R3/R4).

Declaration is configuration (013 SC-006): the body is these lists, and
the channel contract in specs/027-minecraft-body/contracts/ is the
meaning of every dimension. obs_dim 14, n_actions 8 — inside the
validated envelope (arc 026 sizing).
"""

from __future__ import annotations

from pra.anatomy.ros2.specs import ActuatorSpec, SensorSpec

__all__ = ["C1_ACTUATORS", "C1_N_ACTIONS", "C1_OBS_DIM", "C1_SENSORS", "c1_anatomy"]

C1_SENSORS: tuple[SensorSpec, ...] = (
    SensorSpec(id="pose", topic="pose", width=5),
    SensorSpec(id="vitals", topic="vitals", width=2),
    SensorSpec(id="env", topic="env", width=4),
    SensorSpec(id="blocks", topic="blocks", width=3),
)

C1_ACTUATORS: tuple[ActuatorSpec, ...] = (
    ActuatorSpec(
        id="control",
        topic="control",
        presets=(
            {"forward": 1.0},
            {"back": 1.0},
            {"turn_left": 1.0},
            {"turn_right": 1.0},
            {"jump_forward": 1.0},
            {"dig_ahead": 1.0},
            {"place_ahead": 1.0},
            {},  # idle: the all-defaults command
        ),
    ),
)

C1_OBS_DIM = sum(s.width for s in C1_SENSORS)
C1_N_ACTIONS = sum(len(a.presets) for a in C1_ACTUATORS)


def c1_anatomy() -> tuple[list[SensorSpec], list[ActuatorSpec]]:
    """The (sensors, actuators) lists `Ros2Body.factory` expects."""
    return list(C1_SENSORS), list(C1_ACTUATORS)
