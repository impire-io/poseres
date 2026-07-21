# Feature Specification: Honest Primitives — Crafting as a Ladder, Not a Button

**Feature Branch**: `031-honest-primitives`
**Created**: 2026-07-21
**Status**: Draft
**Input**: User description: "Honest primitives for the C1 body: remove the macro craft actions; add held-class selection and a sensed 2x2 staging grid (put/take/result) so crafting is a learnable ladder of one-step consequences that emerges - or honestly does not - rather than a button"

## Overview

Feature 030 shipped `craft_planks` and `craft_sticks` as action presets.
The owner's challenge, accepted in full (2026-07-21): those are **skills
wearing primitives' clothing**. In Minecraft's own mechanics crafting is
a sequence over a lower interface — select a material, stage it in a
grid, observe what the grid offers, take it — and its availability is
epistemically gated (you figure out what wood is for) and sometimes
structurally gated (a crafting table before the 3×3 recipes exist at
all). A one-button craft makes the body answer the question the brain
was supposed to be asked, and makes any spectator over-credit the brain.

This feature replaces the two macros with an **honest micro-primitive
set** whose every rung is individually learnable because every rung is
*sensed*:

- **`hold_next`** — cycle the held material class (none → blocks →
  logs → planks → sticks → none). Selection becomes the brain's job:
  `place_ahead` now places the *held* class (if placeable) instead of
  auto-picking, and the grid receives the *held* class.
- **`grid_put`** — move one item of the held class into the body's 2×2
  staging grid (column-first fill, a fixed anatomical convention like
  "ahead is the column nearest yaw"). No-op if nothing suitable held or
  the grid is full.
- **`grid_take`** — return the grid's contents to the pocket (the undo).
- **`take_result`** — collect what the grid currently offers, consuming
  the staged inputs; no-op if the grid offers nothing.
- **Two new senses**: `hand` (one-hot held class, width 4) and `grid`
  (width 5: staged count, staged logs, staged planks, result-is-planks,
  result-is-sticks). The result channels are the game's own honesty —
  vanilla shows you what the grid yields before you take it — so
  putting a log in the grid has a *next-tick visible consequence* long
  before any craft completes.

The recipe rules live in the world, identically in both bridges (a log
anywhere → planks; two planks in a column → sticks — vanilla's own
rules for the curated classes). What the brain must learn is unchanged
in kind but now honest in granularity: what each primitive does, and
whether the rungs chain into crafting. **Emergence is the experiment**:
the multi-week run measures whether the ladder gets climbed, and a
never-climbed ladder is an honest null about current capability — the
owner's stated preference over a flattering button.

C1 grows to obs 28 / actions 12 (dims: pose5 vitals2 env4 blocks3
inventory5 hand4 grid5; actions: the eight of 027 unchanged in the
same order, then hold_next, grid_put, grid_take, take_result). The
feature-027 body (14/8) remains one flag away; the 030 macro body is
removed rather than kept as a third variant — it never ran a long run,
and the reversal condition now points at the 14/8 legacy directly.

**One stated pragmatic seam**: live, the 2×2 staging grid is *body
furniture* — the bridge stages materials in a virtual grid whose
material flows in and out of the real inventory are real, and
`take_result` executes the real craft. The grid's recipe read mirrors
vanilla exactly; the server never sees partial stagings. This is the
same class of body convention as "dig targets the block ahead" and is
recorded in the contract, not hidden.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Selection is the brain's job (Priority: P1)

The bot cycles what it holds and both placement and staging follow the
held class. The observer sees the `hand` channels flip as it cycles,
and `place_ahead` place planks *because planks were held* — or no-op
because nothing was.

**Why this priority**: held-class selection is the primitive every
other new primitive routes through; it also removes 030's last
mini-macro (auto-pick placement).

**Acceptance Scenarios**:

1. **Given** planks and blocks in the pocket, **When** `hold_next`
   cycles, **Then** the `hand` one-hot steps none → blocks → logs
   (skipping is not allowed — empty classes still get a beat: the
   cycle order is fixed anatomy) and placement consumes exactly the
   held class when placeable.
2. **Given** nothing held, **When** `place_ahead` or `grid_put`
   executes, **Then** the world and pocket are unchanged.

---

### User Story 2 - The grid is a sensed ladder (Priority: P1)

The bot stages a log; the grid's result channels light up *planks* on
the next tick — before anything is crafted. It takes the result; the
pocket gains planks and the grid empties. Every rung of
dig → hold → stage → observe → take is a one-step sensed consequence.

**Why this priority**: the sensed intermediate state is the load-bearing
design: it is what turns "hierarchy must be learned" from a leap into a
ladder the current frames can in principle climb.

**Acceptance Scenarios**:

1. **Given** a held log, **When** `grid_put` executes, **Then** the
   grid channels show one staged item and result-is-planks on the next
   tick.
2. **Given** result-is-planks showing, **When** `take_result` executes,
   **Then** the pocket gains 4 planks, the log is consumed, the grid
   empties, and the result channels clear.
3. **Given** two planks staged (column-first fill), **Then**
   result-is-sticks shows; taking yields 4 sticks for 2 planks.
4. **Given** a nonsense staging (e.g. one plank alone, or blocks),
   **Then** no result shows and `take_result` no-ops.
5. **Given** a staged grid, **When** `grid_take` executes, **Then**
   everything returns to the pocket exactly.

---

### User Story 3 - The macros are gone and nothing else moved (Priority: P2)

`craft_planks`/`craft_sticks` no longer exist; the first eight actions
are byte-for-byte the 027 set in the same order; the 14/8 legacy body
still constructs; the dashboard shows the new groups and labels with
zero dashboard changes.

**Acceptance Scenarios**:

1. **Given** the new anatomy, **Then** obs 28 / actions 12, action ids
   0–7 unchanged from 027, and `c1_anatomy(crafting=False)` is still
   exactly 14/8.
2. **Given** a fake-mode run, **Then** byte-identity and exact resume
   hold with held + grid in the state seam (mid-staging included).

---

### Edge Cases

- **Grid full** (4 staged): `grid_put` no-ops. **Pocket empty of the
  held class**: `grid_put` no-ops; `hold_next` still cycles (holding a
  class you have none of is a valid, sensed state — hand shows the
  class, counts show zero).
- **take_result with no result**: no-op, one tick consumed.
- **Mixed stagings** (log + plank): no result — vanilla agrees.
- **Snapshot mid-staging**: held class and grid contents travel in the
  fake state seam byte-exactly; live resume is class 4 as always
  (the real inventory is wherever the server says; the virtual grid
  restores from the snapshot and its next material flow reconciles).
- **The live virtual grid vs reality**: if the real inventory lacks the
  staged material at `take_result` time (external interference), the
  craft no-ops and the grid re-syncs from the real inventory — the
  world is always the authority.
- **Old snapshots**: 19-dim (030) and 14-dim snapshots do not resume
  into 28-dim configs — loud config check, stated; no long run has
  started.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The action set MUST be exactly the eight 027 actions (ids
  0–7, unchanged order) plus `hold_next` (8), `grid_put` (9),
  `grid_take` (10), `take_result` (11). The macro craft actions MUST be
  removed from the contract and both bridges.
- **FR-002**: The channel set MUST gain `hand` (width 4, one-hot held
  class) and `grid` (width 5: staged/4, staged-logs/4, staged-planks/4,
  result-is-planks, result-is-sticks); `inventory` keeps slice [14:19]
  with its fifth element redefined as *held class is placeable*.
- **FR-003**: `hold_next` MUST cycle none → blocks → logs → planks →
  sticks → none regardless of counts; `place_ahead` and `grid_put` MUST
  act on the held class only (placeable classes: blocks, planks) and
  no-op otherwise. This replaces 030's auto-pick placement.
