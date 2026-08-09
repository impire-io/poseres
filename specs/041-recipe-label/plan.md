# Implementation Plan: The Recipe and the Label

**Branch**: `041-recipe-label` | **Date**: 2026-08-09 | **Spec**: [spec.md](spec.md)

## Summary

Promote the measured recipe-reach and E3.1 mechanisms to product, the
feature-040 pattern: additive keyword params on `CompletionItchPolicy`
(the label), a new `pra/action/recipe.py` (RecipeMemory + RecipePolicy —
the measured gate arithmetic verbatim, constants generalized to
constructor params), additive surface (v1.3.0), row-level closure rerun,
topic graduation to Doc 0010.

## Technical Context

Python 3.12, numpy only; no engine/persistence changes at all (policies
are injected; recipes are caller-kept state per spec assumption).
Touches: `src/pra/action/policy.py` (label params), new
`src/pra/action/recipe.py`, tests (2 new unit files), surface inventory +
Doc 0008 + Doc 0005 §4.5, pyproject 1.3.0. Constitution check: article I
satisfied by label-off/recipe-off bit-exactness tests; III by the
measured provenance (episodes 0075/0076); VI the working rule.
Post-design re-check: PASS (no new deps, additive only).

## Source layout

- `policy.py`: `label_index: int | None = None, label_beta: float = 0.0`
  keyword-only; completion branch gains the one guarded line.
- `recipe.py`: `Recipe` (frozen dataclass: `steps: tuple[np.ndarray,...]`,
  `terminal: np.ndarray`), `RecipeMemory(pocket_index, label_index=None)`
  with `.add_demonstration(seq) -> Recipe | None` and `.recipes`;
  `RecipePolicy(CompletionItchPolicy)` ctor adds `memory, lambda_r,
  position_indices=(0, 1), position_scale=64.0`; overrides
  `select_action` to pick the active recipe + subgoal then delegates to
  the parent arithmetic with `potential_of` bound to the subgoal hold;
  counters `advance_events`, `out_of_context`.
- Tests: `tests/unit/test_recipe.py`, label cases into
  `tests/unit/test_completion_itch_policy.py`.

## Complexity Tracking

None — additive, pattern-following.
