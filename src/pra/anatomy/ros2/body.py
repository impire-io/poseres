"""The ROS2 body: per-topic tools, the control tick, the staleness policy (feature 013).

A robot is N independent message streams, so each topic is a first-class
Doc 02 tool (research R1): :class:`TopicSensor` caches the latest message
and answers for silent ticks (hold-last-value, counted — research R3);
:class:`CommandActuator` publishes preset *i* for local action *i* and
nothing else (Doc 02 §4.2). :class:`Ros2Body` owns the feature's named
semantics — one engine step is publish → advance exactly one control tick →
sample every cache (research R2) — and the startup gate that keeps the brain
from ever observing an invented placeholder.

All telemetry (ticks, overruns, per-sensor staleness, publish counts) lives
on the adapter objects, outside the learning surface: the engine only ever
sees observation vectors.
"""

from __future__ import annotations

import numpy as np

from pra.anatomy.body import AnatomyError, Body
from pra.anatomy.ros2.specs import ActuatorSpec, SensorSpec, extract_vector

__all__ = ["CommandActuator", "Ros2Body", "TopicSensor"]


class TopicSensor:
    """A declared (topic, width) subscription with a latest-message cache.

    Doc 02 ``Sensor``. Staleness accounting happens at sample time (``read``
    is called once per composed observation): no fresh delivery since the
    previous sample → the cached value stands, the staleness counters
    advance, and a streak crossing ``stale_limit_ticks`` fails the run loudly
    — the brain never learns from a frozen ghost (research R3). Reading
    before the first message is a contract error, same as ``WorldSensor``;
    the body's startup gate exists so the engine never encounters it.
    """

    def __init__(self, spec: SensorSpec, *, stale_limit_ticks: int = 50):
        if not isinstance(spec, SensorSpec):
            raise AnatomyError(f"TopicSensor needs a SensorSpec, got {type(spec).__name__}")
        if int(stale_limit_ticks) < 1:
            raise AnatomyError(f"sensor '{spec.id}': stale_limit_ticks must be >= 1")
        self.spec = spec
        self._stale_limit = int(stale_limit_ticks)
        self._cache: np.ndarray | None = None
        self._seq = 0  # deliveries so far
        self._seen_seq = 0  # deliveries as of the previous sample
        self.deliveries = 0
        self.overwritten = 0  # deliveries beyond the first between two samples
        self.staleness_total = 0
        self.staleness_streak = 0

    # ---- Doc 02 Sensor surface --------------------------------------------------
    def id(self) -> str:
        return self.spec.id

    def width(self) -> int:
        return self.spec.width

    def labels(self) -> tuple[str, ...] | None:
        return self.spec.labels  # per-channel names for telemetry (feature 033)

    def read(self) -> np.ndarray:
        if self._cache is None:
            raise AnatomyError(
                f"sensor '{self.spec.id}' on topic '{self.spec.topic}' read before "
                "its first message"
            )
        fresh = self._seq - self._seen_seq
        if fresh == 0:
            self.staleness_total += 1
            self.staleness_streak += 1
            if self.staleness_streak > self._stale_limit:
                raise AnatomyError(
                    f"sensor '{self.spec.id}' on topic '{self.spec.topic}' has been "
                    f"silent for {self.staleness_streak} consecutive samples "
                    f"(stale_limit_ticks={self._stale_limit})"
                )
        else:
            self.overwritten += fresh - 1
            self.staleness_streak = 0
            self._seen_seq = self._seq
        return self._cache

    # ---- transport delivery -------------------------------------------------------
    def deliver(self, msg: object) -> None:
        """Extract, width-check (loud), cache. Called by the transport only."""
        self._cache = extract_vector(msg, self.spec)
        self._seq += 1
        self.deliveries += 1

    @property
    def has_message(self) -> bool:
        return self._cache is not None


class CommandActuator:
    """A declared (topic, presets) publication. Doc 02 ``Actuator``.

    ``apply(i)`` publishes exactly preset *i* and returns nothing — the only
    feedback path is subsequent observations. It does **not** advance the
    tick: the tick belongs to the body (research R1), so the one-tick-per-step
    invariant holds no matter which actuator an action routes to.
    """

    def __init__(self, spec: ActuatorSpec, transport):
        if not isinstance(spec, ActuatorSpec):
            raise AnatomyError(f"CommandActuator needs an ActuatorSpec, got {type(spec).__name__}")
        self.spec = spec
        self._transport = transport
        self.published = 0

    def id(self) -> str:
        return self.spec.id

    def action_count(self) -> int:
        return len(self.spec.presets)

    def action_labels(self) -> list[str]:
        """Human names for telemetry (feature 029): preset keys in declared
        order, ``+``-joined; the all-defaults command is ``idle``."""
        return ["+".join(p) if p else "idle" for p in self.spec.presets]

    def apply(self, local_action_index: int) -> None:
        self._transport.publish(self.spec, local_action_index)
        self.published += 1


