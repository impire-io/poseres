"""T006/T008/T010 — real CartPole through the adapter: byte-identical re-runs,
seed sensitivity, respawns exercised under the pinned random policy, and the
body ≡ direct-world equivalence (feature 004 R1, replayed on the adapter)."""

from __future__ import annotations

import gymnasium

from pra.anatomy.gymnasium_body import GymnasiumBody, GymnasiumWorld
from pra.config import Config
from pra.core.engine import Engine


def _small_config() -> Config:
    return Config(
        obs_dim=4,
        n_actions=2,
        warmup_episodes=3,
        n_cycles=2,
        episodes_per_cycle=1,
        steps_per_episode=40,
        horizon_checkpoints=(1, 2),
    )


def test_same_config_and_seed_is_byte_identical():
    cfg = _small_config()
    factory = GymnasiumBody.factory("CartPole-v1")
    a = Engine(cfg, world_factory=factory).run(seed=1)
    b = Engine(cfg, world_factory=factory).run(seed=1)
    assert a.serialize() == b.serialize()


def test_different_seeds_differ():
    cfg = _small_config()
    factory = GymnasiumBody.factory("CartPole-v1")
    a = Engine(cfg, world_factory=factory).run(seed=1)
    b = Engine(cfg, world_factory=factory).run(seed=2)
    assert a.serialize() != b.serialize()


def test_respawns_happen_under_the_random_policy():
    # CartPole under random actions falls well within a 40-step PRA episode:
    # the termination semantics (immediate seeded respawn, research R2) is
    # exercised by the run itself, not just implemented (FR-010, US2/AS2).
    cfg = _small_config()
    factory = GymnasiumBody.factory("CartPole-v1")
    mounted: list[GymnasiumBody] = []

    def capturing_factory(config, rng):
        body = factory(config, rng)
        mounted.append(body)
        return body

    summary = Engine(cfg, world_factory=capturing_factory).run(seed=1)
    assert summary.observation_steps > 0
    assert len(mounted) == 1
    assert mounted[0].respawns > 0
    # every reset was either a PRA episode start or a counted respawn
    episodes = cfg.warmup_episodes + cfg.n_cycles * cfg.episodes_per_cycle
    assert mounted[0].resets == episodes + mounted[0].respawns


def test_body_run_is_byte_identical_to_direct_world_run():
    cfg = _small_config()

    def world_factory(config, rng) -> GymnasiumWorld:
        return GymnasiumWorld(gymnasium.make("CartPole-v1"), rng=rng)

    via_body = Engine(cfg, world_factory=GymnasiumBody.factory("CartPole-v1")).run(seed=3)
    direct = Engine(cfg, world_factory=world_factory).run(seed=3)
    assert via_body.serialize() == direct.serialize()
