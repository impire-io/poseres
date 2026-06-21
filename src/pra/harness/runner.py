"""Multi-seed orchestration (FR-001, data-model §4, research R7).

Runs every configured seed for ``effective_n_cycles`` and captures each
``PerSeedRunSummary``. For T3 it also runs each seed's effort-only ablation — a
*separate* run with a fresh world (``seed + 9999``), ``scoring_mode=effort_only``,
and equal online experience — and keeps the predictive/ablation summary pair
joined by seed. A seed that errors is recorded in ``failed_seeds`` and never
silently dropped (FR-008). The determinism check runs one seed twice and
byte-compares the canonical summaries (FR-006, SC-003).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from time import perf_counter

from pra.config import Config
from pra.core.engine import Engine
from pra.telemetry.recorder import PerSeedRunSummary

__all__ = ["SuiteRun", "DeterminismResult", "run_suite", "check_determinism"]

ABLATION_SEED_OFFSET = 9999


@dataclass
class SuiteRun:
    config: Config
    true_dim: int
    seeds: list[int]
    predictive: list[PerSeedRunSummary]
    ablation: dict[int, PerSeedRunSummary]
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


def run_suite(config: Config, *, with_ablation: bool = True) -> SuiteRun:
    predictive: list[PerSeedRunSummary] = []
    ablation: dict[int, PerSeedRunSummary] = {}
    failed: list[int] = []
    per_seed_wall: dict[int, float] = {}
    t0 = perf_counter()
    for seed in config.seeds:
        try:
            ts = perf_counter()
            summary = Engine(config, scoring_mode="predictive").run(seed, do_offline=True)
            if with_ablation:
                ab = Engine(config, scoring_mode="effort_only").run(
                    seed + ABLATION_SEED_OFFSET, do_offline=False
                )
                ablation[seed] = ab
            predictive.append(summary)
            per_seed_wall[seed] = perf_counter() - ts
        except Exception:  # noqa: BLE001 — a failed seed is reported, not fatal (FR-008)
            failed.append(seed)
    return SuiteRun(
        config=config,
        true_dim=config.true_dim,
        seeds=list(config.seeds),
        predictive=predictive,
        ablation=ablation,
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
