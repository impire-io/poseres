# Research: The Web Dashboard (One Face for Any Brain)

Phase 0 of `plan.md`. Decision / rationale / alternatives, each tracing to
`spec.md` or AGENTS.md. The two load-bearing facts were verified at source
before any shape was chosen: (1) the rover world speaks to its telemetry
through exactly three calls — `record_reset(x, y, theta)`,
`record_step(x, y, theta, bump)` (world.py:199-226), and
`attach_layout(world.layout())` applied by `make_rover_body`
(world.py:339-340) — so a view adapter with that surface mounts the rover
**unchanged**; (2) the B1 viewer's test discipline (endpoint assertions via
urllib on an ephemeral port, byte-identity under a polling hammer —
test_rover.py:68-99) is directly reusable as this feature's gate shape.

## R1 — Dashboard shape: a consumer model + a stdlib server + one self-contained page

**Decision.** A new subpackage `src/pra/dash/` with three layers:

1. **`model.py`** — `DashboardModel(transport)`: subscribes `pra.v1.>` on
   the existing `BusTransport` seam, runs a discovery sweep at start and on
   a slow interval, and materializes one `RunModel` per run id from
   *received payloads only* — identity, state, liveness (monotonic age of
   the last message), latest census, bounded census history, counters as
   published, snapshot notices, world view. Payload handlers are
   thread-safe (they run on the transport's delivery thread) and skip
   malformed payloads with a counted `wire_errors`, never an exception.
2. **`server.py`** — the B1 viewer's server pattern generalized:
   `ThreadingHTTPServer` on 127.0.0.1 (port 0 = ephemeral), endpoints
   `/` (the page), `/runs` (discovery list), `/run/<id>/state` (one JSON
   snapshot carrying everything both modes render), and
   `/run/<id>/ctrl` (POST: forwards the control command through
   `transport.request`, returns the reply verbatim — success or error —
   with the timeout surfaced as an error payload, never a hang).
3. **`page.html`** — one self-contained page (package data, the rover
   viewer precedent): polls `/runs` and `/run/<id>/state`, renders simple
   and advanced modes as client-side tabs, draws the rover world view as
   SVG from the view payloads, and posts control commands. No external
   assets, no framework, no build step.

Plus **`cli.py`** — a `pra-dash` console script: real transport (lazy, the
B6 error message), server URL printed, runs until interrupted.

**Rationale.** The project already validated this exact shape in-process
(feature 006): static page + polled JSON + all derived work off the run
path. Off-process, the split is even cleaner — the dashboard owns no run
state at all, only received payloads — and it keeps the gate browser-free:
everything a browser would render is asserted at the endpoint level
(spec FR-008). A framework or a websocket layer would buy latency the
instrument does not need at the price of a build system the repo does not
have.

**Alternatives considered.** (a) Server-sent events / websockets instead of
polling — rejected for v1: the B1 poll pattern is proven, testable with
urllib, and the data rate (censuses and poses) is trivially poll-sized;
push can arrive later without changing the model. (b) Rendering
server-side (HTML fragments) — rejected: the state endpoint doubles as the
machine-readable surface the tests (and any future tool) consume.
(c) Living inside `pra.nats` — rejected: the dashboard is a *consumer* of
the documented scheme (spec FR-001); a separate package keeps that
contractual distance real (it imports `pra.nats.subjects` for names and
the transport protocol, nothing else from B6).

## R2 — The world-view channel: the tap grows a third-party-shaped adapter, the rover mounts unchanged

**Decision.** `NatsTap.world_view(kind)` returns a view adapter exposing
exactly the call surface the rover world already speaks:
`attach_layout(layout)`, `record_reset(*args)`, `record_step(*args)` —
so the wiring is one line, `make_rover_body(cfg, rng,
telemetry=tap.world_view("rover"))`, and **no rover file changes**. The
adapter mirrors plain copies into the tap's existing bounded buffer (the
same seq family, the same pump, the same drop derivation): a **static
part** (`kind` + layout payload) published on first drain and re-published
on a slow heartbeat (default every 5 s) so late-attaching dashboards catch
it, and a **live part** (kind-defined: for the rover, episode + pose +
bump per `record_step`) published as drained. Two new subjects in the
scheme: `…tele.view.static` and `…tele.view.live`. The dashboard builds
the capped trail client-side from received poses — the wire carries poses,
not history. Worlds that offer nothing publish nothing (the adapter is
only created when asked for). Observer safety is the tap's existing proof
extended: rover-with-view vs rover-without vs bare, all byte-identical.

**Rationale.** The world already owns its ground truth and already has the
habit of narrating it (the L1 occupancy precedent; RoverWorld's telemetry
parameter) — the only new thing is *where the narration lands*. Reusing
the RoverTelemetry call surface means the two taps (in-process viewer,
off-process bus) are interchangeable at the same argument, which is
exactly what "the B1 viewer generalized" should mean mechanically. Reusing
the mirror buffer keeps every no-backpressure and drop-count guarantee
without new machinery (spec FR-005).

**Alternatives considered.** (a) The dashboard reconstructs the world from
`tele.step` observations — rejected: observations are the brain's senses,
not the world's map; reconstructing pose from a rangefinder is research,
not plumbing. (b) A request/reply "give me the layout" command — rejected:
it would grow the frozen three-command control surface and turn a
telemetry concern into a control concern; the slow static re-publish costs
bytes, not contracts. (c) Publishing the trail server-side — rejected: the
trail is a *view* preference (its cap is a rendering choice); the wire
carries facts. (d) Coalescing poses at drain time — deferred, named: at
the rover's paced rate the live part is comparable to `tele.step` volume;
a coalescing knob can arrive if a fast world ever carries a view.

