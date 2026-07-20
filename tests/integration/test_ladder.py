"""Ladder integration — degenerate byte-identity, determinism, the rung
runners, and the CLI (feature 005; FR-005/FR-006/FR-010/FR-012).

Small budgets throughout: these tests check the instrument, never the
science — recorded results live in hq/02-DESIGN/validate/LADDER-CRITERIA.md.
"""

from __future__ import annotations

import json

import pytest

from pra.config import Config
from pra.core.engine import Engine
from pra.harness.cli import main
from pra.harness.ladder import run_ladder
from pra.harness.report import build_ladder_report, render_json, render_text
from pra.harness.runner import run_suite
from pra.world.ladder import make_world

SMALL = dict(
    warmup_episodes=2,
    n_cycles=2,
    episodes_per_cycle=1,
    steps_per_episode=10,
    horizon_checkpoints=(1, 2),
)


def _summary(cfg: Config, seed: int = 1) -> str:
    return Engine(cfg, world_factory=make_world).run(seed).serialize()


# --- degenerate byte-identity per rung (FR-012) ------------------------------


@pytest.mark.parametrize(
    "world_kw",
    [
        dict(world="nonuniform"),
        dict(world="compositional"),
        dict(world="distractor"),
    ],
    ids=["l1", "l2", "l3"],
)
def test_degenerate_dial_is_byte_identical_to_reference(world_kw):
    reference = Engine(Config(**SMALL)).run(1).serialize()
    degenerate = _summary(Config(**SMALL, **world_kw))
    assert degenerate == reference


# --- determinism on non-degenerate rungs (FR-005) ----------------------------


@pytest.mark.parametrize(
    "world_kw",
    [
        dict(world="nonuniform", region_noise_std=0.6),
        dict(world="compositional", true_dim=4, obs_dim=12, factor_dims=(2, 2)),
        dict(
            world="distractor",
            obs_dim=14,
            distractor_dim=2,
            distractor_channels=4,
            distractor_mode="noise",
        ),
    ],
    ids=["l1", "l2", "l3"],
)
def test_nondegenerate_rung_runs_are_deterministic(world_kw):
    cfg = Config(**SMALL, **world_kw)
    assert _summary(cfg) == _summary(cfg)


# --- run_suite world_factory default is byte-identical (FR-006) --------------


def test_run_suite_world_factory_default_unchanged():
    cfg = Config(**SMALL, seeds=(1,))
    a = run_suite(cfg, with_ablation=True)
    b = run_suite(cfg, with_ablation=True, world_factory=None)
    assert a.predictive[0].serialize() == b.predictive[0].serialize()


# --- the rung runners produce readings and verdicts ---------------------------


def test_run_ladder_produces_rows_and_verdicts_per_dial_set():
    base = Config(**SMALL, seeds=(1, 2))
    results = run_ladder(base, rungs=("l1", "l2", "l3"), seeds=[1, 2])
    # default dial grid: 2 (L1) + 2 (L2) + 2 (L3)
    assert [r.rung for r in results] == ["l1", "l1", "l2", "l2", "l3", "l3"]
    for r in results:
        assert r.verdict.verdict in {"PASS", "FAIL"}
        assert len(r.rows) == 2
    l1 = results[0]
    assert {"occupancy", "twin_best_dim"} <= set(l1.rows[0])
    l2 = results[2]
    assert {"paired_margin", "census"} <= set(l2.rows[0])
    l3 = results[4]
    assert set(l3.rows[0]["checkpoints"]) == {"1", "2"}


def test_base_config_dials_override_the_default_grid():
    base = Config(**SMALL, world="nonuniform", region_noise_std=0.3, seeds=(1,))
    results = run_ladder(base, rungs=("l1",), seeds=[1])
    assert len(results) == 1
    assert results[0].label == "L1@noise=0.3"
    assert results[0].config.region_noise_std == 0.3


# --- report + CLI (FR-009/FR-010) ---------------------------------------------


def test_ladder_report_renders_and_serializes():
    base = Config(**SMALL, seeds=(1, 2))
    results = run_ladder(base, rungs=("l1",), seeds=[1, 2])
    report = build_ladder_report(base, [1, 2], results, wall_clock_seconds=1.0)
    assert report.mode == "ladder"
    text = render_text(report)
    assert "L1@noise=0.2" in text and "occupancy" in text
    obj = render_json(report)
    assert obj["run_metadata"]["ladder_detail"][0]["rung"] == "l1"


def test_cli_ladder_is_investigatory_and_writes_one_artifact(tmp_path, capsys):
    cfg = tmp_path / "cfg.json"
    cfg.write_text(
        json.dumps(
            {
                "seeds": [1, 2],
                **{k: v for k, v in SMALL.items() if k != "horizon_checkpoints"},
                "horizon_checkpoints": [1, 2],
            }
        )
    )
    out = tmp_path / "out" / "ladder.json"
    code = main(["ladder", "--rungs", "l1,l3", "--config", str(cfg), "--json", str(out)])
    assert code == 0  # verdicts are data, never a build failure
    text = capsys.readouterr().out
    assert "PRA VALIDATION — mode: ladder" in text
    assert list(out.parent.iterdir()) == [out]  # the one disk artifact
    obj = json.loads(out.read_text())
    assert obj["mode"] == "ladder"
    assert {t["id"] for t in obj["tests"]} == {
        "L1@noise=0.2",
        "L1@noise=0.8",
        "L3@structured",
        "L3@noise",
    }
