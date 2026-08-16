"""The C1 anatomy declaration (features 027 + 030 + 031 + 033 + 044).

Declaration is configuration (013 SC-006): the body is these lists, and
the channel contract in specs/027-minecraft-body/contracts/ (as amended
by 030/031/033 and the survival sections) is the meaning of every
dimension. **The default is the survival body** — obs_dim 86,
n_actions 13 (feature 044, design 0015's measured operating point):
the property body of feature 033 (classifier-free senses, appearance
signatures, held intentions, the sensed staging grid) plus the mouth
(`use_held`, edible affordance), the distal senses (drops + glance),
the flood channel, and the palate's worth channel. ``survival=False``
gives the pre-044 property body (obs_dim 32, n_actions 12);
``crafting=False`` is the exact feature-027 body (obs_dim 14,
n_actions 8) — the recorded reversal path.

``survival=True`` is the **native-survival instrument** (research topic
native-survival, 2026-08-11; ships into the default only on promotion):
the hand channel widens to 7 with `edible` beside `placeable` (the
game's own fact: the held item maps to a food), and `use_held` — apply
the held item, a held intention like the dig — joins as action id 12.
The distal senses (topic distal-senses, 2026-08-13) append after
`grid`: `drops` (8 — nearest ground item: presence, egocentric
bearing, distance, count, signature) and `glance` (32 — eight
egocentric sectors of feet-level distance-to-surface + that surface's
signature). obs_dim 73, n_actions 13; every shipped id and offset
unchanged.

The aim (research topic the-aim, 2026-08-15) is the palate — worth
eaten into existence (episode 0089's EMA) — read at the distance. Its
worth form appends `aim` (9 — one relative price per glance sector +
the sensed drop's) LAST; its salience form changes no declaration at
all (hungry, unpriced appearances fade at the bridge).
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

# The native-survival instrument (see module doc): the widened hand and the
# mouth. Appended AFTER the shipped presets so ids 0–11 keep their meaning.
_SURVIVAL_HAND = SensorSpec(
    id="hand",
    topic="hand",
    width=7,
    labels=("present", "placeable", "edible", "count", "sig0", "sig1", "sig2"),
)
_SURVIVAL_PRESETS: tuple[dict, ...] = ({"use_held": 1.0},)

# The flood (research topic the-flood, 2026-08-13): the deficit expanded
# nonlinearly into the observation — a width-4 channel appended LAST
# (obs 77). Dim 0 is the flood level f; dims 1-3 carry the form's body
# (intrusion pseudo-noise or f-scaled classifier-free food cues) — the
# contract names the modes. The ablation body is the same anatomy with
# the channel silenced at the bridge.
_FLOOD = SensorSpec(id="flood", topic="flood", width=4, labels=("f", "f1", "f2", "f3"))

# The distal senses (research topic distal-senses, 2026-08-13): the drops
# sense and the glance — egocentric, properties + signatures, appended
# after `grid` so every shipped offset is unchanged.
_SURVIVAL_DISTAL: tuple[SensorSpec, ...] = (
    SensorSpec(
        id="drops",
        topic="drops",
        width=8,
        labels=("present", "sin_b", "cos_b", "dist", "count", "sig0", "sig1", "sig2"),
    ),
    SensorSpec(
        id="glance",
        topic="glance",
        width=32,
        labels=tuple(f"s{k}_{n}" for k in range(8) for n in ("dist", "sig0", "sig1", "sig2")),
    ),
)

# The aim (research topic the-aim, 2026-08-15): the palate's learned,
# relative prices read at the distance. Only the worth form widens the
# declaration — one worth per glance sector plus the sensed drop's,
# appended LAST so every prior offset (flood included) is unchanged.
# The salience form is bridge behavior on the same declaration: hungry,
# unpriced appearances fade toward each sense's own "nothing" reading.
_AIM = SensorSpec(
    id="aim",
    topic="aim",
    width=9,
    labels=tuple(f"s{k}" for k in range(8)) + ("drop",),
)


def c1_anatomy(
    crafting: bool = True,
    survival: bool | None = None,
    flood: bool | None = None,
    aim: str | None = None,
) -> tuple[list[SensorSpec], list[ActuatorSpec]]:
    """The (sensors, actuators) lists `Ros2Body.factory` expects.

    **The default is the survival body** (feature 044, promoted from
    design 0015's measured operating point): the property body plus
    the mouth, the distal senses, the flood, and the worth channel —
    obs_dim 86, n_actions 13. Every EXPLICIT flag keeps its exact
    pre-044 meaning; only the zero-argument default changed.
    ``survival=False``: the pre-044 default (the property body, 32/12).
    ``crafting=False``: the exact feature-027 body (14/8).
    ``flood=True``/``aim="worth"``: the instrument senses individually
    (module doc); ``aim="salience"`` is bridge behavior only, the
    declaration byte-identical to ``aim=""``.
    """
    if survival is None:
        blessed = crafting  # the zero-override default: design 0015's stack
        survival = blessed
        if flood is None:
            flood = blessed
        if aim is None:
            aim = "worth" if blessed else ""
    else:
        if flood is None:
            flood = False
        if aim is None:
            aim = ""
    if survival and not crafting:
        raise ValueError("survival needs the property body: the 027 body has no hand channel")
    if flood and not survival:
        raise ValueError("the flood is a survival-instrument sense: it needs the meter body")
    if aim not in ("", "salience", "worth"):
        raise ValueError(f"unknown aim form {aim!r}: expected '', 'salience', or 'worth'")
    if aim and not survival:
        raise ValueError("the aim is a survival-instrument sense: it needs the distal body")
    sensors = list(_BASE_SENSORS) + (list(_PROPERTY_SENSORS) if crafting else [])
    if survival:
        sensors = [_SURVIVAL_HAND if s.id == "hand" else s for s in sensors]
        sensors += list(_SURVIVAL_DISTAL)
    if flood:
        sensors.append(_FLOOD)
    if aim == "worth":
        sensors.append(_AIM)
    presets = _BASE_PRESETS + (_GRID_PRESETS if crafting else ())
    presets += _SURVIVAL_PRESETS if survival else ()
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
