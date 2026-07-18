# Research: The External Bus Backend (NATS at the Seams)

Phase 0 of `plan.md`. Every decision below is stated as
decision / rationale / alternatives, and each traces to a functional
requirement of `spec.md` or a working rule of `AGENTS.md`. The
load-bearing verification behind this document: the engine's injection
seams were read at source before any shape was chosen, and one obvious
design died on a fact — the engine's hot loop does **not** route steps
through `Bus.publish` (it drives the batched `FrameProcessor` directly;
`src/pra/core/bus.py` docstring), so "wrap the bus and mirror its
events" observes nothing. What the B1 viewer actually proved is subtler
and better: capture references at injection time, mirror plain values on
the run path, derive everything else on a background thread
(`src/pra/examples/rover/viewer.py`). This feature generalizes exactly
that discipline off-process.

## R1 — Attach shape: one tap object binding three existing injection seams; no engine edits

**Decision.** A subpackage `src/pra/nats/` whose central object,
`NatsTap`, binds the three injection seams the `Engine` constructor
already exposes (engine.py:95-109), all pure delegation:

1. **`world_factory` wrapper** — `tap.world_factory(inner_factory)`
   returns a factory producing `_TapWorld` delegates. Each `_TapWorld`
   forwards `reset()`/`step(action)` to the wrapped world unchanged and
   mirrors plain copies (action index, observation array copy, episode
   and step counters, stream index by construction order — the engine
   constructs worlds `k = 0..K-1` in order, engine.py:174-176) into the
   tap's bounded buffer. `__getattr__` passthrough preserves every
   duck-typed contract the engine reads (`n_actions`,
   `snapshot_needs_state`, `state_dict`/`load_state_dict`,
   `apply_pending_tools`). This is the per-step surface — and the pause
   gate (R2).
2. **`bus_factory` capture** — the viewer pattern verbatim
   (viewer.py:79-83): keep the live `FrameStore` reference, return the
   stock `InMemorySyncBus` unchanged. The store reference feeds the
   census (R3) on the publisher thread through public read-only
   accessors; the engine's delivery seam is byte-for-byte the object it
   would have had anyway.
