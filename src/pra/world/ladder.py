"""The complexity ladder — worlds that get harder in known ways (feature 005,
ROADMAP A3; spec/contracts in ``specs/005-complexity-ladder/``).

Three opt-in ``EventSource`` worlds, each one known difficulty axis off the
validated reference world, selected by ``Config.world`` through
:func:`make_world` (the factory the harness passes as ``world_factory`` —
zero engine changes):

- ``nonuniform`` (L1): a half-space region of latent space (``latent[0] > 0``)
  where the transition gains fresh Gaussian noise — unlearnable dynamics the
  agent's own actions carry it into and out of (the A4 noisy-TV/camping
  testbed). World-side occupancy counters; harness-only readings.
- ``compositional`` (L2): factored dynamics — action ``a`` displaces only
  factor group ``a mod K`` — under the reference *joint* emission, so the
  parts never leak through channels.
- ``distractor`` (L3): extra observation channels driven by an autonomous
  fixed-drift latent (``structured``) or fresh unit noise (``noise``) —
  signal that carries zero action information.

**Draw-order discipline (the degenerate-dial contract).** Each world
replicates the reference world's draw sequence exactly — construction: per
object ``start`` then ``emit`` in object order, then the action
displacements; per step: displacement lookup (no draw), then rung-specific
draws (only when the dial is non-degenerate), then the sensor-noise draw.
At its degenerate dial every rung consumes *exactly* the reference
sequence, so engine summaries are byte-identical to ``SensorimotorWorld``
— pinned by integration tests, which is also what guards the deliberate
duplication of the ~40-line reference core here (the reference world is
byte-frozen and cannot drift; ``design/validate/`` records why it must
not be modified even for subclass hooks).

**Ground-truth hiding.** The ``EventSource`` surface (``reset``/``step``/
``obs_dim``/``n_actions``) exposes nothing about regions, groups, or
splits; ground truth and occupancy counters are behind the harness-only
``ladder_readings()`` accessor, which the engine never calls.

**Occupancy definition (L1).** A step is "in-region" iff the latent the
agent acted *from* (pre-displacement) lies in the region; ``reset()`` is
not counted. Counters are per-process instruments read by the ladder
runner after a run (they are not snapshot state).
"""

from __future__ import annotations

import numpy as np

from pra.config import TRUE_DIM_REF, Config
from pra.world.event_source import EventSource, SensorimotorWorld

__all__ = [
    "NonUniformWorld",
    "CompositionalWorld",
    "DistractorWorld",
    "ShiftingWorld",
    "MultiRegionWorld",
    "make_world",
]


class _LadderWorldBase:
    """Shared reference core: reference draw order for construction, reset,
    and emission. Subclasses add their one difficulty axis on top.

    ``core_obs_dim`` is the controllable emission width. ``Config.obs_dim``
    always means the system-visible width (the anatomy precedent: the engine
    and the scale rules key off it), so L3 passes
    ``obs_dim − distractor_channels`` here and appends its channels on top.
    """

    def __init__(self, config: Config, rng: np.random.Generator, core_obs_dim: int | None = None):
        self._config = config
        self._core_obs_dim = int(config.obs_dim if core_obs_dim is None else core_obs_dim)
        self._n_actions = int(config.n_actions)
        self._noise_std = float(config.sensor_noise_std)
        self._rng = rng
        self._true_dim = int(config.true_dim)
        self._emit_norm = float(np.sqrt(self._true_dim / TRUE_DIM_REF))

        # Reference construction draws: per object (start, emit), then actions.
        self._objects: list[tuple[np.ndarray, np.ndarray]] = []
        for _ in range(int(config.n_objects)):
            start = rng.standard_normal(self._true_dim)
            emit = rng.standard_normal((self._core_obs_dim, self._true_dim))
            self._objects.append((start, emit))
        self._actions: list[np.ndarray] = [
            rng.standard_normal(self._true_dim) * config.action_scale
            for _ in range(self._n_actions)
        ]

        self._latent: np.ndarray | None = None
        self._obj: int | None = None

    @property
    def n_actions(self) -> int:
        return self._n_actions

    @property
    def obs_dim(self) -> int:
        return self._core_obs_dim

    def reset(self) -> np.ndarray:
        self._obj = int(self._rng.integers(len(self._objects)))
        self._latent = self._objects[self._obj][0].copy()
        return self._emit()

    def _require_latent(self) -> np.ndarray:
        if self._latent is None:
            raise RuntimeError("step() called before reset()")
        return self._latent

    def _emit_core(self) -> np.ndarray:
        """The reference clean emission of the current latent (no noise draw)."""
        assert self._latent is not None and self._obj is not None
        emit = self._objects[self._obj][1]
        return np.tanh(emit @ self._latent / self._emit_norm)

    def _emit(self) -> np.ndarray:
        clean = self._emit_core()
        return clean + self._rng.standard_normal(self._core_obs_dim) * self._noise_std

    # --- world-state capture (feature 008, optional protocol): mutable run
    # state only; construction is seed-derived. Subclasses extend. -----------
    def state_dict(self) -> dict:
        return {
            "latent": None if self._latent is None else np.array(self._latent, copy=True),
            "obj": self._obj,
        }

    def load_state_dict(self, state: dict) -> None:
        latent = state["latent"]
        self._latent = None if latent is None else np.array(latent, copy=True)
        self._obj = None if state["obj"] is None else int(state["obj"])


