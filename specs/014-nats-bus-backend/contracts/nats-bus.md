# Contracts: The External Bus Backend (NATS at the Seams)

Phase 1 of `plan.md`. The testable promises, grouped by seam. Every
clause here maps to at least one test in the suites named by the plan;
the fake transport (`fake.py`) is the instrument for all of them
(FR-008), and the worked example is the real-stack proof (FR-011).

## §1 Transport contract (`BusTransport`, both implementations)

1. `publish(subject, payload)` is fire-and-forget: it never raises for
   delivery failure and never blocks beyond a local enqueue; in the
   `down` state it increments `publish_failures` and returns.
2. `subscribe(subject, handler)` delivers each published message on
   that subject to the handler at most once, in publish order (the
   fake: exactly once, synchronously journaled; the real stack:
   at-most-once core NATS semantics — stated, not hidden).
3. `serve_requests(subject, handler)` invokes `handler(payload) →
   reply-payload` per request and delivers the reply to the requester;
   `request(subject, payload, timeout)` returns the reply bytes or
   raises on timeout — loudly, naming the subject.
4. Object-store ops (`object_put/get/list/delete`) are synchronous and
   loud: failures raise naming the bucket, operation, and object; `get`
   of a missing object raises `KeyError`-equivalent naming the id.
5. `healthy` reflects the up/down state; transitions down→up increment
   `reconnects`. The fake exposes `set_down()`/`set_up()` to script
   outages; the journal records every publish with its subject and
   payload bytes.
6. `close()` is idempotent and releases the loop thread (real) /
   clears handlers (fake).

## §2 Tap contract (observer safety + the mirror)

1. **Byte-identity attached/absent** (FR-002/SC-002): same config, same
   seed, one run with the tap's factories and one without → serialized
   summaries byte-identical. Asserted for the reference world and for a
   multi-stream continuous run.
2. **RNG non-perturbation**: the engine generator's bit-state after a
   tap-attached run equals the state after the bare run (007/013
   pattern).
3. **Mirror fidelity**: over the fake transport, the `tele.step`
   journal reproduces the run's exact (stream, episode, step, action)
   sequence, and each `obs` equals the world's returned observation at
   that step (compared against a reference run's recorded values).
   Payloads are byte-deterministic across identical runs.
4. **No backpressure** (FR-003): with `buffer_size` forced tiny and the
   publisher stalled, the run completes at full stride to a
   byte-identical summary; `events_dropped` equals the sequence-gap
   total; with the transport `down` for a run's whole life, same
   byte-identity, `publish_failures > 0`.
5. **Census discipline**: the census derives only on the publisher
   thread, only via `frame_states()` + the run's scorer on copies; a
   scripted torn read (store raising mid-scan) yields the last good
   census, never an exception and never a run-path effect.
6. **Counters stay outside the learning surface** (FR-012): no engine,
   world, drive, or scorer code path reads any tap counter (asserted
   structurally: the tap is never passed inward; the wrapped world
   exposes the inner world's public surface unchanged).
7. **Status lifecycle**: `started` is published at first boot with the
   anatomy's public numbers; `completed` with the canonical summary
   when the caller invokes `tap.finish(summary)`.

## §3 Control contract (`control.py`)

1. **Pause is boundary-exact** (FR-006/SC-005): after a `pause` reply,
   the run halts before the next world transition; no observation is
   produced while paused (journal quiescent); `resume` continues the
   schedule; the completed paused-then-resumed run's summary is
   byte-identical to the never-paused run (steppable world).
2. **Pause semantics documented**: schedule-relative; on a
   free-running world the world keeps moving (stated in docs; §5b
   class 4 unchanged — R9). Idempotent pause/resume with the state
   named in the reply.
3. **Inspect is read-only**: replies with run identity, state, mirrored
   counters, last census, tap counters; provably touches no live
   engine state (derives from tap fields only) and answers in every
   state including `completed`.
4. **Snapshot is honestly deferred** (R5): on a snapshot-configured
   run, the reply arrives after the next C4 store write and carries
   that write's id; on a run with no store or zero cadence, an
   immediate error reply names the missing configuration; a run that
   completes first produces an error reply, never silence.
5. **Every malformed request is answered**: non-JSON, non-object,
   unknown `cmd` → `{ok: false, error}` naming the problem; the run
   thread never observes any of it.
6. **Discovery**: a `pra.v1.discover` request receives one reply per
   live tap, each naming its run id and full subject set.

## §4 Store contract (`NatsSnapshotStore`)

1. **Protocol fidelity**: implements `write/read/list/delete` with the
   existing metadata contract; ids come from `snapshot_id_for`; `list`
   is newest-first — asserted by the same expectations the existing
   store contract tests apply to `FileSnapshotStore`/
   `InMemorySnapshotStore`, run against the fake-backed instance.
2. **Byte-exact round-trip** (SC-004): `read(write(blob, meta)) ==
   blob` bit-for-bit, and the listed metadata equals the written
   metadata after canonical serialization — at reference size and at a
   realistic scaled-run size.
3. **Resume equivalence** (SC-004): an engine resumed from a blob
   fetched through the object store produces a summary byte-identical
   to one resumed from the same snapshot in a `FileSnapshotStore`.
4. **Loud failures** (FR-005): a missing snapshot id raises `KeyError`
   (the protocol's own contract — the file store's grammar, matched);
   transport trouble raises `RuntimeError` naming store, operation, and
   id; bounded timeout — no hang. A store with no bucket yet lists `[]`
   (an empty store, exactly like a fresh directory), and `delete` is
   idempotent.
5. **Engine-side blocking is stated**: a store-backed run blocks at C4
   for the write's duration — the user's explicit backend choice,
   documented in quickstart and §5b.

## §5 Dependency & regression contract

1. **Gate is NATS-free** (FR-007/SC-001): the full suite passes with no
   `nats-py` installed and no server running, zero skips; requesting
   `NatsTransport` or `NatsSnapshotStore` without the library raises a
   clear error naming `pip install "poseres[nats]"` (monkeypatched
   test).
2. **Purely additive** (FR-009): no edits under `core/`, `harness/`,
   `persistence/`, `world/`, or `config.py`; the only file touched
   outside the new directories is `pyproject.toml` (the `nats` extra)
   plus the closing docs (Doc 06 §5b, ROADMAP, JOURNEY).
3. **§5b recorded** (FR-010/SC-006): telemetry-out observer-safe;
   pause class-preserving; store-backed snapshots inherit their world's
   class; experience-in named class 4 and out of scope — all present in
   Doc 06 §5b before the feature merges.

## §6 Worked-example contract (`examples/nats/`, outside the gate)

1. `demo.py` exits zero only if: a separate consumer received live
   `tele.*` messages for the run; `inspect`, `pause`, `resume`, and
   `snapshot` round-trips completed; and the snapshot pulled from the
   object store byte-matched the store's write.
2. Without a reachable server, `demo.py` fails with a message naming
   the two ways to get one (local `nats-server`, the documented
   `docker run … nats:latest -js`); without the extra, the R7 error —
   never a traceback.
