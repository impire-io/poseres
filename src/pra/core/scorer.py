"""Scorer seam (PRA-01 §6.2, contracts/seams.md §2).

The single place survival scoring is defined. Lower is better. The default adds
a parsimony term ``w_complexity * dim`` (the STEP-0 gate fix) so the winner sits
at the diminishing-returns elbow rather than over-dimensioning. ``combine`` is
written to accept numpy arrays so a whole FrameGroup scores at once.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

import numpy as np
from numpy.typing import ArrayLike

from pra.config import Config

__all__ = ["Scorer", "WeightedSumScorer"]


@runtime_checkable
class Scorer(Protocol):
    def combine(
        self,
        recon_err_ema: ArrayLike,
        pred_err_ema: ArrayLike,
        effort_ema: ArrayLike,
        dim: ArrayLike,
    ) -> np.ndarray:
        """Survival score(s); lower = better. Vectorized over a FrameGroup."""
        ...


class WeightedSumScorer:
    """``w_explain·recon + w_predict·pred + w_effort·effort + w_complexity·dim``."""

    def __init__(self, config: Config):
        self.w_explain = float(config.w_explain)
        self.w_predict = float(config.w_predict)
        self.w_effort = float(config.w_effort)
        # Scale-invariant parsimony [D] (SCALE-DIAGNOSIS layer 4): the per-dim
        # error span flattens as obs_dim grows, so the raw linear penalty
        # overwhelms it at scale; the effective weight is the raw one at the
        # reference obs_dim.
        self.w_complexity = float(config.effective_w_complexity)

    def combine(
        self,
        recon_err_ema: ArrayLike,
        pred_err_ema: ArrayLike,
        effort_ema: ArrayLike,
        dim: ArrayLike,
    ) -> np.ndarray:
        recon = np.asarray(recon_err_ema, dtype=np.float64)
        pred = np.asarray(pred_err_ema, dtype=np.float64)
        effort = np.asarray(effort_ema, dtype=np.float64)
        d = np.asarray(dim, dtype=np.float64)
        return (
            self.w_explain * recon
            + self.w_predict * pred
            + self.w_effort * effort
            + self.w_complexity * d
        )
