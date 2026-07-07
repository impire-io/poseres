"""T013 — US2: the validated core is untouched under the pinned random baseline."""

from __future__ import annotations

import json

from pra.config import Config
from pra.core.engine import Engine
from pra.harness.acceptance import evaluate_suite
from pra.harness.runner import check_determinism, run_suite


def test_reference_seed_reproduces_validated_build_values():
    # The recorded seed-1 trajectory of the validated build (FR-008, SC-003).
    s = Engine(Config()).run(1)
    assert round(s.pred_error_early, 4) == 0.4465
    assert round(s.pred_error_late, 4) == 0.1574
    assert round(s.mean_map_fraction, 3) == 0.869
    readings = {c: (r.best_dim, r.population_size) for c, r in s.checkpoints.items()}
    assert readings == {18: (3, 19), 30: (3, 24), 50: (4, 27)}


def test_baseline_summary_carries_no_agency_fields():
    cfg = Config(
        warmup_episodes=3,
        n_cycles=2,
        episodes_per_cycle=1,
        steps_per_episode=10,
        horizon_checkpoints=(1, 2),
    )
    s = Engine(cfg).run(1)
    assert s.agency is None
    obj = json.loads(s.serialize())
    assert "agency" not in obj  # canonical form byte-compatible with the validated build


def test_determinism_check_unchanged():
    cfg = Config(
        seeds=(1,),
        warmup_episodes=3,
        n_cycles=2,
        episodes_per_cycle=1,
        steps_per_episode=15,
        horizon_checkpoints=(1, 2),
    )
    assert check_determinism(cfg, seed=1).verdict == "PASS"


def test_suite_emits_exactly_t1_to_t6():
    cfg = Config(
        seeds=(1, 2),
        warmup_episodes=2,
        n_cycles=2,
        episodes_per_cycle=1,
        steps_per_episode=10,
        horizon_checkpoints=(1, 2),
    )
    suite_run = run_suite(cfg, workers=1)
    ids = [t.id for t in evaluate_suite(suite_run)]
    assert ids == ["T1", "T2", "T3", "T4", "T5", "T6"]  # no T7 in the regression gate
