"""The body: sensors, actuators, fixed-order composition, tools (Doc 02 §2–§5).

The anatomy is configurable and meaning-free: the system sees observations as
vectors (the fixed-order concatenation of all active sensors) and emits actions
as indices into the fixed-order disjoint union of all active actuators. The
declared order is semantic — changing it changes the meaning of every
observation dimension (Doc 02 §3.3).

The :class:`Body` satisfies the existing ``EventSource`` seam
(``reset``/``step``/``obs_dim``/``n_actions``), so it mounts wherever the
synthetic world mounts today — with 1:1 delegation for a world-only body, which
is what makes world-through-body runs byte-identical to the direct connection
(feature 004 research R1). Tool registrations are queued and take effect only
when the Engine calls :meth:`Body.apply_pending_tools` at a slow-loop boundary
(C4, Doc 02 §5.2); the only feedback path from an action is subsequent
observations (actuators return nothing, Doc 02 §4.2).
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

import numpy as np

__all__ = [
    "Sensor",
    "Actuator",
    "AnatomyError",
    "Body",
    "WorldSensor",
    "WorldActuator",
    "ConstantSensor",
]


class AnatomyError(ValueError):
    """A body-contract violation (wrong width, duplicate id, invalid routing)."""


@runtime_checkable
class Sensor(Protocol):
    def id(self) -> str: ...
    def width(self) -> int: ...
    def read(self) -> np.ndarray: ...


@runtime_checkable
class Actuator(Protocol):
    def id(self) -> str: ...
    def action_count(self) -> int: ...
    def apply(self, local_action_index: int) -> None: ...


class WorldSensor:
    """Mounts the synthetic world's observation as one sensor. The world emits
    on reset/step; this sensor exposes the cached emission (width = obs_dim)."""

    def __init__(self, world, sensor_id: str = "world"):
        self._world = world
        self._id = sensor_id
        self.last: np.ndarray | None = None

    def id(self) -> str:
        return self._id

    def width(self) -> int:
        return int(self._world.obs_dim)

    def read(self) -> np.ndarray:
        if self.last is None:
            raise AnatomyError(f"sensor '{self._id}' read before the first emission")
        return self.last


class WorldActuator:
    """Mounts the synthetic world's action space; applying steps the world and
    feeds the paired WorldSensor's cache. Returns nothing (Doc 02 §4.2)."""

    def __init__(self, world, sensor: WorldSensor, actuator_id: str = "world"):
        self._world = world
        self._sensor = sensor
        self._id = actuator_id

    def id(self) -> str:
        return self._id

    def action_count(self) -> int:
        return int(self._world.n_actions)

    def apply(self, local_action_index: int) -> None:
        self._sensor.last = self._world.step(local_action_index)


class ConstantSensor:
    """A fixed-vector sensor (no RNG) — the tool-demo and test part."""

    def __init__(self, sensor_id: str, values):
        self._id = sensor_id
        self._values = np.asarray(values, dtype=np.float64)

    def id(self) -> str:
        return self._id

    def width(self) -> int:
        return int(self._values.shape[0])

    def read(self) -> np.ndarray:
        return self._values


