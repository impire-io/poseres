"""Frontier drive through the engine — determinism, composition, resume
(PREDLP-DIAGNOSIS). Small budgets; the science lives in the trail doc."""

from __future__ import annotations

from pra.config import Config
from pra.core.engine import Engine
from pra.persistence.store import InMemorySnapshotStore
from pra.world.ladder import make_world

SMALL = dict(
    warmup_episodes=2,
    n_cycles=3,
    episodes_per_cycle=2,
    steps_per_episode=10,
    horizon_checkpoints=(1, 3),
)


def _cfg(**kw) -> Config:
    return Config(
        **SMALL,
        policy_mode="curiosity",
        drive_weights=(("frontier", 0.5), ("competence", 0.5)),
        frontier_neighbors=3,
        **kw,
    )


def test_frontier_runs_are_deterministic_on_ladder_worlds():
    cfg = _cfg(world="nonuniform", region_noise_std=0.5)
    a = Engine(cfg, world_factory=make_world).run(1).serialize()
    b = Engine(cfg, world_factory=make_world).run(1).serialize()
    assert a == b


def test_frontier_snapshot_resume_is_byte_identical():
    store = InMemorySnapshotStore()
    cfg = _cfg(snapshot_every_n_cycles=2)
    uninterrupted = Engine(cfg, snapshot_store=store).run(1).serialize()
    blob = store.read(store.list()[-1][0])
    resumed = Engine(cfg).run(1, resume_from=blob).serialize()
    assert resumed == uninterrupted


def test_random_baseline_is_untouched_by_the_new_bookkeeping():
    # the pinned random baseline never builds agency state; summaries with and
    # without the frontier config surface present are byte-identical
    a = Engine(Config(**SMALL)).run(1).serialize()
    b = Engine(Config(**SMALL, frontier_neighbors=7)).run(1).serialize()
    assert a == b
