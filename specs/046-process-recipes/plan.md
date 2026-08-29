# Implementation Plan: Process Recipes

**Branch**: `046-process-recipes` | **Date**: 2026-08-29 | **Spec**: [spec.md](spec.md)

## Summary

Rung 2 of the design-0021 ladder, the 040–045 pattern: one
keyword-only opt-in on `RecipeMemory` (`process=False`) opens a
second storage door — a gainless demonstration with a strictly
positive label stores as a process recipe, terminal chosen by the
EXISTING max-label rule, `Recipe` gaining an inspectable
`process` mark. `RecipePolicy` is untouched: worth is the shipped
label/deficit grammar (features 041/042), futility (045) and the
hold operate on process recipes with zero process-conditional
branches. Surface v2.4.0 (inventory param, Doc 0008 note, Doc 0010
vocabulary paragraph, design 0021 rung-2 propagation, CHANGELOG,
pyproject).

## Technical Context

Python ≥3.12 (repo venv), numpy only — no new dependencies. Pure
memory-vocabulary mechanics (FR-008): no engine, persistence,
observation-contract, anatomy, or policy changes; recipes stay
caller-kept policy-side state. Touches:
`src/pra/action/recipe.py` (`Recipe.process` field,
`RecipeMemory(process=…)` + the process branch in
`add_demonstration`), `tests/unit/test_recipe.py`,
`tests/contract/surface_inventory.py` (one param on the
`RecipeMemory` row), Doc 0008 (row + 2.4.0 note), Doc 0010
(vocabulary paragraph), `hq/02-DESIGN/0021-the-long-carry.md`
(rung 2 shipped), `CHANGELOG.md` ([2.4.0]), `pyproject.toml`
(2.3.0 → 2.4.0), CLAUDE.md speckit pointer. No Doc 0011 change —
`process` is a mode, not a dial.

## Constitution Check

- **I. Reference-preserving**: PASS — `process=False` (default)
  short-circuits to the exact v2.3.0 storage rule; the sharp case
  (label users already feed gainless labeled sequences, which must
  keep storing NOTHING by default) is pinned by its own test; the
  `Recipe.process` field defaults so every existing construction
  site is unchanged; T1–T6 never touch recipes.
- **II. Honest measurement**: PASS — the measured absence (0 of 15
  lap demonstrations stored, episode 0120) is the provenance and
  its closure is a deterministic storage test (SC-002); no
  behavioral spread claims are made — the walking question is
  explicitly the arena revival's, not this gate's.
- **III. Diagnose before fixing**: PASS — the diagnosis is episode
  0120's isolated gap (a taught path unstorable as behavior); the
  fix opens the narrowest door that closes it, reusing measured
  worth machinery rather than inventing any.
- **IV. Research gates**: PASS — rung 2 of the gated ladder; the
  standing 0020/0021 caution is honored by adding NO new value
  arithmetic and NO policy shape: worth-by-label is a
  [mechanism-argument] promotion of measured pathways (episodes
  0076, 0080, 0083–0085), recorded as such in the spec.
- **V. Instrument panel**: N/A — no new world.
- **VI. All-green gate**: the working rule — full gate, signed
  commits.

Post-design re-check: PASS (no new deps, additive only, no
violation rows — Complexity Tracking empty).

## Design decisions (phase-0 research, consolidated)

1. **A second door, not a rewrite.** *Decision*: the acquisition
   path in `add_demonstration` stays verbatim; only sequences it
   rejects (no gain) and only under `process=True` are considered
   for process storage, requiring a strictly positive label and
   using the same max-label/latest-tie terminal rule.
   *Rationale*: FR-005's bit-exactness for every gainful sequence
   falls out structurally; one terminal rule keeps one vocabulary.
   *Alternative rejected*: unifying both doors into one
   label-first rule — would change stored terminals for existing
   gainful-labeled users (a constitution-I break).
2. **Explicit opt-in flag, not label-presence keying.**
   *Decision*: `process: bool = False`, keyword-only, ValueError
   when set without `label_index`. *Rationale*: feature-041 users
   already feed labeled sequences; keying off `label_index` alone
   would silently start storing for them (US2's sharp case).
   *Alternative rejected*: a separate `ProcessRecipeMemory` class
   — splits the vocabulary rung 3 must read, doubles the surface.
3. **Worth = the shipped grammar, zero policy delta.** *Decision*:
   no `RecipePolicy` change; a process terminal is priced by
   `drive_value_of(terminal) + weight · terminal[label]` exactly
   as any terminal. *Rationale*: the label-as-terminal-marker and
   deficit amplification are measured (24/24 transmission, episode
   0076; menu steering, 0080; the appetite, 0083–0085); design
   0021 calls the worth question "adjacent to the completion
   itch's existing grammar" and 0020/0021 forbid unmeasured shape.
   *Alternative rejected*: a process-specific worth dial —
   unmeasured arithmetic, exactly what the caution names.
4. **The mark is a field, not a subclass.** *Decision*:
   `Recipe.process: bool = False` (frozen dataclass, defaulted) —
   observability now, rung 3's hook later, no promised-param
   change (the `Recipe` row promises no params). *Alternative
   rejected*: an unmarked record — the arena's registered analysis
   and rung 3 would need to re-derive provenance the memory
   already knew.
5. **Version 2.4.0, additive minor.** Inventory row gains
   `process`; Doc 0008 note; Doc 0010 gets the vocabulary
   paragraph (it owns the recipe design); design 0021 rung 2
   marked shipped. No Doc 0011 entry: `process` is a mode switch,
   not an operating-point dial.

## Source layout

- `src/pra/action/recipe.py` — `Recipe` gains `process: bool =
  False`; `RecipeMemory.__init__` gains keyword-only
  `process: bool = False` with the `label_index` requirement
  (ValueError); `add_demonstration` gains the guarded process
  branch (no gains + `process` + max label > 0 → store marked
  recipe through the max-label terminal; else the existing
  `return None`). Module docstring gains the rung-2 provenance
  paragraph; `RecipeMemory`/class docstrings updated.
- `tests/unit/test_recipe.py` — new cases: default-off parity
  (gainless labeled → `None`, gainful byte-identical to the
  pre-046 rule) (US2.1/FR-001); ValueError on `process=True`
  without `label_index` (FR-002); process store with terminal =
  applauded obs, steps through it, marked process (US1.1/FR-003);
  the 0-of-15 closure — fifteen gainless end-applauded demos
  store fifteen recipes (SC-002); gainless unlabeled stores
  nothing even opted in (US1.3/FR-004); gainful identical with
  `process` on/off and unmarked (US1.4/FR-005); applause-at-first
  degenerate path (edge case); worth through the label weight —
  weight 0 leaves selection at drive order, weight > 0 elects the
  process recipe, deficit amplifies (US3/SC-004); one-vocabulary
  twin — identical step sequences stored via each door produce
  identical subgoal series, hold values, and futility counters
  through a stall-poison-revive cycle (SC-003/US4).
- `tests/contract/surface_inventory.py` — `process` appended to
  the `RecipeMemory` row.
- Docs: Doc 0008 row + [2.4.0] release note; Doc 0010 process
  paragraph; design 0021 candidate 2 marked shipped; CHANGELOG
  [2.4.0]; pyproject 2.4.0; CLAUDE.md speckit pointer → this
  plan.

## Complexity Tracking

None — additive, pattern-following (the sixth consecutive feature
on this seam; the smallest of them).
