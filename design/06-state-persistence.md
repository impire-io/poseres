# 06 — State and Persistence

This document specifies what constitutes the system's state, how it is snapshotted and restored, and the storage layer. Persistence is a core requirement: the system learns continuously, and its accumulated state must survive restarts and failures.

> **Build status (2026-07-08, feature `003-state-persistence`):** implemented and
> validated. The full Section-2 state (frame population, drive bookkeeping,
> counters and summary accumulators, RNG state, config in force; tool registry
> reserved-empty) serializes to a versioned, pickle-free blob through an atomic
> `SnapshotStore` seam (filesystem default + in-memory substitute). The build
> exceeds §1's bar: a run resumed from a cycle-boundary snapshot is
> **byte-identical** to the uninterrupted run, in both random and curiosity
> policy modes — test-locked. Restore validates format version and body
> compatibility (§3.4/§5). Persistence is opt-in (`snapshot_every_n_cycles=0`
> default); every validated mode stays byte-frozen and file-free. The event-log
> and pose-index seams (§4.2) remain defined, not built.

---

## 1. Principles

- The system's entire learned state **MUST** be serializable to a durable **snapshot** and restorable from it. **[D]**
- A snapshot is taken on a **consistent, point-in-time state** — only during the slow loop or at a clean stop, never mid-fast-loop-step (cross-cutting requirement C4). **[D]**
- Restoring a snapshot yields a **valid continuation** of the system from that point. It is **not** required to reproduce a bit-identical future (continuous operation may be stochastic); it is required that the restored system is in exactly the state captured. **[D]**

---

## 2. What constitutes system state

The complete state is the union of the following. A snapshot **MUST** capture all of it; restore **MUST** reconstruct all of it.

| Part | Contents | Source doc |
|---|---|---|
| **Configuration** | Anatomy declaration (sensors, actuators, order), drive declaration and parameters, all Doc 07 parameters in force | 02, 05, 07 |
| **Frame population** | For every frame: `frame_id`, `dim`, `is_candidate`, `age_cycles`, the three EMAs, and all weights (encoder, decoder, transition) | 03 |
| **Drive state** | The drive bookkeeping: recent/baseline prediction-error windows, `recent_observation_memory` | 05 §3.3 |
| **Policy state** | Any learned policy parameters and `exploration_epsilon` state, if the configured policy holds state | 05 §4 |
| **Counters** | Global step counter, slow-loop `cycle` counter, the next `frame_id` to assign | 01, 04 |
| **Tool registry** | The active set of registered tools beyond base anatomy | 02 §5 |

**MUST:** no part of learned state lives only in transient memory that a snapshot omits. If a component holds state that affects future behavior, that state is in the snapshot.

---

## 3. Snapshot and restore

### 3.1 Interface — **[D]**
```
SnapshotStore:
  write(snapshot_blob, metadata) -> snapshot_id      # persist a snapshot durably
  read(snapshot_id) -> snapshot_blob                 # retrieve a snapshot
  list() -> [ {snapshot_id, metadata} ]              # enumerate snapshots, newest first
  delete(snapshot_id)
```
`metadata` **MUST** include at least: timestamp, step counter, cycle counter, population size, and a format version.

### 3.2 Snapshot operation — **[D]**
- Triggered during the slow loop (Doc 04 §6 step 5) at a configured cadence (`snapshot_every_n_cycles`, Doc 07), and on clean stop.
- Serializes all of Section 2 into one blob and writes it via `SnapshotStore.write`.
- **MUST** be atomic from the reader's perspective: a partially written snapshot is never returned by `read`. (Write to a temporary location, then commit.)

### 3.3 Restore operation — **[D]**
- On boot in restore mode (Doc 01 §4.1), read the specified snapshot (or newest), deserialize all of Section 2, reconstruct the frame population (registering every frame on the bus), the drive state, the policy state, the counters, and the tool registry.
- After restore, the system resumes the fast loop. The first event after restore has `previous_observation = null` and `action = null` (a fresh sensing start), since the in-flight step was not part of the consistent snapshot.

