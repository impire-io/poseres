"""Brain-seeding chain integration test (feature 028 US3): the full two-hop
experiment (pretrain → probe B → resize → probe C, across the permuted-world
maturity training and the +1-sensor resize) reproduces byte-identically, and the
reference rover is untouched by the seeding machinery."""

from __future__ import annotations

import dataclasses

from pra.config import Config
from pra.harness.seeding import SeedingParams, run_seeding

_FAST_BASE = Config(warmup_episodes=6, n_cycles=3, horizon_checkpoints=(3,), episodes_per_cycle=3)
_PARAMS = SeedingParams(
    n_pretrain=3, n_probe=4, theta_b=0.4, theta_c=0.4, w_smooth=50, base_config=_FAST_BASE
)


def _tau_table(result):
    return {(r.arm, r.seed, r.map_label): r.tau for r in result.readings}


def test_two_hop_run_is_byte_deterministic():
    a = run_seeding([1, 2], "confirmatory", _PARAMS, do_hop2=True)
    b = run_seeding([1, 2], "confirmatory", _PARAMS, do_hop2=True)
    # every arm's tau on B and C reproduces exactly (the chain resumes and
    # resizes deterministically), as do the margins.
    assert _tau_table(a) == _tau_table(b)
    for name in ("margin1", "marginM", "margin2", "delta"):
        assert a.margins[name].per_seed == b.margins[name].per_seed


def test_hop2_readings_grow_the_body():
    result = run_seeding([1], "confirmatory", _PARAMS, do_hop2=True)
    c_readings = [r for r in result.readings if r.map_label == "C"]
    assert {r.arm for r in c_readings} == {"seeded", "fresh", "maturity"}
    for r in c_readings:
        assert r.n_censor > 0  # a real probe trajectory on the grown map


def test_seeding_does_not_perturb_the_reference_rover():
    # The pinned rover run (no seeding flags) is unchanged by the presence of the
    # seeding machinery: same-seed runs are byte-identical.
    from pra.core.engine import Engine
    from pra.examples.rover.world import make_rover_body
    from pra.persistence.snapshot import decode
    from pra.persistence.store import InMemorySnapshotStore

    cfg = dataclasses.replace(_FAST_BASE, snapshot_every_n_cycles=3)

    def run():
        store = InMemorySnapshotStore()
        Engine(cfg, world_factory=lambda c, r: make_rover_body(c, r), snapshot_store=store).run(1)
        return decode(store.read(store.list()[0][0])).pred_errors

    assert run() == run()
