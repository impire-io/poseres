"""T-SCALE investigatory runner (FR-009, SC-006, research R9).

Runs the same world/engine at large true dimensionality and measures, per
``true_dim``, the per-seed ``best_dim`` spread, throughput, and wall-clock. It is
**investigatory** — never scored as a build pass/fail. Batched evaluation
(PRA-01 §7.2) is what makes the observation×frame work reach the millions on one
machine; ``throughput = Σ_seed(observation_steps × mean_population) ÷ wall-clock``.
``run_scale_t3`` additionally measures T3's ablation triad at each scale
(ROADMAP A2): the reference criterion applied verbatim to the scaled ecology.

**Parallel execution.** Seeds are independent runs and execute in worker
processes when ``workers > 1`` (dimensionalities stay sequential so each
``true_dim``'s wall-clock and throughput describe a machine dedicated to it).
Parallelism cannot change results — each run's float-op sequence is untouched
and per-seed results are reassembled in seed order.
"""

from __future__ import annotations

from concurrent.futures import ProcessPoolExecutor
from time import perf_counter

from pra.config import Config
from pra.core.engine import Engine
from pra.core.policies import ClimbingProposalPolicy
from pra.harness.acceptance import ScaleReading
from pra.harness.runner import SuiteRun, run_suite
from pra.telemetry.recorder import PerSeedRunSummary

__all__ = ["run_scale", "run_scale_t3", "scaled_config", "SCALE_SCORE_WINDOW", "SCALE_NORM_CAP"]

# Scaled runs default to the fair-judge ecology (THRESHOLD-DIAGNOSIS): the
# survival EMAs advance on the first K steps of each episode, which activates
# the conveyor correction, and proposals climb (PROPOSAL-DIAGNOSIS). Without
# the pair, scaled best_dim reads the maturation filter or the proposal
# conveyor, not the world. Long schedules additionally need the lifetime-
# stability cap (LONGEVITY-DIAGNOSIS): without it, mid-dim frames rot after
# ~400-800 cycles and long-run selection favors rot-resistance. Override via
# --config score_window_steps / weight_norm_cap / a custom `proposal` for
# provenance runs against the old ecology.
SCALE_SCORE_WINDOW = 5
SCALE_NORM_CAP = 1.2


def scaled_config(base: Config, true_dim: int, seeds: list[int]) -> Config:
    """The scaled-run configuration for one ``true_dim`` (see module docstring)."""
    return base.replace(
        true_dim=true_dim,
        obs_dim=max(base.obs_dim, 3 * true_dim),
        # capacity must scale with the world: hidden < true_dim caps the
        # resolvable dimensionality at the frame's own width
        # (SCALE-DIAGNOSIS §5), so scaled runs use hidden ≳ 2·true_dim.
        hidden_size=max(base.hidden_size, 2 * true_dim),
        # fair-judge ecology + lifetime stability by default (see module
        # docstring); explicit base overrides win.
        score_window_steps=(
            base.score_window_steps if base.score_window_steps > 0 else SCALE_SCORE_WINDOW
        ),
        weight_norm_cap=(base.weight_norm_cap if base.weight_norm_cap > 0 else SCALE_NORM_CAP),
        seeds=tuple(seeds),
    )


def _run_scale_seed(cfg: Config, seed: int, proposal) -> PerSeedRunSummary:
    """One scaled seed (module-level: picklable for worker processes)."""
    policy = proposal if proposal is not None else ClimbingProposalPolicy(cfg)
    return Engine(cfg, proposal=policy).run(seed)


def _climbing(cfg: Config) -> ClimbingProposalPolicy:
    """Picklable proposal factory for the scaled T3 triad (one policy per engine)."""
    return ClimbingProposalPolicy(cfg)


def run_scale_t3(
    base: Config,
    true_dims: list[int],
    seeds: list[int],
    *,
    workers: int = 1,
) -> list[tuple[int, SuiteRun]]:
    """The scaled T3 quartet (ROADMAP A2, T3SCALE-DIAGNOSIS) — per ``true_dim``,
    the exact reference triad (predictive + effort-only + identity, seed offsets
    and all, PRA-02 §2) under the scaled ecology defaults and climbing proposals,
    plus the churn-matched fourth arm of the amended scaled criterion
    (predictive training on the identity arm's world, no consolidation).
    Investigatory context: the per-scale T3 verdict is data, never a build
    pass/fail."""
    return [
        (
            true_dim,
            run_suite(
                scaled_config(base, true_dim, seeds),
                with_ablation=True,
                workers=workers,
                proposal_factory=_climbing,
                with_matched=True,
            ),
        )
        for true_dim in true_dims
    ]


def run_scale(
    base: Config,
    true_dims: list[int],
    seeds: list[int],
    *,
    proposal=None,
    workers: int = 1,
) -> list[ScaleReading]:
    readings: list[ScaleReading] = []
    for true_dim in true_dims:
        cfg = scaled_config(base, true_dim, seeds)
        t0 = perf_counter()
        summaries: dict[int, PerSeedRunSummary] = {}
        if workers > 1 and len(seeds) > 1:
            with ProcessPoolExecutor(max_workers=min(workers, len(seeds))) as pool:
                futures = {
                    seed: pool.submit(_run_scale_seed, cfg, seed, proposal) for seed in seeds
                }
                summaries = {seed: fut.result() for seed, fut in futures.items()}
        else:
            summaries = {seed: _run_scale_seed(cfg, seed, proposal) for seed in seeds}
        wall = perf_counter() - t0

        best_dims: list[int] = []
        total_obs = 0
        frame_evals = 0.0
        for seed in seeds:  # reassemble in seed order
            summary = summaries[seed]
            best_dims.append(summary.best_dim if summary.best_dim is not None else 0)
            total_obs += summary.observation_steps
            frame_evals += summary.observation_steps * summary.mean_population
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
