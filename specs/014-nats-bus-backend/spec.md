# Feature Specification: The External Bus Backend (NATS at the Seams)

**Feature Branch**: `014-nats-bus-backend`
**Created**: 2026-07-18
**Status**: Draft
**Input**: User description: "External bus backend (NATS/JetStream) — ROADMAP
B6. NATS enters at the seams, opt-in, with the reference paths byte-frozen;
the rejected framing (NATS underneath the engine) is out of scope. Three
integration surfaces: (1) bus backend — run telemetry fanned out as NATS
subjects so any external process can tap a live brain without touching the run
path, generalizing the B1 viewer discipline off-process; (2) snapshot
transport — the SnapshotStore seam backed by a JetStream object store, which
is also Phase D's shareable-brains transport bought once; (3) control plane —
request/reply for pause/snapshot/inspect, the management surface B7 and future
fleet tooling sit on. Inter-brain communication is named as the enabled
horizon but excluded from the exit. Determinism boundary drawn in the spec
before code: telemetry out is observer-safe (byte-identity with the backend
attached, the B1 viewer precedent); experience in over a network is a Doc 06
§5b class-4 openly non-reproducible mode, stated up front. Exit criteria:
reference suite byte-identical with the backend absent and attached as
observer; a live run's telemetry consumed from NATS subjects by a separate
process; snapshot round-trip through JetStream verified; reproducibility
classes of every NATS-touching mode recorded in Doc 06 §5b."

## Overview

Every PRA run so far lives and dies inside one process: the brain, its world,
its telemetry, and its snapshots share an address space, and the only window
in was the B1 viewer — same process, proven not to perturb the run. The
distributed-operation chain the roadmap has carried since Phase A (A1 → B4 →
**external bus backend** → multi-machine) names this feature as the next
link: give a live brain an off-process presence, so any external program can
watch it, manage it, and carry its snapshots — without entering the run path.

