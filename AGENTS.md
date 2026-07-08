# Agent guide for the PRA project

Durable instructions for any coding agent working in this repository.

## Orientation (read in this order)

1. `JOURNEY.md` — the narrative of the project so far: what was built, what was
   refuted, and why things are the way they are. Start here.
2. The current feature plan — pointed to by the SPECKIT block in `CLAUDE.md`
   (tech stack, structure, commands).
3. `design/00-README-index.md` — the system design map; `design/validate/` —
   the normative specs (PRA-01/PRA-02) and the evidence-trail documents
   (`*-DIAGNOSIS.md`).

## Maintaining JOURNEY.md (required)

Whenever you complete a feature, conclude a research investigation, or make a
load-bearing decision (a spec change, a criterion amendment, a refuted
hypothesis), **append or extend a chapter in `JOURNEY.md`** using the template
at its bottom, and update its "Where things stand" section. Record what
actually happened — including failures, reversals, and findings that
contradicted expectations. Commit it with the work it describes.

## Non-negotiable working rules

- **Quality gate before "done"** (all green, none skipped):
  `./.venv/bin/ruff format --check . && ./.venv/bin/ruff check . && ./.venv/bin/pytest -q`
- **Use the repo venv** (`./.venv/bin/python`); the system interpreter is
  PEP-668 managed. Sign commits.
- **The validated behavior is byte-frozen.** The T1–T6 suite under the pinned
  random baseline must reproduce the recorded reference values exactly
  (`tests/integration/test_baseline_unchanged.py` guards seed 1). New
  capability must be opt-in and leave existing modes' RNG stream, behavior, and
  serialized summaries untouched.
- **Honest measurement.** Report spreads, never a mean where a spread is
  required; a FAIL is data, shown with the numbers that explain it; criteria
  are amended openly (with the raw measurements recorded), never tuned quietly
  until green.
- **Diagnose before fixing.** For behavioral problems: hypothesis → cheap
  discriminating experiment → only then a principled fix, with the trail
  recorded in a `design/validate/*-DIAGNOSIS.md` document.
- **Reference-preserving parameter rules.** Scale-dependent constants ship as
  effective forms whose factors are exactly 1 at the validated reference scale
  (see PRA-01 §8.8 for the pattern).
- **Research experiments** live in the session scratchpad, not the repo; only
  their conclusions, documents, and principled code changes land in git.

## Feature workflow

New capabilities go through the Spec Kit flow (`/speckit-specify` → plan →
tasks → implement) on a numbered feature branch (`specs/NNN-name/`), merged to
`main` when the gate is green. Small hardening/research changes may land
directly with tests and spec propagation (see JOURNEY chapters 4 and 7 for
precedent). Propagate every behavioral change into the design docs it touches
(`design/0X-*.md`, PRA-01/PRA-02, Doc 07 for parameters).
