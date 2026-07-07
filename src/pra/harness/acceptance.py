"""Acceptance evaluators T1-T6 + T-SCALE (PRA-02 §4, data-model §5).

Each test binds a claim, an exact criterion, a measure, and a verdict. The honest-
summary rules are structural: T4 carries the full per-seed ``best_dim`` spread at
every checkpoint and is never reduced to a mean; T5 carries the per-seed
still-growing flag, not just a final count; a seed that errored is surfaced, never
silently dropped.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

__all__ = [
    "Measured",
    "HorizonReading",
    "T5Detail",
    "ScaleReading",
    "AcceptanceVerdict",
    "VerdictReport",
    "PASS",
    "FAIL",
    "INVESTIGATORY",
    "NOT_AVAILABLE",
    "evaluate_suite",
    "evaluate_t7",
]

PASS = "PASS"
FAIL = "FAIL"
INVESTIGATORY = "INVESTIGATORY"
NOT_AVAILABLE = "NOT_AVAILABLE"


def strict_majority(count: int, n: int) -> bool:
    return count > n // 2


@dataclass
class Measured:
    mean: float | None = None
    std: float | None = None
    per_seed: list | None = None
    note: str | None = None


@dataclass
class HorizonReading:
    checkpoint: int
    best_dim_per_seed: list[int]
    within_one_count: int
    exact_count: int
    n_seeds: int


@dataclass
class T5Detail:
    final_population_mean: float
    final_population_std: float
    max_frames: int
    still_growing_per_seed: list[bool]
    capped: bool


@dataclass
class ScaleReading:
    true_dim: int
    best_dim_per_seed: list[int]
    observation_steps: int
    throughput: float
    wall_clock_seconds: float


@dataclass
class AcceptanceVerdict:
    id: str
    claim: str
    criterion: str
    verdict: str
    measured: Measured
    horizon_readings: list[HorizonReading] | None = None
    t5_detail: T5Detail | None = None
    scale_detail: list[ScaleReading] | None = None


@dataclass
class VerdictReport:
    mode: str
    run_metadata: dict
    tests: list[AcceptanceVerdict]
    determinism_check: dict | None = None
    for_debugging_only: bool = False
    scale_detail: list[ScaleReading] = field(default_factory=list)


def _aggregate(values: list[float | None]) -> Measured:
    present = [v for v in values if v is not None]
    if not present:
        return Measured(mean=None, std=None, per_seed=values, note="not available")
    return Measured(mean=float(np.mean(present)), std=float(np.std(present)), per_seed=list(values))


# --- individual evaluators -------------------------------------------------
def _t1(predictive, n) -> AcceptanceVerdict:
    measured = _aggregate([s.mean_map_fraction for s in predictive])
    verdict = PASS if (measured.mean is not None and measured.mean < 0.99) else FAIL
    return AcceptanceVerdict(
        "T1",
        "Sparsity by pull — frames map only what they explain, not everything.",
        "mean map_fraction < 0.99",
        verdict,
        measured,
    )


def _t2(predictive, n) -> AcceptanceVerdict:
    improvements = [s.improvement for s in predictive]
    both = [
        (s.pred_error_early, s.pred_error_late)
        for s in predictive
        if s.pred_error_early is not None and s.pred_error_late is not None
    ]
    n_fell = sum(1 for e, latev in both if latev < e)
    measured = _aggregate(improvements)
    measured.note = f"late < early in {n_fell}/{n} seeds"
    if not both:
        verdict = NOT_AVAILABLE
    else:
        verdict = PASS if strict_majority(n_fell, n) else FAIL
    return AcceptanceVerdict(
        "T2",
        "Prediction error falls — the system learns the world (honest obs space).",
        "predictive error late < early in a majority of seeds",
        verdict,
        measured,
    )


def _margins_vs(predictive, baseline_by_seed) -> tuple[list[float | None], int, int]:
    margins: list[float | None] = []
    n_better = 0
    comparable = 0
    for s in predictive:
        b = baseline_by_seed.get(s.seed)
        if b is None or s.improvement is None or b.improvement is None:
            margins.append(None)
            continue
        comparable += 1
        margin = s.improvement - b.improvement
        margins.append(margin)
        if margin > 0:
            n_better += 1
    return margins, n_better, comparable


def _t3(predictive, ablation, identity, n) -> AcceptanceVerdict:
    """Two clauses, both required (PRA-02 §2): predictive improvement must beat
    the effort-only (zero-pull) ablation AND the identity (learned-persistence)
    ablation in a strict majority of seeds. The identity clause is the strong
    claim — "the system predicts better than assuming nothing changes" — and is
    the reported margin, being the binding one."""
    margins_e, n_effort, comp_e = _margins_vs(predictive, ablation)
    margins_i, n_ident, comp_i = _margins_vs(predictive, identity)
    measured = _aggregate(margins_i if comp_i else margins_e)
    measured.note = (
        f"predictive beat effort-only in {n_effort}/{n} seeds and "
        f"identity (persistence) in {n_ident}/{n} seeds"
    )
    if comp_e == 0 and comp_i == 0:
        verdict = NOT_AVAILABLE
    else:
        verdict = PASS if strict_majority(n_effort, n) and strict_majority(n_ident, n) else FAIL
    return AcceptanceVerdict(
        "T3",
        "Ablation — neither effort-only nor learned-persistence training learns "
        "the world; the predictive anchor is what drives the improvement.",
        "predictive improvement > effort-only AND > identity(persistence) "
        "improvement, each in a majority of seeds",
        verdict,
        measured,
    )


def _t4(predictive, true_dim, checkpoints, n) -> AcceptanceVerdict:
    readings: list[HorizonReading] = []
    all_pass = True
    for c in checkpoints:
        best_dims = [s.checkpoints[c].best_dim for s in predictive if c in s.checkpoints]
        within = sum(1 for bd in best_dims if abs(bd - true_dim) <= 1)
        exact = sum(1 for bd in best_dims if bd == true_dim)
        readings.append(HorizonReading(c, best_dims, within, exact, len(best_dims)))
        if not strict_majority(within, n):
            all_pass = False
    last = checkpoints[-1] if checkpoints else None
    spread = (
        [s.checkpoints[last].best_dim for s in predictive if last in s.checkpoints]
        if last is not None
        else []
    )
    measured = Measured(
        per_seed=spread,
        note="judged on the per-seed spread at every checkpoint; the mean is never the verdict",
    )
    return AcceptanceVerdict(
        "T4",
        "Structure grows to the right dimensionality (the load-bearing test).",
        f"|best_dim - true_dim| <= 1 in a strict majority at EVERY checkpoint "
        f"(true_dim={true_dim})",
        PASS if all_pass else FAIL,
        measured,
        horizon_readings=readings,
    )


def _t5(predictive, max_frames, n) -> AcceptanceVerdict:
    finals = [s.final_population for s in predictive]
    growing = [s.still_growing for s in predictive]
    measured = _aggregate([float(f) for f in finals])
    capped = any(f >= max_frames for f in finals)
    bounded = measured.mean is not None and measured.mean < max_frames
    self_limiting = not any(growing)
    verdict = PASS if (bounded and self_limiting) else FAIL
    n_growing = sum(growing)
    measured.note = f"{n_growing}/{n} seeds still growing; capped={capped}"
    detail = T5Detail(
        final_population_mean=measured.mean if measured.mean is not None else 0.0,
        final_population_std=measured.std if measured.std is not None else 0.0,
        max_frames=max_frames,
        still_growing_per_seed=growing,
        capped=capped,
    )
    return AcceptanceVerdict(
        "T5",
        "Decay is default — the population self-limits (eviction paces spawn), "
        "not merely caps out.",
        "mean final_population < max_frames AND no seed still growing over its final third",
        verdict,
        measured,
        t5_detail=detail,
    )


def _t6(predictive, n) -> AcceptanceVerdict:
    measured = _aggregate([s.loss_fraction for s in predictive])
    verdict = PASS if (measured.mean is not None and measured.mean < 0.15) else FAIL
    return AcceptanceVerdict(
        "T6",
        "No-loss guard — post-warmup, observations are rarely left unmapped.",
        "post-warmup loss_fraction < 0.15",
        verdict,
        measured,
    )


# One-sided noninferiority threshold: FAIL only when the curious arm's paired
# mean margin is significantly below zero (≈ t(α=0.05) for the suite's df; [D]).
T7_NONINFERIORITY_T = 1.9


def evaluate_t7(agency_run) -> AcceptanceVerdict:
    """T7 — directed curiosity is not worse than random exploration (FR-009).

    Same-seed paired runs, equal experience; per seed the margin is
    ``improvement(curious) − improvement(random)``. The pre-registered claim
    (spec Assumptions) is *noninferiority* — "directedness does not hurt" — so
    the verdict is a one-sided paired test: **FAIL iff
    ``mean(margin) < −T·SE(margin)``** (T = 1.9 ≈ t(0.05) at the reference df).
    A sign-majority bar was measured first and discarded openly: with
    continuous margins it degenerates into "strictly better per seed" and fails
    exact equivalence by coin-flip (reference measurement 2026-07-07: 3/8 signs,
    mean −0.006 ± 0.036 — statistically equivalent). Sign counts and the full
    per-seed spread are always reported alongside the verdict."""
    margins: list[float | None] = []
    n_strictly_better = 0
    comparable = 0
    for cur, rnd in zip(agency_run.curious, agency_run.random, strict=True):
        if cur.improvement is None or rnd.improvement is None:
            margins.append(None)
            continue
        comparable += 1
        margin = cur.improvement - rnd.improvement
        margins.append(margin)
        if margin > 0:
            n_strictly_better += 1
    n = len(agency_run.seeds)
    measured = _aggregate(margins)
    if comparable == 0:
        measured.note = "not available"
        verdict = NOT_AVAILABLE
    elif comparable == 1:
        measured.note = f"single comparable seed (margin {measured.mean:+.4f}); no spread"
        verdict = PASS if measured.mean >= 0 else FAIL
    else:
        se = measured.std / np.sqrt(comparable)
        threshold = -T7_NONINFERIORITY_T * se
        verdict = PASS if measured.mean >= threshold else FAIL
        measured.note = (
            f"mean margin {measured.mean:+.4f} vs noninferiority bound {threshold:+.4f} "
            f"(SE {se:.4f}); strictly better in {n_strictly_better}/{n} seeds"
        )
    return AcceptanceVerdict(
        "T7",
        "Directed curiosity gathers experience at least as useful for learning "
        "the world as random exploration (equal experience, same seed).",
        "paired mean margin not significantly below zero "
        f"(mean ≥ −{T7_NONINFERIORITY_T}·SE, one-sided noninferiority)",
        verdict,
        measured,
    )


def evaluate_suite(suite_run) -> list[AcceptanceVerdict]:
    """Evaluate T1-T6 from a completed SuiteRun (predictive + both ablations)."""
    predictive = suite_run.predictive
    ablation = suite_run.ablation
    identity = getattr(suite_run, "identity", {})
    n = len(predictive)
    checkpoints = list(suite_run.config.horizon_checkpoints)
    return [
        _t1(predictive, n),
        _t2(predictive, n),
        _t3(predictive, ablation, identity, n),
        _t4(predictive, suite_run.true_dim, checkpoints, n),
        _t5(predictive, suite_run.config.max_frames, n),
        _t6(predictive, n),
    ]
