"""T023 — across-seed mean/std + the full per-seed best_dim spread (FR-003)."""

from __future__ import annotations

import math

from pra.harness.acceptance import _aggregate, _t4
from pra.telemetry.recorder import CheckpointReading, PerSeedRunSummary


def _summary(seed, best_dims_by_checkpoint):
    return PerSeedRunSummary(
        seed=seed,
        scoring_mode="predictive",
        mean_map_fraction=0.8,
        pred_error_early=0.5,
        pred_error_late=0.3,
        best_dim=best_dims_by_checkpoint[max(best_dims_by_checkpoint)],
        best_score=0.4,
        final_population=20,
        loss_fraction=0.0,
        observation_steps=1000,
        mean_population=15.0,
        checkpoints={c: CheckpointReading(bd, 20) for c, bd in best_dims_by_checkpoint.items()},
        population_by_cycle=[10, 12, 14],
        still_growing=False,
    )


def test_aggregate_returns_mean_std_and_full_per_seed():
    m = _aggregate([1.0, 2.0, 3.0])
    assert m.mean == 2.0
    assert math.isclose(m.std, math.sqrt(2.0 / 3.0))
    assert m.per_seed == [1.0, 2.0, 3.0]


def test_aggregate_with_all_missing_is_not_available():
    m = _aggregate([None, None])
    assert m.mean is None and m.std is None
    assert m.note == "not available"


def test_aggregate_keeps_missing_entries_in_per_seed():
    m = _aggregate([1.0, None, 3.0])
    assert m.mean == 2.0
    assert m.per_seed == [1.0, None, 3.0]  # the gap is visible, not dropped


def test_t4_reports_full_spread_and_never_a_mean():
    # 4 seeds; best_dim spreads differ per checkpoint.
    summaries = [
        _summary(1, {18: 3, 30: 3, 50: 4}),
        _summary(2, {18: 2, 30: 3, 50: 3}),
        _summary(3, {18: 3, 30: 3, 50: 1}),
        _summary(4, {18: 4, 30: 2, 50: 3}),
    ]
    verdict = _t4(summaries, true_dim=3, checkpoints=[18, 30, 50], n=4)
    # FR-003: the verdict carries the spread, never a mean.
    assert verdict.measured.mean is None
    assert verdict.measured.per_seed == [4, 3, 1, 3]  # last-checkpoint spread
    assert verdict.horizon_readings is not None
    r18 = verdict.horizon_readings[0]
    assert r18.best_dim_per_seed == [3, 2, 3, 4]  # full per-seed list, not reduced
    assert r18.within_one_count == 4 and r18.exact_count == 2
    # at @50 the spread is [4,3,1,3]; within-one of 3 = {4,3,3} = 3/4 (a majority).
    r50 = verdict.horizon_readings[2]
    assert r50.best_dim_per_seed == [4, 3, 1, 3]
    assert r50.within_one_count == 3
