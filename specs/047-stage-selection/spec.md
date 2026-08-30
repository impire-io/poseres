# Feature Specification: Stage-Conditional Selection

**Feature Branch**: `047-stage-selection`
**Created**: 2026-08-30
**Status**: Draft
**Input**: User description: "Stage-conditional selection (mechanism
ladder rung 3, the last, from design 0021 the-long-carry): a pathway
by which observation context — sensed stage, or for composed tiers
carried stage written into the observation — modulates WHICH recipe
is eligible, not just which terminal is valuable. Episode 0120
measured the absence: the sibling arm's declared laps sense was
structurally inert because a sense reaches selection only through
the terminal's drive value, and the world's own reset zeroed the
laps channel at every recorded terminal. The mechanism: declared
stage channels on RecipePolicy (anatomy knowledge, like
position_indices; empty default = off, bit-exact); a recipe is
eligible only when the current observation's stage values match some
step of its demonstrated sequence within a declared tolerance — the
demonstration already carries its stage trajectory, so the teacher's
demos partition behavior by context with no new storage. Hard
eligibility (the 0021 wording), not a value bonus — value modulation
is precisely the pathway 0120 proved inert. No stage-matching recipe
means the layer degrades to parent, like futility's wander phase.
Composes with rung 1 (eligibility = stage-matched AND not
place-poisoned) and rung 2 (process recipes carry stage in their
steps — the lap recipe becomes selectable at laps 0-2, the gate
recipe at laps 3). This is the pathway a winning composed arm would
speak through; the gate's comparison waits on it. Opt-in and
bit-exact off per constitution I; whether the composed ladder walks
the larder loop is the arena revival's question, not this feature's
gate."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - The sensed stage decides which taught behavior applies (Priority: P1)

A person teaching the brain in a staged world (the larder loop: walk
the course while the counter reads 0–2, enter the gate when it reads
3) demonstrates each behavior in its context and declares which
sensed channels carry the stage. The brain then selects the recipe
whose demonstrated context includes NOW: the lap path while the
count is low, the gate entry when the count arrives — with the
teacher's demonstrations, not any hand-written rule, drawing the
partition.

**Why this priority**: Measured absence (episode 0120): the sibling
arm had the lap count DECLARED IN ITS OBSERVATION and still scored
identically zero at n = 8, because a sense reaches selection only
through the terminal's drive value — and the world's own reset
zeroed the laps channel at every recorded terminal. The declared
sense was structurally inert. This is the ladder's last rung, and
the pathway the compositional gate's comparison reads through
(design 0021): a winning composed arm would speak by writing carried
stage into observation context.

**Independent Test**: Store two recipes demonstrated at different
stage values; sweep the sensed stage across both contexts and a
never-demonstrated third; selection follows the demonstrated
partition exactly — each recipe selectable precisely in its own
context, neither in the third.

**Acceptance Scenarios**:

1. **Given** declared stage channels and recipes demonstrated at
   distinct stage values, **When** the sensed stage matches steps of
   exactly one recipe, **Then** only that recipe is eligible — even
   when an ineligible recipe carries strictly higher worth (hard
   eligibility, not a bonus: outvaluing was precisely the pathway
   measured inert).
2. **Given** a recipe whose demonstration spans several stage values
   (the lap path walked at counts 0, 1, and 2), **When** the sensed
   stage is any of them, **Then** the recipe is eligible at each —
   the demonstrated trajectory, not a single stamp, defines its
   context.
3. **Given** a sensed stage matching no stored demonstration,
   **When** actions are selected, **Then** the policy behaves
   exactly as its parent — no demonstrated behavior fits this
   context, so none is imposed (the futility wander-phase precedent).
4. **Given** stage values within the declared tolerance of a
   demonstrated step's stage, **Then** they match; just beyond it,
   they do not — the boundary is exact and declared, not learned.

---

### User Story 2 - Existing users are untouched (Priority: P1)

