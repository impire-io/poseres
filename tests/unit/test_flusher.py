"""Feature 032 — the flusher core: batching per (run, family), visible seq
ranges in object keys, the ack-after-write discipline's shape, size and age
triggers, gzip round-trip, and the snapshot prune plan. No broker, no S3."""

from __future__ import annotations

import gzip
import json

from pra.flush import DirSink, Flusher, batch_key, prune_plan


def _payload(seq: int, **extra) -> bytes:
    return json.dumps({"run": "c1", "seq": seq, **extra}).encode()


def test_batch_key_scopes_by_run_and_family():
    assert batch_key("pra.v1.run.c1.tele.step") == ("c1", "tele.step")
    assert batch_key("pra.v1.run.c1.brain.events") == ("c1", "brain.events")
    assert batch_key("pra.v1.run.other.status") == ("other", "status")
    assert batch_key("pra.v1.discover") == ("_bus", "discover")


def test_batches_flush_by_age_with_seq_range_in_the_key():
    flusher = Flusher(flush_interval=10.0, stamp=lambda: "T0")
    flusher.add("pra.v1.run.c1.tele.step", _payload(5), "a5", now=0.0)
    flusher.add("pra.v1.run.c1.tele.step", _payload(7), "a7", now=1.0)
    flusher.add("pra.v1.run.c1.brain.events", _payload(6), "a6", now=1.0)
    assert flusher.due(now=5.0) == []  # nothing old enough
    flushes = flusher.due(now=10.0)  # only the batch born at 0.0 is due
    assert [f.key for f in flushes] == [
        "pra/v1/c1/tele.step/T0-000000000005-000000000007.jsonl.gz",
    ]
    later = flusher.due(now=11.0)  # the events batch (born 1.0) follows
    assert [f.key for f in later] == [
        "pra/v1/c1/brain.events/T0-000000000006-000000000006.jsonl.gz",
    ]
    step_flush = flushes[0]
    assert step_flush.acks == ["a5", "a7"] and step_flush.count == 2
    lines = gzip.decompress(step_flush.data).decode().strip().split("\n")
    assert [json.loads(line)["seq"] for line in lines] == [5, 7]
    assert flusher.pending() == 0


def test_size_trigger_flushes_early():
    flusher = Flusher(flush_interval=1e9, flush_bytes=100, stamp=lambda: "T0")
    flusher.add("pra.v1.run.c1.tele.step", _payload(1, pad="x" * 200), "a", now=0.0)
    assert len(flusher.due(now=0.0)) == 1  # size, not age


def test_drain_empties_everything():
    flusher = Flusher(stamp=lambda: "T0")
    flusher.add("pra.v1.run.a.status", _payload(1), "x", now=0.0)
    flusher.add("pra.v1.run.b.status", _payload(2), "y", now=0.0)
    assert sorted(f.key for f in flusher.drain()) == [
        "pra/v1/a/status/T0-000000000001-000000000001.jsonl.gz",
        "pra/v1/b/status/T0-000000000002-000000000002.jsonl.gz",
    ]
    assert flusher.pending() == 0


def test_dir_sink_writes_atomically_under_the_key(tmp_path):
    sink = DirSink(tmp_path)
    sink.write("pra/v1/c1/tele.step/T0-1-2.jsonl.gz", b"data")
    assert (tmp_path / "pra/v1/c1/tele.step/T0-1-2.jsonl.gz").read_bytes() == b"data"
    assert not list(tmp_path.glob("**/*.tmp"))


def test_prune_plan_deletes_only_old_and_mirrored():
    ids = ["snap-9", "snap-8", "snap-7", "snap-6"]
    assert prune_plan(ids, keep=2, mirrored={"snap-7", "snap-9"}) == ["snap-7"]
    assert prune_plan(ids, keep=0, mirrored=set(ids)) == ids
    assert prune_plan(ids, keep=10, mirrored=set(ids)) == []


def test_payloads_without_seq_still_flush():
    flusher = Flusher(stamp=lambda: "T0")
    flusher.add("pra.v1.run.c1.status", b"not-json", "a", now=0.0)
    flush = flusher.drain()[0]
    assert flush.key == "pra/v1/c1/status/T0-000000000000-000000000000.jsonl.gz"
    assert gzip.decompress(flush.data) == b"not-json\n"
