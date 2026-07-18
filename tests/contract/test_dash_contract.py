"""Feature 015 contracts §1/§3 — the view channel on the tap, and the
dashboard's endpoints via urllib. Fake transport everywhere; no browser."""

from __future__ import annotations

import json
import time
import urllib.error
import urllib.request

import numpy as np
import pytest

from pra.config import Config
from pra.core.engine import Engine
from pra.dash.model import DashboardModel
from pra.dash.server import start_dashboard
from pra.examples.rover.world import make_rover_body
from pra.nats import NatsTap, subjects
from pra.nats.fake import FakeBusTransport

SMALL = dict(
    warmup_episodes=2,
    n_cycles=2,
    episodes_per_cycle=1,
    steps_per_episode=10,
    horizon_checkpoints=(1, 2),
)

QUIET = dict(census_interval=1e9, view_heartbeat=1e9)
QUIET_LOOPS = dict(discover_interval=1e9, inspect_interval=1e9)


def _rover_factory(tap: NatsTap, with_view: bool):
    view = tap.world_view("rover") if with_view else None

    def inner(config, rng):
        return make_rover_body(config, rng, telemetry=view)

    return tap.world_factory(inner=inner)


# --- §1 the view channel --------------------------------------------------------


def test_rover_mounts_unchanged_and_the_journal_carries_the_view():
    cfg = Config(**SMALL)
    transport = FakeBusTransport()
    tap = NatsTap(transport, run_id="t", **QUIET)
    tap.start()
    summary = Engine(cfg, world_factory=_rover_factory(tap, True), bus_factory=tap.bus_factory).run(
        1
    )
    tap.finish(summary)

    statics = [json.loads(p) for p in transport.published(subjects.view_static_subject("t"))]
    assert len(statics) == 1  # heartbeat suppressed: exactly the first-drain publish
    assert statics[0]["kind"] == "rover"
    layout = statics[0]["static"]
    assert set(layout) >= {"arena_half", "obstacles", "spawns", "actions", "sensors"}

    lives = [json.loads(p) for p in transport.published(subjects.view_live_subject("t"))]
    events = [e["event"] for e in lives]
    assert events.count("reset") == 4 and events.count("step") == 40  # every record mirrored
    assert all(set(e) >= {"kind", "episode", "x", "y", "theta"} for e in lives)
    steps = [e for e in lives if e["event"] == "step"]
    assert all("bump" in e for e in steps)
    assert [e["episode"] for e in lives] == sorted(e["episode"] for e in lives)


def test_view_channel_byte_identity_on_off_bare():
    cfg = Config(**SMALL)
    bare = Engine(cfg, world_factory=make_rover_body).run(1).serialize()

    tap_off = NatsTap(FakeBusTransport(), run_id="t", **QUIET)
    tap_off.start()
    without_view = Engine(
        cfg, world_factory=_rover_factory(tap_off, False), bus_factory=tap_off.bus_factory
    ).run(1)
    tap_off.finish(without_view)

    tap_on = NatsTap(FakeBusTransport(), run_id="t", **QUIET)
    tap_on.start()
    with_view = Engine(
        cfg, world_factory=_rover_factory(tap_on, True), bus_factory=tap_on.bus_factory
    ).run(1)
    tap_on.finish(with_view)

    assert with_view.serialize() == without_view.serialize() == bare


def test_view_construction_draws_identical_under_the_adapter():
    cfg = Config(**SMALL)
    rng_bare = np.random.default_rng(5)
    make_rover_body(cfg, rng_bare)
    rng_view = np.random.default_rng(5)
    tap = NatsTap(FakeBusTransport(), run_id="t", **QUIET)
    _rover_factory(tap, True)(cfg, rng_view)
    assert rng_bare.bit_generator.state == rng_view.bit_generator.state


def test_static_heartbeat_republishes_for_late_attachers():
    transport = FakeBusTransport()
    tap = NatsTap(
        transport, run_id="t", census_interval=1e9, view_heartbeat=0.03, drain_interval=0.01
    )
    tap.world_view("rover").attach_layout({"arena_half": 1.0, "obstacles": []})
    tap.start()
    deadline = time.monotonic() + 10
    while len(transport.published(subjects.view_static_subject("t"))) < 3:
        assert time.monotonic() < deadline, "heartbeat never re-published the layout"
        time.sleep(0.01)
    statics = [json.loads(p) for p in transport.published(subjects.view_static_subject("t"))]
    assert all(s["static"] == {"arena_half": 1.0, "obstacles": []} for s in statics)


def test_worlds_offering_nothing_publish_nothing():
    cfg = Config(**SMALL)
    transport = FakeBusTransport()
    tap = NatsTap(transport, run_id="t", **QUIET)
    tap.start()
    summary = Engine(cfg, world_factory=tap.world_factory(), bus_factory=tap.bus_factory).run(1)
    tap.finish(summary)
    assert transport.published("pra.v1.run.t.tele.view.>") == []