class NonUniformWorld(_LadderWorldBase):
    """L1 — unlearnable dynamics inside the half-space ``latent[0] > 0``.

    The transition from an in-region state gains ``N(0, region_noise_std²·I)``
    (drawn after the displacement, before emission); everywhere else the world
    is the reference. ``region_noise_std = 0`` is the degenerate dial: no
    extra draws, byte-identical behavior.
    """

    def __init__(self, config: Config, rng: np.random.Generator):
        super().__init__(config, rng)
        self._region_noise_std = float(config.region_noise_std)
        self._steps_in_region = 0
        self._steps_total = 0

    def step(self, action: int) -> np.ndarray:
        latent = self._require_latent()
        in_region = bool(latent[0] > 0)
        self._steps_total += 1
        if in_region:
            self._steps_in_region += 1
        self._latent = latent + self._actions[action]
        if in_region and self._region_noise_std > 0:
            self._latent = (
                self._latent + self._rng.standard_normal(self._true_dim) * self._region_noise_std
            )
        return self._emit()

    def state_dict(self) -> dict:
        state = super().state_dict()
        state["steps_in_region"] = self._steps_in_region
        state["steps_total"] = self._steps_total
        return state

    def load_state_dict(self, state: dict) -> None:
        super().load_state_dict(state)
        self._steps_in_region = int(state["steps_in_region"])
        self._steps_total = int(state["steps_total"])

    def ladder_readings(self) -> dict:
        """Harness-only ground truth + occupancy (never on the system surface)."""
        return {
            "rung": "l1",
            "region": "latent[0] > 0",
            "region_noise_std": self._region_noise_std,
            "steps_in_region": self._steps_in_region,
            "steps_total": self._steps_total,
            "occupancy": (self._steps_in_region / self._steps_total if self._steps_total else None),
        }


class CompositionalWorld(_LadderWorldBase):
    """L2 — factored dynamics under the reference joint emission.

    Hidden state = ``K`` independent groups of sizes ``factor_dims``
    (``sum == true_dim``); action ``a`` displaces only group ``a mod K``.
    Displacements are drawn exactly as reference and masked afterwards, so
    construction draws are byte-equal; ``factor_dims`` of ``()`` or
    ``(true_dim,)`` is the degenerate single-group dial (mask is a no-op).
    """

    def __init__(self, config: Config, rng: np.random.Generator):
        super().__init__(config, rng)
        dims = config.factor_dims if config.factor_dims else (self._true_dim,)
        self._factor_dims = tuple(int(d) for d in dims)
        offsets = np.cumsum((0, *self._factor_dims))
        self._group_slices = [
            slice(int(offsets[k]), int(offsets[k + 1])) for k in range(len(self._factor_dims))
        ]
        # Mask each already-drawn displacement to its group (a mod K).
        k_groups = len(self._factor_dims)
        self._action_group = [a % k_groups for a in range(self._n_actions)]
        for a, disp in enumerate(self._actions):
            mask = np.zeros(self._true_dim)
            mask[self._group_slices[self._action_group[a]]] = 1.0
            self._actions[a] = disp * mask

    def step(self, action: int) -> np.ndarray:
        latent = self._require_latent()
        self._latent = latent + self._actions[action]
        return self._emit()

    def ladder_readings(self) -> dict:
        """Harness-only ground truth (never on the system surface)."""
        return {
            "rung": "l2",
            "factor_dims": self._factor_dims,
            "action_group": list(self._action_group),
        }


