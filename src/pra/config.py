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

__all__ = ["Config", "ScoringMode"]

ScoringMode = Literal["predictive", "effort_only"]


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
            self.scoring_mode in ("predictive", "effort_only"),
            "scoring_mode must be 'predictive' or 'effort_only'",
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

    def replace(self, **changes: object) -> Config:
        """Return a validated copy with ``changes`` applied."""
        return dataclasses.replace(self, **changes)
