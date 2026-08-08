"""``pra-flush`` — the observatory flusher's entry point (feature 032).

Connects to NATS, ensures the ``PRA_V1`` JetStream ring buffer exists
(file store, bounded age — the 1-hour buffer), pull-consumes it durably,
and drains :class:`~pra.flush.Flusher` batches into the sink with the
ack-after-write discipline. Optionally mirrors snapshot blobs to the
sink as their notices arrive and prunes the local store to newest-N
(delete only what is mirrored — FR-004).
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

from pra.flush import DirSink, Flusher, S3Sink, prune_plan

__all__ = ["main"]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="pra-flush", description=__doc__)
    parser.add_argument("--url", default="nats://127.0.0.1:4222")
    parser.add_argument("--stream-max-age", type=float, default=3600.0, help="buffer seconds")
    parser.add_argument("--interval", type=float, default=120.0, help="batch flush seconds")
    parser.add_argument("--dir", default="", help="DirSink root (default: S3 from env)")
    parser.add_argument("--snapshot-dir", default="", help="mirror+prune this store")
    parser.add_argument("--snapshot-keep", type=int, default=5)
    args = parser.parse_args(argv)

    sink = DirSink(args.dir) if args.dir else S3Sink()
    try:
        import asyncio

        asyncio.run(_pump(args, sink))
    except KeyboardInterrupt:
        pass
    return 0


async def _pump(args, sink) -> None:
    import nats
    from nats.errors import TimeoutError as NatsTimeout
    from nats.js.api import ConsumerConfig, RetentionPolicy, StorageType, StreamConfig
    from nats.js.errors import NotFoundError

    nc = await nats.connect(args.url)
    js = nc.jetstream()
    config = StreamConfig(
        name="PRA_V1",
        subjects=["pra.v1.>"],
        max_age=float(args.stream_max_age),
        storage=StorageType.FILE,
        retention=RetentionPolicy.LIMITS,
    )
    try:
        await js.stream_info("PRA_V1")
    except NotFoundError:
        await js.add_stream(config)
    # ack_wait must comfortably outlive the flush interval: messages stay
    # unacked until their batch is durably written (the discipline), and a
    # shorter ack_wait makes JetStream redeliver them into the same batch —
    # measured live on beno4 (3.2x duplicates at the 30s default).
    sub = await js.pull_subscribe(
        "pra.v1.>",
        durable="pra-flush",
        stream="PRA_V1",
        config=ConsumerConfig(ack_wait=max(300.0, args.interval * 3.0)),
    )

    flusher = Flusher(flush_interval=args.interval)
    mirrored: set[str] = set()
    snapshot_dir = Path(args.snapshot_dir) if args.snapshot_dir else None
    print(f"pra-flush: consuming PRA_V1 (buffer {args.stream_max_age:.0f}s) -> sink", flush=True)

    while True:
        try:
            messages = await sub.fetch(500, timeout=5)
        except (NatsTimeout, TimeoutError):
            # nats-py's _fetch_n raises a bare asyncio.TimeoutError (builtin
            # TimeoutError on 3.11+) when a partial batch expires — measured
            # live on beno4 as the c1c-era crash loop (14 restarts,
            # journalctl 2026-07-21..08-06); NatsTimeout alone missed it.
            messages = []
        now = time.monotonic()
        for message in messages:
            flusher.add(message.subject, message.data, message, now)
        for flush in flusher.due(time.monotonic()):
            await _write_with_retry(sink, flush.key, flush.data)
            for message in flush.acks:
                await message.ack()  # the discipline: durably written first
        if snapshot_dir is not None:
            _mirror_and_prune(sink, snapshot_dir, args.snapshot_keep, mirrored)


async def _write_with_retry(sink, key: str, data: bytes) -> None:
    import asyncio

    delay = 1.0
    while True:
        try:
            sink.write(key, data)
            return
        except Exception as err:  # S3 down: the buffer absorbs; we retry
            print(f"pra-flush: sink write failed ({err}); retry in {delay:.0f}s", flush=True)
            await asyncio.sleep(delay)
            delay = min(delay * 2, 60.0)


def _mirror_and_prune(sink, directory: Path, keep: int, mirrored: set[str]) -> None:
    # the store directory is the truth (catches snapshots written while the
    # flusher was down); the .json commit marker gates visibility (store.py)
    committed = sorted(
        (p.stem for p in directory.glob("snap-*.json") if (directory / f"{p.stem}.npz").exists()),
        reverse=True,
    )
    for snapshot_id in committed:
        if snapshot_id in mirrored:
            continue
        try:
            sink.write(
                f"pra/v1/_snapshots/{snapshot_id}.npz",
                (directory / f"{snapshot_id}.npz").read_bytes(),
            )
            sink.write(
                f"pra/v1/_snapshots/{snapshot_id}.json",
                (directory / f"{snapshot_id}.json").read_bytes(),
            )
            mirrored.add(snapshot_id)
        except Exception as err:
            print(f"pra-flush: snapshot mirror failed ({err}); will retry", flush=True)
            return
    for snapshot_id in prune_plan(committed, keep, mirrored):
        (directory / f"{snapshot_id}.json").unlink(missing_ok=True)
        (directory / f"{snapshot_id}.npz").unlink(missing_ok=True)


if __name__ == "__main__":
    sys.exit(main())
