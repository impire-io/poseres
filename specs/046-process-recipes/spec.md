# Feature Specification: Process Recipes

**Feature Branch**: `046-process-recipes`
**Created**: 2026-08-29
**Status**: Draft
**Input**: User description: "Process recipes (mechanism ladder rung
2 from design 0021 the-long-carry): a vocabulary for gainless
demonstrations, so a taught PATH can be remembered as behavior.
Feature 041's core assumption (recipe = demonstrated acquisition;
RecipeMemory.add_demonstration stores nothing without a pocket gain)
made episode 0120's fifteen lap demonstrations unstorable. Extend
the recipe vocabulary: a demonstration with no pocket gain but a
positive teacher label (the applauded ending) stores as a process
recipe — terminal = the applauded observation, steps = the walked
path through it. The worth question 0021 left open (what makes a
path worth walking when nothing is acquired) is answered by the
EXISTING measured grammar: the label pathway (label_beta, episodes
0075-0081, transmission 24/24 as terminal marker) amplified by the
deficit gate (feature 042) — no new value arithmetic. Unlabeled
gainless sequences still store nothing (a recipe remains a
demonstrated something: an acquisition or an applauded ending).
Interacts with shipped rung 1: a process recipe's stalled subgoal
dies place-keyed with its cohort. Opt-in and bit-exact off per
constitution I; the behavioral reading (do stored lap paths get
walked?) belongs to the arena revival under design 0021, not this
feature's gate."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A taught path becomes storable behavior (Priority: P1)

A person teaching the brain in a long-horizon world (the larder
loop: food behind three counted laps of a closed course)
demonstrates a PROCESS — walk this course, then that gate opens —
where no single demonstration acquires anything. They applaud the
ending, and the walked path is remembered as behavior the policy
can later select and follow.

**Why this priority**: Measured absence (episode 0120): recipe
memory requires a pocket gain, so all fifteen taught lap
demonstrations of the larder arena stored NOTHING — a taught path
cannot currently be remembered as behavior. This is rung 2 of the
mechanism ladder the compositional gate waits on (design 0021), and
the gap that made the arena's teach phase structurally void.

**Independent Test**: Feed a demonstration sequence with no
acquisition but an applauded ending into an opted-in recipe memory;
a recipe is stored whose terminal is the applauded observation and
whose steps are the walked path through it; the policy then points
and holds along those steps exactly as it does for acquisition
recipes.

**Acceptance Scenarios**:

1. **Given** process storage enabled and a demonstration with no
   pocket gain but a positive label somewhere in the sequence,
   **When** the demonstration is added, **Then** a recipe is stored
   with terminal = the highest-labeled observation (latest on ties
   — the existing terminal rule) and steps = the sequence through
   that observation.
2. **Given** a stored process recipe, **When** the policy selects
   and follows it, **Then** the pointer, subgoal hold, and watch
   counters behave exactly as for acquisition recipes — one
   vocabulary, two ways in.
3. **Given** process storage enabled and a gainless sequence with
   no positive label, **When** added, **Then** nothing is stored —
   a recipe remains a demonstrated something: an acquisition or an
   applauded ending, never ambient wandering.
4. **Given** a demonstration containing a pocket gain, **When**
   added with process storage enabled, **Then** the stored recipe
   is identical to what the pre-046 rule stores (the acquisition
   pathway is untouched; process is a second door, not a rewrite).

---

### User Story 2 - Existing users are untouched (Priority: P1)

A person running any existing deployment upgrades and sees
bit-exact behavior: process storage ships off by default, and a
gainless labeled demonstration that stored nothing before still
stores nothing until the owner opts in.

**Why this priority**: Constitution I. This is sharper here than
usual: users of the shipped label pathway (feature 041) already
feed labeled sequences — without an explicit opt-in, this feature
would silently start storing recipes for them. The default must
preserve "no gain → no recipe" exactly.

**Independent Test**: With defaults, gainless labeled sequences
return nothing and store nothing; gainful sequences store
byte-identical recipes to v2.3.0; the byte-frozen suite stays
green.

**Acceptance Scenarios**:

1. **Given** default construction (process storage off), **When**
   any demonstration is added, **Then** storage decisions and
   stored contents are identical to v2.3.0 — including gainless
   labeled sequences storing nothing.
2. **Given** process storage requested without a label channel
   configured, **Then** construction fails loudly (a process
   recipe is DEFINED by its applauded ending — without a label
   sense there is nothing to mark one).

---

### User Story 3 - A process recipe is worth walking through the teacher's voice (Priority: P2)

A person whose brain holds both acquisition recipes and process
recipes wants the existing worth grammar to price them on one
scale: a process recipe's ending speaks through the label channel
(the teacher's voice, deficit-amplified by the body's need), so no
new value arithmetic enters the policy.

**Why this priority**: This is design 0021's open core question —
what makes a path worth walking when nothing is acquired — and the
answer must not invent a new pathway when a measured one exists:
the label as terminal marker measured transmission 24/24 (episode
0076), praise-weight menu steering measured (episode 0080), and
the deficit gate measured (episodes 0083–0085). Reusing it keeps
the worth of a taught path teachable and body-gated with the dials
already in the product.

**Independent Test**: A process recipe (labeled terminal, no gain)
competes in selection against an unlabeled acquisition recipe
purely through the existing label weight: with the teacher's voice
weighted it wins, with weight zero selection is unchanged from
drive value alone.

**Acceptance Scenarios**:

1. **Given** a process recipe and an acquisition recipe of equal
   drive value, **When** the label weight is positive, **Then**
   the process recipe's applauded terminal earns exactly the
   existing label term — no other term exists or is added.
