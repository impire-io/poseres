"""Proposal and Decay seams (PRA-01 §6.4/§6.5, contracts/seams.md §3/§4).

ProposalPolicy decides what ``dim`` to spawn; DecayPolicy decides who is evicted.
Both draw randomness only from the passed seeded generator and break ties by
ascending ``frame_id``. The default decay threshold **divides** by the population
factor so crowding tightens the bar and eviction paces spawn (the corrected
direction — the STEP-0 gate fix). This mirrors the v4 oracle's structural loop.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Protocol, runtime_checkable

import numpy as np

from pra.config import Config
from pra.core.contracts import FrameState
from pra.core.scorer import Scorer

__all__ = [
    "ProposalPolicy",
    "DecayPolicy",
    "BiasedProposalPolicy",
    "PopulationScaledDecayPolicy",
]


@runtime_checkable
class ProposalPolicy(Protocol):
    def propose_dimension(
        self, best_dim: int, population_dims: Sequence[int], rng: np.random.Generator
    ) -> int: ...


@runtime_checkable
class DecayPolicy(Protocol):
    def threshold(self, population_size: int) -> float: ...
    def evict(
        self,
        frames: Sequence[FrameState],
        scorer: Scorer,
        threshold: float,
        *,
        min_frames: int,
        max_frames: int,
        min_age_cycles: int,
    ) -> list[int]: ...


class BiasedProposalPolicy:
    """With prob ``exploit_prob`` step ±1 from the best dim; else explore a
    uniform dim in ``[1, best_dim + explore_dim_max_offset)``."""

    def __init__(self, config: Config):
        self.exploit_prob = float(config.exploit_prob)
        self.explore_offset = int(config.explore_dim_max_offset)

    def propose_dimension(
        self, best_dim: int, population_dims: Sequence[int], rng: np.random.Generator
    ) -> int:
        # Draw order matches the oracle: random() first, then the dim draw.
        if rng.random() < self.exploit_prob:
            return max(1, best_dim + int(rng.choice([-1, 1])))
        return int(rng.integers(1, best_dim + self.explore_offset))


class PopulationScaledDecayPolicy:
    """Soft-evict every unprotected frame over a population-scaled threshold
    (worst first, never below ``min_frames``), then hard cap to ``max_frames``.
    Young frames (``age_cycles < min_age_cycles``) are exempt from both."""

    def __init__(self, config: Config):
        self.base = float(config.survive_threshold_base)
        self.pop_coeff = float(config.survive_threshold_pop_coeff)
        self.pop_baseline = int(config.survive_threshold_pop_baseline)

    def threshold(self, population_size: int) -> float:
        return self.base / (1.0 + self.pop_coeff * max(0, population_size - self.pop_baseline))

    def evict(
        self,
        frames: Sequence[FrameState],
        scorer: Scorer,
        threshold: float,
        *,
        min_frames: int,
        max_frames: int,
        min_age_cycles: int,
    ) -> list[int]:
        scores = {
            f.frame_id: float(scorer.combine(f.recon_err_ema, f.pred_err_ema, f.effort_ema, f.dim))
            for f in frames
        }

        def worst_first(candidates: list[FrameState]) -> list[FrameState]:
            # descending score; ascending frame_id breaks ties (PRA-01 §7.1).
            return sorted(candidates, key=lambda f: (-scores[f.frame_id], f.frame_id))

        unprotected = [f for f in frames if f.age_cycles >= min_age_cycles]
        remove: list[int] = []
        alive = len(frames)

        # §5.4 soft eviction: remove every unprotected frame over threshold.
        for f in worst_first([f for f in unprotected if scores[f.frame_id] > threshold]):
            if alive <= min_frames:
                break
            remove.append(f.frame_id)
            alive -= 1

        # §5.5 hard cap on the post-soft-eviction population.
        if alive > max_frames:
            removed = set(remove)
            still = [f for f in unprotected if f.frame_id not in removed]
            for f in worst_first(still):
                if alive <= max_frames:
                    break
                remove.append(f.frame_id)
                alive -= 1

        return remove
