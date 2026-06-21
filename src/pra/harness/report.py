"""Verdict rendering (FR-002/003/007/008, report-schema.json).

Human-readable text (always) and an optional machine-readable JSON. The honest-
summary principle governs: a failing test is shown as FAIL with the numbers that
explain it; T4 is shown as the per-seed spread at every checkpoint, never a mean.
"""

from __future__ import annotations

from pra.harness.acceptance import (
    INVESTIGATORY,
    AcceptanceVerdict,
    ScaleReading,
    VerdictReport,
)
from pra.harness.runner import DeterminismResult, SuiteRun

__all__ = [
    "build_suite_report",
    "build_determinism_report",
    "build_scale_report",
    "render_text",
    "render_json",
]

SCHEMA_VERSION = "1.0"
_DEBUG_BANNER = "FOR DEBUGGING ONLY — not a validation of a behavioral claim"


def _metadata(suite_run: SuiteRun, scoring_mode: str = "predictive") -> dict:
    return {
        "seeds": list(suite_run.seeds),
        "true_dim": suite_run.true_dim,
        "obs_dim": suite_run.config.obs_dim,
        "checkpoints": list(suite_run.config.horizon_checkpoints),
        "scoring_mode": scoring_mode,
        "wall_clock_seconds": suite_run.wall_clock_seconds,
        "failed_seeds": list(suite_run.failed_seeds),
    }


def build_suite_report(suite_run: SuiteRun, tests: list[AcceptanceVerdict]) -> VerdictReport:
    return VerdictReport(
        mode="suite",
        run_metadata=_metadata(suite_run),
        tests=tests,
        for_debugging_only=len(suite_run.seeds) == 1,
    )


def build_determinism_report(
    config, result: DeterminismResult, wall_clock_seconds: float
) -> VerdictReport:
    return VerdictReport(
        mode="determinism",
        run_metadata={
            "seeds": [result.seed],
            "true_dim": config.true_dim,
            "obs_dim": config.obs_dim,
            "checkpoints": list(config.horizon_checkpoints),
            "scoring_mode": "predictive",
            "wall_clock_seconds": wall_clock_seconds,
            "failed_seeds": [],
        },
        tests=[],
        determinism_check={
            "seed": result.seed,
            "verdict": result.verdict,
            "byte_diff_count": result.byte_diff_count,
            "first_difference": result.first_difference,
        },
        for_debugging_only=False,
    )


def build_scale_report(
    config, seeds: list[int], readings: list[ScaleReading], wall_clock_seconds: float
) -> VerdictReport:
    verdict = AcceptanceVerdict(
        id="T-SCALE",
        claim="Structure-finding is runnable and measured at large true "
        "dimensionality (investigatory; never a build pass/fail).",
        criterion="runnable + per-seed best_dim spread, throughput, and wall-clock reported",
        verdict=INVESTIGATORY,
        measured=_scale_measured(readings),
        scale_detail=readings,
    )
    return VerdictReport(
        mode="scale",
        run_metadata={
            "seeds": list(seeds),
            "true_dim": readings[0].true_dim if readings else config.true_dim,
            "obs_dim": config.obs_dim,
            "checkpoints": list(config.horizon_checkpoints),
            "scoring_mode": "predictive",
            "wall_clock_seconds": wall_clock_seconds,
            "failed_seeds": [],
        },
        tests=[verdict],
        scale_detail=readings,
        for_debugging_only=len(seeds) == 1,
    )


def _scale_measured(readings: list[ScaleReading]):
    from pra.harness.acceptance import Measured

    return Measured(note=f"{len(readings)} dimensionality/dimensionalities measured")


# --- text rendering --------------------------------------------------------
def _fmt_measured(m) -> str:
    if m.mean is None:
        return "not available"
    return f"{m.mean:.3f} ± {m.std:.3f}"


