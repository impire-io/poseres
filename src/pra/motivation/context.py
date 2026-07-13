"""DriveContext — the read-only view a drive evaluates (Doc 05 §2.1).

The Engine builds one per online step. Drives read it and never write through
it; the curiosity drive's own bookkeeping (its error history and observation
memory) is referenced here so valuation and bookkeeping share one source of
truth, but only the owning drive mutates that state, and only *after* valuation.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

import numpy as np

__all__ = ["DriveContext"]


@dataclass(frozen=True)
class DriveContext:
    """What a drive may see at one step (data-model §2)."""

    observation: np.ndarray
    recent_pred_errors: Sequence[float]  # newest last; the engine's per-step statistic
    observation_memory: Sequence[np.ndarray]  # bounded FIFO, newest last
    step_index: int
    # err-at-visit, lockstep with observation_memory (PREDLP-DIAGNOSIS): the
    # per-step mean prediction error recorded when each remembered observation
    # was visited (NaN where none was recorded). Consumed only by the frontier
    # drive; inert default keeps every existing construction valid.
    observation_memory_errors: Sequence[float] = ()
