"""Feature 014 contracts §2–§4 — the tap's mirror and census, the control
plane's commands and error grammar, and the object-store snapshot backend.
Everything runs on the FakeBusTransport: no NATS library, no server."""

from __future__ import annotations

import json
import time

import numpy as np
import pytest

from pra.config import Config
from pra.core.engine import Engine
from pra.nats import NatsSnapshotStore, NatsTap, subjects
from pra.nats.fake import FakeBusTransport
from pra.persistence.snapshot import FORMAT_VERSION
from pra.persistence.store import InMemorySnapshotStore, SnapshotStore
from pra.world.event_source import SensorimotorWorld

SMALL = dict(
    warmup_episodes=2,
    n_cycles=2,
    episodes_per_cycle=1,
    steps_per_episode=10,
    horizon_checkpoints=(1, 2),
)

QUIET = dict(census_interval=1e9)  # suppress the wall-clock census for determinism


def _tapped_run(cfg: Config, seed: int = 1, run_id: str = "t", **tap_kwargs):
    transport = FakeBusTransport()
    tap = NatsTap(transport, run_id=run_id, **{**QUIET, **tap_kwargs})
    engine = Engine(cfg, world_factory=tap.world_factory(), bus_factory=tap.bus_factory)
    tap.start()
    summary = engine.run(seed)
    tap.finish(summary)
    return transport, tap, summary


# --- §2 the tap: mirror fidelity, determinism, census, lifecycle ---------------


def test_mirror_reproduces_the_exact_step_sequence():
    cfg = Config(**SMALL)
    recorded: list[tuple[int, np.ndarray]] = []

    class RecordingWorld(SensorimotorWorld):
        def step(self, action):
            obs = super().step(action)
            recorded.append((int(action), np.array(obs, copy=True)))
            return obs

    Engine(cfg, world_factory=RecordingWorld).run(1)  # ground truth, no tap
    transport, tap, _ = _tapped_run(cfg)

    steps = [json.loads(p) for p in transport.published(subjects.step_subject("t"))]
    assert len(steps) == len(recorded) == 40
    for i, (payload, (action, obs)) in enumerate(zip(steps, recorded, strict=True), start=1):
        assert payload["run"] == "t" and payload["stream"] == 0
        assert payload["step"] == i and payload["action"] == action
        assert payload["obs"] == [float(x) for x in obs]
    seqs = [p["seq"] for p in steps]
    assert seqs == sorted(seqs)  # mirrored order is run order
    assert tap.events_dropped == 0


def test_payloads_are_byte_deterministic_across_identical_runs():
    cfg = Config(**SMALL)
    journal_a = _tapped_run(cfg)[0].journal
    journal_b = _tapped_run(cfg)[0].journal
    assert journal_a == journal_b  # byte-for-byte, subjects and payloads


def test_status_lifecycle_started_then_completed():
    cfg = Config(**SMALL)
    transport, tap, summary = _tapped_run(cfg)
    statuses = [json.loads(p) for p in transport.published(subjects.status_subject("t"))]
    assert statuses[0]["state"] == "started"
    assert statuses[0]["obs_dim"] == 10 and statuses[0]["n_actions"] == 4
    assert statuses[0]["n_streams"] == 1 and statuses[0]["episode_mode"] == "episodic"
    assert statuses[-1]["state"] == "completed"
    assert statuses[-1]["summary"] == summary.canonical()
    # the announce precedes every step in the journal
    subjects_in_order = [s for s, _ in transport.journal]
    assert subjects_in_order.index(subjects.status_subject("t")) < subjects_in_order.index(
        subjects.step_subject("t")
    )


def test_episode_events_carry_boot_then_resets():
    cfg = Config(**SMALL)
    transport, _, _ = _tapped_run(cfg)
    episodes = [json.loads(p) for p in transport.published(subjects.episode_subject("t"))]
    assert [e["kind"] for e in episodes] == ["boot", "reset", "reset", "reset"]
    assert [e["episode"] for e in episodes] == [1, 2, 3, 4]


def test_census_derives_off_path_and_survives_torn_reads():
    cfg = Config(**SMALL)
    transport = FakeBusTransport()
    tap = NatsTap(transport, run_id="t", **QUIET)
    engine = Engine(cfg, world_factory=tap.world_factory(), bus_factory=tap.bus_factory)
    tap.start()
    summary = engine.run(1)

    tap._publish_census()  # publisher-thread method, driven synchronously here
    census = json.loads(transport.published(subjects.census_subject("t"))[-1])
    assert census["population"] == summary.final_population
    assert census["best_dim"] == summary.best_dim
    assert census["steps"] == 40
    assert sum(census["dims"].values()) == census["population"]

    class TornStore:
        def frame_states(self):
            raise RuntimeError("concurrent mutation mid-scan")

    good = tap.census()
    tap._store = TornStore()
    tap._publish_census()  # no raise, no new message, last good reading kept
    assert tap.census() == good
    assert len(transport.published(subjects.census_subject("t"))) == 1
    tap.finish(summary)


