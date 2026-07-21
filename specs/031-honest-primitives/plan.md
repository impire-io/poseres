# Implementation Plan: Honest Primitives

**Branch**: `031-honest-primitives` | **Date**: 2026-07-21 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/031-honest-primitives/spec.md`

## Summary

Remove the 030 macro-craft presets; add `hold_next` + the sensed 2×2
staging grid (`grid_put`/`grid_take`/`take_result`) and the `hand`/`grid`
channels; make placement held-based. C1 default becomes obs 28 /
actions 12 (action ids 0–7 unchanged from 027); `crafting=False` stays
the exact 14/8 legacy. Zero brain-side edits beyond the anatomy
declaration (the 030-proven pattern); the contract is amended in place
in the 027 file with the 031 delta doc carrying rationale.

## Technical Context

Same stack and constraints as feature 030 (its plan.md §Technical
Context applies verbatim): Python ≥3.12 + Node bridge, no new deps,
FakeBridge carries the gate, live smoke vs the 1.21.11 server.
Deltas only:

**Fake state seam**: `_World` grows `held` (class name or None) and
`grid` (ordered list ≤4 of class names, column-first); both travel in
`state_dict`/`load_state`.
**Live bridge**: the staging grid is a bridge-side virtual structure
(declared body furniture in the contract); `grid_put` decrements
nothing (staging is a reservation over the real inventory), the grid's
result mirrors vanilla's rules, and `take_result` executes the *real*
craft (`bot.recipesFor` + `bot.craft`) then re-syncs; if the real
inventory can no longer cover the staging, the craft no-ops and the
grid re-syncs from reality — the world stays the authority (spec edge
case).
**Anatomy**: sensors + `hand`(4) + `grid`(5); presets: the 027 eight +
four grid primitives; macro presets deleted.
**Scale**: obs 28 / actions 12 — the pilot quantifies the tax again
(FR-009; one bar, context rows otherwise).

## Constitution Check

- **I — PASS**: no `src/pra/core` edits; anatomy/bridges/tests only;
  reference suite untouched.
- **II — PASS**: pilot bar + context design pre-registered in spec
  FR-009 *with the 030 lesson encoded* (no stochastic-engagement bar);
  numbers published either way.
- **III — applied**: the 030 pilot's diagnosis (contact = two rarities)
  directly shaped this design (sensed intermediate state; engagement
  moved to the long run's question).
- **IV — decision recorded**: the owner's argument (primitives must be
  honest; hierarchy is to be learned) is the direction decision,
  argued adversarially in-conversation (the never-climbed-ladder risk
  stated at full strength), teach-back inherent in the owner making
  the argument himself; superseding reversal condition in the spec.
- **V — PASS**: the fake sketch gains the same grid deterministically;
  ground truth, steppable time, byte-identity all preserved.
- **VI — applies**: full gate, signed commits.

**Post-design re-check: PASS.**

## Project Structure

```text
specs/031-honest-primitives/
├── plan.md  spec.md  checklists/  tasks.md  pilot-results.md (after T-pilot)
└── contracts/contract-amendment.md   # delta applied to specs/027 contract

src/pra/anatomy/minecraft/
├── anatomy.py        # hand+grid sensors, 4 grid presets, macros deleted; 28/12
└── fake.py           # held/grid state, held-based place, grid mechanics + channels

examples/minecraft/bridge/bridge.js  # hand/grid channels, virtual staging,
                                     # real craft at take_result, held-based place

tests/
├── contract/test_minecraft_contract.py   # ladder test replaces macro chain test;
│                                         # held-based place; mid-staging state seam
├── integration/test_minecraft_fake_run.py # runs at 28/12 (constants follow)
└── unit/test_anatomy_meta.py             # 28/12 groups/labels; legacy unchanged
```

**Structure Decision**: identical boundaries to 030; the 027 contract
file is amended in place again (this feature is the next spec change).

## Design decisions

1. **Sensed intermediates are the load-bearing piece**: result-is-planks
  /result-is-sticks are vanilla's own pre-craft display — world truth,
  not smuggled knowledge; they give `grid_put` a next-tick consequence.
2. **Column-first fill** is a motor convention (anatomy), keeping the
  stick recipe reachable without 4 slot-addressing actions that add no
  learnable structure in a 2×2.
3. **Held-based placement** removes 030's auto-pick (itself a
  mini-macro): all selection is the brain's.
4. **Virtual staging live** (stated in contract): real click
  choreography over the player-inventory grid is fragile under
  mineflayer; the virtual grid with real material flows and a real
  craft at `take_result` is behaviorally identical at the channel level
  and byte-mirrored by the fake. Declared, not hidden.
5. **Pilot**: bar (a) learning ≥6/8 at 28/12 only; engagement numbers
  (grid actions, result activations, rungs, chains) and the paired
  delta are context — the 030 lesson.

## Complexity Tracking

No violations; table not needed.
