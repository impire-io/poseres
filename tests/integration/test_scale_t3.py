"""T3 at scale (ROADMAP A2) — the ablation triad runs per true_dim under the
scaled ecology, judged by the exact reference criterion, investigatory context.

Small budgets: these tests check the plumbing (triad joined by seed, one
evaluator, report shape, CLI surface), never the science — the measured
verdicts at the real protocol live in the trail document.
"""

from __future__ import annotations

import json

from pra.config import Config
from pra.harness.acceptance import evaluate_t3, evaluate_t3_scaled
from pra.harness.cli import main
from pra.harness.report import build_scale_t3_report, render_json, render_text
from pra.harness.runner import ABLATION_SEED_OFFSET, IDENTITY_SEED_OFFSET, run_suite
from pra.harness.scale import run_scale_t3


def _base():
    return Config(
        warmup_episodes=2,
        n_cycles=2,
        episodes_per_cycle=1,
        steps_per_episode=10,
        horizon_checkpoints=(1, 2),
    )


def test_quartet_runs_per_dim_and_joins_by_seed():
    results = run_scale_t3(_base(), true_dims=[6, 9], seeds=[1, 2])
    assert [td for td, _run in results] == [6, 9]
    for td, run in results:
        # the scaled config was used for every arm
        assert run.config.true_dim == td
        assert run.config.obs_dim >= 3 * td
        assert run.config.score_window_steps > 0 and run.config.weight_norm_cap > 0
        # quartet present and keyed by the base seed (offsets stay internal)
        assert [s.seed for s in run.predictive] == [1, 2]
        assert set(run.ablation) == {1, 2} and set(run.identity) == {1, 2}
        assert set(run.matched) == {1, 2}
        assert run.ablation[1].seed == 1 + ABLATION_SEED_OFFSET
        assert run.identity[1].seed == 1 + IDENTITY_SEED_OFFSET
        assert run.ablation[1].scoring_mode == "effort_only"
        assert run.identity[1].scoring_mode == "identity"
        # the churn-matched arm: predictive training on the identity arm's world
        assert run.matched[1].seed == 1 + IDENTITY_SEED_OFFSET
        assert run.matched[1].scoring_mode == "predictive"


def test_scaled_t3_uses_the_reference_evaluator():
    results = run_scale_t3(_base(), true_dims=[6], seeds=[1, 2])
    verdict = evaluate_t3(results[0][1])
    assert verdict.id == "T3"
    assert verdict.verdict in {"PASS", "FAIL", "NOT_AVAILABLE"}


def test_amended_scaled_evaluator_pairs_matched_vs_identity():
    results = run_scale_t3(_base(), true_dims=[6], seeds=[1, 2])
    run = results[0][1]
    verdict = evaluate_t3_scaled(run)
    assert verdict.id == "T3"
    assert verdict.verdict in {"PASS", "FAIL", "NOT_AVAILABLE"}
    assert "churn-matched" in verdict.measured.note
    assert "as-written" in verdict.measured.note
    # the reported measure is the paired margin: matched − identity, per seed
    expected = [
        run.matched[s].improvement - run.identity[s].improvement
        for s in (1, 2)
        if run.matched[s].improvement is not None and run.identity[s].improvement is not None
    ]
    present = [m for m in verdict.measured.per_seed if m is not None]
    assert present == expected


def test_proposal_factory_default_leaves_run_suite_unchanged():
    # run_suite with no factory must produce byte-identical summaries to the
    # pre-change path (the validated default); the factory arg is opt-in only.
    cfg = _base().replace(seeds=(1,))
    a = run_suite(cfg, with_ablation=True)
    b = run_suite(cfg, with_ablation=True, proposal_factory=None)
    assert a.predictive[0].serialize() == b.predictive[0].serialize()
    assert a.ablation[1].serialize() == b.ablation[1].serialize()
    assert a.identity[1].serialize() == b.identity[1].serialize()


def test_scale_t3_report_shape_and_rendering():
    base = _base()
    results = run_scale_t3(base, true_dims=[6, 9], seeds=[1, 2])
    report = build_scale_t3_report(base, [1, 2], results, wall_clock_seconds=1.0)
    assert report.mode == "scale-t3"
    assert [t.id for t in report.tests] == ["T3@td=6", "T3@td=9"]
    detail = report.run_metadata["t3_scale_detail"]
    assert [d["true_dim"] for d in detail] == [6, 9]
    for d in detail:
        assert len(d["per_seed"]) == 2
        for row in d["per_seed"]:
            assert set(row) == {
                "seed",
                "predictive_improvement",
                "effort_only_improvement",
                "identity_improvement",
                "matched_improvement",
                "margin_vs_effort",
                "margin_vs_identity",
                "margin_matched_vs_identity",
                "predictive_best_dim",
            }
    text = render_text(report)
    assert "T3 quartet @ true_dim=6" in text
    assert "paired-margin" in text
    obj = render_json(report)
    assert obj["mode"] == "scale-t3"
    assert obj["run_metadata"]["t3_scale_detail"][0]["true_dim"] == 6


def test_cli_scale_t3_is_investigatory_and_writes_report(tmp_path, capsys):
    cfg = tmp_path / "cfg.json"
    cfg.write_text(
        json.dumps(
            {
                "seeds": [1, 2],
                "warmup_episodes": 2,
                "n_cycles": 2,
                "episodes_per_cycle": 1,
                "steps_per_episode": 10,
                "horizon_checkpoints": [1, 2],
            }
        )
    )
    report = tmp_path / "out" / "report.json"
    code = main(
        [
            "scale",
            "--t3",
            "--true-dims",
            "6",
            "--seeds",
            "1,2",
            "--config",
            str(cfg),
            "--json",
            str(report),
        ]
    )
    # investigatory: never a build failure, whatever the verdicts
    assert code == 0
    out = capsys.readouterr().out
    assert "T3@td=6" in out
    obj = json.loads(report.read_text())
    assert obj["mode"] == "scale-t3"
    assert {t["id"] for t in obj["tests"]} == {"T3@td=6"}
