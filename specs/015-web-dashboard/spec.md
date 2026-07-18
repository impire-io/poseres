# Feature Specification: The Web Dashboard (One Face for Any Brain)

**Feature Branch**: `015-web-dashboard`
**Created**: 2026-07-18
**Status**: Draft
**Input**: User description: "Web dashboard / monitor — ROADMAP B7. The B1
viewer generalized: one dashboard for any live PRA brain, consuming the B6
telemetry subjects and control plane — never a second transport (it builds
strictly against the documented pra.v1 subject scheme and the three control
commands; zero engine edits, zero new run-path surface). Two modes with an
honest split: simple mode shows what the brain is doing for a person standing
in front of it (a world view when the world offers one, run status,
liveness), advanced mode is the researcher's instrument panel (population
census over time, best_dim trajectory, per-dim histogram, tap/transport
counters, control buttons for inspect/pause/resume/snapshot). The monitor
half is an instrument and ships here; the 'show what makes PRA unique' half
is a showcase spend under roadmap principle 1 and inherits C1/C2's gates —
out of scope. One known gap to close en route: rendering the rover world
requires the world's own view (layout, pose, trail) to travel over the bus —
B6's scheme carries observations and census but no world-view channel, so
this feature adds an additive world-view telemetry family to the tap
(world-defined payload, observer-safe like everything else, absent unless
the world offers it), with the rover as the worked case. Exit criteria
(roadmap): the dashboard attaches to a live run over NATS without perturbing
it — byte-identity with the dashboard attached and actively polling, the B1
discipline now off-process; both modes render the rover world and one scaled
run; zero engine edits. The quality gate keeps the B6 stance: no NATS
library, no server, no browser required — the dashboard's data model and
rendering surface are testable against the fake transport, the real-stack
proof is a worked example."

## Overview

Feature 014 gave a live brain an off-process presence: telemetry as
documented subjects, snapshots in a shared store, a control plane that
answers. What it deliberately did not build is a face — today the only
human-friendly window is the B1 rover viewer, which lives *inside* the run's
process and knows only the rover. B7 is that face, built once for every
brain: a dashboard any consumer machine can open against a NATS server,
which discovers the live runs, renders what a brain is doing, and drives the
management surface — while provably never touching the run.

The constitutional constraint is inherited, not invented: the dashboard is a
**pure consumer of the B6 surface**. It speaks the documented `pra.v1`
subject scheme and the three control commands, and nothing else — no second
transport, no side channel into the engine, no new run-path code. B6's own
success criterion (SC-006) promised that B7 could be specified against the
documented scheme without reading B6's source; this spec is that promise
being collected. Observer safety is likewise inherited and then *re-proven
at this layer*: the B1 viewer's live-polling byte-identity test — the run
watched, hammered with requests, and byte-identical to the unwatched run —
is repeated with the whole dashboard attached, off-process.

One honest gap must close en route. Simple mode's centerpiece for the rover
is the world view — arena, obstacles, pose, trail — and that is the world's
*own* ground truth, which B6's scheme does not carry (observations and
census travel; the world's self-portrait does not). This feature adds a
**world-view telemetry family** to the existing tap: a world that offers a
view publishes it as one more fire-and-forget subject family, world-defined
payload, absent unless offered, observer-safe under the same byte-identity
proof as every other tap surface. The rover is the worked case. Worlds that
offer no view lose nothing: simple mode falls back to the instrument
basics, which work for every run including the scaled reference worlds.

The scope split is stated up front (roadmap principle 1): the **monitor**
is an instrument and ships here — its job is to tell the truth about a
running brain, including ugly truths like drop counts and stale censuses.
The **showcase** — demo material engineered to show what makes PRA unique —
is a spend that inherits C1/C2's research gates and is out of this feature's
scope. Nothing in this dashboard may pretend: staleness is shown, gaps are
shown, a paused brain looks paused, and a dead server looks dead.