- **FR-004**: The grid MUST fill column-first (slots top-left,
  bottom-left, top-right, bottom-right), hold at most 4 items, and
  compute its result by vanilla's rules for the curated classes: any
  staged log → planks (4 per log taken); two planks in one column and
  nothing else → 4 sticks. `take_result` MUST consume exactly the
  recipe's inputs; `grid_take` MUST return contents exactly.
- **FR-005**: Both bridges MUST implement identical semantics; the live
  bridge's grid is declared body furniture (virtual staging, real
  material flows, real craft at `take_result`) in the contract; the
  world stays the authority on every material count.
- **FR-006**: Fake-mode class-1 byte-identity and exact resume MUST
  hold with held + grid in the state seam.
- **FR-007**: Zero brain-side edits beyond the anatomy declaration;
  the dashboard MUST pick up the new groups/labels with no changes
  (the 029 metadata path).
- **FR-008**: The deterministic gate MUST prove the full honest ladder
  step-by-step (dig log → hold → stage → observe result → take →
  re-hold → stage ×2 → take → place), every rung's consequence on the
  next tick.
- **FR-009**: A **pre-registered pilot** MUST run and publish its
  numbers: 8 paired seeds, honest body (28/12) vs legacy (14/8), same
  harness as 030's. Bars: (a) improvement > 0 in ≥ 6/8 at 28/12.
  Everything else is **context, no bars** — grid actions taken,
  result-sense activations, rungs reached, chains completed, and the
  paired improvement delta — the 030 pilot's lesson applied: stochastic
  engagement at pilot budgets measures world density and luck, not
  capability, and the emergence question belongs to the long run.

### Key Entities

- **Held class**: the brain-selected material class (or none); sensed
  one-hot; the routing input for placement and staging.
- **Staging grid**: body furniture, 4 slots, column-first; sensed
  occupancy + result; the ladder's middle rungs.
- **Result offer**: what the grid would yield now — vanilla's own
  pre-craft honesty, sensed as two bits.
- **The ladder**: dig → hold → stage → observe → take → … — each rung a
  one-step sensed consequence; climbing it is the emergence question.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: The full honest ladder is proven deterministically in the
  gate with every rung's next-tick consequence asserted (FR-008).
- **SC-002**: Fake and live bridges agree: the live smoke stages a real
  log, sees result-is-planks, takes it, and the real server inventory
  shows 4 planks — exact arithmetic over the wire.
- **SC-003**: Byte-identity + exact resume hold mid-staging; the
  byte-frozen reference suite is untouched (zero core edits).
- **SC-004**: The Brain tab shows `hand` and `grid` groups and the four
  new action labels with zero dashboard-code changes.
- **SC-005**: Pilot bar (a) decided and every context number published
  in the journey episode, flattering or not.
- **SC-006**: The macro craft actions exist nowhere in the contract,
  bridges, or anatomy after this feature.

## Assumptions

- **The crafting table is the named next rung, not this feature**: the
  3×3 grid and its placement-prerequisite structure arrive only if the
  2×2 ladder shows any climbing. Recorded as the successor experiment.
- **Curated classes stay**: four material classes; the grid only stages
  those. Honesty here is about *granularity of action*, not item-world
  completeness.
- **Column-first fill is anatomy, not knowledge**: a fixed motor
  convention (like "ahead"), stated in the contract; it makes the stick
  recipe reachable without slot-addressing actions (which would add 4+
  actions for no additional learnable structure in a 2×2).
- **Reversal condition (supersedes 030's)**: if the multi-week run
  shows the grid primitives effectively unused (no rungs beyond
  hold/stage noise) *and* improvement materially below the legacy
  pilot arm, the run falls back to `c1_anatomy(crafting=False)` and
  the body/hierarchy question returns to research with the run's
  engagement data as its opening evidence. A never-climbed ladder is
  itself a publishable finding about current capability — the owner's
  stated preference over a flattering macro.
