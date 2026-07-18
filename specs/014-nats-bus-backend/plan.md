# Implementation Plan: The External Bus Backend (NATS at the Seams)

**Branch**: `014-nats-bus-backend` | **Date**: 2026-07-18 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/014-nats-bus-backend/spec.md`

## Summary

Build ROADMAP B6: give a live PRA run an off-process presence over
NATS/JetStream — telemetry out, snapshots through, control in — without
one engine, core, or config edit. One new subpackage, `src/pra/nats/`,
holds the whole feature in transport-separated layers (the 013 pattern):

1. **`subjects.py`** — the versioned subject scheme
   (`pra.v1.run.<run_id>.…`) and the canonical-JSON payload helpers
   (the recorder's serialization discipline, reused).
2. **`tap.py`** — `NatsTap`, binding the three injection seams the
   `Engine` already exposes: a delegating **world wrapper** (per-step
   mirror + the pause gate, research R1/R2), the **`bus_factory`
   capture** (the B1 viewer pattern verbatim — keep the `FrameStore`
   reference, return the stock bus, derive the census on the publisher
   thread), and a delegating **snapshot-store wrapper** (observes the
   engine's C4 writes, publishes snapshot notices, fulfills pending
   control requests). Plus the bounded mirror buffer, the daemon
   publisher thread, and the drop/reconnect counters (R3).
3. **`control.py`** — the request/reply control plane: `inspect`,
   `pause`/`resume` (boundary-exact via the gate), `snapshot` (honest
   deferred fulfillment at the next engine cadence write, R5), error
   replies for everything else.
4. **`store.py`** — `NatsSnapshotStore`, the existing four-method
   `SnapshotStore` protocol over a JetStream object-store bucket; sync,
   loud, byte-exact round-trip; also usable standalone (Phase D's
   shareable-brains transport, R6).
5. **`transport.py` + `fake.py`** — the `BusTransport` protocol;
   `FakeBusTransport` (in-repo, stdlib-only: subject journals,
   scriptable requesters, in-memory object store, an up/down switch)
   carries the entire contract suite; `NatsTransport` is the thin real
   binding — lazy `nats-py` import behind a clear
   `pip install "poseres[nats]"` error, one asyncio loop on a daemon
   thread (R7).

The worked example `examples/nats/` (`demo.py` orchestrating `brain.py`
+ `watch.py` over a throwaway `-js` server) is the integration proof:
telemetry consumed by a separate process, a control round-trip, a
snapshot pushed and pulled back byte-identical (R8). Doc 06 §5b records
the reproducibility class of every NATS-touching mode (R9). The
determinism line is mechanical, not aspirational: the run path gains
one event check, two integer increments, one small copy, and one
bounded-deque append per step — no RNG, no float derivation, no
network — and byte-identity with the tap attached is asserted by test.

## Technical Context

**Language/Version**: Python ≥3.12 (repo `.venv` runs 3.14; 3.12 floor
set by feature 013 — unchanged).
**Primary Dependencies**: numpy (core, unchanged). New optional extra
`nats = ["nats-py>=2.9"]` — never imported by the gate; `dev` extra
unchanged (research R7).
**Storage**: the existing snapshot blob format, unmodified, carried
over a JetStream object-store bucket (metadata in the object
description; ids from the existing `snapshot_id_for`).
**Testing**: pytest — unit (subject scheme + validation, payload
canonicalization, transport-protocol conformance of the fake), contract
(tap mirror ordering and drop derivation, census discipline, control
semantics incl. boundary-exact pause and every error reply, store
backend against the existing store-contract expectations, the
missing-nats-py error via monkeypatch), integration (full engine runs
on the fake transport: byte-identity with tap attached vs absent,
pause/resume byte-identity, snapshot round-trip + resume equivalence vs
`FileSnapshotStore`, multi-stream attribution, continuous mode, RNG
non-perturbation via bit-generator state).
**Project Type**: extends the `pra` package (one new subpackage + tests
+ a two-process worked example).
**Performance Goals**: run-path overhead per step is O(1) plain-Python
work (one `Event.is_set`, one bounded append, one small array copy);
fake-transport integration runs complete in seconds; the publisher
thread drains at 50 ms cadence and the census derives at 500 ms —
telemetry latency is bounded by cadence, never the reverse.
**Constraints**:
- **Byte-frozen reference** (FR-002/FR-009/SC-001): zero edits under
  `core/`, `harness/`, `persistence/`, `config.py`; no new `Config`
  fields (run id, cadences, buffer size are `NatsTap` constructor
  arguments); the existing suite and recorded values stay green
  untouched.
- **Observer safety** (FR-002/SC-002): same-seed runs with and without
  the tap produce byte-identical serialized summaries; the engine
  generator's bit-state is untouched by mount and run (007/013 test
  pattern).
- **No backpressure** (FR-003): the run thread never blocks on
  telemetry — bounded deque, drop-oldest, drops derived from sequence
  gaps; asserted with a full buffer and with the fake transport down.
- **Boundary-exact control** (FR-006/SC-005): pause blocks only at the
  wrapped `step()`/`reset()` entry; paused-then-resumed == never-paused
  by byte-comparison; snapshot-on-request fulfills at the next C4 write
  or errors honestly (no store, no cadence, run completed).
- **Store fidelity** (FR-005/SC-004): blob and canonical metadata
  round-trip byte-identically through the object store; `list` is
  newest-first; resume-from-fetched == resume-from-local, including a
  realistic scaled-size blob.
- **No skipped tests** (FR-007/SC-001): the gate needs no NATS library
  and no server; the real binding's import-error path is monkeypatched;
  `NatsTransport` internals are exercised by the worked example (stated
  openly, the 013 stance).
**Scale/Scope**: telemetry payloads are tens of floats (reference
obs 10, scaled 50); snapshot blobs up to scaled-run size (megabytes —
the object store chunks internally, round-trip asserted); K streams tag
events by construction order with no new mechanism.

## Constitution Check

Constitution file remains the unfilled template; gating against project
rules (AGENTS.md) and the spec:

| Gate | Requirement | Status |
|---|---|---|
| Regression (FR-002/FR-009/SC-001) | validated modes byte-identical; core install numpy-only | PASS — additive leaf subpackage; all attachment through existing injection seams; nothing imports it unless the user does |
| Observer safety (FR-002/SC-002) | tap attached ⇒ byte-identical summary; engine RNG untouched | PASS — delegation-only wrappers, no RNG/float work on the run path (research R1/R2); asserted by same-seed comparison + bit-state test |
| No backpressure (FR-003) | run never waits on the network | PASS — bounded deque, drop-oldest, derived drop counts; publisher thread owns all network I/O (R3) |
| Stable surface (FR-004/SC-006) | documented run-scoped subject scheme B7 can build on | PASS — versioned `pra.v1.` root in `subjects.py`, contract-tested names, inter-brain space reserved unbuilt |
| Store fidelity (FR-005/SC-004) | protocol honored; §5b guarantees unchanged; loud failures | PASS — four-method facade over the object store, existing id scheme, sync + bounded timeout + `RuntimeError` naming store/op/id (R6) |
| Honest control (FR-006/SC-005) | boundary-exact pause; deferred snapshot truthfully scoped; error replies | PASS — gate at the world seam; fulfillment at the engine's own C4 write; every rejection path enumerated in contracts (R5) |
| Optional dependency (FR-007) | gate green with no NATS present, none skipped | PASS — fake transport carries the suite; lazy import + monkeypatched error test; `nats` extra exists, `dev` unchanged (R7) |
| Mirror-only telemetry (FR-012) | no invented measurements; tap counters outside the learning surface | PASS — step mirror = the world seam's own values; census = the viewer's derivation on copies; counters live on the tap object |
| Persistence honesty (FR-010/R9) | every NATS-touching mode's class recorded in Doc 06 §5b | PASS — gated in tasks: §5b paragraph lands with the feature |
| Quality gate | ruff + pytest green, none skipped | PASS — gated in tasks |

## Project Structure

### Documentation (this feature)

```text
specs/014-nats-bus-backend/
├── spec.md, plan.md, research.md, data-model.md, quickstart.md
├── checklists/requirements.md
├── contracts/nats-bus.md        # transport / tap / control / store / regression contracts
└── tasks.md                     # (/speckit-tasks output)
```

This branch runs alone: `JOURNEY.md`, `ROADMAP.md`, and Doc 06 are
edited directly in the closing commits, per AGENTS.md (the 013
precedent; no staged docs-propagation files).

### Source Code (repository root)

```text
src/pra/nats/                  # NEW — the whole feature
├── __init__.py                #   public surface re-exports
├── subjects.py                #   subject scheme v1 + canonical payload helpers (stdlib-only)
├── transport.py               #   BusTransport protocol; NatsTransport (lazy nats-py, asyncio loop on a daemon thread)
├── fake.py                    #   FakeBusTransport — journals, scriptable requesters, in-memory object store, up/down switch
├── tap.py                     #   NatsTap: world wrapper (mirror + pause gate), bus_factory capture, store wrapper,
│                              #     bounded buffer, publisher thread, census, counters, finish()
├── control.py                 #   control plane: inspect / pause / resume / snapshot + error replies
└── store.py                   #   NatsSnapshotStore — SnapshotStore protocol over a JetStream object store