The framing this feature explicitly rejects (JOURNEY.md ch. 27): NATS
*underneath* the engine. The fast loop is a batched in-process kernel whose
entire validation story is byte-identity; Doc 02 §6's Bus interface remains
delivery-only with its in-memory synchronous backend, and no network hop
enters the observation-evaluation-selection path. What crosses the process
boundary is a **mirror**, never the mechanism: telemetry the run already
produces, snapshots the run already writes, control requests the run already
honors at its own boundaries. NATS attaches at three seams the architecture
drew long ago — the telemetry surface (Doc 02's bus, observed from outside),
the SnapshotStore seam (Doc 06), and a management surface generalizing what
the B1 viewer proved — and each attachment is opt-in, with the reference
paths byte-frozen.

The determinism line is drawn here, before code. Telemetry **out** is
observer-safe: a run with the backend attached is byte-identical to the same
run without it, the B1 viewer discipline now holding across a process
boundary. Observer safety has a stated mechanical consequence — the run never
waits on the network. A slow consumer, a dead server, or no server at all
must cost the run nothing but a counted, visible drop; backpressure into the
run path is forbidden by specification, not by hope. Experience **in** over a
network — remote sensors feeding the brain — is a Doc 06 §5b class-4 openly
non-reproducible mode: named here so it is stated up front rather than
discovered, and excluded from this feature's exit. Inter-brain communication
(broadcast, anycast, unicast between brains) is the horizon this transport
enables; it is research, not plumbing, and stays out of scope.

Everything else follows standing law. The feature is purely additive: no
engine or core edits, every recorded reference value byte-identical, the
NATS client an optional dependency the core install never acquires. The
quality gate must pass on a machine with no NATS library and no NATS server
— the 013 precedent: the contract lives behind a transport seam with an
in-repo fake carrying every test, and the real stack is proven by a worked
example. This is also deliberately the transport bought once: the snapshot
surface B6 builds is Phase D's shareable-brains channel, and the subjects
B6 publishes are the exact surface B7's dashboard consumes — one transport,
built once, consumed twice.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Watch a live brain from another process (Priority: P1)

A maker starts a run with the bus backend enabled and, from a second process
— another terminal, another machine on the LAN — subscribes to the run's
subjects and watches the brain live: step progress, population census,
scores, the same telemetry the run records anyway, fanned out under a
documented subject scheme with the run's own identity as the namespace. The
run itself neither knows nor cares: with the backend enabled or absent, its
recorded summary is byte-identical.

**Why this priority**: This is the feature's core claim — an off-process
window that provably does not touch the run — and the surface B7 is gated
on. Without it the other two seams have no live counterpart.

**Independent Test**: Can be fully tested against the in-repo fake transport:
run a seeded schedule with the publisher attached, assert the messages seen
by the fake (subjects, payloads, ordering), and assert the run summary is
byte-identical to the same run with the backend absent — no NATS library, no
server, no example involved.

**Acceptance Scenarios**:

1. **Given** a seeded run with the bus backend enabled, **When** a separate
   subscriber listens on the documented subjects, **Then** it receives the
   run's telemetry as the run progresses, each message attributable to run,
   stream, and step, under the documented subject scheme.
2. **Given** the same configuration and seed, **When** the run executes once
   with the backend absent and once with it attached, **Then** the two
   serialized run summaries are byte-identical — the observer proof, off
   process.
3. **Given** no consumer, a slow consumer, or no reachable server at all,
   **When** the run executes, **Then** it completes at full stride to a
   byte-identical summary; undeliverable telemetry is dropped, and the drop
   and reconnect counts are readable outside the learning surface.
4. **Given** two runs publishing through one server, **When** a subscriber
   follows one run's namespace, **Then** it receives only that run's
   telemetry — no cross-talk between brains.

---

### User Story 2 - Snapshots through the object store: shareable brains (Priority: P2)

A user snapshots a run into a NATS JetStream object store instead of a local
directory — same snapshot surface, different backend behind the existing
store seam. On another machine, they list the store, fetch the snapshot, and
resume: the resumed run behaves exactly as a resume from a local snapshot of
the same run, under exactly the per-world-class guarantees Doc 06 §5b
already states. A brain is now something you can push to a server and pull
somewhere else — Phase D's shareable-brains transport, bought once.

**Why this priority**: The snapshot store is the second seam the roadmap
names and the one with lasting Phase D value, but it is useful without a
live run attached — hence below the live window, above management.

**Independent Test**: Can be fully tested against the fake transport's
object-store behavior: write a snapshot through the store seam, read it
back, assert blob and metadata round-trip byte-identically, and assert list
and delete semantics match the existing store contract — then resume from
the fetched blob and compare against a resume from the original.

**Acceptance Scenarios**:

1. **Given** a snapshot written through the object-store backend, **When** it
   is read back (same process or another machine), **Then** blob and
   metadata are byte-identical to what was written, and listing shows it
   with the same metadata contract as the existing store backends.
2. **Given** a snapshot fetched from the store, **When** a run resumes from
   it, **Then** the resumed run is indistinguishable from one resumed from a
   local copy of the same snapshot — the §5b class guarantees carry over
   unchanged, none weakened, none silently strengthened.
3. **Given** an unreachable server or a missing snapshot id, **When** a
   store operation runs, **Then** it fails loudly naming the store, the
   operation, and the id — an explicit snapshot operation is allowed to
   fail; it is never allowed to pretend.

---

### User Story 3 - The control plane: pause, snapshot, inspect (Priority: P3)

An operator sends a request to a live run and gets a reply: **inspect**
answers with the run's current status (identity, step position, census
summary — read-only, never a mutation); **pause** takes effect at the next
step boundary and a later resume continues the schedule exactly where it
stopped; **snapshot** writes through the configured store and replies with
the snapshot's identity. Malformed or unknown requests get an error reply
naming the problem — never silence, never a crashed run. This is the
management surface B7's dashboard and any future fleet tooling sit on.

**Why this priority**: Management is only meaningful once the live window
(US1) and the store (US2) exist — a control plane's pause is observable via
telemetry and its snapshot lands in the store. It is P3 by dependency, not
by importance.

**Independent Test**: Can be fully tested against the fake transport:
scripted requests during a seeded run assert boundary-exact pause, exact
continuation after resume (byte-identity of the completed run against an
unpaused run of the same seed for a steppable world), snapshot-on-request
landing through the store seam, read-only inspect, and error replies for
malformed requests.

**Acceptance Scenarios**:

1. **Given** a live seeded run on a steppable world, **When** it is paused,
   later resumed, and runs to completion, **Then** the final summary is
   byte-identical to the same run never paused — pause is schedule-relative,
   not an event the brain can observe.
2. **Given** a pause request mid-step, **When** it arrives, **Then** it
   takes effect at the next step boundary — never inside the fast loop —
   and the reply states the position at which the run halted.
3. **Given** a snapshot request on a run whose world class permits
   snapshotting, **When** it executes, **Then** the snapshot lands through
   the configured store and the reply carries its identity; **Given** a
   world class that cannot promise capture, **Then** the existing §5b
   refusal applies unchanged and the reply says so loudly.
4. **Given** an unknown command or malformed request, **When** it arrives,
   **Then** the requester receives an error reply naming the problem and
   the run continues unperturbed.

---

### User Story 4 - The worked example: two processes, one real server (Priority: P4)

A user with the optional NATS extra installed runs one documented command: a
local NATS server comes up, a seeded run starts publishing, and a separate
consumer process prints the live telemetry, round-trips a control request
(inspect, pause, resume), pushes a snapshot into the JetStream object store,
and pulls it back — the integration proof that the contract the fake
transport encodes is the contract the real stack honors.

