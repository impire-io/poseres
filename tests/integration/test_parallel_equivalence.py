"""Parallel seed execution must be byte-identical to sequential (FR-010).

Seeds are independent runs; running them in worker processes may change
wall-clock only. Every per-seed summary — predictive and both ablations — must
serialize to exactly the same bytes either way, and the suite verdicts must
match.
"""

from __future__ import annotations

from pra.config import Config
from pra.harness.acceptance import evaluate_suite
from pra.harness.runner import run_suite
from pra.harness.scale import run_scale


def _small_config():
    return Config(
        seeds=(1, 2, 3),
        warmup_episodes=3,
        n_cycles=2,
        episodes_per_cycle=1,
        steps_per_episode=15,
        horizon_checkpoints=(1, 2),
    )


def test_parallel_suite_is_byte_identical_to_sequential():
    cfg = _small_config()
    seq = run_suite(cfg, workers=1)
    par = run_suite(cfg, workers=3)

    assert [s.seed for s in par.predictive] == [s.seed for s in seq.predictive]
    for a, b in zip(seq.predictive, par.predictive, strict=True):
        assert a.serialize() == b.serialize()
    for seed in cfg.seeds:
        assert seq.ablation[seed].serialize() == par.ablation[seed].serialize()
        assert seq.identity[seed].serialize() == par.identity[seed].serialize()

    # verdicts (which depend only on the summaries) are identical too
    v_seq = [(t.id, t.verdict) for t in evaluate_suite(seq)]
    v_par = [(t.id, t.verdict) for t in evaluate_suite(par)]
    assert v_seq == v_par


def test_parallel_scale_matches_sequential():
    base = Config(
        warmup_episodes=2,
        n_cycles=2,
        episodes_per_cycle=1,
        steps_per_episode=10,
        horizon_checkpoints=(1, 2),
    )
    seq = run_scale(base, true_dims=[6], seeds=[1, 2], workers=1)
    par = run_scale(base, true_dims=[6], seeds=[1, 2], workers=2)
    assert seq[0].best_dim_per_seed == par[0].best_dim_per_seed
    assert seq[0].observation_steps == par[0].observation_steps