examples/nats/                 # NEW — the worked example (US4)
├── README.md                  #   the one documented command + what you will see
├── brain.py                   #   seeded run with tap + store attached; publishes the summary
├── watch.py                   #   separate consumer: telemetry, control round-trip, snapshot pull + verify
└── demo.py                    #   orchestrates server discovery + both processes; nonzero exit on any failed proof

tests/
├── unit/test_nats_subjects.py        # scheme validation, run-id rules, payload canonicalization
├── contract/test_nats_contract.py    # transport conformance (fake), tap mirror + drop derivation,
│                                     #   census discipline, control semantics + every error reply,
│                                     #   store backend contract, missing-nats-py message
└── integration/test_nats_fake_run.py # full engine runs on FakeBusTransport: byte-identity attached/absent,
                                      #   pause/resume byte-identity, snapshot round-trip + cross-store resume
                                      #   equivalence, multi-stream attribution, continuous mode, rng non-perturbation

pyproject.toml                 # + [project.optional-dependencies] nats = ["nats-py>=2.9"]  (only edit outside new dirs)
design/06-state-persistence.md # §5b paragraph: reproducibility classes of every NATS-touching mode (R9)
```

**Structure Decision**: a subpackage mirroring 013's proven shape,
because the feature has the same three separable layers (pure scheme,
transport-agnostic contract logic, transports) and the fake/real
transport split is again the testability spine (FR-008). The tap,
control plane, and store are synchronous code tested against the
synchronous fake; all asyncio lives inside `NatsTransport`. No changes
to `core/`, `harness/`, `persistence/`, `world/`, or `config.py` at
all; `pyproject.toml` gains one optional-extra line.

## Complexity Tracking

No constitution-gate violations to justify. The accepted, documented
scope cuts are named in the spec's Assumptions with owners: telemetry
history/replay streams are B7's question; immediate (off-cadence)
snapshot-on-request is a future engine feature named in research R5;
inter-brain communication is reserved subject space and research, not
plumbing; server operation (auth, TLS, retention) is the deployment's
affair.
