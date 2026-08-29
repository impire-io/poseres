# Feature Specification: Progress-Keyed Futility

**Feature Branch**: `045-progress-keyed-futility`
**Created**: 2026-08-29
**Status**: Draft
**Input**: User description: "Progress-keyed futility (mechanism
ladder rung 1 from design 0021 the-long-carry): the stalled-pointer
signal RecipePolicy already computes must erode the following
behavior, so the brain stops pressing a gate that doesn't open.
Promoted form is place-keyed layer fatigue: when a recipe's pointer
makes no progress for K followed steps, the stalled subgoal poisons
every recipe currently pointing at that place/subgoal, putting them
dead for W steps, after which they revive (re-check cadence emerges
from the constants). Prototype of record measured at rig level:
K=200, W=800 abolished a 4,672-step futile press and produced the
larder-loop arena's first brain-driven crossings. Two refuted forms
must be avoided: naive per-recipe erosion (boundary thrash, 556
die/revive events) and per-recipe hysteresis (cohort fallback among
near-identical recipes). Kernel-grain feature; the arena/rig stays
research furniture."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - The brain stops pressing a gate that doesn't open (Priority: P1)

A person mounting the brain on a body in a world with blocked paths
(a closed gate, a depleted resource, a moved landmark) wants
recipe-following that gives up on a path that is provably going
nowhere — and comes back later to re-check it — instead of pressing
the same blocked spot for the rest of its life.

**Why this priority**: Measured (the-long-carry, episode 0120): the
current stack parked 4,672 of 6,000 life-steps pressing a closed
obsidian gate. Recipe selection is a stateless argmax with no
disconfirmation pathway; the stalled-pointer signal the policy
already computes feeds nothing. The rig prototype (K = 200
no-advance steps → dead W = 800) abolished the parking, produced
the revive-peek-wander loop (up to 7 peeks/life), and yielded the
larder arena's first brain-driven lap crossings. This is rung 1 of
the mechanism ladder the compositional gate waits on (design 0021).

**Independent Test**: Teach a recipe whose path is blocked at a
known place; run a life with futility on. The policy disengages
within the stall budget, behaves as its parent (wander/explore)
while the place is poisoned, and re-points at the place after the
revival window — repeatably, life after life.

**Acceptance Scenarios**:

1. **Given** futility enabled and a selected recipe whose subgoal
   pointer has not advanced for K consecutive followed steps,
   **When** the next selection runs, **Then** the stalled place is
   poisoned and no recipe currently pointing at it is eligible.
2. **Given** a poisoned place and no other eligible recipe,
   **When** actions are selected, **Then** the policy behaves
   exactly as its parent (the recipe terms inert — the measured
   degrade-to-parent path that already exists for empty memory).
3. **Given** a poison W steps old, **When** the next selection
   runs, **Then** the place revives and recipes pointing at it are
   eligible again (the peek: if the world still blocks it, the
   stall re-accumulates and the place dies again — the re-check
   cadence emerges from K and W, no scheduler).
4. **Given** the pointer advances at any time before K is reached,
   **Then** the stall count for that place resets to zero — genuine
   slow progress is never punished.

---

### User Story 2 - Existing users are untouched (Priority: P1)

A person running any existing PRA deployment upgrades and sees
bit-exact behavior: futility ships off by default, and off means
off — no value perturbation, no RNG-stream change, the byte-frozen
regression suite green.

**Why this priority**: The v1.0 surface contract (Doc 0008) and
every feature since 040: mechanisms enter as opt-in dials with a
measured zero-change default. The larder arena itself must be able
to run its registered flat arm unchanged.

**Independent Test**: Full gate with defaults — the byte-frozen
suite, the surface guard, and the feature's own off-is-off test
(identical action streams with and without the feature present).

**Acceptance Scenarios**:

1. **Given** default parameters (futility disabled), **When** any
   existing scenario runs, **Then** action streams and RNG
   consumption are identical to v2.2.0.
2. **Given** invalid constants (negative or non-finite K or W, or
   K set without W), **Then** construction fails loudly
   (ValueError), never silently disabling.

