# Feature Specification: API Stability & v1.0

**Feature Branch**: `035-api-stability-v1`
**Created**: 2026-07-26
**Status**: Draft
**Input**: User description: "API stability and v1.0 (roadmap Phase D, episode 0060): freeze the public seam surfaces — Body, Sensor/Actuator, Drive, SnapshotStore — as documented public API with semantic versioning and a deprecation policy. Exit criteria from the roadmap: a v1.0 tag, and the seams documented as public API. The validated behavior stays byte-frozen (constitution I); this feature freezes surfaces, not behavior — it names what is public, what is internal, what compatibility v1.x promises, and how deprecations are announced and retired."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A maker builds against the documented surface and upgrades safely (Priority: P1)

A hobbyist or maker writes their own world/body (a new environment for
the brain), possibly their own drive or snapshot storage, using only
what the project documents as public. When they later upgrade to any
newer v1.x release, everything they built keeps working without
modification.

**Why this priority**: This is the core promise of v1.0 and the reason
Phase D exists — the natural contributor on-ramp is *new bodies*, and
nobody builds on a surface that may shift under them. Every other
Phase D item (docs site, shareable brains, contribution surface)
documents or extends this surface.

**Independent Test**: Build a small example world/body using only the
documented public API, then verify it runs unmodified against the
v1.0 surface with the compatibility check that guards the promise.

**Acceptance Scenarios**:

1. **Given** the v1.0 documentation, **When** a user asks "may I rely
   on this name?" for any importable name or command, **Then** the
   documentation answers public or internal for it — no name is
   unclassified.
2. **Given** a world/body written against only the public surface,
   **When** the project advances within v1.x, **Then** the world/body
   runs unmodified (guarded by an automated compatibility check, not
   by promise alone).
3. **Given** the tagged v1.0, **When** the validated reference suite
   runs, **Then** it reproduces its byte-frozen reference values —
   all green, none skipped (constitution I: the freeze names
   surfaces; behavior was already frozen).

---

### User Story 2 - The maintainer evolves internals without breaking users (Priority: P2)

The maintainer refactors internals, adds opt-in capabilities, and
retires mistakes — all without breaking anyone who stayed on the
public surface, because the public/internal boundary is explicit and
deprecations follow a published policy with a grace period.

**Why this priority**: Stability must not mean rigor mortis. The
project's own history (seams added feature by feature) shows internals
keep moving; v1.0 is only sustainable if the boundary lets them.

**Independent Test**: Deprecate a test element following the policy;
verify the notice appears, names the replacement and the removal
horizon, and that removal before the policy's horizon is impossible
without failing the gate.

**Acceptance Scenarios**:

1. **Given** a public element the maintainer wants to retire, **When**
   it is deprecated, **Then** using it produces a visible notice
   naming the replacement and the earliest release that may remove it.
2. **Given** the published versioning policy, **When** a release is
   cut, **Then** the version number's meaning (what may change at
   patch, minor, major) matches what actually changed.

---

### User Story 3 - v1.0 ships as a referenceable release (Priority: P3)

The project tags v1.0 with a changelog and the versioning/deprecation
policy published, so downstream Phase D items (docs site, shareable
brains, CONTRIBUTING) can reference a fixed, named surface, and
external users can pin it.

**Why this priority**: The tag is the roadmap's exit criterion and the
anchor for everything downstream — but it is only meaningful after
stories 1 and 2 define what it promises.

**Independent Test**: The tag exists; installing that tag yields the
documented surface; the changelog states what v1.0 promises.

**Acceptance Scenarios**:

1. **Given** the release, **When** a user installs the tagged version,
   **Then** the version reported by the package matches the tag and
   the documented surface is present.
2. **Given** the changelog, **When** a user reads the v1.0 entry,
   **Then** it states the compatibility promise and links the policy.

---

### Edge Cases

- A name is currently importable but was never meant as public (deep
  internals reachable by import): the boundary must classify it, and
  reaching for internals must be visibly at-your-own-risk rather than
  silently blessed.
- A snapshot written by one v1.x release is loaded by another: the
  compatibility promise must state what is guaranteed (at minimum:
  same-version round-trip exact; cross-version behavior explicitly
  documented, whatever it is — silence is not a policy).
