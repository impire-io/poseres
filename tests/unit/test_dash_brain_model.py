"""Feature 029 — the dashboard model's brain families: latest-wins metadata
and frame rows, bounded step/event windows (the FR-013 mechanism), and
malformed payloads counted as wire noise, never crashes."""

from __future__ import annotations

from pra.dash.model import EVENTS_WINDOW, STEPS_WINDOW, DashboardModel
from pra.nats import subjects
from pra.nats.fake import FakeBusTransport


def _model() -> tuple[DashboardModel, FakeBusTransport]:
    transport = FakeBusTransport()
    model = DashboardModel(transport, discover_interval=1e9, inspect_interval=1e9)
    model.start()
    return model, transport


def _pub(transport: FakeBusTransport, subject: str, payload: dict) -> None:
    transport.publish(subject, subjects.to_bytes(payload))


def test_brain_anatomy_latest_wins():
    model, transport = _model()
    meta = {"run": "a", "seq": 1, "obs_dim": 3, "n_actions": 2, "groups": [], "actuators": []}
    _pub(transport, subjects.brain_anatomy_subject("a"), meta)
    assert model.state_of("a")["brain_meta"]["obs_dim"] == 3
    _pub(transport, subjects.brain_anatomy_subject("a"), {**meta, "seq": 9, "obs_dim": 4})
    assert model.state_of("a")["brain_meta"]["obs_dim"] == 4  # heartbeat replaces


def test_steps_window_fills_and_stays_bounded():
    model, transport = _model()
    for i in range(1, STEPS_WINDOW + 101):
        _pub(
            transport,
            subjects.step_subject("a"),
            {
                "run": "a",
                "seq": i,
                "stream": 0,
                "episode": 1,
                "step": i,
                "action": 2,
                "obs": [0.1, 0.2],
            },
        )
    window = model.state_of("a")["steps_window"]
    assert len(window) == STEPS_WINDOW  # bounded by construction
    assert window[-1]["step"] == STEPS_WINDOW + 100  # newest kept
    assert window[-1]["action"] == 2 and window[-1]["obs"] == [0.1, 0.2]


def test_frames_latest_wins():
    model, transport = _model()
    _pub(
        transport,
        subjects.brain_frames_subject("a"),
        {
            "run": "a",
            "seq": 5,
            "population": 1,
            "best_frame": 7,
            "rows": [
                {
                    "id": 7,
                    "dim": 3,
                    "age": 1,
                    "cand": True,
                    "recon": 0.5,
                    "pred": 0.6,
                    "effort": 0.1,
                    "score": 0.9,
                }
            ],
        },
    )
    latest = model.state_of("a")["frames_latest"]
    assert latest["population"] == 1 and latest["rows"][0]["id"] == 7


def test_events_window_appends_in_order_and_stays_bounded():
    model, transport = _model()
    for i in range(EVENTS_WINDOW + 50):
        _pub(
            transport,
            subjects.brain_events_subject("a"),
            {
                "run": "a",
                "seq": i + 1,
                "event": "spawn" if i % 2 == 0 else "evict",
                "frame": i,
                "steps": i * 10,
            },
        )
    events = model.state_of("a")["events"]
    assert len(events) == EVENTS_WINDOW
    assert events[-1]["frame"] == EVENTS_WINDOW + 49  # newest last, oldest dropped


def test_malformed_brain_events_count_as_wire_noise():
    model, transport = _model()
    _pub(transport, subjects.brain_events_subject("a"), {"run": "a", "seq": 1, "event": "spawn"})
    state = model.state_of("a")
    assert state["wire_errors"] == 1 and state["events"] == []  # no frame id -> noise


def test_absent_families_render_as_null_not_errors():
    model, transport = _model()
    _pub(transport, subjects.census_subject("a"), {"run": "a", "seq": 1, "population": 2})
    state = model.state_of("a")
    assert state["brain_meta"] is None and state["frames_latest"] is None
    assert state["events"] == [] and state["steps_window"] == []
