"""T021 — capstone: at the validated reference config, T1-T6 all PASS (SC-005).

Reproduces the v4 reference behavior through the batched core. This runs the full
default suite (8 seeds, predictive + effort-only ablation), so it is the slowest
test by design — it is the authoritative go/no-go on the behavioral claims.
"""

from __future__ import annotations

import pytest

from pra.config import Config
from pra.harness.acceptance import PASS, evaluate_suite
from pra.harness.runner import run_suite


@pytest.fixture(scope="module")
def reference_tests():
    suite_run = run_suite(Config())
    assert suite_run.complete, f"seeds errored: {suite_run.failed_seeds}"
    return {t.id: t for t in evaluate_suite(suite_run)}


@pytest.mark.parametrize("test_id", ["T1", "T2", "T3", "T4", "T5", "T6"])
def test_reference_test_passes(reference_tests, test_id):
    verdict = reference_tests[test_id]
    assert verdict.verdict == PASS, f"{test_id} = {verdict.verdict} ({verdict.measured.note})"


def test_t4_holds_within_one_majority_at_every_checkpoint(reference_tests):
    t4 = reference_tests["T4"]
    assert t4.horizon_readings is not None and len(t4.horizon_readings) == 3
    for r in t4.horizon_readings:
        assert r.within_one_count > r.n_seeds // 2, (
            f"@{r.checkpoint}: only {r.within_one_count}/{r.n_seeds} within one"
        )


def test_t5_is_self_limiting_not_capped(reference_tests):
    t5 = reference_tests["T5"]
    assert t5.t5_detail is not None
    assert not any(t5.t5_detail.still_growing_per_seed)
    assert not t5.t5_detail.capped
    assert t5.t5_detail.final_population_mean < t5.t5_detail.max_frames
