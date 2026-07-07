"""T014 — US3: the T7 verdict is honest — majority rule, per-seed spread, both paths."""

from __future__ import annotations

from pra.config import Config
from pra.harness.acceptance import FAIL, PASS, evaluate_t7
from pra.harness.agency import AgencyRun, run_agency
from pra.harness.report import build_agency_report, render_json, render_text
from pra.telemetry.recorder import PerSeedRunSummary


def _summary(seed, early, late, agency=None):
    return PerSeedRunSummary(
        seed=seed,
        scoring_mode="predictive",
        mean_map_fraction=0.8,
        pred_error_early=early,
        pred_error_late=late,
        best_dim=3,
        best_score=0.4,
        final_population=20,
        loss_fraction=0.0,
        observation_steps=1000,
        mean_population=15.0,
        checkpoints={},
        population_by_cycle=[10, 11],
        still_growing=False,
        agency=agency,
    )


def _agency_block():
    return {
        "value_signal_mean": 0.2,
        "value_signal_final": 0.1,
        "learning_progress_mean": 0.05,
        "novelty_mean": 0.15,
        "directed_fraction": 0.5,
    }


def _run(pairs):
    seeds = list(range(1, len(pairs) + 1))
    curious = [
        _summary(s, early, late, agency=_agency_block())
        for s, (early, late, _, _) in zip(seeds, pairs, strict=True)
    ]
    random_ = [
        _summary(s, early, late) for s, (_, _, early, late) in zip(seeds, pairs, strict=True)
    ]
    return AgencyRun(
        config=Config(seeds=tuple(seeds)),
        seeds=seeds,
        curious=curious,
        random=random_,
    )


def test_t7_passes_on_statistical_equivalence():
    # (curious_early, curious_late, random_early, random_late)
    # Mixed small margins around zero: equivalent arms — noninferior -> PASS.
    run = _run(
        [
            (0.5, 0.20, 0.5, 0.25),  # margin +0.05
            (0.5, 0.30, 0.5, 0.30),  # margin 0
            (0.5, 0.28, 0.5, 0.25),  # margin -0.03
        ]
    )
    verdict = evaluate_t7(run)
    assert verdict.verdict == PASS
    assert "strictly better in 1/3" in verdict.measured.note
    assert verdict.measured.per_seed is not None and len(verdict.measured.per_seed) == 3


def test_t7_fails_honestly_when_curious_is_systematically_worse():
    run = _run(
        [
            (0.5, 0.30, 0.5, 0.20),  # -0.10
            (0.5, 0.37, 0.5, 0.25),  # -0.12
            (0.5, 0.33, 0.5, 0.25),  # -0.08
        ]
    )
    verdict = evaluate_t7(run)
    assert verdict.verdict == FAIL
    report = build_agency_report(run, verdict)
    text = render_text(report)
    assert "FAIL" in text
    assert "margin" in text  # the per-seed table is rendered, not hidden
    obj = render_json(report)
    assert obj["mode"] == "agency"
    assert len(obj["run_metadata"]["t7_per_seed"]) == 3


def test_t7_end_to_end_on_a_small_real_config():
    cfg = Config(
        seeds=(1, 2),
        warmup_episodes=3,
        n_cycles=2,
        episodes_per_cycle=1,
        steps_per_episode=15,
        horizon_checkpoints=(1, 2),
    )
    run = run_agency(cfg, workers=1)
    verdict = evaluate_t7(run)
    assert verdict.id == "T7"
    assert verdict.verdict in ("PASS", "FAIL", "NOT_AVAILABLE")  # honest, whatever it is
    text = render_text(build_agency_report(run, verdict))
    assert "curious improvement" in text
