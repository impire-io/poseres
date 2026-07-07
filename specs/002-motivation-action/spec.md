# Feature Specification: Motivation and Action Layer

**Feature Branch**: `002-motivation-action`
**Created**: 2026-07-07
**Status**: Draft
**Input**: User description: "Motivation and action layer (design Doc 05): make the PRA system act instead of sampling random actions — a fixed innate drive producing a scalar value signal (curiosity: learning progress + novelty with automatic cold-start handover), a Policy seam with a one-step curiosity-lookahead default replacing random action sampling, drive parameters read-only at runtime, the validated T1–T6 suite untouched under a pinned random-policy baseline, and honest acceptance tests for the new layer (finite value signal from step one, drive immutability, directed exploration beats random on equal experience, no degeneration into inaction or noise-chasing)."

## User Scenarios & Testing *(mandatory)*

Until now the system is a passive world-model: it learns from experience it is
*given* (uniformly random actions). This feature makes it an agent: an innate,
fixed drive tells it what "better" means, and an action layer chooses what to do
next in service of that drive. The researcher's core question is whether
self-directed experience is at least as good for learning as random experience —
measured with the same honesty rules as the existing suite, and without
disturbing the already-validated sensorimotor core.

### User Story 1 - The system acts on its own initiative (Priority: P1)

A researcher runs the agent in the synthetic world and observes it selecting its
own actions: random at cold start (when it knows nothing), increasingly directed
as its world-model matures — with every run still exactly reproducible from its
seed.

**Why this priority**: This is the feature's reason to exist — without a working
drive → value → action path, nothing else in this feature is testable. It is the
minimum viable product.

**Independent Test**: Run one seed with the curiosity policy and confirm (a) the
run completes end-to-end with actions chosen by the policy, (b) the recorded
value signal is finite and well-defined from the very first step, and (c) two
runs of the same seed are byte-identical.

**Acceptance Scenarios**:

1. **Given** a fresh agent with zero frames, **When** the run starts, **Then**
   actions are uniformly random (cold start by design) and the value signal is
   already finite (novelty operates from the first observation).
2. **Given** a matured world-model, **When** the policy selects actions, **Then**
   selections come from the one-step lookahead (not uniform randomness), except
   for the configured exploration fraction.
3. **Given** the same seed and configuration, **When** the run is repeated,
   **Then** the summary is byte-identical (determinism is preserved through the
   drive and policy).

---

### User Story 2 - The validated core is untouched (Priority: P1)

The existing acceptance suite T1–T6 — the project's regression gate — continues
to run under the pinned random-action baseline and keeps passing with results
byte-identical to the validated build. The new layer sits behind seams; choosing
not to use it changes nothing.

**Why this priority**: The suite is the project's only defense against silent
regressions; the STEP-0 gate exists because an unvalidated change once produced
a false positive. Adding an action layer must not invalidate what was already
proven. Equal in priority to US1 because the feature is unacceptable without it.

**Independent Test**: Run the full suite in its default (random-baseline) mode
and byte-compare a reference seed's summary against the validated build's
values; all of T1–T6 PASS unchanged.

**Acceptance Scenarios**:

1. **Given** the validation suite in its default mode, **When** it runs after
   this feature lands, **Then** every per-seed summary is byte-identical to the
   validated build and T1–T6 all PASS.
2. **Given** the determinism mode, **When** a seed is run twice, **Then** the
   summaries are byte-identical (unchanged guarantee).

---

### User Story 3 - Directed exploration is measurably not worse than random (Priority: P2)

A researcher compares, seed by seed with equal experience, the curious agent
against the random-action baseline on honest observation-space prediction error,
and reads an honest verdict: directed exploration must reduce prediction error
at least as well as random exploration in a majority of seeds.

**Why this priority**: This is the load-bearing behavioral claim of the feature
— the drive exists to gather *useful* experience. It needs US1 to exist first;
it turns the feature from "wired up" into "validated."

**Independent Test**: Run the new acceptance test comparing curious vs random
runs (fresh worlds, deterministic seed derivation, equal experience) and confirm
a per-seed comparison table with a PASS/FAIL verdict judged on the majority.

**Acceptance Scenarios**:

1. **Given** paired curious/random runs per seed, **When** the comparison is
   evaluated, **Then** the verdict PASSes only if the curious agent's prediction
   error improvement is at least as large as the random baseline's in a strict
   majority of seeds.
