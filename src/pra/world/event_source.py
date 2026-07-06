"""EventSource seam + SensorimotorWorld (PRA-01 §9.4, PRA-02 §1, contracts/seams.md §5).

The world is the input boundary. It has a hidden latent state and a **nonlinear**
(``tanh``) emission, so a purely linear frame genuinely cannot model it. It MUST
NOT expose ``true_dim``, latents, emission matrices, displacements, or object
indices to anything downstream — the only thing the system sees is the
observation vector. ``true_dim`` is known to the *harness* (via Config) for
scoring T4, never read off the world by the engine.

Draw order (fixed, for determinism — PRA-01 §7.1): per object ``start`` then
``emit``, in object-index order, then the action displacements. This mirrors the
v4 behavioral oracle exactly.

Scale normalization (SCALE-DIAGNOSIS layer 1): the emission pre-activation
``E·latent`` has variance ``true_dim``, so without correction the tanh saturates
into a near-binary sign channel as ``true_dim`` grows (65% saturated at 20 vs 18%
at the reference 3). The emission is therefore normalized by
``sqrt(true_dim / TRUE_DIM_REF)`` so every scale operates in the tanh regime the
reference world was validated in. The factor is exactly 1.0 at ``true_dim=3`` —
the validated reference world is byte-identical.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

import numpy as np

from pra.config import TRUE_DIM_REF, Config

__all__ = ["EventSource", "SensorimotorWorld"]


@runtime_checkable
class EventSource(Protocol):
    """Input boundary: begin an episode, then step it under an action."""

    @property
    def n_actions(self) -> int: ...

    @property
    def obs_dim(self) -> int: ...

    def reset(self) -> np.ndarray:
        """Begin a new episode; return the first observation."""
        ...

    def step(self, action: int) -> np.ndarray:
        """Apply an action; return the next observation."""
        ...


class SensorimotorWorld:
    """Default EventSource: ``n_objects`` latent objects with nonlinear emission.

    Hidden (never exposed): ``true_dim``, object latents, emission matrices,
    action displacements, current object index. Public surface is exactly
    ``reset``/``step`` plus the action-space and observation-space sizes the agent
    is allowed to know.
    """

    def __init__(self, config: Config, rng: np.random.Generator):
        self._obs_dim = int(config.obs_dim)
        self._n_actions = int(config.n_actions)
        self._noise_std = float(config.sensor_noise_std)
        self._rng = rng
        true_dim = int(config.true_dim)
        # Emission normalization; exactly 1.0 at the reference true_dim (see module doc).
        self._emit_norm = float(np.sqrt(true_dim / TRUE_DIM_REF))

        # Draw order: per object (start, emit), then actions. Hidden from system.
        self.__objects: list[tuple[np.ndarray, np.ndarray]] = []
        for _ in range(int(config.n_objects)):
            start = rng.standard_normal(true_dim)
            emit = rng.standard_normal((self._obs_dim, true_dim))
            self.__objects.append((start, emit))
        self.__actions: list[np.ndarray] = [
            rng.standard_normal(true_dim) * config.action_scale for _ in range(self._n_actions)
        ]

        self.__latent: np.ndarray | None = None
        self.__obj: int | None = None

    @property
    def n_actions(self) -> int:
        return self._n_actions

    @property
    def obs_dim(self) -> int:
        return self._obs_dim

    def reset(self) -> np.ndarray:
        self.__obj = int(self._rng.integers(len(self.__objects)))
        self.__latent = self.__objects[self.__obj][0].copy()
        return self._emit()

    def step(self, action: int) -> np.ndarray:
        if self.__latent is None:
            raise RuntimeError("step() called before reset()")
        self.__latent = self.__latent + self.__actions[action]
        return self._emit()

    def _emit(self) -> np.ndarray:
        assert self.__latent is not None and self.__obj is not None
        emit = self.__objects[self.__obj][1]
        clean = np.tanh(emit @ self.__latent / self._emit_norm)
        return clean + self._rng.standard_normal(self._obs_dim) * self._noise_std
