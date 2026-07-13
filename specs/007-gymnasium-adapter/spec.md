# Feature Specification: The Gymnasium Adapter

**Feature Branch**: `007-gymnasium-adapter`
**Created**: 2026-07-13
**Status**: Draft
**Input**: User description: "The Gymnasium adapter (ROADMAP B2): a GymnasiumBody
that mounts any Gymnasium environment behind PRA's Body/EventSource seams —
discrete actions, continuous observations, explicit termination semantics,
deterministic seeding, optional dependency, CartPole worked example."

## Overview

Today PRA learns from worlds written against its own seams: the synthetic
reference family, the ladder rungs, and whatever a user hand-writes against
the Sensor/Actuator protocols. Gymnasium is the ecosystem where hundreds of
ready-made worlds already live — CartPole, MountainCar, LunarLander — with an
API makers already know. One adapter unlocks all of them at once: mount a
Gymnasium environment as a PRA body, run the unchanged engine on it, and get
the same deterministic, byte-reproducible run summaries every other PRA world
produces.

The adapter must resolve one genuine impedance mismatch **explicitly**, not by
accident: PRA episodes are fixed-length (the engine runs `steps_per_episode`
steps, unconditionally), while Gymnasium episodes end when the environment
says so (`terminated`/`truncated`). Whatever the adapter does at that boundary
is a *learning-semantics decision* — it decides what transitions the brain
sees — so this spec names it, documents its consequences, and requires a test
that proves the chosen semantics actually happens in a real run.

Everything else follows the project's standing law: the validated behavior is
byte-frozen (this feature is purely additive — no engine or core edits), runs
are deterministic (same configuration and seed give byte-identical summaries,
which requires a stated per-reset seeding scheme that never touches the
engine's own random stream), and the new dependency is optional (the core
installs with numpy alone; the adapter names its missing dependency clearly).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Mount a Gymnasium world and run the engine on it (Priority: P1)

