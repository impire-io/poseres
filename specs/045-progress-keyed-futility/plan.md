# Implementation Plan: Progress-Keyed Futility

**Branch**: `045-progress-keyed-futility` | **Date**: 2026-08-29 | **Spec**: [spec.md](spec.md)

## Summary

Promote the measured futility mechanism (the-long-carry, episode
0120; design 0021 rung 1) to product, the feature-040/041/042/043
pattern: two additive keyword-only constants on `RecipePolicy`
(`futility_k=0` off-by-default, `futility_w=800`), place-keyed
poison over the quantized subgoal the pointer stalls at, eligibility
filtering in recipe selection, clean-peek revival, two bounded watch
counters. Surface v2.3.0 (inventory rows, Doc 0008 release note,
Doc 0010 mechanism paragraph, Doc 0011 dial rows, design 0021
rung-1 propagation, CHANGELOG, pyproject).

## Technical Context

Python ≥3.12 (repo venv), numpy only — no new dependencies. Pure
policy mechanics (FR-010): no engine, persistence, observation
contract, or anatomy changes; futility state is policy-side and not
snapshot state (the feature-041 recipe-state assumption, restated in
the spec). Touches: `src/pra/action/recipe.py` (the mechanism),
`tests/unit/test_recipe.py` (behavior + off-parity + validation),
`tests/contract/surface_inventory.py` (two param rows), Doc 0008
(inventory + 2.3.0 note), Doc 0010 (mechanism paragraph), Doc 0011
(dial rows), `hq/02-DESIGN/0021-the-long-carry.md` (rung 1 shipped),
`CHANGELOG.md` ([2.3.0]), `pyproject.toml` (2.2.0 → 2.3.0),
CLAUDE.md speckit pointer. `CompletionItchPolicy` is untouched —
futility is recipe-layer mechanics, not itch arithmetic.

## Constitution Check

- **I. Reference-preserving**: PASS — additive keyword-only params,
  `futility_k=0` default disables every code path (no value
  arithmetic, no RNG draw, no state mutation); the byte-frozen
  T1–T6 suite never constructs `RecipePolicy` and stays untouched;
  an off-is-off test pins identical action streams (the 041/042/043
  parity pattern).
- **II. Honest measurement**: PASS — every quantitative claim in
  spec and docs carries its measured provenance (4,672-step press,
  556-event thrash, K=200/W=800 prototype [measured], episode
  0120); the feature's own bars are deterministic unit behaviors,
  no spread claims made.
- **III. Diagnose before fixing**: PASS — the mechanism arrives
  with its diagnosis trail already run at rig level: hypothesis
  (stalled pointer feeds nothing), discriminating experiments (two
  refuted forms with numbers), principled fix (place-keying),
  recorded in episode 0120/design 0021.
- **IV. Research gates**: PASS — this IS the gated ladder's rung 1;
  no showcase spend rides on it. Reviving the larder arena stays a
  research act under design 0021, outside this feature's gate.
- **V. Instrument panel**: N/A — no new world.
- **VI. All-green gate**: the working rule — ruff format/check +
  full pytest, signed commits.

Post-design re-check: PASS (no new deps, additive only, no
violation rows — Complexity Tracking empty).

## Design decisions (phase-0 research, consolidated)

1. **Eligibility = pure pointed-place check per candidate.**
   *Decision*: `_select_recipe` skips any recipe whose pointer
   would currently resolve (nearest-step-plus-one, computed
   side-effect-free) to a poisoned place; the selected recipe then
   runs the existing `_point_subgoal` so `advance_events` /
   `out_of_context` semantics are unchanged. When no poison is
   live, the check short-circuits — zero extra work on the common
   path. *Rationale*: poison must stick to the place through each
   recipe's CURRENT pointer (spec US3.3) — identity-keyed filters
   are the two refuted forms. *Alternatives rejected*: per-recipe
   erosion (boundary thrash, 556 events [measured]); per-recipe
   hysteresis (cohort fallback [measured]); layer-wide gate (the
   prototype's degenerate case — loses the elsewhere-recipe
   liveness of US3.2).
