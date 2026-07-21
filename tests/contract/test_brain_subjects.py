"""Feature 029 contract §1–§2 — the brain.* subject family: wire words,
metadata announcement + heartbeat, and canonical payload discipline.
Everything runs on the FakeBusTransport: no NATS library, no server."""

from __future__ import annotations

import json

import pytest

from pra.config import Config
from pra.core.engine import Engine
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

QUIET = dict(census_interval=1e9, view_heartbeat=1e9)  # publisher clocks off: determinism


def _tapped_rover_run(run_id: str = "t"):
    transport = FakeBusTransport()
    tap = NatsTap(transport, run_id=run_id, **QUIET)
    engine = Engine(
        cfg := Config(**SMALL),
        world_factory=tap.world_factory(inner=lambda c, rng: make_rover_body(c, rng)),
        bus_factory=tap.bus_factory,
    )
    tap.start()
    summary = engine.run(1)
    tap.finish(summary)
    assert cfg.obs_dim == 10  # the rover reference widths carried the run
    return transport, tap


# --- §1 the wire words ---------------------------------------------------------


def test_brain_subjects_are_run_scoped():
    assert subjects.brain_anatomy_subject("r1") == "pra.v1.run.r1.brain.anatomy"
    assert subjects.brain_frames_subject("r1") == "pra.v1.run.r1.brain.frames"
    assert subjects.brain_events_subject("r1") == "pra.v1.run.r1.brain.events"


def test_brain_subjects_validate_run_ids():
    for bad in ("", "a.b", "a b", 'a"b'):
        with pytest.raises(ValueError):
            subjects.brain_anatomy_subject(bad)


def test_discover_reply_advertises_the_brain_family():
    advertised = subjects.run_subjects("r1")
    assert advertised["brain_anatomy"] == subjects.brain_anatomy_subject("r1")
    assert advertised["brain_frames"] == subjects.brain_frames_subject("r1")
    assert advertised["brain_events"] == subjects.brain_events_subject("r1")


def test_brain_payloads_share_the_canonical_wire_form():
    payload = {"run": "r1", "seq": 3, "groups": []}
    assert subjects.from_bytes(subjects.to_bytes(payload)) == payload
    assert json.loads(subjects.to_bytes(payload)) == payload


# --- §2 metadata: announced at construction, heartbeat for late attachers ------


def test_anatomy_meta_is_announced_once_at_world_construction():
    transport, _ = _tapped_rover_run()
    metas = [json.loads(p) for p in transport.published(subjects.brain_anatomy_subject("t"))]
    assert len(metas) == 1  # heartbeat clock is off — the announce itself
    meta = metas[0]
    assert meta["run"] == "t" and isinstance(meta["seq"], int)
    assert [g["id"] for g in meta["groups"]] == ["rays", "compass", "gps", "bump"]
    assert meta["obs_dim"] == 10 and meta["n_actions"] == 4
    assert "time" not in meta and "timestamp" not in meta  # no wall-clock, ever
    # the announce precedes every step in the journal (attach-at-boot ordering)
    order = [s for s, _ in transport.journal]
    assert order.index(subjects.brain_anatomy_subject("t")) < order.index(
        subjects.step_subject("t")
    )


def test_anatomy_meta_heartbeat_republishes_for_late_attachers():
    transport, tap = _tapped_rover_run()
    tap._republish_brain_meta()  # publisher-thread method, driven synchronously
    metas = [json.loads(p) for p in transport.published(subjects.brain_anatomy_subject("t"))]
    assert len(metas) == 2
    assert metas[0]["groups"] == metas[1]["groups"]  # same declaration, latest seq
    assert metas[1]["seq"] >= metas[0]["seq"]


def test_worlds_without_a_declaration_publish_nothing_on_the_subject():
    transport = FakeBusTransport()
    tap = NatsTap(transport, run_id="bare", **QUIET)
    engine = Engine(Config(**SMALL), world_factory=tap.world_factory(), bus_factory=tap.bus_factory)
    tap.start()
    tap.finish(engine.run(1))
    assert transport.published(subjects.brain_anatomy_subject("bare")) == []
    tap._republish_brain_meta()  # heartbeat with nothing to say stays silent
    assert transport.published(subjects.brain_anatomy_subject("bare")) == []


def test_tapped_rover_journal_is_byte_deterministic():
    journal_a = _tapped_rover_run()[0].journal
    journal_b = _tapped_rover_run()[0].journal
    assert journal_a == journal_b
