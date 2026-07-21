# Feature Specification: The Observatory — Deployment Split, Durable Telemetry, One Node

**Feature Branch**: `032-deployment-observatory`
**Created**: 2026-07-21
**Status**: Draft
**Input**: User description: "Deployment split for the multi-week run on beno4: infrastructure (nats+jetstream buffer, minecraft, minio/s3) vs shared observability (pra-dash, s3 flusher) vs per-experiment units (bridge+brain, templated for multi-brain); JetStream 1h buffer flushed durably to S3; systemd supervision; node provisioning"

## Overview

The multi-week C1 run moves off the laptop onto a dedicated node
(`beno4`: 32 cores / 122 GB / x86_64 Ubuntu). The owner's architecture,
adopted with one correction from the seam analysis: **infrastructure**
(NATS with a JetStream ring buffer, the Minecraft server, the S3
endpoint) is shared; **observability** (pra-dash — already multi-run by
design — and the new S3 flusher) is shared; **each experiment** is a
bridge+brain pair (the bridge owns one bot, so it is body, not
environment), templated so N brains can later share one world. Durable
truth lives in S3: JetStream holds a ~1-hour buffer and a small flusher
consumes it durably (ack-after-write, at-least-once) into compressed
batches — this is what makes the run's "published telemetry" exit
criterion and the crafting-emergence analysis computable afterwards.
Supervision is systemd (`Restart=on-failure` per unit), closing the
unattended-restart gap from the launch audit; brain restarts resume
from the newest snapshot by the proven path.

Default S3 endpoint is a MinIO container on the node (so the stack is
complete and testable today); pointing the flusher at real S3 is an
env-file change — stated, not hidden.

## User Scenarios & Testing

### US1 — Telemetry survives everything (P1)

Every `pra.v1` message lands in S3 within minutes, batched and
compressed; a flusher crash loses nothing while the buffer outlives the
outage; the run's whole history is queryable after weeks.

**Acceptance**: fake-carried contract tests: batching by subject family,
ack-only-after-write, object naming carries run/family/sequence range;
live: a short run on beno4 produces objects in MinIO whose decoded
contents match the published messages, gap-free by seq.

### US2 — The three layers, deployable and supervised (P1)

`deploy/` in the repo: infra compose (nats+minecraft+minio),
observability + experiment systemd units (dash, flush, `pra-bridge@`,
`pra-brain@` templated on an experiment env file), an idempotent
`provision.sh`, and the beno4 runbook. A killed unit restarts itself;
a restarted brain resumes from its newest snapshot.

**Acceptance**: on beno4 — units enabled and running; kill the bridge →
systemd restarts it; kill the brain → it restarts and logs a resume;
the c1 experiment env file is the only per-experiment configuration.

### US3 — Multi-brain ready (P2)

A second experiment env file (own bot name, bridge port, run id, seed,
snapshot dir) yields a second bridge+brain pair against the same world
and NATS; the dashboard shows both runs; telemetry stays run-scoped.

**Acceptance**: template instantiation documented and smoke-checked
(second pair boots and appears on the bus; full multi-brain science is
a later, deliberate run-plan choice — bots interact through terrain,
stated).

### Edge cases

- Flusher down > buffer age: the gap is real and *visible* (seq gaps in
  S3 batches) — never silently repaired (constitution II).
- S3 down: flusher retries with backoff; JetStream absorbs ≥1h.
- Snapshots: newest-N kept locally for fast resume; every blob mirrored
  to S3 by the same flusher discipline (closes the no-pruning disk
  audit item).
- Dash binds 127.0.0.1 on the node; the operator reaches it by SSH
  tunnel (stated; exposing it is an explicit choice).
- beno4 disk: 46 GB free; with S3 offload the steady-state local
  footprint is world + buffer + last-N snapshots (budgeted in runbook).

## Requirements

- **FR-001**: A `pra-flush` service: durable JetStream consumer over
  `pra.v1.>` (1h/file-store stream, created idempotently), batches per
  run+family per interval, gzip JSONL to S3, ack after write; S3 client
  behind an optional `[s3]` extra (boto3), endpoint/bucket/creds via
  env; a directory sink for tests and S3-less use.
- **FR-002**: Flusher core logic (batching, naming, ack discipline)
  MUST be testable in-repo without brokers or S3 (fake source + dir
  sink carry the gate; the JetStream/boto3 bindings are thin adapters).
- **FR-003**: `deploy/` MUST contain: infra compose, systemd units
  (dash, flush, `pra-bridge@`, `pra-brain@`), per-experiment env files
  (`c1` shipped), an idempotent `provision.sh`, and the runbook
  (`deploy/README.md`) with node specs, tunnel access, disk budget,
  and the real-S3 switch.
- **FR-004**: Brain units MUST resume on restart (the existing
  newest-snapshot path) and keep only newest-N snapshots locally once
  mirrored (N configurable; deletion only after confirmed S3 write).
- **FR-005**: Zero engine/dash changes; the flusher is a pure consumer
  of the published protocol.
- **FR-006**: End-to-end verification on beno4: a short real run with
  the full stack, objects in MinIO matching the stream, supervised
  restart observed, dashboard reachable through the tunnel.

## Success Criteria

- **SC-001**: gate green with flusher tests carried by fakes; no new
  hard deps (boto3 optional).
- **SC-002**: on beno4: kill-and-recover for bridge and brain observed;
  telemetry objects in MinIO decode to the exact published messages.
- **SC-003**: the c1 experiment is one env file; a second experiment
  needs only a second env file.
- **SC-004**: local disk footprint bounded (snapshot retention active);
  the runbook states the budgets.

## Assumptions

- MinIO on-node is the default S3 (stack complete today); real S3 is an
  env change the owner makes when ready. Off-node durability until then
  is the owner's known gap.
- The RUN-PLAN pre-registration and the overnight 28/12 soak ride along
  with this feature's landing (audit items 2–3) but are experiment
  documents, not deployment code.
- Wall-clock timestamps appear in S3 *object keys* (operational layer),
  never inside payloads (the recorder discipline stands).
