"""Learned channel weighting (feature 016) — live-run coverage: ON smoke on
the L3 noise rung, summary-field gating (byte-identity when off), and mode
composition (multi-stream, continuous)."""

from __future__ import annotations

from pra.config import Config
from pra.core.engine import Engine
from pra.world.ladder import make_world

SMALL = dict(
    warmup_episodes=6,
    n_cycles=4,
    episodes_per_cycle=2,
    steps_per_episode=40,
    horizon_checkpoints=(1, 4),
)

L3_NOISE = dict(
    world="distractor",
    true_dim=3,
    obs_dim=20,
    distractor_dim=3,
    distractor_channels=10,
    distractor_mode="noise",
)

ON = dict(channel_weight_floor=0.2, channel_stats_decay=0.995)


def test_on_smoke_l3_noise_carries_summary_block_and_floors_static():
    cfg = Config(**SMALL, **L3_NOISE, **ON)
    s = Engine(cfg, world_factory=make_world).run(1)
    cw = s.canonical()["channel_weighting"]
    assert cw["floor"] == 0.2 and cw["decay"] == 0.995
    assert cw["ready_channels"] == 20  # 6 warmup episodes x 40 steps > 200
    weights = cw["final_weights"]
    # the ten white channels sit at the floor; the ten core channels keep
    # their voice (the P1 no-suppression reading, live)
    assert all(w == 0.2 for w in weights[10:])
    assert all(w > 0.5 for w in weights[:10])


def test_explicit_inert_config_summary_is_byte_equal_to_default():
    small = dict(SMALL, warmup_episodes=2, steps_per_episode=10)
    default = Engine(Config(**small)).run(1).serialize()
    explicit = (
        Engine(Config(**small, channel_weight_floor=0.0, channel_stats_decay=0.995))
        .run(1)
        .serialize()
    )
    assert explicit == default
    assert "channel_weighting" not in default


def test_bare_engine_refuses_ladder_world_without_factory():
    import pytest

    with pytest.raises(ValueError, match="world_factory"):
        Engine(Config(**SMALL, **L3_NOISE))


def test_on_is_deterministic_across_modes():
    """K=2 multi-stream and continuous mode compose with the feature ON:
    the runs complete and a same-seed rerun is byte-identical."""
    for extra in (dict(n_streams=2), dict(episode_mode="continuous")):
        cfg = Config(**SMALL, **ON, **extra)
        a = Engine(cfg).run(2).serialize()
        b = Engine(cfg).run(2).serialize()
        assert a == b
