"""Feature 015 T002 — the consumer model from scripted payloads (contracts §2).
No engine, no server: the fake transport's publish IS the wire."""

from __future__ import annotations

import time

from pra.dash.model import DashboardModel, RunModel
from pra.nats import subjects
from pra.nats.fake import FakeBusTransport

QUIET_LOOPS = dict(discover_interval=1e9, inspect_interval=1e9)


def _model() -> tuple[FakeBusTransport, DashboardModel]:
    transport = FakeBusTransport()
    model = DashboardModel(transport, **QUIET_LOOPS)
    model.start()
    return transport, model


def _pub(transport, subject, payload: dict) -> None:
    transport.publish(subject, subjects.to_bytes(payload))


def test_runs_materialize_from_observed_traffic_and_never_crosstalk():
    transport, model = _model()
    _pub(transport, subjects.census_subject("a"), {"run": "a", "seq": 1, "population": 3})
    _pub(transport, subjects.census_subject("b"), {"run": "b", "seq": 1, "population": 9})
    rows = model.runs_summary()["runs"]
    assert [r["run"] for r in rows] == ["a", "b"]  # sorted, both present
    assert model.state_of("a")["census"]["population"] == 3
    assert model.state_of("b")["census"]["population"] == 9
    assert model.state_of("c") is None
    model.stop()


def test_late_appearing_run_is_listed_without_restart():
    transport, model = _model()
    assert model.runs_summary()["runs"] == []
    _pub(transport, subjects.step_subject("late"), {"run": "late", "seq": 1, "step": 1})
    assert [r["run"] for r in model.runs_summary()["runs"]] == ["late"]
    model.stop()


def test_discovery_sweep_materializes_replying_runs():
    transport = FakeBusTransport()

    def responder(payload, reply):
        reply(subjects.to_bytes({"run": "swept", "state": "running", "subjects": {}}))

    transport.serve_requests(subjects.DISCOVER_SUBJECT, responder)
    model = DashboardModel(transport, **QUIET_LOOPS)
    model.start()  # the start-time sweep
    row = model.runs_summary()["runs"][0]
    assert row["run"] == "swept" and row["state"] == "running"
    model.stop()


def test_liveness_ages_monotonically():
    transport, model = _model()
    _pub(transport, subjects.census_subject("a"), {"run": "a", "seq": 1, "population": 1})
    age_then = model.state_of("a")["age_seconds"]
    time.sleep(0.05)
    age_now = model.state_of("a")["age_seconds"]
    assert age_then is not None and age_now > age_then >= 0
    model.stop()


def test_status_lifecycle_and_completion_is_terminal():
    transport, model = _model()
    _pub(
        transport,
        subjects.status_subject("a"),
        {"run": "a", "seq": 1, "state": "started", "obs_dim": 10, "n_actions": 4},
    )
    state = model.state_of("a")
    assert state["state"] == "running" and state["anatomy"]["obs_dim"] == 10
    _pub(
        transport,
        subjects.status_subject("a"),
        {"run": "a", "seq": 9, "state": "completed", "summary": {"seed": 1}},
    )
    _pub(transport, subjects.status_subject("a"), {"run": "a", "seq": 10, "state": "started"})
    state = model.state_of("a")
    assert state["state"] == "completed"  # terminal
    assert state["completed_summary"] == {"seed": 1}
    model.stop()


def test_seq_gaps_are_counted_not_repaired():
    transport, model = _model()
    _pub(transport, subjects.step_subject("a"), {"run": "a", "seq": 2, "step": 1})
    _pub(transport, subjects.step_subject("a"), {"run": "a", "seq": 6, "step": 4})
    state = model.state_of("a")
    assert state["seq_gaps"] == 3 and state["last_step"] == 4
    model.stop()


def test_interleaved_family_seqs_are_not_gaps():
    """The mirrored seq family is shared (steps, episodes, views, snapshots) —
    a single subject's seqs legitimately skip; only union holes are gaps.
    Regression: the first live rover run showed seq_gaps 1171 with zero drops."""
    transport, model = _model()
    _pub(transport, subjects.step_subject("a"), {"run": "a", "seq": 1, "step": 1})
    _pub(
        transport,
        subjects.view_live_subject("a"),
        {"run": "a", "seq": 2, "kind": "rover", "event": "step", "x": 0.0},
    )
    _pub(transport, subjects.step_subject("a"), {"run": "a", "seq": 3, "step": 2})
    _pub(transport, subjects.episode_subject("a"), {"run": "a", "seq": 4, "episode": 2})
    _pub(transport, subjects.step_subject("a"), {"run": "a", "seq": 5, "step": 3})
    assert model.state_of("a")["seq_gaps"] == 0
    _pub(transport, subjects.step_subject("a"), {"run": "a", "seq": 9, "step": 4})  # a real hole
    assert model.state_of("a")["seq_gaps"] == 3
    model.stop()


def test_malformed_payloads_count_and_never_raise():
    transport, model = _model()
    transport.publish(subjects.census_subject("a"), b"not json")
    transport.publish(subjects.step_subject("a"), subjects.to_bytes({"run": "a"}))  # no seq/step
    state = model.state_of("a")
    assert state["wire_errors"] == 2
    _pub(transport, subjects.census_subject("a"), {"run": "a", "seq": 1, "population": 2})
    assert model.state_of("a")["census"]["population"] == 2  # still consuming
    model.stop()


def test_census_history_is_bounded_and_ordered():
    transport, model = _model()
    for i in range(600):
        _pub(
            transport,
            subjects.census_subject("a"),
            {"run": "a", "seq": i, "population": i, "best_dim": 3},
        )
    history = model.state_of("a")["census_history"]
    assert len(history) == 512  # bounded
    assert history[0]["seq"] == 88 and history[-1]["seq"] == 599  # oldest dropped
    model.stop()


def test_view_payloads_land_and_flag_presence():
    transport, model = _model()
    _pub(
        transport,
        subjects.view_static_subject("a"),
        {"run": "a", "seq": 1, "kind": "rover", "static": {"arena_half": 1.0}},
    )
    _pub(
        transport,
        subjects.view_live_subject("a"),
        {"run": "a", "seq": 2, "kind": "rover", "event": "step", "x": 0.1, "y": 0.2},
    )
    state = model.state_of("a")
    assert state["view"]["kind"] == "rover"
    assert state["view"]["static"] == {"arena_half": 1.0}
    assert state["view"]["live"]["x"] == 0.1
    assert model.runs_summary()["runs"][0]["has_view"] is True
    model.stop()


def test_run_model_state_payload_is_coherent_before_any_traffic():
    run = RunModel("empty")
    payload = run.state_payload()
    assert payload["state"] == "unknown" and payload["age_seconds"] is None
    assert payload["view"] is None and payload["census_history"] == []
