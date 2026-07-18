"""Feature 014 — full engine runs over the FakeBusTransport: the observer
proof (byte-identity attached/absent), no-backpressure under outage and
overflow, boundary-exact pause/resume, snapshot round-trip + resume
equivalence through the object store, multi-stream attribution. No NATS
library, no server, nothing skipped."""

from __future__ import annotations

import json
import threading
import time

import numpy as np

from pra.config import Config
from pra.core.engine import Engine
from pra.nats import NatsSnapshotStore, NatsTap, subjects
from pra.nats.fake import FakeBusTransport
from pra.persistence.snapshot import FORMAT_VERSION
from pra.world.event_source import SensorimotorWorld

SMALL = dict(
    warmup_episodes=2,
    n_cycles=2,
    episodes_per_cycle=1,
    steps_per_episode=10,
    horizon_checkpoints=(1, 2),
)

QUIET = dict(census_interval=1e9)


def _attach(cfg: Config, tap: NatsTap, **engine_kwargs) -> Engine:
    return Engine(
        cfg, world_factory=tap.world_factory(), bus_factory=tap.bus_factory, **engine_kwargs
    )


# --- §2.1/§2.2: the observer proof ---------------------------------------------


def test_byte_identity_attached_vs_absent_reference_world():
    cfg = Config(**SMALL)
    bare = Engine(cfg).run(1).serialize()
    tap = NatsTap(FakeBusTransport(), run_id="t", **QUIET)
    tap.start()
    engine = _attach(cfg, tap)
    summary = engine.run(1)
    tap.finish(summary)
    assert summary.serialize() == bare
    assert tap.events_mirrored > 0  # the run really was observed


def test_byte_identity_attached_vs_absent_multistream_continuous():
    cfg = Config(**SMALL, n_streams=2, episode_mode="continuous")
    bare = Engine(cfg).run(1).serialize()
    tap = NatsTap(FakeBusTransport(), run_id="t", **QUIET)
    tap.start()
    summary = _attach(cfg, tap).run(1)
    tap.finish(summary)
    assert summary.serialize() == bare


def test_world_construction_draws_are_identical_under_the_wrapper():
    cfg = Config(**SMALL)
    rng_bare = np.random.default_rng(5)
    SensorimotorWorld(cfg, rng_bare)
    rng_tapped = np.random.default_rng(5)
    NatsTap(FakeBusTransport(), run_id="t", **QUIET).world_factory()(cfg, rng_tapped)
    assert rng_bare.bit_generator.state == rng_tapped.bit_generator.state


# --- §2.4: no backpressure ------------------------------------------------------


def test_transport_down_for_life_costs_nothing_but_counters():
    cfg = Config(**SMALL)
    bare = Engine(cfg).run(1).serialize()
    transport = FakeBusTransport()
    transport.set_down()
    tap = NatsTap(transport, run_id="t", drain_interval=0.005, **QUIET)
    tap.start()
    summary = _attach(cfg, tap).run(1)
    tap.finish(summary)
    assert summary.serialize() == bare
    assert transport.publish_failures > 0  # attempts were made, counted, dropped
    assert transport.journal == []


def test_overflow_drops_oldest_counts_and_never_blocks():
    cfg = Config(**SMALL)
    bare = Engine(cfg).run(1).serialize()
    transport = FakeBusTransport()
    # a stalled publisher: the pump sleeps far longer than the run lasts
    tap = NatsTap(transport, run_id="t", buffer_size=8, drain_interval=1e9, **QUIET)
    tap.start()
    summary = _attach(cfg, tap).run(1)
    tap.finish(summary)  # stop wakes the pump; the final drain publishes the tail
    assert summary.serialize() == bare
    assert tap.events_dropped > 0
    assert tap.events_dropped + len(transport.journal) - 1 == tap.events_mirrored + 1
    # (journal carries the tail + the completed status; started/mirror share the seq family)
    tail = [json.loads(p) for p in transport.published(subjects.step_subject("t"))]
    assert tail[-1]["step"] == 40  # the newest events survived (drop-oldest)


# --- §3.1: boundary-exact pause, byte-identical completion ----------------------


def test_pause_before_start_gates_the_first_reset_then_resumes_exactly():
    cfg = Config(**SMALL)
    bare = Engine(cfg).run(1).serialize()
    transport = FakeBusTransport()
    tap = NatsTap(transport, run_id="t", drain_interval=0.005, **QUIET)
    tap.start()
    tap.pause()
    engine = _attach(cfg, tap)
    box: dict = {}

    def run():
        box["summary"] = engine.run(1)

    thread = threading.Thread(target=run, daemon=True)
    thread.start()
    time.sleep(0.1)
    assert "summary" not in box and tap.steps == 0  # gated before the first boot
    assert transport.published(subjects.step_subject("t")) == []
    tap.resume()
    thread.join(timeout=30)
    tap.finish(box["summary"])
    assert box["summary"].serialize() == bare


