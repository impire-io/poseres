"""Core data contracts (PRA-01 §3, data-model §2).

These are the values that cross the Bus boundary between the world, the Engine,
and the frames. Their null-rules are part of the contract and are enforced at
construction so a malformed event/result cannot enter the system silently.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

__all__ = ["SensorimotorEvent", "FrameResult", "GlobalPose", "FrameState"]


@dataclass(frozen=True)
class SensorimotorEvent:
    """One step the system observes (PRA-01 §3.1).

    ``previous_observation`` and ``action`` are null **only** on the first event
    of an episode, and otherwise carry the true prior step regardless of any
    frame's map/drop decision.
    """

    observation: np.ndarray
    previous_observation: np.ndarray | None = None
    action: int | None = None

    def __post_init__(self) -> None:
        if (self.previous_observation is None) != (self.action is None):
            raise ValueError(
                "previous_observation and action must both be set or both be None "
                "(null only on the first event of an episode)"
            )

    @property
    def has_previous(self) -> bool:
        return self.previous_observation is not None


@dataclass(frozen=True)
class FrameResult:
    """A single frame's response to an event (PRA-01 §3.2).

    Null-rules: ``local_pose`` and ``recon_error`` are null iff ``mapped`` is
    false; ``pred_error`` and ``effort`` are additionally null when there is no
    previous observation to predict from.
    """

    frame_id: int
    mapped: bool
    local_pose: np.ndarray | None = None
    recon_error: float | None = None
    pred_error: float | None = None
    effort: float | None = None

    def __post_init__(self) -> None:
        if self.mapped:
            if self.local_pose is None or self.recon_error is None:
                raise ValueError("mapped result must carry local_pose and recon_error")
        else:
            if self.local_pose is not None or self.recon_error is not None:
                raise ValueError("unmapped result must have null local_pose and recon_error")


@dataclass(frozen=True)
class GlobalPose:
    """The Engine's assembled view: one local pose per frame that mapped the
    observation (PRA-01 §3.4). Telemetry only; never persisted."""

    poses: dict[int, np.ndarray]

    def __len__(self) -> int:
        return len(self.poses)


@dataclass
class FrameState:
    """A frame's identity/survival record (data-model §2).

    The weights live in the :class:`~pra.core.frame.FrameGroup` arrays; this is
    the per-frame bookkeeping the Engine reasons over (identity, age, survival
    EMAs). Init rules (PRA-01 §5.3): EMAs start at 1.0 for a zero-start birth and
    0.9 for a candidate spawned in an offline cycle; ``age_cycles = 0``,
    ``is_candidate = True``.
    """

    frame_id: int
    dim: int
    is_candidate: bool = True
    age_cycles: int = 0
    recon_err_ema: float = 1.0
    pred_err_ema: float = 1.0
    effort_ema: float = 0.0
