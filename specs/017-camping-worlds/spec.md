# Feature Specification: Frontier Where Camping Costs (The Worlds That Move)

**Feature Branch**: `017-camping-worlds`
**Created**: 2026-07-18
**Status**: Draft
**Input**: User description: "Frontier where camping costs — mastered-then-changing
and multi-region learnable worlds (research arc 017). The named successor from
JOURNEY ch. 24 / PREDLP-DIAGNOSIS: the frontier drive is validated non-inferior
but has only matched competence on worlds where avoidance is optimal; this arc
builds the two named world families where competence's park-where-error-is-low
strategy should cost something, and measures frontier vs competence vs blend vs
random at 24-seed power under pre-registered bars."

## Overview

Chapter 24 closed Phase A with an honest asterisk. The frontier drive — the
first per-candidate learnability signal independent of novelty — beat random
everywhere, occupied the sensible middle ground between competence (which
avoids the unlearnable) and curiosity (which stares at it), and *matched*
competence on the only worlds available. But those worlds are exactly where
matching is the ceiling: on L1, avoidance is simply optimal, so a drive built
to seek the moving edge of learnability has nothing to show. The chapter named
the two world families where the edge should pay: **mastered-then-changing**
(the world quietly changes after the brain has mastered it — a camper never
notices; a frontier-seeker re-engages) and **multi-region learnable** (several
regions of differing difficulty — an avoider retreats to the easiest and
stays; visiting the harder-but-learnable regions is where improvement lives).

This arc builds both as opt-in worlds behind the existing world seam — same
discipline as every ladder rung: degenerate dials byte-identical to the
reference world, construction draw order fixed, ground truth (what changed,
when; which region is which) visible only to the harness — and measures the
four arms (random, competence, frontier, frontier+competence) at 24-seed
power across the standard horizons, with occupancy-style steering readings
captured per seed. The science is pre-registered in
`design/validate/CAMPING-DIAGNOSIS.md` before any run: the bars state, in
advance, what "frontier earns its keep" means numerically — and what gets
recorded if it doesn't. A FAIL is a finding about the drive, not a defeat:
either way the blend guidance in Doc 05 gets its first evidence from worlds
that punish camping.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - The brain notices when a mastered world changes (Priority: P1)

A researcher runs a brain with the frontier drive (alone or blended) on a
world that changes its dynamics mid-run, after mastery. The frontier-driven
brain re-engages with the changed structure and recovers prediction quality
measurably faster or further than a competence-only brain, which lingers on
what it already knows.

**Why this priority**: This is the drive's reason to exist — realized local
progress is precisely a change detector; if it cannot beat camping here, the
drive has no earned niche and that finding closes the question.

**Independent Test**: The shifting world at the pre-registered shift point,
four arms, 24 seeds, margins and steering readings judged against the
pre-registered bars.

**Acceptance Scenarios**:

1. **Given** the shifting world with the shift at the registered boundary,
   **When** the four arms run at 24 seeds, **Then** the pre-registered
   primary bar (frontier or blend vs competence, post-shift) is decided —
   PASS or an honestly recorded FAIL with spreads.
2. **Given** the degenerate dial (no shift), **When** the world runs,
   **Then** its byte stream is identical to the reference world's.

---

### User Story 2 - Harder-but-learnable regions get visited (Priority: P2)

On a world with several regions of differing learnability (all learnable,
none pure noise), a frontier-driven brain distributes its experience toward
regions where progress is still available, instead of retreating to the
easiest mastered region — and its overall prediction improvement reflects it.

**Why this priority**: The second named family; distinguishes "avoids the
unlearnable" (competence's win, already measured) from "seeks the learnable
edge" (the frontier's claim, never yet measured).

**Independent Test**: The multi-region world, four arms, 24 seeds, per-region
occupancy readings plus improvement margins against the pre-registered bars.

**Acceptance Scenarios**:

1. **Given** the multi-region world, **When** the arms run, **Then**
   per-region occupancy is reported per seed and the registered steering and
   margin bars are decided.
2. **Given** the degenerate dial (uniform regions), **When** the world runs,
   **Then** its byte stream is identical to the reference world's.

---

### Edge Cases

