# Phase 0 Research: Motivation and Action Layer

Load-bearing decisions with rationale and alternatives. The governing sources
are design Doc 05 (normative behavior), PRA-01/PRA-02 (the validated core and
suite this feature must not disturb), and the feature spec's FR-001..FR-011.

---

## R1 — The Policy seam replaces the inline action draw, byte-identically

**Decision.** Add a `Policy` protocol (`select_action(context, rng) -> int`) and
inject it into the Engine like the existing seams. The default
**`RandomPolicy`** implements exactly the current inline behavior — a single
`rng.integers(n_actions)` draw per step, nothing else — so every existing mode
(suite, determinism, scale, scan oracle comparisons) consumes the identical RNG
stream and produces byte-identical summaries. The curiosity policy is selected
explicitly (`policy_mode="curiosity"` / the `agency` command), never by default.

**Rationale.** FR-008/SC-003 make byte-identity with the validated build a hard
gate. The only way to introduce a seam without disturbing bytes is for the
default implementation to reproduce the current draw exactly — same call, same
order, same count.

**Alternatives considered.** Making curiosity the default policy (rejected: the
validated suite would change behavior and bytes; the baseline is also the
control arm of T7); wrapping the policy around the Engine externally (rejected:
Doc 05 §7 wires the policy into the fast loop — it needs the frames' transition
models and the drive, which live inside the run).

**Verification hook.** `tests/contract/test_policy_contract.py` byte-compares a
`RandomPolicy` run against the recorded validated reference values;
`tests/integration/test_baseline_unchanged.py` guards the full summary.

---

## R2 — Value-signal telemetry is conditional, so baseline bytes never change

**Decision.** `PerSeedRunSummary` gains **optional** agency fields (mean/final
value signal, mean learning-progress and novelty terms, fraction of
lookahead-directed actions). `canonical()` includes them **only when the run
used a drive** (agency mode); in every existing mode the serialized form is
bit-for-bit what the validated build produced.

**Rationale.** The determinism and regression checks compare serialized bytes.
Unconditional new fields would fail SC-003 against the validated build without
changing any behavior — a false regression. Conditional presence keeps the
baseline artifact frozen while giving the new tests real telemetry (FR-010).

**Alternatives considered.** A separate telemetry file (rejected: two artifacts
to keep deterministic; the summary is the canonical unit the harness already
byte-compares); versioning the summary format (rejected: needless breakage of
the validated artifact).

---

## R3 — Determinism: drives are pure; the policy's draw order is fixed

**Decision.** Drives consume **no RNG** — `value(context)` is a pure function of
the context and the drive's fixed parameters (Doc 05 §2.1 requires exactly
this). The curiosity policy consumes RNG in a fixed per-step order: (1) one
uniform draw for the ε-gate; (2) one `integers` draw **only if** exploring or
below the maturity bar. Exploit steps draw nothing further (argmax with
lowest-index tie-break is deterministic).

**Rationale.** FR-007: byte-identical re-runs from a seed. A fixed,
data-independent draw *order* (though not count — the branch is itself a
deterministic function of the seeded stream and state) preserves reproducibility
exactly as the zero-start birth logic already does in the validated engine.

