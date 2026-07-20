# Phase 1 Data Model: Brain Seeding

Entities are the experiment's nouns — worlds, arms, readings, and the config
dials that select them. No persistent store; all state is either a brain blob
(existing snapshot codec) or an in-memory result aggregated into the report and
trail.

## Config dials (new, opt-in; `pra.config.Config`)

| Field | Type | Default | Meaning / validation |
|---|---|---|---|
| `rover_layout_seed` | `int \| None` | `None` | When set, the rover draws its layout from this seed instead of the engine rng (FR-001). `None` = today's behavior, byte-identical. |
| `rover_permute` | `bool` | `False` | When true, the rover applies a construction-time permutation of actions/sensors (FR-002). |
| `rover_permute_seed` | `int \| None` | `None` | Seed for the permutation draw; ignored when `rover_permute` is false. Identity permutation ⇒ byte-identical to plain rover. |

**Validation / invariants**: defaults reproduce today's rover byte-for-byte
(degenerate-dial contract). Draw order at construction is fixed and documented:
layout (obstacles: center then radius, per obstacle; then spawns) → permutation
(actions then sensors). No randomness is consumed at a hop or resize boundary
beyond the documented resize draws.

## Rover map

- **Represents**: one obstacle+spawn layout of the rover world (one body, one
  physics).
- **Fields**: `layout_seed` (identity of the map), derived obstacles/spawns.
- **Relationships**: maps A/B/C for experiment seed *s* are
  `layout_seed = H(s, "A"|"B"|"C")` — distinct layouts, shared body/anatomy.

## Permuted rover

- **Represents**: the rover with a fixed action/sensor permutation — learnable but
  unrelated; the maturity control's world.
- **Fields**: `permute_seed`, action-permutation vector, sensor-permutation vector.
- **State**: permutation drawn once at construction, then static (no per-step RNG
  beyond the plain rover's).

## Arm

- **Represents**: one of the three brains under comparison on a probe map.
- **Enum**: `seeded` | `fresh` | `maturity`.
- **Provenance**:
  - `seeded` — resume from the map-A snapshot (hop 1); the A→B chain resumed across
    +1-sensor resize (hop 2).
  - `fresh` — blank brain booted with the run seed.
  - `maturity` — resume from the permuted-world snapshot (identical `N_pretrain`).

## Time-to-competence reading (`τ`)

- **Represents**: how much experience an arm needed to reach the competence line on
  one probe map, one seed.
- **Fields**: `arm`, `seed`, `map` (`B`|`C`), `theta`, `tau` (checkpoint index or
  the censoring floor), `reached` (bool), `final_error` (context).
- **Derivation**: first checkpoint where the `W_smooth`-smoothed prediction error
  ≤ θ; if none within `N_probe`, `reached = false` and `tau = N_probe` (R7).

## Margin

- **Represents**: a paired per-seed comparison of two arms' τ on one map.
- **Named margins**: `margin1 = τ_fresh(B) − τ_seeded(B)`; `marginM = τ_maturity(B)
  − τ_seeded(B)`; `margin2 = τ_fresh(C) − τ_seeded(C)`; `delta = margin2 −
  margin1`. Positive = seeded faster.
- **Aggregate**: mean, SD, SE, `±1.9·SE` bound, sign-count (n>0 / n), per-arm
  reach-rates.

## Bar / verdict

- **Represents**: the pre-registered decision on a hypothesis.
- **Bars**: `B1` (margin1 superiority), `B2` (marginM superiority), `C1` (margin2
  superiority AND delta non-shrink). Overall "seeding holds" = `B1 ∧ B2 ∧ C1`.
- **Fields**: `bar`, `measured` (mean ± SD, SE, bound), `verdict`
  (`PASS`|`FAIL`), `note` (sign-count, reach-rates).

## Frozen calibration table (from the pilot; lives in `SEEDING-DIAGNOSIS.md`)

`N_pretrain`, `N_probe`, `θ_B`, `θ_C`, `W_smooth`, `p = 0.5`. These parameterize
the run; they are frozen and committed before the confirmatory 24-seed run.

## Trail document

- **`design/validate/SEEDING-DIAGNOSIS.md`**: normative pre-registration
  (hypotheses, worlds, instrument, metric, calibration procedure, bars, censoring,
  reversal condition) plus the appended pilot + confirmatory results and outcome.