def test_unknown_view_kind_carries_args_verbatim():
    tap = NatsTap(FakeBusTransport(), run_id="t", **QUIET)
    adapter = tap.world_view("alien")
    adapter.record_reset(1.0, 2.0)
    adapter.record_step(3.0)
    items = list(tap._buffer)
    assert items[0][3] == {"event": "reset", "episode": 1, "args": [1.0, 2.0]}
    assert items[1][3] == {"event": "step", "episode": 1, "args": [3.0]}


# --- §3 the endpoints -----------------------------------------------------------


def _get(url: str):
    try:
        with urllib.request.urlopen(url, timeout=5) as response:
            return response.status, json.loads(response.read())
    except urllib.error.HTTPError as err:
        with err:  # close the response body — unraisable-at-GC otherwise
            return err.code, json.loads(err.read())


def _post(url: str, body: dict):
    request = urllib.request.Request(url, data=json.dumps(body).encode(), method="POST")
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            return response.status, json.loads(response.read())
    except urllib.error.HTTPError as err:
        with err:
            return err.code, json.loads(err.read())


@pytest.fixture()
def dash():
    transport = FakeBusTransport()
    model = DashboardModel(transport, **QUIET_LOOPS)
    model.start()
    server, url = start_dashboard(model, port=0)
    yield transport, model, url
    server.shutdown()
    server.server_close()
    model.stop()


def test_page_and_runs_endpoints(dash):
    transport, model, url = dash
    with urllib.request.urlopen(url, timeout=5) as response:
        page = response.read()
    assert b"PRA" in page and b"</html>" in page  # the self-contained page
    status, runs = _get(url + "runs")
    assert status == 200 and runs == {"runs": []}
    transport.publish(
        subjects.census_subject("a"), subjects.to_bytes({"run": "a", "seq": 1, "population": 2})
    )
    status, runs = _get(url + "runs")
    assert runs["runs"][0]["run"] == "a"


def test_state_endpoint_serves_both_modes_and_404s_unknown(dash):
    transport, model, url = dash
    status, body = _get(url + "run/ghost/state")
    assert status == 404 and "unknown run" in body["error"]
    transport.publish(
        subjects.census_subject("a"),
        subjects.to_bytes({"run": "a", "seq": 1, "population": 2, "best_dim": 3, "dims": {"3": 2}}),
    )
    transport.publish(
        subjects.view_static_subject("a"),
        subjects.to_bytes({"run": "a", "seq": 2, "kind": "alien", "static": {"z": 1}}),
    )
    status, state = _get(url + "run/a/state")
    assert status == 200
    # everything both modes render is present (contracts §3.3)
    for key in (
        "run",
        "state",
        "age_seconds",
        "census",
        "census_history",
        "counters",
        "snapshots",
        "view",
        "seq_gaps",
        "wire_errors",
        "completed_summary",
    ):
        assert key in state
    assert state["view"]["kind"] == "alien"  # unknown kinds pass through, named


def test_ctrl_endpoint_forwards_verbatim_and_404s(dash):
    transport, model, url = dash
    status, body = _post(url + "run/ghost/ctrl", {"cmd": "inspect"})
    assert status == 404

    # a live tap on the same transport: the real control plane answers
    tap = NatsTap(transport, run_id="a", **QUIET)
    tap.start()
    transport.publish(
        subjects.census_subject("a"), subjects.to_bytes({"run": "a", "seq": 1, "population": 2})
    )

    status, reply = _post(url + "run/a/ctrl", {"cmd": "inspect"})
    assert status == 200 and reply["ok"] and reply["state"] == "running"
    status, reply = _post(url + "run/a/ctrl", {"cmd": "pause"})
    assert reply == {"ok": True, "state": "paused", "position": 0, "already": False}
    status, reply = _post(url + "run/a/ctrl", {"cmd": "resume"})
    assert reply["ok"] and reply["state"] == "running"
    status, reply = _post(url + "run/a/ctrl", {"cmd": "reboot"})
    assert reply["ok"] is False and "unknown cmd" in reply["error"]  # B6 grammar, unsoftened
    status, reply = _post(url + "run/a/ctrl", {"cmd": "snapshot"})
    assert reply["ok"] is False and "snapshot-configured" in reply["error"]


def test_ctrl_transport_failure_is_an_error_payload_not_a_hang(dash):
    transport, model, url = dash
    transport.publish(subjects.census_subject("lone"), subjects.to_bytes({"run": "lone", "seq": 1}))
    status, reply = _post(url + "run/lone/ctrl", {"cmd": "inspect"})  # nobody serving ctrl
    assert status == 200 and reply["ok"] is False and "failed" in reply["error"]
