"""Policies: action selection (Doc 05 §4).

The Policy seam replaces the engine's inline random action draw. The default
``RandomPolicy`` reproduces that draw EXACTLY — one ``rng.integers(n_actions)``
per step, nothing else — so every existing mode (the validated T1-T6 suite,
determinism, scale, scan) consumes an identical RNG stream and stays
byte-identical to the validated build (FR-008, research R1).

``CuriosityLookaheadPolicy`` is the shipped directed default (Doc 05 §4.2/§4.3):
ε-gate first; uniformly random when exploring, when no best frame exists, or
when the best frame is younger than the maturity bar; otherwise a one-step
lookahead — predict each candidate action's outcome with the best frame's
transition model, decode it, value it via the drive set — choosing the argmax
with ties broken by the lowest action index (no further draws). Policies are
stateless across steps; all randomness comes from the run's single seeded
generator in this fixed order (FR-007).
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Protocol, runtime_checkable

import numpy as np

from pra.config import Config

__all__ = ["PolicyContext", "Policy", "RandomPolicy", "CuriosityLookaheadPolicy", "PolicyParams"]


@dataclass(frozen=True)
class PolicyContext:
    """The read-only view a policy selects from (data-model §3)."""

    observation: np.ndarray
    n_actions: int
    best_frame_age: int | None  # None when no frame exists
    predict_decoded: Callable[[int], np.ndarray | None]  # best-frame one-step, decoded
    drive_value_of: Callable[[np.ndarray], float]  # drive set valued at a hypothetical obs


@runtime_checkable
class Policy(Protocol):
    def select_action(self, context: PolicyContext, rng: np.random.Generator) -> int: ...


class RandomPolicy:
    """The pinned validation baseline: exactly the validated engine's inline draw."""

    def select_action(self, context: PolicyContext, rng: np.random.Generator) -> int:
        return int(rng.integers(context.n_actions))


@dataclass(frozen=True)
class PolicyParams:
    exploration_epsilon: float
    lookahead_min_age_cycles: int

    @classmethod
    def from_config(cls, config: Config) -> PolicyParams:
        return cls(
            exploration_epsilon=config.exploration_epsilon,
            lookahead_min_age_cycles=config.lookahead_min_age_cycles,
        )


class CuriosityLookaheadPolicy:
    """One-step curiosity lookahead with ε-exploration and a cold-start gate."""

    def __init__(self, params: PolicyParams):
        self.params = params
        self.last_was_directed = False  # telemetry only; overwritten every step

    def select_action(self, context: PolicyContext, rng: np.random.Generator) -> int:
        # Fixed draw order (research R3): one uniform for the ε-gate, then one
        # integer draw only on the random path. Exploit draws nothing further.
        explore = rng.random() < self.params.exploration_epsilon
        immature = (
            context.best_frame_age is None
            or context.best_frame_age < self.params.lookahead_min_age_cycles
        )
        if explore or immature:
            self.last_was_directed = False
            return int(rng.integers(context.n_actions))

        best_action = 0
        best_value = -np.inf
        for action in range(context.n_actions):  # ascending: lowest index wins ties
            predicted = context.predict_decoded(action)
            if predicted is None:
                continue
            value = context.drive_value_of(predicted)
            if value > best_value:
                best_value = value
                best_action = action
        self.last_was_directed = True
        return best_action