def render_text(report: VerdictReport) -> str:
    lines: list[str] = []
    bar = "=" * 74
    lines.append(bar)
    lines.append(f"PRA VALIDATION — mode: {report.mode}")
    lines.append(bar)
    if report.for_debugging_only:
        lines.append(f"  *** {_DEBUG_BANNER} ***")
    md = report.run_metadata
    lines.append(
        f"  seeds={md['seeds']}  true_dim={md['true_dim']}  obs_dim={md['obs_dim']}  "
        f"checkpoints={md['checkpoints']}"
    )
    lines.append(f"  wall_clock={md['wall_clock_seconds']:.1f}s")
    if md.get("failed_seeds"):
        lines.append(
            f"  !! INCOMPLETE: seeds {md['failed_seeds']} errored — "
            f"the aggregate is NOT a complete result."
        )

    if report.determinism_check is not None:
        dc = report.determinism_check
        lines.append("")
        lines.append(f"[DETERMINISM] seed {dc['seed']}: {dc['verdict']}")
        if dc["verdict"] == "PASS":
            lines.append("     two runs produced byte-identical summaries.")
        else:
            lines.append(
                f"     {dc['byte_diff_count']} bytes differ; first difference at "
                f"'{dc['first_difference']}'."
            )

    for t in report.tests:
        lines.append("")
        lines.append(f"[{t.id}] {t.claim}")
        lines.append(f"     criterion: {t.criterion}")
        if t.horizon_readings is not None:
            lines.append("     horizon | best-frame dim across seeds | within-1 | exact")
            for r in t.horizon_readings:
                lines.append(
                    f"       @{r.checkpoint:<3} | {str(r.best_dim_per_seed):<34} | "
                    f"{r.within_one_count}/{r.n_seeds:<5} | {r.exact_count}/{r.n_seeds}"
                )
        else:
            lines.append(f"     measured: {_fmt_measured(t.measured)}")
        if t.measured.note:
            lines.append(f"     {t.measured.note}")
        if t.t5_detail is not None:
            d = t.t5_detail
            lines.append(
                f"     final population: {d.final_population_mean:.1f} ± "
                f"{d.final_population_std:.1f} (cap {d.max_frames}); "
                f"still-growing per seed: {d.still_growing_per_seed}"
            )
        if t.scale_detail is not None:
            lines.append("     true_dim | best_dim across seeds | throughput | wall")
            for r in t.scale_detail:
                lines.append(
                    f"       {r.true_dim:<6} | {str(r.best_dim_per_seed):<26} | "
                    f"{r.throughput:,.0f}/s | {r.wall_clock_seconds:.1f}s"
                )
        lines.append(f"     -> {t.verdict}")

    lines.append("")
    return "\n".join(lines)


# --- JSON rendering (conforms to contracts/report-schema.json) -------------
def _measured_json(m) -> dict:
    out: dict = {}
    if m.mean is not None:
        out["mean"] = m.mean
    if m.std is not None:
        out["std"] = m.std
    if m.per_seed is not None:
        out["per_seed"] = m.per_seed
    if m.note is not None:
        out["note"] = m.note
    return out


def _test_json(t) -> dict:
    obj: dict = {
        "id": t.id,
        "claim": t.claim,
        "criterion": t.criterion,
        "verdict": t.verdict,
        "measured": _measured_json(t.measured),
    }
    if t.horizon_readings is not None:
        obj["horizon_readings"] = [
            {
                "checkpoint": r.checkpoint,
                "best_dim_per_seed": r.best_dim_per_seed,
                "within_one_count": r.within_one_count,
                "exact_count": r.exact_count,
                "n_seeds": r.n_seeds,
            }
            for r in t.horizon_readings
        ]
    if t.t5_detail is not None:
        d = t.t5_detail
        obj["t5_detail"] = {
            "final_population_mean": d.final_population_mean,
            "final_population_std": d.final_population_std,
            "max_frames": d.max_frames,
            "still_growing_per_seed": d.still_growing_per_seed,
        }
    if t.scale_detail is not None:
        obj["scale_detail"] = [
            {
                "true_dim": r.true_dim,
                "best_dim_per_seed": r.best_dim_per_seed,
                "observation_steps": r.observation_steps,
                "throughput": r.throughput,
                "wall_clock_seconds": r.wall_clock_seconds,
            }
            for r in t.scale_detail
        ]
    return obj


def render_json(report: VerdictReport) -> dict:
    obj: dict = {
        "schema_version": SCHEMA_VERSION,
        "mode": report.mode,
        "for_debugging_only": report.for_debugging_only,
        "run_metadata": report.run_metadata,
        "tests": [_test_json(t) for t in report.tests],
    }
    if report.determinism_check is not None:
        obj["determinism_check"] = report.determinism_check
    return obj
