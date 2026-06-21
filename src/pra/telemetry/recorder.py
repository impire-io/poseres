"""Telemetry (PRA-02 §3, data-model §4).

Records exactly the fields the acceptance tests read, and serializes a per-seed
summary to a **byte-identical** canonical form so the determinism check (FR-010,
SC-007) is well-defined: fixed key order, fixed float formatting, no smoothing.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field

import numpy as np

__all__ = [
    "PerStepRecord",
    "PerCycleRecord",
    "PerSeedRunSummary",
    "CheckpointReading",
    "EARLY_LATE_WINDOW",
    "MIN_PRED_SAMPLES",
    "STILL_GROWING_SLOPE",
    "late_slope",
    "is_still_growing",
]

# Early/late predictive error are averaged over this many recorded per-step values;
# fewer than MIN_PRED_SAMPLES early samples => "not available" (R8).
EARLY_LATE_WINDOW = 200
MIN_PRED_SAMPLES = 50
# A seed whose population's late slope exceeds this (frames/cycle) is "still growing"
# rather than self-limiting (R6; mirrors the v4 reference "paces spawn" boundary).
STILL_GROWING_SLOPE = 0.5


@dataclass
class PerStepRecord:
    map_fraction: float
    mean_pred_error: float | None
    loss_flag: bool  # zero frames mapped, counted only post-warmup


@dataclass
class PerCycleRecord:
    population_size: int
    dims_alive: list[int]
    best_frame: tuple[int, float] | None  # (dim, survival_score)
    removed: list[tuple[int, float]]  # (dim, survival_score) evicted this cycle


@dataclass
class CheckpointReading:
    best_dim: int
    population_size: int


def late_slope(populations: list[int]) -> float:
    """Least-squares slope (frames/cycle) over the final third of the cycles."""
    n = len(populations)
    if n < 2:
        return 0.0
    k = max(2, n // 3)
    seg = np.asarray(populations[-k:], dtype=np.float64)
    xs = np.arange(seg.shape[0], dtype=np.float64)
    xbar = xs.mean()
    denom = float(((xs - xbar) ** 2).sum())
    if denom == 0.0:
        return 0.0
    return float(((xs - xbar) * (seg - seg.mean())).sum() / denom)


def is_still_growing(populations: list[int]) -> bool:
    return late_slope(populations) > STILL_GROWING_SLOPE


def _canonical_float(x: float | None) -> float | None:
    if x is None:
        return None
    return float(x)


@dataclass
class PerSeedRunSummary:
    """One run's outcome (data-model §4). The T3 ablation is a *separate* run with
    its own summary; the runner pairs predictive/effort-only summaries by seed."""

    seed: int
    scoring_mode: str
    mean_map_fraction: float
    pred_error_early: float | None
    pred_error_late: float | None
    best_dim: int | None
    best_score: float | None
    final_population: int
    loss_fraction: float
    observation_steps: int
    mean_population: float
    checkpoints: dict[int, CheckpointReading]
    population_by_cycle: list[int]
    still_growing: bool
    error: str | None = None
    _improvement: float | None = field(default=None, repr=False)

    @property
    def improvement(self) -> float | None:
        if self.pred_error_early is None or self.pred_error_late is None:
            return None
        return self.pred_error_early - self.pred_error_late

    def canonical(self) -> dict:
        """Ordered, JSON-ready dict — the basis for byte-identical comparison."""
        return {
            "seed": int(self.seed),
            "scoring_mode": self.scoring_mode,
            "mean_map_fraction": _canonical_float(self.mean_map_fraction),
            "pred_error_early": _canonical_float(self.pred_error_early),
            "pred_error_late": _canonical_float(self.pred_error_late),
            "improvement": _canonical_float(self.improvement),
            "best_dim": None if self.best_dim is None else int(self.best_dim),
            "best_score": _canonical_float(self.best_score),
            "final_population": int(self.final_population),
            "loss_fraction": _canonical_float(self.loss_fraction),
            "observation_steps": int(self.observation_steps),
            "mean_population": _canonical_float(self.mean_population),
            "checkpoints": {
                str(c): {
                    "best_dim": int(r.best_dim),
                    "population_size": int(r.population_size),
                }
                for c, r in sorted(self.checkpoints.items())
            },
            "population_by_cycle": [int(p) for p in self.population_by_cycle],
            "still_growing": bool(self.still_growing),
            "error": self.error,
        }

    def serialize(self) -> str:
        """Deterministic, byte-stable serialization (FR-010, SC-007)."""
        return json.dumps(self.canonical(), separators=(",", ":"), ensure_ascii=True)
