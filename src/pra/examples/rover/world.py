"""The rover world (feature 006, ROADMAP B1) — a deterministic 2D arena
mounted through the Doc 02 anatomy layer.

A rover with pose ``(x, y, θ)`` moves in the square arena ``[-1, 1]²``
among seeded circular obstacles. Its anatomy is four named sensors — a
5-ray rangefinder, a compass, a position beacon, a bumper — and one drive
actuator (forward / reverse / turn left / turn right), composed in fixed
order into the standard :class:`~pra.anatomy.body.Body`: obs_dim 10,
n_actions 4, exactly the validated reference widths (research R1 — every
scale-rule factor is 1 there). The engine mounts the body through the
existing ``world_factory`` seam; nothing in the core changes.

**Draw discipline (research R4).** The world consumes the run's single
seeded generator in a fixed order. Construction: per obstacle — center
(one ``uniform(size=2)`` draw) then radius; then spawn poses by rejection
sampling (per attempt: position ``uniform(size=2)`` + heading draw) with a
hard attempt budget that raises a constraint-naming error. Per ``reset()``:
one spawn-index integer draw, then one emission-noise draw
(``standard_normal(10)``). Per step: physics (no RNG), then one
emission-noise draw. No other draws exist, so runs are byte-reproducible
per ``(config, seed)`` and the world is a pure function of the seed prefix,
like the reference family.

**Ground-truth hiding (FR-005).** The engine sees only the Body's
``reset``/``step``/``obs_dim``/``n_actions``. Pose, map, and layout live
behind the world's harness/viewer-only :meth:`RoverWorld.layout` accessor
and the telemetry tap's recordings — the engine never calls either.

**Pacing (research R8).** ``step_delay`` sleeps after each step's emission
— wall-clock only, no RNG, no float work on run state; byte-identity under
pacing is integration-tested. Pacing belongs to the demo run, never to the
viewer.
"""

from __future__ import annotations

import math
import time

import numpy as np

from pra.anatomy.body import AnatomyError, Body
from pra.config import Config

__all__ = ["RoverWorld", "RoverSensor", "RoverDrive", "make_rover_body"]

# --- world constants (stated dials, data-model table; research R1) -----------
ARENA_HALF = 1.0
N_OBSTACLES = 5
OBSTACLE_R_MIN = 0.12
OBSTACLE_R_MAX = 0.22
OBSTACLE_SPREAD = 0.7
ROVER_RADIUS = 0.06
MOVE_STEP = 0.08
REVERSE_FACTOR = 0.5
TURN_STEP = math.pi / 6.0
RAY_ANGLES = (-math.pi / 2.0, -math.pi / 4.0, 0.0, math.pi / 4.0, math.pi / 2.0)
RAY_MAX = 1.0
# feature 028: the +1-sensor resize hop's extra rangefinder ray (straight back).
# A clean (noiseless, RNG-free) 11th channel; appended after the 10 standard
# channels so its index is fixed. Present only when a grow flag is set.
BACK_RAY_ANGLE = math.pi
N_SPAWNS = 8
SPAWN_ATTEMPTS = 1000
SPAWN_SPREAD = 0.85

# The fixed anatomy (order is semantic, Doc 02 §3.3): 5 + 2 + 2 + 1 = 10.
SENSOR_PARTS = (("rays", 5), ("compass", 2), ("gps", 2), ("bump", 1))
ACTION_NAMES = ("forward", "reverse", "turn_left", "turn_right")
ROVER_OBS_DIM = sum(w for _, w in SENSOR_PARTS)
ROVER_N_ACTIONS = len(ACTION_NAMES)

_TWO_PI = 2.0 * math.pi
_EPS = 1e-12


# --- pure geometry (unit-tested directly) -------------------------------------


def _ray_distance(
    x: float,
    y: float,
    dx: float,
    dy: float,
    obstacles: list[tuple[float, float, float]],
    arena_half: float = ARENA_HALF,
    cap: float = RAY_MAX,
) -> float:
    """Distance from ``(x, y)`` along unit direction ``(dx, dy)`` to the
    nearest wall or obstacle circle, capped at ``cap``."""
    best = cap
    for pos, d in ((x, dx), (y, dy)):
        if d > _EPS:
            t = (arena_half - pos) / d
        elif d < -_EPS:
            t = (-arena_half - pos) / d
        else:
            continue
        if 0.0 <= t < best:
            best = t
    for cx, cy, r in obstacles:
        mx, my = cx - x, cy - y
        b = dx * mx + dy * my
        disc = b * b - (mx * mx + my * my - r * r)
        if disc >= 0.0:
            t = b - math.sqrt(disc)
            if 0.0 <= t < best:
                best = t
    return best


