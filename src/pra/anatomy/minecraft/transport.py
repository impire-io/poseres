"""MinecraftTransport: the feature-013 Transport surface over a pra-mc/1 bridge.

The adapter is a *transport*, not a body (research R1): `Ros2Body`
mounts unchanged over this class, inheriting the control-tick step
semantics, hold-last-value staleness, the startup gate, and telemetry.
One engine step is: queued command presets → one ``tick`` round-trip
(the bridge holds the controls for ``tick_ms`` and samples the world) →
every subscribed channel's vector delivered.

Honesty guards: `hello` validates the protocol version and every
subscribed channel's width at start (never a shape error mid-run,
FR-002); the bridge's tick index must advance by exactly one per
round-trip (a silently restarted or desynced bridge fails the run
loudly, FR-004); a lost connection is an :class:`AnatomyError` at the
next operation — the recovery path is resume-from-snapshot, stated in
the runbook. A wall-clock budget per tick feeds ``overruns`` (the
free-running honesty meter, 013 research R2); against the live server
this mode is Doc 06 §5b **class 4, openly non-reproducible** — against
the in-repo FakeBridge everything is deterministic and the state seam
round-trips the full world (class 1, gate-proven).
"""

from __future__ import annotations

import socket
import time

import numpy as np

from pra.anatomy.body import AnatomyError
from pra.anatomy.minecraft.protocol import PROTOCOL_VERSION, request
from pra.anatomy.ros2.specs import ActuatorSpec, SensorSpec

__all__ = ["MinecraftTransport"]


