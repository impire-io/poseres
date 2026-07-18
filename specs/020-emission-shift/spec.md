# Feature Specification: The Emission-Shift World (Appearance Moves, Territory Doesn't)

**Feature Branch**: `020-emission-shift`
**Created**: 2026-07-18
**Status**: Draft
**Input**: User description: "Emission-shift world — appearance changes at
fixed dynamics (research arc 020). Chapter 33's testbed note: the 017
shifting world confounds 'knowledge went stale' with 'territory changed'
(a displacement shift moves where the brain goes). This feature adds the
complementary mode — at the boundary the per-object emission matrices swap
while the displacements never change, so the latent trajectory
distribution is fixed and only appearance moves. With both modes on the
ladder, any future staleness detector can be tested unconfounded."

## Overview

Chapter 33 closed with a testbed debt: the shifting world changes *where
the brain goes* along with *what actions do*, so a staleness detector
validated there can't be told apart from a novelty detector. The
complement is one dial away: `shift_mode="emission"` on the existing
shifting world swaps the per-object emission matrices at the boundary
(drawn at construction, after all other draws, in object order — zero RNG
at shift time) while the displacement set never changes. The latent
trajectory distribution is identical before and after; only the
observations wearing it change. Together the two modes separate the two
things a change can do — move the territory (dynamics mode) or repaint it
(emission mode) — and the harness knows which is which through
`ladder_readings`.

The default (`"dynamics"`) is the recorded 017 behavior, byte-identical;
the mode is read only when a shift boundary is configured. The trail
(`design/validate/EMSHIFT-DIAGNOSIS.md`) pre-registers the first
measured read: the chapter-33 offline place-memory replay on this world,
recorded with the same frozen bars — completing the testbed pair with a
baseline reading either way it falls.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A repainted world at fixed territory (Priority: P1)

A researcher configures `world="shifting", shift_mode="emission"` and gets
a world whose appearance swaps at the boundary while every displacement —
and hence the visited latent distribution — stays exactly as before.

**Acceptance Scenarios**:

1. **Given** emission mode with a boundary, **When** the world steps
   through the shift, **Then** every displacement equals the reference
   set's (dynamics unchanged) and post-boundary observations come from
   the post-shift emission matrices (unit-tested directly).
2. **Given** `shift_mode="dynamics"` (default), **Then** behavior is
   byte-identical to the recorded 017 world, and the degenerate dial
   (no boundary) remains byte-identical to the reference.
3. **Given** a mid-run snapshot across the shift, **Then** the resumed
   world continues byte-identically.

### Edge Cases

- Emission mode without a boundary is a configuration error (loudly
  rejected) — the mode is meaningless without a shift.
- Post-boundary resets (new episodes) also wear the new emission — the
  swap is a world property, not a step artifact.

## Requirements *(mandatory)*

- **FR-001**: `shift_mode: "dynamics" | "emission"` on the shifting world;
  `"dynamics"` default = the recorded 017 behavior byte-identically;
  emission mode draws per-object post-shift emission matrices at
  construction (after all other draws, object order) and swaps them at
  the boundary; displacements never change; no RNG at shift time.
- **FR-002**: `ladder_readings` reports the mode; state capture works
  across the shift; validation rejects emission mode without a boundary.
- **FR-003**: The trail's pre-registered read (the offline place-memory
  replay, chapter-33 bars) is recorded on this world before any detector
  research uses it.

## Success Criteria *(mandatory)*

- **SC-001**: Unit-tested swap semantics, dynamics invariance, state
  capture, validation; full suite green, baseline untouched.
- **SC-002**: The offline replay read recorded in the trail with the
  frozen bars — the testbed pair ships with its first baseline.
- **SC-003**: Docs propagated (Doc 07 dial row, JOURNEY ch. 34) whatever
  the reading.

## Assumptions

- One world class, two modes (extends `ShiftingWorld`) — a separate class
  would duplicate the boundary machinery for no gain.
- Feature numbering follows the branch (`020-emission-shift`); JOURNEY
  chapter 34.
