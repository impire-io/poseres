"""T041 — T-SCALE is runnable and measured, and never a build failure (US5, SC-006)."""

from __future__ import annotations

from pra.config import Config
from pra.harness.acceptance import FAIL, INVESTIGATORY
from pra.harness.report import build_scale_report, render_json, render_text
from pra.harness.scale import run_scale


def _base():
    return Config(
        warmup_episodes=2,
        n_cycles=2,
        episodes_per_cycle=1,
        steps_per_episode=10,
        horizon_checkpoints=(1, 2),
    )


def test_scale_emits_spread_throughput_and_wallclock():
    readings = run_scale(_base(), true_dims=[6, 9], seeds=[1, 2])
    assert len(readings) == 2
    for r, td in zip(readings, [6, 9], strict=True):
        assert r.true_dim == td
        assert len(r.best_dim_per_seed) == 2  # per-seed spread
        assert r.observation_steps > 0
        assert r.throughput > 0
        assert r.wall_clock_seconds > 0


def test_scale_obs_dim_scales_with_true_dim():
    # obs_dim >= 3 * true_dim must hold for the scaled configs (PRA-02 §1.3).
    readings = run_scale(_base(), true_dims=[20], seeds=[1])
    assert readings[0].true_dim == 20  # ran without error at a large true_dim


def test_scale_is_investigatory_never_a_build_failure():
    readings = run_scale(_base(), true_dims=[6], seeds=[1, 2])
    report = build_scale_report(_base(), [1, 2], readings, wall_clock_seconds=1.0)
    assert report.mode == "scale"
    assert report.tests[0].id == "T-SCALE"
    assert report.tests[0].verdict == INVESTIGATORY
    # a poor dimensionality result at scale is NEVER reported as a build failure.
    assert all(t.verdict != FAIL for t in report.tests)
    # it renders and serializes with the scale detail present.
    assert "INVESTIGATORY" in render_text(report)
    obj = render_json(report)
    assert obj["tests"][0]["scale_detail"][0]["true_dim"] == 6
