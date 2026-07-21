# Feature Specification: Brain Telemetry & Introspection Dashboard — Seeing What the Brain Is Made Of, Live

**Feature Branch**: `029-brain-telemetry-dashboard`
**Created**: 2026-07-21
**Status**: Draft
**Input**: User description: "Brain telemetry protocol and introspection dashboard (feature 029). Extend the pra.v1 telemetry scheme with an additive `brain.*` subject family so a live brain's internals are observable off-process, and grow pra-dash into a real introspection surface: anatomy/channel metadata, per-frame census rows, frame lifecycle events, named per-channel strip charts with a live message log, a frame population table, a spawn/evict timeline, and a graphical anatomy view."

## Overview

The C1 showcase is launching: a brain living in a Minecraft world for weeks,
watchable two ways — through a spectator's eyes in the world (feature 027 +
the `up.sh` stack) and through the dashboard (feature 015). But both windows
show the *outside* of the brain. The dashboard renders run-level aggregates
(step counts, population size, best-frame score); the world shows behavior.
Neither can answer the questions an owner actually asks while watching:
*what are the body's channels saying right now? How many frames does the
brain have, and what is inside each one? When are frames born and when do
they die?*

Today those answers exist in-process and are thrown away at the telemetry
boundary. The per-step observation vector already crosses the wire, but
nothing on the wire says which numbers mean "health" and which mean "the
block ahead" — the anatomy knows, the protocol doesn't say. The census walks
every frame's state and publishes only aggregates. Frame births and deaths
(the propose-and-select and decay machinery — the closest thing PRA has to
consolidation) are not published at all.

This feature extends the versioned telemetry protocol with an **additive
brain-introspection family** — anatomy/channel metadata, per-frame census
rows, and lifecycle events — and grows the dashboard into an introspection
surface: named per-channel live views with a scrolling message log, a
frame-population table, a birth/death timeline, and a **graphical anatomy
view**: the body drawn as a schematic with live activity, generated from the
published metadata so it works for any mounted body, not just Minecraft.

The constitution's lines hold throughout: everything is additive and opt-in
(existing subjects and consumers byte-unchanged), the reference behavior
stays byte-frozen (zero new work when telemetry is off), payloads carry no
wall-clock time, and the dashboard remains a pure consumer of the published
protocol.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - The channels have names, and you can watch them talk (Priority: P1)

An observer opens the dashboard during a live run and sees the body's
sensor channels *by name* — for C1: pose, vitals, environment, blocks —
each as a live chart of recent values plus a scrolling log of the messages
flowing through them, decoded from the step stream using published channel
metadata. The same dashboard, with zero body-specific code, does this for a
rover run or the reference world: the names and slices come off the wire.

**Why this priority**: This is the smallest slice that turns the dashboard
from "numbers about a run" into "a window into an embodied brain," and it
is the foundation the anatomy view (US4) and every later panel builds on.
Without channel metadata on the wire, nothing else in this feature can be
labeled.

**Independent Test**: Run any world with telemetry on, attach the
dashboard, and verify every channel group appears under its published name
with live values matching the step stream; run a body without published
names and verify generic labels appear instead of a broken page.

**Acceptance Scenarios**:

1. **Given** a live C1 run with telemetry on, **When** the observer opens
   the dashboard, **Then** the four channel groups appear under their
   anatomy names with per-channel live values and a scrolling log, and the
   values match the step stream's observation vectors exactly.
2. **Given** a dashboard that attaches mid-run, **When** it has missed the
   original metadata announcement, **Then** it still labels the channels
   within one heartbeat period (no restart required).
3. **Given** a run published by an older brain that emits no channel
   metadata, **When** the dashboard attaches, **Then** it degrades to
   today's behavior plus generically-labeled channels — never an error
   page.

---

### User Story 2 - The frame population, frame by frame (Priority: P2)

The observer sees a table of every frame in the brain's population: its
id, its dimensionality, its age, its reconstruction/prediction/effort
statistics, and its current score — updating on the census cadence. They
can watch a young frame's prediction error fall as it learns, and see
which frame is currently the brain's best and why.

**Why this priority**: "What is inside the frames" is the heart of the
introspection request, and the data already exists at the census seam —
it is currently aggregated away. High value, bounded risk.

**Independent Test**: Attach during a live run and verify the table's
row count equals the published population aggregate at every census, and
that a chosen frame's statistics evolve plausibly (errors fall while it
learns) across consecutive censuses.

**Acceptance Scenarios**:

1. **Given** a live run at census time, **When** per-frame rows are
   published, **Then** the row count equals the aggregate population
   count in the same census, every time.
2. **Given** the dashboard is open across many censuses, **When** frames
   learn, **Then** each frame's row updates in place and its statistics
   match what the engine's own scorer would report for that frame.

---

### User Story 3 - Births and deaths on a timeline (Priority: P3)

