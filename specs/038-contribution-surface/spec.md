# Feature Specification: Contribution Surface

**Feature Branch**: `038-contribution-surface`
**Created**: 2026-07-27
**Status**: Draft
**Input**: User description: "Contribution surface (roadmap Phase D):
CONTRIBUTING.md, good-first-issue labels on world/sensor/actuator
implementations — the natural contributor on-ramp is *new bodies*, not
core changes. Exit criterion from the roadmap: first external world
contribution merged. That exit depends on an external human and is
recorded as pending; this feature ships the surface the exit needs:
the contributor guide, the issue and PR templates, and the seed
material (labels, scoped first issues) grounded in the real seams."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - An outside builder finds what to build and how (Priority: P1)

A maker lands on the repository wanting to contribute. Within one
document they learn: what the project wants (new worlds, bodies,
sensors, actuators, drives against the frozen v1.x seams), what it
does not want without a conversation (core changes — the validated
behavior is byte-frozen), where the seam protocols live, which worked
examples to copy, how to set up a dev environment, and the exact
quality gate their change must pass.

**Why this priority**: This is the feature. The roadmap names new
bodies as the natural contributor on-ramp; without a guide that names
the seams and the bar, every would-be contribution starts with a
guessing game and most end before they start.

**Independent Test**: Read CONTRIBUTING.md cold; every file path it
names resolves in the repository, the gate command it quotes is the
repository's real gate verbatim, and each class of wanted
contribution points at a live protocol plus a worked example.

**Acceptance Scenarios**:

1. **Given** CONTRIBUTING.md, **When** a reader asks "what should I
   build?", **Then** the answer names the seam protocols by file path
   (world, body/sensor/actuator, drive) and links the public-surface
   promise (Doc 0008) that makes building against them safe.
2. **Given** CONTRIBUTING.md, **When** a reader asks "what will get my
   PR declined?", **Then** the answer is explicit: core behavior
   changes without a prior conversation, gate failures, skipped tests,
   unsigned commits, and measured claims without spreads.
3. **Given** the dev-setup section, **When** a reader follows it on a
   clean checkout, **Then** the quoted gate command runs and its
   verbatim text matches the constitution's gate.

---

### User Story 2 - A contribution arrives through a template that asks the right questions (Priority: P2)

Someone proposes a new world or reports a bug through a GitHub issue
template that asks for what the project actually needs: for worlds —
what it would teach the brain, and the ground-truth/determinism plan
constitution V requires; for bugs — the repro, the seed, and the
byte-determinism expectation. Pull requests arrive with the
non-negotiables as explicit checkboxes.

**Why this priority**: Templates are the difference between a
reviewable contribution and a correspondence project. They encode the
constitution's requirements at the point of entry, so the first
review round is about the idea, not about missing information.

**Independent Test**: Each template file is valid GitHub template
front-matter plus a body whose prompts map one-to-one onto the
constitution articles they serve (V for worlds, I/II/VI for PRs).

**Acceptance Scenarios**:

1. **Given** the new-world template, **When** it is filled honestly,
   **Then** the resulting issue states what the world is, what it
   would teach the brain, and how ground truth, determinism, and
   steppable time are kept (constitution V).
2. **Given** the bug template, **When** it is filled honestly, **Then**
   the issue carries a repro command, the seed, and expected-vs-actual
   including the byte-determinism expectation.
3. **Given** the PR template, **When** a PR is opened, **Then** the
   author has affirmed: gate green with zero skips, additive/opt-in
   only, surface inventory updated if the public surface grew, and
   honest claims.

---

### User Story 3 - The maintainer seeds a first-issue shelf that is real (Priority: P3)

The maintainer creates the contribution labels and opens a small set
of good-first-issues from prepared drafts — each one a specific,
genuinely completable world/sensor/actuator idea verified against the
actual APIs, with its scope stated honestly. Nothing on the shelf is
fiction.

**Why this priority**: An empty "good first issue" label is a promise
with nothing behind it; a fictional one is worse. The drafts must
exist and be real before the labels mean anything — but they are seed
material, applied by the maintainer, not by this feature's merge.

**Independent Test**: Every API, file path, and pattern a draft cites
exists in the repository as cited; every draft states expected scope
and an acceptance bar that includes the gate.

**Acceptance Scenarios**:

1. **Given** a seed draft, **When** its cited files and classes are
   checked against the tree, **Then** all of them exist and behave as
   the draft describes.
2. **Given** the labels file, **When** the maintainer applies it,
   **Then** each label has a name, color, and description and the set
   covers worlds, sensors/actuators, drives, and first-issue scoping.

---

### Edge Cases

- A contributor wants to change core behavior: the guide must not say
  "no" — it must say "conversation first", and why (constitution I
  makes behavior byte-frozen; opt-in additions are the legal shape).
- A contribution grows the public surface: the PR checklist must
  route the author to the surface inventory and Doc 0008, because the
  surface guard in the gate will otherwise fail them without context.
- Blank issues: politely disabled — free-form questions get pointed
  at the guide rather than dropped into an untriaged void.
- The roadmap exit ("first external world contribution merged")
  cannot be shipped by this feature: it depends on an external human.
  The spec records it as pending rather than claiming it.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The repository MUST carry a root CONTRIBUTING.md, in
  the project's own voice, covering: wanted contributions (worlds,
  bodies, sensors, actuators, drives against the frozen seams, with
  Doc 0008 linked); the conversation-first rule for core changes with
  its constitutional reason; the seam protocols by file path; the
  worked examples to copy; dev setup; the quality gate verbatim (zero
  skips, signed commits); the honesty rules for measured claims
  (constitution II); the feature/research flow in a sentence each;
  and where the narrative lives (`hq/04-JOURNEY/`).
- **FR-002**: `.github/ISSUE_TEMPLATE/` MUST provide a new-world
  proposal template (what world, what it teaches the brain, ground
  truth/determinism/steppable time per constitution V), a bug-report
  template (repro, seed, expected byte-determinism), and a config
  that disables blank issues with a polite pointer.
- **FR-003**: `.github/PULL_REQUEST_TEMPLATE.md` MUST carry explicit
  checkboxes: gate green (command quoted), additive/opt-in only,
  surface inventory updated when the public surface grew, honest
  claims.
- **FR-004**: `.github/contribution-seed/` MUST carry the maintainer's
  seed material: `labels.json` (names, colors, descriptions) and
  three to five good-first-issue drafts, each verified against the
  real APIs and stating expected scope honestly.
- **FR-005**: README.md MUST end with a three-line Contributing
  section linking CONTRIBUTING.md.
- **FR-006**: Every repository path, protocol name, and command
  quoted in any artifact MUST resolve against the tree at merge time
  — no fictional APIs, no paraphrased gate.
- **FR-007**: The feature MUST ship zero code changes: no `src/`, no
  `tests/`, no `pyproject.toml`, no behavior of any kind.

### Key Entities

- **Contributor guide**: CONTRIBUTING.md — the on-ramp document.
- **Templates**: issue templates + config + PR template — the entry
  points that encode the constitution.
- **Seed material**: labels.json + issue drafts — applied by the
  maintainer with `gh`, outside this merge.
- **Exit criterion (pending)**: first external world contribution
  merged — depends on an external human; tracked on the roadmap, not
  claimable here.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of file paths, class/protocol names, and commands
  cited in CONTRIBUTING.md, the templates, and the seed drafts
  resolve against the repository tree.
- **SC-002**: The gate command appears verbatim (character-identical
  to constitution VI) in CONTRIBUTING.md and the PR template.
- **SC-003**: The full gate is green with zero skips on the feature
  branch — the feature adds documents only and proves it.
- **SC-004**: Each of the 3–5 seed drafts names its seam files, its
  acceptance bar, and an honest scope estimate; none cites an API
  that does not exist.
- **SC-005**: The roadmap exit criterion is recorded as *pending
  external contribution* — not claimed met.

## Assumptions

- **Labels and issues are maintainer acts.** Creating labels and
  opening issues on GitHub requires repository authority and a
  judgment call on timing; this feature prepares the material and the
  exact commands, and the maintainer executes them.
- **"Good first issue" spelling**: the drafts assume GitHub's
  conventional `good first issue` label name (surfaced by GitHub's
  contribute page and filters), created or updated with `--force`.
- **The README is concurrently edited** by the docs-site feature; the
  Contributing section goes at the very end of the file to keep the
  merge surface minimal.
- **Journey episode and roadmap update land with the merge** per house
  rules; they are written on the main checkout at landing time (this
  branch deliberately does not touch `hq/`).