class DistractorWorld(_LadderWorldBase):
    """L3 — appended channels that carry zero action information.

    An autonomous latent of size ``distractor_dim`` advances by a fixed
    drift vector every step (``structured`` mode: predictable in principle)
    and emits into ``distractor_channels`` extra channels through its own
    tanh emission; in ``noise`` mode the extra channels are fresh normals
    scaled by ``distractor_noise_std`` (default 1.0 — the original unit
    draw, bit-exact). Construction draws happen after all reference draws, in the
    documented order (start, drift, emission). ``distractor_channels = 0``
    is the degenerate dial: no extra draws, reference-width observation.
    """

    def __init__(self, config: Config, rng: np.random.Generator):
        super().__init__(config, rng, core_obs_dim=config.obs_dim - config.distractor_channels)
        self._d_channels = int(config.distractor_channels)
        self._d_dim = int(config.distractor_dim)
        self._d_mode = str(config.distractor_mode)
        self._d_noise_std = float(config.distractor_noise_std)
        if self._d_channels > 0:
            self._d_start = rng.standard_normal(self._d_dim)
            self._d_drift = rng.standard_normal(self._d_dim) * config.action_scale
            self._d_emit = rng.standard_normal((self._d_channels, self._d_dim))
            self._d_norm = float(np.sqrt(max(self._d_dim, 1) / TRUE_DIM_REF))
        self._d_latent: np.ndarray | None = None

    @property
    def obs_dim(self) -> int:
        # Total = Config.obs_dim (system-visible; the scale rules key off it);
        # the harness reports both widths (spec edge case).
        return self._core_obs_dim + self._d_channels

    def reset(self) -> np.ndarray:
        self._obj = int(self._rng.integers(len(self._objects)))
        self._latent = self._objects[self._obj][0].copy()
        if self._d_channels > 0:
            self._d_latent = self._d_start.copy()
        return self._emit()

    def step(self, action: int) -> np.ndarray:
        latent = self._require_latent()
        self._latent = latent + self._actions[action]
        if self._d_channels > 0 and self._d_mode == "structured":
            assert self._d_latent is not None
            self._d_latent = self._d_latent + self._d_drift
        return self._emit()

    def _emit(self) -> np.ndarray:
        clean = self._emit_core()
        obs_core = clean + self._rng.standard_normal(self._core_obs_dim) * self._noise_std
        if self._d_channels == 0:
            return obs_core
        if self._d_mode == "structured":
            assert self._d_latent is not None
            clean_d = np.tanh(self._d_emit @ self._d_latent / self._d_norm)
            obs_d = clean_d + self._rng.standard_normal(self._d_channels) * self._noise_std
        else:  # "noise": fresh normals scaled by the dose-response dial
            # (CHANNELNOISE-DIAGNOSIS); the default 1.0 is the original
            # unit-normal draw, bit-exact — same RNG stream, same bytes.
            obs_d = self._rng.standard_normal(self._d_channels) * self._d_noise_std
        return np.concatenate([obs_core, obs_d])

    def state_dict(self) -> dict:
        state = super().state_dict()
        state["d_latent"] = None if self._d_latent is None else np.array(self._d_latent, copy=True)
        return state

    def load_state_dict(self, state: dict) -> None:
        super().load_state_dict(state)
        d_latent = state["d_latent"]
        self._d_latent = None if d_latent is None else np.array(d_latent, copy=True)

    def ladder_readings(self) -> dict:
        """Harness-only ground truth (never on the system surface)."""
        return {
            "rung": "l3",
            "controllable_obs_dim": self._core_obs_dim,
            "distractor_channels": self._d_channels,
            "distractor_dim": self._d_dim,
            "distractor_mode": self._d_mode,
        }