def test_wrapped_world_hides_nothing_and_adds_nothing():
    cfg = Config(**SMALL)
    tap = NatsTap(FakeBusTransport(), run_id="t", **QUIET)
    world = tap.world_factory()(cfg, np.random.default_rng(1))
    assert world.n_actions == 4 and world.obs_dim == 10
    assert getattr(world, "snapshot_needs_state", False) is False  # passthrough default
    assert callable(world.state_dict)  # capture protocol reaches the inner world
    with pytest.raises(AttributeError):
        _ = world.no_such_attribute


# --- §3 the control plane ------------------------------------------------------


def _live_tap(cfg=None, **tap_kwargs):
    transport = FakeBusTransport()
    tap = NatsTap(transport, run_id="t", **{**QUIET, **tap_kwargs})
    tap.start()
    if cfg is not None:  # capture the config through the public factory surface
        tap.world_factory()(cfg, np.random.default_rng(1))
    return transport, tap


def _ctrl(transport, request: dict, timeout: float = 2.0) -> dict:
    return json.loads(
        transport.request(subjects.control_subject("t"), subjects.to_bytes(request), timeout)
    )


def test_inspect_answers_in_every_state():
    transport, tap = _live_tap()
    reply = _ctrl(transport, {"cmd": "inspect"})
    assert reply["ok"] and reply["run"] == "t" and reply["state"] == "running"
    assert reply["census"] is None and reply["counters"]["events_mirrored"] == 0
    tap.pause()
    assert _ctrl(transport, {"cmd": "inspect"})["state"] == "paused"
    tap.resume()

    class _Summary:
        def canonical(self):
            return {"seed": 1}

    tap.finish(_Summary())
    assert _ctrl(transport, {"cmd": "inspect"})["state"] == "completed"


def test_pause_resume_replies_and_idempotence():
    transport, tap = _live_tap()
    first = _ctrl(transport, {"cmd": "pause"})
    assert first == {"ok": True, "state": "paused", "position": 0, "already": False}
    again = _ctrl(transport, {"cmd": "pause"})
    assert again["already"] is True
    resumed = _ctrl(transport, {"cmd": "resume"})
    assert resumed == {"ok": True, "state": "running", "already": False}
    assert _ctrl(transport, {"cmd": "resume"})["already"] is True


def test_every_malformed_request_is_answered_and_the_run_never_crashes():
    transport, tap = _live_tap()
    bad = [
        b"not json",
        b"[1,2]",
        subjects.to_bytes({"cmd": "reboot"}),
        subjects.to_bytes({}),
    ]
    for payload in bad:
        reply = json.loads(transport.request(subjects.control_subject("t"), payload, 2.0))
        assert reply["ok"] is False and reply["error"]
    assert tap.control_errors == len(bad)
    assert tap.control_requests == len(bad)


def test_snapshot_command_error_paths():
    # unconfigured: no wrapped store, no cadence
    transport, tap = _live_tap(cfg=Config(**SMALL))
    reply = _ctrl(transport, {"cmd": "snapshot"})
    assert reply["ok"] is False and "snapshot-configured" in reply["error"]

    # configured but the run completes before the next boundary
    cfg = Config(**SMALL, snapshot_every_n_cycles=1)
    transport, tap = _live_tap(cfg=cfg)
    tap.wrap_store(InMemorySnapshotStore())
    got: list[dict] = []
    tap._control.handle(subjects.to_bytes({"cmd": "snapshot"}), lambda b: got.append(json.loads(b)))
    assert got == []  # deferred: no reply yet

    class _Summary:
        def canonical(self):
            return {"seed": 1}

    tap.finish(_Summary())  # completion beats the boundary
    assert got and got[0]["ok"] is False and "completed" in got[0]["error"]


def test_snapshot_command_fulfills_at_the_next_c4_write():
    cfg = Config(**SMALL, snapshot_every_n_cycles=1)
    transport, tap = _live_tap(cfg=cfg, drain_interval=0.005)
    store = tap.wrap_store(InMemorySnapshotStore())
    got: list[dict] = []
    tap._control.handle(subjects.to_bytes({"cmd": "snapshot"}), lambda b: got.append(json.loads(b)))
    assert got == []
    metadata = {
        "timestamp": 1.0,
        "step": 40,
        "cycle": 2,
        "population": 3,
        "format_version": FORMAT_VERSION,
    }
    snapshot_id = store.write(b"blob", metadata)  # the engine's C4 call, simulated
    assert got == [{"ok": True, "snapshot_id": snapshot_id, "step": 40, "cycle": 2}]
    # the write is announced on the snapshot subject once the pump drains it
    deadline = time.monotonic() + 10
    while not transport.published(subjects.snapshot_subject("t")):
        assert time.monotonic() < deadline, "snapshot notice never published"
        time.sleep(0.005)
    notice = json.loads(transport.published(subjects.snapshot_subject("t"))[-1])
    assert notice == {
        "run": "t",
        "seq": notice["seq"],
        "snapshot_id": snapshot_id,
        "step": 40,
        "cycle": 2,
        "population": 3,
        "format_version": FORMAT_VERSION,
    }