class MinecraftTransport:
    """The delivery boundary to a pra-mc/1 bridge (see module doc)."""

    def __init__(
        self,
        host: str = "127.0.0.1",
        port: int = 25580,
        *,
        tick_ms: int = 250,
        tick_budget: float | None = None,
        connect_timeout: float = 10.0,
    ):
        if int(tick_ms) < 1:
            raise AnatomyError("tick_ms must be >= 1")
        if float(connect_timeout) <= 0:
            raise AnatomyError("connect_timeout must be > 0")
        self._host = host
        self._port = int(port)
        self._tick_ms = int(tick_ms)
        self._tick_budget = float(tick_budget) if tick_budget else self._tick_ms / 1000.0 * 1.5
        self._connect_timeout = float(connect_timeout)
        self._sock: socket.socket | None = None
        self._rfile = None
        self._channels: dict[str, int] = {}
        self._subscribers: list[tuple[SensorSpec, object]] = []
        self._queued: list[dict] = []
        self._pending_state: dict | None = None
        self._last_tick: int | None = None
        self._overruns = 0
        self._closed = False

    # ---- Transport surface ----------------------------------------------------
    def start(self) -> None:
        if self._sock is not None:
            raise AnatomyError(
                "transport already started — a live world boots exactly once "
                "(the feature-008 single-boot contract)"
            )
        deadline = time.monotonic() + self._connect_timeout
        while True:
            try:
                self._sock = socket.create_connection(
                    (self._host, self._port), timeout=self._connect_timeout
                )
                break
            except OSError as exc:
                if time.monotonic() >= deadline:
                    raise AnatomyError(
                        f"no bridge at {self._host}:{self._port} after "
                        f"{self._connect_timeout}s — is the bridge running? "
                        "(examples/minecraft/README.md)"
                    ) from exc
                time.sleep(0.2)
        try:
            self._sock.settimeout(max(self._connect_timeout, self._tick_budget * 10))
            self._rfile = self._sock.makefile("rb")
            hello = request(self._sock, self._rfile, {"op": "hello", "version": PROTOCOL_VERSION})
            if hello.get("version") != PROTOCOL_VERSION:
                raise AnatomyError(
                    f"protocol version mismatch: bridge speaks {hello.get('version')!r}, "
                    f"this adapter {PROTOCOL_VERSION}"
                )
            if not hello.get("spawn", False):
                raise AnatomyError("bridge answered hello before its bot spawned — bridge bug")
            channels = hello.get("channels")
            if not isinstance(channels, dict) or not channels:
                raise AnatomyError("bridge hello carried no channel table")
            self._channels = {str(k): int(v) for k, v in channels.items()}
            for spec, _deliver in self._subscribers:
                self._check_channel(spec)
            if self._pending_state is not None:
                request(
                    self._sock,
                    self._rfile,
                    {"op": "load_state", "world": self._pending_state},
                )
                self._pending_state = None
                self._last_tick = None
        except BaseException:
            # a failed boot must not leak the socket (loud AND clean)
            if self._rfile is not None:
                self._rfile.close()
            self._sock.close()
            self._sock = None
            self._rfile = None
            raise

    def subscribe(self, spec: SensorSpec, deliver) -> None:
        if self._sock is not None:
            self._check_channel(spec)
        self._subscribers.append((spec, deliver))

    def publish(self, spec: ActuatorSpec, preset_index: int) -> None:
        self._ensure_started()
        self._queued.append({k: float(v) for k, v in spec.presets[preset_index].items()})

    def tick(self) -> None:
        self._ensure_started()
        commands, self._queued = self._queued, []
        started = time.monotonic()
        response = request(
            self._sock,
            self._rfile,
            {"op": "tick", "commands": commands, "tick_ms": self._tick_ms},
        )
        if time.monotonic() - started > self._tick_budget:
            self._overruns += 1
        tick_index = int(response.get("tick", -1))
        if self._last_tick is not None and tick_index != self._last_tick + 1:
            raise AnatomyError(
                f"bridge tick index jumped {self._last_tick} -> {tick_index} — "
                "the bridge restarted or desynced; restart it and resume from the "
                "latest snapshot"
            )
        self._last_tick = tick_index
        channels = response.get("channels")
        if not isinstance(channels, dict):
            raise AnatomyError("bridge tick response carried no channels")
        for spec, deliver in self._subscribers:
            if spec.topic not in channels:
                raise AnatomyError(
                    f"bridge tick response is missing channel '{spec.topic}' (sensor '{spec.id}')"
                )
            deliver(np.asarray(channels[spec.topic], dtype=np.float64))

    @property
    def can_reset(self) -> bool:
        return False  # a live world does not restart (research R5)

    def reset_world(self) -> None:
        raise AnatomyError(
            "a Minecraft world cannot reset mid-run — run episode_mode='continuous' "
            "(single boot, virtual episodes; feature 008)"
        )

    @property
    def overruns(self) -> int:
        return self._overruns

    def close(self) -> None:
        if self._closed:
            return
        self._closed = True
        if self._sock is not None:
            try:
                request(self._sock, self._rfile, {"op": "bye"})
            except Exception:
                pass  # goodbye is best-effort; the socket closes either way
            self._rfile.close()
            self._sock.close()

    # ---- the state seam (feature 008/010 world capture) --------------------------
    def state_dict(self) -> dict:
        self._ensure_started()
        return dict(request(self._sock, self._rfile, {"op": "state"})["world"])

    def load_state_dict(self, state: dict) -> None:
        # The engine restores world state before the world's first reset()
        # (the resume path); a live world applies it at boot, right after the
        # handshake — buffered here, sent in start().
        if self._sock is None:
            self._pending_state = dict(state)
            return
        request(self._sock, self._rfile, {"op": "load_state", "world": dict(state)})
        self._last_tick = None  # adopt the bridge's next index; the guard re-arms after

    # ---- internals ---------------------------------------------------------------
    def _ensure_started(self) -> None:
        # A resumed continuous run never calls reset() (the restored pending
        # observation supersedes it, feature 008), so the transport boots at
        # first use — applying any buffered restored world state. Safe here
        # because pra-mc delivers every channel every tick: the first composed
        # read after a lazy boot is never stale. Fresh runs still boot through
        # Ros2Body.reset()/start(), and an explicit double start() stays loud.
        if self._sock is None:
            self.start()

    def _check_channel(self, spec: SensorSpec) -> None:
        if spec.topic not in self._channels:
            raise AnatomyError(
                f"sensor '{spec.id}': bridge declares no channel '{spec.topic}' "
                f"(it has: {', '.join(sorted(self._channels))})"
            )
        if self._channels[spec.topic] != spec.width:
            raise AnatomyError(
                f"sensor '{spec.id}': channel '{spec.topic}' is width "
                f"{self._channels[spec.topic]}, the spec declares {spec.width}"
            )

    def _require_started(self, what: str) -> None:
        if self._sock is None:
            raise AnatomyError(f"{what}() before start() — the transport is not up")
