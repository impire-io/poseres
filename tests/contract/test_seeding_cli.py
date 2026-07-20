"""Brain-seeding CLI/report contract (feature 028, contracts/seeding-cli.md):
pilot reports calibration without bar verdicts; confirmatory decides B1/B2 and
the overall verdict; every reading carries `reached`; the JSON shape is stable."""

from __future__ import annotations

import json

from pra.config import Config
from pra.harness.cli import main
from pra.harness.seeding import SeedingParams, params_from_dict, run_seeding, to_json

# A tiny but real budget: small warmup + few cycles keeps the contract fast.
_FAST_BASE = Config(warmup_episodes=6, n_cycles=3, horizon_checkpoints=(3,), episodes_per_cycle=3)
_PARAMS = SeedingParams(
    n_pretrain=3, n_probe=4, theta_b=0.4, theta_c=0.4, w_smooth=50, base_config=_FAST_BASE
)


def test_pilot_reports_calibration_without_bars():
    result = run_seeding([1, 2], "pilot", _PARAMS)
    assert result.mode == "pilot"
    assert result.bars == []
    assert result.overall is None
    assert result.calibration is not None
    assert "suggested_theta_p0.5" in result.calibration


def test_confirmatory_decides_bars_and_overall():
    result = run_seeding([1, 2], "confirmatory", _PARAMS, do_hop2=False)
    names = {b.name for b in result.bars}
    assert names == {"B1", "B2"}
    for b in result.bars:
        assert b.verdict in ("PASS", "FAIL")
    assert result.overall in ("PASS", "FAIL")


def test_hop2_adds_c1_bar_and_compounding_margins():
    result = run_seeding([1, 2], "confirmatory", _PARAMS, do_hop2=True)
    assert {b.name for b in result.bars} == {"B1", "B2", "C1"}
    assert {"margin1", "marginM", "margin2", "delta"} <= set(result.margins)
    # map-C readings exist for all three arms and grew the body (n_censor > 0)
    c_arms = {r.arm for r in result.readings if r.map_label == "C"}
    assert c_arms == {"seeded", "fresh", "maturity"}
    assert result.overall in ("PASS", "FAIL")


def test_every_reading_carries_reached_and_censor():
    result = run_seeding([1, 2], "confirmatory", _PARAMS, do_hop2=False)
    assert result.readings
    for r in result.readings:
        assert isinstance(r.reached, bool)
        assert r.tau <= r.n_censor
        assert r.arm in ("seeded", "fresh", "maturity")


def test_margin_sign_convention_positive_is_seeded_faster():
    # tau is lower-better; margin = fresh - seeded, so a positive mean means the
    # seeded arm reached theta sooner (contract guarantee #4).
    result = run_seeding([1, 2, 3], "confirmatory", _PARAMS, do_hop2=False)
    m1 = result.margins["margin1"]
    assert m1.per_seed == [
        result_tau(result, "fresh", s) - result_tau(result, "seeded", s) for s in (1, 2, 3)
    ]


def result_tau(result, arm, seed):
    for r in result.readings:
        if r.arm == arm and r.seed == seed and r.map_label == "B":
            return r.tau
    raise AssertionError(f"no reading for {arm} seed {seed}")


def test_to_json_shape_is_stable():
    result = run_seeding([1, 2], "confirmatory", _PARAMS, do_hop2=False)
    doc = to_json(result)
    assert set(doc) >= {
        "mode",
        "seeds",
        "frozen",
        "readings",
        "margins",
        "reach_rates",
        "bars",
        "overall",
    }
    assert set(doc["frozen"]) == {"n_pretrain", "n_probe", "theta_b", "theta_c", "w_smooth"}
    assert set(doc["margins"]) == {"margin1", "marginM"}


def test_params_from_dict_splits_seeding_and_base_config():
    p = params_from_dict({"n_pretrain": 7, "theta_b": 0.25, "warmup_episodes": 9})
    assert p.n_pretrain == 7
    assert p.theta_b == 0.25
    assert p.base_config.warmup_episodes == 9  # unknown keys feed the base config


def test_cli_writes_json(tmp_path):
    cfg = tmp_path / "seed.json"
    cfg.write_text(
        json.dumps(
            {
                "n_pretrain": 3,
                "n_probe": 4,
                "theta_b": 0.4,
                "theta_c": 0.4,
                "w_smooth": 50,
                "warmup_episodes": 6,
                "n_cycles": 3,
                "horizon_checkpoints": [3],
                "episodes_per_cycle": 3,
            }
        )
    )
    out = tmp_path / "out.json"
    rc = main(
        [
            "seeding",
            "--mode",
            "confirmatory",
            "--seeds",
            "1,2",
            "--no-hop2",
            "--config",
            str(cfg),
            "--json",
            str(out),
        ]
    )
    assert rc == 0
    doc = json.loads(out.read_text())
    assert doc["mode"] == "confirmatory"
    assert doc["overall"] in ("PASS", "FAIL")
