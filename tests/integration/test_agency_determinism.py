"""T010 — US1: the agent runs end-to-end, value finite from step one, reproducible."""

from __future__ import annotations

import json

import numpy as np

from pra.config import Config
from pra.core.engine import Engine
from pra.harness.agency import run_agency


def _small_config(**overrides):
    base = dict(
        seeds=(1, 2),
        warmup_episodes=3,
        n_cycles=2,
        episodes_per_cycle=1,
        steps_per_episode=15,
        horizon_checkpoints=(1, 2),
    )
    base.update(overrides)
    return Config(**base)


def test_curiosity_run_completes_with_finite_telemetry():
    cfg = _small_config(policy_mode="curiosity")
    summary = Engine(cfg).run(1)
    a = summary.agency
    assert a is not None
    for key in (
        "value_signal_mean",
        "value_signal_final",
        "learning_progress_mean",
        "novelty_mean",
        "directed_fraction",
    ):
        assert np.isfinite(a[key]), key
    # novelty operates from the very first step (empty memory -> 1.0), so the
    # value signal exists from step one and its mean is strictly positive.
    assert a["value_signal_mean"] > 0.0
    assert 0.0 <= a["directed_fraction"] <= 1.0


def test_curiosity_rerun_is_byte_identical():
    cfg = _small_config(policy_mode="curiosity")
    a = Engine(cfg).run(3)
    b = Engine(cfg).run(3)
    assert a.serialize() == b.serialize()


def test_agency_runner_pairs_arms_by_seed():
    cfg = _small_config()
    run = run_agency(cfg, workers=1)
    assert [s.seed for s in run.curious] == [1, 2]
    assert [s.seed for s in run.random] == [1, 2]
    # the curious arm carries agency telemetry; the pinned random arm does not.
    assert all(s.agency is not None for s in run.curious)
    assert all(s.agency is None for s in run.random)
    # agency block serializes with fixed keys (JSON round-trip sanity)
    obj = json.loads(run.curious[0].serialize())
    assert set(obj["agency"]) == {
        "value_signal_mean",
        "value_signal_final",
        "learning_progress_mean",
        "novelty_mean",
        "directed_fraction",
    }


def test_agency_runner_parallel_matches_sequential():
    cfg = _small_config()
    seq = run_agency(cfg, workers=1)
    par = run_agency(cfg, workers=2)
    for a, b in zip(seq.curious + seq.random, par.curious + par.random, strict=True):
        assert a.serialize() == b.serialize()
