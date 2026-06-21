# Phase 0 Research: PRA Validation Harness

This document resolves the technical unknowns and records the load-bearing design
decisions. Each entry: **Decision**, **Rationale**, **Alternatives considered**.
The behavioral oracle for every decision is `design/validate/pra_sim_v4.py` (the
validated reference run) read against the normative specs PRA-01 and PRA-02.

---

## R1 — Batched, `dim`-grouped frame evaluation (the load-bearing engineering decision)

**Decision.** Represent each frame's state as a row in a per-`dim` *FrameGroup*. A
FrameGroup for dimension `D` stacks the weights of all `F` frames of that dim along a
leading frame axis: encoder `W1[F,H,O] b1[F,H] W2[F,D,H] b2[F,D]`, decoder
`Dc1[F,H,D] dc1[F,H] Dc2[F,O,H] dc2[F,O]`, transition `T1[F,A,H,D] tb1[F,A,H]
T2[F,A,D,H] tb2[F,A,D]`, plus stacked EMA vectors. Encode/decode/transition/fit and
the gradient updates are expressed as batched numpy ops (`np.einsum` / batched matmul)
over the leading `F` axis. Frames of different `dim` live in different groups; the
Engine iterates over **groups** (a handful) not over **frames** (up to 200), and merges
results. A frame is born by appending a row to (or creating) its `dim`'s group; evicted
by deleting a row.

