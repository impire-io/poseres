# Contracts: Multi-Stream Experience

Binding promises of feature 009; every MUST has a test.

## 1. Mode contract

- `n_streams=1` (default): behavior, RNG stream, and serialized summaries
  byte-identical to the validated build (SC-002; frozen-baseline suite +
  explicit K=1 equivalence test).
- `n_streams=K>1`: K worlds of identical hidden structure (one
  construction per run seed), K per-stream generators derived from the
  run seed by spawn keys, one shared brain generator, merged by the fixed
  episode round-robin (`episode e → stream e mod K`) (FR-001/002).
- Validation rejects `n_streams < 1`, and `n_streams > 1` with snapshots
  enabled (loud, names B5) (FR-008/009).

## 2. Regime contract

- Transition chains and scoring windows are episode-local, hence
  stream-local; no mechanism reads across streams (FR-003).
- Consolidation and warmup count **merged** episodes: equal-schedule runs
  have identical total experience and identical consolidation positions
  for every K (FR-005, SC-003).
- Brain-side draws (births, proposals, decay, init) come from the shared
  brain generator in merge order; stream-side draws (world noise, policy
  exploration) from the acting stream's generator (FR-004).

## 3. Determinism contract

- Byte-identical summaries per (config, seed) for every K, re-run and
  worker-parallel (FR-002, SC-001).
- Continuous mode composes: each stream boots exactly once and carries
  its own trailing observation; deterministic in both modes (SC-005).

## 4. Measurement contract

- The exit reading is pre-registered (research R5) and recorded with
  per-seed spreads: K ∈ {1, 2, 4}, equal total experience, paired
  margins, T7-style noninferiority bar — whichever way it lands (FR-007,
  SC-004). The continuous-rover reading is investigatory (no bar).