A person running any existing deployment upgrades and sees bit-exact
behavior: no stage channels are declared by default, and selection,
RNG consumption, and every action stream are identical to v2.4.0.

**Why this priority**: Constitution I, the standing rule of every
rung: capability enters as an opt-in declaration with a measured
zero-change default.

**Independent Test**: Full gate with defaults; the off-parity idiom
(default vs. explicitly empty declaration vs. armed with an
all-matching context) shows identical action streams and RNG states.

**Acceptance Scenarios**:

1. **Given** no declared stage channels (the default), **When** any
   existing scenario runs, **Then** behavior is byte-identical to
   v2.4.0.
2. **Given** an invalid declaration (a negative channel index, a
   non-finite or negative tolerance), **Then** construction fails
   loudly (ValueError), never silently disabling.

---

### User Story 3 - The three rungs compose (Priority: P2)

A person running the full ladder wants one eligibility law: a recipe
is selectable when its demonstrated context includes the current
stage AND its pointed place is not poisoned — futility and stage
each removing exactly their own recipes, process and acquisition
recipes treated identically throughout.

**Why this priority**: The ladder was isolated as three gaps in one
diagnosis (episode 0120) and the arena needs all three at once: the
lap paths are process recipes (rung 2) whose stage trajectory
partitions them from the gate entry (rung 3), and the closed gate's
stall must kill exactly the pointing cohort and revive it (rung 1).
Composition failures here would be invisible to any single-rung
test.

**Independent Test**: A memory holding process recipes with distinct
stage spans, run through a stall-poison-revive cycle while the
sensed stage changes: at every step the eligible set is exactly the
stage-matched, unpoisoned recipes.

**Acceptance Scenarios**:

1. **Given** a stage-matched recipe whose pointed place is poisoned,
   **Then** it is ineligible until the peek; a differently-placed
   stage-matched recipe stays eligible throughout.
2. **Given** the sensed stage moves out of a poisoned recipe's
   demonstrated span, **When** the poison later expires, **Then**
   the recipe stays ineligible on stage grounds alone — the two
   filters are independent and both must pass.
3. **Given** process and acquisition recipes with identical
   demonstrated stage trajectories, **Then** their stage eligibility
   is identical in every scenario (one vocabulary — rung 2's
   guarantee extends through rung 3).

---

### Edge Cases

- The stage channels never appear in a recipe's demonstration era
  (recipes stored before the sense was declared, or a body upgrade
  widened the observation): a stored step simply has whatever value
  the channel had — matching is against recorded values, honestly;
  teaching with the sense on is the owner's responsibility and the
  documented practice.
- Stage channels overlapping position channels: legal but
  self-defeating (position already has the pointer); the
  documentation warns, construction does not forbid — the
  declaration is anatomy knowledge and the anatomy's author decides.
- Tolerance zero: exact-value matching — correct for discrete
  senses (a lap count); the default tolerance is small and
  positive so scaled integer channels survive float representation.
- All recipes stage-ineligible AND the futility layer active: the
  parent runs; no stall accrues (no followed step — rung 1's
  existing rule), so a context with no demonstrated behavior can
  never poison places.
- A demonstration whose stage channel drifts continuously (a clock
  rather than a counter): every observed value along the walk is in
  the trajectory, so the recipe is eligible across its demonstrated
  span — the mechanism does not require discreteness, only
  demonstration.
- Selection cost: the stage filter examines stored steps only when
  stage channels are declared; undeclared (the default) adds zero
  work.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: `RecipePolicy` gains keyword-only
  `stage_indices: tuple[int, ...] = ()` (declared stage channels —
  anatomy knowledge, the `position_indices` precedent) and
  `stage_tolerance: float = 1.0 / 128.0` (the match half-width; the
  `completion_threshold` quantum precedent). Empty `stage_indices`
  (default) disables the mechanism entirely.
- **FR-002**: Validation at construction: every stage index an
  integer ≥ 0; `stage_tolerance` finite and ≥ 0; violations raise
  ValueError.