class Body:
    """Fixed-order composition of sensors and actuators around an environment.

    EventSource-compatible: ``reset()`` begins an episode on the environment
    (the world sensor caches the first emission) and composes the observation;
    ``step(a)`` routes the global index to ``(actuator, local)`` and composes
    all sensors' reads. ``obs_dim``/``n_actions`` are derived from the active
    parts and change only when :meth:`apply_pending_tools` applies queued
    registrations at a slow-loop boundary.
    """

    def __init__(self, environment, sensors: list, actuators: list):
        if not sensors or not actuators:
            raise AnatomyError("a body needs at least one sensor and one actuator")
        self._environment = environment
        self._sensors: list = []
        self._actuators: list = []
        self._pending: list[tuple[str, object]] = []
        for s in sensors:
            self._add_sensor(s)
        for a in actuators:
            self._add_actuator(a)
        # World-state capture (feature 008): a body is capturable exactly when
        # its environment is, so the protocol is exposed per instance — the
        # engine's capability check stays honest for bodies around
        # non-capturing environments.
        if callable(getattr(environment, "state_dict", None)) and callable(
            getattr(environment, "load_state_dict", None)
        ):
            self.state_dict = environment.state_dict
            self.load_state_dict = environment.load_state_dict

    # ---- derived anatomy (Doc 02 §3.3 / §4.2) ---------------------------------
    @property
    def obs_dim(self) -> int:
        return sum(s.width() for s in self._sensors)

    @property
    def n_actions(self) -> int:
        return sum(a.action_count() for a in self._actuators)

    # ---- EventSource surface --------------------------------------------------
    def reset(self) -> np.ndarray:
        first = self._environment.reset()
        for s in self._sensors:
            if isinstance(s, WorldSensor):
                s.last = first
        return self._compose()

    def step(self, action: int) -> np.ndarray:
        actuator, local = self.route(action)
        actuator.apply(local)
        return self._compose()

    # ---- composition & routing ------------------------------------------------
    def _compose(self) -> np.ndarray:
        parts = []
        for s in self._sensors:
            value = np.asarray(s.read(), dtype=np.float64)
            if value.shape != (s.width(),):
                raise AnatomyError(
                    f"sensor '{s.id()}' returned shape {value.shape}, declared width {s.width()}"
                )
            parts.append(value)
        return parts[0] if len(parts) == 1 else np.concatenate(parts)

    def route(self, action: int) -> tuple[object, int]:
        """Global index -> (actuator, local index), by fixed declared order."""
        if not 0 <= action < self.n_actions:
            raise AnatomyError(f"action {action} outside [0, {self.n_actions})")
        offset = 0
        for a in self._actuators:
            count = a.action_count()
            if action < offset + count:
                return a, action - offset
            offset += count
        raise AnatomyError("unreachable: routing table exhausted")  # pragma: no cover

    # ---- ToolRegistry (Doc 02 §5): queued, applied at the slow loop ------------
    def register_sensor(self, sensor) -> str:
        self._check_new_id(sensor.id())
        self._pending.append(("sensor", sensor))
        return sensor.id()

    def register_actuator(self, actuator) -> str:
        self._check_new_id(actuator.id())
        self._pending.append(("actuator", actuator))
        return actuator.id()

    def deregister(self, tool_id: str) -> None:
        self._pending.append(("deregister", tool_id))

    def list_tools(self) -> list[tuple[str, str]]:
        return [(s.id(), "sensor") for s in self._sensors] + [
            (a.id(), "actuator") for a in self._actuators
        ]

    def apply_pending_tools(self) -> tuple[int, int] | None:
        """Apply queued registrations (slow loop only, C4). Returns the new
        ``(obs_dim, n_actions)`` iff anything changed, else None."""
        if not self._pending:
            return None
        for kind, item in self._pending:
            if kind == "sensor":
                self._add_sensor(item)
            elif kind == "actuator":
                self._add_actuator(item)
            else:
                self._remove(item)
        self._pending.clear()
        return self.obs_dim, self.n_actions

    # ---- internals --------------------------------------------------------------
    def _check_new_id(self, tool_id: str) -> None:
        active = {i for i, _ in self.list_tools()}
        queued = {(item.id() if kind != "deregister" else item) for kind, item in self._pending}
        if tool_id in active or tool_id in queued:
            raise AnatomyError(f"duplicate tool id '{tool_id}'")

    def _add_sensor(self, sensor) -> None:
        if sensor.width() < 1:
            raise AnatomyError(f"sensor '{sensor.id()}' declares width < 1")
        self._sensors.append(sensor)

    def _add_actuator(self, actuator) -> None:
        if actuator.action_count() < 1:
            raise AnatomyError(f"actuator '{actuator.id()}' declares no actions")
        self._actuators.append(actuator)

    def _remove(self, tool_id: str) -> None:
        for group, kind in ((self._sensors, "sensor"), (self._actuators, "actuator")):
            for part in group:
                if part.id() == tool_id:
                    if len(group) == 1:
                        raise AnatomyError(f"cannot deregister the last {kind} ('{tool_id}')")
                    group.remove(part)
                    return
        raise AnatomyError(f"no tool with id '{tool_id}'")
