# Tasks: Contribution Surface

**Input**: Design documents from `/specs/038-contribution-surface/`
**Prerequisites**: plan.md, spec.md

**Tests**: no code ships, so no new tests; the deliverable-level check
is citation accuracy (SC-001) verified against the tree, and the full
gate proving zero behavior change (SC-003).

**Organization**: grouped by user story; US1 (the guide) is the
feature's core, US2 (templates) encodes the constitution at the entry
points, US3 (seed material) is prepared here and applied by the
maintainer.

## Phase 1: Setup

- [X] T001 Confirm branch `038-contribution-surface`; venv built and
  the full gate green before any change:
  `./.venv/bin/ruff format --check . && ./.venv/bin/ruff check . && ./.venv/bin/pytest -q`
  (zero skips)

## Phase 2: Foundational

- [X] T002 Ground every claim: read the seam protocols
  (`src/pra/world/event_source.py`, `src/pra/anatomy/body.py`,
  `src/pra/motivation/drive.py`), the worked examples
  (`src/pra/world/ladder.py`, `src/pra/anatomy/gymnasium_body.py` +
  `examples/cartpole.py`, `src/pra/examples/rover/world.py`), Doc
  0008, and the constitution — the guide and drafts cite only what
  exists (FR-006)

## Phase 3: User Story 1 — the on-ramp guide (P1) 🎯 MVP

- [X] T003 [US1] Write `CONTRIBUTING.md`: wanted contributions
  against the frozen seams (Doc 0008 linked); conversation-first for
  core (constitution I stated as the reason); seam protocols by path;
  worked examples; dev setup (venv + `pip install -e ".[gym]"` +
  ruff/pytest); the gate verbatim with zero skips + signed commits;
  honesty rules (constitution II); feature vs research flow, one
  sentence each; the narrative pointer (`hq/04-JOURNEY/`)
- [X] T004 [US1] Append the three-line Contributing section at the
  very end of `README.md` linking CONTRIBUTING.md (concurrent-edit
  courtesy to the docs-site feature)

## Phase 4: User Story 2 — templates that ask the right questions (P2)

- [X] T005 [P] [US2] `.github/ISSUE_TEMPLATE/new-world-proposal.md`:
  what world, what it would teach the brain, ground truth /
  determinism / steppable time (constitution V), seam and scope
- [X] T006 [P] [US2] `.github/ISSUE_TEMPLATE/bug-report.md`: repro
  commands, seed, expected vs actual, the byte-determinism
  expectation, environment
- [X] T007 [P] [US2] `.github/ISSUE_TEMPLATE/config.yml`: blank
  issues disabled, polite contact link to CONTRIBUTING.md
- [X] T008 [US2] `.github/PULL_REQUEST_TEMPLATE.md`: gate-green
  checkbox (command quoted), additive/opt-in-only checkbox,
  surface-inventory checkbox, honest-claims checkbox

## Phase 5: User Story 3 — the seed shelf (P3)

- [X] T009 [US3] `.github/contribution-seed/labels.json`: label
  names, colors, descriptions covering first-issue scoping, worlds,
  sensors/actuators, drives, proposals
- [X] T010 [US3] Write 4 good-first-issue drafts, each verified
  against the real APIs, with seam paths, acceptance bar, and honest
  scope: Acrobot worked example, delayed-echo world, rover odometry
  sensor (feature-028 `emit_back` pattern), Gymnasium reward-as-sensor
  (the documented v1 deferral)
- [X] T011 [US3] `.github/contribution-seed/README.md`: what the
  folder is + the exact `gh` commands to apply labels and open the
  issues

## Phase 6: Landing

- [X] T012 Full gate green, zero skips (SC-003); citation sweep: every
  path/API/command in the new documents resolves (SC-001, SC-002)
- [ ] T013 **Maintainer, at landing (outside this branch)**: update
  `hq/03-IMPLEMENTATION/roadmap.md` (contribution surface shipped;
  exit *pending* first external world contribution) and write the
  journey episode via `/journey-log` — this branch deliberately does
  not touch `hq/`
- [ ] T014 **Maintainer, after merge**: apply
  `.github/contribution-seed/` with the `gh` commands in its README
  (labels, then issues); the roadmap exit closes only when the first
  external world contribution actually merges

## Dependencies

- T002 blocks T003 and T010 (grounding before writing).
- T005–T007 parallel; T008 independent.
- T009 before T011 (the commands reference the labels).
- T012 last on this branch; T013/T014 are maintainer acts.