class ShiftingWorld(_LadderWorldBase):
    """W1 — mastered-then-changing (feature 017, CAMPING-DIAGNOSIS).

    The reference world until ``shift_after_steps`` step observations have
    been emitted; from the next step on, the action-displacement set swaps
    to a second set drawn at construction (immediately after all reference
    draws, in action order) — the emission map is unchanged, what actions
    DO changes, and no RNG is consumed at shift time. ``shift_after_steps
    = 0`` is the degenerate dial: no extra draws, byte-identical behavior.
    """

    def __init__(self, config: Config, rng: np.random.Generator):
        super().__init__(config, rng)
        self._shift_after = int(config.shift_after_steps)
        if self._shift_after > 0:
            self._post_actions: list[np.ndarray] = [
                rng.standard_normal(self._true_dim) * config.action_scale
                for _ in range(self._n_actions)
            ]
        self._steps_emitted = 0

    def step(self, action: int) -> np.ndarray:
        latent = self._require_latent()
        shifted = self._shift_after > 0 and self._steps_emitted >= self._shift_after
        disp = self._post_actions[action] if shifted else self._actions[action]
        self._latent = latent + disp
        self._steps_emitted += 1
        return self._emit()

    def state_dict(self) -> dict:
        state = super().state_dict()
        state["steps_emitted"] = self._steps_emitted
        return state

    def load_state_dict(self, state: dict) -> None:
        super().load_state_dict(state)
        self._steps_emitted = int(state["steps_emitted"])

    def ladder_readings(self) -> dict:
        """Harness-only ground truth (never on the system surface)."""
        return {
            "rung": "shifting",
            "shift_after_steps": self._shift_after,
            "steps_emitted": self._steps_emitted,
            "shifted": bool(self._shift_after > 0 and self._steps_emitted >= self._shift_after),
        }


class MultiRegionWorld(_LadderWorldBase):
    """W2 — multi-region learnable (feature 017, CAMPING-DIAGNOSIS).

    The NonUniformWorld mechanism generalized: the sign-defined regions of
    ``latent[0]`` (2 levels) or ``(latent[0], latent[1])`` (4 levels) each
    carry their own transition-noise level; a 0.0 entry draws nothing inside
    its region (exactly the L1 degenerate branch). All levels are meant to
    stay inside the learnable band — difficulty, not noise traps.
    ``region_noise_levels = ()`` is the degenerate dial: no counters, no
    extra draws, byte-identical behavior.
    """

    def __init__(self, config: Config, rng: np.random.Generator):
        super().__init__(config, rng)
        self._levels = tuple(float(s) for s in config.region_noise_levels)
        self._steps_by_region = [0] * len(self._levels)

    def _region(self, latent: np.ndarray) -> int:
        if len(self._levels) == 2:
            return 1 if latent[0] > 0 else 0
        return (2 if latent[0] > 0 else 0) + (1 if latent[1] > 0 else 0)

    def step(self, action: int) -> np.ndarray:
        latent = self._require_latent()
        if self._levels:
            region = self._region(latent)
            self._steps_by_region[region] += 1
        self._latent = latent + self._actions[action]
        if self._levels and self._levels[region] > 0:
            self._latent = (
                self._latent + self._rng.standard_normal(self._true_dim) * self._levels[region]
            )
        return self._emit()

    def state_dict(self) -> dict:
        state = super().state_dict()
        state["steps_by_region"] = list(self._steps_by_region)
        return state

    def load_state_dict(self, state: dict) -> None:
        super().load_state_dict(state)
        self._steps_by_region = [int(x) for x in state["steps_by_region"]]

    def ladder_readings(self) -> dict:
        """Harness-only ground truth + per-region occupancy (never on the
        system surface)."""
        total = sum(self._steps_by_region)
        return {
            "rung": "multiregion",
            "region_noise_levels": list(self._levels),
            "steps_by_region": list(self._steps_by_region),
            "occupancy_by_region": ([s / total for s in self._steps_by_region] if total else None),
        }


def make_world(config: Config, rng: np.random.Generator) -> EventSource:
    """World factory keyed on ``Config.world`` — pass as the Engine's
    ``world_factory``. ``"reference"`` (the default) builds the untouched
    validated world."""
    if config.world == "nonuniform":
        return NonUniformWorld(config, rng)
    if config.world == "compositional":
        return CompositionalWorld(config, rng)
    if config.world == "distractor":
        return DistractorWorld(config, rng)
    if config.world == "shifting":
        return ShiftingWorld(config, rng)
    if config.world == "multiregion":
        return MultiRegionWorld(config, rng)
    return SensorimotorWorld(config, rng)
