# Feature Specification: Brain Seeding — Does a Learned Brain Give the Next One a Head Start That Compounds?

**Feature Branch**: `028-brain-seeding`
**Created**: 2026-07-20
**Status**: Draft
**Input**: User description: "Brain seeding — does a snapshotted brain used as a seed give a new brain a head start that compounds across chaining (brain A seeds B seeds C)? Testbed: the rover world, with maps A/B/C as different obstacle layouts drawn from a harness-owned layout seed (same body/physics). Three arms measured by time-to-competence: seeded (brain trained on map A), fresh (blank brain), and a maturity control (a brain that trained the identical experience budget on a permuted rover — learnable but unrelated). Act 1 (hop A→B) tests transfer (bars B1 vs fresh, B2 vs maturity control). Act 2 (hop B→resize→C) tests compounding (bar C1: head-start margin must not shrink hop-over-hop). 24 paired seeds. Reversal condition: if seeded loses or margins shrink, earned persistence is the suspect and 'seed brains' leaves the vision language until diagnosed. Pre-registered in design/validate/SEEDING-DIAGNOSIS.md; existing behavior byte-frozen."

## Overview

The roadmap's compounding-intelligence horizon (JOURNEY ch. 42; ROADMAP
"Seeding / compounding intelligence") names a claim and marks it *runnable with
current code* — B5 snapshots plus the existing rover world and paired-seed
harness. This feature makes it runnable and measures it, honestly, at
pre-registered power.

The claim, plainly: **a brain that already learned one world should give the
next brain a real head start when moved to a new one — and the head start should
keep compounding when chained** (brain A seeds B, B seeds C), not fade after the
first hop. If it holds, "share your brain / build on someone else's" becomes a
real capability and a building block for the language horizon. If the head start
halves each hop, it is a one-time discount, not compounding — and per the
roadmap's own reversal condition, that points a finger at how the brain protects
old knowledge (earned persistence, and PRA's two forgetting channels — weight
drift *and* eviction).

The testbed is the **rover** (feature 006): bounded, stationary, and the natural
"shareable brain" demonstrator, so "reached competence" is a stable, meaningful
line rather than a moving target. A "map" is the rover world's obstacle layout,
drawn at construction — so maps A/B/C are the same body and physics with
different layouts, built from a **layout seed the harness owns separately from
the brain's seed** (the ownership-split-rng discipline of features 009/017), so
all three arms at a given seed face the *identical* new map. The maturity control
matures on a **permuted rover** (its action/sensor wiring scrambled by a fixed
construction-time permutation: fully learnable, so it matures normally, but its
learned mapping is useless on a real map) — the honest arm that separates a head
start from *relevant* knowledge from one from just being older and bigger.

The science is pre-registered in `design/validate/SEEDING-DIAGNOSIS.md` before
any confirmatory run: hypotheses, arms, worlds, the time-to-threshold metric, the
θ/budget calibration procedure (a pilot sets them, then they *freeze*), the exact
bars, the right-censoring rule, and the reversal condition. A FAIL is a finding
about the brain, not a defeat.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A seeded brain learns a new map faster, and it is transfer not maturity (Priority: P1)

A researcher trains a brain on rover map A until it plateaus, snapshots it, and
mounts it on a fresh map B. It reaches the competence line in fewer episodes
than a blank brain — *and* fewer than a brain that spent the same experience in
an unrelated (permuted) world. The head start is real and it comes from relevant
learned structure, not from age.

**Why this priority**: This is the seeding claim's core. Without the transfer
edge over *both* fresh and the maturity control, there is no head start worth
compounding, and that finding closes the question.

**Independent Test**: Hop 1 (A → B), three arms (seeded, fresh, maturity), 24
paired seeds, time-to-threshold margins judged against the pre-registered
superiority bars B1 (vs fresh) and B2 (vs maturity control), with sign-counts,
spreads, and reach-rates reported.

**Acceptance Scenarios**:

1. **Given** 24 seeds, map A pre-training frozen at the plateau budget and θ_B
   frozen from the fresh-brain pilot, **When** the three arms run on map B,
   **Then** bars B1 and B2 are *decided* — PASS or an honestly recorded FAIL
   with the per-seed spread and reach-rates.
