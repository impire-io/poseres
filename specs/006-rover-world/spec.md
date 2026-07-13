# Feature Specification: The Watchable Rover World

**Feature Branch**: `006-rover-world`
**Created**: 2026-07-13
**Status**: Draft
**Input**: User description: "The watchable rover world (ROADMAP B1): an
in-repo 2D rover world with a built-in live web viewer — one command, a
browser tab opens, you watch frames learn the map. Deterministic,
resettable, zero extra dependencies. This — not any branded game — is the
getting-started experience."

## Overview

Everything the project has validated so far is invisible: the system learns
a synthetic world nobody can see, and the proof is a table of numbers. The
watchable rover world is the first artifact whose *product is the watching*:
a small two-dimensional world — a rover, an arena, obstacles — where a
newcomer runs one command, a browser tab opens, and they see the rover
wander while the brain's honest telemetry moves in real time: prediction
error falling, the frame population breathing, the selected structure
settling. Nothing about the learning is new; what is new is that a person
can stand in front of it.

Two properties are non-negotiable, because they are the project's identity.
First, the demo runs through the **unchanged engine** on the **existing
seams** — the rover world is a body of named sensors and actuators mounted
exactly where the synthetic world mounts, which makes B1 the showcase of the
anatomy layer, not a fork of the system. Second, **watching must cost
nothing**: the viewer observes the run without perturbing it — the same run
with the viewer on and off produces byte-identical summaries, and the
example run reproduces byte-for-byte on re-run. A demo that changed what it
demonstrated would be worthless here; determinism is the feature.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A rover world behind the existing seams (Priority: P1)

A user creates a deterministic 2D rover environment — an arena with
obstacles, a rover with distance sensors, a compass, a position beacon, and
a bump detector, driven by a small set of movement actions — and runs the
existing engine on it, unchanged. The world is seeded and resettable: each
episode begins the rover at a fresh pose, the same seed and configuration
reproduce the same run byte-for-byte, and the learning system sees only
observation vectors and an action count — never positions, headings, or the
map.

**Why this priority**: The world is the substrate everything else in this
feature stands on. It is independently valuable without any viewer — a
second in-repo environment (the first that is *spatial* rather than
abstract-latent) proves the anatomy layer carries a genuinely different
world through the same seams, and it is usable by library users and future
drive research immediately.

**Independent Test**: Can be fully tested by mounting the rover body on the
engine, running a seed to a summary, re-running it, and comparing the
serialized summaries byte-for-byte — no viewer, no command, no browser.

**Acceptance Scenarios**:

1. **Given** the rover body mounted on the unchanged engine, **When** a
   seed runs to completion, **Then** it produces the standard per-seed
   summary (prediction error, population, best structure size) exactly as
   the reference world does.
2. **Given** the same configuration and seed, **When** the run is repeated,
   **Then** the serialized summaries are byte-identical.
3. **Given** the mounted rover body, **When** the learning system inspects
   its world surface, **Then** it can reach only the observation vector and
   the action-space size — no pose, no map, no layout.
4. **Given** an episode boundary, **When** the world resets, **Then** the
   rover begins at a freshly drawn pose, mirroring the reference world's
   per-episode reset semantics.

---

### User Story 2 - The live viewer that costs nothing (Priority: P2)

A user starts a rover run with the built-in viewer and opens the printed
URL in any modern browser. They see, live while the engine runs: the arena
and its obstacles, the rover moving with its trail, and the learning
telemetry — the prediction-error trend, the frame-population size, and the
currently selected structure size (best_dim). The page needs no build step,
no internet access, and no installed dependencies beyond the project
itself. Closing the tab, polling it from several windows, or never opening
it at all changes nothing about the run: with the viewer on or off, the
run's summary is byte-identical.

**Why this priority**: The viewer is the visible half of the exit
criterion, but it is meaningless without US1's world — and its defining
constraint (observe without perturbing) is only testable once a
deterministic world exists to perturb.

**Independent Test**: Can be fully tested without a browser: start the
viewer against a running engine, fetch its endpoints over HTTP, assert the
served state carries pose, trail, and learning telemetry — then compare the
run summary byte-for-byte against the same run with no viewer attached.

**Acceptance Scenarios**:

1. **Given** a run with the viewer serving, **When** the state endpoint is
   polled mid-run, **Then** it returns the rover's pose and recent trail
   and the current learning telemetry (prediction-error reading, population
   size, best_dim, step and episode counters).