A maker who knows Gymnasium picks an environment with a discrete action space
and a continuous observation vector (CartPole: 4 observation channels, 2
actions — inside PRA's validated range today), wraps it in the adapter body,
sets the two matching configuration numbers (observation size, action count),
and runs the unchanged engine on it. Observations arrive at the brain as
float64 vectors; the brain's action indices drive the environment. Two runs
with the same configuration and seed produce byte-identical run summaries.

**Why this priority**: This is the adapter itself — without it nothing else
in the feature exists. Determinism is part of this story, not a follow-up:
a Gymnasium run that cannot be reproduced byte-for-byte would be the first
non-reproducible mode in the project, which the roadmap's operating
principles forbid.

**Independent Test**: Can be fully tested by running the engine on a wrapped
CartPole across a small schedule, twice with the same seed, and comparing
serialized summaries byte-for-byte — with no example file and no
documentation present.

**Acceptance Scenarios**:

1. **Given** a Gymnasium environment with a discrete action space and a
   continuous observation vector, **When** it is wrapped in the adapter body
   and the engine runs on it, **Then** the run completes to a normal per-seed
   summary, observations crossing the seam are float64 vectors of the
   declared width, and every action the environment receives is a valid
   member of its own action space.
2. **Given** the same configuration and seed, **When** the run is repeated,
   **Then** the serialized run summaries are byte-identical.
3. **Given** two different seeds, **When** the runs complete, **Then** the
   summaries differ (the seed actually reaches the environment).
4. **Given** an environment whose sizes do not match the configuration's
   observation size or action count, **When** the body is mounted through the
   factory, **Then** mounting fails immediately with a message naming both
   numbers — never a shape error deep inside a run.

---

### User Story 2 - The termination boundary is explicit, documented, and tested (Priority: P2)

A researcher runs PRA on an environment that ends its own episodes (CartPole
terminates when the pole falls — under a random policy, within a few dozen
steps). PRA's episode keeps going: the adapter immediately respawns the
environment (a fresh seeded reset) and the PRA episode continues to its fixed
length. The researcher can read, in the feature documentation, exactly what
the brain experiences at that boundary — an action whose outcome is an
unpredictable teleport to a fresh start state — and can see from the adapter's
own counters that respawns actually happened during their run.

**Why this priority**: This is the named design question of ROADMAP B2. It is
P2 only because the adapter (US1) must exist before its boundary semantics
can be observed; it is the part of the feature most likely to silently
mislead users if left implicit.

**Independent Test**: Can be fully tested with a scripted fake environment
that terminates after a known number of steps: the adapter must reset it
mid-PRA-episode, discard the terminal observation, return the respawn
observation as the step's outcome, and count the respawn — plus one real
CartPole run asserting the respawn counter is positive under the random
policy.

**Acceptance Scenarios**:

1. **Given** an environment that reports `terminated` (or `truncated`) on a
   step, **When** the adapter applies that action, **Then** the environment
   is immediately reset with the next seed in the adapter's seed sequence,
   the observation returned for that step is the fresh reset observation,
   and the PRA episode continues uninterrupted.
2. **Given** a full engine run on CartPole under the pinned random policy,
   **When** the run completes, **Then** the adapter's respawn counter is
   greater than zero — the semantics is exercised, not just implemented.
3. **Given** the feature documentation, **When** a user looks up what happens
   at termination, **Then** the semantics and its stated consequence for
   learning (the boundary transition is irreducibly unpredictable, like the
   ladder's unlearnable region) are written down, including the alternatives
   that were rejected and why.

---

### User Story 3 - The CartPole worked example: a newcomer's second stop (Priority: P3)

A newcomer who has read the getting-started guide opens `examples/`, finds a
single heavily-commented CartPole script, runs it with the optional
dependency installed, and watches the engine learn on a world they recognize
— completing in well under a minute, printing the honest per-seed summary,
and proving its own determinism by running the seed twice and comparing
bytes.

**Why this priority**: The example is the roadmap exit criterion's visible
half, but it is pure composition of US1 + US2 — nothing in it can work before
they do.

**Independent Test**: Run the example script in a fresh shell; it exits
successfully in under a minute and prints a summary plus a determinism
verdict.

**Acceptance Scenarios**:

1. **Given** an installation with the optional dependency, **When** the user
   runs the example, **Then** it completes in under a minute, prints the run
   summary in plain language, reports the respawn count, and shows the
   byte-identity of a repeated seed.
2. **Given** an installation without the optional dependency, **When** the
   adapter module is used, **Then** the failure is a clear error naming the
   missing package and the install command — not a bare import traceback
   from somewhere inside the adapter.

---

### Edge Cases

- An action space whose labels do not start at zero (Gymnasium's `Discrete`
  has a configurable start): the adapter maps PRA's local action index onto
  the environment's own labels — index 0 is the space's first action, always.
- A multi-dimensional continuous observation (an image-like Box): flattened
  in a fixed, documented order into one vector; the declared width is the
  element count. (Whether such a world is *learnable* at today's validated
  scales is the user's experiment; the adapter's job is only to be honest
  about sizes.)
- Reading the sensor before the first reset: rejected with the same
  body-contract error the existing world sensor raises.
- Unsupported spaces — continuous (Box) *action* spaces, and discrete /
  dict / tuple *observation* spaces: rejected at mount time with a message
  naming the offending space; never a silent cast. Box-action support is a
  documented non-goal of v1.
- Snapshot/resume of a Gymnasium-mounted run: **not supported in v1** — the
  environment's internal state cannot be re-derived from PRA's seed stream
  the way the built-in worlds' can, so a resumed run would silently diverge
  from the uninterrupted one. Documented here and in the adapter; the honest
  persistence story for external worlds is ROADMAP B5's work.
- The environment's reward, info dict, and terminal observation: discarded,
  and *documented* as discarded. PRA has no reward channel — motivation is
  intrinsic (the drive) — so the adapter must not pretend otherwise.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST provide an adapter body that mounts any
  Gymnasium environment with a discrete action space and a continuous
  (Box) observation space behind the existing body seam, so the engine,
  drives, and validation harness run on it unchanged.
- **FR-002**: The adapter MUST convert every environment observation to a
  one-dimensional float64 vector of a declared, fixed width (multi-dimensional
  observations flattened in a fixed, documented order), and MUST expose
  exactly the existing world surface — begin an episode, step under an
  action, observation size, action count — with nothing else (no reward, no
  termination flags, no info) crossing into the learning system.
- **FR-003**: The adapter MUST map PRA's local action index onto the
  environment's own action labels, including action spaces that do not start
  at zero, and MUST declare the action count from the environment's space.
- **FR-004**: On an environment-terminated or truncated step, the adapter
  MUST immediately reset the environment with the next seed in its
  deterministic seed sequence and return the fresh reset observation as that
  step's outcome — the PRA episode continues at its fixed length ("the world
  respawns"). The terminal observation is discarded. The adapter MUST count
  respawns and expose the count outside the learning surface.
- **FR-005**: A run on a seeded Gymnasium environment MUST be deterministic:
  the same configuration and seed produce byte-identical serialized run
  summaries. Every environment reset (episode starts and respawns alike)
  MUST be seeded from a deterministic sequence derived from the run's seed,
  and the adapter MUST NOT draw from — or otherwise perturb — the engine's
  own random generator.
- **FR-006**: The Gymnasium dependency MUST be optional: the core package
  keeps its numpy-only install; the adapter ships in a named optional extra
  and in the development extra (so the quality gate always exercises its
  tests — none skipped); using the adapter without the package installed
  MUST fail with a clear error naming the package and the install command.
- **FR-007**: Environments the adapter does not support (non-discrete action
  spaces; non-Box observation spaces) MUST be rejected at mount time with a
  message naming the offending space, and a factory-mounted body whose sizes
  do not match the run configuration MUST be rejected at mount time with a
  message naming both numbers.
- **FR-008**: The feature MUST be purely additive: no engine or core edits;
  every existing test and recorded reference value stays byte-identical; the
  adapter is opt-in by construction (nothing references it unless imported).
- **FR-009**: The repository MUST ship a worked CartPole example in a new
  `examples/` directory — minimal, heavily commented, runnable in under a
  minute — that builds the adapter, runs the engine, prints the summary and
  respawn count, and demonstrates byte-identical reproduction of its seed.
- **FR-010**: The termination-semantics decision (FR-004) MUST be recorded in
  this feature's documentation with its consequences for learning and the
  rejected alternatives, and MUST be exercised by tests (a scripted
  fake-environment test of the boundary mechanics, plus a real-environment
  run asserting respawns occurred).

### Key Entities

- **Adapter body**: the mounted composition — a Gymnasium environment wrapped
  as an event source plus the sensor/actuator pair the body layer already
  understands; presents exactly the existing world surface to the engine.
- **Seed sequence**: the deterministic per-reset seed scheme — derived once
  from the run's seed at mount time, indexed by reset count (episode starts
  and respawns alike), independent of the engine's generator.
- **Respawn**: the adapter's answer to environment termination — an
  immediate seeded reset whose observation stands in as the step outcome;
  counted, and readable outside the learning surface.
- **Worked example**: the CartPole script in `examples/` — the newcomer's
  second stop after the getting-started guide.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A CartPole run under the adapter, repeated with the same
  configuration and seed, produces byte-identical serialized summaries; runs
  under different seeds differ.
- **SC-002**: The full existing validation suite passes with its recorded
  reference values byte-identical after the adapter ships (zero behavioral
  drift in every validated mode), and the core install still requires numpy
  only.
- **SC-003**: The worked example completes in under one minute on a
  developer laptop and prints a per-seed summary, a respawn count, and a
  determinism verdict a newcomer can read without opening source code.
- **SC-004**: The adapter's contract is covered by tests: surface conformance
  (event-source protocol, float64 widths, action mapping including nonzero
  start), every rejection path (action space, observation space, size
  mismatch, missing dependency, read-before-reset), the respawn boundary
  mechanics on a scripted environment, and a positive respawn count on real
  CartPole.
- **SC-005**: The termination decision and the per-reset seeding scheme are
  documented in the feature's spec/research record before the first release
  of the adapter, including rejected alternatives.
- **SC-006**: Installing the named optional extra is sufficient to run the
  example (`pip install "poseres[gym]"` or the development extra).

## Assumptions

- **Discrete action spaces only in v1.** Continuous (Box) action spaces are
  out of scope and documented as such: PRA's action surface is a discrete
  index into the body's actuators (Doc 02); a principled discretization of
  continuous action spaces is future adapter work, not a hidden default.
- **Continuous (Box) observation spaces only in v1.** Discrete, dict, tuple,
  and text observation spaces are out of scope; multi-dimensional Box
  observations are supported by flattening.
- **Determinism is conditional on the Gymnasium convention.** The adapter
  guarantees byte-identical runs for environments whose stochasticity flows
  entirely through the seeded reset (`env.reset(seed=...)` seeding the
  environment's own generator — the Gymnasium API contract). An environment
  that consults outside randomness breaks its own reproducibility, not the
  adapter's.
- **Reward is discarded in v1.** PRA is not a reward-maximizing RL agent;
  motivation is intrinsic and structurally immutable (Doc 05). Exposing the
  environment's reward as an optional extra *sensor* is plausible future
  work; silently wiring it into the drive would misrepresent the
  architecture.
- **The engine's fixed-length episode semantics is not negotiable here.**
  Adapting PRA's episode length to the environment's own boundaries would be
  an engine-semantics change (ROADMAP B3's territory, with a written design
  first). The adapter conforms the world to the engine, not the engine to
  the world — that is what keeps this feature purely additive.
- **Snapshot/resume for externally-stateful worlds is B5's work.** V1
  documents the limitation loudly rather than shipping a resume that would
  silently diverge.
- **CartPole's scale is inside the validated range** (4 observation channels
  against the reference 10; 2 actions against the reference 4), so the
  worked example makes no scaling claim; larger Gymnasium worlds are the
  user's experiment, with the scale rules keying off total observation size
  as everywhere else.
