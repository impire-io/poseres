# Research: Brain Telemetry & Introspection Dashboard (feature 029)

Phase-0 record: every seam decision, its rationale, and the alternatives
considered. No NEEDS CLARIFICATION markers existed in the Technical
Context; the decisions below resolve the design unknowns the spec left to
plan time. Evidence classes per the working agreement: **[measured]** =
read from the repo in this session, **[mechanism-argument]** = reasoned.

## D1. Anatomy metadata source: an optional `anatomy_meta()` world method

**Decision**: Worlds that can describe their body implement
`anatomy_meta() -> dict` (groups with names/slices, actuators with
names/ids). `_TapWorld.__init__` does one `getattr(world, "anatomy_meta",
None)`; when present, the tap deep-copies the result once, buffers it, and
re-publishes on the existing view-heartbeat clock.

**Rationale**: FR-001 demands the metadata be *sourced from the body's own
definition*. Each body already holds it **[measured]**:
- `Ros2Body` keeps live `self._sensors` (id, width, order) and
  `self._actuators` (id, presets) — covers ROS2 **and** Minecraft (C1's
  `c1_anatomy()` is `SensorSpec`/`ActuatorSpec` lists fed to
  `Ros2Body.factory`), and stays correct after grown tools
  (`register_topic_sensor` queues apply at C4, and `anatomy_meta()` reads
  the live lists).
- The rover world declares `SENSOR_PARTS = (("rays",5), ("compass",2),
  ("gps",2), ("bump",1))` (world.py:68) and has named actions.
- `GymnasiumWorld` knows its flattened Box width and Discrete action
  count → structural metadata with generic labels.
- The bare reference world implements nothing → the family is simply
  absent and the dash falls back (FR-012); obs_dim/n_actions already
  travel in the `started` status payload **[measured]**.

Actuator naming from `ActuatorSpec.presets`: each preset dict's keys
joined with `+`, empty preset → `idle` (C1 yields forward, back,
turn_left, turn_right, jump_forward, dig_ahead, place_ahead, idle)
**[measured]** from `anatomy.py`.

**Alternatives considered**:
- *Launcher passes the anatomy to the tap* (e.g. `run_c1.py` hands
  `c1_anatomy()` over): rejected — duplicates the definition per launcher,
  silently wrong after a mid-run grown sensor, violates FR-001's
  "never duplicated by hand per world".
- *Reuse the `world_view` adapter*: rejected — that channel narrates world
  *state* (rover pose), not body *structure*; conflating them would couple
  two heartbeats and two consumer schemas.

## D2. Per-frame rows ride the existing census walk

**Decision**: `_publish_census` (tap.py:434) publishes a second payload on
`brain.frames` in the same pass: the full `FrameState` list it already
walks, each row scored with the same `WeightedSumScorer` call it already
makes for the aggregate. `tele.census` stays byte-identical.

**Rationale**: The rows exist at the seam **[measured]** —
`FrameStore.frame_states()` returns frame_id, dim, is_candidate,
age_cycles, recon/pred/effort EMAs (frame.py:514-530), and the census
already computes per-frame scores then discards them. Same cadence, same
publisher thread, same torn-read guard (`except Exception: return`) —
zero new failure modes. Size is bounded by `max_frames` **[measured]**
(population rides the ceiling in continuous mode, arc 026): ~population ×
~90 B ≈ a few KB per census — no truncation needed, satisfying the spec's
no-silent-caps edge case by construction.