2. **Given** the same configuration and seed, **When** one run executes
   with the viewer attached and polled, and one runs with no viewer,
   **Then** their serialized summaries are byte-identical.
3. **Given** the viewer page, **When** it is loaded, **Then** it is a
   single self-contained page (no external resources) that renders the
   world map and telemetry from the served state alone.
4. **Given** a finished run, **When** the viewer is still open, **Then** it
   shows the run has completed together with the final summary readings.

---

### User Story 3 - One command, five minutes (Priority: P3)

A newcomer who has just installed the package types one command. It prints
the viewer URL (and opens a browser tab when running interactively), starts
a paced rover run they can actually watch, and — when the run finishes —
prints the same honest end-of-run summary the harness always prints, with
an optional machine-readable artifact. From a fresh install to watching
learning is under five minutes; the run they watched is byte-reproducible
with the same command and seed.

**Why this priority**: The command is the packaging of US1+US2 into the
getting-started experience the roadmap names. It composes the other two
stories and adds pacing and ergonomics, but no new world or viewer
capability.

**Independent Test**: Can be fully tested by invoking the command entry
point with a small configuration and no browser: it must print the URL,
run to completion, print the summary, write the JSON artifact when asked,
and exit cleanly.

**Acceptance Scenarios**:

1. **Given** a fresh install, **When** the user runs the rover command,
   **Then** the viewer URL is printed before the run starts and the
   process serves the viewer while running.
2. **Given** the default invocation, **When** the run executes, **Then**
   it is paced for watching (a stated steps-per-second dial), and the
   pacing dial changes wall-clock time only — never the run's bytes.
3. **Given** the command with a JSON output path, **When** the run
   completes, **Then** the canonical per-seed summary is written there and
   a human-readable summary is printed.
4. **Given** a non-interactive context (tests, CI, piped output), **When**
   the command runs, **Then** it never attempts to open a browser.

---

### Edge Cases

- The requested port is already in use → the command must fail with a
  clear message naming the port (or bind an ephemeral port when asked for
  port 0 and print the actual URL).
- The viewer is polled before the first step or between episodes → the
  state endpoint must answer coherently (empty trail, zero counters) and
  never error.
- A configuration override changes the observation width or action count
  away from the rover's anatomy → rejected at mount time with a message
  naming the mismatch, never a shape error deep in a run.
- A world layout so dense that no collision-free start pose exists → world
  construction must fail deterministically with a clear message, never
  loop forever.
- No browser is available on the machine → the command still runs and
  prints the URL; auto-open is attempted only in interactive terminals and
  its failure is never fatal.
- The run finishes while the viewer is open → the served state must say so
  (completed flag + final readings); the command holds the server open for
  watching until interrupted, except when asked to exit on completion.
- Concurrent state polls from several tabs → each gets a consistent
  snapshot; polling frequency must not affect the run.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST provide a deterministic, seeded 2D rover
  world: a bounded arena with obstacles, a rover with position and
  heading, and a small set of discrete movement actions (move and turn)
  whose effects are pure functions of the current pose and the action.
- **FR-002**: The rover's observations MUST be position-derived sensor
  readings rich enough to learn from — distance sensors toward obstacles
  and walls, heading and position readings, and a bump reading that
  reports blocked movement — with the world's stated sensor noise applied,
  totalling an observation width inside the validated range.
- **FR-003**: The rover world MUST mount through the anatomy layer as a
  body of named sensors and actuators (fixed order, meaning-free to the
  system) and present exactly the standard world surface to the unchanged
  engine: begin an episode, step under an action, expose only observation
  width and action count.
- **FR-004**: `reset()` MUST begin a new episode at a freshly drawn start
  pose, with per-episode semantics mirroring the reference world; the same
  `(configuration, seed)` MUST reproduce byte-identical run summaries on
  re-run.
- **FR-005**: Nothing on the system-visible surface may expose ground
  truth (pose, map, layout, spawn set); ground truth MUST be reachable
  only through harness/viewer-only accessors that the engine never calls.
- **FR-006**: The system MUST provide a built-in live viewer with zero
  dependencies beyond the standard library: a single self-contained page
  served by the run process, rendering the arena, obstacles, live rover
  pose and trail, and learning telemetry (prediction-error trend,
  population size, best_dim, step/episode counters) from a small
  machine-readable state endpoint.
- **FR-007**: The viewer MUST observe without perturbing: the tap that
  feeds it consumes no randomness and performs no floating-point work on
  the run path (recording is plain value copies; all derived computation
  happens off the run path), and run summaries MUST be byte-identical with
  the viewer on or off, however often it is polled.