class PacedWorld(SensorimotorWorld):
    """Identical draws, slower wall clock — the rover pacing precedent: gives a
    mid-run pause something to interrupt without changing a single byte."""

    def step(self, action):
        time.sleep(0.005)
        return super().step(action)


def test_pause_mid_run_quiesces_then_completes_byte_identical():
    cfg = Config(**SMALL)
    bare = Engine(cfg).run(1).serialize()
    transport = FakeBusTransport()
    tap = NatsTap(transport, run_id="t", drain_interval=0.001, **QUIET)

    paused_at: list[int] = []

    def pause_at_step_20(subject, payload):
        event = json.loads(payload)
        if event["step"] == 20 and not paused_at:
            paused_at.append(tap.pause())

    transport.subscribe(subjects.step_subject("t"), pause_at_step_20)
    tap.start()
    engine = Engine(
        cfg, world_factory=tap.world_factory(inner=PacedWorld), bus_factory=tap.bus_factory
    )
    box: dict = {}

    def run():
        box["summary"] = engine.run(1)

    thread = threading.Thread(target=run, daemon=True)
    thread.start()

    deadline = time.monotonic() + 30
    while not paused_at and time.monotonic() < deadline:
        time.sleep(0.005)
    assert paused_at, "the pause trigger never fired"
    # quiescence: the mirrored step count stops advancing while paused
    settled = tap.steps
    time.sleep(0.1)
    assert tap.steps <= settled + 1  # at most the in-flight step completed
    frozen = tap.steps
    time.sleep(0.1)
    assert tap.steps == frozen and "summary" not in box

    tap.resume()
    thread.join(timeout=30)
    tap.finish(box["summary"])
    assert box["summary"].serialize() == bare  # pause is schedule-relative


# --- §4.3: snapshot round-trip + resume equivalence through the object store ---


def test_engine_snapshots_through_the_object_store_and_resumes_equivalently():
    cfg = Config(**SMALL, snapshot_every_n_cycles=1)
    baseline = Engine(cfg).run(1)
    store = NatsSnapshotStore(FakeBusTransport())
    Engine(cfg, snapshot_store=store).run(1)
    assert len(store.list()) == 2  # one per cycle
    for snapshot_id, metadata in store.list():
        assert metadata["format_version"] == FORMAT_VERSION
        resumed = Engine(cfg).run(1, resume_from=store.read(snapshot_id))
        assert resumed.serialize() == baseline.serialize()


def test_snapshot_notices_and_control_fulfillment_during_a_live_run():
    cfg = Config(**SMALL, snapshot_every_n_cycles=1)
    transport = FakeBusTransport()
    tap = NatsTap(transport, run_id="t", drain_interval=0.005, **QUIET)
    inner = NatsSnapshotStore(transport)
    tap.start()
    engine = _attach(cfg, tap, snapshot_store=tap.wrap_store(inner))
    # capture the config through the public factory surface so the deferred
    # snapshot command is accepted before the run's own worlds exist
    tap.world_factory()(cfg, np.random.default_rng(99))

    replies: list[dict] = []
    tap._control.handle(
        subjects.to_bytes({"cmd": "snapshot"}), lambda b: replies.append(json.loads(b))
    )
    summary = engine.run(1)
    tap.finish(summary)

    assert summary.serialize() == Engine(cfg).run(1).serialize()  # still the observer
    assert replies and replies[0]["ok"], replies
    assert replies[0]["snapshot_id"] in {i for i, _ in inner.list()}
    notices = [json.loads(p) for p in transport.published(subjects.snapshot_subject("t"))]
    assert [n["cycle"] for n in notices] == [1, 2]
    assert {n["snapshot_id"] for n in notices} == {i for i, _ in inner.list()}


# --- §2.3 attribution: streams and episodes -------------------------------------


def test_multistream_attribution_by_construction_order():
    cfg = Config(**SMALL, n_streams=2, episode_mode="continuous")
    transport = FakeBusTransport()
    tap = NatsTap(transport, run_id="t", **QUIET)
    tap.start()
    summary = _attach(cfg, tap).run(1)
    tap.finish(summary)
    steps = [json.loads(p) for p in transport.published(subjects.step_subject("t"))]
    assert {s["stream"] for s in steps} == {0, 1}
    episodes = [json.loads(p) for p in transport.published(subjects.episode_subject("t"))]
    boots = [e for e in episodes if e["kind"] == "boot"]
    assert len(boots) == 2 and {b["stream"] for b in boots} == {0, 1}  # one boot per stream
    assert all(e["kind"] == "boot" for e in episodes)  # continuous: no resets ever