2. **Given** the deficit gate configured (feature 042), **When**
   the sensed deficit rises, **Then** a process recipe's worth
   rises exactly as any labeled terminal's does — the body's need
   amplifies the taught path's voice through the shipped pathway.

---

### User Story 4 - A stalled process path dies at its place, and comes back (Priority: P3)

A person running process recipes against a world that blocks the
path (the closed gate before lap 3) wants rung 1's futility to
govern them unchanged: the stalled subgoal poisons its PLACE, the
whole pointing cohort goes quiet together, and the peek returns.

**Why this priority**: Design 0021 named this interplay when rung 1
shipped place-keyed: "required the moment process recipes exist, or
the lap recipe dies with the stalled turn-in cohort." The two rungs
must compose without either changing.

**Independent Test**: A process recipe whose pointer stalls
accumulates place-keyed fatigue and revives exactly as an
acquisition recipe does — same constants, same counters, no
process-specific futility state.

**Acceptance Scenarios**:

1. **Given** a process recipe stalled at a place for the stall
   budget, **When** the place is poisoned, **Then** the process
   recipe is ineligible while the poison holds and eligible at the
   peek — identical to acquisition-recipe futility in every
   counter.

---

### Edge Cases

- Applause at the very first observation: the stored path is a
  single observation pointing at its own ending — degenerate but
  legal (the pointer arithmetic already clamps); the teacher
  applauded standing still, and the recipe faithfully records that.
- Applause at multiple points: the existing terminal rule decides —
  highest label wins, latest index on ties; everything after the
  chosen terminal is not part of the path.
- A sequence with both a gain and a label: the acquisition door is
  taken (the pre-046 rule, unchanged); process storage only
  considers sequences the acquisition rule rejects.
- Label present but never positive (all zeros): not an applauded
  ending; nothing stores. Strictly positive is the mark.
- A stored process recipe is distinguishable from an acquisition
  recipe on inspection (observability for the arena's registered
  analysis and for rung 3's future selection work), but the policy
  treats them identically everywhere in this feature.
- Memory growth: process storage is bounded by demonstrations
  given, exactly as acquisition storage is — teaching is the only
  way in, and the opt-in flag is the only door.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: `RecipeMemory` gains a keyword-only opt-in
  `process: bool = False`. Off (default) preserves v2.3.0 storage
  decisions and contents bit-exactly — including "no gain → no
  recipe" for gainless labeled sequences.
- **FR-002**: `process=True` requires `label_index` to be set;
  violation raises ValueError at construction.
- **FR-003**: With `process=True`, a demonstration with no pocket
  gain and at least one strictly positive label stores a recipe:
  terminal = the max-label observation (latest index on ties — the
  existing rule), steps = the sequence through the terminal.
- **FR-004**: With `process=True`, a gainless demonstration with no
  strictly positive label stores nothing and returns nothing (the
  existing contract for unstorable sequences).
- **FR-005**: Demonstrations containing a pocket gain store
  identically with `process` on or off — the acquisition door is
  untouched.
- **FR-006**: A stored process recipe is marked as such on the
  recipe record (inspectable), with the mark defaulting to
  not-process so existing acquisition recipes and their
  construction sites are unchanged.
- **FR-007**: `RecipePolicy` requires no changes: selection prices
  a process terminal through the existing
  drive-plus-label-weight arithmetic (features 041/042 dials);
  pointing, holding, watch counters, and place-keyed futility
  (feature 045) operate on process recipes without any
  process-conditional branch.
- **FR-008**: No engine, persistence, observation-contract, or
  anatomy changes; recipes (process included) remain policy-side
  caller-kept state, not snapshot state (the standing feature-041
  assumption).

### Key Entities

- **Process recipe**: a remembered demonstration whose ending is an
  applauded observation rather than an acquisition — same steps /
  terminal shape as any recipe, marked process, priced through the
  label channel.
- **The applauded ending**: the strictly-positive-label observation
  chosen by the existing max-label terminal rule; the teacher's
  mark that makes a gainless path a demonstration rather than
  wandering.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: With defaults, the full regression gate is green and
  storage decisions are byte-identical to v2.3.0 for every
  demonstration class (gainful, gainless labeled, gainless
  unlabeled).
- **SC-002**: The measured absence closes: a lap-style
  demonstration set (gainless, end-applauded — the class episode
  0120 recorded as unstorable, 0 of 15 stored) stores one recipe
  per demonstration when opted in, each replaying the walked path
  through its applauded ending.
- **SC-003**: One vocabulary: on identical step sequences, a
  process recipe and an acquisition recipe produce identical
  pointing, holding, and futility behavior — zero
  process-conditional differences in any watch counter.
- **SC-004**: The worth grammar is reused, not extended: selection
  over a mixed memory is fully explained by the existing
  drive + label-weight arithmetic (verified by comparing selection
  outcomes against that arithmetic directly), and the policy
  gains no new dial.

## Assumptions

- The strictly-positive-label mark is sufficient to separate
  demonstration from wandering: labels are teacher-emitted, sparse,
  and already the measured terminal marker (episode 0076); ambient
  worlds without a teacher never emit them, and `process` off is
  the default besides.
- Worth-by-label is a promotion by mechanism-argument, not a new
  measurement: the label pathway's transmission and deficit
  amplification are measured on acquisition recipes (episodes
  0076, 0080, 0083–0085); their reuse for process terminals adds
  no arithmetic, and the behavioral reading — do stored lap paths
  get WALKED on the arena — is the arena revival's question under
  design 0021, deliberately outside this feature's gate.
- Marking process recipes on the record is observability only in
  this feature; rung 3 (stage-conditional selection) may later
  read it, and giving it a home now avoids a record-shape change
  then.
- The feature-041 caller-kept-state rule carries: process recipes
  are reconstructible from kept demonstrations; nothing enters
  snapshots.