**Rationale.** PRA-01 §7.2 makes this mandatory ("a Python-level loop iteration at a
time does **not** satisfy this requirement") and §1.3/§7.2 tie the scale goal to it.
T-SCALE (this spec, SC-006) needs millions of observation steps × up to 200 frames on
one machine; only vectorization over the frame axis gets there. Grouping by `dim` is the
spec's prescribed layout because different `dim` means different tensor shapes that
cannot share one stack.

**Alternatives considered.**
- *Per-frame object loop* (what the v4 prototype does): rejected — explicitly
  disallowed by §7.2 and orders of magnitude too slow for T-SCALE.
- *Ragged/padded single tensor across all dims* (pad every frame to max dim): rejected —
  wastes compute, complicates the parsimony term, and obscures the per-`dim`
  bookkeeping T4 needs.
- *PyTorch/JAX for autodiff*: rejected — adds a heavy dependency for a single-hidden-
  layer net whose gradients are written out analytically in PRA-01 §5.5/§5.6; numpy is
  sufficient and keeps the dependency surface at one package.

**Verification hook.** `tests/unit/test_batched_equivalence.py` asserts the batched
group path produces bitwise-equal (or within tight float tolerance, then exact after
fixing draw order) results to a straightforward reference per-frame implementation on a
small fixed seed — proving the optimization did not change behavior.

---

## R2 — Conceptual "Frame" object vs. batched storage (reconciling §5 and §7.2)

**Decision.** Keep the *Frame* as a conceptual/identity entity (a `frame_id`, a `dim`,
an `is_candidate`/`age_cycles`/EMA record) but store its **weights and EMAs inside the
FrameGroup arrays**, never as per-object numpy arrays evaluated in isolation. Provide a
thin internal accessor for a frame's state (PRA-01 §9.3 storage seam) so field access is
not scattered. The Bus delivers events to the Engine, which dispatches to FrameGroups;
`FrameResult`s are reassembled per `frame_id` in deterministic (ascending `frame_id`)
order.

**Rationale.** §5 describes behavior per frame; §7.2 mandates batched execution. The
homogeneity requirement ("no per-frame branching in the kernel; all variation lives in
data") is exactly what makes a single batched kernel correct. Reconstructing
`FrameResult`s per `frame_id` preserves the §4.3 deterministic subscriber order and the
§3.2 contract.

**Alternatives considered.** A literal `Frame` class with its own `process()` (the spec's
illustrative form): rejected as the *execution* model (violates §7.2) but retained as the
*conceptual* model and as the reference implementation behind the equivalence test (R1).

---

## R3 — Determinism: single seeded generator, fixed draw order

**Decision.** One `numpy.random.Generator` (`np.random.default_rng(seed)`) per run, the
sole source of randomness, consumed in the exact order PRA-01 mandates: world
construction (objects: start then emission per object in index order, then actions) →
frame weight initialization on each birth → online action sampling → proposal-policy
choices → any tie-breaking. Ties ("lowest survival_score") break by ascending `frame_id`
(§7.1). The effort-only ablation uses a **separate deterministic seed** `seed + 9999`
with its own generator (PRA-02 §2). Summaries are serialized with fixed key order and
fixed float formatting so byte-equality is well-defined.

**Rationale.** FR-010, SC-007, PRA-01 §7.1: identical seed + config ⇒ identical
telemetry, verified by running a seed twice (FR-006). Byte-identical comparison (not
"approximately equal") is the spec's bar; it requires deterministic serialization, not
just deterministic computation.

**Alternatives considered.**
- *Per-component RNGs / Python `random`*: rejected — multiple streams make draw order
  fragile and re-introduce the nondeterminism the spec forbids.
- *Hashing/float-tolerance comparison for the determinism check*: rejected — the spec
  demands **byte-identical** summaries (FR-006, SC-003); any tolerance hides drift.

**Risk.** numpy reductions can be order-sensitive across BLAS threading. Mitigation:
deterministic reduction order in the harness's own aggregation; **pin the BLAS thread
count to 1** (set `OMP_NUM_THREADS=1` / `OPENBLAS_NUM_THREADS=1` in-process before numpy
imports, or use single-threaded reductions) so float accumulation order is fixed; and the
determinism test runs in-process on the same machine/build (the spec's scope is
single-machine reproducibility, SC-007). T011/T012/T036 carry this pin explicitly.

---

## R4 — Observation-space prediction + coverage-fair EMAs + parsimony (the T4 fix)

**Decision.** Implement scoring exactly as the STEP-0 gate fix prescribes:
1. `prediction_error` is measured in **observation space** — decode the predicted next
   pose and compare to the real next observation (PRA-01 §5.2), **not** in pose space.
2. Survival EMAs (`recon_err_ema`, `pred_err_ema`, `effort_ema`) update on **every
   event the frame is exposed to**, not only mapped events (PRA-01 §5.4 coverage-fair);
   *learning* stays gated on mapped events (sparsity / T1).
3. The Scorer adds a parsimony term `w_complexity · dim`
   (`survival_score = w_explain·recon_err_ema + w_predict·pred_err_ema +
   w_effort·effort_ema + w_complexity·dim`), default `w_complexity = 0.04` (PRA-01 §6.2).

**Rationale.** These three changes are the entire reason v4 exists and the only reason T4
is honest (NEXT-STEPS "What the STEP-0 gate changed"). The spec's FR-013 requires the
harness to exercise this exact scoring, not a gameable variant.

**Alternatives considered.** Pose-space prediction, mapped-subset-only scoring, or
no-parsimony scoring — each rejected: they are precisely the three gaming channels the
gate caught (v3's lucky-horizon T4 pass and unbounded population).

---

## R5 — T4 horizon-checkpoint judging (the harness's core new guarantee)

**Decision.** Record `best_dim` (and `population_size`) at **each** configured horizon
checkpoint (default 18/30/50 offline cycles), keep the **full per-seed list** at every
checkpoint, and PASS T4 only if `|best_dim − true_dim| ≤ 1` holds in a strict majority
of seeds at **every** checkpoint. The report prints the per-seed spread + within-one +
exact counts per checkpoint; the mean is never the verdict (FR-003/FR-004, SC-002).

**Rationale.** The prototype passed at 18 cycles and failed at 30 — reading one snapshot
is exactly the false-positive path (US2, PRA-02 §4 T4 horizon rule). Surfacing the spread
is mandatory because a mean near `true_dim` can hide a wide uncentered spread.

**Alternatives considered.** End-of-run snapshot only (prohibited by §4 T4);
mean-of-best_dim verdict (prohibited by FR-003 / §3.4).

---

## R6 — T5 self-limiting (not merely capped)

**Decision.** Compute a per-seed **"still-growing" flag**: true if `population_size` is
strictly increasing over the final third of that seed's offline cycles (e.g. a positive
late slope of frames/cycle above a small epsilon). PASS T5 only if mean `final_population
< max_frames` **and** no seed is still growing. Report `final_population` mean/std and the
per-seed flag. The population-scaled eviction threshold **divides** by the population
factor so crowding tightens the bar and eviction paces spawn (PRA-01 §6.4).

**Rationale.** FR-005, US4, PRA-02 §4 T5: a run that grows to the cap looks bounded but
is not earning persistence. The reference v4 uses a "late slope < 0.5 frames/cycle" read;
the harness generalizes it to "no seed strictly increasing over its final third".

**Alternatives considered.** `final_population < max_frames` alone (the v3 mistake) —
rejected; it passes a population pinned just under the cap that is still climbing.

---

## R7 — Effort-only ablation (T3) with equal experience

**Decision.** A second independent run per seed: fresh world from `seed + 9999`,
`scoring_mode = effort_only`, **same total experience** (same `warmup_episodes` and same
`n_cycles × episodes_per_cycle` online episodes). Transitions train to minimize
predicted-move magnitude, but the recorded `pred_error` is the **true** observation-space
predictive error. T3 PASSes if `improvement(predictive) > improvement(effort_only)` in a
majority of seeds, where `improvement = pred_error_early − pred_error_late`.

**Rationale.** PRA-02 §2 + T3. This is the strongest positive result; equal-experience
and independent-but-deterministic seeding keep the comparison fair and reproducible.

**Alternatives considered.** Reusing the predictive run's world for the ablation —
rejected (§2 requires an independent fresh world); unequal experience — rejected (§2
requires equal total experience).

---

## R8 — Telemetry fields, "not-available", and edge cases

**Decision.** Record exactly the PRA-02 §3 fields. `pred_error_early` = mean over the
first 200 recorded per-step `mean_pred_error` values, **requiring ≥ 50 recorded values**
else mark **not-available** (printed literally, never a misleading number);
`pred_error_late` = mean over the last 200. Loss counts **only post-warmup** (warmup
births are expected and excluded — T6 / US edge case). A seed that errors mid-run is
reported as a failed seed and **excluded from being presented as a complete result**
(never silently dropped from the aggregate). A population pinned at the hard cap is
reported as **capped** and FAILs T5's self-limiting clause.

**Rationale.** PRA-02 §3.1–§3.3 and the spec's Edge Cases section / FR-008 (honest
measurement). "Not available" beats a fabricated number; a dropped seed beats a
silently-shrunk aggregate.

**Alternatives considered.** Imputing early error when too few samples — rejected
(misleading). Averaging over surviving seeds without flagging the failure — rejected
(FR-008, dishonest).

---

## R9 — Reaching millions of observations for T-SCALE

**Decision.** T-SCALE uses the same world/engine with `true_dim ∈ {20, 35, 50}`,
`obs_dim ≥ 3 × true_dim`, the high-dimensionality proposal policy (PRA-01 §6.5, supplied
via the swappable ProposalPolicy seam), and a **lengthened run schedule** so
`observation_steps` per seed reaches the millions (e.g. larger `n_cycles ×
episodes_per_cycle × steps_per_episode`). Report per-`true_dim` `best_dim` spread,
`throughput = observation_steps × mean_population ÷ wall-clock`, and wall-clock. Label it
**investigatory** — never scored as a build pass/fail (FR-009, SC-006, PRA-02 T-SCALE).

**Rationale.** Definition-of-done item 7: the build is complete when T-SCALE is *runnable
and measured*; the dimensionality result at scale is a research finding. Batched
evaluation (R1) is what makes millions-on-one-machine feasible.

**Alternatives considered.** Treating a poor high-dim `best_dim` as a build failure —
explicitly prohibited (T-SCALE is investigatory).

---

## R10 — Tooling, packaging, and quality gates

**Decision.** `pyproject.toml` declares the package, the single runtime dep (numpy), and
config for **pytest** (tests) and **ruff** (format + lint). Run inside the repo-root
`.venv` (Python 3.14, numpy 2.4.6; PEP 668 blocks the system interpreter). Quality gate
before "done": `ruff format --check`, `ruff check`, and `pytest` (all pass, none
skipped) — matching the user's global CLAUDE.md mandate. The harness is exposed both as a
module (`python -m pra.harness.cli`) and a console entry point.

**Rationale.** CLAUDE.md: tests pass / none skipped, artifacts build, code formatted,
lint clean — all blocking. ruff is already on PATH and used for the prototypes; pytest is
the standard Python choice.

**Alternatives considered.** black + flake8 + isort — rejected; ruff subsumes all three
with one tool and one config. unittest — rejected; pytest's fixtures/parametrization fit
the multi-seed, multi-config matrix better.

---

## Resolved unknowns summary

| Unknown (from Technical Context) | Resolution |
|---|---|
| How to satisfy batched §7.2 with per-frame §5 semantics | R1 + R2: `dim`-grouped FrameGroup stacks; conceptual frame identity preserved |
| How to guarantee byte-identical re-runs | R3: single seeded generator, fixed draw order, deterministic serialization |
| How T4 avoids the lucky-snapshot false positive | R5: per-checkpoint spread + within-one majority at every horizon |
| How T5 distinguishes self-limiting from capped | R6: per-seed still-growing flag + dividing population-scaled threshold |
| How to reach millions of observations | R1 + R9: batched eval + lengthened schedule + high-dim proposal seam |
| Test/format/lint tooling | R10: pytest + ruff in repo `.venv`, pyproject-configured |

All NEEDS CLARIFICATION items are resolved. Proceed to Phase 1.
