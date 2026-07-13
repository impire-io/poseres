"""The live viewer (feature 006) — a telemetry tap plus a stdlib HTTP server.

**Non-perturbation is the contract** (FR-007, contracts/rover.md §3): the
run path only ever appends/assigns plain Python values into the tap — the
world records pose events (the L1 occupancy-counter precedent: the world
owns its ground truth and may count it), and the tap's ``bus_factory``
captures the live ``FrameStore`` reference while returning the **standard**
``InMemorySyncBus`` unchanged, so the engine's delivery seam is byte-for-
byte the object it would have had anyway. No RNG, no float work, no locks
on the run path.

All derived computation happens in the serving thread: ``snapshot()``
copies the trail (retrying on a concurrent-mutation ``RuntimeError``) and
reads learning state through public read-only accessors —
``FrameStore.frame_states()`` scored with the run's own
``WeightedSumScorer`` on copies — so every displayed quantity is an
existing, defined quantity of the system (SC-006). Any race during a scan
falls back to the last good reading: a torn read costs one stale viewer
frame, never a byte of the run.

The server is a ``ThreadingHTTPServer`` (daemon threads) bound to
127.0.0.1 with three routes: ``/`` (the single self-contained page,
shipped as package data), ``/layout`` (static world geometry, fetched
once), ``/state`` (the snapshot JSON, polled). Port 0 binds an ephemeral
port; the returned URL always carries the real one.
"""

from __future__ import annotations

import json
import threading
from collections import deque
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from importlib import resources

from pra.config import Config
from pra.core.bus import InMemorySyncBus
from pra.core.scorer import WeightedSumScorer

__all__ = ["RoverTelemetry", "start_viewer"]

TRAIL_MAX = 4000


class RoverTelemetry:
    """The observation-only tap between a rover run and its viewer."""

    def __init__(self, config: Config):
        self._scorer = WeightedSumScorer(config)
        self.pose: tuple[float, float, float] | None = None
        self.bump = 0
        self.step = 0
        self.episode = 0
        self.trail: deque[tuple[float, float]] = deque(maxlen=TRAIL_MAX)
        self.layout: dict | None = None
        self.done = False
        self.final: dict | None = None
        self._store = None
        self._last_trail: list[list[float]] = []
        self._last_learning: dict | None = None

    # ---- run path: plain value copies only (FR-007) ---------------------------
    def attach_layout(self, layout: dict) -> None:
        self.layout = layout

    def record_reset(self, x: float, y: float, theta: float) -> None:
        self.episode += 1
        self.trail.clear()
        self.trail.append((x, y))
        self.pose = (x, y, theta)
        self.bump = 0

    def record_step(self, x: float, y: float, theta: float, bump: int) -> None:
        self.step += 1
        self.trail.append((x, y))
        self.pose = (x, y, theta)
        self.bump = bump

    def bus_factory(self, processor):
        """Pass-through capture point: keep the store reference, return the
        stock bus — the engine's delivery semantics are untouched."""
        self._store = processor
        return InMemorySyncBus(processor)

    def finish(self, summary) -> None:
        self.final = summary.canonical()
        self.done = True

    # ---- serving thread: all derived float work happens here ------------------
    def snapshot(self) -> dict:
        pose = self.pose
        return {
            "step": self.step,
            "episode": self.episode,
            "pose": list(pose) if pose is not None else None,
            "bump": int(self.bump),
            "trail": self._copy_trail(),
            "done": self.done,
            "final": self.final,
            "learning": self._learning(),
        }

    def _copy_trail(self) -> list[list[float]]:
        for _ in range(3):
            try:
                self._last_trail = [[p[0], p[1]] for p in self.trail]
                break
            except RuntimeError:  # deque mutated during iteration — retry/fall back
                continue
        return self._last_trail

    def _learning(self) -> dict | None:
        store = self._store
        if store is None:
            return self._last_learning
        try:
            states = store.frame_states()
            if not states:
                return self._last_learning
            dims: dict[int, int] = {}
            best: tuple[float, int, int, float] | None = None
            for s in states:
                dims[s.dim] = dims.get(s.dim, 0) + 1
                score = float(
                    self._scorer.combine(s.recon_err_ema, s.pred_err_ema, s.effort_ema, s.dim)
                )
                # ties by ascending frame_id — the store's own rule (PRA-01 §7.1)
                if best is None or (score, s.frame_id) < (best[0], best[1]):
                    best = (score, s.frame_id, s.dim, s.pred_err_ema)
        except Exception:  # concurrent mutation mid-scan — one stale frame, no harm
            return self._last_learning
        self._last_learning = {
            "population": len(states),
            "dims": {str(d): dims[d] for d in sorted(dims)},
            "best_dim": best[2],
            "best_score": best[0],
            "pred_err_ema": best[3],
        }
        return self._last_learning


class _ViewerServer(ThreadingHTTPServer):
    daemon_threads = True


def start_viewer(tap: RoverTelemetry, port: int = 8765) -> tuple[ThreadingHTTPServer, str]:
    """Serve the viewer for ``tap`` on 127.0.0.1; returns ``(server, url)``.

    Port 0 binds an ephemeral port (the URL carries the real one); a busy
    port raises ``OSError`` with a message naming it (FR-011). The server
    runs on a daemon thread; call ``shutdown()`` + ``server_close()`` when
    done.
    """
    page = resources.files("pra.examples.rover").joinpath("viewer.html").read_bytes()

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):  # noqa: N802 — http.server API
            if self.path in ("/", "/index.html"):
                self._reply(200, "text/html; charset=utf-8", page)
            elif self.path == "/layout":
                self._reply_json(tap.layout if tap.layout is not None else {})
            elif self.path == "/state":
                self._reply_json(tap.snapshot())
            else:
                self._reply(404, "text/plain; charset=utf-8", b"not found")

        def _reply_json(self, obj: dict) -> None:
            self._reply(200, "application/json", json.dumps(obj).encode("utf-8"))

        def _reply(self, code: int, ctype: str, body: bytes) -> None:
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *args) -> None:  # silence request logging
            pass

    try:
        server = _ViewerServer(("127.0.0.1", port), Handler)
    except OSError as err:
        raise OSError(f"viewer port {port} is unavailable ({err})") from err
    threading.Thread(target=server.serve_forever, daemon=True, name="pra-rover-viewer").start()
    host, real_port = server.server_address[0], server.server_address[1]
    return server, f"http://{host}:{real_port}/"