3. **snapshot-store wrapper** — `tap.wrap_store(inner_store)` returns a
   delegating `SnapshotStore` that forwards `write/read/list/delete`
   and, on each `write` (the engine's C4 call site, engine.py:578),
   records `(snapshot_id, metadata)`, publishes a snapshot-written
   notice, and fulfills any pending control-plane snapshot request (R5).

Nothing in `core/`, `harness/`, `config.py`, or `persistence/` changes;
the tap activates only when the user passes its factories to `Engine`
(FR-001, FR-009).

**Rationale.** These are the seams the architecture already drew, each
with a validated non-perturbation precedent: `world_factory` is how
Gymnasium (007) and ROS2 (013) mount whole worlds; `bus_factory` is how
the B1 viewer proved byte-identity with an observer attached;
`snapshot_store` is Doc 06's injection point. A delegating wrapper on an
injection seam is invisible to the engine by construction — the
byte-identity tests make it invisible by proof.

**Alternatives considered.** (a) A delegating `Bus` that mirrors
published events — rejected on the read fact above: the hot loop calls
`store.online_step` directly (engine.py:296); `publish` is the
contract-test path, so a bus wrapper sees zero traffic in a real run.
(b) A new engine callback/hook — rejected: spec FR-009 forbids engine
edits, and the 004 precedent (one inert duck-typed hook) is a last
resort for capabilities no seam can carry; three seams carry this one.
(c) Store-polling only (no world wrapper) — rejected: no per-step
attribution (SC-003 requires run/stream/step on every message) and no
legal pause point (FR-006).

## R2 — The run-path budget and the pause gate: what the tap may do inside a step

**Decision.** The wrapped `step()` does exactly this before delegating:
one `threading.Event` check (the pause gate), and after delegating:
increment two integers, copy the small action/observation values, and
`append` one tuple to a bounded `collections.deque`. No RNG anywhere, no
float derivation, no locks (a `deque.append` is atomic under the GIL —
the viewer's trail precedent, viewer.py:73-77). The **pause gate**: when
the control plane sets the paused flag, the wrapped `step()` (and
`reset()`) blocks on the event *before* forwarding to the inner world —
after the engine has drawn this step's action, before the world
transitions and before the next step's float work. While blocked,
nothing advances and nothing draws; on resume the call proceeds
unchanged, so a paused-and-resumed seeded run on a steppable world
completes byte-identical to an unpaused one (SC-005 — asserted by
integration test, not argued). The reported pause position is the tap's
mirrored step count.

**Consequences (documented, not hidden).** Pause halts the *schedule*,
not the world's clock: a free-running world (013's real-time mode) keeps
moving while the schedule is blocked, and the next observation will have
moved on — stated in the docs; such runs are §5b class 4 already, and
pause does not change their class (R9). The gate costs one event check
per step when unpaused — pure Python, no measurable dent next to
`store.online_step`'s matrix work, and byte-identity is unaffected
regardless.

**Alternatives considered.** (a) Pausing inside a wrapped policy —
rejected: the policy seam is mode-dependent (baseline vs curiosity
construct different defaults, engine.py:124-129) and replacing it
touches the action path this feature must never touch. (b) Pausing only
at cycle boundaries via the store wrapper — rejected: FR-006 says step
boundaries, and a cycle at scale is thousands of steps. (c) An
OS-signal-based pause — rejected: not a request/reply surface, no
reply semantics, nothing B7 can build on.

## R3 — The publisher thread and the no-backpressure mechanics: drop, count, never wait

**Decision.** One daemon publisher thread per tap (the viewer's serving
thread, generalized). The run path only ever appends to the bounded
mirror deque (maxlen configurable, default 4096 events); when full, the
deque evicts oldest — the run thread never blocks, never allocates
unboundedly, never touches the network (FR-003). Every mirrored event
carries a monotonically increasing sequence number, so drops are
*derived*, not counted on the run path: the publisher tracks the last
sequence it drained, and any gap is `events_dropped`. The publisher
wakes on a short poll interval (default 50 ms), drains the buffer,
serializes (R4), and hands each message to the transport
fire-and-forget; a transport in a failed state counts
`publish_failures` and `reconnects` instead of raising. At census
cadence (default 500 ms) it derives the population reading exactly the
way the viewer does (viewer.py:112-139): `FrameStore.frame_states()` on
the captured reference, scored on copies with the run's own scorer,
`try/except` with last-good fallback — a torn read costs one stale
census, never a byte of the run. All counters (`events_mirrored`,
`events_published`, `events_dropped`, `publish_failures`, `reconnects`)
live on the tap object, readable outside the learning surface (FR-012).

**Payloads carry no wall-clock time.** Sequence numbers and the run's
own counters (step, episode, cycle, stream) are the only ordering
facts; receipt time is the consumer's business. This keeps every
payload over the fake transport fully deterministic — contract tests
byte-compare them — and keeps the honest clock (the run's counters)
separate from the network's clock.

**Alternatives considered.** (a) Publish synchronously from the run
thread — banned by FR-003 outright. (b) An unbounded queue — rejected:
a dead consumer would grow memory without bound; bounded-with-derived-
drop-count is the honesty meter (spec edge case). (c) Condition-variable
wakeup instead of polling — rejected: the notify side would put a lock
acquisition on the run path; a 50 ms poll on a daemon thread costs
nothing the run can feel. (d) Drop-newest instead of drop-oldest —
rejected: a reconnecting consumer wants the run's *recent* state; the
census message makes any gap self-healing.

## R4 — The subject scheme and the wire form: versioned, run-scoped, canonical JSON

**Decision.** `subjects.py` owns the scheme; everything is rooted under
a versioned prefix and namespaced by run identity (FR-004):

| Subject | Payload |
|---|---|
| `pra.v1.run.<run_id>.status` | announce (`started`, config fingerprint, anatomy sizes) and completion (`completed`, the canonical per-seed summary) |
| `pra.v1.run.<run_id>.tele.step` | seq, stream, episode, step, action, observation |
| `pra.v1.run.<run_id>.tele.episode` | seq, stream, episode — boot/reset boundaries |
| `pra.v1.run.<run_id>.tele.census` | population, per-dim counts, best_dim, best_score, pred_err_ema, step counters |
| `pra.v1.run.<run_id>.tele.snapshot` | snapshot_id + the engine's write metadata (step, cycle, population, format_version) |
| `pra.v1.run.<run_id>.ctrl` | request/reply (R5) |
| `pra.v1.discover` | request; every live tap replies with its identity |

`run_id` is a user-supplied token (validated: no `.`, `*`, `>`,
whitespace) or a default `run-<8 hex>` drawn from `uuid4` — OS entropy,
never the engine's generator (the byte-frozen stream is untouched;
asserted by the bit-generator state test, the 007/013 pattern). Two runs
on one server cannot cross-talk because every run-scoped subject embeds
the id (SC-003). Wire form is canonical JSON with the recorder's
discipline (recorder.py:124-162): fixed key order, compact separators,
`ensure_ascii` — one serialization idiom for the whole project. The
`pra.v1.` root leaves sibling space (`pra.v1.brain.*` is *reserved and
unimplemented* — the inter-brain horizon named by the spec, foreclosed
by nothing, built by nothing; FR-004).

**Rationale.** B7 builds against these names (SC-006), so they are
versioned from the first release; a scheme change is a `v2` root, never
a silent mutation. Discovery is a request/reply sweep rather than
retained announcements because core NATS has no retained messages and
v1 buys durability only where it is the point (the object store — spec
assumption "live tap, not history").

**Alternatives considered.** (a) JetStream-backed telemetry streams for
replayable history — deferred to B7's stated needs, per the spec
assumption; the tap's contract (fire-and-forget, drop-counted) does not
change if a consumer-side stream is added later, which is exactly why it
can wait. (b) Binary payloads (msgpack/protobuf) — rejected for v1: a
new dependency and a schema compiler to save bytes on payloads measured
in tens of floats; canonical JSON is already the project's byte-stable
idiom. (c) Hierarchical per-stream subjects (`...tele.step.<k>`) —
rejected: the stream index is payload, not routing; K is small and
subscribers filter trivially.

## R5 — The control plane: three commands, boundary-exact, deferred snapshot fulfillment

**Decision.** The tap subscribes to `...ctrl` (request/reply). Requests
and replies are canonical JSON; every malformed or unknown request gets
`{"ok": false, "error": "<what and why>"}` and the run never notices
(FR-006). Commands:

- **`inspect`** — read-only: run_id, state (`running` / `paused` /
  `completed`), mirrored step/episode counters, the latest census, the
  tap's own counters. Derived entirely from tap state + the last-good
  census; touches nothing live.
- **`pause`** / **`resume`** — set/clear the gate event (R2). The pause
  reply carries the position at which the schedule will hold (the next
  gated call blocks); resume's reply confirms. Pausing a paused run (or
  resuming a running one) is an idempotent `ok` with the state named.
