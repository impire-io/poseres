# Feature Specification: The Recipe and the Label

**Feature Branch**: `041-recipe-label`
**Created**: 2026-08-09
**Status**: Draft
**Input**: User description: "Ship the measured recipe-reach and praise-label mechanisms as product: recipe memory (taught order carries reach), the recipe-following policy, and the completion label — zero behavior change for existing users."

## Licensing context

Two pre-registered results license this build: **recipe-reach** (all three
bars PASS: transmission 24/24 vs the label-alone floor of 0/24, own chains
18/24 at bar, recipe-led 20/24) and **E3.1** (the label proven safe: no
hangover at any dose, chains 22/24). Both mechanisms ran as scratchpad
policies over shipped seams; this feature promotes them exactly as
measured, the feature-040 pattern (additive surface, off-by-default,
row-level closure rerun).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Praise as a label (Priority: P1)

A user whose anatomy carries an approval channel constructs the shipped
completion-itch policy with a label: completions the brain expects
applause for count fuller (1 + β·clip(predicted label delta, 0, 1)); the
label is read ONLY inside fired completions, so the measured hangover
mechanism cannot form. Users who don't pass a label channel get bit-exact
v1.2.0 behavior.

**Independent Test**: unit tests against stubbed contexts; label-off
draw-order parity with the 1.2.0 policy.

**Acceptance Scenarios**:
1. **Given** no label parameters, **When** the policy selects, **Then**
   selection and RNG use are identical to v1.2.0's policy.
2. **Given** a label channel and β, **When** a completion fires with
   positive predicted label delta, **Then** progress-after counts
   1 + β·clip(Δ̂,0,1); the label is never read outside fired completions.

### User Story 2 - Recipe memory and the recipe policy (Priority: P1)

A user teaches by demonstration and keeps the demonstrations' observation
sequences. Recipe memory extracts each demonstration's recipe (the
sequence up to its terminal gain); the shipped recipe policy then selects
the most valued recipe ending (drive + β·label at the terminal), walks its
stepping stones via head-predicted positions (the measured chained-hold
form), and lets the completion itch do the work at each station. All
anatomy knowledge (position channels and scale, progress/pocket/label
indices) is constructor parameters.

**Independent Test**: unit tests for extraction, selection, pointer
advance, and the hold arithmetic on synthetic sequences — no world.

**Acceptance Scenarios**:
1. **Given** demonstration sequences with pocket gains, **When** added to
   memory, **Then** each yields a recipe whose terminal is the max-label
   observation (label set) or the final gain observation (no label).
2. **Given** two recipes with different terminal label values, **When**
   the policy selects, **Then** the higher drive+β·label terminal wins.
3. **Given** the bot near step k of the active recipe, **When** it
   advances within reach of step k+1's position, **Then** the subgoal
   pointer advances (measurable via the policy's counters).

### User Story 3 - The research closure (Priority: P2)

The recipe-reach confirmatory rerun on shipped classes reproduces the
measured rows; recorded in the topic (which graduates to a design doc).

**Acceptance Scenarios**:
1. **Given** shipped RecipeMemory + RecipePolicy, **When** the 24-seed
   arm reruns at β = 0.5, **Then** R1/R2/R3 reproduce (row-level; exact
   match expected per the 040 precedent) and the result is recorded.

### Edge Cases

- Empty memory → the recipe terms are inert; the policy degrades to the
  labeled itch.
- Event head off (predict_event_delta None) → hold and label terms
  contribute zero; no crash.
- Out-of-range indices fail loudly at first selection (040 precedent).
- Recipes are policy-side state, deliberately NOT snapshot state in v1
  (reconstructible from kept demonstrations; recorded as an assumption).

## Requirements *(mandatory)*

- **FR-001**: `CompletionItchPolicy` gains keyword-only `label_index`
  (default None = off, bit-exact 1.2.0 behavior) and `label_beta`
  (default 0.0); the label read only inside fired completions.
- **FR-002**: A `RecipeMemory` extracts recipes from demonstration
  observation sequences (terminal = max-label obs when a label index is
  set, else the last pocket-gain obs; sequence = everything through the
  terminal) and holds them for policies.
- **FR-003**: A `RecipePolicy` (subclass of the itch policy) adds
  recipe selection (argmax drive + β·label at terminals, each directed
  step), nearest-step-plus-one subgoal pointing over position channels
  in world units, and the head-predicted subgoal hold
  (λ_r·−Chebyshev) as its potential; draw order unchanged from the
  measured gate policies. Bounded counters: advance events, out-of-
  context steps (the parrot watch).
- **FR-004**: All channel indices, position scale, λ_r, κ, β are
  constructor parameters; nothing anatomy-specific in Config.
- **FR-005**: Surface grows additively only (inventory + Doc 0008 both
  directions; Docs 0005 updated; version 1.2.0 → 1.3.0).
- **FR-006**: The recipe-reach confirmatory rerun on shipped classes
  reproduces the measured rows before the feature is done; the topic
  graduates to design with the episode.

## Success Criteria *(mandatory)*

- **SC-001**: Label-off and recipe-off paths bit-exact vs v1.2.0
  (tests prove draw-order and value parity).
- **SC-002**: The closure rerun reproduces recipe-reach's confirmatory
  (R1 24/24, R2 18/24, R3 20/24) on shipped components.
- **SC-003**: Full gate green; additive-only surface diff.

## Assumptions

- Recipe memory persistence is the caller's concern in v1 (demos are
  kept artifacts); a snapshot-state promotion is a later feature if a
  long run needs it.
- The clone-free hold from Doc 0009 remains available separately; the
  RecipePolicy's subgoal hold subsumes it when recipes are active (the
  measured gate ran exactly this composition).
- Measured operating points (κ 0.25, λ_r 0.25, β 0.5) are documented
  defaults-of-record, not hard-coded.