def _collides(
    x: float,
    y: float,
    obstacles: list[tuple[float, float, float]],
    arena_half: float = ARENA_HALF,
    rover_radius: float = ROVER_RADIUS,
) -> bool:
    """True iff a rover disc at ``(x, y)`` overlaps a wall or an obstacle."""
    if abs(x) > arena_half - rover_radius or abs(y) > arena_half - rover_radius:
        return True
    for cx, cy, r in obstacles:
        ddx, ddy = x - cx, y - cy
        reach = r + rover_radius
        if ddx * ddx + ddy * ddy < reach * reach:
            return True
    return False


def _draw_spawns(
    rng: np.random.Generator,
    obstacles: list[tuple[float, float, float]],
    n_spawns: int = N_SPAWNS,
    attempts: int = SPAWN_ATTEMPTS,
) -> list[tuple[float, float, float]]:
    """Rejection-sample ``n_spawns`` collision-free poses. Each attempt draws
    position then heading (fixed order); exceeding the budget raises a
    constraint-naming error instead of hanging (FR-011)."""
    spawns: list[tuple[float, float, float]] = []
    tried = 0
    while len(spawns) < n_spawns:
        if tried >= attempts:
            raise ValueError(
                f"RoverWorld: could not place {n_spawns} collision-free spawn poses "
                f"within {attempts} attempts — the obstacle layout leaves too little "
                "free space"
            )
        tried += 1
        pos = rng.uniform(-SPAWN_SPREAD, SPAWN_SPREAD, size=2)
        theta = float(rng.uniform(0.0, _TWO_PI))
        px, py = float(pos[0]), float(pos[1])
        if not _collides(px, py, obstacles):
            spawns.append((px, py, theta))
    return spawns


def _wrap_angle(theta: float) -> float:
    return (theta + math.pi) % _TWO_PI - math.pi


# --- the environment -----------------------------------------------------------


