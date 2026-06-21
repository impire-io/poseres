# Contract: Configuration

The harness MUST expose every PRA-01 §8 parameter as configuration with the stated
default (PRA-01 §11 item 2). Defaults are used when unset. Config is immutable per run.
See `data-model.md` §1 for the full table with types, defaults, and ranges. This contract
fixes the *behavior* of the config layer.

## Requirements

- **Completeness.** Every parameter in PRA-01 §8.1–§8.7 MUST be settable, plus the
  harness-only `horizon_checkpoints` (default `(18, 30, 50)`). A config that omits a
  field uses the spec default.
- **Validation.** Construction MUST reject out-of-range values (e.g. `ema_decay ∉ [0,1)`,
  `max_frames < min_frames`, `initial_dim_max < initial_dim_min`, empty `seeds`,
  `horizon_checkpoints` non-ascending or any entry `< 1`) with a clear error, before any
  run starts.
- **Run length covers checkpoints.** PRA-01 §8's `n_cycles` default is 18, but T4 reads
  `best_dim` at every horizon checkpoint (default last = 50). The harness MUST run each
  suite seed for `effective_n_cycles = max(n_cycles, max(horizon_checkpoints))`, so every
  checkpoint is reached and snapshotted; the default suite therefore runs 50 offline
  cycles, matching the v4 reference. A checkpoint can never exceed the effective run
  length.
- **Hidden-from-system fields.** `true_dim` is configuration of the *world* and is known
  to the harness for scoring T4, but MUST NOT be passed into the system-under-test
  (engine/frames/telemetry) as an input (PRA-01 §1.2 hidden-state requirement).
- **Modes.** `scoring_mode ∈ {predictive, effort_only}` selects predictive (default) vs
  the T3 ablation. The ablation run is constructed by the harness with a derived seed
  (`seed + 9999`) and equal experience (PRA-02 §2) — not by the user toggling a flag
  mid-suite.
- **Override precedence.** CLI flags override file config; file config overrides defaults.
- **Determinism.** The config plus the seed fully determine a run (FR-010). Two runs with
  the same config + seed MUST produce byte-identical summaries (SC-007).
- **Scaled configs.** `true_dim ∈ {20, 35, 50}` with `obs_dim ≥ 3·true_dim` MUST be
  expressible for T-SCALE (PRA-02 §1.3); only dimensions and run length change.

## Load-bearing tunables (expected to be adjusted — tag [D])

These are the parameters the specs flag as the ones most likely to need tuning to pass
T4/T5; they remain spec-faithful defaults but are first-class config:

- `w_complexity` (parsimony; too small over-dimensions, too large collapses toward dim 1).
- `survive_threshold_base`, `survive_threshold_pop_coeff`, `survive_threshold_pop_baseline`
  (the decay block that makes the population self-limit for T5).

Changing the eviction *mechanism* or the scoring *definition* is out of scope; tuning
these *parameters* is in scope (PRA-02 §4 T5 note).