---

### User Story 3 - The whole stalled cohort dies together, and only it (Priority: P2)

A person whose brain holds many near-identical recipes (the larder
rig held ~15 lap demonstrations, all pointing through the same
gate) wants futility keyed to the PLACE, so that when the gate
stalls, every recipe pointing at it goes quiet together — and
recipes pointing elsewhere stay live.

**Why this priority**: Both refuted forms are cohort failures,
recorded with numbers (episode 0120): naive per-recipe erosion
thrashed at the poison boundary (556 die/revive events in one
life); per-recipe hysteresis produced cohort fallback — the argmax
slid to the next near-identical recipe pointing at the same
blocked place, and the press continued under a different name.
Place-keying is also the form process recipes (ladder rung 2) will
require: a dying recipe's stalled subgoal must poison the place,
or the lap recipe dies with the stalled turn-in cohort.

**Independent Test**: Store several recipes pointing at one place
and one pointing elsewhere; stall the shared place. All recipes
pointing at it become ineligible in the same selection step (zero
fallback presses); the elsewhere recipe remains selectable
throughout.

**Acceptance Scenarios**:

1. **Given** N recipes whose current pointers resolve to the same
   place, **When** that place's stall budget is exhausted, **Then**
   all N are ineligible at once — no successor from the cohort is
   selected at that place while the poison holds.
2. **Given** a recipe whose current pointer resolves elsewhere,
   **When** a different place is poisoned, **Then** that recipe's
   eligibility and value are unchanged.
3. **Given** a poisoned place, **When** a poisoned recipe's pointer
   would now resolve to a different (unpoisoned) place — the body
   moved on, so its nearest-step-plus-one changed — **Then** the
   recipe is eligible again through that new place: poison sticks
   to the place, never to the recipe.

---

### User Story 4 - The mechanism is watchable (Priority: P3)

A person running a long life (or the larder arena) wants to read
whether futility fired, how often, and at what places — from
bounded counters, without logs or instrumentation forks.

**Why this priority**: Every mechanism since the watch-counter
pattern landed (`advance_events`, `out_of_context`) ships with its
own bounded meters; the arena's registered analysis reads them.

**Independent Test**: Run a stall-and-revive scenario; the counters
report the fatigue and revival events that visibly occurred, and
memory stays bounded regardless of life length.

**Acceptance Scenarios**:

1. **Given** a life with stalls, **Then** bounded counters expose
   fatigue events (places poisoned) and revival events (poisons
   expired), in the existing watch-counter style.
2. **Given** an arbitrarily long life, **Then** futility state
   (stall counts, active poisons) is bounded — expired poisons
   leave no residue.

---

### Edge Cases

- Stall accumulates only on FOLLOWED steps — steps where a recipe
  is selected and its subgoal is live. Steps where the layer is
  inert (empty memory, event head off, all places poisoned) never
  count toward any place's stall budget.
- Two places within pointer-resolution distance of each other: the
  place key is quantized at the policy's existing position scale
  (block grain at C1); a poison covers exactly the places that
  quantize to its key — adjacent stations are distinct places.
- The pointer advances on the very step K is reached: advance wins
  — the count resets, no poison.
- All recipes poisoned simultaneously: the policy degrades to its
  parent (User Story 1, scenario 2) — this is the measured wander
  phase of the revive-peek-wander loop, not an error.
- Poison expiry while the body is far away: the place simply
  becomes eligible again; nothing forces a return trip (revival
  restores eligibility, the drive does the rest).
