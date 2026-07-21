"""The observatory flusher (feature 032): a JetStream ring buffer made
durable in S3.

The core is pure and fake-carried: a :class:`Flusher` groups incoming
``(subject, payload)`` pairs into per-(run, family) batches and, when a
batch is due (age or size), emits a :class:`Flush` — the object key
(seq range included, so gaps are *visible*, never repaired), the gzip
JSONL bytes, and the ack handles. The caller's contract is the ack
discipline: write the object first, ack only after — at-least-once by
construction. Sinks: :class:`DirSink` (tests and S3-less use) and
:class:`S3Sink` (boto3 behind the optional ``[s3]`` extra, endpoint
from env — MinIO or AWS alike). Wall-clock appears only in object keys
(the operational layer); payloads keep the recorder discipline.
"""

from __future__ import annotations

import gzip
import json
import os
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path

__all__ = ["DirSink", "Flush", "Flusher", "S3Sink", "batch_key", "prune_plan", "utc_stamp"]


def utc_stamp() -> str:
    return datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")


def batch_key(subject: str) -> tuple[str, str]:
    """``pra.v1.run.<id>.<family...>`` → ``(run, family)``; anything else
    (discover, control replies never land here anyway) → ``("_bus", tail)``."""
    parts = subject.split(".")
    if len(parts) >= 5 and parts[:3] == ["pra", "v1", "run"]:
        return parts[3], ".".join(parts[4:])
    return "_bus", ".".join(parts[2:]) or "misc"


@dataclass
class _Batch:
    lines: list[bytes] = field(default_factory=list)
    acks: list[object] = field(default_factory=list)
    seq_first: int | None = None
    seq_last: int | None = None
    born: float = 0.0
    size: int = 0

    def add(self, payload: bytes, ack: object) -> None:
        self.lines.append(payload)
        self.acks.append(ack)
        self.size += len(payload) + 1
        try:
            seq = json.loads(payload).get("seq")
        except (ValueError, AttributeError):
            seq = None
        if isinstance(seq, int):
            self.seq_first = seq if self.seq_first is None else min(self.seq_first, seq)
            self.seq_last = seq if self.seq_last is None else max(self.seq_last, seq)


@dataclass
class Flush:
    """One due batch: write ``data`` at ``key``, then ack every handle."""

    key: str
    data: bytes
    acks: list[object]
    count: int


class Flusher:
    """Pure batching core. ``add`` buffers; ``due``/``drain`` emit."""

    def __init__(
        self,
        *,
        flush_interval: float = 120.0,
        flush_bytes: int = 4_000_000,
        stamp: Callable[[], str] = utc_stamp,
    ):
        self._interval = float(flush_interval)
        self._bytes = int(flush_bytes)
        self._stamp = stamp
        self._batches: dict[tuple[str, str], _Batch] = {}

    def add(self, subject: str, payload: bytes, ack: object, now: float) -> None:
        key = batch_key(subject)
        batch = self._batches.get(key)
        if batch is None:
            batch = self._batches[key] = _Batch(born=now)
        batch.add(bytes(payload), ack)

    def due(self, now: float) -> list[Flush]:
        ready = [
            key
            for key, b in self._batches.items()
            if b.size >= self._bytes or now - b.born >= self._interval
        ]
        return [self._emit(key) for key in sorted(ready)]

    def drain(self) -> list[Flush]:
        return [self._emit(key) for key in sorted(self._batches)]

    def pending(self) -> int:
        return sum(len(b.lines) for b in self._batches.values())

    def _emit(self, key: tuple[str, str]) -> Flush:
        run, family = key
        batch = self._batches.pop(key)
        first = 0 if batch.seq_first is None else batch.seq_first
        last = 0 if batch.seq_last is None else batch.seq_last
        object_key = f"pra/v1/{run}/{family}/{self._stamp()}-{first:012d}-{last:012d}.jsonl.gz"
        data = gzip.compress(b"\n".join(batch.lines) + b"\n")
        return Flush(key=object_key, data=data, acks=batch.acks, count=len(batch.lines))


def prune_plan(ids_newest_first: list[str], keep: int, mirrored: set[str]) -> list[str]:
    """Local snapshots safe to delete: beyond newest-``keep`` AND mirrored."""
    return [i for i in ids_newest_first[max(keep, 0) :] if i in mirrored]


class DirSink:
    """Objects as files under a root — tests, and S3-less deployments."""

    def __init__(self, root: str | Path):
        self.root = Path(root)

    def write(self, key: str, data: bytes) -> None:
        path = self.root / key
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(path.suffix + ".tmp")
        tmp.write_bytes(data)
        tmp.replace(path)


class S3Sink:
    """boto3 put_object; endpoint/bucket from env or arguments. The import
    lives here so the gate never needs boto3 (the ``[s3]`` extra pattern)."""

    def __init__(self, bucket: str | None = None, endpoint: str | None = None):
        try:
            import boto3
        except ImportError as err:  # pragma: no cover - message contract only
            raise ImportError(
                "the S3 client library is not installed; install the optional "
                'extra: pip install "poseres[s3]" — the DirSink needs no library'
            ) from err
        self.bucket = bucket or os.environ["PRA_S3_BUCKET"]
        endpoint = endpoint or os.environ.get("PRA_S3_ENDPOINT") or None
        self._client = boto3.client("s3", endpoint_url=endpoint)

    def write(self, key: str, data: bytes) -> None:
        self._client.put_object(Bucket=self.bucket, Key=key, Body=data)