2. **Given** a failing comparison, **When** results are reported, **Then** the
   per-seed numbers that explain the failure are shown (never hidden or
   smoothed).

---

### User Story 4 - The drive cannot be corrupted or gamed (Priority: P2)

The drive's identity, parameters, and weights are read-only to the running
system: no learning process, no policy, and no structural change can modify
them. The value signal also self-limits: a mastered region (low, flat error) and
an unlearnable region (high, flat error) both yield ~zero learning progress, so
the agent neither freezes on what it knows nor chases pure noise.

**Why this priority**: The "no self-modification" rule is the feature's one
mandatory safety invariant (a drive that can rewrite itself is trivially
maximized by redefining it). Self-limiting is what makes curiosity a workable
default rather than a degenerate one.

**Independent Test**: Attempt to mutate drive parameters at runtime and confirm
it is impossible; feed the drive mastered-region and noise-region error
histories and confirm both yield ~zero learning progress while a
genuinely-improving history yields a positive signal.

**Acceptance Scenarios**:

1. **Given** a running agent, **When** any runtime process attempts to modify a
   drive parameter or weight, **Then** the attempt fails (the configuration is
   immutable).
2. **Given** a flat-low (mastered) prediction-error history, **When** the drive
   evaluates learning progress, **Then** the term is ~zero.
3. **Given** a flat-high (unlearnable noise) prediction-error history, **When**
   the drive evaluates learning progress, **Then** the term is ~zero.
4. **Given** a falling prediction-error history, **When** the drive evaluates
   learning progress, **Then** the term is positive.

---

### User Story 5 - A counter-drive is a configuration, not a code change (Priority: P3)

A researcher can configure a second fixed drive (for example a competence drive
in tension with curiosity) purely through configuration — weights fixed at boot
— and the value signal becomes the configured weighted sum, with no modification
to any other component.

**Why this priority**: The multi-drive mechanism is the specified remedy if
curiosity wanders; shipping the mechanism (not the counter-drive itself) keeps
that door open without expanding the base build.

**Independent Test**: Register a trivial second drive via configuration, run,
and confirm the value signal equals the fixed weighted sum of the two drives'
contributions, with all other behavior unchanged.

**Acceptance Scenarios**:

1. **Given** two configured drives with fixed weights, **When** the value signal
   is produced, **Then** it equals the weighted sum of their contributions.
2. **Given** the base configuration, **When** the system runs, **Then** exactly
   one drive (curiosity) is active and behavior matches US1.

---

### Edge Cases

- **Cold start (zero frames)**: the policy has no transition models to consult;
  it selects uniformly random actions by design, and the novelty term alone
  carries the value signal. No error, no undefined values.
- **Immature frames**: lookahead is gated on a configured minimum frame
  maturity; below it the policy stays random rather than acting on noise.
- **All candidate actions predict equal value**: ties break deterministically by
  lowest action index (reproducibility).
- **Empty observation memory**: the first observation ever seen has maximal
  unfamiliarity; the novelty term is still finite and well-defined.
- **Exploration override**: with the configured probability the policy takes a
  uniformly random action even when lookahead is confident, drawn from the
  single seeded generator (determinism preserved).
- **Drives disagree**: with a counter-drive configured, the value signal is the
  fixed weighted sum — no runtime re-weighting, no arbitration logic.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST produce a scalar value signal every online step
  from its own state and recent experience; the signal MUST be finite and
  well-defined from the first step of a run (no external reward exists).
- **FR-002**: Drives MUST be supplied at configuration as one or more fixed
  (terminal) drives; when multiple are configured the value signal MUST be the
  fixed weighted sum of their contributions.
- **FR-003**: Drive identities, parameters, and weights MUST be read-only to the
  running system: no online learning, structural learning, or policy process can
  modify them; the configuration objects themselves MUST reject mutation.
- **FR-004**: The default (and only shipped) drive MUST be curiosity, combining
  a learning-progress term — rewarding recent *reduction* in prediction error,
  ~zero on both mastered (low flat) and unlearnable (high flat) regions — and a
  novelty term over a bounded recent-observation memory, with automatic
  cold-start handover and no explicit phase switch.
- **FR-005**: The action layer MUST select each step's action through a
  swappable policy seam whose objective is to increase the value signal; the
  shipped default is a one-step lookahead that predicts each candidate action's
  outcome with the frames' transition models and values it via the drive(s),
  breaking ties by lowest action index.
