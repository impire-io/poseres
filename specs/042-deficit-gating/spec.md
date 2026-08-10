# Feature Specification: The Deficit Gate

**Feature Branch**: `042-deficit-gating`
**Created**: 2026-08-10
**Status**: Draft
**Input**: User description: "Promote the measured deficit→value coupling (episodes 0083/0084) into the product with zero behavior change when off — the coupling-promotion topic holds the frozen timing-primary bars."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - The mounted brain gains an emergency appetite (Priority: P1)

A person mounting the brain on a body with a homeostatic meter (a
survival energy level, a battery, any depleting resource sensed as an
observation channel) wants the brain's preference for felt-valuable
outcomes to strengthen as the resource depletes — sated, curiosity
rules; depleted, remembered value insists — without writing any
custom policy code.

**Why this priority**: This is the feature. Measured on two bodies,
the gated coupling is the difference between mostly dying and nobody
dying under a draining meter; without it, deprivation changes nothing
about choice.

**Independent Test**: Mount the shipped policy on a metered body with
the deficit parameters set; verify the effective label weight rises
as the sensed meter falls and that behavior shifts toward
high-felt-value outcomes when depleted (the archived instrument runs
are the reference).

**Acceptance Scenarios**:

1. **Given** a policy constructed with a deficit channel and gain,
   **When** the sensed meter reads full (1.0), **Then** the label
   weight equals the static `label_beta` alone (the coupling is
   silent when sated).
2. **Given** the same policy, **When** the sensed meter reads 0.6,
   **Then** the effective label weight is `label_beta + 0.4 × gain`,
   applied identically at both label read sites (completion read and
   recipe-terminal selection).
3. **Given** a meter reading outside [0, 1], **When** the weight is
   computed, **Then** the deficit is clipped to [0, 1] (no runaway
   weights).

---

### User Story 2 - Existing users are untouched (Priority: P1)

A person running any v1.3.0 configuration upgrades and observes
byte-identical behavior: the new parameters default off, and off means
no new observation reads, no float work, no RNG perturbation.

**Why this priority**: The additive-surface promise (Doc 0008) and the
arc's closure discipline both hang on exact off-parity.

**Independent Test**: Run identical seeds through the v1.3.0 arithmetic
and the new build with defaults; every action and the final RNG state
must be equal.

**Acceptance Scenarios**:

1. **Given** a policy constructed without deficit parameters, **When**
   any sequence of steps runs, **Then** actions and RNG state match
   v1.3.0 exactly.
2. **Given** `deficit_kappa=0` with a `deficit_index` set, **When**
   steps run, **Then** behavior is likewise identical (a zero gain is
   off).

---

### User Story 3 - Misconfiguration fails loudly at construction (Priority: P2)

A person wiring the policy to a body passes an inconsistent
configuration (a deficit channel with no label channel, an
out-of-range index, a negative or non-finite gain) and gets an
immediate, specific constructor error — never a silent misread of an
unrelated channel.

**Why this priority**: Index wiring is the one place body knowledge
enters; a silent off-by-one would corrupt every downstream reading.

**Acceptance Scenarios**:

1. **Given** `deficit_index` set and `label_index` unset, **When** the
   policy is constructed, **Then** construction fails with a specific
   error.
2. **Given** a `deficit_index` outside the observation, **When**
   constructed, **Then** construction fails.
3. **Given** a negative or non-finite `deficit_kappa`, **When**
   constructed, **Then** construction fails.

---

### Edge Cases

- Meter channel saturated above 1.0 or below 0.0 (sensor quirk):
  deficit clips to [0, 1].
- `label_beta > 0` together with the gate: the static (parent) term
  and the gated (body) term add — both teachers can speak at once.
- The recipe-selection site and the completion site must use the same
  per-step weight (one observation, one weight).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: `CompletionItchPolicy` accepts keyword-only
  `deficit_index: int | None = None` and
  `deficit_kappa: float = 0.0`; `RecipePolicy` inherits both by
  passthrough.
- **FR-002**: When enabled (index set and gain > 0), the effective
  label weight per directed step is
  `label_beta + deficit_kappa · clip(1 − obs[deficit_index], 0, 1)`,
  used at the fired-completion progress read and at recipe-terminal
  selection.
- **FR-003**: Disabled (index `None` or gain 0) is bit-identical to
  v1.3.0: no observation read at the deficit index, no additional
  float operations, identical action stream and RNG state.
- **FR-004**: Construction validates: `deficit_index` requires
  `label_index`; `deficit_index` within the observation;
  `deficit_kappa` finite and ≥ 0.
- **FR-005**: No new persistent state — the gate is pure per-step
  arithmetic; snapshots are unchanged.
- **FR-006**: The public surface grows additively:
  `surface_inventory` rows for both parameters, Doc 0008 inventory +
  release notes, Doc 0005 and Doc 0010 updated (instrument-grade
  **[O]** → shipped **[V]** citing the promotion bars), version
  1.3.0 → 1.4.0.

### Research-side closure (the coupling-promotion registration)

- **FR-007 (Bar P1)**: The shipped gate, substituted for the
  instrument subclass in the otherwise-unchanged archived runners,
  reproduces episode 0083's W1 arm and episode 0084's T2 arm
  row-for-row against the archived row files.
- **FR-008 (Bars P2/P3)**: The timing-primary bars are then evaluated
  on those rows and recorded in the topic README (C1 body: crisis-bin
  share ≥ 2× uncoupled, survival gap ≥ 4, sated rotation ≥ 12/24,
  chains ≥ 18/24; second body: hungry-bin margin ≥ +0.15, deaths ≤
  half of uncoupled).

## Success Criteria *(mandatory)*

- **SC-001**: Full quality gate green (format, lint, tests including
  the structural lint and surface guard).
- **SC-002**: Off-parity proven by test with RNG-state equality.
- **SC-003**: Gating arithmetic verified at known meter readings at
  both read sites by unit test.
- **SC-004**: All three validation errors raised with specific
  messages, by test.
- **SC-005**: Bar P1 row-for-row identity on both archived arms; Bars
  P2/P3 pass on those rows; verdict recorded in the topic README.

## Assumptions

- The deficit is defined against a [0, 1]-normalized meter (all
  measured meters are); readings outside clip.
- The gate composes additively with `label_beta` (measured arms used
  `label_beta = 0`; additivity is the natural extension and is
  covered by unit test, not by a new behavioral gate).
- Policy-side counters and recipes remain caller-kept, per v1.3.0.
