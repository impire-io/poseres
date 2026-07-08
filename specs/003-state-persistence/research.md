# Phase 0 Research: State Persistence

Load-bearing decisions. Governing sources: design Doc 06 (normative), the
validated engine/frame internals (what state actually exists), and feature
001/002's byte-identity discipline.

---

## R1 — Opt-in hook; the baseline stays byte-frozen and file-free

**Decision.** One new config field, `snapshot_every_n_cycles` (default **0** =
off). The engine takes a snapshot only when a store is injected **and** the
cadence fires, at the **end of an offline cycle** — a pure `if` with no RNG and
no float work on the hot path. No harness command changes; validation modes
never construct a store.

**Rationale.** FR-009/SC-003 and feature 001's FR-011 (only report summaries on
disk) must keep holding. A guarded hook cannot perturb the validated RNG stream
or summary bytes; re-verified against the recorded reference values.

**Alternatives.** A wrapper process that snapshots externally (rejected: cannot
see internal state without exactly this API); always-on snapshots (rejected:
violates FR-011 for validation runs).

## R2 — The state inventory that makes continuation byte-identical

**Decision.** The blob captures: (1) config (all fields); (2) frame population
as the FrameStore's per-dim arrays — `frame_ids`, `is_candidate`, `age_cycles`,
three EMAs, and all 12 weight tensors per group — plus `next_id`; (3) run
counters and **all summary accumulators** (`map_fractions`, `pred_errors`,
loss/step counters, `pop_sum`, `warmed`, cycles completed, checkpoint readings
so far, `population_by_cycle`); (4) agency state when present (error-history
FIFO, observation-memory FIFO, value/LP/novelty accumulators, directed/total
counts); (5) the generator's `bit_generator.state`; (6) seed and scoring/policy
modes; (7) a reserved-empty `tool_registry` field.

**Rationale.** Doc 06 §2's MUST: "if a component holds state that affects
future behavior, that state is in the snapshot." The summary accumulators and
RNG state are exactly what upgrade "valid continuation" (§1) to the testable
byte-identical form (FR-003). The **world is excluded** (environment, §2): sound
because snapshots occur at cycle boundaries, which fall between episodes — the
next act in *both* the resumed and the uninterrupted run is a fresh
`world.reset()` consuming the same RNG draw.

**Alternatives.** Snapshot world latents too (rejected: leaks hidden state into
system artifacts, and unnecessary per the boundary argument); omit telemetry
accumulators (rejected: the final summary would differ — dishonest
"continuation").

## R3 — Blob format: versioned npz, no pickle; atomicity by rename

**Decision.** The blob is a `numpy.savez_compressed` archive: every array under
a stable key (`g{dim}__W1`, …), plus one `meta` entry holding a JSON string
(format version **first-checked**, config, counters, FIFO contents, RNG state).
Load uses `allow_pickle=False`. `FileSnapshotStore.write` writes to
`<id>.npz.tmp` then `os.replace` (atomic on POSIX); `read`/`list` recognize only
committed `*.npz` files. `snapshot_id = "snap-{step:012d}-{cycle:05d}"`;
metadata (timestamp, step, cycle, population, version) lives in a sidecar-free
JSON entry inside the blob and duplicated in an in-store index file? — **No**:
metadata is returned by parsing the blob's `meta` entry on `list()` (small
archives; simplicity beats an index that can desynchronize).

**Rationale.** FR-004/005/006. npz is the one dependency-free container that
holds arrays losslessly; JSON carries the rest; pickle is rejected (unsafe,
version-fragile). Rename-commit is the standard atomicity idiom. Blob *bytes*
need not be reproducible (zip timestamps) — the invariant lives in the
continuation summaries (spec Assumptions).

**Alternatives.** One JSON file with base64 arrays (rejected: 33% bloat, slow);
separate metadata files (rejected: two artifacts can disagree).

## R4 — Resume rebuilds the world from the seed prefix, then overwrites RNG state

**Decision.** `Engine.run(seed, resume_from=state)`: construct the world with a
fresh `default_rng(seed)` exactly as normal (consuming the construction draws),
then **set the generator's state to the snapshot's** — the world's fixed
structure (objects, emissions, actions) is reproduced from the seed prefix
while the stream continues from the snapshot point. Then load the FrameStore
arrays, counters, accumulators, and agency FIFOs; skip warmup and the
already-completed cycles; run the remainder.

**Rationale.** The world is environment and must not be serialized (R2), but
its *structure* is a pure function of the seed prefix — reconstruction plus
state-overwrite yields the identical generator stream the uninterrupted run
sees at that boundary. Warmup/early-error stats are already inside the restored
accumulators.

**Alternatives.** Serializing the world (rejected, R2); re-deriving RNG by
replaying all draws (rejected: O(run) cost and fragile).

## R5 — Store seam with an in-memory substitute

**Decision.** `SnapshotStore` protocol: `write(blob, metadata) → id`,
`read(id) → blob`, `list() → [(id, metadata)]` newest-first (by step, then id),
`delete(id)`. Default `FileSnapshotStore(directory)`; `InMemorySnapshotStore`
ships as the contract-test substitute (and is useful for tests/embedding).
Event-log and pose-index remain named, unbuilt seams (Doc 06 §4.2).

**Rationale.** FR-006/007; the contract test proves substitutability the same
way the 001 seams do.

## R6 — Compatibility validation before any state is applied

**Decision.** Restore first checks format version, then body compatibility:
snapshot config's `obs_dim` and `n_actions` must equal the booting config's;
mismatch raises a `SnapshotCompatibilityError` naming field, snapshot value,
and boot value. Other config fields are *taken from the snapshot* (the
configuration in force is part of state, Doc 06 §2).

**Rationale.** FR-008 / Doc 06 §5. Body fields are the anatomy contract; the
rest of config travels with the learned state it produced.

## Resolved unknowns

| Unknown | Resolution |
|---|---|
| How to add persistence without touching validated bytes | R1: opt-in guarded hook at the cycle boundary |
| What "complete state" is in this codebase | R2: frames + counters + accumulators + agency FIFOs + RNG + config |
| Blob format without new deps or pickle | R3: versioned npz + JSON meta entry, atomic rename |
| How resume gets a correct world without serializing it | R4: rebuild from seed prefix, overwrite RNG state |
| Store seam shape | R5: write/read/list/delete + in-memory substitute |
| What restore validates | R6: version first, then body fields; rest of config from snapshot |
