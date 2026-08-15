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

__all__ = [
    "PolicyContext",
    "Policy",
    "RandomPolicy",
    "CuriosityLookaheadPolicy",
    "CompletionItchPolicy",
    "PolicyParams",
]


def _no_event_delta(action: int) -> None:
    """The inert default: the event head is off (feature 040)."""
    return None


@dataclass(frozen=True)
class PolicyContext:
    """The read-only view a policy selects from (data-model §3)."""

    observation: np.ndarray
    n_actions: int
    best_frame_age: int | None  # None when no frame exists
    predict_decoded: Callable[[int], np.ndarray | None]  # best-frame one-step, decoded
    drive_value_of: Callable[[np.ndarray], float]  # drive set valued at a hypothetical obs
    # Event-head one-step delta (feature 040): the predicted next-observation
    # delta for an action at the current observation; None whenever the head
    # is off. Defaulted so every pre-040 construction site stays valid
    # (keyword-only-legal minor addition, Doc 0008).
    predict_event_delta: Callable[[int], np.ndarray | None] = _no_event_delta


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


class CompletionItchPolicy:
    """The measured completion itch (feature 040; motivation-stack G3,
    episode 0071): value each candidate action as the drive term, plus an
    optional caller-injected per-action term, plus κ · (progress_after −
    progress_now) — the itch read from the event head with the learnable
    completion rule (a predicted pocket gain above ``completion_threshold``
    counts progress as full; else clipped sensed progress + predicted delta).

    Draw order, ε/maturity gating, the frames candidate-skip rule, and
    lowest-index tie-breaking are identical to
    :class:`CuriosityLookaheadPolicy`; with the event head off the itch term
    is inert and selection reduces to drive + potential. ``progress_index``
    and ``pocket_index`` are anatomy-specific constructor knowledge (e.g. the
    Minecraft anatomy's ``C1_MINING_INDEX``/``C1_POCKET_TOTAL_INDEX``) and are
    validated against the observation width on first selection. The measured
    operating point is κ = 0.25 with ``event_head_eta = 0.5``; the itch
    composes — G1 measured itch-without-hold at 2/8 digging, 0/8 chains — so
    ``potential_of`` exists to inject a stay-near-the-work term.

    The honesty watch (bounded, measurement-only — never a selection input):
    ``completions_fired``, ``false_completions`` (a fired completion whose
    realized pocket delta at the next observation did not clear the
    threshold), and ``progress_pred_error_ema`` (EMA, decay 0.99, of
    |predicted − realized| progress delta on chosen directed actions).
    """

    _EMA_DECAY = 0.99

    def __init__(
        self,
        params: PolicyParams,
        *,
        kappa: float,
        progress_index: int,
        pocket_index: int,
        completion_threshold: float = 1.0 / 128.0,
        potential_of: Callable[[int], float] | None = None,
        label_index: int | None = None,
        label_beta: float = 0.0,
        deficit_index: int | None = None,
        deficit_kappa: float = 0.0,
        commit_kappa: float = 0.0,
        explore_defers_holds: bool = False,
    ):
        self.params = params
        self.kappa = float(kappa)
        self.progress_index = int(progress_index)
        self.pocket_index = int(pocket_index)
        self.completion_threshold = float(completion_threshold)
        self.potential_of = potential_of
        # the praise label (feature 041; E3.1 + recipe-reach measured): read
        # ONLY inside fired completions — the hangover mechanism cannot form.
        # None (default) = off: bit-exact v1.2.0 behavior.
        self.label_index = None if label_index is None else int(label_index)
        self.label_beta = float(label_beta)
        # the deficit gate (feature 042; episodes 0083/0084 measured): the
        # label weight grows with the sensed homeostatic deficit — sated
        # silent, depleted insistent. None/0.0 (default) = bit-exact v1.3.0.
        self.deficit_index = None if deficit_index is None else int(deficit_index)
        self.deficit_kappa = float(deficit_kappa)
        if self.deficit_index is not None and self.label_index is None:
            raise ValueError("CompletionItchPolicy: deficit_index requires label_index")
        if not np.isfinite(self.deficit_kappa) or self.deficit_kappa < 0.0:
            raise ValueError(
                f"CompletionItchPolicy: deficit_kappa {self.deficit_kappa} must be finite and >= 0"
            )
        # commitment (research topic the-last-crack, 2026-08-15 — instrument
        # grade, ships only on promotion): the L1 trace measured the hold's
        # per-step margin (κ·Δ̂ ≈ 0.008) thinner than frame-to-frame drive
        # noise (release margins 0.00002–0.069), and the ε-gate killing
        # WINNING holds (one at progress 0.994) — a 30-frame live dig must
        # win 30 near-coin-flips in a row. ``commit_kappa`` pays repeating
        # the previous action while sensed progress advances (hysteresis
        # against the noise); ``explore_defers_holds`` makes the ε-gate
        # defer while progress advances. 0.0/False (default) = bit-exact
        # shipped behavior, RNG stream included.
        self.commit_kappa = float(commit_kappa)
        self.explore_defers_holds = bool(explore_defers_holds)
        if not np.isfinite(self.commit_kappa) or self.commit_kappa < 0.0:
            raise ValueError(
                f"CompletionItchPolicy: commit_kappa {self.commit_kappa} must be finite and >= 0"
            )
        self.last_was_directed = False  # telemetry only; overwritten every step
        self.completions_fired = 0
        self.false_completions = 0
        self.progress_pred_error_ema = 0.0
        self._prev_obs: np.ndarray | None = None
        self._pending_delta: float | None = None
        self._pending_completion = False
        self._indices_checked = False
        self._last_action: int | None = None

    def _label_weight(self, obs: np.ndarray) -> float:
        """The effective label weight (feature 042): the static ``label_beta``
        plus ``deficit_kappa · clip(1 − obs[deficit_index], 0, 1)``. Disabled
        (index ``None`` or gain 0) returns ``label_beta`` exactly, with no
        observation read."""
        beta = self.label_beta
        if self.deficit_index is not None and self.deficit_kappa > 0.0:
            deficit = min(max(1.0 - float(obs[self.deficit_index]), 0.0), 1.0)
            beta += self.deficit_kappa * deficit
        return beta

    def _settle_watch(self, obs: np.ndarray) -> None:
        """Resolve last step's predictions against the realized observation."""
        if self._prev_obs is None:
            return
        if self._pending_delta is not None:
            realized = float(obs[self.progress_index]) - float(self._prev_obs[self.progress_index])
            err = abs(self._pending_delta - realized)
            d = self._EMA_DECAY
            self.progress_pred_error_ema = d * self.progress_pred_error_ema + (1.0 - d) * err
            self._pending_delta = None
        if self._pending_completion:
            realized_gain = float(obs[self.pocket_index]) - float(self._prev_obs[self.pocket_index])
            if realized_gain <= self.completion_threshold:
                self.false_completions += 1
            self._pending_completion = False

    def select_action(self, context: PolicyContext, rng: np.random.Generator) -> int:
        obs = context.observation
        if not self._indices_checked:
            idxs = (
                [self.progress_index, self.pocket_index]
                + ([] if self.label_index is None else [self.label_index])
                + ([] if self.deficit_index is None else [self.deficit_index])
            )
            hi = max(idxs)
            lo = min(idxs)
            if lo < 0 or hi >= obs.shape[0]:
                raise ValueError(
                    f"CompletionItchPolicy: channel index {hi if hi >= obs.shape[0] else lo} "
                    f"out of range for obs_dim {obs.shape[0]}"
                )
            self._indices_checked = True
        self._settle_watch(obs)
        # incumbency dies with its intention (the L2 pair measured the twin:
        # without this boundary the committed vote locked DIG for 517
        # consecutive frames across breaks — perseveration): a progress
        # collapse is the world's own completion/reset, and the next vote
        # runs fresh
        if (
            self._prev_obs is not None
            and float(self._prev_obs[self.progress_index]) - float(obs[self.progress_index]) > 0.5
        ):
            self._last_action = None
        # a held intention is advancing when sensed progress rose since the
        # previous frame (or sits pinned at the top awaiting the world's own
        # confirmation) — read BEFORE _prev_obs is overwritten
        advancing = (
            self._last_action is not None
            and self._prev_obs is not None
            and (
                float(obs[self.progress_index]) > float(self._prev_obs[self.progress_index]) + 1e-9
                or float(obs[self.progress_index]) >= 0.995
            )
        )
        self._prev_obs = np.array(obs, copy=True)
        # Fixed draw order (research R3, identical to CuriosityLookaheadPolicy):
        # one uniform for the ε-gate, then one integer draw only on the random
        # path. Exploit draws nothing further.
        explore = rng.random() < self.params.exploration_epsilon
        if explore and self.explore_defers_holds and advancing:
            explore = False  # the-last-crack: exploration defers to a live hold
        immature = (
            context.best_frame_age is None
            or context.best_frame_age < self.params.lookahead_min_age_cycles
        )
        if explore or immature:
            self.last_was_directed = False
            action = int(rng.integers(context.n_actions))
            self._last_action = action
            return action

        progress_now = float(obs[self.progress_index])
        label_weight = self._label_weight(obs)  # one observation, one weight
        best_action = 0
        best_value = -np.inf
        best_delta: float | None = None
        best_completion = False
        for action in range(context.n_actions):  # ascending: lowest index wins ties
            predicted = context.predict_decoded(action)
            if predicted is None:
                continue
            value = context.drive_value_of(predicted)
            if self.potential_of is not None:
                value += self.potential_of(action)
            delta = context.predict_event_delta(action)
            completion = False
            if delta is not None:
                completion = float(delta[self.pocket_index]) > self.completion_threshold
                if completion:
                    progress_after = 1.0
                    if self.label_index is not None:
                        progress_after += label_weight * min(
                            max(float(delta[self.label_index]), 0.0), 1.0
                        )
                else:
                    progress_after = min(
                        max(progress_now + float(delta[self.progress_index]), 0.0), 1.0
                    )
                value += self.kappa * (progress_after - progress_now)
            if self.commit_kappa > 0.0 and action == self._last_action and advancing:
                value += self.commit_kappa  # the-last-crack: incumbency holds
            if value > best_value:
                best_value = value
                best_action = action
                best_delta = None if delta is None else float(delta[self.progress_index])
                best_completion = completion
        self.last_was_directed = True
        self._pending_delta = best_delta
        if best_completion:
            self.completions_fired += 1
            self._pending_completion = True
        self._last_action = best_action
        return best_action