- **`snapshot`** — honest deferred fulfillment: the engine writes
  snapshots only at its C4 cadence boundary (engine.py:456-459), and no
  external thread can force one mid-cycle without engine edits. So the
  command *requires the run to be snapshot-configured* (store injected
  and `snapshot_every_n_cycles > 0`); it registers a pending request,
  and when the store wrapper (R1.3) observes the next engine write, the
  reply is sent carrying that snapshot's id. Error replies name the
  problem when the run has no store or no cadence, and when the run
  completes before the next boundary. A paused run cannot reach a
  boundary — documented: resume first. The requester sets its own
  timeout sized to the run's cadence (the example does).

**Rationale.** This is the largest honesty decision in the feature: a
snapshot is only well-defined at C4 (the engine's own comment:
"capture consumes no RNG and mutates nothing" — engine.py:461-462), and
pretending to snapshot mid-cycle from another thread would tear the
state the whole persistence feature exists to protect. Deferred
fulfillment keeps the reply contract (the reply carries the id, spec
US3) while telling the truth about *when*. If B7 needs immediate
snapshots, that is an engine feature (an on-demand flag checked at C4)
to be specced on its own — named here so it is not lost.

**Alternatives considered.** (a) Forcing a snapshot from the control
thread via `encode(...)` on live state — rejected: reads mutating
closures mid-cycle; exactly the torn state Doc 06 §5b exists to forbid.
(b) Two-phase reply (immediate ack + later notice on a status subject)
— rejected for v1: two delivery paths for one answer; the single
deferred reply plus the `tele.snapshot` notice already covers the
observable need. (c) `stop` as a fourth command — rejected: killing a
run is the operator's process-level affair; a half-stopped engine has
no resumable meaning short of the snapshot path that already exists.

