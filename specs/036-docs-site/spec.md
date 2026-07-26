# Feature Specification: Docs Site

**Feature Branch**: `036-docs-site`
**Created**: 2026-07-27
**Status**: Draft
**Input**: User description: "Docs site (roadmap Phase D, episode 0060):
GETTING-STARTED, the design docs, and a worlds gallery rendered as a small
static site. Exit criteria from the roadmap: docs deployed, linked from
README. The site must single-source its content — the design docs and the
getting-started guide are not duplicated into the site's directory; they are
copied in at deploy time. Every capability claim on the site must match the
measured record (constitution II/IV): quote the journey's phrasing, never
marketing language, no demo promises."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A maker finds, reads, and follows the docs on the web (Priority: P1)

A hobbyist or maker lands on the project's documentation site from the
README (or a search), understands in one paragraph what PRA is and is
not, follows the getting-started guide from install to a running brain,
and browses the design documents 0001–0008 — all without cloning the
repository.

**Why this priority**: This is the roadmap item itself. The natural
contributor on-ramp (new bodies, new worlds) starts with readable docs;
today everything lives as markdown files a visitor must dig out of the
repo tree.

**Independent Test**: Open the deployed site root; verify the index
states the thesis honestly, the getting-started page's commands match
the real CLI, and every design doc 0001–0008 renders and is reachable
from the site's navigation.

**Acceptance Scenarios**:

1. **Given** the deployed site, **When** a visitor opens the root page,
   **Then** they see what PRA is (the honest one-paragraph thesis) with
   links to the journey, the interactive explainer, getting started,
   the worlds gallery, the design docs, and the public-API page.
2. **Given** the getting-started page, **When** a visitor runs its
   commands (`uvx --from poseres pra-validate suite`, `pra-rover`),
   **Then** the commands exist and behave as the page states.
3. **Given** the design docs pages, **When** compared with
   `hq/02-DESIGN/*.md` at the deployed commit, **Then** they are the
   same content — rendered from the single source, not a fork of it.

---

### User Story 2 - A visitor picks a world to mount (Priority: P2)

A visitor who wants to try the brain against something browses a worlds
gallery: every shipped world and adapter with an honest one-paragraph
description, the exact configuration that mounts it, and a pointer to
the journey episode that measured it.

**Why this priority**: The gallery is the one genuinely new document
this feature writes. Worlds are the product's contribution surface, and
today the knowledge of what worlds exist and what was measured on them
is scattered across docstrings and journey episodes.

**Independent Test**: For each entry in the gallery, verify the class
or command exists in the source tree, the config snippet is accepted by
`Config` validation, and the cited journey episode exists and actually
measured that world.

**Acceptance Scenarios**:

1. **Given** the worlds gallery, **When** a visitor reads any entry,
   **Then** it names the mounting configuration and links the journey
   episode with the measured record behind the description.
2. **Given** the gallery's claims, **When** checked against the journey
   README's "Where things stand", **Then** no claim exceeds the
   measured record (a FAIL that is part of the record is stated, not
   hidden).

---

### User Story 3 - The docs deploy themselves and cannot silently rot (Priority: P3)

A push to main that touches docs-relevant paths redeploys the site
automatically. A repo-local test guards the site's references: if a
file the site depends on is renamed or removed, the quality gate fails
before the site can 404.

**Why this priority**: Without automation the site drifts from the
repo; without the guard, single-sourcing (copy at build time) would rot
silently — the failure mode of every "copies at deploy" scheme.

**Independent Test**: The workflow builds the assembled site from a
clean checkout; the guard test fails when a referenced file is renamed
in a scratch copy of the tree.

**Acceptance Scenarios**:

1. **Given** a push to main touching `docs/`, `hq/02-DESIGN/`, the
   getting-started source, or the workflow itself, **When** CI runs,
   **Then** the site is rebuilt and redeployed without manual steps.
2. **Given** a reference the site depends on (a copied file, a nav
   entry, a relative link), **When** its target disappears from the
   repo, **Then** `pytest` fails in the normal gate — no network, no
   site build needed.

---

### Edge Cases

- The design docs contain repo-relative links (e.g. the design README
  links `../00-GENESIS/how-we-work.md`): copied verbatim these would
  404 on the site. Links that leave the site's scope must be rewritten
  to the GitHub source at build time or the linking page not copied.
- A future design doc `0009-*.md` is added: the site must pick it up
  without editing the workflow (glob copy), though the navigation index
  page may need a row — the guard cannot force prose, but the glob
  keeps the content deployed.
- The Pages URL scheme (project site under `/poseres/`) breaks
  root-absolute links: all site-internal links must be relative.
