# Feature Specification: Commitment

**Feature Branch**: `043-commitment`
**Created**: 2026-08-16
**Status**: Shipped
**Input**: User description: "Promote the measured commitment mechanism (research topic the-last-crack, episode 0101, design 0014) into the product with zero behavior change when off — the hold that finishes."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Multi-frame intentions survive the vote (Priority: P1)

A person mounting the brain on a body whose actions take many
consecutive frames to pay (a live dig: ~30 frames, with the world
resetting progress on any interruption) wants a started intention to
be finished rather than re-litigated every frame — without the policy
becoming an addiction machine.

**Why this priority**: Measured (L1, the-last-crack): the vote is a
knife-edge — hold margin κ·Δ̂ ≈ 0.008 vs frame-noise flips up to
0.069, with the ε-gate breaking even winning holds. The shipped
policy completed 0 digs in 4,500 parked steps; with commitment, 10
breaks and a full forage chain first-eating at step 333.

**Acceptance Scenarios**:

1. **Given** `commit_kappa > 0` and the previous emitted action's
   sensed progress rose since the last frame, **When** candidates are
   valued, **Then** the incumbent (same action as previous) earns
   `+commit_kappa` and holds a knife-edge vote.
2. **Given** `explore_defers_holds=True` and progress advancing,
   **When** the ε-gate draws explore, **Then** the directed path runs
   instead (the uniform draw still happens — draw-order parity).
3. **Given** sensed progress COLLAPSES by more than 0.5 (the world's
   own completion/reset), **When** the next selection runs, **Then**
   the incumbent is cleared and the vote runs fresh (incumbency dies
   with its intention — the anti-perseveration boundary; measured
   twin without it: a 517-frame lock).
4. **Given** progress pinned ≥ 0.995 (awaiting the world's own
   confirmation), **Then** the intention still counts as advancing.

### User Story 2 - Existing users are untouched (Priority: P1)

Defaults (`commit_kappa=0.0`, `explore_defers_holds=False`) are
bit-exact with v2.0.0 behavior: no value perturbation, no RNG-stream
change, the byte-frozen T1–T6 suite green.

## Requirements *(mandatory)*

- **FR-001**: `commit_kappa: float = 0.0` and
  `explore_defers_holds: bool = False`, keyword-only, on
  `CompletionItchPolicy`; `RecipePolicy` passes both through.
- **FR-002**: `commit_kappa` must be finite and ≥ 0 (ValueError).
- **FR-003**: Off means off — 0.0/False add zero float perturbation
  (`+0.0` never applied: guarded) and identical RNG consumption.
- **FR-004**: The incumbency bonus applies only when the candidate
  equals the previous EMITTED action (random path included) and the
  intention is advancing.
- **FR-005**: Pure policy arithmetic — no engine, persistence, or
  observation-contract changes.

## Success Criteria *(mandatory)*

- **SC-001**: 25 unit tests green (`test_completion_itch_policy.py`),
  covering the knife-edge hold, the advancing requirement, deferral,
  the boundary, and validation.
- **SC-002**: Full gate green with defaults — byte-frozen suite
  included (the off-parity proof).
- **SC-003**: The free-roam promotion reading exists: both
  N2/N3-committed arms first-ate unaided faster than any
  pre-commitment life (573 / 1,146 vs 1,119 best-with-steering), and
  the gate-free arm sustained 99.3% fed over 100,501 steps
  (native-survival amendment-2/3 readings).

## Measured provenance

Research topic the-last-crack (episode 0101, design 0014): L1 value
trace (release-margin attribution), L2 3-repeat parked pair (10-vs-0
breaks, chain at step 333), L3 gate. Operating point: κ_c = 0.1 —
above the largest measured flip margin (0.069).