**Why this priority**: Pure composition of US1–US3 — nothing in it can work
before they do — and the only story that touches a real server, so it lives
as a worked example rather than inside the default quality gate.

**Independent Test**: Run the documented command on a machine with the NATS
extra and a NATS server available; the example exits successfully having
printed consumed telemetry, the control round-trip, and the verified
snapshot round-trip.

**Acceptance Scenarios**:

1. **Given** a machine with the optional extra and a server, **When** the
   user runs the documented example command, **Then** a live run's telemetry
   is consumed by a separate process, a control round-trip completes, and a
   snapshot pushed through the object store is pulled back byte-identical.
2. **Given** an installation without the NATS extra, **When** any NATS
   backend is requested, **Then** the failure is a clear error naming the
   optional extra to install — never a bare import traceback.

---

### Edge Cases

- The server dies mid-run (or was never reachable): the run continues
  untouched — telemetry drops are counted and visible, reconnection is
  attempted quietly, and only *explicit* operations (a snapshot write, a
  control reply) may fail loudly, each naming the operation. The backend
  never converts a network failure into a run failure.
- A consumer cannot keep up: undelivered telemetry is dropped at the
  publisher side, never buffered without bound and never allowed to slow the
  run; the drop count is the honesty meter, readable outside the learning
  surface.
