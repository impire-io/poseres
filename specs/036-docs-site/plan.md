# Implementation Plan: Docs Site

**Branch**: `036-docs-site` | **Date**: 2026-07-27 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/036-docs-site/spec.md`

## Summary

A small Jekyll static site under `docs/`, deployed to GitHub Pages by a
GitHub Actions workflow. The repo commits only what is new: the index
page, the worlds gallery, the public-API pointer page, a design-docs
index, and the site config. Everything that already exists once —
`GETTING-STARTED.md`, `hq/02-DESIGN/*.md`, `explainer/index.html` — is
copied into the assembled site at build time, never duplicated in git.
A repo-local guard test keeps every reference the site makes (copy
sources, nav entries, relative links) resolvable against the tree, so
the site cannot silently rot. Zero runtime changes: no file under
`src/`, no existing test, no packaging metadata moves.

## Technical Context

**Language/Version**: Markdown + YAML (site); Python 3.12+ for the guard test only
**Primary Dependencies**: GitHub-hosted Jekyll build (`actions/jekyll-build-pages`) — the Pages default; no Node toolchain, no new Python dependencies (the guard test is stdlib + pytest)
**Storage**: N/A (static files)
**Testing**: pytest (repo gate: `ruff format --check && ruff check && pytest -q`, zero skips); the new guard test needs no network and no Jekyll
**Target Platform**: GitHub Pages project site at `https://impire-io.github.io/poseres/`
**Project Type**: static documentation site + CI workflow + one unit test
**Performance Goals**: N/A
**Constraints**: constitution I — byte-frozen suite untouched (this feature is docs/workflow/test only); constitution II/IV — every capability claim on the site matches the measured record, no demo promises; single-sourcing — design docs and getting-started exist exactly once in git
**Scale/Scope**: 5 committed pages + 1 config, 1 workflow, 1 guard test, 1 README section; ~10 build-time-copied documents

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **I. Reference-Preserving Forever — PASS (by construction).** No file
  under `src/` changes; no existing test changes; `pyproject.toml` is
  untouched. The additions are markdown under `docs/`, one workflow,
  one new test file, spec artifacts, and a README section. Nothing can
  move any mode's RNG stream, behavior, or serialized summaries. The
  full gate proves it as always.
- **II. Honest Measurement — PASS.** The site's claims are sourced from
  the journey's measured record, FAILs included (the L3 channel-static
  collapse, the rover's random policy, the Minecraft emergence floor
  are stated, not smoothed). Exit criteria are pre-written in the spec
  (SC-001..005). Every gallery entry links the telemetry-backed episode
  behind it.
- **III. Diagnose Before Fixing — N/A** (no behavioral problem in
  scope; any behavioral surprise during implementation stops the work).
- **IV. Research Gates Before Showcase Spends — PASS.** The site
  documents measured capability only; no demo outruns the record. The
  index's thesis quotes the roadmap/journey phrasing; the gallery cites
  episodes; no promise of undemonstrated behavior anywhere.
- **V. Never Lose the Instrument Panel — N/A** (no worlds are built;
  the gallery documents existing ones and their instrument properties).
- **VI. All-Green Quality Gate — PASS.** The gate grows by the docs
  guard test and stays all-green, zero skips; signed commits.

**Post-design re-check (after Phase 1)**: unchanged — PASS. The design
adds no runtime coupling: the site is data, the workflow runs only on
GitHub, the guard is a test.

## Project Structure

### Documentation (this feature)

```text
specs/036-docs-site/
├── spec.md              # Feature specification
├── plan.md              # This file
└── tasks.md             # Task list
```

### Source Code (repository root)

```text
docs/                            # NEW — the committed site source
├── _config.yml                  # title, url/baseurl, theme (minima), nav (header_pages)
├── index.md                     # what PRA is (honest thesis); links journey + explainer
├── worlds.md                    # the worlds gallery (the one new document)
├── api.md                       # public API: links Doc 0008, does not restate it
└── design/
    └── index.md                 # design-docs reading order; siblings arrive at build time

.github/workflows/
└── docs.yml                     # NEW — assemble (copy sources) → Jekyll build → deploy Pages

tests/unit/
└── test_docs_site.py            # NEW — the reference guard (no network, no Jekyll)

README.md                        # gains: a Documentation section linking the Pages URL
```

**Build-time assembly (in docs.yml, never in git)**:

```text
GETTING-STARTED.md        → docs/getting-started.md
hq/02-DESIGN/0*.md        → docs/design/          (glob: future 0009+ auto-deploys)
explainer/index.html      → docs/explainer/index.html
```

**Structure Decision**: Jekyll with the stock GitHub Pages build action
and the default `minima` theme — the Pages default plugin set
(optional-front-matter, relative-links, titles-from-headings,
default-layout) renders plain repo markdown without adding front matter
to single-sourced files, which is what makes copy-don't-fork possible.
The guard test mirrors the workflow's copy list as an explicit mapping
(site path → repo source) and cross-checks that the workflow text still
contains each copy — so workflow and test cannot drift apart silently
either.

## Complexity Tracking

No constitution violations; table not needed.
