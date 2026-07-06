"""T-SCALE investigatory runner (FR-009, SC-006, research R9).

Runs the same world/engine at large true dimensionality and measures, per
``true_dim``, the per-seed ``best_dim`` spread, throughput, and wall-clock. It is
**investigatory** — never scored as a build pass/fail. Batched evaluation
(PRA-01 §7.2) is what makes the observation×frame work reach the millions on one
machine; ``throughput = Σ_seed(observation_steps × mean_population) ÷ wall-clock``.
"""

from __future__ import annotations

from time import perf_counter

from pra.config import Config
from pra.core.engine import Engine
from pra.core.policies import HighDimProposalPolicy
from pra.harness.acceptance import ScaleReading

__all__ = ["run_scale"]


def run_scale(
    base: Config,
    true_dims: list[int],
    seeds: list[int],
    *,
    proposal=None,
) -> list[ScaleReading]:
    readings: list[ScaleReading] = []
    for true_dim in true_dims:
        cfg = base.replace(
            true_dim=true_dim,
            obs_dim=max(base.obs_dim, 3 * true_dim),
            # capacity must scale with the world: hidden < true_dim caps the
            # resolvable dimensionality at the frame's own width
            # (SCALE-DIAGNOSIS §5), so scaled runs use hidden ≳ 2·true_dim.
            hidden_size=max(base.hidden_size, 2 * true_dim),
            seeds=tuple(seeds),
        )
        policy = proposal if proposal is not None else HighDimProposalPolicy(cfg)
        best_dims: list[int] = []
        total_obs = 0
        frame_evals = 0.0
        t0 = perf_counter()
        for seed in seeds:
            summary = Engine(cfg, proposal=policy).run(seed)
            best_dims.append(summary.best_dim if summary.best_dim is not None else 0)
            total_obs += summary.observation_steps
            frame_evals += summary.observation_steps * summary.mean_population
        wall = perf_counter() - t0
        throughput = frame_evals / wall if wall > 0 else 0.0
        readings.append(
            ScaleReading(
                true_dim=true_dim,
                best_dim_per_seed=best_dims,
                observation_steps=total_obs,
                throughput=throughput,
                wall_clock_seconds=wall,
            )
        )
    return readings