- Pause on a free-running world (the ROS2 adapter's real-time mode): the
  schedule halts but the world keeps moving — sensors will have moved on
  when the run resumes. Stated in the documentation; such runs are already
  §5b class 4, and pause does not change their class.
- A control request races a run's natural end: the reply states the run has
  completed rather than pretending to act.
- Two runs share one server: namespaces derived from run identity keep
  telemetry, control, and snapshots separate; a subscriber must be able to
  discover which runs are present without guessing subjects.
- A snapshot blob at realistic size (a mature scaled brain) crosses the
  object store: round-trips byte-identically — the size boundary is
  measured by test, not assumed.
- The object store holds snapshots from an older format version: the
  existing snapshot format/compatibility rules (Doc 06) apply unchanged;
  the transport adds no new versioning semantics of its own.
- Telemetry payloads must not leak learning-surface internals beyond what
  the recorder already exposes: the tap mirrors recorded telemetry; it
  invents no new measurements and perturbs no state to measure better.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST provide an opt-in bus backend that publishes a
  live run's telemetry to NATS subjects without entering the run path: the
  fast loop, the Doc 02 delivery bus, and the learning surface remain
  in-process and unmodified. Nothing activates unless the user opts in.
- **FR-002**: Observer safety MUST be proven by byte-identity: the full
  reference suite passes byte-identically with the backend absent, and a
  seeded run with the backend attached produces a summary byte-identical to
  the same run without it.
- **FR-003**: The run MUST never wait on the network: no telemetry path may
  block, buffer unboundedly, or slow the run under a slow consumer, a dead
  server, or no server. Undeliverable telemetry is dropped; drop and
  reconnect counts are readable outside the learning surface.
- **FR-004**: Subjects MUST follow a documented, stable scheme namespaced by
  run identity: two runs on one server cannot cross-talk, a consumer can
  discover live runs, and the scheme is sufficient for B7 to build against
  without reading this feature's source. The scheme MUST NOT foreclose the
  named horizon (inter-brain broadcast/anycast/unicast) and MUST NOT
  implement it.
- **FR-005**: The system MUST provide a snapshot store backend over a
  JetStream object store implementing the existing store seam (write, read,
  list, delete, with the existing metadata contract): blobs and metadata
  round-trip byte-identically, resume from a fetched snapshot is
  indistinguishable from resume from a local copy, and every Doc 06 §5b
  per-class guarantee carries over unchanged. Store failures (unreachable
  server, missing id) fail their operation loudly, naming store, operation,
  and id.
- **FR-006**: The system MUST provide a request/reply control plane with
  exactly three v1 commands — inspect (read-only status), pause/resume
  (effective only at step boundaries; schedule-relative, so a
  paused-and-resumed seeded run on a steppable world completes
  byte-identical to an unpaused one), and snapshot-on-request (through the
  configured store, honoring existing §5b refusals) — plus error replies
  naming the problem for malformed or unknown requests. No control path may
  interrupt the fast loop mid-step.
- **FR-007**: The NATS client MUST be an optional dependency: the core
  install is unchanged, the quality gate passes on a machine with no NATS
  library and no NATS server, zero tests skipped, and requesting any NATS
  backend without the extra fails with a clear error naming the extra.
- **FR-008**: The backend's contract logic MUST sit behind a transport seam
  with an in-repo fake implementing it, so that every requirement above —
  publishing, subject scheme, drop policy, store round-trip and failure
  paths, control semantics including boundary-exact pause, and every
  rejection path — is exercised by the in-repo suite against the fake. The
  real NATS binding is a thin adapter over the same seam, proven by the
  worked example.
- **FR-009**: The feature MUST be purely additive: no engine or core edits,
  every existing test and recorded reference value byte-identical, all
  attachment through existing seams (the telemetry surface, the store seam,
  the run loop's existing boundaries).
- **FR-010**: The reproducibility class of every NATS-touching mode MUST be
  recorded in Doc 06 §5b before release: telemetry out is observer-safe;
  store-backed snapshots inherit their world's class unchanged; pause is
  schedule-relative (class-preserving, with the free-running caveat
  stated); and experience in over a network is named as class 4 — openly
  non-reproducible, out of this feature's scope, stated up front.
- **FR-011**: The repository MUST ship a worked example launched by one
  documented command: a real NATS server, a live publishing run, and a
  separate consumer that prints telemetry, completes a control round-trip,
  and verifies a snapshot round-trip through the object store.
- **FR-012**: The backend's own telemetry (drop counts, reconnects, publish
  failures) MUST stay outside the learning surface everywhere, and the tap
  MUST mirror only what the run already records — it invents no new
  measurements and never perturbs state to observe it.

### Key Entities

- **Telemetry tap**: the opt-in publisher mirroring a run's recorded
  telemetry onto subjects; fire-and-forget with visible drop counts; the
  B1 viewer discipline generalized off-process.
- **Subject scheme**: the documented, run-identity-namespaced naming of
  telemetry, control, and discovery subjects — the stable surface B7
  consumes.
- **Object-store snapshot backend**: the existing store seam implemented
  over a JetStream object store; Phase D's shareable-brains transport.
- **Control plane**: request/reply management — inspect, pause/resume at
  step boundaries, snapshot-on-request — with loud error replies.
- **Transport seam**: the boundary between backend contract and message
  delivery; implemented by the real NATS stack in deployment and by the
  in-repo fake in the test suite — the same contract, provably.
- **Worked example**: the two-process run over a real server — the
  integration proof.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: The full existing validation suite passes with its recorded
  reference values byte-identical after the feature ships, on a machine
  with no NATS library and no NATS server, zero tests skipped, and the
  core install unchanged.
- **SC-002**: A seeded run with the bus backend attached produces a
  serialized summary byte-identical to the same run with the backend
  absent — including runs where no consumer and no reachable server exist.
- **SC-003**: A live run's telemetry is consumed from NATS subjects by a
  separate process (worked example), each message attributable to run,
  stream, and step under the documented scheme, with two concurrent runs
  cleanly separated.
- **SC-004**: A snapshot pushed through the object store and pulled back is
  byte-identical, at reference and realistic scaled sizes, and a resume
  from the fetched snapshot matches a resume from a local copy under the
  unchanged §5b class guarantees.
- **SC-005**: A paused-and-resumed seeded run on a steppable world
  completes byte-identical to the same run never paused; inspect answers
  read-only during a live run; snapshot-on-request lands through the
  configured store; malformed requests receive error replies while the run
  continues.
- **SC-006**: Doc 06 §5b records the reproducibility class of every
  NATS-touching mode before release, and B7 can be specified against the
  documented subject scheme and control commands without reading this
  feature's source.

## Assumptions

- **The server is the deployment's affair.** PRA connects to a NATS server;
  it does not manage one. Authentication, TLS, retention, and server
  hardening are the operator's configuration, documented as such; the
  worked example scripts a throwaway local server for the demonstration.
- **The tap mirrors the recorder.** v1 telemetry payloads are the run's
  existing recorded telemetry in a canonical serialized form, at the
  cadence the run already records. New measurement kinds are B7's question
  to raise, not this transport's to invent.
- **Live tap, not history.** v1 telemetry subjects are fire-and-forget:
  a consumer sees the run from the moment it subscribes. Whether telemetry
  also lands in a replayable stream for dashboard history is deferred to
  B7's stated needs; durability in v1 is bought only where it is the
  point — the snapshot object store.
- **Pause is schedule-relative.** Pausing halts the schedule between steps
  and resumes it exactly there; it is not wall-clock control. On
  free-running worlds the world keeps moving while paused — stated, and
  already §5b class 4.
- **Control is uncommanded by default.** v1 ships exactly inspect,
  pause/resume, and snapshot; richer fleet management (reconfiguration,
  migration, multi-brain orchestration) waits for the tooling that needs
  it.
- **Inter-brain communication stays research.** Broadcast/anycast/unicast
  between brains is the horizon this transport enables; nothing in v1
  implements or forecloses it.
- **The client library installs from the package index** as an optional
  extra (unlike 013's ROS2 stack there is no distribution barrier), but
  the quality gate still never requires it — the seam-and-fake pattern
  carries the contract, and the worked example carries the integration
  proof.
