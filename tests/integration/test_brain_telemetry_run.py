"""Feature 029 — the brain family over a real engine run (fake transport):
per-frame rows agree with the aggregate census at every publication, and
the scores are the engine's own."""

from __future__ import annotations

import json

from pra.config import Config
from pra.core.engine import Engine
from pra.core.scorer import WeightedSumScorer
from pra.nats import NatsTap, subjects
from pra.nats.fake import FakeBusTransport

SMALL = dict(
    warmup_episodes=2,
    n_cycles=4,
    episodes_per_cycle=1,
    steps_per_episode=10,
    horizon_checkpoints=(1, 2),
)

QUIET = dict(census_interval=1e9, view_heartbeat=1e9)


def _run_with_periodic_census(cfg: Config, every: int = 20):
    """A tapped run that drives the census synchronously mid-run: same thread
    as the store's writer, so every publication reads settled state."""
    transport = FakeBusTransport()
    tap = NatsTap(transport, run_id="t", **QUIET)

    inner_factory = tap.world_factory()

    def factory(config, rng):
        world = inner_factory(config, rng)
        original_step = world.step

        def step(action):
            obs = original_step(action)
            if tap.steps and tap.steps % every == 0:
                tap._publish_census()
            return obs

        world.step = step
        return world

    engine = Engine(cfg, world_factory=factory, bus_factory=tap.bus_factory)
    tap.start()
    summary = engine.run(1)
    tap._publish_census()  # one final settled reading
    tap.finish(summary)
    return transport, tap, summary


def test_frame_rows_agree_with_every_census():
    cfg = Config(**SMALL)
    transport, tap, summary = _run_with_periodic_census(cfg)

    censuses = [json.loads(p) for p in transport.published(subjects.census_subject("t"))]
    frames = [json.loads(p) for p in transport.published(subjects.brain_frames_subject("t"))]
    assert len(censuses) >= 3, "the run must have produced several mid-run censuses"
    assert len(frames) == len(censuses)  # one rows payload per census, always

    for census, frame in zip(censuses, frames, strict=True):
        assert frame["seq"] == census["seq"]  # same walk, same stamp
        assert frame["population"] == census["population"] == len(frame["rows"])
        best_row = min(frame["rows"], key=lambda r: (r["score"], r["id"]))
        assert frame["best_frame"] == best_row["id"]
        assert census["best_dim"] == best_row["dim"]
        ids = [r["id"] for r in frame["rows"]]
        assert ids == sorted(ids)  # the store's ascending-id order

    final = frames[-1]
    assert final["population"] == summary.final_population


def test_lifecycle_events_are_exactly_once_ordered_and_reconcile():
    # a small ceiling forces churn: spawns every cycle, cap evictions to match
    cfg = Config(**SMALL, max_frames=4)
    transport, tap, summary = _run_with_periodic_census(cfg)

    events = [json.loads(p) for p in transport.published(subjects.brain_events_subject("t"))]
    assert events, "the run must have produced lifecycle events"
    spawns = [e for e in events if e["event"] == "spawn"]
    evicts = [e for e in events if e["event"] == "evict"]
    assert evicts, "the ceiling must have forced at least one eviction"

    # exactly once, in mirror order
    seqs = [e["seq"] for e in events]
    assert seqs == sorted(seqs) and len(seqs) == len(set(seqs))
    assert tap.events_dropped == 0

    # reconciliation from boot: spawn includes boot registration (contract §2.3)
    assert len(spawns) - len(evicts) == summary.final_population

    # per-frame sanity: a frame's history alternates spawn, evict, spawn, ...
    history: dict[int, list[str]] = {}
    for e in events:
        history.setdefault(e["frame"], []).append(e["event"])
    for kinds in history.values():
        assert kinds[0] == "spawn"
        assert all(a != b for a, b in zip(kinds, kinds[1:], strict=False))

    # steps stamps are monotone (the run's own counter, no wall clock)
    steps = [e["steps"] for e in events]
    assert steps == sorted(steps)
    assert all(set(e) == {"run", "seq", "event", "frame", "steps"} for e in events)


def test_mid_run_attach_reconciles_from_the_census():
    cfg = Config(**SMALL, max_frames=4)
    transport, _, summary = _run_with_periodic_census(cfg)
    censuses = [json.loads(p) for p in transport.published(subjects.census_subject("t"))]
    events = [json.loads(p) for p in transport.published(subjects.brain_events_subject("t"))]
    attach = censuses[len(censuses) // 2]  # a mid-run attacher's first census
    later = [e for e in events if e["seq"] > attach["seq"]]
    delta = sum(1 if e["event"] == "spawn" else -1 for e in later)
    assert attach["population"] + delta == summary.final_population


def test_engine_outputs_are_identical_with_and_without_the_tap_bus():
    cfg = Config(**SMALL, max_frames=4)
    plain = Engine(cfg).run(1).serialize()
    _, _, tapped_summary = _run_with_periodic_census(cfg)
    assert tapped_summary.serialize() == plain


def test_row_scores_are_the_engine_scorers_own():
    cfg = Config(**SMALL)
    transport, tap, _ = _run_with_periodic_census(cfg)
    scorer = WeightedSumScorer(cfg)
    final = json.loads(transport.published(subjects.brain_frames_subject("t"))[-1])
    states = {s.frame_id: s for s in tap._store.frame_states()}
    for row in final["rows"]:
        s = states[row["id"]]
        expected = float(scorer.combine(s.recon_err_ema, s.pred_err_ema, s.effort_ema, s.dim))
        assert row["score"] == expected
        assert (row["dim"], row["age"], row["cand"]) == (s.dim, s.age_cycles, s.is_candidate)
        assert (row["recon"], row["pred"], row["effort"]) == (
            s.recon_err_ema,
            s.pred_err_ema,
            s.effort_ema,
        )
