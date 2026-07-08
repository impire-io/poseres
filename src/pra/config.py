"""Configuration (PRA-01 §8, data-model §1, contracts/config.md).

A frozen dataclass exposing every PRA-01 §8 parameter with its spec default plus
the harness-only ``horizon_checkpoints``. Construction validates ranges before
any run starts. ``true_dim`` is *world* configuration known to the harness for
scoring T4; it is never passed into the system-under-test as an input.
"""

from __future__ import annotations

import dataclasses
from dataclasses import dataclass
from typing import Literal

__all__ = ["Config", "ScoringMode", "PolicyMode", "OBS_DIM_REF", "HIDDEN_REF", "TRUE_DIM_REF"]

ScoringMode = Literal["predictive", "effort_only", "identity"]
PolicyMode = Literal["random", "curiosity"]

# The validated reference scale (PRA-02 §1 defaults). Every scale-dependent
# constant below was validated AT this scale; the effective_* rules hold the
# validated *regime* constant as dimensions grow, and are exactly the raw
# constants at the reference (all scale factors equal 1). See
# design/validate/SCALE-DIAGNOSIS.md for the evidence behind each rule.
OBS_DIM_REF = 10
HIDDEN_REF = 12
TRUE_DIM_REF = 3


@dataclass(frozen=True)
class Config:
    # --- World (PRA-02 §1) ---
    true_dim: int = 3
    obs_dim: int = 10
    n_objects: int = 4
    n_actions: int = 4
    sensor_noise_std: float = 0.04
    action_scale: float = 0.4

    # --- Frame (PRA-01 §5) ---
    hidden_size: int = 12
    init_weight_scale: float = 0.3
    learning_rate: float = 0.03
    gradient_clip: float = 1.0
    ema_decay: float = 0.9

    # --- Gate / birth ---
    fit_gate: float = 1.0
    initial_dim_min: int = 2
    initial_dim_max: int = 6

    # --- Scorer (PRA-01 §6.2) ---
    scoring_mode: ScoringMode = "predictive"
    w_explain: float = 0.5
    w_predict: float = 0.5
    w_effort: float = 0.0
    w_complexity: float = 0.04

    # --- Proposal (PRA-01 §6.5) ---
    exploit_prob: float = 0.75
    explore_dim_max_offset: int = 4

    # --- Decay (PRA-01 §6.4) ---
    survive_threshold_base: float = 0.8
    survive_threshold_pop_coeff: float = 0.04
    survive_threshold_pop_baseline: int = 4
    spawn_per_cycle: int = 1
    min_age_cycles: int = 2
    min_frames: int = 1
    max_frames: int = 200

    # --- Schedule ---
    warmup_episodes: int = 25
    n_cycles: int = 18
    episodes_per_cycle: int = 6
    steps_per_episode: int = 40
    seeds: tuple[int, ...] = tuple(range(1, 9))

    # --- Drives (Doc 05 §2-§3; [O]-tagged internals are first-class tunables) ---
    drive_weights: tuple[tuple[str, float], ...] = (("curiosity", 1.0),)
    w_progress: float = 1.0
    w_novelty: float = 1.0
    lp_recent_window: int = 60
    lp_baseline_window: int = 600
    novelty_memory_size: int = 200

    # --- Policy (Doc 05 §4). "random" is the pinned validation baseline: every
    # existing mode keeps it and stays byte-identical to the validated build. ---
    policy_mode: PolicyMode = "random"
    exploration_epsilon: float = 0.1
    lookahead_min_age_cycles: int = 2

    # --- Persistence (Doc 06). 0 = off: no snapshots, no files, validated modes
    # byte-identical to the validated build (feature 003 FR-009). ---
    snapshot_every_n_cycles: int = 0

    # --- Harness-only ---
    horizon_checkpoints: tuple[int, ...] = (18, 30, 50)

    def __post_init__(self) -> None:
        self._validate()

    def _validate(self) -> None:
        def require(cond: bool, msg: str) -> None:
            if not cond:
                raise ValueError(f"Config: {msg}")

        require(self.true_dim >= 1, "true_dim must be >= 1")
        require(self.obs_dim >= 1, "obs_dim must be >= 1")
        require(self.n_objects >= 1, "n_objects must be >= 1")
        require(self.n_actions >= 1, "n_actions must be >= 1")
        require(self.sensor_noise_std >= 0, "sensor_noise_std must be >= 0")
        require(self.action_scale > 0, "action_scale must be > 0")

        require(self.hidden_size >= 1, "hidden_size must be >= 1")
        require(self.init_weight_scale > 0, "init_weight_scale must be > 0")
        require(self.learning_rate > 0, "learning_rate must be > 0")
        require(self.gradient_clip > 0, "gradient_clip must be > 0")
        require(0.0 <= self.ema_decay < 1.0, "ema_decay must be in [0, 1)")

        require(self.fit_gate > 0, "fit_gate must be > 0")
        require(self.initial_dim_min >= 1, "initial_dim_min must be >= 1")
        require(
            self.initial_dim_max >= self.initial_dim_min,
            "initial_dim_max must be >= initial_dim_min",
        )

        require(
            self.scoring_mode in ("predictive", "effort_only", "identity"),
            "scoring_mode must be 'predictive', 'effort_only', or 'identity'",
        )
        for name in ("w_explain", "w_predict", "w_effort", "w_complexity"):
            require(getattr(self, name) >= 0, f"{name} must be >= 0")

        require(0.0 <= self.exploit_prob <= 1.0, "exploit_prob must be in [0, 1]")
        require(self.explore_dim_max_offset >= 1, "explore_dim_max_offset must be >= 1")

        require(self.survive_threshold_base > 0, "survive_threshold_base must be > 0")
        require(
            self.survive_threshold_pop_coeff >= 0,
            "survive_threshold_pop_coeff must be >= 0",
        )
        require(
            self.survive_threshold_pop_baseline >= 0,
            "survive_threshold_pop_baseline must be >= 0",
        )
        require(self.spawn_per_cycle >= 0, "spawn_per_cycle must be >= 0")
        require(self.min_age_cycles >= 0, "min_age_cycles must be >= 0")
        require(self.min_frames >= 1, "min_frames must be >= 1")
        require(self.max_frames >= self.min_frames, "max_frames must be >= min_frames")

        require(self.warmup_episodes >= 0, "warmup_episodes must be >= 0")
        require(self.n_cycles >= 0, "n_cycles must be >= 0")
        require(self.episodes_per_cycle >= 1, "episodes_per_cycle must be >= 1")
        require(self.steps_per_episode >= 1, "steps_per_episode must be >= 1")
        require(len(self.seeds) >= 1, "seeds must contain at least one seed")

        require(len(self.drive_weights) >= 1, "drive_weights must be non-empty")
        names = [n for n, _ in self.drive_weights]
        require(len(set(names)) == len(names), "drive_weights names must be unique")
        require(
            all(w >= 0 and w == w for _, w in self.drive_weights),
            "drive weights must be finite and >= 0",
        )
        require(self.w_progress >= 0, "w_progress must be >= 0")
        require(self.w_novelty >= 0, "w_novelty must be >= 0")
        require(self.lp_recent_window >= 1, "lp_recent_window must be >= 1")
        require(
            self.lp_baseline_window > self.lp_recent_window,
            "lp_baseline_window must be > lp_recent_window",
        )
        require(self.novelty_memory_size >= 1, "novelty_memory_size must be >= 1")

        require(
            self.policy_mode in ("random", "curiosity"),
            "policy_mode must be 'random' or 'curiosity'",
        )
        require(
            0.0 <= self.exploration_epsilon <= 1.0,
            "exploration_epsilon must be in [0, 1]",
        )
        require(self.lookahead_min_age_cycles >= 0, "lookahead_min_age_cycles must be >= 0")
        require(self.snapshot_every_n_cycles >= 0, "snapshot_every_n_cycles must be >= 0")

        require(len(self.horizon_checkpoints) >= 1, "horizon_checkpoints must be non-empty")
        require(
            all(c >= 1 for c in self.horizon_checkpoints),
            "every horizon checkpoint must be >= 1",
        )
        require(
            all(
                b < a
                for b, a in zip(
                    self.horizon_checkpoints, self.horizon_checkpoints[1:], strict=False
                )
            ),
            "horizon_checkpoints must be strictly ascending",
        )

    @property
    def effective_n_cycles(self) -> int:
        """Run length that guarantees every horizon checkpoint is reached
        (data-model §1): ``max(n_cycles, max(horizon_checkpoints))``."""
        return max(self.n_cycles, max(self.horizon_checkpoints))

    # --- Scale-invariant parameter rules [D] (SCALE-DIAGNOSIS layers 2 & 4) ---
    # SGD's stability threshold shrinks as ‖obs‖² grows (∝ obs_dim): the raw
    # learning_rate diverges at obs_dim=60. The parsimony term must stay
    # commensurate with the per-dim error span, which flattens as the world's
    # information spreads over more observation dims. Both rules are exactly the
    # raw constants at the reference scale.

    @property
    def effective_learning_rate(self) -> float:
        """``learning_rate · (OBS_DIM_REF / obs_dim)^1.5`` — 0.03 at the reference.

        The naive stability bound gives exponent 1 (‖obs‖² ∝ obs_dim), but the
        outer-product gradients also grow with input norms; the 1.5 exponent is
        the empirically supported rule (recipe probe, SCALE-DIAGNOSIS §5:
        lr=0.002 dominates lr=0.005 at obs_dim=60 across every scanned dim).
        """
        return self.learning_rate * (OBS_DIM_REF / self.obs_dim) ** 1.5

    @property
    def effective_w_complexity(self) -> float:
        """``w_complexity · (OBS_DIM_REF / obs_dim)`` — 0.04 at the reference."""
        return self.w_complexity * (OBS_DIM_REF / self.obs_dim)

    @property
    def effective_min_age_cycles(self) -> int:
        """``round(min_age_cycles · (obs_dim / OBS_DIM_REF)^1.5)`` — 2 at the reference.

        The young-frame protection window must scale with convergence time, which
        grows by the same factor the effective learning rate shrank: judged at the
        raw window, a scaled candidate is evicted on its transient score (~0.85)
        long before its asymptote (~0.44), and selection freezes at low dim
        regardless of schedule length (SCALE-DIAGNOSIS §7: patience 2/12/24/29 →
        mean best_dim 4.7/5.7/6.7/10.7 at true_dim=20, one seed reaching 18).
        """
        return int(round(self.min_age_cycles * (self.obs_dim / OBS_DIM_REF) ** 1.5))

    def replace(self, **changes: object) -> Config:
        """Return a validated copy with ``changes`` applied."""
        return dataclasses.replace(self, **changes)