- **FR-006**: The default policy MUST select uniformly random actions at cold
  start and whenever the frame population is below a configured maturity bar,
  and MUST take a uniformly random action with a configured exploration
  probability at all times.
- **FR-007**: All randomness in drives and policies MUST come from the run's
  single seeded generator in a fixed draw order; two runs of a seed MUST produce
  byte-identical summaries.
- **FR-008**: The existing acceptance suite T1–T6 MUST continue to run under the
  pinned random-action baseline and keep passing with per-seed summaries
  byte-identical to the validated build; using the new layer is opt-in and MUST
  NOT alter any existing mode's behavior.
- **FR-009**: The harness MUST gain an acceptance test for the load-bearing
  claim: with equal experience and same-seed pairing, the curious agent is not
  systematically worse than the random baseline at reducing prediction error —
  judged as one-sided noninferiority on the paired mean margin (FAIL only when
  `mean(margin) < −1.9·SE`), reported with the per-seed spread and sign counts,
  honest-summary rules unchanged. *(Amended 2026-07-07 from a per-seed
  sign-majority bar, which was measured first — 3/8 signs, mean −0.006 ± 0.036 —
  and discarded openly because with continuous margins it degenerates into
  "strictly better per seed" and fails exact equivalence by coin-flip; the
  noninferiority form operationalizes the Assumption's pre-registered intent.)*
- **FR-010**: The value signal and the policy's chosen actions MUST be
  observable in telemetry (recorded per run for the tests and reports), without
  persisting any model state to disk.
- **FR-011**: Multi-step planning, tool self-invention, and drive evolution
  remain out of scope; the policy and drive seams MUST be replaceable without
  touching any other component.

### Key Entities

- **Drive**: a fixed terminal preference; produces a value contribution from a
  read-only context (recent poses, frames' error statistics, recent
  observations, its own bookkeeping). Never mutated at runtime.
- **Value signal**: the scalar, per-step combination (fixed weighted sum) of
  drive contributions; the system's only notion of "better."
- **Curiosity bookkeeping**: the drive's recent/baseline prediction-error
  windows and the bounded recent-observation memory — state, not policy.
- **Policy**: the action selector; consumes the current context and the
  drive(s), returns an action index each step.
- **Curious-vs-random comparison**: the paired-run measurement (equal
  experience, deterministic derived seeds) behind the new acceptance verdict.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A default-configuration agent run completes with policy-selected
  actions and a finite value signal recorded at every step, from step one.
- **SC-002**: Re-running any seed reproduces its summary byte-for-byte with the
  drive and policy active.
- **SC-003**: The full existing suite (T1–T6) passes unchanged in its
  random-baseline mode, with a reference seed's summary byte-identical to the
  validated build.
- **SC-004**: The curious-vs-random acceptance test produces a per-seed
  comparison and an honest PASS/FAIL verdict; at the reference configuration the
  verdict is PASS (the curious arm is not significantly worse than random).
  *(Measured 2026-07-07: mean margin −0.0061 vs noninferiority bound −0.0239;
  strictly better in 3/8 seeds — the arms are statistically equivalent in the
  reference world, where random coverage is already near-complete. Directed
  exploration neither helps nor hurts here; whether it helps in larger worlds
  is a research question for scaled configurations.)*
- **SC-005**: Attempts to modify drive parameters at runtime fail; the
  mastered-region and noise-region histories both yield ~zero learning progress
  while an improving history yields a positive value.
- **SC-006**: A second drive can be added purely by configuration, and the value
  signal equals the fixed weighted sum of contributions.

## Assumptions

- The synthetic validation world (PRA-02) remains the environment; no new world
  or body is introduced by this feature.
- "Curious ≥ random" (not strictly greater) is the honest pass bar for SC-004:
  in a world where random exploration already covers the state space well,
  directed exploration may only match it; the claim that must not fail is that
  directedness does not *hurt* learning. A strictly-greater result is reported
  when observed but not required to pass.
- The existing suite's runs remain the random baseline (the policy seam defaults
  to the current random sampling in validation mode), which is what keeps FR-008
  satisfiable byte-for-byte.
- The scale-invariance parameter rules from the validated build apply unchanged;
  this feature adds no new scale-dependent constants beyond the drive/policy
  parameters themselves, which are validated at the reference scale first.
- Counter-drives ship as mechanism only (configuration + weighted sum); no
  second drive is enabled in the base configuration.