## R6 — The object-store snapshot backend: the store seam over JetStream, sync facade, loud failures

**Decision.** `NatsSnapshotStore` implements the four-method
`SnapshotStore` protocol (store.py:35-39) over a JetStream object-store
bucket (name configurable, default `pra-snapshots`): `write` computes
the id with the existing `snapshot_id_for(metadata)` helper (one id
scheme project-wide), puts the blob as the object and the canonical
metadata JSON in the object's description; `read`/`delete` address by
id; `list` returns newest-first by the metadata timestamp — the
`FileSnapshotStore` contract, matched exactly and asserted by running
the existing store contract tests against the fake-backed
implementation. All operations are synchronous facades over the
transport (R7) with a bounded timeout; any failure raises
`RuntimeError` naming the store, the operation, and the id (FR-005) —
an explicit persistence operation is allowed to fail loudly and is
never allowed to hang or pretend. A store-backed engine run therefore
*does* block at C4 for the duration of the write — the user's explicit
choice of backend, stated in the docs (the no-backpressure rule, R3,
governs telemetry; persistence is an explicit operation by spec).

**Rationale.** The store seam is the whole reason this surface is
cheap: the engine already writes through an injected protocol
(engine.py:578), resume already accepts any store's bytes
(engine.py:131-139), and Doc 06 §5b's per-class guarantees are
properties of the *blob*, which the transport carries unmodified —
byte-identical round-trip is asserted at reference and scaled sizes
(SC-004). This is Phase D's shareable-brains transport bought once:
push on one machine, `list`/`read`/resume on another.

**Alternatives considered.** (a) JetStream KV instead of the object
store — rejected: snapshots at scale are multi-megabyte blobs; the
object store exists for exactly this and chunks internally. (b) Async
store API — rejected: the protocol is sync, the engine calls it
synchronously, and changing the protocol is a core edit (FR-009).
(c) Storing metadata as a separate object — rejected: two-object commit
has torn-write states the file store solved with a marker file; the
description field makes metadata-with-object atomic.

## R7 — The dependency and the threading model: optional extra, lazy import, one asyncio loop on a daemon thread

**Decision.** A new optional extra `nats = ["nats-py>=2.9"]` in
`pyproject.toml`; the core install and the `dev` extra are unchanged, so
the quality gate runs on a machine with no NATS client and no server,
zero tests skipped (FR-007) — the 013 discipline, except this
dependency *is* pip-installable so the extra honestly exists (spec
assumption). All contract logic sits above a small `BusTransport`
protocol (`transport.py`): `start`, `publish(subject, payload)`
(fire-and-forget), `subscribe(subject, handler)`,
`serve_requests(subject, handler)`, `request(subject, payload,
timeout)`, object-store ops (`object_put/get/list/delete`), `healthy`,
counters, `close`. `FakeBusTransport` (`fake.py`, in-repo, stdlib-only)
implements it with subject journals, scriptable requesters, an
in-memory object store, and an up/down switch — every requirement in
the contract suite runs against it (FR-008). `NatsTransport` is the
thin real binding: `_require_nats()` imports lazily and raises a clear
error naming `pip install "poseres[nats]"` (tested by monkeypatching
the import handle, the 007/013 pattern); internally it owns one asyncio
event loop on a daemon thread — publishes hop over via
`call_soon_threadsafe` (non-blocking), store and request operations via
`run_coroutine_threadsafe(...).result(timeout)` (blocking by intent,
R6), subscriptions dispatch handlers on the loop thread into the tap's
thread-safe control state.

