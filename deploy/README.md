# The Observatory — running the multi-week experiment on a node (feature 032)

Three layers on one box (sized: 4 vCPU / 12 GB suffices; no GPU — the
brain is numpy, the heavyweight is the Minecraft JVM):

| Layer | What | How it runs |
|---|---|---|
| Infrastructure | NATS (+ JetStream 1h ring buffer), Minecraft server, MinIO (default S3) | `deploy/infra/compose.yml`, `restart: unless-stopped` |
| Observability (shared) | `pra-dash` (multi-run by design), `pra-flush` (buffer → S3, ack-after-write) | systemd, `Restart=on-failure` |
| Experiment (× N) | one bridge (one bot — the body) + one brain | `pra-bridge@<name>` / `pra-brain@<name>` on `/etc/pra/<name>.env` |

## Provision / update

```bash
rsync -a --exclude .venv --exclude '**/node_modules' --exclude '**/data' \
      --exclude '**/__pycache__' <repo>/ <node>:~/pra/     # or git pull, once pushed
ssh <node> '~/pra/deploy/provision.sh'                     # idempotent
```

## Start / stop the run

```bash
sudo systemctl enable --now pra-bridge@c1 pra-brain@c1   # start
journalctl -fu pra-brain@c1                              # watch
sudo systemctl disable --now pra-brain@c1 pra-bridge@c1  # stop (brain resumes on next start)
```

The brain resumes from its newest snapshot on every restart (proven
byte-exact); systemd restarts any crashed unit — the unattended-night
gap from the launch audit is closed. **Keep `SEED` and `TICK_MS` fixed
for the life of a run** (config-in-force travels in snapshots).

## Watching

- Dashboard: `ssh -L 8600:localhost:8600 <node>` → http://localhost:8600
  (bound to localhost on the node; exposing it is your explicit choice).
- Spectating: connect Minecraft 1.21.11 to `<node>:25565`, then
  `docker compose --project-directory ~/pra/deploy/infra exec minecraft rcon-cli "gamemode spectator <you>"`.
- MinIO console: `ssh -L 9101:localhost:9101 <node>` → http://localhost:9101.

## Durable telemetry

`pra-flush` consumes the `PRA_V1` stream (created idempotently, file
store, 1h max age) with a durable consumer and writes gzip JSONL batches
to S3 as `pra/v1/<run>/<family>/<utc>-<seq_first>-<seq_last>.jsonl.gz` —
acked only after the write, so a flusher outage shorter than the buffer
loses nothing, and gaps stay *visible* in the key ranges. Delivery is
**at-least-once**: analysis dedupes by `(run, family, seq)` — duplicates
are possible around restarts, never silent loss. Snapshots are
mirrored to `pra/v1/_snapshots/` and the local store pruned to newest-5
(only after a confirmed mirror).

**Real S3 instead of MinIO**: edit `/etc/pra/s3.env` (bucket, creds;
empty `PRA_S3_ENDPOINT` = AWS), then `sudo systemctl restart pra-flush`.
Until then, durable-off-node is not yet true — MinIO lives on the node.

## A second brain (multi-experiment)

Copy `deploy/experiments/c1.env`, change `BOT_NAME`, `BRIDGE_PORT`,
`RUN_ID`, `SNAPSHOT_DIR` (and `SEED`), re-run `provision.sh`, then
`enable --now pra-bridge@<name> pra-brain@<name>`. Telemetry is
run-scoped, the dashboard lists every run. Note the science: bots share
one world and interact through terrain edits — deliberate choice, not a
surprise (`c1-smoke` is the shipped example twin). Snapshot mirroring
for extra experiments: add their `--snapshot-dir` to a second flush
unit or extend the flush unit's arguments.

## Disk budget (98 GB disk, ~46 GB free at provision)

world grows slowly (view distance 6); JetStream ≤ ~1h of stream (tens
of MB); MinIO grows ~30–60 MB/day compressed telemetry + snapshot
mirrors (each snapshot grows ~8 B/step; newest-5 kept locally);
`journalctl` is the log store (systemd caps it). Weeks fit comfortably;
`df -h` on your visits is the honest meter.