- **FR-008**: The system MUST provide one console command that starts the
  run and the viewer together, prints the URL before the run begins,
  attempts to open a browser only in interactive terminals, prints the
  honest end-of-run summary, and optionally writes the canonical summary
  as a JSON artifact.
- **FR-009**: The command MUST offer a pacing dial (steps per second) so a
  human can watch the run; pacing MUST change wall-clock behavior only,
  never any byte of the run's results, and MUST be fully disengageable.
- **FR-010**: The feature MUST be purely additive: no changes to the
  engine, core, config semantics, or any validated behavior; every
  existing test and recorded reference value stays byte-identical.
- **FR-011**: Impossible setups MUST be rejected with a message naming the
  constraint: anatomy-width mismatches at mount time, unusable ports at
  serve time, and unsatisfiable world layouts at construction time.
- **FR-012**: All of the above MUST be testable without a browser: world
  behavior, determinism, viewer endpoints, and the command path have
  automated tests that drive HTTP and the library surface directly.

### Key Entities

- **Rover world**: the 2D environment — arena bounds, obstacle set, rover
  pose, movement rules, sensor model, spawn poses; owns its ground truth
  and its per-episode reset semantics.
- **Rover anatomy**: the named sensors (distance array, compass, position
  beacon, bumper) and the drive actuator, composed in fixed order into the
  standard body; the only thing the learning system ever sees.
- **Telemetry tap**: the observation channel between the run and the
  viewer — receives plain-value pose/step recordings from the world and
  read-only access to learning state; serves consistent snapshots to the
  viewer without touching the run.
- **Viewer**: the single self-contained page plus the small state/layout
  endpoints the run process serves.
- **Rover command**: the console entry point that wires world, engine,
  tap, viewer, pacing, and reporting together.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: From a fresh install, a newcomer reaches a live view of the
  learning rover in under five minutes using only documented commands —
  install, one command, open the printed URL.
- **SC-002**: The example run is byte-reproducible: the same command,
  configuration, and seed produce byte-identical serialized summaries
  across repeated runs (tested).
- **SC-003**: A run with the viewer attached and actively polled produces
  a summary byte-identical to the same run with no viewer (tested).
- **SC-004**: The full existing validation suite passes unchanged after
  the feature ships; zero behavioral drift in any validated mode.
- **SC-005**: The feature adds zero runtime dependencies: the viewer and
  command use only the standard library and the project's existing
  dependency.
- **SC-006**: The viewer communicates honestly what is shown: every
  telemetry reading displayed is an existing, defined quantity of the
  system (no invented or smoothed-for-effect metrics), labeled well enough
  that a newcomer can say what moved and why it matters.

## Assumptions

- **Reference-scale anatomy, deliberately.** The rover's anatomy is fixed
  at the validated reference widths (observation width 10, four actions),
  so the demo runs in exactly the regime every acceptance result was
  recorded in — all scale-rule factors are 1 there. Making the rover's
  sensor set configurable is future work; the world's internal dials
  (arena, obstacles, speeds) ship as stated constants.
- **The pinned random policy is the default demo policy**, matching how
  every validated result is produced. Watching a *directed* rover
  (curiosity/competence drives on the rover world) is deliberately left to
  the A4 drive research; the library mount makes it a one-line change.
- **Honest telemetry only.** The viewer displays quantities the system
  already defines (per-frame prediction-error EMAs, population size,
  best_dim, step/episode counters) sampled live; it invents no new
  metrics. The prediction-error trend shown is the best frame's survival
  EMA — the quantity the ecology is actually judged on.
- **Single-seed by default.** The demo is one watchable seed (seed
  selectable); multi-seed spreads remain the harness's job
  (`pra-validate`), and the command says so rather than implying a
  validated claim from one seed.
- **Snapshots/resume of rover runs are out of scope** for this feature.
  Nothing prevents them structurally (the world rebuilds from the seed
  prefix like the reference world), but the byte-identity claim for
  resumed rover runs is neither made nor tested here.
- **A separate command (`pra-rover`) rather than a `pra-validate`
  subcommand.** `pra-validate` is the measurement harness: multi-seed,
  verdict-producing, report-rendering. The rover is an experience:
  single-seed, long-running, serving HTTP. Folding an interactive server
  into the harness CLI would blur what `pra-validate` promises (run,
  judge, exit); a dedicated entry point keeps both honest. Documented
  again in the plan.
- **The five-minute exit criterion** counts documented-path time (install
  command plus one command plus opening a URL), not download bandwidth.