class RoverWorld:
    """Physics + senses. Not an ``EventSource`` itself: the Doc 02 ``Body``
    composes it from named parts (research R2). The engine never holds a
    reference to this object — only to the body around it."""

    def __init__(
        self,
        config: Config,
        rng: np.random.Generator,
        *,
        telemetry=None,
        step_delay: float = 0.0,
        layout_seed: int | None = None,
        permute: bool = False,
        permute_seed: int | None = None,
        emit_back: bool = False,
    ):
        self._noise_std = float(config.sensor_noise_std)
        self._rng = rng
        self._telemetry = telemetry
        self._step_delay = float(step_delay)
        # feature 028 resize hop: when set, _emit also computes the clean back-ray
        # into a "ray_back" sense so the grown body (native or resized) can read it.
        self._emit_back = bool(emit_back)

        # Brain-seeding seam (feature 028): the *map* (obstacles + spawns) may be
        # drawn from a harness-owned ``layout_seed`` separate from the run/brain
        # generator, so the seeding experiment can face all three arms at one
        # seed with the identical new map while each brain keeps its own
        # exploration stream. ``layout_seed=None`` draws from ``rng`` in exactly
        # the recorded order — byte-identical to feature 006.
        layout_rng = rng if layout_seed is None else np.random.default_rng(layout_seed)

        # Construction draws: per obstacle (center, radius), then spawns (R4).
        obstacles: list[tuple[float, float, float]] = []
        for _ in range(N_OBSTACLES):
            center = layout_rng.uniform(-OBSTACLE_SPREAD, OBSTACLE_SPREAD, size=2)
            radius = float(layout_rng.uniform(OBSTACLE_R_MIN, OBSTACLE_R_MAX))
            obstacles.append((float(center[0]), float(center[1]), radius))
        self._obstacles = obstacles
        self._spawns = _draw_spawns(layout_rng, obstacles)

        # Permuted rover (feature 028): a fixed construction-time permutation of
        # action semantics and sensor channels — fully learnable, structurally
        # unrelated to an un-permuted map, so a brain that masters it transfers
        # nothing useful. Drawn from an independent ``permute_seed`` generator
        # (never the run/brain rng), so a permuted world consumes no run-stream
        # draws; ``permute=False`` is byte-identical to the plain rover.
        if permute:
            perm_rng = np.random.default_rng(permute_seed)
            self._action_perm: np.ndarray | None = perm_rng.permutation(ROVER_N_ACTIONS)
            self._sensor_perm: np.ndarray | None = perm_rng.permutation(ROVER_OBS_DIM)
        else:
            self._action_perm = None
            self._sensor_perm = None

        self._x = 0.0
        self._y = 0.0
        self._theta = 0.0
        self._bump = 0
        self._senses: dict[str, np.ndarray] | None = None

    # ---- episode lifecycle (per-episode reset semantics, FR-004) --------------
    def reset(self) -> None:
        idx = int(self._rng.integers(len(self._spawns)))
        self._x, self._y, self._theta = self._spawns[idx]
        self._bump = 0
        self._emit()
        if self._telemetry is not None:
            self._telemetry.record_reset(self._x, self._y, self._theta)

    def apply(self, action: int) -> None:
        """One drive action. Physics is a pure function of (pose, action) —
        no RNG; blocked moves hold the pose and set the bumper."""
        if self._senses is None:
            raise RuntimeError("apply() called before reset()")
        if action < 0 or action >= ROVER_N_ACTIONS:
            raise ValueError(f"rover action {action} outside [0, {ROVER_N_ACTIONS})")
        # Permuted rover (feature 028): the brain's action index is relabelled to
        # a scrambled physical action — learnable, but the learned action→outcome
        # map is wrong for an un-permuted world. Identity (None) is a no-op.
        if self._action_perm is not None:
            action = int(self._action_perm[action])
        if action == 0 or action == 1:
            step = MOVE_STEP if action == 0 else -MOVE_STEP * REVERSE_FACTOR
            nx = self._x + step * math.cos(self._theta)
            ny = self._y + step * math.sin(self._theta)
            if _collides(nx, ny, self._obstacles):
                self._bump = 1
            else:
                self._x, self._y, self._bump = nx, ny, 0
        elif action == 2:
            self._theta = _wrap_angle(self._theta + TURN_STEP)
            self._bump = 0
        elif action == 3:
            self._theta = _wrap_angle(self._theta - TURN_STEP)
            self._bump = 0
        else:
            raise ValueError(f"rover action {action} outside [0, {ROVER_N_ACTIONS})")
        self._emit()
        if self._telemetry is not None:
            # observation only: plain value copies, no RNG, no float work (FR-007)
            self._telemetry.record_step(self._x, self._y, self._theta, self._bump)
        if self._step_delay > 0.0:
            time.sleep(self._step_delay)  # pacing: wall-clock only (R8)

    # ---- senses ----------------------------------------------------------------
    def _emit(self) -> None:
        clean = np.empty(ROVER_OBS_DIM, dtype=np.float64)
        for i, angle in enumerate(RAY_ANGLES):
            ang = self._theta + angle
            clean[i] = (
                _ray_distance(self._x, self._y, math.cos(ang), math.sin(ang), self._obstacles)
                / RAY_MAX
            )
        clean[5] = math.cos(self._theta)
        clean[6] = math.sin(self._theta)
        clean[7] = self._x / ARENA_HALF
        clean[8] = self._y / ARENA_HALF
        clean[9] = float(self._bump)
        obs = clean + self._rng.standard_normal(ROVER_OBS_DIM) * self._noise_std
        # Permuted rover (feature 028): scramble which physical channel feeds
        # which named sensor window. A reindex only — no new draw — so the run
        # stream is untouched; identity (None) is a no-op.
        if self._sensor_perm is not None:
            obs = obs[self._sensor_perm]
        self._senses = {
            "rays": obs[0:5],
            "compass": obs[5:7],
            "gps": obs[7:9],
            "bump": obs[9:10],
        }
        if self._emit_back:
            ang = self._theta + BACK_RAY_ANGLE
            back = (
                _ray_distance(self._x, self._y, math.cos(ang), math.sin(ang), self._obstacles)
                / RAY_MAX
            )
            self._senses["ray_back"] = np.array([back], dtype=np.float64)

    def sense(self, part_id: str) -> np.ndarray | None:
        """The cached part vector from the last emission (None before it)."""
        if self._senses is None:
            return None
        return self._senses[part_id]

    # ---- harness/viewer-only ground truth (never called by the engine) --------
    def layout(self) -> dict:
        return {
            "arena_half": ARENA_HALF,
            "rover_radius": ROVER_RADIUS,
            "obstacles": [list(o) for o in self._obstacles],
            "spawns": [list(s) for s in self._spawns],
            "ray_angles": list(RAY_ANGLES),
            "ray_max": RAY_MAX,
            "actions": list(ACTION_NAMES),
            "sensors": [part for part, _ in SENSOR_PARTS],
        }


