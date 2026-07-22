"""The C1 launcher (feature 027): one brain, one Minecraft world, weeks.

Continuous mode, cap on, snapshots on a cadence, resume-from-latest —
the arc-026 launch posture applied. Ctrl-C any time: the work since the
last snapshot is lost, everything before it resumes exactly (the brain;
the live world resumes wherever the server is — Doc 06 §5b class 4,
stated). Optional NATS telemetry (--nats) makes the run watchable with
pra-dash (examples/nats/README.md).

    python run_c1.py                       # local snapshots, no telemetry
    python run_c1.py --nats nats://127.0.0.1:4222
"""

from __future__ import annotations

import argparse
import sys

from pra.anatomy.minecraft import C1_N_ACTIONS, C1_OBS_DIM, MinecraftTransport, c1_anatomy
from pra.anatomy.ros2 import Ros2Body
from pra.config import Config
from pra.core.engine import Engine
from pra.persistence.store import FileSnapshotStore

# Selectable drive sets for the curiosity-lookahead policy. Frontier is the
# default: competence-alone was measured to camp on stasis in Minecraft (its
# only per-candidate term is familiarity, which is maximised by "stand still");
# frontier rewards moving toward regions where prediction error is falling and
# scores both mastered and no-change outcomes at ~0, so it cannot camp on idle.
_DRIVE_SETS = {
    "frontier": (("frontier", 1.0),),
    "competence": (("competence", 1.0),),
    "curiosity": (("curiosity", 1.0),),
    "curiosity+frontier": (("curiosity", 1.0), ("frontier", 1.0)),
    "competence+frontier": (("competence", 1.0), ("frontier", 1.0)),
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bridge-port", type=int, default=25580)
    parser.add_argument("--seed", type=int, default=1, help="must stay fixed across resumes")
    parser.add_argument("--snapshot-dir", default="c1-snapshots")
    parser.add_argument("--snap-every", type=int, default=25, help="cycles between snapshots")
    parser.add_argument("--cycles", type=int, default=100_000)
    parser.add_argument("--tick-ms", type=int, default=250)
    parser.add_argument("--nats", default="", help="NATS url; empty = no telemetry")
    parser.add_argument("--run-id", default="c1")
    parser.add_argument(
        "--drive",
        choices=sorted(_DRIVE_SETS),
        default="frontier",
        help="drive set for action valuation (default: frontier)",
    )
    args = parser.parse_args()

    checkpoints = (18, 30, 50) if args.cycles >= 50 else (args.cycles,)
    cfg = Config(
        obs_dim=C1_OBS_DIM,
        n_actions=C1_N_ACTIONS,
        episode_mode="continuous",
        policy_mode="curiosity",
        drive_weights=_DRIVE_SETS[args.drive],
        weight_norm_cap=1.2,  # arc 026: measured behaviorally free, closes the tail
        n_cycles=args.cycles,
        horizon_checkpoints=checkpoints,
        snapshot_every_n_cycles=args.snap_every,
    )

    store = FileSnapshotStore(args.snapshot_dir)
    resume = None
    snapshots = store.list()
    if snapshots:
        newest_id, meta = snapshots[0]
        resume = store.read(newest_id)
        print(f"resuming from {newest_id} (cycle {meta['cycle']}, step {meta['step']})")

    sensors, actuators = c1_anatomy()

    bus_factory = None
    tap = None
    on_view = None
    if args.nats:
        from pra.nats import NatsTap, NatsTransport

        nats_transport = NatsTransport(args.nats)
        tap = NatsTap(nats_transport, run_id=args.run_id)
        on_view = tap.world_view("minecraft").record_step  # ground truth (033)

    factory = Ros2Body.factory(
        sensors,
        actuators,
        transport=lambda: MinecraftTransport(
            port=args.bridge_port, tick_ms=args.tick_ms, on_view=on_view
        ),
    )

    if tap is not None:
        factory = tap.world_factory(inner=factory)
        bus_factory = tap.bus_factory
        store = tap.wrap_store(store)
        tap.start()
        print(f"telemetry live on {args.nats} as run {tap.run_id!r} (pra-dash can attach)")

    engine_kwargs = dict(world_factory=factory, snapshot_store=store)
    if bus_factory is not None:
        engine_kwargs["bus_factory"] = bus_factory
    engine = Engine(cfg, **engine_kwargs)

    print(
        f"C1 up: obs_dim {C1_OBS_DIM}, n_actions {C1_N_ACTIONS}, drive {args.drive!r}, "
        f"tick {args.tick_ms} ms, snapshot every {args.snap_every} cycles -> {args.snapshot_dir}/"
    )
    try:
        summary = engine.run(args.seed, resume_from=resume)
    except KeyboardInterrupt:
        print("\nstopped; rerun to resume from the latest snapshot")
        return 130
    if tap is not None:
        tap.finish(summary)
    print(f"run complete: {summary.serialize()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
