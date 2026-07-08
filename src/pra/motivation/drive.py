"""Drives: fixed innate preferences producing the value signal (Doc 05 §2-§3).

A Drive is a pure function of a read-only context and its own frozen parameters
— no RNG, no hidden mutable policy state (Doc 05 §2.1). Parameters are
structurally immutable (frozen dataclasses): the running system cannot modify
its own drive (Doc 05 §6, mandatory). The curiosity drive's *bookkeeping* — the
prediction-error history and the bounded recent-observation memory — is state,
not policy (Doc 05 §3.3), owned by the drive and updated only after valuation.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Protocol, runtime_checkable

import numpy as np

from pra.config import Config
from pra.motivation.context import DriveContext

__all__ = ["Drive", "CuriosityDrive", "CuriosityParams", "CompetenceDrive", "WeightedDriveSet"]

_EPS = 1e-6


@runtime_checkable
class Drive(Protocol):
    def id(self) -> str: ...
    def value(self, context: DriveContext) -> float: ...


@dataclass(frozen=True)
class CuriosityParams:
    """Frozen curiosity parameters (FR-003; [O]-tagged tunables from Doc 07)."""

    w_progress: float
    w_novelty: float
    lp_recent_window: int
    lp_baseline_window: int
    novelty_memory_size: int

    @classmethod
    def from_config(cls, config: Config) -> CuriosityParams:
        return cls(
            w_progress=config.w_progress,
            w_novelty=config.w_novelty,
            lp_recent_window=config.lp_recent_window,
            lp_baseline_window=config.lp_baseline_window,
            novelty_memory_size=config.novelty_memory_size,
        )


class CuriosityDrive:
    """Curiosity = learning progress + novelty, with automatic cold-start handover.

    Pure: the drive holds only frozen parameters; the bookkeeping it evaluates
    (prediction-error history, recent-observation memory) is run state owned by
    the Engine and exposed read-only through the :class:`DriveContext`
    (Doc 05 §3.3 — "bookkeeping, not policy"; never persisted).

    - ``learning_progress = max(0, mean(baseline window) − mean(recent window))``
      over the engine's per-step mean mapped prediction error; 0 until the
      history holds at least ``lp_recent_window`` samples. Rewards *reduction* in
      error: mastered (low flat) and unlearnable (high flat) regions both yield
      ~0 — the anti-noise-trap property (Doc 05 §3.1).
    - ``novelty = min-distance unfamiliarity`` of the observation against the
      bounded recent-observation memory; an empty memory yields 1.0 (maximal
      unfamiliarity — finite from the very first step, FR-001) (Doc 05 §3.2).
    """

    def __init__(self, params: CuriosityParams):
        self.params = params

    def id(self) -> str:
        return "curiosity"

    # ---- terms (pure; no RNG) -------------------------------------------------
    def learning_progress(self, history: Sequence[float]) -> float:
        p = self.params
        if len(history) < p.lp_recent_window:
            return 0.0
        arr = np.asarray(history, dtype=np.float64)
        recent = float(arr[-p.lp_recent_window :].mean())
        baseline = float(arr.mean())
        return max(0.0, baseline - recent)

    def novelty(self, observation: np.ndarray, memory: Sequence[np.ndarray]) -> float:
        if len(memory) == 0:
            return 1.0
        stack = np.asarray(memory, dtype=np.float64)
        dists = np.linalg.norm(stack - observation, axis=1)
        return float(dists.min() / (np.linalg.norm(observation) + _EPS))

    def value(self, context: DriveContext) -> float:
        p = self.params
        lp = self.learning_progress(context.recent_pred_errors)
        nov = self.novelty(context.observation, context.observation_memory)
        return p.w_progress * lp + p.w_novelty * nov


class CompetenceDrive:
    """Competence: the fixed terminal counter-pole to curiosity (Doc 05 §5 —
    "rewards mastering: driving prediction error low and keeping it low").

    Two terms, both pure functions of the context:
    - **mastery** = ``max(0, 1 − mean(recent pred errors))`` — high when the
      system predicts well and keeps predicting well (the "keeping it low"
      reading); history-shaped, so constant across one-step lookahead candidates.
    - **familiarity** = ``1 − novelty`` — high for observations close to recent
      experience; the per-candidate term that steers the lookahead toward
      practice on what the system already almost knows.

    Empirical grounding (AGENCY-DIAGNOSIS E5): at `true_dim=20` the
    familiarity-directed lookahead beats random exploration (margin +0.067,
    better in 6/8 seeds) where novelty-directed curiosity loses (−0.062) — in a
    uniformly learnable world, concentrated practice is what pays. The
    curiosity/competence *blend* for richer worlds is the open §5 question.
    """

    def __init__(self, params: CuriosityParams):
        self.params = params  # shares the novelty-memory/window parameters

    def id(self) -> str:
        return "competence"

    def mastery(self, history: Sequence[float]) -> float:
        p = self.params
        if len(history) < p.lp_recent_window:
            return 0.0
        arr = np.asarray(history, dtype=np.float64)  # history may be a deque: no slicing
        recent = float(arr[-p.lp_recent_window :].mean())
        return max(0.0, 1.0 - recent)

    def familiarity(self, observation: np.ndarray, memory: Sequence[np.ndarray]) -> float:
        if len(memory) == 0:
            return 0.0  # nothing is familiar yet; competence is silent at cold start
        stack = np.asarray(memory, dtype=np.float64)
        dists = np.linalg.norm(stack - observation, axis=1)
        return max(0.0, 1.0 - float(dists.min() / (np.linalg.norm(observation) + _EPS)))

    def value(self, context: DriveContext) -> float:
        return self.mastery(context.recent_pred_errors) + self.familiarity(
            context.observation, context.observation_memory
        )


class WeightedDriveSet:
    """Fixed weighted sum of drives (Doc 05 §2.2): ``Σ w[d.id()]·d.value(ctx)``.

    Weights are fixed at configuration; evaluation follows registration order so
    float accumulation is deterministic. Construction rejects any mismatch
    between configured weights and registered drive ids.
    """

    def __init__(self, drives: tuple[Drive, ...], weights: tuple[tuple[str, float], ...]):
        weight_map = dict(weights)
        ids = [d.id() for d in drives]
        if sorted(ids) != sorted(weight_map):
            raise ValueError(
                f"drive_weights {sorted(weight_map)} must match registered drives {sorted(ids)}"
            )
        self._drives = tuple(drives)
        self._weights = tuple(weight_map[d.id()] for d in drives)

    @classmethod
    def from_config(cls, config: Config) -> WeightedDriveSet:
        """The base build registers curiosity only (Doc 05 §5); a counter-drive
        is added by configuring its weight and registering it here — no other
        component changes (US5)."""
        drives: list[Drive] = []
        for name, _ in config.drive_weights:
            if name == "curiosity":
                drives.append(CuriosityDrive(CuriosityParams.from_config(config)))
            elif name == "competence":
                drives.append(CompetenceDrive(CuriosityParams.from_config(config)))
            else:
                raise ValueError(f"unknown drive '{name}' in drive_weights")
        return cls(tuple(drives), config.drive_weights)

    @property
    def drives(self) -> tuple[Drive, ...]:
        return self._drives

    def value(self, context: DriveContext) -> float:
        return float(
            sum(w * d.value(context) for d, w in zip(self._drives, self._weights, strict=True))
        )