# --- anatomy (research R2) ------------------------------------------------------


class RoverSensor:
    """One named window onto the rover's cached emission (RNG-free,
    idempotent; raises before the first emission — the WorldSensor rule)."""

    def __init__(self, world: RoverWorld, sensor_id: str, width: int):
        self._world = world
        self._id = sensor_id
        self._width = int(width)

    def id(self) -> str:
        return self._id

    def width(self) -> int:
        return self._width

    def read(self) -> np.ndarray:
        values = self._world.sense(self._id)
        if values is None:
            raise AnatomyError(f"sensor '{self._id}' read before the first emission")
        return values


class RoverDrive:
    """The drive actuator: forward, reverse, turn left, turn right. Returns
    nothing — feedback arrives only via observations (Doc 02 §4.2)."""

    def __init__(self, world: RoverWorld, actuator_id: str = "drive"):
        self._world = world
        self._id = actuator_id

    def id(self) -> str:
        return self._id

    def action_count(self) -> int:
        return ROVER_N_ACTIONS

    def action_labels(self) -> list[str]:
        """Human names for telemetry (feature 029): the standard mapping —
        the permuted arm (feature 028) relabels physics, not the brain-facing
        indices these describe."""
        return list(ACTION_NAMES)

    def apply(self, local_action_index: int) -> None:
        self._world.apply(local_action_index)


def make_rover_body(
    config: Config,
    rng: np.random.Generator,
    *,
    telemetry=None,
    step_delay: float = 0.0,
    layout_seed: int | None = None,
    permute: bool = False,
    permute_seed: int | None = None,
    extra_ray: bool = False,
    extra_ray_pending: bool = False,
) -> Body:
    """Build the rover body — the Engine's ``world_factory`` for feature 006.

    The anatomy is fixed at the validated reference widths (research R1);
    a config with different widths is rejected here, at mount time, with a
    message naming the mismatch (FR-011). When a telemetry tap is attached
    the world records pose/step events into it and the tap receives the
    static layout — the engine remains ignorant of both.

    Brain-seeding seam (feature 028): ``layout_seed`` draws the map from a
    harness-owned generator separate from the run/brain stream (maps A/B/C at
    one seed), and ``permute`` builds the permuted rover (the maturity
    control's learnable-but-unrelated world). Both default to the feature-006
    behavior, byte-identical.

    Resize hop (feature 028 US2): ``extra_ray`` builds the grown 11-dim rover
    (a 6th clean back-ray sensor active from boot — the native body the fresh-C
    arm mounts); ``extra_ray_pending`` boots the 10-dim body but *queues* the
    6th sensor as a Doc 02 tool, so the seeded chain grows 10→11 at the first
    slow loop (``apply_pending_tools`` → ``FrameStore.resize``). The back-ray is
    RNG-free, so the un-grown path stays byte-identical.
    """
    expected_obs = ROVER_OBS_DIM + (1 if extra_ray else 0)
    if config.obs_dim != expected_obs or config.n_actions != ROVER_N_ACTIONS:
        raise AnatomyError(
            f"the rover anatomy is fixed at obs_dim={expected_obs} / "
            f"n_actions={ROVER_N_ACTIONS} (the validated reference widths"
            f"{' + the resize hop back-ray' if extra_ray else ''}); "
            f"got obs_dim={config.obs_dim} / n_actions={config.n_actions}"
        )
    world = RoverWorld(
        config,
        rng,
        telemetry=telemetry,
        step_delay=step_delay,
        layout_seed=layout_seed,
        permute=permute,
        permute_seed=permute_seed,
        emit_back=extra_ray or extra_ray_pending,
    )
    sensors = [RoverSensor(world, part, width) for part, width in SENSOR_PARTS]
    if extra_ray:  # active from boot: the native grown 11-dim body
        sensors.append(RoverSensor(world, "ray_back", 1))
    body = Body(world, sensors=sensors, actuators=[RoverDrive(world)])
    if extra_ray_pending:  # queued: grows 10→11 at the first slow loop
        body.register_sensor(RoverSensor(world, "ray_back", 1))
    if telemetry is not None:
        telemetry.attach_layout(world.layout())
    return body
