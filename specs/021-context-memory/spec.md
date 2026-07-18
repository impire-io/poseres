# Feature Specification: Action-Context Error Memory (Anchor On What The Brain Did)

**Feature Branch**: `021-context-memory`
**Created**: 2026-07-18
**Status**: Draft
**Input**: User description: "Action-context error memory — anchor on what
the brain did, not what it saw (research arc 021). Chapters 32-34
eliminated sliding FIFOs (forget the baseline) and observation places
(not shift-invariant) and left a measured bracket: 4x separation on both
shift modes. This arc tests the third anchor space — the agent's own
recent action context — which no world change can move: after a dynamics
shift the same context leads somewhere else; after an emission shift it
leads to the same place repainted; either way the error at that index
jumps against a well-posed remembered best. Spike-robust cells (windowed
medians, running best-median) replace the EMA minima that painted phantom
staleness. Offline gate against the chapter-34 bracket before any code;
conditional live stage against the frozen 017 grid."

## Overview

The staleness-detection research has failed twice on representation and
now has measured brackets on both failure modes. This arc's candidate
space is the first that is invariant *by construction*: the index is the
brain's own last-m-actions context, chosen by the policy, not the world.
Cells are `n_actions^m` slots — no anchors to allocate, no distance
metric, nothing the world can relocate. Per cell, a bounded window of
errors-at-visit is summarized by its median (spikes die), and the best
full-window median ever achieved is the remembered mastery; staleness is
the excess of the current median over that best. Two constants (context
length m, window W), pinned by the pre-registered offline scan — one
setting must clear every bar on both shift modes, or the arc closes at
its gate with the numbers recorded (the third gate-stop protocol).

If the gate passes, the memory ships opt-in in the agency layer with a
scout drive reading it, and the chapter-31 question is asked one more
time against the frozen 017 baselines.

## Requirements *(mandatory)*

- **FR-001**: The offline gate (P1) runs before any src change, on both
  shift modes plus the benign floor, with the (m, W) grid and all bars
  frozen in `design/validate/CONTEXTMEM-DIAGNOSIS.md`.
- **FR-002**: If gated through: the memory is opt-in (a size dial, 0 =
  off = byte-identical), lives in the agency bookkeeping, consumes no
  RNG, rides snapshots ON-only, and a `"scout"` registry drive values a
  candidate action by its context cell's staleness.
- **FR-003**: The live stage is judged against the frozen 017 grid with
  competence-AND-random-relative bars; a FAIL is recorded data.

## Success Criteria *(mandatory)*

- **SC-001**: The gate decides the representation question on real traces
  at one pinned (m, W) across all worlds — PASS or a recorded close.
- **SC-002**: Conditional: the live primary decided at 24-seed power;
  no-harm clauses hold; byte-identity at default.
- **SC-003**: Outcome propagated (trail, Doc 05/07 as applicable, ROADMAP,
  JOURNEY ch. 35) whatever the verdict.

## Assumptions

- The scout drive's lookahead evaluates candidate ACTIONS, so the context
  cell of "current context + candidate action" is directly addressable —
  the drive seam fits without new plumbing (verified at implementation).
- Feature numbering follows the branch (`021-context-memory`); JOURNEY
  chapter 35.
