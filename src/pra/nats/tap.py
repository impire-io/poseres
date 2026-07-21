"""NatsTap (feature 014) — the off-process window that provably isn't there.

The tap binds the three injection seams the Engine already exposes (research
R1), all pure delegation:

1. ``world_factory()`` wraps each constructed world in a ``_TapWorld`` that
   forwards ``reset``/``step`` unchanged and mirrors plain copies — the
   per-step surface and the pause gate (R2).
2. ``bus_factory`` is the B1 viewer capture verbatim: keep the ``FrameStore``
   reference, return the stock ``InMemorySyncBus`` — the census derives from
   it on the publisher thread, never on the run path.
3. ``wrap_store()`` observes the engine's C4 snapshot writes: a notice joins
   the mirrored event family and pending control-plane snapshot requests are
   fulfilled with the new id (R5).

**The run-path budget is the contract** (FR-002/FR-003): per step, one
``Event.is_set`` check, two integer increments, one small array copy, one
bounded-deque append. No RNG, no float derivation, no locks, no network. The
daemon publisher thread does everything else — drain, serialize, publish,
census — and drops (derived from sequence gaps, never counted on the run
path) are the honesty meter when a consumer can't keep up.
"""

from __future__ import annotations

import copy
import threading
import time
from collections import deque
from collections.abc import Callable

import numpy as np

from pra.core.bus import InMemorySyncBus
from pra.core.scorer import WeightedSumScorer
from pra.nats import subjects
from pra.nats.transport import BusTransport
from pra.world.event_source import SensorimotorWorld

__all__ = ["NatsTap"]


class _TapWorld:
    """Delegating world: forwards everything, mirrors plain copies, holds the
    pause gate. ``__getattr__`` passthrough preserves every duck-typed contract
    the engine reads (``snapshot_needs_state``, ``state_dict``,
    ``apply_pending_tools``, ...)."""

    def __init__(self, inner, tap: NatsTap, stream: int):
        self._inner = inner
        self._tap = tap
        self._stream = stream
        self._episode = 0
        self._booted = False
        # Body self-description (feature 029): one getattr at construction —
        # metadata is per-run (one body definition), so stream 0 speaks for all.
        if stream == 0:
            meta = getattr(inner, "anatomy_meta", None)
            if callable(meta):
                tap._brain_meta_attach(meta())

    @property
    def n_actions(self) -> int:
        return self._inner.n_actions

    @property
    def obs_dim(self) -> int:
        return self._inner.obs_dim

    def reset(self):
        self._tap._gate()
        obs = self._inner.reset()
        self._episode += 1
        kind = "reset" if self._booted else "boot"
        self._booted = True
        self._tap._mirror_episode(self._stream, self._episode, kind, self._inner)
        return obs

    def step(self, action: int):
        self._tap._gate()
        obs = self._inner.step(action)
        self._tap._mirror_step(self._stream, self._episode, action, obs)
        return obs

    def __getattr__(self, name: str):
        return getattr(self._inner, name)


class _WorldViewAdapter:
    """The world's narration channel (feature 015, contracts §1): exactly the
    call surface `RoverTelemetry` defined, so a world built for the in-process
    viewer mounts on the bus unchanged. Run-path work is the tap's usual
    budget: plain copies into the bounded buffer, nothing else."""

    # kind → (reset field names, step field names); unknown kinds carry "args"
    _FIELDS = {"rover": (("x", "y", "theta"), ("x", "y", "theta", "bump"))}

    def __init__(self, tap: NatsTap, kind: str):
        self._tap = tap
        self.kind = kind
        self._episode = 0

    def attach_layout(self, layout) -> None:
        self._tap._view_attach(self.kind, layout)

    def record_reset(self, *args) -> None:
        self._episode += 1
        self._tap._view_record(self.kind, self._payload("reset", 0, args))

    def record_step(self, *args) -> None:
        self._tap._view_record(self.kind, self._payload("step", 1, args))

    def _payload(self, event: str, which: int, args: tuple) -> dict:
        payload: dict = {"event": event, "episode": self._episode}
        names = self._FIELDS.get(self.kind)
        if names is not None and len(names[which]) == len(args):
            for name, value in zip(names[which], args, strict=True):
                payload[name] = float(value) if isinstance(value, float) else value
        else:
            payload["args"] = list(args)
        return payload