2. **Place key = grid-rounded scaled position.**
   *Decision*: `(round(x), round(z))` of the subgoal position in
   scaled (block-grain) coordinates, from the existing
   `position_indices`/`position_scale`. *Rationale*: exact, stable
   keys; adjacent stations stay distinct places (spec edge case).
   *Alternative rejected*: radius matching (Chebyshev ≤ r) —
   overlapping identities recreate the boundary-ambiguity class
   that thrashes.
3. **Stall bookkeeping = one register, not a dict.**
   *Decision*: a single `(place, count)` register — only one place
   is pointed at per step, so per-place counts cannot accumulate
   in parallel. Same place + no pointer advance → count += 1;
   advance or place change → re-key, count restarts. At
   `futility_k` → poison the place for `futility_w`, clear the
   register, `fatigue_events += 1`. *Rationale*: O(1), bounded by
   construction, and FR-004's semantics exactly. *Alternative
   rejected*: dict of stall counts — stale entries for abandoned
   places, implies concurrent stalls that cannot occur.
4. **The poison clock counts selection steps, not followed steps.**
   *Decision*: a monotone per-selection counter; poison = place →
   expiry step; expired entries dropped at selection start
   (`revive_events += 1` each). *Rationale*: while poisoned the
   layer is often inert (wander phase) — a followed-steps clock
   would never tick and poisons would never expire. *Alternative
   rejected*: wall/engine time — the policy has no clock and needs
   none.
5. **Version 2.3.0, additive minor.** The 040-pattern: params into
   the surface inventory row, Doc 0008 note, dial rows in Doc 0011,
   mechanism prose in Doc 0010 (the recipe doc this touches),
   propagation into design 0021 (rung 1 status). Defaults K=200 /
   W=800 documented as the prototype-of-record dials [measured],
   shipped default off per Constitution I.

## Source layout

- `src/pra/action/recipe.py` — `RecipePolicy.__init__` gains
  `futility_k: int = 0, futility_w: int = 800` (validated:
  integral, `futility_k >= 0`, `futility_w > 0`, ValueError);
  state `_futility_step: int`, `_poisons: dict[place, int]`,
  `_stall: tuple[place, int] | None`; counters `fatigue_events`,
  `revive_events`. A pure `_pointed_place(ctx, recipe)` helper;
  `_select_recipe` gains the poison filter; `select_action` gains
  the guarded (`if self.futility_k:`) tick: expire poisons → track
  stall on the followed pointer → poison at K. Module docstring
  gains the measured-provenance paragraph (episode 0120).
- `tests/unit/test_recipe.py` — new cases: off-is-off action-stream
  parity (defaults vs. pre-045 arithmetic, shared RNG seed);
  stall→poison at exactly K; advance-at-K resets (US1.4); cohort
  dies together, zero fallback presses (US3.1); elsewhere recipe
  unaffected (US3.2); poison sticks to place, recipe re-eligible
  through a new place (US3.3); revival after W is a clean peek —
  count restarts, re-poison takes K again (FR-007); all-poisoned
  degrades to parent (US1.2); no per-recipe futility state exists
  (FR-008); counters and state bounded (US4); constructor
  validation (FR-002).
- `tests/contract/surface_inventory.py` — `futility_k`,
  `futility_w` appended to the `RecipePolicy` row.
- Docs: Doc 0008 §inventory + release note; Doc 0010 mechanism
  paragraph; Doc 0011 dial rows (`futility_k`, `futility_w`, the
  measured operating point and the off default); design 0021
  feature-candidate 1 marked shipped with a pointer here;
  `CHANGELOG.md` [2.3.0]; `pyproject.toml` 2.3.0; CLAUDE.md
  speckit pointer → this plan.

## Complexity Tracking

None — additive, pattern-following (the fifth consecutive feature
on this exact seam).