The quality gate keeps the B6 stance exactly: no NATS library, no server,
and additionally **no browser** in the gate — the dashboard's consumption
model and its rendering surface are exercised against the in-repo fake
transport at the endpoint level (the B1 viewer's own test discipline), and
the real stack is proven by a worked example.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - One dashboard for any live brain (Priority: P1)

A user starts the dashboard pointed at a NATS server. It discovers the live
runs, lists them, and — one click later — shows **simple mode** for the
chosen run: the run's identity and state (running / paused / completed), a
liveness reading (how fresh the last message is), and the latest census in
plain terms (population, best dimensionality, steps seen). When the run
completes, the dashboard says so and shows the final summary. None of this
requires the world to offer anything special — it works for the reference
world, a scaled run, the rover, a Gymnasium mount, all alike.

**Why this priority**: This is the feature's core value — one face for any
brain — and everything else (world views, the instrument panel, control)
hangs off the consumer model this story builds. It is independently
shippable: even without US2–US4 it replaces "read the terminal" with "open
a page" for every run.

**Independent Test**: Can be fully tested against the fake transport with
scripted subject traffic: feed announce/step/census/status messages for two
runs, assert the dashboard's discovery list, its selected-run model, its
liveness and state transitions, and the JSON its page endpoints serve — no
NATS, no server, no browser.

**Acceptance Scenarios**:

1. **Given** two live runs publishing on one server, **When** the dashboard
   starts, **Then** it lists both runs by identity and state, and selecting
   one shows that run's simple mode with no cross-talk from the other.
2. **Given** a selected live run, **When** telemetry flows, **Then** simple
   mode shows state, a liveness reading that ages when messages stop, and
   the latest census; **When** the run completes, **Then** the state reads
   completed and the final summary is displayed.
3. **Given** a dashboard started before any run exists, **When** a run
   appears, **Then** discovery finds it without restarting the dashboard.
4. **Given** a run that stops publishing (dead server, killed run),
   **When** the silence exceeds the liveness window, **Then** the dashboard
   shows the staleness honestly — it never renders a frozen brain as live.

---

### User Story 2 - The world shows itself: the world-view channel (Priority: P2)

A rover run publishes its own self-portrait — the arena layout once, then
pose and trail as it moves — through the same tap that carries everything
else, and the dashboard's simple mode renders it: the same watchable world
the B1 viewer shows, now from any machine. A world that offers no view
changes nothing: the channel is simply absent, and simple mode shows the
instrument basics. The channel is observer-safe under the same proof as
every tap surface: a rover run with the view channel publishing is
byte-identical to the same run without it.

**Why this priority**: The rover render is the roadmap exit's named
requirement and the getting-started emotional payoff — but it depends on
US1's consumer model existing, and every run benefits from US1 even before
this lands.

**Independent Test**: Can be fully tested without the dashboard: mount the
rover with the view channel enabled over the fake transport, assert the
layout and pose/trail payloads in the journal, and assert byte-identity of
the run summary with the channel on vs off. Dashboard-side, scripted view
payloads drive the endpoint assertions.

**Acceptance Scenarios**:

1. **Given** a rover run with the view channel enabled, **When** it runs,
   **Then** the journal carries the layout once and pose/trail updates at a
   bounded cadence, and the run summary is byte-identical to the same run
   with the channel disabled — and to one with no tap at all.
2. **Given** the dashboard watching that run, **When** view payloads
   arrive, **Then** simple mode's world view renders arena, obstacles,
   pose, and trail, updating as the rover moves.
3. **Given** a world that offers no view, **When** the dashboard shows it,
   **Then** simple mode presents the instrument basics with no error and no
   empty placeholder pretending a view exists.
4. **Given** a world publishing a view kind the dashboard does not know,
   **When** it renders, **Then** the dashboard says a world view is present
   but unrenderable, naming the kind — never a crash, never silence.

---

### User Story 3 - The researcher's instrument panel with the controls wired (Priority: P3)

A researcher switches the dashboard to **advanced mode**: the census as a
time series (population and best dimensionality trajectories), the per-dim
population histogram as it stands now, the tap and transport honesty
counters (mirrored, published, dropped, publish failures, reconnects), and
the snapshot notices as they land. Beside the readings sit the controls:
inspect (refresh the authoritative state), pause and resume (the buttons
reflect the boundary-exact semantics and show the position), and snapshot —
whose reply, including the honest error replies (not snapshot-configured;
completed first), is surfaced verbatim rather than swallowed.

**Why this priority**: The instrument panel is what makes the dashboard a
research tool rather than a demo — but it composes US1's model and B6's
control plane, and pause/snapshot on a run you cannot yet see (US1) would
be management before monitoring.

**Independent Test**: Can be fully tested against the fake transport:
scripted census/snapshot traffic drives the history model assertions;
control actions through the dashboard surface assert the request sent, the
reply surfaced, and the state change reflected — including every error
reply path.

**Acceptance Scenarios**:

1. **Given** a run publishing censuses over time, **When** advanced mode
   renders, **Then** the census history, best_dim trajectory, and current
   per-dim histogram reflect exactly the payloads received, and the
   honesty counters are shown, not hidden.
2. **Given** a live run, **When** the user pauses from the dashboard,
   **Then** the pause reply and position are shown, the run's state reads
   paused, the liveness reading makes the quiet honest, and resume
   continues — with the underlying run provably byte-identical to a
   never-paused run (the B6 guarantee, re-asserted through this surface).
3. **Given** a snapshot request from the dashboard on a snapshot-configured
   run, **When** the next boundary fulfills it, **Then** the snapshot id
   appears with its step and cycle; **Given** an unconfigured run, **Then**
   the error reply is displayed naming what is missing.
4. **Given** a scaled run (no world view, large population), **When**
   advanced mode renders it, **Then** the instrument panel is complete and
   readable — the dashboard's claims hold beyond toy runs.

---

### User Story 4 - The worked example: a browser on a live brain (Priority: P4)

A user runs one documented command: a NATS server comes up, a paced rover
brain starts publishing (view channel on), the dashboard starts, and a
browser page shows the rover driving its arena live — switch to advanced
mode and the census history, counters, and working control buttons are
there. The example is scripted to verify its proofs headlessly (the page
endpoints serve the world view, the history, and a control round-trip
succeeds), so "did B7 land" is one command's exit code — a browser makes it
delightful, but is not required for the proof.

**Why this priority**: Pure composition of US1–US3 over the real stack —
nothing in it can work before they do, and it is the only story touching a
real server.

**Independent Test**: Run the documented command with the NATS extra and a
server available; it exits zero only when the dashboard consumed live
telemetry, served the world view and instrument data, and completed a
control round-trip against the real stack.

**Acceptance Scenarios**:

1. **Given** a machine with the extra and a server, **When** the user runs
   the documented command, **Then** a live rover brain, the dashboard, and
   the headless proofs all come up and pass, and the printed URL opens to
   the live page in any browser.
2. **Given** an installation without the NATS extra, **When** the example
   or the dashboard's real transport is requested, **Then** the failure is
   the B6 error naming the extra — never a traceback.

---

### Edge Cases

- The dashboard outlives the run: completed state and final summary stay
  rendered; control buttons answer with the completed-run error replies
  (surfaced, not hidden); nothing spins.
- The run outlives the dashboard: killing the dashboard (or closing the
  browser) is invisible to the run — re-proven by the byte-identity test
  with attach-poll-detach mid-run.
- Telemetry gaps (drops under load, reconnects): the census is the
  self-healing reading; the dashboard renders gaps as gaps (seq
  discontinuities surface in the counters), never interpolating data it
  did not receive.
- Two dashboards on one run: both are observers; both work; neither
  perturbs — observers are cheap by design.
- A malformed or unknown payload on a subscribed subject: logged and
  skipped; the dashboard never crashes on wire data it does not
  understand.
- The world-view payload for a big world: the channel has a bounded
  cadence and bounded payload discipline (the trail is capped, the layout
  travels once) — the tap's no-backpressure rule is not renegotiated by
  prettiness.
- Discovery on a server with non-PRA traffic: the dashboard listens only
  under `pra.v1.` and ignores everything else.
- The dashboard page itself is served to a browser on the user's machine:
  it binds localhost by default (the B1 viewer precedent); serving beyond
  localhost is the operator's explicit choice, stated in docs, and the
  NATS server's own security remains the deployment's affair (B6
  assumption, unchanged).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The dashboard MUST consume only the documented B6 surface —
  the `pra.v1` subject families and the three control commands plus
  discovery — through the existing transport seam. No second transport, no
  new run-path code, no engine edits, and no coupling to B6 internals
  beyond the documented scheme.
- **FR-002**: The dashboard MUST discover live runs (including runs that
  appear after it starts) and let the user select among them; concurrent
  runs MUST NOT cross-talk in any rendered surface.
- **FR-003**: Simple mode MUST show, for any run: identity, state
  (running/paused/completed), a liveness reading that ages honestly when
  messages stop, the latest census in plain terms, and the final summary on
  completion. It MUST NOT require anything world-specific to function.
- **FR-004**: Advanced mode MUST show the census history (population and
  best_dim over time), the current per-dim histogram, the tap/transport
  honesty counters, and snapshot notices; and MUST provide the four
  control actions (inspect, pause, resume, snapshot) with every reply —
  success or error — surfaced verbatim.
- **FR-005**: The tap MUST gain an additive world-view telemetry family: a
  world that offers a view publishes it fire-and-forget under the run's
  namespace (a one-time static part and a bounded-cadence live part,
  world-defined kind and payload); worlds that offer nothing publish
  nothing. The family MUST obey every existing tap rule: observer safety
  by byte-identity, no backpressure, counters outside the learning
  surface.
- **FR-006**: The rover MUST be the world-view worked case: layout once,
  pose and capped trail live; the dashboard MUST render it in simple mode.
  Unknown view kinds MUST render as present-but-unrenderable, named.
- **FR-007**: Observer safety MUST be re-proven at the dashboard layer: a
  seeded run with the full dashboard attached and actively polled is
  byte-identical to the same run bare — including attach-and-detach
  mid-run, and including the rover with its view channel on.
- **FR-008**: The quality gate MUST stay NATS-free, server-free, and
  browser-free: the consumer model and every page endpoint are exercised
  against the fake transport with scripted traffic; zero tests skipped;
  the real stack is the worked example's job.
- **FR-009**: The repository MUST ship a worked example launched by one
  documented command: real server, live rover brain with the view channel,
  the dashboard serving a browsable page, and headless proofs (telemetry
  consumed, world view served, control round-trip) deciding the exit code.
- **FR-010**: The dashboard MUST tell the truth structurally: staleness
  shown, gaps shown, error replies shown, drops and reconnects visible in
  advanced mode; it never interpolates missing data or renders a silent
  run as live.

### Key Entities

- **Run model**: the dashboard's in-memory picture of one run, built
  purely from received payloads — identity, state, liveness, latest
  census, census history, counters, snapshot notices, world view.
- **Discovery list**: the set of live runs the dashboard knows, from the
  discovery sweep plus runs observed publishing.
- **World-view channel**: the additive tap family — a static part
  (layout, once) and a live part (pose/trail, bounded cadence),
  world-defined kind, absent unless offered.
- **Simple mode**: the person-in-front-of-it surface: state, liveness,
  plain census, world view when present.
- **Advanced mode**: the researcher's surface: histories, histogram,
  honesty counters, snapshot notices, control actions with surfaced
  replies.
- **Worked example**: server + rover brain + dashboard + headless proofs,
  one command.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: The full existing suite (including all of B6's byte-identity
  proofs) passes unchanged with recorded reference values byte-identical,
  on a machine with no NATS library, no server, and no browser; zero
  tests skipped; core install unchanged.
- **SC-002**: A seeded run with the dashboard attached and actively polled
  produces a byte-identical summary to the bare run — for the reference
  world, for a multi-stream continuous run, and for the rover with the
  world-view channel publishing; attach/detach mid-run changes nothing.
- **SC-003**: Both modes render both target runs: the rover run shows its
  live world view in simple mode, and a scaled run shows a complete,
  readable instrument panel in advanced mode — demonstrated by the worked
  example and asserted at the endpoint level in the gate.
- **SC-004**: A control round-trip through the dashboard surface succeeds
  on a live run — pause shows its position and the run provably freezes,
  resume continues, snapshot surfaces its id or its honest error — with
  the paused-and-resumed run byte-identical to a never-paused one.
- **SC-005**: The dashboard discovers and cleanly separates at least two
  concurrent runs on one server, including a run that appears after the
  dashboard started.
- **SC-006**: Zero engine edits; the world-view tap extension is additive
  (every existing B6 test passes untouched); a user can point the
  dashboard at any existing PRA run configuration without modifying that
  run beyond enabling the tap.

## Assumptions

- **A localhost instrument, not a hosted product.** The dashboard binds
  localhost by default and ships no authentication of its own; exposure
  beyond localhost is the operator's explicit choice, and NATS server
  security remains the deployment's affair (the B6 assumption, unchanged).
- **Live instrument, bounded memory.** Census history and trails are
  bounded in-memory windows sized for a watching session; durable history
  and replay stay deferred exactly as B6 deferred them (JetStream-backed
  telemetry history remains a named future item, not smuggled in here).
- **The page is self-contained and browser-free to test.** The B1 viewer
  precedent: a static self-contained page polling JSON endpoints; the gate
  asserts the endpoints, the example proves the page.
- **World-view kinds are worlds' business.** The channel carries a named
  kind with a world-defined payload; this feature ships the rover kind and
  the present-but-unrenderable fallback. New kinds ride the same channel
  without dashboard changes to the transport surface.
- **The showcase half stays out.** Published demo material engineered to
  flatter capability inherits C1/C2's research gates (roadmap principle
  1); this feature's aesthetic bar is "clear and honest", not "launch
  video".
- **Control semantics are B6's, unrenegotiated.** Pause is
  schedule-relative (free-running worlds keep moving), snapshot is
  deferred fulfillment on configured runs only, and error replies are the
  contract — the dashboard displays them, it does not soften them.
