# Implementation Plan: Stage-Conditional Selection

**Branch**: `047-stage-selection` | **Date**: 2026-08-30 | **Spec**: [spec.md](spec.md)

## Summary

The ladder's last rung, the 040–046 pattern: two keyword-only
constants on `RecipePolicy` (`stage_indices=()` off-by-default,
`stage_tolerance=1/128`), a hard eligibility filter in recipe
selection — a recipe is selectable only where its demonstrated
stage trajectory stood within tolerance of the current observation
— composing with place-keyed futility as one law (stage-matched AND
unpoisoned), one watch counter, no storage changes. Surface v2.5.0
(inventory params, Doc 0008 note, Doc 0010 mechanism, Doc 0011
tolerance row, design 0021 rung-3/ladder-complete propagation,
CHANGELOG, pyproject).

## Technical Context

Python ≥3.12 (repo venv), numpy only — no new dependencies. Pure
policy mechanics (FR-010): no engine, persistence,
observation-contract, anatomy, or storage changes. Touches:
`src/pra/action/recipe.py` (params + validation + `_stage_matched`
helper + the filter in `_select_recipe` + counter + docstrings),
`tests/unit/test_recipe.py`, `tests/contract/surface_inventory.py`
(two params on the `RecipePolicy` row), Doc 0008 (row + 2.5.0
note), Doc 0010 (mechanism paragraph), Doc 0011
(`stage_tolerance` row), `hq/02-DESIGN/0021-the-long-carry.md`
(rung 3 shipped — the ladder complete, the arena revival
unblocked), `CHANGELOG.md` ([2.5.0]), `pyproject.toml` (2.4.0 →
2.5.0), CLAUDE.md speckit pointer.

## Constitution Check

- **I. Reference-preserving**: PASS — `stage_indices=()` (default)
  short-circuits every stage read; three-arm off-parity test
  (default, explicit empty, armed-always-matching) pins identical
  action streams and RNG states; T1–T6 untouched.
- **II. Honest measurement**: PASS — provenance carried with
  numbers (the declared laps sense inert at n = 8 zero–zero,
  episode 0120); the feature's bars are deterministic eligibility
  behaviors; the walking question is explicitly the arena's.