- The validated byte-frozen behavior conflicts with a wanted change:
  the policy must state that behavior-affecting change is opt-in only
  within v1.x (existing modes' outputs unchanged), matching
  constitution I.
- An element must be removed urgently (e.g., a safety problem): the
  policy must say what overrides the grace period and how that is
  communicated.
- The public surface includes operational commands (the shipped
  command-line tools): renaming/removing a command or its documented
  flags is a public-surface change and follows the same rules.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The project MUST publish a single authoritative
  inventory that classifies every user-reachable element of the
  project surface as **public** or **internal** — covering at minimum
  the four seam families the roadmap names (world/body mounting,
  sensor/actuator anatomy, drives, snapshot storage), the run
  configuration and run entry surface, the shipped command-line
  tools, and the documented telemetry/control subject space.
- **FR-002**: Every public element MUST be documented at the level a
  user needs to build against it without reading internals.
- **FR-003**: The project MUST publish a versioning policy defining
  what may change at patch, minor, and major level for the public
  surface, including: behavior of existing modes is byte-frozen
  within v1.x except by explicit opt-in (constitution I restated as a
  compatibility promise), and snapshot round-trip guarantees stated
  per version distance.
- **FR-004**: The project MUST publish a deprecation policy: how a
  public element is announced as deprecated, the visible notice it
  produces when used (naming replacement and removal horizon), the
  minimum grace period, and the exception path for urgent removals.
- **FR-005**: An automated check MUST guard the public surface: a
  release in which a public element vanished or changed shape without
  following the policy MUST fail the gate, not ship.
- **FR-006**: The project MUST cut a v1.0 release: version set, tag
  created, changelog entry stating the promise, installable from the
  tag with the reported version matching.
- **FR-007**: Internal elements MUST remain reachable for research
  instruments (the arcs' copy-patch discipline depends on it) while
  being visibly outside the promise.
- **FR-008**: The validated reference suite MUST pass byte-exact on
  the tagged release — the tag ships nothing the gate has not proven.

### Key Entities

- **Public API inventory**: the classified surface — element, family
  (seam / config / command / subject space), status (public /
  internal), documentation pointer.
- **Compatibility promise**: the versioning policy — level (patch /
  minor / major), what may change, the byte-frozen clause, snapshot
  guarantees.
- **Deprecation record**: element, release announced, replacement,
  earliest removal release, notice text.
- **Release**: version, tag, changelog entry, gate evidence.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of user-reachable elements in the covered families
  are classified public or internal in the inventory; a reader can
  resolve any "may I rely on this?" question from documentation alone.
- **SC-002**: The reference validation suite reproduces its
  byte-frozen values on the tagged v1.0 — all tests green, zero
  skipped.
- **SC-003**: A worked example built against only the public surface
  runs unmodified on the tagged release, and the automated
  surface-guard check passes — and demonstrably fails when a public
  element is removed in a test scenario.
- **SC-004**: The v1.0 tag exists; installing it reports the tagged
  version; the changelog entry states the compatibility promise; the
  roadmap exit criterion reads met.
- **SC-005**: Using any deprecated element produces a visible notice
  naming its replacement and removal horizon, in 100% of deprecated
  cases (verified for at least one real or synthetic deprecation).

## Assumptions

- **Scope of "public"**: the roadmap names four seam families; this
  spec additionally treats the run configuration/entry surface, the
  four shipped command-line tools, and the documented
  telemetry/control subject space as public, because users already
  build against them daily (the Gymnasium/ROS2/Minecraft adapters
  mount through the named seams and inherit their status). Everything
  else defaults to internal.
- **Versioning baseline**: the package currently reports 0.1.0; v1.0
  is the first stability-bearing version. Standard semantic
  versioning applies (patch = fixes, minor = additive/opt-in, major =
  breaking), tightened by the byte-frozen clause for existing modes.
- **Deprecation defaults**: announce in the changelog + runtime/CLI
  notice on use; minimum grace of one minor release before removal;
  removal only at a major version except documented urgent cases.
- **No rename sweep**: v1.0 freezes the surface largely as it stands;
  cleanups that would rename public elements are out of scope unless
  individually justified — the value is the freeze, not a facelift.
- **Package identity**: the distribution/package naming stays as it
  is today; changing it is out of scope for this feature.
