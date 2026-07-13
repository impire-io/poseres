"""T004/T007 — GymnasiumWorld mechanics on scripted envs: the seed scheme is the
documented closed form, the engine generator is never drawn from, flattening and
action mapping are exact, and the respawn boundary behaves as research R2 states."""

from __future__ import annotations

import gymnasium
import numpy as np

from pra.anatomy.gymnasium_body import GymnasiumWorld


class ScriptedEnv:
    """A minimal Gymnasium-shaped env that records seeds/actions and can
    terminate (or truncate) after a fixed number of live steps per life.

    Observations encode ``(life, step-within-life)`` as ``life * 100 + step``,
    so a test can tell a terminal observation from a fresh reset observation.
    """

    def __init__(self, *, live_steps=None, truncate=False, shape=(3,), n=2, start=0):
        self.action_space = gymnasium.spaces.Discrete(n, start=start)
        self.observation_space = gymnasium.spaces.Box(
            -np.inf, np.inf, shape=shape, dtype=np.float32
        )
        self._live_steps = live_steps
        self._truncate = truncate
        self.seeds: list[int | None] = []
        self.actions: list[int] = []
        self._life = 0
        self._step = 0
        self.closed = False

    def _obs(self):
        value = float(self._life * 100 + self._step)
        return np.full(self.observation_space.shape, value, dtype=np.float32)

    def reset(self, *, seed=None, options=None):
        self.seeds.append(seed)
        self._life += 1
        self._step = 0
        return self._obs(), {}

    def step(self, action):
        self.actions.append(action)
        self._step += 1
        done = self._live_steps is not None and self._step >= self._live_steps
        return self._obs(), 0.0, done and not self._truncate, done and self._truncate, {}

    def close(self):
        self.closed = True


def expected_seed(entropy: int, k: int) -> int:
    """The documented closed form (research R3, data-model seed scheme)."""
    child = np.random.SeedSequence(entropy, spawn_key=(k,))
    return int(child.generate_state(1, dtype=np.uint32)[0])


# ---- the seed scheme (T004) ---------------------------------------------------


def test_reset_seeds_follow_the_documented_closed_form():
    env = ScriptedEnv()
    world = GymnasiumWorld(env, seed=42)
    world.reset()
    world.reset()
    world.reset()
    assert env.seeds == [expected_seed(42, 0), expected_seed(42, 1), expected_seed(42, 2)]


def test_same_seed_same_sequence_across_instances():
    env_a, env_b = ScriptedEnv(), ScriptedEnv()
    for env in (env_a, env_b):
        world = GymnasiumWorld(env, seed=7)
        world.reset()
        world.step(0)
        world.reset()
    assert env_a.seeds == env_b.seeds


def test_rng_derived_entropy_is_a_pure_function_of_the_run_seed():
    env_a, env_b = ScriptedEnv(), ScriptedEnv()
    GymnasiumWorld(env_a, rng=np.random.default_rng(11)).reset()
    GymnasiumWorld(env_b, rng=np.random.default_rng(11)).reset()
    assert env_a.seeds == env_b.seeds
    env_c = ScriptedEnv()
    GymnasiumWorld(env_c, rng=np.random.default_rng(12)).reset()
    assert env_c.seeds != env_a.seeds


def test_engine_generator_is_never_drawn_from():
    rng = np.random.default_rng(5)
    before = rng.bit_generator.state
    world = GymnasiumWorld(ScriptedEnv(live_steps=1), rng=rng)
    world.reset()
    world.step(0)  # includes a respawn — still no draws from the engine stream
    world.reset()
    assert rng.bit_generator.state == before


# ---- conversion (T004) ----------------------------------------------------------


def test_multidim_box_flattens_c_order_to_float64():
    class ImageEnv(ScriptedEnv):
        def _obs(self):
            return np.arange(6, dtype=np.float32).reshape(2, 3)

    world = GymnasiumWorld(ImageEnv(shape=(2, 3)), seed=0)
    obs = world.reset()
    assert obs.dtype == np.float64
    assert obs.shape == (6,)
    assert world.obs_dim == 6
    assert np.array_equal(obs, np.arange(6, dtype=np.float64))  # C order


def test_action_indices_map_onto_the_space_start_offset():
    env = ScriptedEnv(n=3, start=5)
    world = GymnasiumWorld(env, seed=0)
    assert world.n_actions == 3
    world.reset()
    for local in range(3):
        world.step(local)
    assert env.actions == [5, 6, 7]


# ---- the respawn boundary (T007, research R2) -----------------------------------


def test_termination_respawns_immediately_and_discards_the_terminal_observation():
    env = ScriptedEnv(live_steps=2)
    world = GymnasiumWorld(env, seed=3)
    world.reset()  # life 1 begins (reset seed k=0)
    live = world.step(0)  # life 1, step 1 — a live transition
    assert live[0] == 100 + 1
    boundary = world.step(1)  # life 1, step 2 terminates -> immediate respawn
    assert boundary[0] == 200 + 0  # the FRESH reset observation of life 2 ...
    assert 100 + 2 not in {live[0], boundary[0]}  # ... the terminal obs never crossed
    assert world.respawns == 1
    assert world.resets == 2
    assert env.seeds == [expected_seed(3, 0), expected_seed(3, 1)]


def test_truncation_takes_the_same_respawn_path():
    world = GymnasiumWorld(ScriptedEnv(live_steps=1, truncate=True), seed=3)
    world.reset()
    obs = world.step(0)
    assert obs[0] == 200 + 0
    assert world.respawns == 1


def test_one_counter_covers_episode_starts_and_respawns():
    env = ScriptedEnv(live_steps=1)
    world = GymnasiumWorld(env, seed=9)
    world.reset()  # k=0 (PRA episode start)
    world.step(0)  # k=1 (respawn)
    world.reset()  # k=2 (next PRA episode start)
    assert env.seeds == [expected_seed(9, k) for k in range(3)]
    assert world.resets == 3
    assert world.respawns == 1


def test_close_forwards_to_the_env():
    env = ScriptedEnv()
    GymnasiumWorld(env, seed=0).close()
    assert env.closed