- **III. Diagnose before fixing**: PASS — the diagnosis is 0120's
  mechanism trail (a sense reaches selection only through terminal
  drive value; the world's reset zeroes it there); the fix routes
  the sense to selection directly and hard, bypassing the measured
  inert pathway rather than extending it.
- **IV. Research gates**: PASS — the gated ladder's last rung; no
  new value arithmetic, no learned structure, no policy shape
  beyond the eligibility set (the 0020/0021 caution); finer forms
  (pointer-local matching, stage-aware pointing) recorded as
  arena-motivated successors, not built.
- **V. Instrument panel**: N/A — no new world.
- **VI. All-green gate**: the working rule.

Post-design re-check: PASS (no new deps, additive only, no
violation rows — Complexity Tracking empty).

## Design decisions (phase-0 research, consolidated)

1. **Hard eligibility, not a value bonus.** *Decision*: an
   unmatched recipe is excluded from the argmax outright.
   *Rationale*: design 0021's own wording ("modulates WHICH recipe
   is eligible, not just which terminal is valuable"), and the
   soft pathway is precisely what 0120 measured inert — a bonus
   would need a dial calibrated against drive value with no
   measurement behind it. *Alternative rejected*: additive
   stage-affinity term — unmeasured arithmetic on the value path,
   the exact shape the standing caution forbids.
2. **Any-step matching against the demonstrated trajectory.**
   *Decision*: eligible iff SOME stored step matches the current
   observation on EVERY declared channel within tolerance.
   *Rationale*: the demonstration already carries its context — no
   new storage (FR-008), no segmentation, no learning; a
   multi-stage demonstration (the lap walked at counts 0–2) is
   eligible across exactly its demonstrated span. *Alternatives
   rejected*: terminal-stamp matching (rebuilds 0120's failure —
   the reset-zeroed terminal IS the inert stamp);
   pointer-local matching (finer, plausibly better on drifting
   stages, but an unforced guess the arena should motivate —
   recorded as successor).
3. **Filter placement and the counter.** *Decision*: inside
   `_select_recipe`'s loop, poison check first, then stage;
   `stage_filtered_events` increments once per selection step on
   which the stage filter removed an unpoisoned recipe.
   *Rationale*: eligibility is a symmetric AND (FR-007) so order
   only defines the counter's "otherwise-eligible" honestly; the
   no-eligible path reuses the existing `None` → inert-parent
   route, which rung 1's `_subgoal is not None` guard already
   keeps from accruing stall (FR-006/SC-004 fall out with zero new
   code).
4. **Tolerance as a declared quantum, defaulting to 1/128.**
   *Decision*: one scalar half-width for all declared channels.
   *Rationale*: the `completion_threshold` precedent — the repo's
   smallest sensed quantum; discrete scaled counters match exactly
   under float representation, coarser senses declare wider.
   *Alternative rejected*: per-channel tolerances — surface weight
   with no motivating world; a world needing them can declare
   scaled channels instead.
5. **Version 2.5.0, additive minor; the ladder closes.** Inventory
   and Doc 0008 rows; Doc 0010 owns the mechanism prose; Doc 0011
   gains a `stage_tolerance` row beside `completion_threshold`
   (`stage_indices` is anatomy knowledge like `position_indices`,
   not a dial); design 0021 marks rung 3 shipped and the ladder
   complete — the arena revival becomes unblocked as the next
   research act.

## Source layout

- `src/pra/action/recipe.py` — `RecipePolicy.__init__` gains
  `stage_indices: tuple[int, ...] = ()` and
  `stage_tolerance: float = 1.0 / 128.0` (validated: integral
  indices ≥ 0, finite tolerance ≥ 0, ValueError); counter
  `stage_filtered_events = 0`; helper
  `_stage_matched(ctx, recipe) -> bool` (any step within tolerance
  on every declared channel); `_select_recipe` gains the guarded
  filter after the poison check and the once-per-step counter
  increment; class + module docstrings gain the rung-3 paragraph.
- `tests/unit/test_recipe.py` — new cases: constructor validation
  (FR-002); three-arm off-parity with counter-zero assertion
  (FR-003/US2); the partition sweep (SC-002/US1.1–2): lap process
  recipe spanning three stage values vs. a higher-worth gate
  recipe at a fourth — selection follows the demonstrated
  partition, the higher-worth out-of-context recipe never
  selected, eligibility at every demonstrated span point;
  tolerance boundary exact-at, fails-just-beyond (US1.4);
  never-demonstrated context → parent action-stream identity and
  zero stall accrual with futility armed (US1.3/SC-004/FR-006);
  the composition sweep (SC-003/US3): stage-matched recipes at
  distinct places through poison/expiry while the stage moves —
  eligible set equals stage-matched ∩ unpoisoned at every step,
  poison-expired-but-stage-moved stays out; process/acquisition
  twin eligibility (US3.3); `stage_filtered_events` increments
  exactly when an unpoisoned recipe is removed (FR-009).
- `tests/contract/surface_inventory.py` — `stage_indices`,
  `stage_tolerance` appended to the `RecipePolicy` row.
- Docs: Doc 0008 row + [2.5.0] release note; Doc 0010 mechanism
  paragraph; Doc 0011 `stage_tolerance` row; design 0021 rung 3 +
  ladder-complete note; CHANGELOG [2.5.0]; pyproject 2.5.0;
  CLAUDE.md speckit pointer → this plan.

## Complexity Tracking

None — additive, pattern-following (the seventh consecutive
feature on this seam; closes the 0021 ladder).
