"""The dashboard's consumer model (feature 015, contracts §2; research R3).

``DashboardModel`` is a pure consumer of the documented B6 surface: it
subscribes ``pra.v1.>`` on the existing transport seam, sweeps discovery at
start and on a slow interval, and materializes one :class:`RunModel` per run
**from received payloads only** — the run is the authority, the model never
invents. Honesty is structural: liveness is the monotonic age of the last
received message (the dashboard's own requests never reset it), sequence
gaps are counted and rendered rather than repaired, malformed wire data
increments ``wire_errors`` and is skipped, and a completed run is terminal.

An optional slow inspect loop (read-only, the control plane's own
answers-in-every-state contract) refreshes authoritative state and the tap's
honesty counters for runs that are quiet between censuses.

Payload handlers run on the transport's delivery thread; every mutation sits
under one lock, and endpoint reads take snapshots under the same lock.
"""

from __future__ import annotations

import threading
import time
from collections import deque

from pra.nats import subjects
from pra.nats.transport import BusTransport, TransportError

__all__ = ["DashboardModel", "RunModel"]

CENSUS_HISTORY = 512
SNAPSHOT_NOTICES = 64


class RunModel:
    """One run's picture, built from received payloads only."""

    def __init__(self, run_id: str):
        self.run_id = run_id
        self.state = "unknown"
        self.anatomy: dict | None = None
        self.completed_summary: dict | None = None
        self.last_seen: float | None = None  # monotonic stamp
        self.latest_census: dict | None = None
        self.census_history: deque = deque(maxlen=CENSUS_HISTORY)
        self.snapshots: deque = deque(maxlen=SNAPSHOT_NOTICES)
        self.counters: dict | None = None  # from inspect replies
        self.view_kind: str | None = None
        self.view_static: dict | None = None
        self.view_live: dict | None = None
        self.last_step = 0
        self.last_mirror_seq = 0
        self.seq_gaps = 0
        self.wire_errors = 0

    def age_seconds(self) -> float | None:
        if self.last_seen is None:
            return None
        return time.monotonic() - self.last_seen

    def summary_row(self) -> dict:
        return {
            "run": self.run_id,
            "state": self.state,
            "age_seconds": self.age_seconds(),
            "has_view": self.view_kind is not None,
        }

    def state_payload(self) -> dict:
        view = None
        if self.view_kind is not None:
            view = {"kind": self.view_kind, "static": self.view_static, "live": self.view_live}
        return {
            "run": self.run_id,
            "state": self.state,
            "age_seconds": self.age_seconds(),
            "anatomy": self.anatomy,
            "census": self.latest_census,
            "census_history": list(self.census_history),
            "counters": self.counters,
            "snapshots": list(self.snapshots),
            "view": view,
            "last_step": self.last_step,
            "seq_gaps": self.seq_gaps,
            "wire_errors": self.wire_errors,
            "completed_summary": self.completed_summary,
        }


