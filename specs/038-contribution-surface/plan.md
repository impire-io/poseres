# Implementation Plan: Contribution Surface

**Branch**: `038-contribution-surface` | **Date**: 2026-07-27 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/038-contribution-surface/spec.md`

## Summary

Ship the contributor on-ramp the roadmap's Phase D names: a root
CONTRIBUTING.md in the project's voice (seams, worked examples, dev
setup, the gate verbatim, the honesty rules, the two flows), GitHub
issue templates that encode constitution V at the point of entry, a
PR template that encodes I/II/VI as checkboxes, and a
`contribution-seed/` folder holding the labels and 3–5 verified
good-first-issue drafts the maintainer applies with `gh`. Documents
and templates only — zero code, zero behavior. The roadmap exit
("first external world contribution merged") depends on an external
human and stays pending.

## Technical Context

**Language/Version**: Markdown + JSON + GitHub template YAML front-matter (no code)
**Primary Dependencies**: none — no runtime artifacts
**Storage**: N/A
**Testing**: the full repo gate (`ruff format --check && ruff check && pytest -q`, zero skips) proves nothing moved; citation accuracy checked by hand against the tree (SC-001)
**Target Platform**: GitHub (templates, labels) + any checkout (CONTRIBUTING.md)
**Project Type**: documentation/templates
**Performance Goals**: N/A
**Constraints**: no `src/`, `tests/`, `pyproject.toml`, or `hq/` edits on this branch; README section appended at the very end (concurrent docs-site edits); every cited path/API must resolve (FR-006)
**Scale/Scope**: 1 guide, 3 issue-template files, 1 PR template, 1 labels file, 4 issue drafts, 1 three-line README section

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **I. Reference-Preserving Forever — PASS (by construction).** The
  feature is documents and templates; no Python file changes, so no
  RNG stream, behavior, or serialized summary can move. The full gate
  proves it. The guide itself *teaches* article I: core changes need
  a conversation first because behavior is byte-frozen.
- **II. Honest Measurement — PASS.** The exit criterion that depends
  on an external human is recorded as pending, not claimed (SC-005).
  Seed drafts state scope honestly and cite only real APIs (SC-004).
  The guide transmits the honesty rules to contributors (spreads not
  means, FAILs are data, criteria amended openly).
- **III. Diagnose Before Fixing — N/A** (no behavioral problem in
  scope).
- **IV. Research Gates Before Showcase Spends — PASS.** OSS hygiene,
  roadmap Phase D; no demo, no research gate consumed.
- **V. Never Lose the Instrument Panel — PASS (transmitted).** No new
  worlds ship here, but the new-world template makes ground truth,
  determinism, and steppable time mandatory questions for every world
  that will.
- **VI. All-Green Quality Gate — PASS.** Gate green, zero skips,
  signed commits; the gate command is quoted verbatim in the guide
  and the PR template (SC-002).

**Post-design re-check**: unchanged — PASS. No artifact acquired a
runtime path; the seed material is applied by the maintainer with
`gh`, outside the merge.

## Project Structure

### Documentation (this feature)

```text
specs/038-contribution-surface/
├── spec.md              # Feature specification
├── plan.md              # This file
└── tasks.md             # Task list (documents-only feature: research.md,
                         # data-model.md, contracts/ carry no content here
                         # and are deliberately omitted)
```

### Repository artifacts

```text
CONTRIBUTING.md                          # NEW: the on-ramp guide
README.md                                # gains: 3-line Contributing section at the very end
.github/
├── PULL_REQUEST_TEMPLATE.md             # NEW: the four checkboxes
├── ISSUE_TEMPLATE/
│   ├── new-world-proposal.md            # NEW: constitution V as questions
│   ├── bug-report.md                    # NEW: repro + seed + byte-determinism
│   └── config.yml                       # NEW: blank issues off, polite pointer
└── contribution-seed/                   # NEW: maintainer-applied material
    ├── README.md                        # what this folder is + the gh commands
    ├── labels.json                      # names / colors / descriptions
    ├── gfi-01-acrobot-example.md        # draft: second Gymnasium worked example
    ├── gfi-02-delayed-echo-world.md     # draft: a new EventSource world
    ├── gfi-03-rover-odometry-sensor.md  # draft: opt-in rover sensor (028 pattern)
    └── gfi-04-gym-reward-sensor.md      # draft: the documented v1 deferral, opt-in
```

**Structure Decision**: seed material lives under
`.github/contribution-seed/` rather than as live issues because label
and issue creation are repository-authority acts with a timing
judgment attached; the folder carries the exact `gh` commands so
applying it is mechanical.

## Complexity Tracking

No constitution violations; table not needed.