- **Change without a frontier drive**: every arm (including random) sees the
  same shift at the same step — the world change is arm-independent and
  deterministic; only the response differs.
- **Snapshot/resume across the shift**: world state capture must carry
  whatever the shift mechanism needs so a resumed run shifts identically.
- **Continuous mode**: the shift keys on total experience (cycles), which
  continuous mode already tracks through virtual episodes.
- **No new RNG at the shift**: the change must consume no random draws at
  shift time (pre-drawn at construction, in documented order) so determinism
  and the degenerate-dial byte-identity contract hold.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST provide a mastered-then-changing world behind
  the existing world seam: identical to the reference world until a
  configured boundary, then a deterministic, construction-time-drawn change
  to its hidden dynamics; the degenerate setting (no change) MUST be
  byte-identical to the reference world.
- **FR-002**: The system MUST provide a multi-region learnable world behind
  the same seam: multiple regions of differing (but all finite) learnability
  with harness-only ground truth and per-region occupancy counters; the
  degenerate setting MUST be byte-identical to the reference world.
- **FR-003**: Both worlds MUST consume construction randomness in a fixed,
  documented draw order (reference draws first, world-specific draws after),
  and no randomness at change time.
- **FR-004**: Both worlds MUST support state capture/restore such that
  snapshot/resume across any point (including the shift) continues
  byte-identically, and MUST work under continuous mode.
- **FR-005**: The harness MUST run the four-arm comparison (random,
  competence, frontier, frontier+competence) on these worlds with per-seed
  pairing against the same-seed random baseline, at 24-seed power, reporting
  margins with spreads, sign-majorities, and steering readings
  (occupancy/per-region occupancy) — the chapter-24 instrument, pointed at
  the new worlds.
- **FR-006**: The research protocol in `design/validate/CAMPING-DIAGNOSIS.md`
  is normative: hypotheses, arms, bars, and failure exits pre-registered
  before any run; results recorded with spreads regardless of verdict; no
  criterion tuned after the data.
- **FR-007**: All existing behavior stays byte-frozen: new worlds are opt-in
  `Config.world` values with inert-by-default dials; the full existing suite
  passes untouched.

### Key Entities

- **Shifting world**: reference dynamics + a scheduled deterministic change
  (dial: the boundary, plus a magnitude/kind drawn at construction); ground
  truth = what changed and when, harness-only.
- **Multi-region world**: latent space partitioned into regions with
  per-region learnability dials; ground truth = region map + per-region
  occupancy counters, harness-only.
- **Comparison instrument**: the four-arm, 24-seed, paired-margin runner and
  its report (margins, spreads, occupancies, verdicts).
- **Trail document** (`design/validate/CAMPING-DIAGNOSIS.md`): the
  pre-registered protocol and the arc's recorded results and outcome.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Both worlds ship opt-in with degenerate dials byte-identical to
  the reference (stream-level tests), full snapshot/continuous support, and
  the existing suite untouched.
- **SC-002**: The four-arm comparison runs at 24-seed power on both worlds
  with per-seed margins, spreads, and steering readings recorded in the
  trail.
- **SC-003**: The pre-registered primary questions are *decided* — frontier
  (alone or blended) vs competence on each world family — with PASS or an
  honestly recorded FAIL per the trail's bars; either verdict updates Doc
  05's drive guidance and the roadmap's successor list.
- **SC-004**: Whatever the outcome, the trail records it at pre-registered
  power with the raw per-seed data, and JOURNEY chapter 31 tells it
  honestly.

## Assumptions

- The chapter-24 instrument (arms, pairing, T7 noninferiority form, 24-seed
  protocol) transfers to the new worlds unchanged; only the worlds and the
  steering readings are new.
- The shift mechanism can ride the existing deterministic machinery (all
  change parameters drawn at construction; the boundary keyed on the cycle
  counter) — verified against the byte-identity and snapshot contracts
  before any science runs.
- Exact bars (margins, steering orderings, which arm must beat which, at
  which horizons) are frozen in the pre-registration commit BEFORE any run —
  the spec deliberately does not pre-empt them here.
- Feature numbering follows the branch (`017-camping-worlds`); JOURNEY
  chapter 31.
