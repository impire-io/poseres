"""Feature 015 contracts §4/§5.4 — the off-process observer proof: a live
engine run, the dashboard model consuming, the HTTP server hammered, and the
summary byte-identical to the bare run. Fake transport; no NATS, no browser."""

from __future__ import annotations

import json
import threading
import time
import urllib.error
import urllib.request

from pra.config import Config
from pra.core.engine import Engine
from pra.dash.model import DashboardModel
from pra.dash.server import start_dashboard
from pra.examples.rover.world import make_rover_body
from pra.nats import NatsSnapshotStore, NatsTap
from pra.nats.fake import FakeBusTransport
from pra.world.event_source import SensorimotorWorld

SMALL = dict(
    warmup_episodes=2,
    n_cycles=2,
    episodes_per_cycle=1,
    steps_per_episode=10,
    horizon_checkpoints=(1, 2),
)

QUIET = dict(census_interval=1e9, view_heartbeat=1e9)
FAST_LOOPS = dict(discover_interval=1e9, inspect_interval=1e9)


class PacedWorld(SensorimotorWorld):
    """Identical draws, ~5 ms per step — something to interrupt."""

    def step(self, action):
        time.sleep(0.005)
        return super().step(action)


def _get(url: str) -> dict:
    with urllib.request.urlopen(url, timeout=5) as response:
        return json.loads(response.read())


def _post(url: str, body: dict, timeout: float = 90.0) -> dict:
    request = urllib.request.Request(url, data=json.dumps(body).encode(), method="POST")
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read())


def _hammer(url: str, run_id: str, stop: threading.Event, polls: dict) -> None:
    while not stop.is_set():
        try:
            _get(url + "runs")
            _get(url + f"run/{run_id}/state")
            polls["count"] += 1
        except (urllib.error.URLError, ConnectionError, TimeoutError, OSError):
            if stop.is_set():
                break


def _watched_run(cfg: Config, world_factory_for, run_id: str = "t", drain: float = 0.005):
    """Run an engine with tap + model + hammered server attached; return the
    summary and the polls count."""
    transport = FakeBusTransport()
    tap = NatsTap(transport, run_id=run_id, drain_interval=drain, **QUIET)
    tap.start()
    model = DashboardModel(transport, **FAST_LOOPS)
    model.start()
    server, url = start_dashboard(model, port=0)
    stop = threading.Event()
    polls = {"count": 0}
    poller = threading.Thread(target=_hammer, args=(url, run_id, stop, polls), daemon=True)
    try:
        poller.start()
        engine = Engine(cfg, world_factory=world_factory_for(tap), bus_factory=tap.bus_factory)
        summary = engine.run(1)
        tap.finish(summary)
    finally:
        stop.set()
        poller.join(timeout=10)
        server.shutdown()
        server.server_close()
        model.stop()
    return summary, polls["count"], model


# --- §4.1: the polling-hammer observer proof ------------------------------------


def test_dashboard_attached_and_hammered_is_byte_identical_reference():
    cfg = Config(**SMALL)
    bare = Engine(cfg).run(1).serialize()
    summary, polls, model = _watched_run(cfg, lambda tap: tap.world_factory(inner=PacedWorld))
    assert summary.serialize() == bare
    assert polls > 0  # the run really was watched while it happened
    state = model.state_of("t")
    assert state is not None and state["state"] == "completed"
    assert state["completed_summary"] == summary.canonical()  # the wire carried the truth


def test_dashboard_attached_is_byte_identical_rover_with_view():
    cfg = Config(**SMALL)
    bare = Engine(cfg, world_factory=make_rover_body).run(1).serialize()

    def factory_for(tap):
        view = tap.world_view("rover")
        return tap.world_factory(inner=lambda c, r: make_rover_body(c, r, telemetry=view))

    summary, polls, model = _watched_run(cfg, factory_for)
    assert summary.serialize() == bare
    assert polls > 0
    view = model.state_of("t")["view"]
    assert view is not None and view["kind"] == "rover"
    assert "arena_half" in view["static"] and "x" in view["live"]  # the world arrived


