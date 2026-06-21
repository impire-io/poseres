"""T046 — the only artifact written to disk is the requested report (FR-011).

The system is in-memory; no frame/model state is ever persisted. Running the CLI
with ``--json`` must create exactly the one report file and nothing else.
"""

from __future__ import annotations

import json

from pra.harness.cli import main


def _write_small_config(path):
    path.write_text(
        json.dumps(
            {
                "seeds": [1, 2],
                "warmup_episodes": 3,
                "n_cycles": 2,
                "episodes_per_cycle": 1,
                "steps_per_episode": 15,
                "horizon_checkpoints": [1, 2],
            }
        )
    )


def test_suite_writes_only_the_requested_report(tmp_path):
    cfg = tmp_path / "cfg.json"
    _write_small_config(cfg)
    out_dir = tmp_path / "out"
    report = out_dir / "report.json"

    code = main(["suite", "--config", str(cfg), "--json", str(report)])
    assert code == 0

    # exactly one file written under the output directory — no persisted state.
    assert list(out_dir.iterdir()) == [report]
    obj = json.loads(report.read_text())
    assert obj["schema_version"] == "1.0"
    assert obj["mode"] == "suite"
    assert {t["id"] for t in obj["tests"]} == {"T1", "T2", "T3", "T4", "T5", "T6"}


def test_suite_without_json_writes_nothing(tmp_path, capsys):
    cfg = tmp_path / "cfg.json"
    _write_small_config(cfg)
    before = set(tmp_path.iterdir())

    code = main(["suite", "--config", str(cfg)])
    assert code == 0
    # only the input config file exists; the run persisted no artifacts.
    assert set(tmp_path.iterdir()) == before
    assert "PRA VALIDATION" in capsys.readouterr().out