**Alternatives considered.** A separate RNG stream for the policy (rejected:
PRA-01 §7.1 mandates one seeded generator per run, and multiple streams were
already rejected in feature 001's research R3).

---

## R4 — Drive immutability is structural, not procedural

**Decision.** Drive parameters (weights, window lengths, memory size, ε, the
drive roster itself) live in the existing **frozen** `Config` dataclass and in
frozen per-drive parameter structs. No runtime component receives a mutable
handle; attempting attribute assignment raises. The drive's *bookkeeping*
(error windows, observation memory) is explicitly mutable state — Doc 05 §3.3
"bookkeeping, not policy" — held apart from the parameters.

**Rationale.** Doc 05 §6 is mandatory: a drive that can rewrite itself is
trivially maximized by redefining itself. Structural immutability (frozen
dataclasses) is stronger than convention and directly testable (SC-005).

**Alternatives considered.** Runtime guards/assertions on setters (rejected:
weaker, needs discipline everywhere); copying params per step (rejected: cost
and noise without adding safety over frozen structs).

---

## R5 — Curiosity internals: the [O] defaults, chosen and tagged as tunable

**Decision.** (All parameters land in Config with Doc 07 defaults; the *shape*
is normative per Doc 05 §3, the constants are [D]/[O] tunables.)

- **Learning progress** = `max(0, mean(baseline_window) − mean(recent_window))`
  over the per-step mean mapped prediction error the engine already computes;
  `lp_recent_window = 60` steps, `lp_baseline_window = 600` steps (≈ the 10×
  separation the EMA decay structure of the core already uses); LP = 0 until the
  baseline window has at least `lp_recent_window` samples (cold start: novelty
  carries the signal, per §3.3).
- **Novelty** = min-distance unfamiliarity: `min_m ‖obs − m‖ / (‖obs‖ + 1e-6)`
  over a bounded FIFO `recent_observation_memory` (`novelty_memory_size = 200`);
  **empty memory ⇒ novelty = 1.0** (maximal unfamiliarity — finite from step
  one, FR-001).
- **Combination**: `w_progress = 1.0`, `w_novelty = 1.0` (§3.3's fixed weights;
  the automatic handover comes from LP being ~0 early and novelty shrinking as
  the memory fills with familiar observations — no phase switch).

**Rationale.** Doc 05 flags the exact windows/statistics as **[O]** ("expected
to be tuned"); the requirement is only that LP rewards *reduction* (mastered and
noise regions both ~0) and novelty exists from the first observation. These
defaults satisfy the requirement-shape with the fewest new ideas, reuse the
engine's existing per-step error statistic, and are all first-class config.

**Alternatives considered.** EMA-based LP instead of windows (equivalent in
spirit; windows are more literally §3.1 and easier to unit-test against
flat/falling histories); kernel-density novelty (rejected: heavier, no
requirement demands it); per-frame LP (rejected: §3.1 defines LP over the
system's prediction error; per-frame attribution is a future refinement).

---

## R6 — One-step lookahead: predict with the best frame, value via the drive

**Decision.** For each candidate action `a`: encode the current observation with
the current **best frame** (lowest survival score — the same deterministic
notion the engine already maintains), predict the next pose with that frame's
transition model for `a`, decode it to a predicted observation, and evaluate the
drive over the predicted context (in practice the novelty term differentiates
candidates — LP is history-shaped and near-constant across one-step candidates,
which is the honest reading of "estimate the value the predicted outcome would
yield"). Choose the argmax; ties break by lowest action index. Gate: lookahead
runs only when a best frame exists and its `age_cycles ≥
lookahead_min_age_cycles` (default 2); otherwise uniform random (§4.3). With
probability `exploration_epsilon` (default 0.1), take a uniform random action
regardless.

**Rationale.** Doc 05 §4.2 names the frames' transition models and the drive as
the two ingredients; the best frame is the population's operative world-model
and is already deterministically defined (ties by frame_id). Decoding to
observation space keeps the drive evaluating the same currency it always sees
(and reuses the honest obs-space machinery of the core). Single-frame lookahead
costs ~9 small mat-vecs per step at defaults — negligible (plan: Performance
Goals).

**Alternatives considered.** Ensemble lookahead over all mapping frames
(rejected for the base build: cost and an aggregation rule Doc 05 doesn't
specify; the seam allows it later); valuing predicted *pose* novelty instead of
decoded observation novelty (rejected: pose spaces differ per frame and
pose-space scoring is exactly the gaming channel the STEP-0 gate closed);
sampled action subsets (unnecessary at `n_actions = 4`; noted for large action
spaces).

---

## R7 — T7, the honest verdict: curious ≥ random, same seed, equal experience

**Decision.** New measurement (`harness/agency.py`) and evaluator (**T7**): for
each seed run two full predictive runs with **the same seed** — identical world,
identical schedule, equal experience — differing only in policy
(`CuriosityLookaheadPolicy` vs `RandomPolicy`). Compare each run's own
`improvement = pred_error_early − pred_error_late`. **T7 PASSes iff
curious-improvement ≥ random-improvement in a strict majority of seeds** (the
spec's honest bar: directedness must not hurt; strictly-greater is reported when
observed). Rendered with the per-seed margins, never a mean alone. Runs execute
in parallel workers per the 001 pattern; determinism per run is unchanged.

**Rationale.** Same-seed pairing removes world-sampling variance from the
comparison (the two arms see the same objects/emissions), which is the tightest
honest control available and mirrors R7 of feature 001 (the T3 ablation's
equal-experience rule). FR-009 fixes the majority rule and spread reporting.

**Alternatives considered.** Different derived seed for the curious arm
(rejected: adds world variance to a comparison that action policy alone should
drive); requiring strictly-greater (rejected in the spec's Assumptions: in a
small world where random coverage is already good, "not worse" is the honest
claim — a strictly-greater bar would invite tuning-to-pass, the exact failure
mode this project guards against).

---

## R8 — Multi-drive mechanism: a weighted set, one drive shipped

**Decision.** `WeightedDriveSet` combines configured drives as
`Σ drive_weight[d] · value_d(context)` with weights fixed in Config
(`drive_weights`, default `{"curiosity": 1.0}`). The base build registers
curiosity only; a second drive (e.g. competence) is added by constructing the
set from configuration — no code change in Engine/policy (US5). The Drive
protocol carries `id()` so weights bind by name.

**Rationale.** Doc 05 §2.2/§5 requires the mechanism (not the counter-drive) so
wandering has a configuration-level remedy. A named-weight map is the smallest
mechanism satisfying "counter-drive without code change."

**Alternatives considered.** Shipping a competence drive now (rejected: Doc 05
explicitly bases the build on curiosity only; adding a second drive without an
observed wandering problem is speculative tuning).

---

## Resolved unknowns summary

| Unknown | Resolution |
|---|---|
| How to add a policy without touching the validated bytes | R1: seam whose default reproduces the inline draw exactly; R2: conditional telemetry |
| Where drive/policy randomness comes from | R3: drives pure (no RNG); policy fixed draw order from the single seeded generator |
| How immutability is enforced | R4: frozen dataclasses; bookkeeping separated as state |
| The [O] curiosity internals | R5: windowed LP (60/600), min-distance novelty (200-deep memory, empty ⇒ 1.0), weights 1.0/1.0 |
| What "lookahead" concretely computes | R6: best-frame predict→decode per action, drive-valued, argmax, ε=0.1, maturity gate age≥2 |
| How the load-bearing claim is judged | R7: same-seed paired runs, curious ≥ random in strict majority, spread reported |
| Multi-drive without code change | R8: WeightedDriveSet + named drive_weights config |

All NEEDS CLARIFICATION items are resolved. Proceed to Phase 1.
