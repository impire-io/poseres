"""The Gymnasium adapter: mount any Gymnasium environment as a PRA body (feature 007).

One adapter, hundreds of ready-made worlds. :class:`GymnasiumWorld` wraps a
``gymnasium.Env`` behind the existing ``EventSource`` seam; :class:`GymnasiumBody`
composes it through the proven Doc 02 body path (``WorldSensor``/``WorldActuator``
— world-through-body is byte-identical to the direct connection, feature 004 R1).
The engine, drives, and harness run on it unchanged; the feature is purely
additive (nothing imports this module unless the user does).

Scope (v1, spec Assumptions): ``Discrete`` action spaces and ``Box`` observation
spaces only. Observations are flattened C-order to float64; PRA's local action
index ``i`` maps to the environment action ``space.start + i``. Reward, the
``terminated``/``truncated`` flags, and the info dict never cross the seam — PRA's
motivation is intrinsic (Doc 05), so the reward is discarded, openly.

Termination semantics (the named B2 design question, research R2): PRA episodes
are fixed-length; when the environment ends its own episode (``terminated`` or
``truncated``), the adapter immediately resets it with the next seed in its
deterministic sequence and returns the fresh observation as that step's outcome —
the world "respawns" and the PRA episode continues. The terminal observation is
discarded. The boundary transition is therefore irreducibly unpredictable (the
same property as the ladder's unlearnable region, localized at boundaries);
``respawns`` counts how often it happened, outside the learning surface.

Determinism (research R3): at mount time the adapter derives entropy ``E`` from
the engine's run generator by a **pure state read** (no draws — the engine's
stream is bit-identical to a run without the adapter), or from an explicit
``seed=``. Env reset ``k`` (episode starts and respawns share one counter) is
seeded with ``SeedSequence(E, spawn_key=(k,))``. Same (config, seed) → byte-
identical run summaries, for any environment that follows Gymnasium's seeding
convention.

Not supported in v1 (documented deferrals, research R7): Box action spaces,
non-Box observation spaces, reward-as-sensor, and snapshot/resume of
Gymnasium-mounted runs — external env state cannot be re-derived from the seed
stream, so a resumed run would silently diverge (ROADMAP B5 owns that story).
"""

from __future__ import annotations

import numpy as np

from pra.anatomy.body import AnatomyError, Body, WorldActuator, WorldSensor

__all__ = ["GymnasiumWorld", "GymnasiumBody"]

try:  # the optional dependency (pyproject extra "gym"); see _require_gymnasium
    import gymnasium as _gymnasium
except ImportError:  # pragma: no cover - dev environments always carry gymnasium
    _gymnasium = None


def _require_gymnasium():
    """Return the gymnasium module or fail with the install command (FR-006)."""
    if _gymnasium is None:
        raise ImportError(
            "the Gymnasium adapter needs the optional 'gymnasium' package — "
            'install it with: pip install "poseres[gym]"'
        )
    return _gymnasium


def _entropy_from_generator(rng: np.random.Generator) -> int:
    """A pure read of the generator's state — never a draw (research R3)."""
    state = rng.bit_generator.state
    try:
        return int(state["state"]["state"])
    except (TypeError, KeyError, IndexError):
        raise AnatomyError(
            "cannot derive a deterministic seed from this generator "
            f"({type(rng.bit_generator).__name__}); pass seed= explicitly"
        ) from None


