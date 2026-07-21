# Implementation Plan: The Observatory

**Branch**: `032-deployment-observatory` | **Date**: 2026-07-21 | **Spec**: [spec.md](spec.md)

## Summary

New `src/pra/flush/` module (`pra-flush` console script): a durable
JetStream→S3 flusher whose core (batching, naming, ack discipline) is
pure and fake-carried; boto3 behind a new `[s3]` extra mirroring the
`[nats]` pattern. New top-level `deploy/`: infra compose
(nats+minecraft+minio), systemd units (dash, flush, `pra-bridge@`,
`pra-brain@` on `/etc/pra/<name>.env`), idempotent `provision.sh`,
beno4 runbook. Code reaches the node by rsync until the owner pushes
the branches; provisioning is idempotent either way.

## Technical Context (deltas from 031)

**New optional dep**: boto3 (`[s3]`); nats-py already in `[nats]` (the
JetStream consumer binding lives beside NatsTransport).
**Node**: beno4 — 32c/122G/x86_64 Ubuntu, Docker 29 + compose v5,
Python 3.14, node 26, passwordless sudo, user calmera.
**Flusher architecture**: `Flusher(source, sink, *, flush_interval,
flush_bytes)` — source yields `(subject, payload, ack)`; sinks:
`DirSink` (tests + S3-less), `S3Sink` (boto3, lazy import, endpoint
from env). Object keys:
`pra/v1/<run>/<family>/<utc>-<seq_first>-<seq_last>.jsonl.gz`.
Snapshot mirroring: the flusher also subscribes the snapshot-notice
subject and uploads new blobs from the store directory, then prunes
local to newest-N.
**Constitution**: I PASS (zero core edits); II (gaps visible, ack
discipline tested); VI applies. No violations.

## Structure

```text
src/pra/flush/__init__.py   # Flusher core + DirSink + S3Sink + JetStreamSource
src/pra/flush/cli.py        # pra-flush entry point (env-driven)
pyproject.toml              # [s3] extra; pra-flush script
tests/unit/test_flusher.py  # batching/naming/ack/retention via fakes
deploy/
├── README.md               # the beno4 runbook (provision, budgets, tunnel, real-S3 switch)
├── provision.sh            # idempotent: rsync'd repo -> venv -> units -> compose up
├── infra/compose.yml       # nats (JetStream file store) + minecraft + minio
├── units/pra-dash.service  pra-flush.service  pra-bridge@.service  pra-brain@.service
└── experiments/c1.env      # BOT_NAME, BRIDGE_PORT, RUN_ID, SEED, TICK_MS, SNAPSHOT_DIR, CYCLES
hq/02-DESIGN/validate/C1-RUN-PLAN.md  # the pre-registration (rides along)
```

## Verification on the node (FR-006)

provision → infra up → c1 units up (short-cycle brain) → objects in
MinIO decode to published messages → kill bridge and brain, watch
systemd restart + resume → tunnel dashboard check → overnight fake
soak launched (`nohup`, results read next session).