def test_attach_and_detach_mid_run_changes_nothing():
    cfg = Config(**SMALL)
    bare = Engine(cfg).run(1).serialize()

    transport = FakeBusTransport()
    tap = NatsTap(transport, run_id="t", drain_interval=0.002, **QUIET)
    tap.start()
    engine = Engine(
        cfg, world_factory=tap.world_factory(inner=PacedWorld), bus_factory=tap.bus_factory
    )
    box: dict = {}

    def run():
        box["summary"] = engine.run(1)

    runner = threading.Thread(target=run, daemon=True)
    runner.start()

    # attach mid-run, poll a little, then tear the whole dashboard down
    model = DashboardModel(transport, **FAST_LOOPS)
    model.start()
    server, url = start_dashboard(model, port=0)
    deadline = time.monotonic() + 10
    while model.state_of("t") is None and time.monotonic() < deadline:
        time.sleep(0.005)
    _get(url + "runs")
    server.shutdown()
    server.server_close()
    model.stop()  # detached while the run continues

    runner.join(timeout=30)
    tap.finish(box["summary"])
    assert box["summary"].serialize() == bare


# --- §4.3: the control round-trip through the dashboard's own surface ------------


def test_control_round_trip_through_the_dashboard_endpoint():
    cfg = Config(**SMALL, snapshot_every_n_cycles=1)
    bare = Engine(cfg).run(1).serialize()

    transport = FakeBusTransport()
    tap = NatsTap(transport, run_id="t", drain_interval=0.002, **QUIET)
    store = NatsSnapshotStore(transport)
    tap.start()
    model = DashboardModel(transport, **FAST_LOOPS)
    model.start()
    server, url = start_dashboard(model, port=0)

    engine = Engine(
        cfg,
        world_factory=tap.world_factory(inner=PacedWorld),
        bus_factory=tap.bus_factory,
        snapshot_store=tap.wrap_store(store),
    )
    box: dict = {}

    def run():
        box["summary"] = engine.run(1)

    runner = threading.Thread(target=run, daemon=True)
    runner.start()
    deadline = time.monotonic() + 20
    while model.state_of("t") is None and time.monotonic() < deadline:
        time.sleep(0.005)

    paused = _post(url + "run/t/ctrl", {"cmd": "pause"})
    assert paused["ok"] and paused["state"] == "paused"
    settled = tap.steps
    time.sleep(0.1)
    assert tap.steps <= settled + 1  # frozen at the gate (at most the in-flight step)
    frozen = tap.steps
    time.sleep(0.1)
    assert tap.steps == frozen

    resumed = _post(url + "run/t/ctrl", {"cmd": "resume"})
    assert resumed["ok"]
    snap = _post(url + "run/t/ctrl", {"cmd": "snapshot"})  # deferred to the next C4 write
    assert snap["ok"], snap
    assert snap["snapshot_id"] in {i for i, _ in store.list()}

    runner.join(timeout=60)
    tap.finish(box["summary"])
    server.shutdown()
    server.server_close()
    model.stop()
    assert box["summary"].serialize() == bare  # paused-and-resumed ≡ never-paused


# --- §5.4: advanced-mode data completeness beyond the reference config -----------


def test_advanced_mode_data_is_complete_for_a_nonreference_config():
    cfg = Config(**SMALL, obs_dim=20, true_dim=6, snapshot_every_n_cycles=1)
    transport = FakeBusTransport()
    tap = NatsTap(transport, run_id="s", drain_interval=0.005, census_interval=1e9)
    store = NatsSnapshotStore(transport)
    tap.start()
    model = DashboardModel(transport, **FAST_LOOPS)
    model.start()
    engine = Engine(
        cfg,
        world_factory=tap.world_factory(),
        bus_factory=tap.bus_factory,
        snapshot_store=tap.wrap_store(store),
    )
    summary = engine.run(1)
    tap._publish_census()  # drive the publisher-thread reading deterministically
    tap.finish(summary)

    reply = model.control("s", {"cmd": "inspect"})  # counters via the read-only command
    assert reply["ok"]

    state = model.state_of("s")
    assert state["census"] is not None and sum(state["census"]["dims"].values()) > 0
    assert len(state["census_history"]) >= 1
    assert state["counters"] is not None and "events_mirrored" in state["counters"]
    assert len(state["snapshots"]) == 2  # one notice per cycle
    assert state["completed_summary"] == summary.canonical()
    model.stop()