class Ros2Body(Body):
    """A Doc 02 body over a transport, with the control-tick step semantics.

    ``reset()``: first call boots the transport (exactly once — continuous
    mode never comes back here); later calls demand a declared reset
    mechanism and are loud without one. Either way the startup gate follows:
    tick (without publishing) until every topic sensor has its first message,
    bounded by ``startup_timeout_ticks`` — expiry names the silent topics.

    ``step(a)``: route → publish → **one** ``transport.tick()`` → compose.
    The ordering is the feature's named decision (research R2) and is
    asserted against the fake transport's journal, not assumed.
    """

    def __init__(
        self,
        sensors: list[SensorSpec],
        actuators: list[ActuatorSpec],
        transport,
        *,
        startup_timeout_ticks: int = 100,
        stale_limit_ticks: int = 50,
    ):
        if int(startup_timeout_ticks) < 1:
            raise AnatomyError("startup_timeout_ticks must be >= 1")
        topic_sensors = [TopicSensor(s, stale_limit_ticks=stale_limit_ticks) for s in sensors]
        command_actuators = [CommandActuator(a, transport) for a in actuators]
        super().__init__(transport, sensors=topic_sensors, actuators=command_actuators)
        self._transport = transport
        self._stale_limit = int(stale_limit_ticks)
        self._startup_timeout = int(startup_timeout_ticks)
        self._booted = False
        self.ticks = 0
        for sensor in topic_sensors:
            transport.subscribe(sensor.spec, sensor.deliver)

    # ---- EventSource surface --------------------------------------------------
    def reset(self) -> np.ndarray:
        if not self._booted:
            self._transport.start()
            self._booted = True
        else:
            if not self._transport.can_reset:
                raise AnatomyError(
                    "this world cannot reset mid-run (no reset mechanism declared) — "
                    "run episode_mode='continuous' (single boot, virtual episodes; "
                    "feature 008)"
                )
            self._transport.reset_world()
        self._startup_gate()
        return self._compose()

    def step(self, action: int) -> np.ndarray:
        actuator, local = self.route(action)
        actuator.apply(local)  # publish (only CommandActuators publish)
        self._transport.tick()  # advance exactly one control tick
        self.ticks += 1
        return self._compose()  # sample every cache

    # ---- the startup gate (research R3) ------------------------------------------
    def _startup_gate(self) -> None:
        for _ in range(self._startup_timeout):
            if not self._silent_topics():
                return
            self._transport.tick()
            self.ticks += 1
        silent = self._silent_topics()
        if silent:
            raise AnatomyError(
                f"startup gate expired after {self._startup_timeout} tick(s); "
                f"no message yet on: {', '.join(silent)}"
            )

    def _silent_topics(self) -> list[str]:
        return [s.spec.topic for s in self._topic_sensors() if not s.has_message]

    def _topic_sensors(self) -> list[TopicSensor]:
        return [s for s in self._sensors if isinstance(s, TopicSensor)]

    # ---- growing the anatomy (Doc 02 §5, through the existing queue) --------------
    def register_topic_sensor(self, spec: SensorSpec) -> str:
        """Declare-and-subscribe a new topic sensor; applied at the slow loop.

        The subscription starts immediately so the cache warms while the
        registration is pending — by the boundary the sensor normally has
        data; if the topic stays silent, the first composed read is loud
        (the same read-before-first contract as everywhere).
        """
        sensor = TopicSensor(spec, stale_limit_ticks=self._stale_limit)
        self._transport.subscribe(spec, sensor.deliver)
        return self.register_sensor(sensor)

    def register_command_actuator(self, spec: ActuatorSpec) -> str:
        """Declare a new command actuator; applied at the slow loop."""
        return self.register_actuator(CommandActuator(spec, self._transport))

    # ---- outside the learning surface ----------------------------------------------
    def telemetry(self) -> dict:
        """Ticks, overruns, per-sensor and per-actuator counters (never observed)."""
        return {
            "ticks": self.ticks,
            "overruns": int(self._transport.overruns),
            "sensors": {
                s.id(): {
                    "deliveries": s.deliveries,
                    "overwritten": s.overwritten,
                    "staleness_total": s.staleness_total,
                    "staleness_streak": s.staleness_streak,
                }
                for s in self._topic_sensors()
            },
            "actuators": {
                a.id(): {"published": a.published}
                for a in self._actuators
                if isinstance(a, CommandActuator)
            },
        }

    def close(self) -> None:
        self._transport.close()

    # ---- Engine-ready mounting (the 007 factory pattern) ----------------------------
    @classmethod
    def factory(
        cls,
        sensors: list[SensorSpec],
        actuators: list[ActuatorSpec],
        *,
        transport,
        startup_timeout_ticks: int = 100,
        stale_limit_ticks: int = 50,
    ):
        """An Engine-ready ``world_factory(cfg, rng)``.

        ``transport`` is a Transport instance (single-run convenience) or a
        zero-argument callable returning one (fresh transport per run — what
        repeated runs need, since a transport boots once). Mount time
        validates the config's sizes against the declared anatomy and the
        episode-mode/reset-capability pairing, and names what is wrong —
        never a shape error deep inside a run. The engine's generator is
        accepted per the seam's signature and never read or drawn from
        (research R4).
        """

        def world_factory(cfg, rng: np.random.Generator) -> Ros2Body:
            mounted = transport() if callable(transport) else transport
            body = cls(
                sensors,
                actuators,
                mounted,
                startup_timeout_ticks=startup_timeout_ticks,
                stale_limit_ticks=stale_limit_ticks,
            )
            if (cfg.obs_dim, cfg.n_actions) != (body.obs_dim, body.n_actions):
                raise AnatomyError(
                    f"config/anatomy mismatch: config declares obs_dim={cfg.obs_dim}, "
                    f"n_actions={cfg.n_actions} but the declared anatomy provides "
                    f"obs_dim={body.obs_dim}, n_actions={body.n_actions} — "
                    "set Config(obs_dim=..., n_actions=...) to match"
                )
            if cfg.episode_mode == "episodic" and not mounted.can_reset:
                raise AnatomyError(
                    "episode_mode='episodic' needs a transport with a reset mechanism "
                    "(can_reset), and this one declares none — run "
                    "episode_mode='continuous' (single boot, virtual episodes; "
                    "feature 008)"
                )
            return body

        return world_factory
