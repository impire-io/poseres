"""The Transport seam and the real rclpy transport (feature 013, research R2/R7).

`Transport` is the boundary between adapter logic and message delivery
(FR-008): the fake implementation (`pra.anatomy.ros2.fake`) proves the whole
contract in this repository's quality gate; :class:`RclpyTransport` is the
deployment implementation over a ROS2 client library that **ships with a ROS2
distribution, not from PyPI** — there is deliberately no pip extra to name
(research R7), and constructing this class without a sourced ROS2 environment
says exactly that.

Tick modes (research R2):

- ``free_running`` — one wall-clock tick period per control tick (default
  100 ms = 10 Hz), delivering messages until the deadline; a tick whose
  delivery work overruns its period counts in ``overruns`` (the honesty
  meter for real-time claims). Non-reproducible by nature (Doc 06 §5b).
- ``stepped`` — a simulator step service advances the world per control tick
  (the world starts paused); after the step completes, a short drain window
  delivers what the bridge published. Replayable to the extent the simulator
  is deterministic. This is the worked example's mode.

Service wiring is declared as data, like everything else in this adapter:
service name + service type name + request field paths (see
``examples/ros2/`` for the Gazebo wiring). The rclpy-only glue in this module
is exercised by the containerized example — outside the repo's gate, stated
openly (plan Constitution Check).
"""

from __future__ import annotations

import importlib
import time
from collections.abc import Callable, Mapping
from typing import Protocol, runtime_checkable

from pra.anatomy.body import AnatomyError
from pra.anatomy.ros2.specs import ActuatorSpec, SensorSpec, apply_fields

__all__ = ["RclpyTransport", "Transport"]

try:  # rclpy exists only inside a sourced ROS2 environment; see _require_rclpy
    import rclpy as _rclpy
except ImportError:  # pragma: no cover - covered via monkeypatch (repo no-skip rule)
    _rclpy = None

_RCLPY_HELP = (
    "the ROS2 transport needs the 'rclpy' package, which ships with a ROS 2 "
    "distribution and is not installable from PyPI — source a ROS 2 environment "
    "(https://docs.ros.org), or run the containerized worked example in "
    "examples/ros2/ (no local ROS 2 needed; the FakeTransport quickstart in "
    "specs/013-ros2-adapter/quickstart.md needs none either)"
)


def _require_rclpy():
    if _rclpy is None:
        raise ImportError(_RCLPY_HELP)
    return _rclpy


@runtime_checkable
class Transport(Protocol):
    """The delivery boundary. See the module doc; the contract lives in
    specs/013-ros2-adapter/contracts/ros2-adapter.md and is asserted against
    the fake implementation."""

    def start(self) -> None: ...
    def subscribe(self, spec: SensorSpec, deliver: Callable[[object], None]) -> None: ...
    def publish(self, spec: ActuatorSpec, preset_index: int) -> None: ...
    def tick(self) -> None: ...
    @property
    def can_reset(self) -> bool: ...
    def reset_world(self) -> None: ...
    @property
    def overruns(self) -> int: ...
    def close(self) -> None: ...


def _resolve_type(name: str, what: str):
    """``"geometry_msgs/msg/Twist"`` -> the class. Real transport only."""
    parts = name.split("/")
    if len(parts) != 3:
        raise AnatomyError(
            f"{what} type {name!r} is not of the form 'package/kind/Name' "
            "(e.g. 'geometry_msgs/msg/Twist')"
        )
    package, kind, cls_name = parts
    module = importlib.import_module(f"{package}.{kind}")
    try:
        return getattr(module, cls_name)
    except AttributeError:
        raise AnatomyError(f"{what} type {name!r}: {package}.{kind} has no {cls_name!r}") from None