class GymnasiumWorld:
    """EventSource over a ``gymnasium.Env``: flattening, seeding, respawn.

    Exactly one of ``rng``/``seed`` supplies the determinism source: the Engine's
    ``world_factory(cfg, rng)`` path derives entropy from ``rng`` without drawing;
    standalone use passes ``seed=`` directly.
    """

    def __init__(
        self,
        env,
        *,
        rng: np.random.Generator | None = None,
        seed: int | None = None,
    ):
        gym = _require_gymnasium()
        if not isinstance(env.action_space, gym.spaces.Discrete):
            raise AnatomyError(
                f"unsupported action space {env.action_space!r}: the adapter supports "
                "Discrete action spaces only in v1 (Box-action support is out of scope)"
            )
        if not isinstance(env.observation_space, gym.spaces.Box):
            raise AnatomyError(
                f"unsupported observation space {env.observation_space!r}: the adapter "
                "supports continuous (Box) observation spaces only in v1"
            )
        if (rng is None) == (seed is None):
            raise AnatomyError("exactly one of rng/seed must be given (the determinism source)")
        self._env = env
        self._entropy = int(seed) if seed is not None else _entropy_from_generator(rng)
        self._action_start = int(env.action_space.start)
        self._n_actions = int(env.action_space.n)
        self._obs_dim = int(np.prod(env.observation_space.shape, dtype=np.int64))
        self._reset_index = 0
        self._respawns = 0
        self._started = False

    # ---- EventSource surface (nothing else crosses it, FR-002) ----------------
    @property
    def n_actions(self) -> int:
        return self._n_actions

    @property
    def obs_dim(self) -> int:
        return self._obs_dim

    def reset(self) -> np.ndarray:
        obs, _info = self._env.reset(seed=self._next_seed())
        self._started = True
        return self._flatten(obs)

    def step(self, action: int) -> np.ndarray:
        if not self._started:
            raise AnatomyError("step() called before reset()")
        obs, _reward, terminated, truncated, _info = self._env.step(
            self._action_start + int(action)
        )
        if terminated or truncated:
            # Immediate respawn (research R2): the terminal observation is
            # discarded; the fresh, seeded reset observation is this step's
            # outcome, and the fixed-length PRA episode continues.
            self._respawns += 1
            obs, _info = self._env.reset(seed=self._next_seed())
        return self._flatten(obs)

    # ---- outside the learning surface ------------------------------------------
    @property
    def resets(self) -> int:
        """Total env resets so far — PRA episode starts and respawns alike."""
        return self._reset_index

    @property
    def respawns(self) -> int:
        """Mid-episode resets caused by terminated/truncated (FR-004)."""
        return self._respawns

    def close(self) -> None:
        self._env.close()

    # ---- internals ---------------------------------------------------------------
    def _next_seed(self) -> int:
        """Reset ``k`` is seeded from ``SeedSequence(E, spawn_key=(k,))`` (R3)."""
        child = np.random.SeedSequence(self._entropy, spawn_key=(self._reset_index,))
        self._reset_index += 1
        return int(child.generate_state(1, dtype=np.uint32)[0])

    def _flatten(self, obs) -> np.ndarray:
        """C-order float64 flattening; width == prod(space.shape) (FR-002)."""
        return np.asarray(obs, dtype=np.float64).ravel()


class GymnasiumBody(Body):
    """A Doc 02 body around a Gymnasium environment — the 004 composition path.

    ``WorldSensor``/``WorldActuator`` already implement caching, width
    enforcement, and routing over any EventSource; this subclass only wires them
    around a :class:`GymnasiumWorld` and forwards its counters.
    """

    def __init__(
        self,
        env,
        *,
        rng: np.random.Generator | None = None,
        seed: int | None = None,
        sensor_id: str = "gym",
        actuator_id: str = "gym",
    ):
        world = GymnasiumWorld(env, rng=rng, seed=seed)
        sensor = WorldSensor(world, sensor_id)
        super().__init__(
            world,
            sensors=[sensor],
            actuators=[WorldActuator(world, sensor, actuator_id)],
        )
        self._world = world

    @property
    def world(self) -> GymnasiumWorld:
        return self._world

    @property
    def resets(self) -> int:
        return self._world.resets

    @property
    def respawns(self) -> int:
        return self._world.respawns

    def close(self) -> None:
        self._world.close()

    @classmethod
    def factory(cls, env_or_id, *, sensor_id: str = "gym", actuator_id: str = "gym", **make_kwargs):
        """An Engine-ready ``world_factory(cfg, rng)`` (FR-007).

        ``env_or_id`` is an environment id string (a fresh
        ``gymnasium.make(id, **make_kwargs)`` per call, so every run and seed
        gets its own environment) or a zero-argument callable returning an env.
        Mounting validates the config's sizes against the environment and names
        both numbers on mismatch — never a shape error deep inside a run.
        """

        def world_factory(cfg, rng: np.random.Generator) -> GymnasiumBody:
            if isinstance(env_or_id, str):
                env = _require_gymnasium().make(env_or_id, **make_kwargs)
            else:
                env = env_or_id(**make_kwargs)
            body = cls(env, rng=rng, sensor_id=sensor_id, actuator_id=actuator_id)
            if (cfg.obs_dim, cfg.n_actions) != (body.obs_dim, body.n_actions):
                raise AnatomyError(
                    f"config/environment mismatch: config declares obs_dim={cfg.obs_dim}, "
                    f"n_actions={cfg.n_actions} but the environment provides "
                    f"obs_dim={body.obs_dim}, n_actions={body.n_actions} — "
                    "set Config(obs_dim=..., n_actions=...) to match"
                )
            return body

        return world_factory
