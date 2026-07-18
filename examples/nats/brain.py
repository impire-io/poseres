"""The brain half of the worked example (feature 014 US4).

A seeded run with the full B6 surface attached: telemetry tap, JetStream
object-store snapshots at a short cadence, and the control plane. The run is
paced (identical draws, slower wall clock — the rover precedent) so a human
or the watcher process has time to interact with it.

Usage: python brain.py [--url nats://127.0.0.1:4222] [--run-id demo] [--seed 1]
"""

from __future__ import annotations

import argparse
import sys
import time

from pra.config import Config
from pra.core.engine import Engine
from pra.nats import NatsSnapshotStore, NatsTap, NatsTransport, subjects
from pra.world.event_source import SensorimotorWorld


class PacedWorld(SensorimotorWorld):
    """Same draws, ~5 ms per step: watchable without changing a single byte."""

    def step(self, action):
        time.sleep(0.005)
        return super().step(action)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default="nats://127.0.0.1:4222")
    parser.add_argument("--run-id", default="demo")
    parser.add_argument("--seed", type=int, default=1)
    args = parser.parse_args()

    cfg = Config(
        warmup_episodes=2,
        n_cycles=10,
        episodes_per_cycle=2,
        steps_per_episode=50,
        horizon_checkpoints=(5, 10),
        snapshot_every_n_cycles=2,
    )
    transport = NatsTransport(args.url)
    tap = NatsTap(transport, run_id=args.run_id, drain_interval=0.02, census_interval=0.25)
    store = NatsSnapshotStore(transport)
    engine = Engine(
        cfg,
        world_factory=tap.world_factory(inner=PacedWorld),
        bus_factory=tap.bus_factory,
        snapshot_store=tap.wrap_store(store),
    )
    tap.start()
    print(f"brain: run {tap.run_id!r} live on {args.url}", flush=True)
    print(f"brain: subjects {subjects.run_subjects(tap.run_id)}", flush=True)

    summary = engine.run(args.seed)
    tap.finish(summary)
    print(f"brain: run complete — summary follows\n{summary.serialize()}", flush=True)
    print(
        f"brain: telemetry mirrored={tap.events_mirrored} published={tap.events_published} "
        f"dropped={tap.events_dropped} publish_failures={transport.publish_failures} "
        f"control_requests={tap.control_requests}",
        flush=True,
    )
    transport.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
