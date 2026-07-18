"""A rover brain on the bus (feature 015 US4): the B1 world, the B6 tap, and
the world-view channel — the run any dashboard should be able to face.

Usage: python brain_rover.py [--url nats://127.0.0.1:4222] [--run-id rover] [--seed 1]
"""

from __future__ import annotations

import argparse
import sys

from pra.config import Config
from pra.core.engine import Engine
from pra.examples.rover.world import make_rover_body
from pra.nats import NatsSnapshotStore, NatsTap, NatsTransport


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default="nats://127.0.0.1:4222")
    parser.add_argument("--run-id", default="rover")
    parser.add_argument("--seed", type=int, default=1)
    args = parser.parse_args()

    cfg = Config(
        warmup_episodes=2,
        n_cycles=10,
        episodes_per_cycle=2,
        steps_per_episode=60,
        horizon_checkpoints=(5, 10),
        snapshot_every_n_cycles=2,
    )
    transport = NatsTransport(args.url)
    tap = NatsTap(transport, run_id=args.run_id, drain_interval=0.02, census_interval=0.25)
    view = tap.world_view("rover")
    store = NatsSnapshotStore(transport)
    engine = Engine(
        cfg,
        # step_delay paces the world (wall-clock only — the rover's own dial)
        world_factory=tap.world_factory(
            inner=lambda c, r: make_rover_body(c, r, telemetry=view, step_delay=0.01)
        ),
        bus_factory=tap.bus_factory,
        snapshot_store=tap.wrap_store(store),
    )
    tap.start()
    print(f"brain_rover: run {tap.run_id!r} live on {args.url} (view channel on)", flush=True)
    summary = engine.run(args.seed)
    tap.finish(summary)
    print(f"brain_rover: complete — {summary.serialize()}", flush=True)
    transport.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
