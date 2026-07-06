"""Dimension-scan diagnostic (investigatory research tooling; never pass/fail).

For a fixed world (``true_dim`` hidden from the frames), instantiate one frame per
candidate pose dimensionality, train them all with **equal experience** — no fit
gate, every frame learns on every step — then freeze the weights and measure each
frame's honest observation-space prediction error and reconstruction error over an
evaluation window. This isolates *representational capacity* from gating, search,
and selection.

This is the instrument that separates the failure modes behind a poor T-SCALE
dimensionality result:

- A visible elbow at ``true_dim`` in the scan while the live system collapses to
  dim 1 → a **search/selection** problem (proposal policy, parsimony scaling).
- No elbow at any ``hidden_size`` → a **capacity or world** problem. Sweep
  ``hidden_size``: if the elbow appears only once ``hidden_size ≳ true_dim``, the
  encoder/decoder bottleneck was the cause, not the search.

The same STEP-0 diagnostic (a dimension scan) is how the v3 pose-space scoring bug
was caught; this makes it a first-class, reproducible command.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from pra.config import Config
from pra.core.frame import FrameGroup
from pra.core.scorer import WeightedSumScorer
from pra.world.event_source import SensorimotorWorld

__all__ = ["ScanPoint", "run_scan"]


@dataclass
class ScanPoint:
    """Across-seed aggregate for one (hidden_size, dim) cell of the scan."""

    hidden_size: int
    dim: int
    pred_err_mean: float
    pred_err_std: float
    recon_err_mean: float
    recon_err_std: float
    survival_score_mean: float  # w_explain·recon + w_predict·pred + w_complexity·dim


def _run_one_seed(
    cfg: Config, dims: list[int], seed: int, train_episodes: int, eval_episodes: int
) -> dict[int, tuple[float, float]]:
    """Train one frame per dim with equal experience; return per-dim
    ``(mean honest pred error, mean recon error)`` over the frozen eval window."""
    rng = np.random.default_rng(seed)
    world = SensorimotorWorld(cfg, rng)
    lr, clip = cfg.learning_rate, cfg.gradient_clip

    groups: dict[int, FrameGroup] = {}
    for i, d in enumerate(dims):
        g = FrameGroup(d, cfg.obs_dim, cfg.hidden_size, cfg.n_actions)
        g.add_frame(i, ema_init=1.0, scale=cfg.init_weight_scale, rng=rng)
        groups[d] = g

    all_elect = np.ones(1, dtype=bool)

    def episode(learn: bool, pred_acc=None, recon_acc=None) -> None:
        obs = world.reset()
        prev_obs: np.ndarray | None = None
        prev_a: int | None = None
        for _ in range(cfg.steps_per_episode):
            for d, g in groups.items():
                if learn:
                    fit, pose, h, recon, hd = g.fit_quality(obs)
                    g.learn_placement(obs, pose, h, recon, hd, all_elect, lr, clip)
                    if prev_obs is not None:
                        g.learn_transition(prev_obs, prev_a, obs, False, all_elect, lr, clip)
                else:
                    fit, *_ = g.fit_quality(obs)
                    recon_acc[d].append(float(fit[0]))
                    if prev_obs is not None:
                        pred_acc[d].append(float(g.honest_pred_err(prev_obs, prev_a, obs)[0]))
            prev_obs = obs
            prev_a = int(rng.integers(world.n_actions))
            obs = world.step(prev_a)

    for _ in range(train_episodes):
        episode(learn=True)

    pred_acc: dict[int, list[float]] = {d: [] for d in dims}
    recon_acc: dict[int, list[float]] = {d: [] for d in dims}
    for _ in range(eval_episodes):
        episode(learn=False, pred_acc=pred_acc, recon_acc=recon_acc)

    return {d: (float(np.mean(pred_acc[d])), float(np.mean(recon_acc[d]))) for d in dims}


def run_scan(
    base: Config,
    true_dim: int,
    dims: list[int],
    hidden_sizes: list[int],
    seeds: list[int],
    *,
    train_episodes: int = 100,
    eval_episodes: int = 10,
) -> list[ScanPoint]:
    points: list[ScanPoint] = []
    for hidden in hidden_sizes:
        cfg = base.replace(
            true_dim=true_dim,
            obs_dim=max(base.obs_dim, 3 * true_dim),
            hidden_size=hidden,
        )
        scorer = WeightedSumScorer(cfg)
        per_dim: dict[int, list[tuple[float, float]]] = {d: [] for d in dims}
        for seed in seeds:
            result = _run_one_seed(cfg, dims, seed, train_episodes, eval_episodes)
            for d, pair in result.items():
                per_dim[d].append(pair)
        for d in dims:
            preds = np.array([p for p, _ in per_dim[d]])
            recons = np.array([r for _, r in per_dim[d]])
            scores = [float(scorer.combine(r, p, 0.0, d)) for p, r in per_dim[d]]
            points.append(
                ScanPoint(
                    hidden_size=hidden,
                    dim=d,
                    pred_err_mean=float(preds.mean()),
                    pred_err_std=float(preds.std()),
                    recon_err_mean=float(recons.mean()),
                    recon_err_std=float(recons.std()),
                    survival_score_mean=float(np.mean(scores)),
                )
            )
    return points


def render_scan_text(
    points: list[ScanPoint], true_dim: int, seeds: list[int], train_episodes: int
) -> str:
    lines: list[str] = []
    bar = "=" * 74
    lines.append(bar)
    lines.append(
        f"PRA DIMENSION SCAN — DIAGNOSTIC (true_dim={true_dim}, seeds={seeds}, "
        f"train_episodes={train_episodes})"
    )
    lines.append(bar)
    lines.append("equal experience, no gate: capacity probe, not a selection run.")
    by_hidden: dict[int, list[ScanPoint]] = {}
    for p in points:
        by_hidden.setdefault(p.hidden_size, []).append(p)
    for hidden, pts in by_hidden.items():
        pts = sorted(pts, key=lambda p: p.dim)
        best_pred = min(pts, key=lambda p: p.pred_err_mean)
        best_score = min(pts, key=lambda p: p.survival_score_mean)
        lines.append("")
        lines.append(f"hidden_size = {hidden}")
        lines.append("  dim | honest pred err | recon err       | score(parsimony)")
        lines.append("  ----+-----------------+-----------------+-----------------")
        for p in pts:
            mark = ""
            if p.dim == best_score.dim:
                mark += "  <== min score (selection winner)"
            if p.dim == best_pred.dim:
                mark += "  <- min pred err"
            lines.append(
                f"  {p.dim:3d} | {p.pred_err_mean:.3f} ± {p.pred_err_std:.3f}   | "
                f"{p.recon_err_mean:.3f} ± {p.recon_err_std:.3f}   | "
                f"{p.survival_score_mean:.3f}{mark}"
            )
    lines.append("")
    return "\n".join(lines)
