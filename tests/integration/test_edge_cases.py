"""T022/T040 — edge cases: not-available, seed-error, warmup-births, capped."""

from __future__ import annotations

import pra.harness.runner as runner_mod
from pra.config import Config
from pra.core.engine import Engine
from pra.harness.acceptance import FAIL, NOT_AVAILABLE, _t2, _t5
from pra.harness.report import build_suite_report, render_text
from pra.harness.runner import SuiteRun, run_suite


def test_too_few_pred_samples_reports_not_available():
    # One short warmup episode yields < 50 early predictive-error samples.
    cfg = Config(
        warmup_episodes=1,
        n_cycles=1,
        episodes_per_cycle=1,
        steps_per_episode=20,
        horizon_checkpoints=(1,),
    )
    summary = Engine(cfg).run(1)
    assert summary.pred_error_early is None  # literally "not available", not a number
    verdict = _t2([summary], 1)
    assert verdict.verdict == NOT_AVAILABLE
    # rendered honestly as "not available", never a fabricated value.
    suite_run = SuiteRun(
        config=cfg,
        true_dim=cfg.true_dim,
        seeds=[1],
        predictive=[summary],
        ablation={},
        wall_clock_seconds=0.1,
    )
    text = render_text(build_suite_report(suite_run, [verdict]))
    assert "not available" in text


def test_seed_error_is_reported_not_silently_dropped(monkeypatch):
    real_run = Engine.run

    class FlakyEngine(Engine):
        def run(self, seed, *, do_offline=True):
            if seed == 3:
                raise RuntimeError("injected seed failure")
            return real_run(self, seed, do_offline=do_offline)

    monkeypatch.setattr(runner_mod, "Engine", FlakyEngine)
    cfg = Config(
        seeds=(1, 2, 3, 4),
        warmup_episodes=2,
        n_cycles=1,
        episodes_per_cycle=1,
        steps_per_episode=10,
        horizon_checkpoints=(1,),
    )
    suite_run = run_suite(cfg, with_ablation=False)
    assert 3 in suite_run.failed_seeds
    assert {s.seed for s in suite_run.predictive} == {1, 2, 4}
    assert not suite_run.complete
    text = render_text(build_suite_report(suite_run, []))
    assert "INCOMPLETE" in text and "[3]" in text


def test_warmup_births_not_counted_against_no_loss():
    # Frames are born during warmup (zero-start), but warmup losses are excluded:
    # post-warmup loss_fraction stays low even though population grew from zero.
    cfg = Config(
        warmup_episodes=10,
        n_cycles=3,
        episodes_per_cycle=2,
        steps_per_episode=30,
        horizon_checkpoints=(1, 2, 3),
    )
    summary = Engine(cfg).run(1)
    assert summary.final_population > 0  # frames were born (during warmup and after)
    assert summary.loss_fraction < 0.15  # post-warmup losses only


def test_capped_population_fails_self_limiting_and_is_marked_capped():
    # No soft eviction + a tiny hard cap pins the population at the cap (the hard
    # cap trims to max_frames, then the per-cycle spawn re-adds one). The bounded
    # clause fails (final >= max_frames) and it is reported capped, distinct from a
    # genuinely self-limiting population.
    cfg = Config(
        seeds=(1,),
        warmup_episodes=5,
        n_cycles=12,
        episodes_per_cycle=2,
        steps_per_episode=20,
        horizon_checkpoints=(1, 6, 12),
        max_frames=8,
        min_age_cycles=1,
        survive_threshold_base=100.0,  # nothing is ever over threshold -> no soft eviction
    )
    summary = Engine(cfg).run(1)
    assert summary.final_population >= cfg.max_frames  # pinned at the cap
    assert not summary.still_growing  # flat at the cap, not strictly increasing
    verdict = _t5([summary], cfg.max_frames, 1)
    assert verdict.verdict == FAIL
    assert verdict.t5_detail.capped is True