- Snapshot/restore: recipes are deliberately policy-side, not
  snapshot state (feature 041's recorded assumption); futility
  state follows the same rule — a restored brain starts with clean
  stall counts and no poisons, and the spec records this.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: `RecipePolicy` gains keyword-only constants
  `futility_k: int = 0` (stall budget, in followed steps) and
  `futility_w: int = 800` (poison duration, in steps); `futility_k
  = 0` disables the mechanism entirely.
- **FR-002**: Constants are validated at construction: `futility_k
  ≥ 0`, `futility_w > 0`, both finite integers; violations raise
  ValueError.
- **FR-003**: Off means off — with `futility_k = 0` the policy
  performs no additional arithmetic on the value path, consumes no
  RNG, and produces byte-identical action streams to v2.2.0.
- **FR-004**: The stall signal is the existing subgoal pointer: a
  followed step whose pointer does not advance increments the
  stall count of the CURRENTLY POINTED place; a pointer advance
  resets the count of the place it advanced from.
- **FR-005**: When a place's stall count reaches `futility_k`, the
  place is poisoned for `futility_w` steps. Poison is keyed to the
  quantized place (the subgoal position at the policy's position
  scale), never to a recipe identity.
- **FR-006**: Recipe selection excludes any recipe whose current
  pointer resolves to a poisoned place. With no eligible recipe the
  policy is exactly its parent for that step (the existing inert
  path).
- **FR-007**: A poison expires after `futility_w` steps and is
  removed; the place's stall count restarts at zero (revival is a
  clean peek, not a resumed countdown — the refuted hysteresis
  form is explicitly not this).
- **FR-008**: The two refuted forms are excluded by construction
  and covered by tests: no per-recipe erosion state exists
  (boundary thrash), and no per-recipe dead-time exists (cohort
  fallback) — the ONLY futility state is per-place.
- **FR-009**: Bounded watch counters in the existing style:
  `fatigue_events` (poisons created) and `revive_events` (poisons
  expired); active futility state is bounded by the number of
  currently poisoned places.
- **FR-010**: Pure policy mechanics — no engine, persistence,
  observation-contract, or anatomy changes; futility state is
  policy-side and not snapshot state (matching feature 041's
  recorded recipe-state assumption).

### Key Entities

- **Place**: a quantized subgoal position (the policy's existing
  position channels at its position scale) — the unit futility
  attaches to.
- **Stall count**: per-place count of consecutive followed steps
  without pointer advance while pointing at that place; reset by
  advance or poison.
- **Poison**: a place key plus remaining duration; while live it
  removes every recipe currently pointing at that place from
  selection. Expires to nothing.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: With defaults, the full regression gate is green and
  the feature's off-is-off test shows byte-identical behavior —
  zero change for every existing user.
- **SC-002**: In the blocked-path scenario, no futile engagement
  exceeds the stall budget: continuous pressing at a blocked place
  is bounded by K followed steps per engagement (measured baseline
  without the mechanism: 4,672 steps of one life).
- **SC-003**: The re-check emerges: after each poison expires, the
  place is re-pointed within one revival window — a path that
  UNBLOCKS is rediscovered without any new mechanism firing.
- **SC-004**: No boundary thrash: die/revive events per life are of
  the order of genuine stall episodes (one poison per engagement,
  plus one per peek) — not hundreds per life (refuted form: 556).
- **SC-005**: No cohort fallback: in the shared-place test, presses
  at the poisoned place by ANY recipe are zero while the poison
  holds, and the elsewhere-pointing recipe keeps its measured
  selection rate.

## Assumptions

- Default constants follow the prototype of record (K = 200,
  W = 800, episode 0120) as the DOCUMENTED recommended dials; the
  shipped default is off (`futility_k = 0`) per the standing
  opt-in rule. The larder arena revival (design 0021) is where the
  dials get their next measured reading.
- "Place" quantization at the policy's existing
  `position_indices`/`position_scale` grain (block grain at C1) is
  sufficient identity for poisoning; no world declares places.
- Futility state is not snapshot state, matching the feature-041
  assumption that recipes themselves are reconstructible
  policy-side state; if recipes ever enter snapshots, futility
  state re-opens with them.
- The rig-level prototype's layer-wide fatigue (everything died
  together because every recipe pointed at the gate) is the
  degenerate case of place-keying when all pointers coincide — the
  measured crossings therefore carry over to the promoted form.
- The arena/rig stays research furniture: this feature ships the
  kernel mechanism and its unit/behavior tests only; running the
  larder loop is a research act under design 0021, not part of
  this feature's gate.