class _TapBus:
    """Delegating Bus (feature 029): forwards delivery verbatim to the stock
    ``InMemorySyncBus`` and mirrors ``register``/``unregister`` as
    ``spawn``/``evict`` lifecycle events — the engine routes every population
    change through these two calls (boot, birth, decay eviction alike), so
    the mirror is complete without a single engine edit. Runs on the engine
    thread: the same single writer as the step mirror, so the tap's no-lock
    buffer discipline holds. Mirrors fire *after* the inner call — a rejected
    registration never fabricates an event."""

    def __init__(self, inner: InMemorySyncBus, tap: NatsTap):
        self._inner = inner
        self._tap = tap

    def register(self, frame_id: int) -> int:
        result = self._inner.register(frame_id)
        self._tap._mirror_lifecycle("spawn", frame_id)
        return result

    def unregister(self, frame_id: int) -> None:
        self._inner.unregister(frame_id)
        self._tap._mirror_lifecycle("evict", frame_id)

    def publish(self, event):
        return self._inner.publish(event)

    def subscribers(self) -> list[int]:
        return self._inner.subscribers()


class _TapStore:
    """Delegating SnapshotStore: forwards the four-method protocol unchanged
    and lets the tap observe each C4 write (engine.py's only store call)."""

    def __init__(self, inner, tap: NatsTap):
        self._inner = inner
        self._tap = tap

    def write(self, blob: bytes, metadata: dict) -> str:
        snapshot_id = self._inner.write(blob, metadata)
        self._tap._on_snapshot_written(snapshot_id, metadata)
        return snapshot_id

    def read(self, snapshot_id: str) -> bytes:
        return self._inner.read(snapshot_id)

    def list(self) -> list[tuple[str, dict]]:
        return self._inner.list()

    def delete(self, snapshot_id: str) -> None:
        return self._inner.delete(snapshot_id)


