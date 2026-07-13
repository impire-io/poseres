"""T005 — the adapter's binding contract (contracts/gymnasium-adapter.md):
EventSource/Body conformance, surface hiding, and every rejection path from the
data-model validation table — the missing-dependency path via monkeypatching,
never a skip."""

from __future__ import annotations

import gymnasium
import numpy as np
import pytest

import pra.anatomy.gymnasium_body as adapter_mod
from pra.anatomy.body import AnatomyError, Body
from pra.anatomy.gymnasium_body import GymnasiumBody, GymnasiumWorld
from pra.config import Config
from pra.world.event_source import EventSource
from tests.unit.test_gymnasium_world import ScriptedEnv

# ---- conformance ---------------------------------------------------------------


def test_world_satisfies_the_event_source_protocol():
    world = GymnasiumWorld(ScriptedEnv(), seed=0)
    assert isinstance(world, EventSource)


def test_body_is_a_doc02_body_with_the_composed_surface():
    body = GymnasiumBody(ScriptedEnv(shape=(3,), n=2), seed=0)
    assert isinstance(body, Body)
    assert (body.obs_dim, body.n_actions) == (3, 2)
    obs = body.reset()
    assert obs.dtype == np.float64 and obs.shape == (3,)
    nxt = body.step(1)
    # nothing but the observation vector crosses the seam (FR-002): no reward,
    # no flags, no info — the step result IS the observation.
    assert isinstance(nxt, np.ndarray) and nxt.shape == (3,)
    assert (body.resets, body.respawns) == (1, 0)


def test_counters_live_outside_the_learning_surface():
    # The EventSource seam is reset/step/obs_dim/n_actions; the counters are
    # adapter-object extras the engine never reads (spec key entities).
    for name in ("resets", "respawns"):
        assert not hasattr(EventSource, name)


# ---- rejection paths (data-model validation table) -------------------------------


def test_rejects_box_action_space_naming_the_space():
    env = ScriptedEnv()
    env.action_space = gymnasium.spaces.Box(-1.0, 1.0, shape=(2,), dtype=np.float32)
    with pytest.raises(AnatomyError, match="action space Box.*Discrete"):
        GymnasiumWorld(env, seed=0)


def test_rejects_discrete_observation_space_naming_the_space():
    env = ScriptedEnv()
    env.observation_space = gymnasium.spaces.Discrete(5)
    with pytest.raises(AnatomyError, match="observation space Discrete.*Box"):
        GymnasiumWorld(env, seed=0)


def test_rejects_zero_or_two_determinism_sources():
    with pytest.raises(AnatomyError, match="exactly one of rng/seed"):
        GymnasiumWorld(ScriptedEnv())
    with pytest.raises(AnatomyError, match="exactly one of rng/seed"):
        GymnasiumWorld(ScriptedEnv(), rng=np.random.default_rng(0), seed=1)


def test_rejects_generator_without_a_pure_state_read():
    mt = np.random.Generator(np.random.MT19937(0))
    with pytest.raises(AnatomyError, match="pass seed= explicitly"):
        GymnasiumWorld(ScriptedEnv(), rng=mt)


def test_step_before_reset_is_a_contract_error():
    world = GymnasiumWorld(ScriptedEnv(), seed=0)
    with pytest.raises(AnatomyError, match="before reset"):
        world.step(0)
    body = GymnasiumBody(ScriptedEnv(), seed=0)
    with pytest.raises(AnatomyError, match="before reset"):
        body.step(0)


def test_factory_size_mismatch_names_both_numbers():
    cfg = Config(obs_dim=10, n_actions=4)
    factory = GymnasiumBody.factory(lambda: ScriptedEnv(shape=(3,), n=2))
    with pytest.raises(AnatomyError) as err:
        factory(cfg, np.random.default_rng(1))
    message = str(err.value)
    assert "obs_dim=10" in message and "n_actions=4" in message  # the config side
    assert "obs_dim=3" in message and "n_actions=2" in message  # the environment side


def test_missing_gymnasium_names_the_install_command(monkeypatch):
    monkeypatch.setattr(adapter_mod, "_gymnasium", None)
    with pytest.raises(ImportError, match=r"poseres\[gym\]"):
        GymnasiumWorld(ScriptedEnv(), seed=0)


# ---- factory mechanics ------------------------------------------------------------


def test_factory_builds_a_fresh_env_per_call():
    built: list[ScriptedEnv] = []

    def make() -> ScriptedEnv:
        env = ScriptedEnv(shape=(3,), n=2)
        built.append(env)
        return env

    cfg = Config(obs_dim=3, n_actions=2)
    factory = GymnasiumBody.factory(make)
    body_a = factory(cfg, np.random.default_rng(1))
    body_b = factory(cfg, np.random.default_rng(2))
    assert len(built) == 2
    assert body_a.world is not body_b.world


def test_body_close_forwards_to_the_env():
    env = ScriptedEnv()
    GymnasiumBody(env, seed=0).close()
    assert env.closed
