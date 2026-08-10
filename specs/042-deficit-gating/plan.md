# Implementation Plan: The Deficit Gate

**Branch**: `042-deficit-gating` | **Date**: 2026-08-10 | **Spec**: [spec.md](spec.md)

## Summary

Promote the measured deficit→value coupling (episodes 0083/0084) to
product, the feature-040/041 pattern: two additive keyword params on
`CompletionItchPolicy` (`deficit_index`, `deficit_kappa`), one
effective-weight helper used at both existing label read sites,
additive surface (v1.4.0), row-level closure reruns on both archived
bodies (Bar P1), timing-primary bars P2/P3 recorded in the
coupling-promotion topic, graduation to Doc 0010.

## Technical Context

Python 3.12, numpy only; no engine/persistence changes (pure policy
arithmetic, FR-005). Touches: `src/pra/action/policy.py` (params +
`_label_weight(obs)` helper + completion-read call site),
`src/pra/action/recipe.py` (ctor passthrough + selection reads the
helper), tests (parity/arithmetic/validation), surface inventory +
Doc 0008 + Doc 0005 + Doc 0010, pyproject 1.3.0 → 1.4.0.
Bit-exactness discipline: the helper reads the deficit channel only
when enabled; disabled returns `label_beta` unchanged (FR-003), and
the closure identity relies on `0.0 + κ·d ≡ κ·d` and
`min(max(1−e,0),1) ≡ max(0,1−e)` for e ∈ [0,1] (the instrument's
arithmetic). Constitution check: article I satisfied by the off-parity
RNG-state test; III by measured provenance (0083/0084) and the frozen
promotion bars; post-design re-check PASS (no new deps, additive
only).

## Source layout

- `policy.py`: keyword-only `deficit_index: int | None = None,
  deficit_kappa: float = 0.0`; validation per FR-004; helper
  `_label_weight(obs)`; the completion branch multiplies by the
  helper's value instead of `self.label_beta` directly.
- `recipe.py`: ctor passthrough; `_select_recipe` uses
  `self._label_weight(ctx.observation)`.
- Tests: cases into `tests/unit/test_completion_itch_policy.py`
  (off-parity incl. RNG state, weight arithmetic at e ∈ {1.0, 0.6,
  −0.2, 1.4}, validation errors) and `tests/unit/test_recipe.py`
  (selection-site gating, same-weight-both-sites).
- Closure: scratchpad runners `deficit_coupling.py` /
  `sample_field.py` re-run arms W1/T2 with the shipped params via a
  logging-only subclass; rows diffed field-by-field against
  `dc-arms-rows.json` / `sf-arms-rows.json`.

## Complexity Tracking

None — additive, pattern-following.