2. **Given** the degenerate dials (single layout seed; identity permutation),
   **When** the rover and permuted-rover worlds run, **Then** their byte streams
   are identical to today's rover world.

---

### User Story 2 - The head start does not shrink when the brain grows a sensor and hops again (Priority: P2)

The seeded brain is chained onward: A → B, then its body grows by one sensor
(obs_dim 10 → 11 through the existing `register_sensor` → `resize` path), then it
learns map C. Its head start over a fresh brain on map C is no smaller than its
head start was on map B. A head start that survives a body change and a second
hop is compounding; one that halves is a discount.

**Why this priority**: The second, harder half of the claim, and the one the
roadmap flags as genuinely unmeasured — transfer benefit *across* `resize()` has
never been measured (only bit-preservation has).

**Independent Test**: Hop 2 (B → resize → C), 24 paired seeds, the seeded-vs-fresh
time-to-threshold margin at C judged against bar C1: (a) margin₂ superiority and
(b) non-shrink — margin₂ not significantly below margin₁.

**Acceptance Scenarios**:

1. **Given** the seeded chain resumed across a +1-sensor resize onto map C with
   θ_C frozen from its own fresh pilot, **When** hop 2 runs at 24 seeds,
   **Then** bar C1 is decided — PASS or an honestly recorded FAIL, with margin₁
   and margin₂ both reported per seed.

---

### User Story 3 - The experiment is reproducible and does not disturb the reference (Priority: P3)

Anyone can re-run the seeding experiment and get byte-identical numbers, and
mounting the new worlds or running the experiment never changes the validated
reference behavior. The degenerate dials reproduce today's rover exactly, and a
seeded-then-resized chain snapshots and resumes byte-identically.

**Why this priority**: The constitution (reference-preserving forever; determinism
is the instrument). A research verdict is only worth recording if it reproduces
and if the machinery that produced it left the validated core untouched.

**Independent Test**: Stream-level byte-identity of the degenerate dials against
today's rover; the full existing suite passing untouched; a snapshot/resume of a
seeded chain across the permuted-world maturity training and the +1-sensor resize
continuing byte-identically.

**Acceptance Scenarios**:

1. **Given** the single-layout-seed rover and the identity-permutation rover,
   **When** each runs a seed, **Then** its byte stream equals today's rover
   world's for the same seed.
2. **Given** a seeded chain snapshotted mid-run, **When** it is resumed across
   the maturity training and the +1-sensor resize, **Then** the resumed run
   continues byte-identically (the B5 guarantee, now exercised across a
   transfer-then-resize chain).

---

### Edge Cases

- **Never reaches the line (right-censoring)**: an arm whose smoothed error never
  crosses θ within the probe budget is censored at the probe budget (recorded as
  "did not reach"); the margin uses the censored value (conservative — it never
  inflates a seeded advantage beyond the budget) and reach-rate is reported
  separately. The probe budget is pilot-set generously so fresh censoring is rare.
- **Fair pairing**: at seed *s* all three arms face the *same* map B layout and
  the same map C layout — only the starting brain differs. Layout is drawn from a
  world-owned layout seed (function of *s* and the hop label), independent of the
  brain's exploration randomness (which the seeded/maturity arms carry from their
  snapshot and the fresh arm draws from *s*).
- **Resize determinism**: the +1-sensor growth is applied identically to all
  chained arms at the same point; resume across it is byte-identical (feature
  010 guarantee).
- **Permuted-identity byte-identity**: the identity permutation of the permuted
  rover consumes construction randomness in the same order as the plain rover and
  produces an identical byte stream.
- **No new RNG at hop boundaries**: layout and permutation draws happen at world
  construction in a documented order; nothing consumes randomness at a hop beyond
  the already-specified resize draws.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The rover world MUST accept a **layout seed owned separately from
  the run/brain seed**, so the harness can build maps A/B/C with independent
  layouts while the brain's exploration randomness is owned elsewhere; the
  single-seed degenerate path MUST be byte-identical to today's rover world.
- **FR-002**: The system MUST provide a **permuted rover** world behind the
  existing world seam: the rover with a fixed, construction-time-drawn permutation
  of its action semantics and/or sensor channels — fully learnable, structurally
  unrelated to an un-permuted map; the identity-permutation degenerate setting
  MUST be byte-identical to the plain rover.
