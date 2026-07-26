# Tasks: Docs Site

**Input**: Design documents from `/specs/036-docs-site/`
**Prerequisites**: plan.md, spec.md

**Tests**: The spec demands one enforcement test (the reference guard,
FR-006/SC-004) — a deliverable, not TDD ceremony, tasked as such.

**Organization**: grouped by user story; US1 alone is a viable MVP (the
readable site source), US2 adds the gallery, US3 wires deploy + guard.

## Phase 1: Setup

- [X] T001 Confirm branch `036-docs-site` is current and the full gate
  is green before any change: `./.venv/bin/ruff format --check . &&
  ./.venv/bin/ruff check . && ./.venv/bin/pytest -q` (zero skips) — the
  byte-frozen baseline this feature must not move

## Phase 2: Foundational (blocking all stories)

- [X] T002 Verify the sources the site will single-source: the commands
  in `GETTING-STARTED.md` against the real CLI (`pra-validate --help`,
  `pra-rover` flags), the relative links inside `hq/02-DESIGN/*.md`
  (which would break when copied), and the explainer's
  self-containment (no external assets) — record what needs rewriting
  at build time (finding: only `hq/02-DESIGN/README.md` carries a
  repo-relative link, so it is not copied; a committed design index
  replaces it)

## Phase 3: User Story 1 — find, read, follow the docs on the web (P1) 🎯 MVP

**Goal**: the committed site source — index, config, design index,
public-API page — honest and internally consistent.

**Independent Test**: every committed page's claims trace to the
journey record; all relative links resolve per the build-time mapping.

- [X] T003 [US1] Write `docs/_config.yml`: title, description (the
  honest thesis line), `url`/`baseurl` for the project site, theme
  `minima`, `strip_title` for copied docs, explicit `header_pages` nav
- [X] T004 [US1] Write `docs/index.md`: what PRA is — the one-paragraph
  thesis in the roadmap's phrasing (an OSS continuously-learning brain
  for hobbyists and makers), what is measured vs open, links to
  getting-started, worlds, design docs, API page, the journey (GitHub)
  and the interactive explainer (in-site copy)
- [X] T005 [P] [US1] Write `docs/design/index.md`: reading order
  0001–0008 with one-line "covers" summaries, status-legend pointer,
  note that content is copied from `hq/02-DESIGN/` at build time
- [X] T006 [P] [US1] Write `docs/api.md`: the v1.x promise in one
  sentence, link to Doc 0008 (in-site copy) as the single authority —
  no surface list restated (FR-004)

**Checkpoint**: US1 alone = a coherent committed site source (MVP)

## Phase 4: User Story 2 — pick a world to mount (P2)

**Goal**: the worlds gallery — 9 entries, honest, measured, mountable.

**Independent Test**: each entry's class/command exists; each config is
legal per `Config` validation; each episode link exists in
`hq/04-JOURNEY/`.

- [X] T007 [US2] Write `docs/worlds.md` covering: reference world,
  NonUniformWorld (L1), CompositionalWorld (L2), DistractorWorld (L3),
  ShiftingWorld, MultiRegionWorld, `pra-rover`, the Gymnasium adapter,
  the Minecraft body — each with an honest description (FAILs in the
  record stated), the mounting config (checked against
  `src/pra/config.py` validation and `src/pra/harness/ladder.py`
  dials), and the measuring episode(s) from the journey index (0003,
  0017, 0025/0030, 0031, 0034, 0020, 0019, 0043 — read from the index,
  not guessed)

**Checkpoint**: the one new document exists and is honest

## Phase 5: User Story 3 — deploys itself, cannot rot (P3)

**Goal**: the workflow and the guard.

**Independent Test**: workflow YAML is well-formed; guard fails on a
removed reference (demonstrated in-test); gate green.

- [X] T008 [US3] Write `.github/workflows/docs.yml`: triggers (push to
  main on docs-relevant paths + workflow_dispatch), assemble step
  (copy `GETTING-STARTED.md`, glob-copy `hq/02-DESIGN/0*.md`, copy
  `explainer/index.html`), `actions/jekyll-build-pages` build,
  `actions/upload-pages-artifact` + `actions/deploy-pages` with the
  Pages permissions and concurrency group
- [X] T009 [US3] Write `tests/unit/test_docs_site.py`: (a) every
  workflow copy source exists (glob-aware), (b) the workflow still
  contains each copy the site relies on, (c) every relative link in
  committed `docs/` pages resolves — committed or build-provided via
  the explicit mapping, (d) `header_pages` nav entries resolve the same
  way, (e) the guard demonstrably fails on a missing reference
  (negative control inside the test); no network, no Jekyll
- [X] T010 [P] [US3] Add a "Documentation" section to `README.md`
  linking `https://impire-io.github.io/poseres/` and stating the site
  builds from `docs/` + `hq/02-DESIGN/` (+ `GETTING-STARTED.md`)

## Phase 6: Polish & Landing (house rules: same merge)

- [X] T011 Full gate green with the guard in it: `./.venv/bin/ruff
  format --check . && ./.venv/bin/ruff check . && ./.venv/bin/pytest
  -q` — zero skips, byte-frozen baseline untouched (constitution I
  evidence)
- [ ] T012 Owner/coordinator (outside this branch): enable Pages
  (Settings → Pages → Source: GitHub Actions) — first deploy happens on
  the next docs-touching push to main; then roadmap + journey episode
  land with the merge per the house rules

## Dependencies

- Phase 2 (T002) blocks all stories (it decides the copy list).
- US1: T003→T004; T005, T006 parallel after T003.
- US2: T007 independent of US1 pages (parallel after T002).
- US3: T008 needs T002; T009 needs T003–T008 (it guards their
  references); T010 parallel.
- Phase 6 strictly last; T012 is external to the branch.

## Implementation Strategy

MVP = Phases 1–3 (US1): the committed site source. US2 adds the gallery,
US3 makes it deploy and keeps it honest. Single-session feasible; the
review-heavy artifact is the gallery (T007) — every sentence in it is a
capability claim and is checked against the journey record.