The observer sees a timeline of frame lifecycle events: each spawn and
each eviction, ordered by the run's own sequence numbers, with the frame
id and the reason (spawned by the proposal policy, evicted by decay or
survival threshold). Watching C1 overnight, they can answer "did the
population churn or settle?" at a glance.

**Why this priority**: Lifecycle is the brain's consolidation-like
machinery made visible, and the only part of this feature that requires a
new emission point rather than enriching an existing one. Valuable, but
US1/US2 stand without it.

**Independent Test**: Run a short scripted world where the exact spawn
and evict sequence is known from the engine's own records, and verify the
published event stream matches it one-for-one, in order, with reasons.

**Acceptance Scenarios**:

1. **Given** a run in which the engine spawns and evicts frames, **When**
   the run completes, **Then** every spawn and evict appears exactly once
   in the event stream, in sequence order, and the final
   spawns-minus-evictions equals the final population count.
2. **Given** an eviction, **When** its event is published, **Then** it
   names the frame id and a reason drawn from a fixed, documented
   vocabulary.

---

### User Story 4 - The anatomy, drawn (Priority: P3)

The observer opens an anatomy view and sees the body as a picture, not a
table: sensor channel groups and actuators laid out as a schematic
diagram, generated from the published metadata. Live activity animates
it — a channel group lights up in proportion to how much its values are
moving, and the actuator for the currently chosen action highlights as
the brain acts. For C1 the observer *sees* the brain choose "forward,
forward, dig" while the blocks channel flickers.

**Why this priority**: This is the "graphical way" the owner asked for —
the most demo-worthy panel — but it is a pure consumer of US1's metadata
and step stream, so it correctly comes after the protocol work.

**Independent Test**: Render the anatomy view for three different bodies
(reference, rover, Minecraft) from their published metadata alone, with
zero body-specific dashboard code, and verify actuator highlights match
the action stream.

**Acceptance Scenarios**:

1. **Given** any run publishing channel metadata, **When** the anatomy
   view opens, **Then** a schematic renders showing every sensor group
   and every actuator by name, with no body-specific configuration.
2. **Given** a live step stream, **When** the brain chooses an action,
   **Then** the corresponding actuator highlights within one step's
   latency budget, and channel-group activity reflects the current
   observation movement.

---

### Edge Cases

- **Attaching mid-run**: metadata must be recoverable by a late consumer
  (announcement repeats on a heartbeat, as the world-view static part
  already does). A consumer that missed lifecycle events shows the
  timeline from its attach point and reconciles population via the census
  — it never invents history.
- **Accelerated runs**: at `TICK_RATE`/`--tick-ms` compression the step
  stream can run at 10+ steps/s for hours. The dashboard must keep up
  with bounded memory: logs and timelines are bounded live windows, not
  archives; the page must not grow without limit or fall behind
  unrecoverably.
- **Population at its ceiling**: continuous mode rides `max_frames`
  (measured, arc 026). Per-frame rows at the ceiling must stay complete
  and affordable; if any publication is ever bounded, the bound and the
  dropped count must be stated in the payload — silent truncation is a
  lie (constitution II).
- **Same-cycle churn**: a frame evicted and another spawned in the same
  cycle must appear as distinct, correctly ordered events (sequence
  numbers decide; there are no wall-clock timestamps to lean on).
- **Multi-stream runs**: step decoding must respect the stream id the
  protocol already carries; channel metadata is per-run (one body
  definition), not per-stream.
- **Bodies without names**: a world mounted without an anatomy (the bare
  reference world) publishes structural metadata only (dimension count,
  action count); every panel falls back to generic labels.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The telemetry protocol MUST carry per-run **anatomy/channel
  metadata**: every sensor channel group's name, its slice of the
  observation vector, and per-channel labels where the body defines them;
  and every actuator's name and action id. The metadata MUST be sourced
  from the body's own definition (never duplicated by hand per world) and
  MUST be available to consumers that attach at any point in the run.
- **FR-002**: The telemetry protocol MUST carry **per-frame census rows**
  on the existing census cadence: frame id, dimensionality, age, the
  frame's reconstruction/prediction/effort statistics, and its score
  under the engine's own scoring rule. The rows MUST agree with the
  aggregate census published for the same moment (same population count,
  same best frame).
- **FR-003**: The telemetry protocol MUST carry **frame lifecycle
  events** — spawn and evict — each with the frame id, the run's own
  ordering facts (sequence number, cycle/step counters), and a reason
  from a fixed documented vocabulary. Every lifecycle change in the
  engine MUST produce exactly one event.
- **FR-004**: All new publications MUST be **additive** under the
  existing versioned scheme: existing subjects, payloads, and consumers
  remain byte-identical; a consumer ignorant of the new family loses
  nothing it has today. The discovery reply MUST advertise the new
  subjects so consumers never guess subject names.
- **FR-005**: With telemetry absent, the engine MUST do **zero new
  work**: no new allocations or branches in the hot loop, and the
  byte-frozen reference suite (RNG streams, serialized summaries)
  unchanged. With telemetry on, new publications MUST ride the existing
  tap seams and cadences (no new hot-loop publication points beyond the
  lifecycle emission, which fires only on population change).