- **FR-003**: The system MUST provide a **seeding experiment command**
  (`pra-validate seeding`) that orchestrates, per seed: pre-train on map A →
  snapshot → three-arm hop-1 on map B (seeded / fresh / maturity) → +1-sensor
  resize of the seeded (and maturity) chain → hop-2 on map C, across 24 paired
  seeds.
- **FR-004**: The harness MUST measure **time-to-competence** from the recorded
  per-checkpoint prediction-error trajectory: the first checkpoint at which the
  smoothed error crosses the pre-registered θ, with the documented right-censoring
  rule and reach-rate reporting.
- **FR-005**: The research protocol in `design/validate/SEEDING-DIAGNOSIS.md` is
  normative: hypotheses, arms, worlds, metric, the θ/budget calibration procedure
  (pilot then freeze), bars, censoring, and reversal condition pre-registered; θ
  and budgets frozen and committed *before* any confirmatory run; no criterion
  tuned after the data.
- **FR-006**: The harness MUST report **paired per-seed margins with spreads,
  sign-counts, and reach-rates**, reusing the existing paired-margin statistical
  form (one-sided; superiority PASS iff `mean > +1.9·SE`, non-shrink PASS iff
  `mean ≥ −1.9·SE`), and MUST emit human-readable plus optional JSON.
- **FR-007**: All existing behavior MUST stay byte-frozen: the new worlds are
  opt-in with inert-by-default dials, the reference suite passes untouched, and
  snapshot/resume across the permuted-world maturity training and across the
  +1-sensor resize is byte-identical.

### Key Entities

- **Rover map**: the rover world's obstacle+spawn layout, drawn from a
  harness-owned layout seed; A/B/C are three layouts of one body and physics.
- **Permuted rover**: the rover with a construction-time permutation of action
  and/or sensor wiring — learnable but unrelated; the maturity control's world.
- **The three arms**: seeded (map-A brain), fresh (blank), maturity control
  (permuted-world brain, identical experience budget).
- **The two acts**: hop 1 (A → B, the transfer test, bars B1/B2); hop 2 (B →
  resize → C, the compounding test, bar C1).
- **Time-to-competence reading**: first-crossing of θ on the smoothed
  prediction-error trajectory, with censoring and reach-rate.
- **Trail document** (`design/validate/SEEDING-DIAGNOSIS.md`): the pre-registered
  protocol, the frozen θ/budgets, and the arc's recorded results and outcome.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Both worlds ship opt-in with degenerate dials byte-identical to
  today's rover (stream-level tests), and the existing suite passes untouched.
- **SC-002**: The seeding experiment runs at 24-seed power over the two acts, with
  per-seed time-to-competence, margins, spreads, sign-counts, and reach-rates
  recorded in the trail.
- **SC-003**: The pre-registered bars are *decided* — B1 (seeded vs fresh, hop 1),
  B2 (seeded vs maturity control, hop 1), and C1 (seeded-vs-fresh margin
  non-shrink across the resize hop) — each PASS or an honestly recorded FAIL per
  the trail's frozen criteria; the verdict updates the roadmap's seeding entry and
  Doc 06's persistence guidance.
- **SC-004**: Whatever the outcome, the trail records it at pre-registered power
  with the raw per-seed data, and JOURNEY chapter 44 tells it honestly — including
  triggering the reversal condition if seeded loses or the margin shrinks.

## Assumptions

- The rover produces a per-checkpoint prediction-error trajectory through the
  standard `Engine.run` path (it mounts on the unchanged engine), so
  time-to-competence is measurable without new telemetry.
- The existing paired-margin statistical form (one-sided ±1.9·SE, sign-counts and
  spreads reported alongside) transfers to time-to-threshold margins unchanged;
  only the metric (episodes-to-θ instead of improvement) is new.
- θ (per map) and the pre-train/probe budgets are pilot-calibrated and then frozen
  in the pre-registration commit BEFORE any confirmatory run — the spec
  deliberately does not pre-empt their numeric values here.
- The +1-sensor resize rides the existing `register_sensor` →
  `apply_pending_tools` → `FrameStore.resize` path and the feature-010
  resume-across-resize guarantee; transfer *benefit* across it is exactly what
  act 2 measures (bit-preservation is already guaranteed).
- Feature numbering follows the branch (`028-brain-seeding`); JOURNEY chapter 44.