class DashboardModel:
    """All known runs, one subscription, one discovery sweep."""

    def __init__(
        self,
        transport: BusTransport,
        *,
        discover_interval: float = 10.0,
        inspect_interval: float = 2.0,
    ):
        self.transport = transport
        self._lock = threading.Lock()
        self._runs: dict[str, RunModel] = {}
        self._discover_interval = float(discover_interval)
        self._inspect_interval = float(inspect_interval)
        self._stop = threading.Event()
        self._loop_thread: threading.Thread | None = None

    # -- lifecycle -------------------------------------------------------------
    def start(self) -> None:
        self.transport.start()
        self.transport.subscribe("pra.v1.>", self._on_message)
        self._discover_once()
        self._loop_thread = threading.Thread(
            target=self._slow_loop, daemon=True, name="pra-dash-model"
        )
        self._loop_thread.start()

    def stop(self) -> None:
        self._stop.set()
        if self._loop_thread is not None:
            self._loop_thread.join(timeout=5.0)

    # -- reads (endpoint surface) ----------------------------------------------
    def runs_summary(self) -> dict:
        with self._lock:
            rows = [self._runs[r].summary_row() for r in sorted(self._runs)]
        return {"runs": rows}

    def state_of(self, run_id: str) -> dict | None:
        with self._lock:
            run = self._runs.get(run_id)
            return None if run is None else run.state_payload()

    def known(self, run_id: str) -> bool:
        with self._lock:
            return run_id in self._runs

    # -- control forwarding (verbatim; contracts §3.2) ---------------------------
    def control(self, run_id: str, request: dict) -> dict:
        timeout = 60.0 if request.get("cmd") == "snapshot" else 5.0
        try:
            reply = self.transport.request(
                subjects.control_subject(run_id), subjects.to_bytes(request), timeout
            )
            parsed = subjects.from_bytes(reply)
        except (TransportError, ValueError) as err:
            return {"ok": False, "error": f"control request failed: {err}"}
        with self._lock:
            run = self._runs.get(run_id)
            if run is not None and parsed.get("ok"):
                state = parsed.get("state")
                if state in ("running", "paused") and run.state != "completed":
                    run.state = state
                if request.get("cmd") == "inspect":
                    run.counters = parsed.get("counters")
                    if parsed.get("state") in ("running", "paused", "completed"):
                        run.state = parsed["state"]
        return parsed

    # -- the wire (delivery thread; contracts §2) ---------------------------------
    def _on_message(self, subject: str, payload: bytes) -> None:
        parts = subject.split(".")
        # pra.v1.run.<id>.<family...>
        if len(parts) < 5 or parts[0] != "pra" or parts[1] != "v1" or parts[2] != "run":
            return  # discovery/control/others — not run telemetry
        run_id, family = parts[3], parts[4:]
        with self._lock:
            run = self._runs.setdefault(run_id, RunModel(run_id))
            run.last_seen = time.monotonic()
            try:
                event = subjects.from_bytes(payload)
            except ValueError:
                run.wire_errors += 1
                return
            try:
                self._apply(run, family, event)
            except (KeyError, TypeError, ValueError):
                run.wire_errors += 1  # a payload shaped wrong is wire noise, not a crash
                return
            # gap tracking runs on the union of the mirrored seq family — steps,
            # episodes, views, snapshots, status all share one tap-side sequence,
            # so any single subject's seqs legitimately skip. Only forward jumps
            # beyond the union count, and nothing before attach counts at all.
            seq = event.get("seq")
            if isinstance(seq, int):
                if run.last_mirror_seq and seq > run.last_mirror_seq + 1:
                    run.seq_gaps += seq - run.last_mirror_seq - 1
                run.last_mirror_seq = max(run.last_mirror_seq, seq)

    def _apply(self, run: RunModel, family: list[str], event: dict) -> None:
        if family == ["status"]:
            state = event["state"]
            if state == "started":
                if run.state != "completed":
                    run.state = "running"
                run.anatomy = {
                    key: event[key]
                    for key in ("obs_dim", "n_actions", "n_streams", "episode_mode")
                    if key in event
                }
            elif state == "completed":
                run.state = "completed"
                run.completed_summary = event.get("summary")
        elif family == ["tele", "step"]:
            run.last_step = int(event["step"])
        elif family == ["tele", "census"]:
            run.latest_census = event
            run.census_history.append(
                {
                    "seq": event.get("seq"),
                    "population": event.get("population"),
                    "best_dim": event.get("best_dim"),
                }
            )
        elif family == ["tele", "snapshot"]:
            run.snapshots.append(event)
        elif family == ["tele", "view", "static"]:
            run.view_kind = str(event["kind"])
            run.view_static = event.get("static")
        elif family == ["tele", "view", "live"]:
            run.view_kind = str(event["kind"])
            run.view_live = event
        # tele.episode and unknown families: presence already refreshed last_seen

    # -- discovery + the slow inspect loop ---------------------------------------
    def _discover_once(self) -> None:
        request_all = getattr(self.transport, "request_all", None)
        try:
            if request_all is not None:
                replies = request_all(subjects.DISCOVER_SUBJECT, subjects.to_bytes({}), 2.0)
            else:
                replies = [
                    self.transport.request(subjects.DISCOVER_SUBJECT, subjects.to_bytes({}), 2.0)
                ]
        except TransportError:
            return  # nobody home yet — passive observation still materializes runs
        for reply in replies:
            try:
                info = subjects.from_bytes(reply)
                run_id = subjects.validate_run_id(info["run"])
            except (ValueError, KeyError):
                continue
            with self._lock:
                run = self._runs.setdefault(run_id, RunModel(run_id))
                if run.state == "unknown" and info.get("state") in (
                    "running",
                    "paused",
                    "completed",
                ):
                    run.state = info["state"]

    def _slow_loop(self) -> None:
        next_discover = time.monotonic() + self._discover_interval
        while not self._stop.wait(self._inspect_interval):
            if time.monotonic() >= next_discover:
                self._discover_once()
                next_discover = time.monotonic() + self._discover_interval
            with self._lock:
                live = [r for r, m in self._runs.items() if m.state != "completed"]
            for run_id in live:
                reply = self.control(run_id, {"cmd": "inspect"})
                if not reply.get("ok"):
                    continue  # quiet failure: liveness aging is the honest signal