- **FR-006**: All new payloads MUST use the canonical wire form and MUST
  carry **no wall-clock time**; ordering facts are sequence numbers and
  the run's own counters only, so payloads over a scripted transport
  remain byte-deterministic and the contract is testable without a live
  broker (the in-repo fake transport carries the gate).
- **FR-007**: The dashboard MUST render **named per-channel panels**:
  live recent-value charts per channel group and a scrolling log of
  decoded channel messages, driven entirely by the published metadata —
  no body-specific dashboard code.
- **FR-008**: The dashboard MUST render a **frame population table** from
  the per-frame census rows, updating in place on the census cadence.
- **FR-009**: The dashboard MUST render a **lifecycle timeline** of
  spawn/evict events from its attach point onward, in sequence order.
- **FR-010**: The dashboard MUST render a **graphical anatomy view**: a
  schematic of sensor groups and actuators generated from the metadata,
  animated by live activity (channel-group movement, chosen-action
  highlight). The same renderer MUST serve every body that publishes
  metadata.
- **FR-011**: The dashboard MUST remain a **pure consumer** of the
  published protocol: everything on screen is derivable by any
  third-party consumer of the same subjects.
- **FR-012**: The dashboard MUST **degrade gracefully**: attached to a
  run that publishes none of the new family, it shows today's view;
  partial publication (metadata but no lifecycle) lights up only the
  panels whose data exists.
- **FR-013**: The dashboard MUST remain usable on **accelerated runs**
  (sustained 10+ steps/s): bounded log/timeline windows, bounded page
  memory, and a consumer that falls behind MUST recover to live rather
  than stall.

### Key Entities

- **Channel group**: a named contiguous slice of the observation vector
  (e.g. C1's `pose`[0:5], `vitals`[5:7], `env`[7:11], `blocks`[11:14]),
  with optional per-channel labels; owned by the body's anatomy.
- **Actuator**: a named action id (e.g. C1's `forward`, `dig`); owned by
  the body's anatomy.
- **Anatomy metadata announcement**: the per-run publication carrying all
  channel groups and actuators, repeated on a heartbeat for late
  consumers.
- **Frame census row**: one frame's public state at a census — id, dim,
  age, error/effort statistics, score. "Inside the frame" for v1 means
  these statistics, not raw weights (see Assumptions).
- **Lifecycle event**: one spawn or evict — frame id, ordering facts,
  reason from a fixed vocabulary.
- **Anatomy schematic**: the dashboard's drawn body — sensor groups and
  actuators as diagram nodes, animated from the live step stream.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: An observer watching a live C1 run can name which body
  channel is changing, the current frame count, and the most recent
  frame birth or death **within 30 seconds of opening the dashboard**,
  without reading any code — the question list this feature exists to
  answer.
- **SC-002**: Per-frame rows and the aggregate census agree (row count =
  population, same best frame) at **100% of censuses** in a full
  validation run.
- **SC-003**: In a run with known churn, **every** spawn/evict appears
  exactly once and in order; final spawns − evictions = final
  population. Zero missing, duplicated, or reordered events.
- **SC-004**: The anatomy view and channel panels render correctly for
  **three different bodies** (reference, rover, Minecraft) with zero
  body-specific dashboard code — the metadata alone drives all three.
- **SC-005**: The full quality gate passes with the byte-frozen suite
  untouched: reference RNG streams and serialized summaries show **zero
  diffs** with the feature merged and telemetry off.
- **SC-006**: On an accelerated run sustained at ≥10 steps/s for one
  hour, the dashboard stays live (lag bounded and recoverable) and page
  memory stays bounded.

## Assumptions

- **"Inside the frames" means statistics, not weights.** Publishing raw
  weight matrices would be heavy on the wire and unreadable on screen;
  v1 publishes the per-frame statistics the engine itself uses to judge
  frames (errors, effort, age, dim, score). Raw-weight export can be a
  later, explicitly-requested capability.
- **Logs are live windows, not archives.** The scrolling channel log and
  the lifecycle timeline show a bounded recent window; durable history
  is out of scope for v1 (the existing snapshot/object-store path is the
  archival seam if it is ever wanted).
- **"Consolidation" is rendered as spawn/evict.** The current brain has
  no sleep-style consolidation phase; its population machinery is
  propose-and-select plus decay. The timeline shows exactly that, and
  the vocabulary on screen says "spawn"/"evict" — no invented phases.
- **One dashboard instance is the normal case.** Multiple simultaneous
  consumers must work (the protocol is fan-out by nature) but the
  performance bar (SC-006) is set for one.
- **The C1 stack is the proving ground**: acceptance runs use the
  existing worked examples (reference world, rover, Minecraft via the
  `up.sh` stack) rather than new worlds.
- **Existing cadences are enough.** Per-frame rows ride the census
  cadence and lifecycle events fire on population change; no new
  periodic publication clock is introduced.