**Alternatives considered**:
- *Enrich `tele.census` in place*: rejected — existing consumers (the
  dash's census history, the B6 gate) parse that payload; FR-004 says
  additive, and a separate subject lets a consumer opt into the heavy rows.
- *Publish per-frame deltas*: rejected — complexity without need at these
  sizes; full rows are idempotent for late attachers.

## D3. Lifecycle events from a tap-owned Bus wrapper (zero engine edits)

**Decision**: `NatsTap.bus_factory` returns `_TapBus(InMemorySyncBus(
processor), tap)` — a delegating wrapper whose `register`/`unregister`
mirror `spawn`/`evict` events (frame_id, the tap's step counter, seq)
into the existing buffer, then forward verbatim.

**Rationale**: The engine already routes every population change through
the Bus **[measured]**: `offline_cycle` calls `bus.unregister(fid)` for
each eviction and `bus.register(store.birth(...))` for each spawn
(engine.py:420-424), and boot/restore registration goes through the same
calls. Register/unregister happen on the engine thread — the same single
writer that runs `_mirror_step` — so the tap's no-lock buffer discipline
is preserved **[mechanism-argument]**. The tap constructs the bus today;
wrapping it is invisible to the engine and absent without a tap.

**Vocabulary** (FR-003, fixed and documented in the contract):
`spawn` = the frame joined the live population — including initial boot
and snapshot-restore registration (that inclusion is what makes SC-003's
`spawns − evicts = population` reconciliation exact at any attach point);
`evict` = it left (decay/threshold/cap — the engine's single evict path).
Richer per-event reasons would require engine edits for telemetry's sake;
rejected for v1 and recorded as a possible follow-up.

**Alternatives considered**:
- *Engine emits lifecycle callbacks*: rejected — core edits for telemetry
  invert the tap philosophy (the window that provably isn't there) and
  would touch constitution-I surface for no functional gain.
- *Dash infers churn from census diffs*: rejected — misses same-cadence
  churn (evict+spawn between censuses cancels out), violating SC-003.

## D4. Dashboard: bounded windows in the model, one new Brain tab

**Decision**: `RunModel` grows `brain_meta` (latest metadata),
`frames_latest` (latest rows), `events` (deque, maxlen 512), and
`steps_window` (deque, maxlen 600, filled by the existing `tele.step`
handler with {step, stream, action, obs}). `state_payload()` exposes them;
`page.html` adds a **Brain** tab rendering: the anatomy schematic (SVG
generated from metadata: sensor-group boxes with per-channel activity
bars, actuator nodes, chosen-action highlight from the newest window
entry), per-group strip charts + scrolling decoded log (from the window),
the frame table, and the lifecycle timeline. Absent data → the note-style
fallbacks the page already uses (FR-012).

**Rationale**: The model is the documented pure-consumer surface
**[measured]** (model.py builds everything from received payloads; the
page reads `/run/<id>/state` only). Bounded deques are the existing
idiom (census_history maxlen 512) and satisfy FR-013/SC-006 by
construction: at 10 steps/s the window holds the last minute, the state
payload stays ~tens of KB on localhost, and page memory cannot grow
unboundedly. Hand-rolled SVG matches the page's existing chart style
(no new dependencies — the strict no-CDN posture of a self-contained
page) **[measured]**.

**Alternatives considered**:
- *Server-sent events/WebSocket push*: rejected — the 4 Hz poll is the
  shipped pattern, meets the latency bar (one step's budget at 250 ms;
  "within one heartbeat" for metadata), and keeps the server stdlib-only.
- *A charting library*: rejected — external deps break the self-contained
  page and the repo's no-new-hard-deps posture.

## D5. Test strategy

- **Contract** (`tests/contract/test_brain_subjects.py`, FakeBusTransport):
  subject names/shapes; metadata announced at construction and
  re-published on the heartbeat clock; frames payload rows agree with the
  aggregate census from the same walk; canonical wire form, no wall-clock
  keys.
- **Integration** (`test_brain_telemetry_run.py`): a short reference-config
  run with churn (the existing small-run pattern from
  `test_nats_fake_run.py`): every spawn/evict exactly once, seq-ordered,
  `spawns − evicts == final population`; rows==census at every published
  census; `_TapBus` delegation equivalence (same run with and without tap
  → byte-identical engine outputs, the existing tap-equivalence pattern).
- **Dash**: model-level family handling (malformed payloads → wire_errors,
  bounded windows respect maxlen); `test_dash_live.py` grows assertions
  that `/run/<id>/state` carries brain fields and the page serves the
  Brain tab markup.
- **Byte-frozen**: no core edits, so `test_baseline_unchanged.py` is the
  witness, not a risk.
- SC-006's one-hour accelerated soak stays a live criterion (quickstart
  documents it); the gate encodes its mechanism (bounded windows) instead.
