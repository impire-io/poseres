"""FakeTransport: the scripted, journaling transport (feature 013, research R1/R6).

This is the adapter's instrument, and it ships in the package deliberately:
it is how the entire contract suite runs on machines where ROS2 cannot be
installed (FR-008), and how a user dry-runs an anatomy declaration before
pointing it at a robot (quickstart §1).

Script: ``{topic: {tick_index: [payload, ...]}}`` — payloads are delivered,
in order, to that topic's subscribers during that tick. Payloads are
message-shaped objects (or plain arrays, for whole-payload specs); the same
:func:`~pra.anatomy.ros2.specs.extract_vector` path runs as on the real
transport. Only subscribed topics deliver — a script may carry topics nobody
senses, exactly like a real ROS graph.

Journal: an ordered list of events —``("start",)``, ``("subscribe", topic)``,
``("publish", topic, preset_dict)``, ``("tick", k)``, ``("deliver", topic)``,
``("reset",)``, ``("close",)`` — the evidence the tick-ordering contract
(C2.3) is asserted against.

Honesty guards, always on: a second ``start()`` raises (the feature-008
single-boot contract — a regression re-homing a robot must fail on the
transport's own honesty); ``publish``/``tick`` before ``start()`` raise; a
declared-but-failing reset mechanism is scripted with ``fail_reset=True``.
"""

from __future__ import annotations

from collections.abc import Callable

from pra.anatomy.body import AnatomyError
from pra.anatomy.ros2.specs import ActuatorSpec, SensorSpec

__all__ = ["FakeTransport"]


class FakeTransport:
    """Scripted transport with an event journal (see module doc)."""

    def __init__(
        self,
        script: dict[str, dict[int, list]] | None = None,
        *,
        resettable: bool = False,
        fail_reset: bool = False,
    ):
        self._script: dict[str, dict[int, list]] = {
            topic: {int(k): list(payloads) for k, payloads in by_tick.items()}
            for topic, by_tick in (script or {}).items()
        }
        self._resettable = bool(resettable)
        self._fail_reset = bool(fail_reset)
        self._subscribers: dict[str, list[Callable[[object], None]]] = {}
        self._started = False
        self._closed = False
        self._ticks_run = 0
        self.journal: list[tuple] = []

    # ---- Transport surface ----------------------------------------------------
    def start(self) -> None:
        if self._started:
            raise AnatomyError(
                "transport already started — a ROS2 world boots exactly once "
                "(the feature-008 single-boot contract)"
            )
        self._started = True
        self.journal.append(("start",))

    def subscribe(self, spec: SensorSpec, deliver: Callable[[object], None]) -> None:
        self._subscribers.setdefault(spec.topic, []).append(deliver)
        self.journal.append(("subscribe", spec.topic))

    def publish(self, spec: ActuatorSpec, preset_index: int) -> None:
        self._require_started("publish")
        self.journal.append(("publish", spec.topic, dict(spec.presets[preset_index])))

    def tick(self) -> None:
        self._require_started("tick")
        k = self._ticks_run
        self.journal.append(("tick", k))
        for topic, deliverers in self._subscribers.items():
            for payload in self._script.get(topic, {}).get(k, []):
                for deliver in deliverers:
                    deliver(payload)
                self.journal.append(("deliver", topic))
        self._ticks_run += 1

    @property
    def can_reset(self) -> bool:
        return self._resettable

    def reset_world(self) -> None:
        if not self._resettable:
            raise AnatomyError(
                "this transport declares no reset mechanism — run episode_mode='continuous'"
            )
        if self._fail_reset:
            raise AnatomyError("reset mechanism failed (scripted failure: reset_world)")
        self._ticks_run = 0  # the world restarts its script
        self.journal.append(("reset",))

    @property
    def overruns(self) -> int:
        return 0  # the fake never misses a deadline — there is none

    def close(self) -> None:
        if not self._closed:
            self._closed = True
            self.journal.append(("close",))

    # ---- test conveniences ------------------------------------------------------
    @property
    def ticks_run(self) -> int:
        return self._ticks_run

    def _require_started(self, what: str) -> None:
        if not self._started:
            raise AnatomyError(f"{what}() before start() — the transport is not up")