class RclpyTransport:
    """The deployment transport (see module doc). Container-verified glue."""

    def __init__(
        self,
        *,
        mode: str = "free_running",
        tick_period: float = 0.1,
        node_name: str = "pra_ros2_body",
        step_service: str | None = None,
        step_service_type: str | None = None,
        step_fields: Mapping[str, float] | None = None,
        reset_service: str | None = None,
        reset_service_type: str | None = None,
        reset_fields: Mapping[str, float] | None = None,
        service_timeout: float = 5.0,
        drain_period: float = 0.05,
    ):
        _require_rclpy()
        if mode not in ("free_running", "stepped"):
            raise AnatomyError(f"unknown mode {mode!r}: 'free_running' or 'stepped'")
        if mode == "stepped" and not (step_service and step_service_type):
            raise AnatomyError(
                "stepped mode needs step_service and step_service_type "
                "(the simulator's world-control step interface)"
            )
        if float(tick_period) <= 0 or float(service_timeout) <= 0 or float(drain_period) < 0:
            raise AnatomyError("tick_period/service_timeout must be > 0, drain_period >= 0")
        if bool(reset_service) != bool(reset_service_type):
            raise AnatomyError("reset_service and reset_service_type come together")
        self._mode = mode
        self._tick_period = float(tick_period)
        self._node_name = node_name
        self._step = (step_service, step_service_type, dict(step_fields or {}))
        self._reset = (reset_service, reset_service_type, dict(reset_fields or {}))
        self._service_timeout = float(service_timeout)
        self._drain_period = float(drain_period)
        self._pending_subs: list[tuple[SensorSpec, Callable[[object], None]]] = []
        self._publishers: dict[str, object] = {}
        self._node = None
        self._executor = None
        self._step_client = None
        self._reset_client = None
        self._we_initialized = False
        self._overruns = 0
        self._closed = False

    # ---- Transport surface ----------------------------------------------------
    def start(self) -> None:
        if self._node is not None:
            raise AnatomyError(
                "transport already started — a ROS2 world boots exactly once "
                "(the feature-008 single-boot contract)"
            )
        rclpy = _require_rclpy()
        if not rclpy.ok():
            rclpy.init()
            self._we_initialized = True
        executors = importlib.import_module("rclpy.executors")
        self._node = rclpy.create_node(self._node_name)
        self._executor = executors.SingleThreadedExecutor()
        self._executor.add_node(self._node)
        for spec, deliver in self._pending_subs:
            self._make_subscription(spec, deliver)
        self._pending_subs.clear()
        if self._mode == "stepped":
            self._step_client = self._make_client(*self._step[:2], what="step service")
        if self.can_reset:
            self._reset_client = self._make_client(*self._reset[:2], what="reset service")

    def subscribe(self, spec: SensorSpec, deliver: Callable[[object], None]) -> None:
        if self._node is None:
            self._pending_subs.append((spec, deliver))
        else:
            self._make_subscription(spec, deliver)

    def publish(self, spec: ActuatorSpec, preset_index: int) -> None:
        self._require_started("publish")
        publisher = self._publishers.get(spec.topic)
        if publisher is None:
            if not spec.msg_type:
                raise AnatomyError(
                    f"actuator '{spec.id}': msg_type is required on the real transport"
                )
            publisher = self._node.create_publisher(  # type: ignore[union-attr]
                _resolve_type(spec.msg_type, f"actuator '{spec.id}' message"), spec.topic, 10
            )
            self._publishers[spec.topic] = publisher
        message = apply_fields(publisher.msg_type(), spec.presets[preset_index])
        publisher.publish(message)

    def tick(self) -> None:
        self._require_started("tick")
        if self._mode == "stepped":
            self._call(self._step_client, self._step, what="step service")
            self._spin_for(self._drain_period)
        else:
            started = time.monotonic()
            self._spin_for(self._tick_period)
            if time.monotonic() - started > self._tick_period * 1.5:
                self._overruns += 1

    @property
    def can_reset(self) -> bool:
        return self._reset[0] is not None

    def reset_world(self) -> None:
        if not self.can_reset:
            raise AnatomyError(
                "this transport declares no reset mechanism (reset_service) — "
                "run episode_mode='continuous'"
            )
        self._require_started("reset_world")
        self._call(self._reset_client, self._reset, what="reset service")

    @property
    def overruns(self) -> int:
        return self._overruns

    def close(self) -> None:
        if self._closed:
            return
        self._closed = True
        if self._node is not None:
            self._executor.remove_node(self._node)  # type: ignore[union-attr]
            self._node.destroy_node()
        if self._we_initialized:
            _require_rclpy().shutdown()

    # ---- rclpy glue (container-verified; see module doc) --------------------------
    def _make_subscription(self, spec: SensorSpec, deliver: Callable[[object], None]) -> None:
        if not spec.msg_type:
            raise AnatomyError(f"sensor '{spec.id}': msg_type is required on the real transport")
        qos = importlib.import_module("rclpy.qos")
        self._node.create_subscription(  # type: ignore[union-attr]
            _resolve_type(spec.msg_type, f"sensor '{spec.id}' message"),
            spec.topic,
            deliver,
            qos.qos_profile_sensor_data,  # the ecosystem's sensor-data convention
        )

    def _make_client(self, service: str, service_type: str, *, what: str):
        client = self._node.create_client(  # type: ignore[union-attr]
            _resolve_type(service_type, what), service
        )
        if not client.wait_for_service(timeout_sec=self._service_timeout):
            raise AnatomyError(f"{what} '{service}' not available after {self._service_timeout}s")
        return client

    def _call(self, client, wiring: tuple, *, what: str) -> None:
        service, _type_name, fields = wiring
        request = apply_fields(client.srv_type.Request(), fields)
        future = client.call_async(request)
        deadline = time.monotonic() + self._service_timeout
        while not future.done():
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise AnatomyError(
                    f"{what} '{service}' did not answer within {self._service_timeout}s"
                )
            self._executor.spin_once(timeout_sec=remaining)  # type: ignore[union-attr]
        if future.exception() is not None:
            raise AnatomyError(f"{what} '{service}' failed: {future.exception()}")

    def _spin_for(self, period: float) -> None:
        deadline = time.monotonic() + period
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                return
            self._executor.spin_once(timeout_sec=remaining)  # type: ignore[union-attr]

    def _require_started(self, what: str) -> None:
        if self._node is None:
            raise AnatomyError(f"{what}() before start() — the transport is not up")
