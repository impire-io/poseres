# Episode 0051 — The observatory: the run gets a home (2026-07-21)

Feature 032 (`032-deployment-observatory`): the multi-week run moved
off the laptop onto `beno4` (32c/122G x86_64 — a shared box, discovered
politely: MinIO moved to 9100/9101 because another service owns 9000).
The owner's three-layer architecture, built with one seam correction:
**infrastructure** (NATS + a 1-hour JetStream ring buffer, the
Minecraft server, MinIO as the default S3) and **observability**
(pra-dash — multi-run by design — and the new `pra-flush`) are shared;
**each experiment** is a bridge+brain systemd pair on one env file (the
bridge owns one bot, so it is body, not environment — N brains against
one world is a file-copy away, with the terrain-interaction
non-stationarity named as a deliberate later choice, not a surprise).

`pra-flush` is the durability piece the exit criterion needed: a
durable JetStream consumer batching per (run, family) into gzip JSONL
S3 objects whose keys carry seq ranges — gaps visible, never repaired —
acked only after the write. The core is pure and fake-carried (the
gate needs no broker, no S3; boto3 rides a new `[s3]` extra mirroring
the `[nats]` pattern); snapshots mirror to S3 and the local store
prunes to newest-N only after a confirmed mirror (closing the
accumulate-forever disk finding). systemd `Restart=on-failure`
closes the unattended-night gap; the brain resumes from its newest
snapshot on every restart by the proven path.

Verified live on the node, end to end [measured]: provision idempotent;
the c1-smoke twin experiment (second bot, second bridge, run id
`c1smoke`) ran the honest 28/12 body against the real server under
systemd — 1,720 steps, clean completion — with the dashboard listing
the run and MinIO holding every family's batches (tele.step,
tele.census, brain.anatomy/frames/events, status). The kill test
passed (bridge SIGKILLed → systemd brought it back, run unharmed).
**And the live stack caught a real flusher bug the unit tests could
not**: the ack-after-write discipline holds messages unacked for the
whole flush interval, and JetStream's 30-second default `ack_wait`
redelivered them into the same batch — 2,007 lines for 626 seqs, a
3.2× duplication, measured in the first real object. Fixed
(`ack_wait ≥ 3× interval`), consumer recreated, re-verified: 626
lines, 626 unique seqs, ordered. The at-least-once contract (dedupe
by run+family+seq) is now stated in the runbook instead of discovered
by the analyst.

The run itself is pre-registered before boot
(`hq/02-DESIGN/validate/C1-RUN-PLAN.md`): seed 1, real-time 250 ms
posture (no world acceleration — emergence is denominated in
brain-steps), ≥14 days of accumulated steps, and the readings R1–R5 —
headlined by the emergence bar against feature 031's measured chance
baseline (~1 accidental planks-craft per ~2,200 undirected steps,
zero sticks). The last pre-launch gate, the ~1M-step length soak of
the 28/12 body at the launch config (no-rot + resume-at-length), was
launched on the node as this episode was written; its numbers append
to the run plan before boot.

Reversal condition: none — records a completed build/deployment; the
run's own reversal reading is R4 in the pre-registration.

Trail: specs/032-deployment-observatory/; deploy/ (runbook incl. node
sizing: 4 vCPU / 12 GB suffices, no GPU — the brain is numpy);
commits 8172110, bafc112, 791d34d; soak in beno4:~/pra-runs/soak/.