### 3.4 Format versioning — **[D]**
The snapshot blob **MUST** carry a format version. `read`/restore **MUST** reject a version it does not support with a clear error rather than silently misinterpreting it.

---

## 4. The storage backend

### 4.1 Built now — **[D]**
A single durable `SnapshotStore` backend (e.g. local filesystem) implementing Section 3.1. It stores opaque blobs; it does **not** interpret frame contents. This is the only storage built for the base system.

### 4.2 Optional seams (interfaces noted; do not implement now)
- **Event log — [D] seam.** An append-only log of sensorimotor events, for replay or audit. Built only if replay is required. It is a *log of messages*, distinct from the snapshot store (a *state* store); it does not replace snapshots.
- **Pose index — [O] seam.** A nearest-neighbour index over frame poses ("have I been near this pose"), e.g. a vector database. Built only if a frame is shown to need fast pose lookup. It is a *query index over frame state*, distinct from both the snapshot store and the event log. Frame state access **MUST** go through a small internal accessor (not scattered field reads) so this can be introduced later without rework.

These three are **separate concerns** and **MUST NOT** be collapsed into one: a state snapshot, a message log, and a query index answer different questions. Only the snapshot store is built now.

---

## 5. Consistency requirements

- **C4 (restated).** A snapshot is taken only when no fast-loop step is partway through. The slow loop is the safe point; a clean stop is a safe point.
- A frame resize or tool registration (Docs 02, 03) changes the state shape; it occurs during the slow loop *before* the cycle's snapshot, so the snapshot always reflects the post-change shape with a consistent format version.
- Restore **MUST** validate that the configuration in the snapshot is compatible with the anatomy the system is booting with (same sensor/actuator order and widths). On mismatch, restore **MUST** fail with a clear error rather than load an inconsistent body.

---

## 5b. What snapshots guarantee, per world class (feature 010, ROADMAP B5)

The brain's state always snapshots exactly. The *world's* continuity
depends on what the world can promise — stated here per class, including
what is **not** guaranteed:

1. **Seed-derivable worlds** (the reference family, the ladder worlds, the
   rover): exact byte-identical resume in both episode modes. Episodic
   runs re-derive the world from the seeded stream; continuous runs carry
   the world's mutable state via the capture protocol
   (`state_dict`/`load_state_dict`, feature 008).
2. **Capture-supporting worlds** (anything implementing the protocol,
   including grown bodies — the anatomy's *current* dimensions are
   recorded and verified at resume; the resuming factory supplies the
   grown parts, since tools are code and code comes from the caller):
   exact resume; continuous mode requires the protocol.
3. **Capture-required worlds** (the Gymnasium adapter: its reset counter
   is history, not seed): they declare `snapshot_needs_state`, their
   state travels in every snapshot, and resume is exact — **conditional
   on the environment's own `reset(seed)` determinism**, which is the
   environment's promise, not ours. Declaring the marker without
   providing capture fails loudly at run start.
4. **Non-capturable worlds** (live services, hardware): **no snapshot
   guarantee.** Persistence for such deployments means the brain's state;
   the world re-attaches at boot (the feature-008 single-boot contract).
   Nothing is written that would silently diverge on resume.

Multi-stream runs snapshot all stream positions (per-stream generators,
world state where the class requires it, carried observations, and the
merge position) and resume exactly under the same per-class rules.

One recorded repair (feature 010): group *insertion order* now travels in
the blob — restoring frame groups in sorted rather than lived order
changed float-accumulation order and made resumed runs drift by one ULP.
Old blobs decode unchanged; their lived order was lost at write time.

---

## 6. Definition of done (this document)
1. The full state of Section 2 is serializable and restorable; no behavior-affecting state is omitted.
2. Snapshots are taken only at consistent points (slow loop, clean stop), are atomic, and carry a format version.
3. Restore reconstructs the population (re-registering frames on the bus), drive state, policy state, counters, and tool registry, then resumes the fast loop.
4. A single durable snapshot-store backend exists; the event-log and pose-index seams are defined but not implemented.
5. Restore validates body/configuration compatibility and rejects mismatches.