class NatsTap:
    """One live run's presence on the bus: telemetry out, control in."""

    def __init__(
        self,
        transport: BusTransport,
        run_id: str | None = None,
        *,
        buffer_size: int = 4096,
        drain_interval: float = 0.05,
        census_interval: float = 0.5,
        view_heartbeat: float = 5.0,
    ):
        self.run_id = (
            subjects.validate_run_id(run_id) if run_id is not None else subjects.default_run_id()
        )
        self.transport = transport
        self._buffer: deque = deque(maxlen=int(buffer_size))
        self._drain_interval = float(drain_interval)
        self._census_interval = float(census_interval)
        self._view_heartbeat = float(view_heartbeat)
        self._view_static_latest: tuple[str, dict] | None = None
        self._brain_meta_latest: dict | None = None

        # run-thread state (no locks by design — single writer)
        self._seq = 0
        self.steps = 0
        self.episodes = 0
        self._announced = False
        self._worlds_made = 0
        self._config = None  # captured at world construction, read-only
        self._store_wrapped = False

        # captured references (viewer discipline: read-only, off-path)
        self._store = None  # the live FrameStore
        self._scorer = None
        self._last_census: dict | None = None

        # pause gate: set = running (control writes, run thread reads)
        self._run_event = threading.Event()
        self._run_event.set()
        self._completed = False

        # snapshot observation (C4 writes) + control-plane waiters
        self._snapshot_lock = threading.Lock()
        self._snapshot_waiters: list[Callable[[str, dict], None]] = []
        self.last_snapshot: tuple[str, dict] | None = None

        # publisher thread; _last_drained starts at 0 (seq starts at 1) so
        # events evicted before the very first drain are still counted as drops
        self._stop = threading.Event()
        self._pump_thread: threading.Thread | None = None
        self._last_drained = 0

        # counters — outside the learning surface, FR-012
        self.events_mirrored = 0
        self.events_published = 0
        self.events_dropped = 0
        self.census_published = 0
        self.control_requests = 0
        self.control_errors = 0

    # -- the three seams -------------------------------------------------------
    def world_factory(self, inner: Callable = SensorimotorWorld) -> Callable:
        """An Engine-ready ``world_factory``: constructs ``inner(cfg, rng)`` and
        wraps it. Stream index is construction order (engine builds k=0..K−1)."""

        def factory(config, rng):
            self._config = config
            world = inner(config, rng)
            wrapped = _TapWorld(world, self, self._worlds_made)
            self._worlds_made += 1
            return wrapped

        return factory

    def bus_factory(self, processor):
        """Pass-through capture point (the B1 viewer pattern): keep the store
        reference, return the stock bus wrapped for the lifecycle mirror
        (feature 029) — delivery semantics untouched."""
        self._store = processor
        return _TapBus(InMemorySyncBus(processor), self)

    def wrap_store(self, inner):
        """Wrap an injected SnapshotStore so C4 writes are observed."""
        self._store_wrapped = True
        return _TapStore(inner, self)

    def world_view(self, kind: str):
        """A world-view adapter (feature 015): exposes the RoverTelemetry call
        surface (``attach_layout``/``record_reset``/``record_step``) and
        mirrors it onto the ``tele.view.*`` subjects through the existing
        buffer, pump, and drop machinery — absent unless a world speaks it."""
        return _WorldViewAdapter(self, str(kind))

    # -- lifecycle -------------------------------------------------------------
    def start(self) -> None:
        """Start the transport, the publisher thread, and the control listener."""
        self.transport.start()
        from pra.nats.control import ControlPlane  # local: avoid module cycle

        self._control = ControlPlane(self)
        self.transport.serve_requests(subjects.control_subject(self.run_id), self._control.handle)
        self.transport.serve_requests(subjects.DISCOVER_SUBJECT, self._control.handle_discover)
        self._pump_thread = threading.Thread(
            target=self._pump, daemon=True, name=f"pra-nats-tap-{self.run_id}"
        )
        self._pump_thread.start()

    def finish(self, summary) -> None:
        """Publish the canonical summary and stop the publisher (run is over)."""
        self._completed = True
        self._stop.set()
        if self._pump_thread is not None:
            self._pump_thread.join(timeout=10.0)
        payload = {
            "run": self.run_id,
            "seq": self._seq,
            "state": "completed",
            "summary": summary.canonical(),
        }
        self.transport.publish(subjects.status_subject(self.run_id), subjects.to_bytes(payload))
        with self._snapshot_lock:
            waiters, self._snapshot_waiters = self._snapshot_waiters, []
        for waiter in waiters:
            waiter("", {})  # completion beat the next boundary — control errors out

    # -- control surface (called by ControlPlane) ------------------------------
    @property
    def state(self) -> str:
        if self._completed:
            return "completed"
        return "paused" if not self._run_event.is_set() else "running"

    def pause(self) -> int:
        self._run_event.clear()
        return self.steps

    def resume(self) -> None:
        self._run_event.set()

    def snapshot_configured(self) -> bool:
        cfg = self._config
        cadence_on = cfg is not None and getattr(cfg, "snapshot_every_n_cycles", 0) > 0
        return self._store_wrapped and cadence_on

    def add_snapshot_waiter(self, waiter: Callable[[str, dict], None]) -> None:
        with self._snapshot_lock:
            self._snapshot_waiters.append(waiter)

    def census(self) -> dict | None:
        return self._last_census

    # -- run path (mirror only; the budget documented in the module header) ----
    def _gate(self) -> None:
        if not self._run_event.is_set():
            self._run_event.wait()

    def _mirror_step(self, stream: int, episode: int, action: int, obs) -> None:
        self._seq += 1
        self.steps += 1
        self.events_mirrored += 1
        self._buffer.append(
            ("step", self._seq, stream, episode, self.steps, int(action), np.array(obs, copy=True))
        )

    def _mirror_episode(self, stream: int, episode: int, kind: str, inner_world) -> None:
        if not self._announced:
            self._announced = True
            self._seq += 1
            self._buffer.append(
                ("started", self._seq, int(inner_world.obs_dim), int(inner_world.n_actions))
            )
        self._seq += 1
        self.episodes += 1
        self.events_mirrored += 1
        self._buffer.append(("episode", self._seq, stream, episode, kind))

    def _view_attach(self, kind: str, layout) -> None:
        # run thread (world construction): one deep copy, then heartbeat reuse
        static = copy.deepcopy(layout)
        self._view_static_latest = (kind, static)
        self._seq += 1
        self.events_mirrored += 1
        self._buffer.append(("view_static", self._seq, kind, static))

    def _view_record(self, kind: str, payload: dict) -> None:
        self._seq += 1
        self.events_mirrored += 1
        self._buffer.append(("view_live", self._seq, kind, payload))

    def _mirror_lifecycle(self, event: str, frame_id: int) -> None:
        # engine thread (offline cycle / boot): counters + one deque append
        self._seq += 1
        self.events_mirrored += 1
        self._buffer.append(("brain_event", self._seq, event, int(frame_id), self.steps))

    def _brain_meta_attach(self, meta: dict) -> None:
        # run thread (world construction): one deep copy, then heartbeat reuse
        static = copy.deepcopy(meta)
        self._brain_meta_latest = static
        self._seq += 1
        self.events_mirrored += 1
        self._buffer.append(("brain_meta", self._seq, static))

    def _on_snapshot_written(self, snapshot_id: str, metadata: dict) -> None:
        # engine thread, C4: plain copies + the pending-request handoff
        self._seq += 1
        meta = {
            "step": int(metadata["step"]),
            "cycle": int(metadata["cycle"]),
            "population": int(metadata["population"]),
            "format_version": metadata["format_version"],
        }
        self.last_snapshot = (snapshot_id, meta)
        self._buffer.append(("snapshot", self._seq, snapshot_id, meta))
        with self._snapshot_lock:
            waiters, self._snapshot_waiters = self._snapshot_waiters, []
        for waiter in waiters:
            waiter(snapshot_id, meta)

    # -- publisher thread ------------------------------------------------------
    def _pump(self) -> None:
        next_census = time.monotonic() + self._census_interval
        next_view = time.monotonic() + self._view_heartbeat
        while not self._stop.wait(self._drain_interval):
            self._drain()
            if time.monotonic() >= next_census:
                self._publish_census()
                next_census = time.monotonic() + self._census_interval
            if time.monotonic() >= next_view:
                self._republish_view_static()
                self._republish_brain_meta()
                next_view = time.monotonic() + self._view_heartbeat
        self._drain()  # final: everything still buffered goes out

    def _republish_view_static(self) -> None:
        # heartbeat so late-attaching dashboards catch the layout (015 R2);
        # publisher-side reading, census-style seq snapshot
        latest = self._view_static_latest
        if latest is None:
            return
        kind, static = latest
        payload = {"run": self.run_id, "seq": self._seq, "kind": kind, "static": static}
        self.transport.publish(
            subjects.view_static_subject(self.run_id), subjects.to_bytes(payload)
        )

    def _republish_brain_meta(self) -> None:
        # same late-attach guarantee as the view static (contract §2.2)
        latest = self._brain_meta_latest
        if latest is None:
            return
        payload = {"run": self.run_id, "seq": self._seq, **latest}
        self.transport.publish(
            subjects.brain_anatomy_subject(self.run_id), subjects.to_bytes(payload)
        )

    def _drain(self) -> None:
        run = self.run_id
        while True:
            try:
                item = self._buffer.popleft()
            except IndexError:
                return
            seq = item[1]
            if seq > self._last_drained + 1:
                self.events_dropped += seq - self._last_drained - 1
            self._last_drained = seq
            kind = item[0]
            if kind == "step":
                _, _, stream, episode, step, action, obs = item
                payload = {
                    "run": run,
                    "seq": seq,
                    "stream": stream,
                    "episode": episode,
                    "step": step,
                    "action": action,
                    "obs": [float(x) for x in obs],
                }
                subject = subjects.step_subject(run)
            elif kind == "episode":
                _, _, stream, episode, ep_kind = item
                payload = {
                    "run": run,
                    "seq": seq,
                    "stream": stream,
                    "episode": episode,
                    "kind": ep_kind,
                }
                subject = subjects.episode_subject(run)
            elif kind == "snapshot":
                _, _, snapshot_id, meta = item
                payload = {"run": run, "seq": seq, "snapshot_id": snapshot_id, **meta}
                subject = subjects.snapshot_subject(run)
            elif kind == "view_static":
                _, _, view_kind, static = item
                payload = {"run": run, "seq": seq, "kind": view_kind, "static": static}
                subject = subjects.view_static_subject(run)
            elif kind == "view_live":
                _, _, view_kind, live = item
                payload = {"run": run, "seq": seq, "kind": view_kind, **live}
                subject = subjects.view_live_subject(run)
            elif kind == "brain_meta":
                _, _, static = item
                payload = {"run": run, "seq": seq, **static}
                subject = subjects.brain_anatomy_subject(run)
            elif kind == "brain_event":
                _, _, event, frame_id, steps = item
                payload = {
                    "run": run,
                    "seq": seq,
                    "event": event,
                    "frame": frame_id,
                    "steps": steps,
                }
                subject = subjects.brain_events_subject(run)
            else:  # "started"
                _, _, obs_dim, n_actions = item
                cfg = self._config
                payload = {
                    "run": run,
                    "seq": seq,
                    "state": "started",
                    "obs_dim": obs_dim,
                    "n_actions": n_actions,
                    "n_streams": int(getattr(cfg, "n_streams", 1)),
                    "episode_mode": str(getattr(cfg, "episode_mode", "episodic")),
                }
                subject = subjects.status_subject(run)
            self.transport.publish(subject, subjects.to_bytes(payload))
            self.events_published += 1

    def _publish_census(self) -> None:
        store, cfg = self._store, self._config
        if store is None or cfg is None:
            return
        try:
            states = store.frame_states()
            if not states:
                return
            if self._scorer is None:
                self._scorer = WeightedSumScorer(cfg)
            dims: dict[int, int] = {}
            best: tuple[float, int, int, float] | None = None
            rows: list[dict] = []  # feature 029: the same walk, kept per frame
            for s in states:
                dims[s.dim] = dims.get(s.dim, 0) + 1
                score = float(
                    self._scorer.combine(s.recon_err_ema, s.pred_err_ema, s.effort_ema, s.dim)
                )
                rows.append(
                    {
                        "id": s.frame_id,
                        "dim": s.dim,
                        "age": s.age_cycles,
                        "cand": s.is_candidate,
                        "recon": s.recon_err_ema,
                        "pred": s.pred_err_ema,
                        "effort": s.effort_ema,
                        "score": score,
                    }
                )
                # ties by ascending frame_id — the store's own rule (PRA-01 §7.1)
                if best is None or (score, s.frame_id) < (best[0], best[1]):
                    best = (score, s.frame_id, s.dim, s.pred_err_ema)
        except Exception:  # torn read mid-scan — one stale census, no harm
            return
        assert best is not None
        payload = {
            "run": self.run_id,
            "seq": self._seq,
            "population": len(states),
            "dims": {str(d): dims[d] for d in sorted(dims)},
            "best_dim": best[2],
            "best_score": best[0],
            "pred_err_ema": best[3],
            "steps": self.steps,
            "episodes": self.episodes,
        }
        self._last_census = payload
        self.transport.publish(subjects.census_subject(self.run_id), subjects.to_bytes(payload))
        self.census_published += 1
        # feature 029: the rows the aggregate came from — complete (bounded by
        # max_frames), same walk, so population/best_frame agree by construction
        frames_payload = {
            "run": self.run_id,
            "seq": payload["seq"],
            "steps": payload["steps"],
            "population": len(rows),
            "best_frame": best[1],
            "rows": rows,
        }
        self.transport.publish(
            subjects.brain_frames_subject(self.run_id), subjects.to_bytes(frames_payload)
        )
