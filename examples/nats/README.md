# The NATS worked example (feature 014, ROADMAP B6)

Two processes, one real server: a live PRA brain publishing its telemetry,
and a separate watcher that consumes it, drives the control plane, and pulls
a snapshot back out of the JetStream object store. This is the integration
proof that the contract the in-repo fake transport encodes is the contract
the real NATS stack honors — the quality gate itself never needs any of
this.

## The one command

```bash
pip install "poseres[nats]"
python examples/nats/demo.py
```

`demo.py` finds a NATS server (a running one on `:4222`, a `nats-server`
binary on PATH, or Docker — it runs
`docker run --rm -p 4222:4222 nats:latest -js`), starts `brain.py` and
`watch.py` as separate processes, and exits **zero only when every proof
passed**:

1. **Telemetry off-process** — the watcher receives live `tele.step` and
   `tele.census` messages for the run under
   `pra.v1.run.demo.…` (discovered via `pra.v1.discover`, never guessed).
2. **The control round-trip** — `inspect` answers; `pause` freezes the
   mirrored step counter (verified twice, 300 ms apart); `resume` continues;
   `snapshot` is fulfilled at the engine's next cadence boundary and the
   reply carries the new snapshot's id.
3. **The snapshot round-trip** — the watcher pulls the blob back from the
   `pra-snapshots` object-store bucket and decodes it as a real PRA
   snapshot with the expected seed.

## What you will see

```
demo: starting nats-server -js
brain: run 'demo' live on nats://127.0.0.1:4222
watch: discovered run 'demo' (running)
watch: live telemetry flowing (23 steps so far)
watch: inspect ok at step 41
watch: paused and frozen at step 58
watch: snapshot-on-request fulfilled: snap-000000000400-00004
watch: snapshot verified — 31482 bytes, seed 1, cycle 4, population present
watch: run completed — best_dim 3, all proofs PASS
brain: run complete — summary follows
{...the canonical per-seed summary...}
demo: ALL PROOFS PASS
```

(Step numbers and sizes vary with timing; the proofs do not.)

## Watching by hand instead

With the brain running (`python examples/nats/brain.py`), any NATS client
can watch — for example the `nats` CLI:

```bash
nats sub 'pra.v1.run.demo.tele.>'
nats sub 'pra.v1.run.demo.brain.>'   # feature 029: anatomy, per-frame rows, spawn/evict
nats req 'pra.v1.run.demo.ctrl' '{"cmd":"inspect"}'
nats req 'pra.v1.run.demo.ctrl' '{"cmd":"pause"}'
nats req 'pra.v1.run.demo.ctrl' '{"cmd":"resume"}'
nats req 'pra.v1.discover' '{}'
```

Kill the server mid-run if you like: the brain finishes at full stride with
its drop counters raised and a byte-identical summary — the run never waits
on the network. That claim is not this example's; it is proven by the test
suite on the fake transport (`tests/integration/test_nats_fake_run.py`).

## The dashboard (feature 015, ROADMAP B7)

One face for any brain: the same subjects, rendered.

```bash
pip install "poseres[nats]"
python examples/nats/dashboard_demo.py
```

A rover brain comes up with its world-view channel on, the dashboard
starts, and the printed URL opens to the live page: **Simple** shows the
rover driving its arena (pose, trail, obstacles — the B1 viewer, now from
any machine); **Advanced** shows the census history, best_dim trajectory,
per-dim histogram, the honesty counters, and the four control buttons with
replies shown verbatim. The demo verifies its proofs headlessly (telemetry
consumed, world view served, pause → frozen → resume → snapshot through
the dashboard's own endpoint) and exits zero only when they pass — the
browser is the reward, not the requirement.

Point the dashboard at anything:

```bash
pra-dash --url nats://127.0.0.1:4222   # every tap-attached run appears
```
