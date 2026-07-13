# Contracts: The Complexity Ladder

The binding interface promises of feature 005. Everything here is
testable, and every MUST maps to a functional requirement in `spec.md`.

## 1. World contract (all rungs)

Every ladder world:

- **MUST** satisfy the `EventSource` protocol exactly as the reference
  world does — `reset() → obs`, `step(action) → obs`, `n_actions`,
  `obs_dim` — and nothing on that surface may expose ground truth
  (FR-004, SC-005). `obs_dim` reports the width the system actually
  receives (total, including distractor channels).
- **MUST** be constructible as `WorldClass(config, rng)` and usable
  through `Engine(config, world_factory=...)` and through the Doc 02
  `Body` unchanged (spec edge case: no new plumbing for drive research).
- **MUST** be deterministic per `(config, seed)`: byte-identical run
  summaries on re-run, worker-parallelism invariant (FR-005), and
  snapshot/resume-exact (world state reconstructs from the seeded stream).
- **MUST**, at its degenerate dial, produce engine-run summaries
  **byte-identical** to `SensorimotorWorld` under the same
  `(config, seed)` (FR-012) — enforced by an integration test per rung.
- **MUST** validate its dials at `Config` construction, rejecting
  impossible combinations with a message naming the violated constraint
  (FR-011).
- **MAY** expose a harness-only `ladder_readings()` accessor for ground
  truth and world-side counters; the engine **MUST NOT** call it.

## 2. Rung-specific behavioral contracts

- **L1 `NonUniformWorld`**: with `region_noise_std = σ > 0`, the latent
  transition inside the region `latent[0] > 0` carries one fresh
  `N(0, σ²I)` draw per step, applied after the action displacement;
  outside the region behavior is bit-equal to reference. Occupancy
  counters count every step exactly once (FR-001, FR-008).
- **L2 `CompositionalWorld`**: with `factor_dims = (d_1, …, d_K)`,
  action `a` displaces only group `a mod K`; construction draws are
  byte-equal to reference (mask applied after the draw); emission is the
  reference emission (FR-002).
- **L3 `DistractorWorld`**: with `distractor_channels = m > 0`, the
  system-visible observation is a reference-form observation (same
  dynamics and emission math over the controllable latent) with `m`
  appended channels that carry zero action information: in `structured`
  mode a fixed-drift latent through its own tanh emission (+ sensor
  noise), in `noise` mode fresh unit-normal draws. Bit-equality with the
  reference world holds at the degenerate dial (`m = 0`); non-degenerate
  runs consume extra draws from the shared stream by design (FR-003).

## 3. Harness contract

- `run_ladder(base_config, rungs, seeds, *, workers) → list[RungResult]`
  runs each requested rung across seeds (parallel workers permitted,
  results reassembled in seed order, a failed seed surfaced never
  dropped), performing per-rung auxiliary runs its criterion requires:
  L1 paired degenerate twin (same seed), L2 quartet arms + end-of-run
  snapshot census, L3 both-mode runs when configured (FR-008).
- `run_suite` gains optional `world_factory` (default `None` — validated
  behavior byte-identical), the same opt-in pattern as
  `proposal_factory` (FR-006).
- Verdicts are judged against `design/validate/LADDER-CRITERIA.md`,
  which **MUST** exist in-repo before the first recorded results
  (FR-007); a FAIL is reported as data with its numbers (FR-009).

## 4. CLI contract

```
pra-validate ladder [--rungs l1,l2,l3] [--seeds ...] [--config PATH]
                    [--json OUT.json] [--workers N]
```

- Runs the requested rungs (default: all implemented) and prints one
  combined report: per rung — configuration summary (including total vs
  learnable observation widths), per-seed reading table, criterion,
  verdict, wall-clock (FR-010, SC-006).
- Exit code 0 whenever the command executed; rung FAILs are data, never
  build failures (FR-009). `--strict` is deliberately not accepted.
- Single-seed invocations carry the existing "FOR DEBUGGING ONLY" banner.
- `--json` writes the machine-readable `LadderReport`; it is the only
  disk artifact (the L2 census snapshot is taken in-memory via the
  snapshot codec, not written to disk).

## 5. Regression contract

With `world = "reference"` (the default), every existing command, test,
and recorded reference value is byte-identical to the pre-feature state;
`tests/integration/test_baseline_unchanged.py` and the full suite remain
the gate (FR-006, SC-002).