- GitHub Pages is not yet enabled for the repository: the workflow must
  be inert-but-ready (deploy step fails visibly until Pages is enabled;
  enabling is an owner action outside this feature's scope).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The repository MUST contain a static-site source under
  `docs/` with: an index page (what PRA is — the honest one-paragraph
  thesis; links to the journey and the interactive explainer), a
  worlds-gallery page, a public-API page, and a design-docs index page.
- **FR-002**: The getting-started page and the design documents MUST
  NOT be duplicated under `docs/`: the deploy workflow copies
  `GETTING-STARTED.md` and `hq/02-DESIGN/*.md` (and the explainer) into
  the assembled site at build time. The repo holds exactly one copy of
  each document.
- **FR-003**: The worlds gallery MUST cover: the reference world, every
  world class in `src/pra/world/ladder.py` (NonUniform, Compositional,
  Distractor, Shifting, MultiRegion), the `pra-rover` world, the
  Gymnasium adapter, and the Minecraft body — each with an honest
  description, the config that mounts it, and the journey episode(s)
  that measured it.
- **FR-004**: The public-API page MUST link Doc 0008 as the authority
  and MUST NOT restate the surface list (one source, the guard already
  keeps Doc 0008 honest).
- **FR-005**: A GitHub Actions workflow MUST build and deploy the site
  to GitHub Pages (upload-pages-artifact + deploy-pages), triggered on
  pushes to main touching docs-relevant paths and by manual dispatch.
  Rendering is Jekyll via the standard Pages build action — no Node
  toolchain, no new repo dependencies.
- **FR-006**: A repo-local test MUST verify every local file the site
  references — the workflow's copy sources, the nav entries in the site
  config, and relative links in committed `docs/` pages (including
  links to build-time-copied files) — exists in the repository. It MUST
  need no network and no Jekyll.
- **FR-007**: `README.md` MUST link the deployed site
  (`https://impire-io.github.io/poseres/`) and state that the docs
  build from `docs/` plus `hq/02-DESIGN/`.
- **FR-008**: Every capability claim on the site MUST match the
  measured record; where a summary sentence exists in the journey
  README's "Where things stand", its phrasing is preferred over fresh
  wording. Measured FAILs that are part of a world's record are stated.
- **FR-009**: The feature MUST be purely additive to the runtime:
  no file under `src/`, no existing test, and no packaging metadata
  changes (constitution I — the byte-frozen suite is untouched by
  construction).

### Key Entities

- **Site source**: committed pages under `docs/` + the site config
  (title, base URL, navigation).
- **Build-time copy**: a (source path in repo → path in site) pair
  executed by the workflow; the set of these is what the guard test and
  the workflow must agree on.
- **Gallery entry**: world/adapter name, honest description, mounting
  config, measured-record episode link(s).
- **Deploy workflow**: trigger paths, assemble step (the copies + link
  rewrite), Jekyll build, Pages artifact upload, deploy job.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: The site deploys from the workflow and serves the index,
  getting-started, all eight design docs, the worlds gallery, and the
  public-API page (exit criterion: docs deployed, linked from README).
- **SC-002**: Zero duplicated documents: `git grep`-level check that no
  file under `docs/` contains a committed copy of GETTING-STARTED or
  any `hq/02-DESIGN/*.md` content — the copies exist only in the
  deployed artifact.
- **SC-003**: The gallery covers 100% of the required worlds/adapters
  (9 entries), each with a config that `Config` validation or the
  documented CLI accepts, and an episode link that exists in
  `hq/04-JOURNEY/`.
- **SC-004**: The guard test fails when any referenced file is removed
  (demonstrated in the test itself against a mutated reference), and
  the full gate stays green with zero skips on the unchanged suite.
- **SC-005**: The README links the Pages URL; the workflow needs only
  the owner's one-time Pages enablement (Settings → Pages → Source:
  GitHub Actions) to go live — no further repo changes.

## Assumptions

- **Pages URL**: the repository is `impire-io/poseres`, so the project
  site serves at `https://impire-io.github.io/poseres/`; the site config
  sets that base URL.
- **Jekyll defaults**: the GitHub Pages Jekyll build (with its default
  plugin set: optional front matter, relative links, titles from
  headings, default layout) renders plain markdown files copied from
  the repo without modification — this is why no per-file front matter
  is added to single-sourced documents.
- **Enabling Pages is an owner action**: this feature ships the
  workflow and the site source; flipping the repository's Pages source
  to "GitHub Actions" happens outside the branch (coordinator/owner),
  after which the next push to main deploys.
- **The explainer ships too**: `explainer/index.html` is a
  self-contained page (no external assets) and is copied into the site
  at build time so the index can link it as a working page rather than
  a raw file on GitHub.
- **Journey stays in the repo**: the journey is linked to GitHub, not
  copied into the site — it is a narrative of record, not reference
  documentation, and its 60+ episodes cross-link repo paths the site
  cannot resolve.