- **FR-003**: Off means off — with no declared channels the policy
  performs no stage reads, no additional arithmetic, consumes no
  RNG, and produces byte-identical action streams to v2.4.0.
- **FR-004**: With channels declared, a recipe is eligible for
  selection only if some step of its stored sequence matches the
  current observation on EVERY declared channel within
  `stage_tolerance` (|sensed − recorded| ≤ tolerance, per channel,
  one step satisfying all channels at once).
- **FR-005**: Eligibility is hard: an ineligible recipe is excluded
  from the selection argmax regardless of its worth — no value
  bonus, no soft weighting (the pathway episode 0120 proved inert is
  not extended, it is bypassed).
- **FR-006**: With no eligible recipe the policy is exactly its
  parent for that step (the existing inert path shared with empty
  memory and all-poisoned futility); such steps are not followed
  steps and accrue no futility stall.
- **FR-007**: Composition law: eligible = stage-matched AND not
  place-poisoned (feature 045); the two filters are independent,
  order-indifferent in effect, and each removes only its own
  recipes. Process recipes (feature 046) pass through both filters
  identically to acquisition recipes.
- **FR-008**: No storage changes: the stage trajectory IS the
  stored demonstration (features 041/046 records, unchanged); no
  new recipe fields, no memory API change.
- **FR-009**: A bounded watch counter in the existing style:
  `stage_filtered_events` — selection steps on which the stage
  filter removed at least one otherwise-eligible recipe
  (measurement-only, never a selection input).
- **FR-010**: Pure policy mechanics — no engine, persistence,
  observation-contract, or anatomy changes; nothing enters
  snapshots.

### Key Entities

- **Declared stage channels**: observation indices the anatomy's
  author names as carrying stage — a world's sensed counter, or a
  composed tier's carried context written into observation; the
  policy treats them opaquely as values to match.
- **Demonstrated stage trajectory**: the values those channels took
  along a recipe's stored steps — the recipe's own record of the
  contexts it was taught in; the eligibility set is derived from
  it, never stored separately.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: With defaults, the full regression gate is green and
  the off-parity test shows byte-identical behavior — zero change
  for every existing user.
- **SC-002**: The measured inertness closes: in the two-context
  scenario (the 0120 shape — a low-stage path recipe and a
  high-stage entry recipe), sweeping the sensed stage flips the
  selected recipe at exactly the demonstrated boundary, and a
  higher-worth out-of-context recipe is never selected — the
  declared sense now reaches selection structurally, not through
  terminal value.
- **SC-003**: The ladder composes: through a scripted
  stage-sweep-plus-stall scenario, the eligible set at every step
  equals the set-intersection prediction (stage-matched ∩
  unpoisoned), with process and acquisition recipes
  indistinguishable in eligibility.
- **SC-004**: A never-demonstrated context yields parent behavior
  exactly (action-stream identity with the parent policy) and zero
  futility stall accrual.

## Assumptions

- Any-step matching (the recipe is eligible wherever its
  demonstration ever stood) is the honest minimal reading of "the
  demonstration carries its context": it requires no segmentation,
  no learning, and no new storage. Finer forms — matching only near
  the pointer, or stage-aware pointing WITHIN a recipe — are
  recorded as possible successors for the arena to motivate, not
  built now (the 0020/0021 caution).
- The default tolerance (1/128) matches the repo's established
  smallest-sensed-quantum precedent and makes exact discrete senses
  (scaled integer counters) match robustly under float
  representation; worlds with coarser stage senses declare a wider
  tolerance as anatomy knowledge.
- Declaring stage channels is anatomy/owner knowledge, like
  position indices and pocket index — the kernel never guesses
  which channels are stage.
- The behavioral question — does the three-rung stack walk the
  larder loop, and does a composed arm beat flat through this
  pathway — is the arena revival's registered question under design
  0021, deliberately outside this feature's gate.
