# Implementation Plan: State Persistence

**Branch**: `003-state-persistence` | **Date**: 2026-07-08 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/003-state-persistence/spec.md`

## Summary

Implement design Doc 06's snapshot/restore for the current build: capture the
**complete behavior-affecting state** of a run — configuration, the batched
frame population (all FrameGroup tensors + identity records + next frame id),
drive/agency bookkeeping when present, run counters and summary accumulators,
and the seeded generator's state — into one versioned blob, stored through an
atomic `SnapshotStore` seam (filesystem default, substitutable). Snapshots are
taken only at consolidation-cycle boundaries (the C4 safe point); restore
rebuilds the state into a fresh Engine which **resumes the run byte-identically
to the uninterrupted execution** — the load-bearing invariant, testable with
the determinism machinery the project already trusts. Persistence is opt-in
(`snapshot_every_n_cycles=0` default): every validated mode stays byte-frozen
and file-free (FR-009, feature-001 FR-011 preserved).

## Technical Context

**Language/Version**: Python 3.14 (repo `.venv`)
**Primary Dependencies**: numpy ≥ 2.4 only (blob = `.npz` archive: arrays + one JSON metadata entry; no pickle — `allow_pickle=False` on load)
**Storage**: Local filesystem `FileSnapshotStore` (atomic via write-to-temp + rename); blobs opaque to the store; **only when explicitly configured** — default writes nothing
**Testing**: pytest — unit (round-trip fidelity, versioning, store semantics), contract (store substitutability), integration (byte-identical continuation in both policy modes, baseline unchanged, compatibility rejection)
**Target Platform**: Single machine, macOS/Linux
**Project Type**: Single Python project — extends the `pra` package (`persistence/` subpackage + an Engine resume/snapshot hook)
**Performance Goals**: Snapshot cost is O(population weights) ≈ a few MB compressed at reference scale; taken at slow-loop cadence, negligible vs a cycle's compute
**Constraints**:
- **Byte-identical continuation** (FR-003, SC-001): resume(cycle k) + remaining cycles ≡ uninterrupted run — requires capturing RNG state, all telemetry accumulators the summary reads, and drive FIFOs; the world is *not* captured (environment), which is sound because cycle boundaries fall between episodes and the next act either way is a fresh `world.reset()`.
- **Baseline frozen** (FR-009, SC-003): the snapshot hook in the engine is a no-RNG, no-float `if` guarded by config; reference values re-verified.
- **C4** (FR-002): the only snapshot trigger is the end of an offline cycle (or an explicit capture between runs/episodes).
- **No silent misread** (FR-005): format version checked before any array is touched.
**Scale/Scope**: Reference-scale validation; blobs scale linearly with population × weight sizes (the batched layout serializes directly as arrays)

## Constitution Check

Constitution remains the unfilled template; gating against project specs and
user global instructions:

| Gate (source) | Requirement | Status |
|---|---|---|
| Regression gate (FR-009) | Validated modes byte-identical, zero files by default | PASS — opt-in config, guarded hook, reference re-verified (research R1) |
| Continuation honesty (FR-003) | Byte-identical resume, not "approximately restored" | PASS — full state inventory incl. RNG + accumulators (research R2) |
| C4 consistency (FR-002) | Snapshot only at slow-loop boundary / clean stop | PASS — hook placed at end of offline cycle only |
| Atomicity + versioning (FR-004/005) | temp+rename; version checked first | PASS — research R3 |
| Seam isolation (FR-006/007) | Store substitutable; blobs opaque | PASS — protocol + in-memory substitute in contract test |
| No new deps / no pickle | numpy-only serialization | PASS — npz + JSON entry, `allow_pickle=False` |
| Quality gate (CLAUDE.md) | ruff + pytest green, none skipped | PASS — gated in tasks |

## Project Structure

### Documentation (this feature)

```text
specs/003-state-persistence/
├── plan.md, research.md, data-model.md, quickstart.md
├── contracts/
│   ├── seams.md         # SnapshotStore seam + Engine snapshot/resume surface
│   └── config.md        # snapshot_every_n_cycles + blob format contract
└── tasks.md
```

### Source Code (repository root)

```text
src/pra/
├── config.py                # + snapshot_every_n_cycles (default 0 = off)
├── persistence/
│   ├── __init__.py
│   ├── snapshot.py          # SystemState capture/apply + blob encode/decode (versioned npz)
│   └── store.py             # SnapshotStore protocol; FileSnapshotStore (atomic); InMemorySnapshotStore
└── core/
    ├── frame.py             # FrameStore.state_dict()/load_state_dict()
    └── engine.py            # snapshot hook (cycle cadence) + run(resume_from=...)

tests/
├── contract/test_snapshot_store_contract.py
├── integration/test_snapshot_resume.py      # byte-identical continuation (both modes) + compat rejection
└── unit/test_snapshot_blob.py               # round-trip fidelity, versioning, store semantics
```

**Structure Decision**: `persistence/` is its own subpackage mirroring Doc 01's
component map. The Engine grows exactly two optional surfaces: a store+cadence
for taking snapshots and a `resume_from` for continuing; nothing else changes.

## Complexity Tracking

> No violations. One scope note: Doc 06's event-log and pose-index seams are
> documented interfaces only (contracts/seams.md names them); implementing them
> now was rejected — Doc 06 §4.2 explicitly defers both until a demonstrated
> need, and collapsing them into the snapshot store is prohibited.
