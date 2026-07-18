# Feature Specification: Predictive LP — The Scout Drive

**Feature Branch**: `018-predictive-lp`
**Created**: 2026-07-18
**Status**: Draft
**Input**: User description: "Predictive LP — the scout drive: anticipate
progress instead of remembering it (research arc 018). The Doc 05 [O] gap,
sharpened by chapter 31: realized LP is a lagging indicator — after a world
shift, newer errors near a candidate exceed older ones, so
max(0, older − newer) reads zero exactly when progress is available. The
scout drive is its mirror: max(0, newer − older) over the same remembered
neighborhood — positive precisely where local error has risen (stale
knowledge), zero on flat-high noise and flat-low mastery. Measured on the
017 camping-costs worlds against their frozen 576-run baseline, same seeds,
competence-relative bars per the chapter-31 clause lesson."

## Overview

Chapter 31 measured the camping bill and found nobody collects it: when a
mastered world shifts, the camper (competence) recovers worst of all arms,
yet the frontier drive — built to seek learning — re-engages no better than
random, because its signal is *realized* progress: error having fallen.
After a shift, error has *risen* near everything the brain knew, so the
frontier reads zero at exactly the moment progress is available.

The scout drive closes that gap with the smallest possible change: the same
k-nearest-neighbor machinery over the same remembered errors-at-visit, with
the halves compared the other way. Rising local error is the signature of
knowledge gone stale — a place where relearning is available now. Flat-high
regions (noise) and flat-low regions (mastery) both read zero, so the
noisy-TV guard and the no-camping property are inherited by construction.
Scout and frontier are complementary detectors — one sees progress being
made, the other sees progress newly available — and they blend on a real
surface with each other and with competence.

The claim is measured where it can fail: on the shifting world, against the
frozen 017 grid (same seeds, same construction — arms don't affect world
draws), with the chapter-31 clause lesson applied: the primary bar is
competence-relative AND random-relative — a scout-bearing arm must beat
*both* the camper and undirected exploration post-shift, else the niche is
not earned and that is the recorded finding. The multi-region world runs as
the no-harm check. The science is pre-registered in
`design/validate/SCOUT-DIAGNOSIS.md` with a signal-shape probe before any
drive code.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Stale knowledge gets revisited (Priority: P1)

A researcher runs a brain with a scout-bearing drive configuration on a
world that changes after mastery. Post-shift, the brain steers toward the
places whose remembered errors no longer match reality and recovers faster
than both a camper and an undirected explorer.

**Why this priority**: the entire point — the first drive whose signal
*leads* a change instead of trailing it.

**Independent Test**: the shifting world at the 017 dial, scout arms at 24
seeds, judged post-shift against the frozen competence and random baselines.

**Acceptance Scenarios**:

1. **Given** the shifting world, **When** scout arms run at 24 seeds,
   **Then** the pre-registered primary (beats both competence and random
   post-shift) is decided — PASS or an honestly recorded FAIL.
2. **Given** the pre-shift phase, **When** the same runs are read at the
   shorter horizons, **Then** scout arms are noninferior to competence
   (the edge is not bought before the shift).

---

### User Story 2 - No harm where nothing is stale (Priority: P2)

On worlds where knowledge never goes stale (the multi-region world, the
reference), scout-bearing configurations behave like their non-scout
counterparts: the signal sits at zero and adds no cost.

**Independent Test**: multi-region arms at 24 seeds vs the frozen 017
competence baseline (noninferiority); the drive is opt-in and the validated
build is untouched.

**Acceptance Scenarios**:

1. **Given** the multi-region world, **When** scout arms run, **Then**
   improvement is noninferior to competence's frozen baseline.
2. **Given** any existing configuration (no "scout" in `drive_weights`),
   **When** it runs, **Then** behavior is byte-identical to the current
   build.

---

### Edge Cases

- **Cold start / resumed pre-frontier snapshots**: silent (0) until 2k
  finite-error memory entries exist — inherited from the frontier's guard.
- **Noise regions**: flat-high errors → older ≈ newer → 0; the scout never
  stares at the noisy TV.
- **No new constants**: the scout reuses `frontier_neighbors` — same
  neighborhood, opposite reading.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST provide a `"scout"` drive in the registry:
  `max(0, mean(err@visit, newer half) − mean(err@visit, older half))` over
  the 2k nearest finite-error remembered neighbors of a candidate — the
  frontier's machinery, halves compared the other way; pure floats, no RNG,
  silent below 2k entries.
- **FR-002**: The drive MUST be opt-in via `drive_weights` only; every
  configuration not naming it is byte-identical to the current build.
- **FR-003**: The research protocol in `design/validate/SCOUT-DIAGNOSIS.md`
  is normative: a signal-shape probe (P1) runs before any drive code lands;
  E1 bars are frozen before any run; the 017 grid is the baseline (same
  seeds); failure exits are binding and a FAIL is recorded data.
- **FR-004**: The comparison MUST report per-seed margins with spreads,
  sign-majorities, and the post-shift readings, competence- and
  random-relative.

### Key Entities

- **Scout drive**: the mirrored neighborhood statistic; registry id
  `"scout"`.
- **Trail document** (`design/validate/SCOUT-DIAGNOSIS.md`): protocol,
  probe, results, outcome.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: P1 shows the pre-registered signal shapes on real traces
  (post-shift: scout > 0 where frontier ≈ 0) before the drive ships.
- **SC-002**: The primary question is decided at 24-seed power against the
  frozen baselines: a scout-bearing arm beats both competence and random
  post-shift — PASS, or a recorded FAIL naming what the signal still lacks.
- **SC-003**: No harm: pre-shift and multi-region noninferiority vs
  competence; the validated build byte-identical without the drive.
- **SC-004**: The outcome propagates (Doc 05 guidance, Doc 07 registry
  note, ROADMAP, JOURNEY chapter 32) whatever the verdict.

## Assumptions

- The 017 grid is a valid frozen baseline: arms do not affect world
  construction or streams, so same-seed comparisons are exactly paired.
- The scout's noisy-TV guard (flat-high → 0) holds by construction and is
  probed in P1, not assumed.
- Feature numbering follows the branch (`018-predictive-lp`); JOURNEY
  chapter 32.