**Rationale.** nats-py is asyncio-native; the engine is synchronous and
single-threaded by design (BLAS pinned, process-parallel seeds). One
loop thread per transport is the standard bridge, and it keeps the
asyncio machinery entirely inside `transport.py` — the tap, control
plane, and store logic are all synchronous code tested against the
synchronous fake. `filterwarnings = ["error"]` makes stray
unawaited-coroutine warnings test failures — a reason the gate runs on
the fake and the real binding stays thin.

**Alternatives considered.** (a) nats-py in `dev` so the gate imports
it — rejected: without a server every real-transport test would need
`importorskip`/skip-on-connect, banned by the no-skip rule; an
import-only test proves nothing the lazy-import unit test doesn't.
(b) A synchronous third-party NATS client — none is maintained.
(c) One shared loop for N taps — rejected: taps are per-run objects in
per-process seeds; sharing buys nothing and couples lifetimes.

## R8 — The worked example: one command, two processes, a throwaway server

**Decision.** `examples/nats/` with three files and a README: `brain.py`
(a seeded run — rover-sized config — with the tap attached, a
`NatsSnapshotStore` injected at a short cadence, and `finish()`
publishing the summary), `watch.py` (subscribes to the run's subjects
and prints live telemetry; then demonstrates the control plane —
`inspect`, `pause`, `resume`, `snapshot` with a cadence-sized timeout —
and finally pulls the snapshot back from the object store and verifies
the round-trip byte-identical), and `demo.py` — the one documented
command (US4): it locates a NATS server (a running `nats-server`, else
`docker run --rm -p 4222:4222 nats:latest -js`, else a clear error
naming both options), starts `brain.py` and `watch.py` as separate
processes, and exits nonzero unless the telemetry was consumed, the
control round-trip completed, and the snapshot round-trip verified.
JetStream is enabled (`-js`) for the object store. The example requires
`pip install "poseres[nats]"`; without it, the error is the R7 message,
never a traceback (spec US4 scenario 2).

**Rationale.** The example is the integration proof that the contract
the fake encodes is the contract the real stack honors (FR-011) — the
same burden 013's Gazebo container carried, much cheaper here because
the server is a single static binary. It deliberately exercises all
three surfaces in one sitting so "did B6 land" is one command's exit
code.

**Alternatives considered.** Docker-compose (two processes and a
binary don't need an orchestrator); wiring the example into the gate
(needs a server binary the gate must not require — FR-007; the demo's
exit code is the manual proof, the 007/013 stance); an in-repo embedded
server (nats-server is Go; embedding is not a Python option).

## R9 — Reproducibility classes: what Doc 06 §5b will say, decided now

**Decision.** Doc 06 §5b gains a feature-014 paragraph recording every
NATS-touching mode (FR-010, SC-006):

- **Telemetry out** (tap attached): observer-safe — the run's RNG
  stream, behavior, and serialized summary are byte-identical with the
  backend absent or attached; proven by the same-seed two-run test (the
  B1 viewer discipline, off-process).
- **Pause/resume**: schedule-relative and class-preserving — a
  steppable world's run completes byte-identical after pause/resume; a
  free-running world keeps moving while paused (stated; already class
  4 by 013).
- **Store-backed snapshots**: the transport carries the blob unmodified;
  every per-class §5b guarantee (classes 1–4) applies to a
  JetStream-stored snapshot exactly as to a file-stored one.
- **Experience in over the network**: named class 4 — openly
  non-reproducible — and *out of this feature's scope*; recorded so it
  is stated before anyone builds it, never discovered after.

**Rationale.** The determinism boundary is this feature's constitution-
level claim (spec Overview); writing it into the persistence design doc
is what makes it law rather than a release note, and it is the one
place B7 and the fleet tooling will look.

**Alternatives considered.** Recording only the new observer-safe mode —
rejected: §5b's value is completeness; an unlisted mode is exactly the
"discovered, not stated" failure the spec forbids.
