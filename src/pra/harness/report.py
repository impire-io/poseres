"""Verdict rendering (FR-002/003/007/008, report-schema.json).

Human-readable text (always) and an optional machine-readable JSON. The honest-
summary principle governs: a failing test is shown as FAIL with the numbers that
explain it; T4 is shown as the per-seed spread at every checkpoint, never a mean.
"""

from __future__ import annotations

import dataclasses

from pra.harness.acceptance import (
    INVESTIGATORY,
    AcceptanceVerdict,
    ScaleReading,
    VerdictReport,
    evaluate_t3,
    evaluate_t3_scaled,
)
from pra.harness.runner import DeterminismResult, SuiteRun

__all__ = [
    "build_suite_report",
    "build_determinism_report",
    "build_scale_report",
    "build_scale_t3_report",
    "build_ladder_report",
    "build_agency_report",
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


def _improvement_margin(a, b) -> float | None:
    if a is None or b is None or a.improvement is None or b.improvement is None:
        return None
    return a.improvement - b.improvement


def build_scale_t3_report(
    base, seeds: list[int], results: list[tuple[int, SuiteRun]], wall_clock_seconds: float
) -> VerdictReport:
    """Per-``true_dim`` T3 verdicts from scaled triad runs (ROADMAP A2).

    Investigatory context like T-SCALE — each scale's verdict is data, never a
    build failure — but the criterion applied per scale is exactly the reference
    T3 (one evaluator). The full per-seed triad improvements and both margins are
    carried in the metadata: the honest record is the spread, not the verdict."""
    tests: list[AcceptanceVerdict] = []
    detail: list[dict] = []
    failed = sorted({s for _td, run in results for s in run.failed_seeds})
    for td, run in results:
        evaluate = evaluate_t3_scaled if run.matched else evaluate_t3
        tests.append(dataclasses.replace(evaluate(run), id=f"T3@td={td}"))
        by_seed = {s.seed: s for s in run.predictive}
        detail.append(
            {
                "true_dim": td,
                "obs_dim": run.config.obs_dim,
                "n_cycles": run.config.effective_n_cycles,
                "matched": bool(run.matched),
                "per_seed": [
                    {
                        "seed": seed,
                        "predictive_improvement": (
                            by_seed[seed].improvement if seed in by_seed else None
                        ),
                        "effort_only_improvement": (
                            run.ablation[seed].improvement if seed in run.ablation else None
                        ),
                        "identity_improvement": (
                            run.identity[seed].improvement if seed in run.identity else None
                        ),
                        "matched_improvement": (
                            run.matched[seed].improvement if seed in run.matched else None
                        ),
                        "margin_vs_effort": _improvement_margin(
                            by_seed.get(seed), run.ablation.get(seed)
                        ),
                        "margin_vs_identity": _improvement_margin(
                            by_seed.get(seed), run.identity.get(seed)
                        ),
                        "margin_matched_vs_identity": _improvement_margin(
                            run.matched.get(seed), run.identity.get(seed)
                        ),
                        "predictive_best_dim": (
                            by_seed[seed].best_dim if seed in by_seed else None
                        ),
                    }
                    for seed in run.seeds
                ],
            }
        )
    report = VerdictReport(
        mode="scale-t3",
        run_metadata={
            "seeds": list(seeds),
            "true_dim": results[0][0] if results else base.true_dim,
            "obs_dim": base.obs_dim,
            "checkpoints": list(base.horizon_checkpoints),
            "scoring_mode": "predictive + effort_only + identity (T3 triad)",
            "wall_clock_seconds": wall_clock_seconds,
            "failed_seeds": failed,
        },
        tests=tests,
        for_debugging_only=len(seeds) == 1,
    )
    report.run_metadata["t3_scale_detail"] = detail
    return report


def build_ladder_report(
    base, seeds: list[int], results, wall_clock_seconds: float
) -> VerdictReport:
    """Per-rung, per-dial-set verdicts from ladder runs (feature 005).

    Investigatory context: rung verdicts are data judged against the
    pre-registered LADDER-CRITERIA.md, never a build failure. The full
    per-seed reading tables ride in the metadata — the honest record is the
    spread, not the verdict."""
    failed = sorted({s for r in results for s in r.failed_seeds})
    report = VerdictReport(
        mode="ladder",
        run_metadata={
            "seeds": list(seeds),
            "true_dim": base.true_dim,
            "obs_dim": base.obs_dim,
            "checkpoints": list(base.horizon_checkpoints),
            "scoring_mode": "predictive (+ quartet arms on L2)",
            "wall_clock_seconds": wall_clock_seconds,
            "failed_seeds": failed,
        },
        tests=[r.verdict for r in results],
        for_debugging_only=len(seeds) == 1,
    )
    report.run_metadata["ladder_detail"] = [
        {
            "rung": r.rung,
            "label": r.label,
            "world": r.config.world,
            "true_dim": r.config.true_dim,
            "obs_dim": r.config.obs_dim,
            "dials": {
                "region_noise_std": r.config.region_noise_std,
                "factor_dims": list(r.config.factor_dims),
                "distractor_dim": r.config.distractor_dim,
                "distractor_channels": r.config.distractor_channels,
                "distractor_mode": r.config.distractor_mode,
                "distractor_noise_std": r.config.distractor_noise_std,
            },
            "wall_clock_seconds": r.wall_clock_seconds,
            "failed_seeds": list(r.failed_seeds),
            "per_seed": r.rows,
        }
        for r in results
    ]
    return report


def build_agency_report(agency_run, t7: AcceptanceVerdict) -> VerdictReport:
    """T7 verdict + curious-arm telemetry (contracts/cli.md of 002)."""
    cfg = agency_run.config
    agency_blocks = [s.agency for s in agency_run.curious if s.agency is not None]

    def _mean(key: str) -> float:
        return sum(b[key] for b in agency_blocks) / len(agency_blocks) if agency_blocks else 0.0

    report = VerdictReport(
        mode="agency",
        run_metadata={
            "seeds": list(agency_run.seeds),
            "true_dim": cfg.true_dim,
            "obs_dim": cfg.obs_dim,
            "checkpoints": list(cfg.horizon_checkpoints),
            "scoring_mode": "predictive",
            "wall_clock_seconds": agency_run.wall_clock_seconds,
            "failed_seeds": list(agency_run.failed_seeds),
        },
        tests=[t7],
        for_debugging_only=len(agency_run.seeds) == 1,
    )
    report.run_metadata["agency_telemetry"] = {
        "value_signal_mean": _mean("value_signal_mean"),
        "learning_progress_mean": _mean("learning_progress_mean"),
        "novelty_mean": _mean("novelty_mean"),
        "directed_fraction_mean": _mean("directed_fraction"),
    }
    report.run_metadata["t7_per_seed"] = [
        {
            "seed": seed,
            "curious_improvement": cur.improvement,
            "random_improvement": rnd.improvement,
            "margin": (
                cur.improvement - rnd.improvement
                if cur.improvement is not None and rnd.improvement is not None
                else None
            ),
        }
        for seed, cur, rnd in zip(
            agency_run.seeds, agency_run.curious, agency_run.random, strict=True
        )
    ]
    return report


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

    if "agency_telemetry" in md:
        t = md["agency_telemetry"]
        lines.append("")
        lines.append(
            f"[AGENCY] value signal {t['value_signal_mean']:.3f} "
            f"(learning-progress {t['learning_progress_mean']:.4f}, "
            f"novelty {t['novelty_mean']:.3f}); "
            f"directed actions {t['directed_fraction_mean']:.0%}"
        )
    if "t7_per_seed" in md:
        lines.append("")
        lines.append("     seed | curious improvement | random improvement | margin")
        lines.append("     -----+---------------------+--------------------+-------")
        for row in md["t7_per_seed"]:

            def _fmt(x):
                return "   n/a" if x is None else f"{x:+.4f}"

            lines.append(
                f"      {row['seed']:3d} |       {_fmt(row['curious_improvement'])}       |"
                f"      {_fmt(row['random_improvement'])}       | {_fmt(row['margin'])}"
            )

    if "t3_scale_detail" in md:
        for block in md["t3_scale_detail"]:

            def _fmt6(x):
                return "    n/a" if x is None else f"{x:+.4f}"

            has_matched = block.get(
                "matched",
                any(row.get("matched_improvement") is not None for row in block["per_seed"]),
            )
            lines.append("")
            lines.append(
                f"  [T3 {'quartet' if has_matched else 'triad'} @ "
                f"true_dim={block['true_dim']}] "
                f"obs_dim={block['obs_dim']}  cycles={block['n_cycles']}"
            )
            if has_matched:
                lines.append(
                    "     seed | predictive | effort-only | identity  | matched   |"
                    " paired-margin | best_dim"
                )
                for row in block["per_seed"]:
                    bd = row["predictive_best_dim"]
                    lines.append(
                        f"      {row['seed']:3d} |  {_fmt6(row['predictive_improvement'])}  |"
                        f"   {_fmt6(row['effort_only_improvement'])}  |"
                        f" {_fmt6(row['identity_improvement'])}  |"
                        f" {_fmt6(row['matched_improvement'])}  |"
                        f"    {_fmt6(row['margin_matched_vs_identity'])}    "
                        f"| {'n/a' if bd is None else bd}"
                    )
            else:
                lines.append(
                    "     seed | predictive | effort-only | identity  | vs-effort | vs-identity"
                    " | best_dim"
                )
                for row in block["per_seed"]:
                    bd = row["predictive_best_dim"]
                    lines.append(
                        f"      {row['seed']:3d} |  {_fmt6(row['predictive_improvement'])}  |"
                        f"   {_fmt6(row['effort_only_improvement'])}  |"
                        f" {_fmt6(row['identity_improvement'])}  |"
                        f"  {_fmt6(row['margin_vs_effort'])} |"
                        f"   {_fmt6(row['margin_vs_identity'])}"
                        f" | {'n/a' if bd is None else bd}"
                    )

    if "ladder_detail" in md:
        for block in md["ladder_detail"]:

            def _fmt4(x):
                return "   n/a" if x is None else f"{x:+.4f}"

            def _fmtd(x):
                return "n/a" if x is None else str(x)

            lines.append("")
            lines.append(
                f"  [{block['label']}] world={block['world']}  "
                f"true_dim={block['true_dim']}  obs_dim={block['obs_dim']}  "
                f"wall={block['wall_clock_seconds']:.1f}s"
            )
            if block["failed_seeds"]:
                lines.append(f"     !! seeds {block['failed_seeds']} errored")
            if block["rung"] == "l1":
                lines.append("     seed | best_dim | twin | improvement | twin-impr | occupancy")
                for row in block["per_seed"]:
                    occ = row["occupancy"]
                    lines.append(
                        f"      {row['seed']:3d} |    {_fmtd(row['best_dim']):<4} |"
                        f"  {_fmtd(row['twin_best_dim']):<3} |"
                        f"   {_fmt4(row['improvement'])}   |"
                        f"  {_fmt4(row['twin_improvement'])}  |"
                        f"   {'n/a' if occ is None else f'{occ:.3f}'}"
                    )
            elif block["rung"] == "l2":
                lines.append("     seed | best_dim | paired-margin | census (dim: frames/mature)")
                for row in block["per_seed"]:
                    census = ", ".join(
                        f"{d}: {v['frames']}/{v['mature']}" for d, v in row["census"].items()
                    )
                    lines.append(
                        f"      {row['seed']:3d} |    {_fmtd(row['best_dim']):<4} |"
                        f"    {_fmt4(row['paired_margin'])}    | {census}"
                    )
            else:
                lines.append("     seed | best_dim | best_dim at checkpoints")
                for row in block["per_seed"]:
                    cps = ", ".join(f"@{c}: {bd}" for c, bd in row["checkpoints"].items())
                    lines.append(f"      {row['seed']:3d} |    {_fmtd(row['best_dim']):<4} | {cps}")

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
