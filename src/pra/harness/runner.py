"""Multi-seed orchestration (FR-001, data-model §4, research R7).

Runs every configured seed for ``effective_n_cycles`` and captures each
``PerSeedRunSummary``. For T3 it also runs each seed's two ablations — separate
runs with fresh worlds and equal online experience: ``effort_only`` (transitions
pulled to the zero pose, ``seed + 9999``) and ``identity`` (transitions pulled to
the *current* pose — the learned persistence predictor, ``seed + 18888``) — and
keeps the summaries joined by seed. T3 requires genuine prediction to beat BOTH:
zero-pull is the weak claim, persistence is the strong one (PRA-02 §2). A seed
that errors is recorded in ``failed_seeds`` and never silently dropped (FR-008).
The determinism check runs one seed twice and byte-compares the canonical
summaries (FR-006, SC-003).

**Parallel execution.** Seeds are fully independent runs (one seeded generator
each, single-threaded BLAS pinned per process), so they execute in worker
*processes* when ``workers > 1``. Parallelism MUST NOT — and by construction
cannot — change any result: each run's float-op sequence is untouched, and
results are reassembled in configured seed order. ``workers=1`` (the default for
library callers) runs inline; the CLI defaults to one worker per seed up to the
CPU count.
"""

from __future__ import annotations

import os
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass, field
from time import perf_counter

from pra.config import Config
from pra.core.engine import Engine
from pra.telemetry.recorder import PerSeedRunSummary

__all__ = ["SuiteRun", "DeterminismResult", "run_suite", "check_determinism", "auto_workers"]

ABLATION_SEED_OFFSET = 9999
IDENTITY_SEED_OFFSET = 18888


def auto_workers(n_tasks: int) -> int:
    """One worker per task, capped at the machine's CPU count."""
    return max(1, min(n_tasks, os.cpu_count() or 1))


@dataclass
class SuiteRun:
    config: Config
    true_dim: int
    seeds: list[int]
    predictive: list[PerSeedRunSummary]
    ablation: dict[int, PerSeedRunSummary]
    identity: dict[int, PerSeedRunSummary] = field(default_factory=dict)
    # churn-matched predictive arm (amended scaled T3, T3SCALE-DIAGNOSIS);
    # empty in every validated mode.
    matched: dict[int, PerSeedRunSummary] = field(default_factory=dict)
    failed_seeds: list[int] = field(default_factory=list)
    wall_clock_seconds: float = 0.0
    per_seed_wall: dict[int, float] = field(default_factory=dict)

    @property
    def complete(self) -> bool:
        return not self.failed_seeds


@dataclass
class DeterminismResult:
    seed: int
    verdict: str
    byte_diff_count: int
    first_difference: str | None


def _run_seed_group(
    config: Config, seed: int, with_ablation: bool, proposal_factory=None, with_matched=False
) -> tuple[
    int,
    PerSeedRunSummary,
    PerSeedRunSummary | None,
    PerSeedRunSummary | None,
    PerSeedRunSummary | None,
    float,
]:
    """One seed's predictive run + its two ablations (module-level: picklable).

    ``proposal_factory`` (a picklable ``Config -> ProposalPolicy`` callable) lets
    the scaled T3 measurement run the triad under the scaled ecology's proposal
    policy; ``None`` keeps the validated default. A fresh policy is built per
    engine; the ablation runs never consolidate, so it is inert there — passed
    anyway so all three arms share one construction, differing only in
    ``scoring_mode`` (PRA-02 §2).

    ``with_matched`` adds the churn-matched fourth arm of the amended scaled T3
    (T3SCALE-DIAGNOSIS): *predictive* training under the identity arm's exact
    semantics — the same ``seed + 18888`` world, no consolidation — so the paired
    (matched, identity) comparison differs only in the training target."""
    ts = perf_counter()

    def _proposal():
        return proposal_factory(config) if proposal_factory is not None else None

    summary = Engine(config, scoring_mode="predictive", proposal=_proposal()).run(
        seed, do_offline=True
    )
    ab = ident = matched = None
    if with_ablation:
        ab = Engine(config, scoring_mode="effort_only", proposal=_proposal()).run(
            seed + ABLATION_SEED_OFFSET, do_offline=False
        )
        ident = Engine(config, scoring_mode="identity", proposal=_proposal()).run(
            seed + IDENTITY_SEED_OFFSET, do_offline=False
        )
    if with_matched:
        matched = Engine(config, scoring_mode="predictive", proposal=_proposal()).run(
            seed + IDENTITY_SEED_OFFSET, do_offline=False
        )
    return seed, summary, ab, ident, matched, perf_counter() - ts


def run_suite(
    config: Config,
    *,
    with_ablation: bool = True,
    workers: int = 1,
    proposal_factory=None,
    with_matched: bool = False,
) -> SuiteRun:
    predictive: list[PerSeedRunSummary] = []
    ablation: dict[int, PerSeedRunSummary] = {}
    identity: dict[int, PerSeedRunSummary] = {}
    matched: dict[int, PerSeedRunSummary] = {}
    failed: list[int] = []
    per_seed_wall: dict[int, float] = {}
    t0 = perf_counter()

    results: dict[int, tuple] = {}
    if workers > 1 and len(config.seeds) > 1:
        with ProcessPoolExecutor(max_workers=min(workers, len(config.seeds))) as pool:
            futures = {
                seed: pool.submit(
                    _run_seed_group, config, seed, with_ablation, proposal_factory, with_matched
                )
                for seed in config.seeds
            }
            for seed, fut in futures.items():
                try:
                    results[seed] = fut.result()
                except Exception:  # noqa: BLE001 — reported, not fatal (FR-008)
                    failed.append(seed)
    else:
        for seed in config.seeds:
            try:
                results[seed] = _run_seed_group(
                    config, seed, with_ablation, proposal_factory, with_matched
                )
            except Exception:  # noqa: BLE001 — reported, not fatal (FR-008)
                failed.append(seed)

    # reassemble in configured seed order — parallelism never reorders results
    for seed in config.seeds:
        if seed not in results:
            continue
        _, summary, ab, ident, match, wall = results[seed]
        predictive.append(summary)
        if ab is not None:
            ablation[seed] = ab
        if ident is not None:
            identity[seed] = ident
        if match is not None:
            matched[seed] = match
        per_seed_wall[seed] = wall

    return SuiteRun(
        config=config,
        true_dim=config.true_dim,
        seeds=list(config.seeds),
        predictive=predictive,
        ablation=ablation,
        identity=identity,
        matched=matched,
        failed_seeds=failed,
        wall_clock_seconds=perf_counter() - t0,
        per_seed_wall=per_seed_wall,
    )


def _first_difference(a: dict, b: dict, path: str = "") -> str | None:
    for key in a:
        here = f"{path}.{key}" if path else str(key)
        if key not in b:
            return here
        av, bv = a[key], b[key]
        if isinstance(av, dict) and isinstance(bv, dict):
            sub = _first_difference(av, bv, here)
            if sub is not None:
                return sub
        elif av != bv:
            return here
    return None


def check_determinism(config: Config, seed: int) -> DeterminismResult:
    a = Engine(config, scoring_mode="predictive").run(seed)
    b = Engine(config, scoring_mode="predictive").run(seed)
    sa, sb = a.serialize(), b.serialize()
    if sa == sb:
        return DeterminismResult(seed, "PASS", 0, None)
    diff_count = sum(1 for x, y in zip(sa, sb, strict=False) if x != y) + abs(len(sa) - len(sb))
    first = _first_difference(a.canonical(), b.canonical())
    return DeterminismResult(seed, "FAIL", diff_count, first)