def test_discover_names_every_live_run():
    transport = FakeBusTransport()
    taps = [NatsTap(transport, run_id=r, **QUIET) for r in ("alpha", "beta")]
    for tap in taps:
        tap.start()
    replies = [json.loads(b) for b in transport.request_all(subjects.DISCOVER_SUBJECT, b"{}")]
    assert {r["run"] for r in replies} == {"alpha", "beta"}
    for r in replies:
        assert r["subjects"] == subjects.run_subjects(r["run"])


# --- §4 the object-store snapshot backend --------------------------------------


def _metadata(step, cycle):
    return {
        "timestamp": 1.0,
        "step": step,
        "cycle": cycle,
        "population": 3,
        "format_version": FORMAT_VERSION,
    }


def test_store_satisfies_the_existing_protocol_semantics():
    store = NatsSnapshotStore(FakeBusTransport())
    assert isinstance(store, SnapshotStore)
    id1 = store.write(b"one", _metadata(10, 1))
    id2 = store.write(b"two", _metadata(20, 2))
    assert [i for i, _ in store.list()] == [id2, id1]  # newest first
    assert store.read(id1) == b"one"  # blobs opaque: bytes back verbatim
    store.delete(id2)
    assert [i for i, _ in store.list()] == [id1]
    store.delete(id2)  # idempotent


def test_store_metadata_round_trips_verbatim():
    store = NatsSnapshotStore(FakeBusTransport())
    metadata = _metadata(10, 1)
    store.write(b"one", metadata)
    assert store.list()[0][1] == metadata


def test_store_empty_and_missing_grammar():
    store = NatsSnapshotStore(FakeBusTransport())
    assert store.list() == []  # no bucket yet = an empty store
    with pytest.raises(KeyError, match="no committed snapshot"):
        store.read("snap-000000000010-00001")
    store.delete("snap-000000000010-00001")  # idempotent even before the bucket


def test_store_failures_are_loud_and_named():
    transport = FakeBusTransport()
    store = NatsSnapshotStore(transport)
    store.write(b"one", _metadata(10, 1))
    transport.set_down()
    with pytest.raises(RuntimeError, match="write"):
        store.write(b"two", _metadata(20, 2))
    with pytest.raises(RuntimeError, match="read"):
        store.read("snap-000000000010-00001")
    with pytest.raises(RuntimeError, match="list"):
        store.list()
    with pytest.raises(RuntimeError, match="delete"):
        store.delete("snap-000000000010-00001")
    with pytest.raises(ValueError, match="missing required fields"):
        store.write(b"x", {"step": 1})


def test_store_round_trips_a_scaled_size_blob():
    store = NatsSnapshotStore(FakeBusTransport())
    blob = np.random.default_rng(0).bytes(5 * 1024 * 1024)  # a mature scaled brain
    snapshot_id = store.write(blob, _metadata(100000, 40))
    assert store.read(snapshot_id) == blob


def test_tap_store_wrapper_delegates_the_whole_protocol():
    tap = NatsTap(FakeBusTransport(), run_id="t", **QUIET)
    wrapped = tap.wrap_store(InMemorySnapshotStore())
    assert isinstance(wrapped, SnapshotStore)
    snapshot_id = wrapped.write(b"blob", _metadata(10, 1))
    assert wrapped.read(snapshot_id) == b"blob"
    assert [i for i, _ in wrapped.list()] == [snapshot_id]
    wrapped.delete(snapshot_id)
    assert wrapped.list() == []
    assert tap.last_snapshot is not None  # the write was observed


# --- §5.1 the real binding's dependency grammar --------------------------------


def test_missing_nats_library_error_names_the_extra(monkeypatch):
    import pra.nats.transport as transport_module

    def raiser():
        raise ImportError("No module named 'nats'")

    monkeypatch.setattr(transport_module, "_import_nats", raiser)
    with pytest.raises(ImportError, match=r'pip install "poseres\[nats\]"'):
        transport_module.NatsTransport("nats://127.0.0.1:4222")
    from pra.nats import NatsTransport as exported  # the lazy re-export resolves

    assert exported is transport_module.NatsTransport
