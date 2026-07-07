"""Agency measurement: curious vs random, paired by seed (research R7, FR-009).

For every configured seed, two full predictive runs with the **same seed** —
identical world, identical schedule, equal experience — differing only in the
policy: the curious arm (`policy_mode="curiosity"`: lookahead + drive) and the
random arm (the pinned `RandomPolicy` baseline). The T7 evaluator compares each
run's own ``improvement = pred_error_early − pred_error_late``.

Seeds run in parallel worker processes exactly as the suite does; parallelism
cannot change results (per-run determinism untouched, results reassembled in
seed order).
"""

from __future__ import annotations

from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass, field
from time import perf_counter

from pra.config import Config
from pra.core.engine import Engine
from pra.telemetry.recorder import PerSeedRunSummary

__all__ = ["AgencyRun", "run_agency"]


@dataclass
class AgencyRun:
    config: Config
    seeds: list[int]
    curious: list[PerSeedRunSummary]
    random: list[PerSeedRunSummary]
    failed_seeds: list[int] = field(default_factory=list)
    wall_clock_seconds: float = 0.0
    per_seed_wall: dict[int, float] = field(default_factory=dict)

    @property
    def complete(self) -> bool:
        return not self.failed_seeds


def _run_seed_pair(
    config: Config, seed: int
) -> tuple[int, PerSeedRunSummary, PerSeedRunSummary, float]:
    """One seed's curious + random arms (module-level: picklable)."""
    ts = perf_counter()
    curious_cfg = config.replace(policy_mode="curiosity")
    random_cfg = config.replace(policy_mode="random")
    curious = Engine(curious_cfg, scoring_mode="predictive").run(seed, do_offline=True)
    baseline = Engine(random_cfg, scoring_mode="predictive").run(seed, do_offline=True)
    return seed, curious, baseline, perf_counter() - ts


def run_agency(config: Config, *, workers: int = 1) -> AgencyRun:
    curious: list[PerSeedRunSummary] = []
    baseline: list[PerSeedRunSummary] = []
    failed: list[int] = []
    per_seed_wall: dict[int, float] = {}
    t0 = perf_counter()

    results: dict[int, tuple] = {}
    if workers > 1 and len(config.seeds) > 1:
        with ProcessPoolExecutor(max_workers=min(workers, len(config.seeds))) as pool:
            futures = {seed: pool.submit(_run_seed_pair, config, seed) for seed in config.seeds}
            for seed, fut in futures.items():
                try:
                    results[seed] = fut.result()
                except Exception:  # noqa: BLE001 — reported, not fatal (FR-008 style)
                    failed.append(seed)
    else:
        for seed in config.seeds:
            try:
                results[seed] = _run_seed_pair(config, seed)
            except Exception:  # noqa: BLE001
                failed.append(seed)

    for seed in config.seeds:  # reassemble in configured order
        if seed not in results:
            continue
        _, cur, rnd, wall = results[seed]
        curious.append(cur)
        baseline.append(rnd)
        per_seed_wall[seed] = wall

    return AgencyRun(
        config=config,
        seeds=list(config.seeds),
        curious=curious,
        random=baseline,
        failed_seeds=failed,
        wall_clock_seconds=perf_counter() - t0,
        per_seed_wall=per_seed_wall,
    )
