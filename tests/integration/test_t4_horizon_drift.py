"""T032 — T4 cannot pass on a lucky single horizon (US2, SC-002).

A result that meets the within-one majority at an early checkpoint but drifts away
by a later one MUST be reported FAIL, and the per-seed spread MUST be shown at every
checkpoint. The verdict logic is exercised on engineered per-seed summaries whose
best_dim drifts with horizon — exactly the false-positive the prototype hit.
"""

from __future__ import annotations

from pra.harness.acceptance import FAIL, PASS, _t4, strict_majority
from pra.telemetry.recorder import CheckpointReading, PerSeedRunSummary


def _summary(seed, per_checkpoint):
    return PerSeedRunSummary(
        seed=seed,
        scoring_mode="predictive",
        mean_map_fraction=0.8,
        pred_error_early=0.5,
        pred_error_late=0.3,
        best_dim=per_checkpoint[max(per_checkpoint)],
        best_score=0.4,
        final_population=20,
        loss_fraction=0.0,
        observation_steps=1000,
        mean_population=15.0,
        checkpoints={c: CheckpointReading(bd, 20) for c, bd in per_checkpoint.items()},
        population_by_cycle=[10, 11, 12],
        still_growing=False,
    )


def test_early_pass_late_drift_is_reported_fail():
    true_dim = 3
    checkpoints = [18, 30, 50]
    # @18 and @30 hold the within-one majority; @50 drifts far away.
    summaries = [
        _summary(1, {18: 3, 30: 3, 50: 7}),
        _summary(2, {18: 2, 30: 3, 50: 8}),
        _summary(3, {18: 3, 30: 4, 50: 6}),
        _summary(4, {18: 4, 30: 3, 50: 1}),
        _summary(5, {18: 3, 30: 2, 50: 1}),
    ]
    verdict = _t4(summaries, true_dim, checkpoints, n=5)
    assert verdict.verdict == FAIL

    readings = {r.checkpoint: r for r in verdict.horizon_readings}
    # the spread is present at EVERY checkpoint (FR-003), never reduced to a mean.
    assert verdict.measured.mean is None
    assert readings[18].best_dim_per_seed == [3, 2, 3, 4, 3]
    assert readings[50].best_dim_per_seed == [7, 8, 6, 1, 1]
    # @18 passes the within-one majority; @50 does not -> overall FAIL.
    assert strict_majority(readings[18].within_one_count, 5)
    assert not strict_majority(readings[50].within_one_count, 5)


def test_consistent_within_one_passes_at_every_checkpoint():
    summaries = [
        _summary(1, {18: 3, 30: 3, 50: 4}),
        _summary(2, {18: 2, 30: 3, 50: 3}),
        _summary(3, {18: 3, 30: 4, 50: 3}),
    ]
    verdict = _t4(summaries, true_dim=3, checkpoints=[18, 30, 50], n=3)
    assert verdict.verdict == PASS
    for r in verdict.horizon_readings:
        assert strict_majority(r.within_one_count, 3)