## R3 — Discovery and liveness: observed traffic is truth, the sweep is a bootstrap

**Decision.** The model materializes a run from *any* message observed
under its namespace (subscribing `pra.v1.>` means late joiners and
never-discovered runs still appear), plus an explicit discovery sweep at
start and every 10 s (`request` on the discover subject; each reply merges
into the list). Liveness is the monotonic age of the last received message
per run, rendered honestly (a paused run goes quiet — the state says
paused *and* the quiet is shown; a dead server ages every run at once).
Runs are never auto-evicted; a stale run reads as stale until the user
removes it or the dashboard restarts.

**Rationale.** Two sources because each fails differently: the sweep finds
runs that predate the dashboard; passive observation finds runs whose
announce the sweep missed (drops are legal). Honest aging is spec FR-010's
concrete form.

**Alternatives considered.** Heartbeats from the tap — rejected for v1: a
new tap surface for what message age already tells; B6 deliberately
shipped no heartbeat, and the dashboard should consume the surface that
exists.

## R4 — Control forwarding: verbatim replies, blocking POST, surfaced timeouts

**Decision.** `/run/<id>/ctrl` accepts `{"cmd": …}` POSTs, forwards
through `transport.request` with a per-command timeout (5 s for
inspect/pause/resume; configurable long timeout, default 60 s, for
snapshot — the deferred-fulfillment contract), and returns whatever the
run replied, byte-verbatim, with HTTP 200 — the reply's own `ok` field is
the truth channel. A transport timeout or error returns
`{"ok": false, "error": …}` naming the failure. The POST handler blocks
its own request thread only (`ThreadingHTTPServer`), so the page stays
responsive while a snapshot waits for its boundary.

**Rationale.** The dashboard must not soften B6's error grammar (spec
assumption "control semantics are B6's, unrenegotiated") — verbatim
forwarding makes the dashboard's control surface exactly as honest as the
control plane, and no more.

**Alternatives considered.** An async job model for snapshot (POST returns
a ticket, page polls) — rejected for v1: the blocking thread costs
nothing at dashboard scale and keeps the surface one round-trip; the
`tele.snapshot` notice already gives the page its asynchronous signal.

## R5 — The gate: scripted traffic, endpoint assertions, the polling-hammer byte-identity

**Decision.** All gate tests run on `FakeBusTransport`: (1) model tests
feed scripted payloads (two runs, malformed frames, gaps, completion) and
assert the `RunModel` fields and `wire_errors`; (2) endpoint tests start
the real server on port 0 against a scripted model and assert `/runs`,
`/run/<id>/state`, and `/run/<id>/ctrl` (every control path incl. error
replies and the unknown-run 404) via urllib — no browser, the B1
discipline; (3) the observer proof re-runs at this layer: a seeded engine
run with tap + view channel + a live `DashboardModel` on the same fake
transport + the HTTP server hammered by a polling thread, byte-identical
to the bare run — including attach/detach mid-run (subscribe, poll,
shut the server down while the run continues); (4) the view channel's own
contract: journal shape (static once + heartbeat, live per step),
byte-identity on vs off, unknown-kind fallback at the endpoint level.
Zero skips; no NATS, no server, no browser.

**Rationale.** Every claim the spec makes is observable at the model, the
endpoint, or the journal — the browser adds pixels, not facts. This is
the same honesty split 006 proved and 014 inherited.

**Alternatives considered.** Headless-browser tests — rejected: a
multi-hundred-megabyte gate dependency to verify JSON already asserted;
the worked example is where a human confirms the pixels.

## R6 — The worked example: the B6 demo grows a face

**Decision.** `examples/nats/` gains `dashboard_demo.py`: find-or-start a
`-js` server (the existing `demo.py` logic, reused), start a paced rover
brain with tap + view channel (`brain_rover.py`, mirroring `brain.py` but
mounted on `make_rover_body` with the view adapter), start `pra-dash`
in-process, print the URL for a human, and run the headless proofs —
telemetry consumed into the model, `/run/<id>/state` serving the world
view and census history, a control round-trip (pause → frozen → resume →
snapshot id) through the dashboard's own ctrl endpoint — deciding the
exit code. The README gains the dashboard section. The scaled-run half of
SC-003 is asserted in the gate (advanced-mode data completeness for a
scaled config over the fake transport) and demonstrated live by pointing
`pra-dash` at any scaled run — the example documents the command.

**Rationale.** One example directory for one transport story; the proofs
stay headless so the exit code means something on CI-less machines, and
the browser URL is the human's reward, not the test's requirement.

**Alternatives considered.** A separate `examples/dash/` — rejected: the
dashboard is the same story's third act; splitting directories splits the
README's narrative for zero isolation gain.

## R7 — Dependencies and entry point: stdlib-only consumer, one new console script

**Decision.** `pra.dash` imports stdlib + `pra.nats.subjects` (names) +
the `BusTransport` protocol; the real transport is reached only inside
`cli.py` behind the existing lazy import, so `pra-dash` without the extra
fails with the B6 message. One `pyproject.toml` addition per surface:
the `pra-dash` script and the `pra.dash` package-data entry for the page.
No new dependencies, no `dev` change, core install unchanged.

**Rationale.** The dashboard must be installable everywhere the package
is, and useless-without-NATS only at the exact moment it truly needs a
server — the same grading B6 shipped.

**Alternatives considered.** Bundling the dashboard into `pra-rover` —
rejected: `pra-rover` is the in-process getting-started toy; the
dashboard is the off-process instrument; conflating them would re-couple
what B6 just decoupled.
