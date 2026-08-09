"""Feature 040 — the event pathway end to end: the off path is inert (format
and behavior), the on path learns every executed transition, persists, and
resumes byte-identically."""

from __future__ import annotations

import dataclasses
import io
import json

import numpy as np

from pra.config import Config
from pra.core.engine import Engine
from pra.persistence.snapshot import decode
from pra.persistence.store import InMemorySnapshotStore


def _cfg(**overrides):
    base = dict(
        warmup_episodes=4,
        n_cycles=6,
        episodes_per_cycle=2,
        steps_per_episode=15,
        horizon_checkpoints=(3, 6),
        snapshot_every_n_cycles=2,
    )
    base.update(overrides)
    return Config(**base)


def _blob_keys(blob: bytes) -> tuple[set, dict]:
    with np.load(io.BytesIO(blob), allow_pickle=False) as archive:
        return set(archive.files), json.loads(str(archive["meta"]))


# --- the off path is inert ---------------------------------------------------


def test_off_blobs_carry_no_head_state():
    store = InMemorySnapshotStore()
    Engine(_cfg(), snapshot_store=store).run(3)
    blob = store.read(store.list()[0][0])
    files, meta = _blob_keys(blob)
    assert not any(k.startswith("eh__") for k in files)
    assert "event_head" not in meta
    assert "event_head" not in decode(blob).frame_store


def test_random_mode_behavior_is_untouched_by_the_learning_head():
    # The head learns but nothing reads it and it consumes no RNG: summaries
    # identical with the dial off and on.
    off = Engine(_cfg()).run(5)
    on = Engine(_cfg(event_head_eta=0.5)).run(5)
    assert on.serialize() == off.serialize()


def test_default_curiosity_policy_ignores_the_head():
    off = Engine(_cfg(policy_mode="curiosity")).run(5)
    on = Engine(_cfg(policy_mode="curiosity", event_head_eta=0.5)).run(5)
    assert on.serialize() == off.serialize()


# --- the on path learns, persists, resumes ----------------------------------


def test_head_learns_every_executed_transition_including_boundaries():
    # updates == observation steps in BOTH episode modes: the step-loop call
    # site sees every executed transition — in continuous mode that includes
    # the virtual episode boundaries (research D2's discriminating count: an
    # online_step-site head would show obs_steps minus one per episode).
    for mode in ("episodic", "continuous"):
        store = InMemorySnapshotStore()
        cfg = _cfg(event_head_eta=0.5, episode_mode=mode, snapshot_every_n_cycles=6)
        summary = Engine(cfg, snapshot_store=store).run(2)
        state = decode(store.read(store.list()[0][0]))
        assert state.frame_store["event_head"]["updates"] == summary.observation_steps


def test_resume_with_the_head_is_byte_identical():
    cfg = _cfg(policy_mode="curiosity", event_head_eta=0.5)
    baseline = Engine(cfg).run(7)
    store = InMemorySnapshotStore()
    Engine(cfg, snapshot_store=store).run(7)
    for snapshot_id, _meta in store.list():
        state = decode(store.read(snapshot_id))
        assert state.frame_store["event_head"]["updates"] > 0
        resumed = Engine(cfg).run(7, resume_from=store.read(snapshot_id))
        assert resumed.serialize() == baseline.serialize()


def test_head_off_blob_resumes_with_head_enabled_via_cold_start():
    # The G3-rerun usage: take a blob written without the head, enable the
    # dial on the config-in-force, resume — the head cold-starts (stated
    # refill) and the run proceeds.
    store = InMemorySnapshotStore()
    Engine(_cfg(policy_mode="curiosity"), snapshot_store=store).run(4)
    state = decode(store.read(store.list()[-1][0]))  # the earliest snapshot
    assert "event_head" not in state.frame_store
    enabled = dataclasses.replace(state, config=state.config.replace(event_head_eta=0.5))
    resumed = Engine(enabled.config).run(4, resume_from=enabled)
    assert resumed.observation_steps > state.obs_steps
