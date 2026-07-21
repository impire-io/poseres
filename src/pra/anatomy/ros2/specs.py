"""Anatomy declaration for ROS2 worlds: plain data, duck-typed helpers (feature 013).

Declaration is configuration, not code (spec SC-006): a robot's anatomy is a
list of :class:`SensorSpec` and :class:`ActuatorSpec` values — topics, widths,
message-type *names*, attribute paths, and preset field values. Nothing in
this module imports ROS2 (research R5): the helpers operate on duck-typed
message objects, so the whole declaration layer is testable with plain
namespaces on machines where ROS2 cannot exist, and only the real transport
ever resolves a type name to a class.

Flattening contract (:func:`extract_vector`): the value resolved by the
spec's attribute path is flattened, C-order, to float64 —

- numbers contribute themselves;
- arrays and sequences contribute their elements, recursively;
- message compounds contribute their fields in the table's fixed order:
  ``(x, y, z, w)`` (Quaternion), ``(x, y, z)`` (Vector3/Point),
  ``(position, orientation)`` (Pose → 7), ``(linear, angular)`` (Twist → 6);
- anything else fails loudly, naming the sensor, the topic, and the shape.

The result must match the declared width exactly — never truncated, never
padded (FR-002).
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass

import numpy as np

from pra.anatomy.body import AnatomyError

__all__ = ["ActuatorSpec", "SensorSpec", "apply_fields", "extract_vector"]

# The compound-flattening table (research R5): the first row whose attributes
# are all present wins; its fields flatten recursively, in row order. The
# order is part of the adapter's documented contract.
_COMPOUND_ROWS: tuple[tuple[str, ...], ...] = (
    ("x", "y", "z", "w"),  # Quaternion
    ("x", "y", "z"),  # Vector3 / Point
    ("position", "orientation"),  # Pose -> 3 + 4
    ("linear", "angular"),  # Twist / Accel -> 3 + 3
)


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise AnatomyError(message)


def _valid_path(path: str) -> bool:
    return all(part.isidentifier() for part in path.split("."))


@dataclass(frozen=True)
class SensorSpec:
    """One topic subscription: `width` float64 values per message.

    ``extract`` selects what to flatten: an empty string means the whole
    payload; a dotted attribute path (``"ranges"``, ``"pose.pose.position"``)
    resolves into the message; a callable is the escape hatch for payloads
    the path syntax cannot reach. ``msg_type`` is required only by the real
    transport (the fake delivers payload objects directly).
    """

    id: str
    topic: str
    width: int
    msg_type: str = ""
    extract: str | Callable[[object], object] = ""
    labels: tuple[str, ...] | None = None  # per-channel names (feature 033 telemetry)

    def __post_init__(self) -> None:
        if self.labels is not None:
            _require(
                len(self.labels) == self.width,
                f"sensor '{self.id}': labels must match width ({self.width})",
            )
        _require(
            bool(self.id) and isinstance(self.id, str), "SensorSpec.id must be a non-empty string"
        )
        _require(
            bool(self.topic) and isinstance(self.topic, str),
            f"sensor '{self.id}': topic must be a non-empty string",
        )
        _require(
            isinstance(self.width, int) and self.width >= 1,
            f"sensor '{self.id}': width must be an int >= 1 (Doc 02 sensor contract)",
        )
        if isinstance(self.extract, str):
            _require(
                self.extract == "" or _valid_path(self.extract),
                f"sensor '{self.id}': extract path {self.extract!r} is not a dotted attribute path",
            )
        else:
            _require(
                callable(self.extract),
                f"sensor '{self.id}': extract must be a dotted path or a callable",
            )


@dataclass(frozen=True)
class ActuatorSpec:
    """One topic publication: local action *i* publishes preset *i*.

    A preset is a mapping of dotted field path -> numeric value; fields not
    named keep the message type's defaults (an empty preset is a valid
    "all defaults" command, e.g. Twist's stop). ``msg_type`` is required only
    by the real transport.
    """

    id: str
    topic: str
    presets: tuple[Mapping[str, float], ...]
    msg_type: str = ""

    def __post_init__(self) -> None:
        _require(
            bool(self.id) and isinstance(self.id, str), "ActuatorSpec.id must be a non-empty string"
        )
        _require(
            bool(self.topic) and isinstance(self.topic, str),
            f"actuator '{self.id}': topic must be a non-empty string",
        )
        presets = tuple(self.presets)
        object.__setattr__(self, "presets", presets)
        _require(
            len(presets) >= 1,
            f"actuator '{self.id}': at least one preset is required (Doc 02 actuator contract)",
        )
        for k, preset in enumerate(presets):
            _require(
                isinstance(preset, Mapping),
                f"actuator '{self.id}': preset {k} must be a mapping of field path -> value",
            )
            for path, value in preset.items():
                _require(
                    isinstance(path, str) and _valid_path(path),
                    f"actuator '{self.id}': preset {k} key {path!r} is not a dotted field path",
                )
                _require(
                    isinstance(value, int | float) and not isinstance(value, bool),
                    f"actuator '{self.id}': preset {k} field {path!r} must be numeric",
                )


def extract_vector(msg: object, spec: SensorSpec) -> np.ndarray:
    """Resolve the spec's extraction against ``msg`` and flatten to float64.

    Loud on every honest failure mode (FR-002): a missing attribute path, a
    non-numeric payload, a width mismatch, and a **non-finite value** all
    raise :class:`AnatomyError` naming the sensor, the topic, and the
    offending shape. Non-finite is a delivery error because the frames have
    no missing-data semantics (research R3/R5): a real sensor that emits
    NaN/±inf — a lidar's no-hit or below-min-range beams, for instance —
    must be sanitized *explicitly* in a callable ``extract``, where the
    choice is declared and visible, never passed through to poison the
    learning surface (the worked example's lidar does exactly this).
    """
    value = msg
    if callable(spec.extract):
        value = spec.extract(msg)
    elif spec.extract:
        for part in spec.extract.split("."):
            try:
                value = getattr(value, part)
            except AttributeError:
                raise AnatomyError(
                    f"sensor '{spec.id}' on topic '{spec.topic}': message of type "
                    f"{type(msg).__name__} has no attribute path {spec.extract!r} "
                    f"(failed at {part!r})"
                ) from None
    try:
        flat = np.asarray(_flatten(value), dtype=np.float64)
    except (TypeError, ValueError) as err:
        raise AnatomyError(
            f"sensor '{spec.id}' on topic '{spec.topic}': payload is not a "
            f"fixed-width numeric vector ({err})"
        ) from None
    if flat.shape != (spec.width,):
        raise AnatomyError(
            f"sensor '{spec.id}' on topic '{spec.topic}' declared width {spec.width} "
            f"but the delivered payload flattens to {flat.size} value(s)"
        )
    if not np.isfinite(flat).all():
        bad = int(np.count_nonzero(~np.isfinite(flat)))
        raise AnatomyError(
            f"sensor '{spec.id}' on topic '{spec.topic}' delivered {bad} non-finite "
            f"value(s) (NaN/±inf) — sanitize them in a callable extract= "
            "(e.g. clamp a lidar's no-hit beams to its max range); the learning "
            "surface has no missing-data semantics"
        )
    return flat


def _flatten(value: object) -> list[float]:
    """The recursive flattening rule behind :func:`extract_vector` (module doc)."""
    if isinstance(value, bool | int | float | np.integer | np.floating):
        return [float(value)]
    if isinstance(value, np.ndarray):
        return [float(v) for v in value.ravel()]
    if isinstance(value, str | bytes):
        raise TypeError(f"cannot flatten {type(value).__name__} {value!r}")
    for row in _COMPOUND_ROWS:
        if all(hasattr(value, name) for name in row):
            out: list[float] = []
            for name in row:
                out.extend(_flatten(getattr(value, name)))
            return out
    try:
        items = iter(value)  # type: ignore[arg-type]
    except TypeError:
        raise TypeError(f"cannot flatten {type(value).__name__}") from None
    out = []
    for item in items:
        out.extend(_flatten(item))
    return out


def apply_fields(msg: object, preset: Mapping[str, float]) -> object:
    """Assign a preset's dotted field paths onto a message object, in place.

    Numeric target fields keep their own type (rclpy enforces field types, so
    an int preset value lands on a float64 field as float). A path the message
    does not have fails loudly — a preset typo must never publish silently.
    """
    for path, value in preset.items():
        target = msg
        *parents, leaf = path.split(".")
        try:
            for part in parents:
                target = getattr(target, part)
            current = getattr(target, leaf)
        except AttributeError as err:
            raise AnatomyError(
                f"preset field {path!r} does not exist on message type {type(msg).__name__} ({err})"
            ) from None
        if isinstance(current, bool | int | float):
            value = type(current)(value)
        setattr(target, leaf, value)
    return msg
