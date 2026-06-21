"""T035 — determinism: byte-identical re-run; injected divergence is a hard FAIL."""

from __future__ import annotations

import pra.harness.runner as runner_mod
from pra.config import Config
from pra.harness.runner import check_determinism
from pra.telemetry.recorder import CheckpointReading, PerSeedRunSummary


def _small_config():
    return Config(
        seeds=(1,),
        warmup_episodes=3,
        n_cycles=2,
        episodes_per_cycle=1,
        steps_per_episode=15,
        horizon_checkpoints=(1, 2),
    )


def test_same_seed_twice_is_byte_identical():
    result = check_determinism(_small_config(), seed=1)
    assert result.verdict == "PASS"
    assert result.byte_diff_count == 0
    assert result.first_difference is None


def _summary(best_dim):
    return PerSeedRunSummary(
        seed=1,
        scoring_mode="predictive",
        mean_map_fraction=0.8,
        pred_error_early=0.5,
        pred_error_late=0.3,
        best_dim=best_dim,
        best_score=0.4,
        final_population=20,
        loss_fraction=0.0,
        observation_steps=1000,
        mean_population=15.0,
        checkpoints={1: CheckpointReading(best_dim, 20)},
        population_by_cycle=[10, 12],
        still_growing=False,
    )


def test_injected_divergence_is_reported_with_first_difference(monkeypatch):
    # Two runs that differ in a single field must be reported as a determinism
    # FAILURE pointing at the offending field — never averaged away.
    returns = iter([_summary(3), _summary(4)])

    class DivergentEngine:
        def __init__(self, *args, **kwargs):
            pass

        def run(self, seed, *, do_offline=True):
            return next(returns)

    monkeypatch.setattr(runner_mod, "Engine", DivergentEngine)
    result = check_determinism(_small_config(), seed=1)
    assert result.verdict == "FAIL"
    assert result.byte_diff_count > 0
    assert "best_dim" in result.first_difference
