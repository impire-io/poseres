# Research: The Watchable Rover World

Phase 0 of `plan.md`. Every decision below is stated as
decision / rationale / alternatives, and each traces to a functional
requirement of `spec.md` or a working rule of `AGENTS.md`.

## R1 — The demo runs at the validated reference widths, on purpose

**Decision.** The rover anatomy is fixed at obs_dim 10 / n_actions 4 —
exactly `Config()`'s defaults, the scale every acceptance result was
recorded at. `make_rover_body` rejects any config whose widths disagree
(FR-011); the world's internal dials (arena size, obstacle count/radii,
speeds, ray geometry) ship as stated module constants, not config fields.

**Rationale.** Every scale-dependent rule (`effective_learning_rate`,
`effective_w_complexity`, `effective_min_age_cycles`) is exactly its raw
validated constant at obs_dim 10 — the demo shows the system in the one
regime where its behavior is a recorded, byte-frozen fact rather than an
extrapolation. A getting-started demo that quietly ran off the validated
staircase would undermine the honesty story it exists to showcase. Config
fields for world dials are the validation-family pattern (feature 005)
and carry obligations (inert defaults, snapshot semantics, degenerate
byte-identity) the demo neither needs nor can honestly meet.

**Alternatives considered.** Configurable sensor suite — deferred: it
multiplies the test surface and invites running the demo at widths where
no reference behavior exists. A bigger, richer world (more rays, odometry)
— rejected for v1: obs_dim 10 is enough for a moving map + telemetry, and
staying at reference scale is the point.

## R2 — Body-of-named-parts mount: the anatomy layer is the showcase

**Decision.** `RoverWorld` is a plain environment (physics + cached sense
vectors + `reset()`), NOT an `EventSource` itself. Four named sensors
(`rays`[5], `compass`[2], `gps`[2], `bump`[1]) and one actuator
(`drive`, 4 actions) wrap it; `make_rover_body(config, rng)` composes them
into the standard Doc 02 `Body` in that fixed order. The engine mounts the
Body through the existing `world_factory` parameter — zero engine changes
(FR-003).

**Rationale.** B1 is the first world that *naturally* decomposes into
parts, which is exactly what the anatomy layer was built for and has never
demonstrated beyond the 1:1 `WorldSensor` delegation. A newcomer reading
the rover source sees the integration surface they would use for their own
hardware: sensors are windows onto an environment, actuators are commands
into it, order is semantic, and the brain sees only the composed vector.
The Body already satisfies `EventSource` (feature 004), so the engine
needs nothing.

**Alternatives considered.** Implementing `EventSource` directly on
`RoverWorld` — works, but wastes the feature's one teaching opportunity
and leaves the anatomy layer undemonstrated. Registering rover parts as
runtime tools (mid-run growth) — a great follow-up demo, out of scope.

## R3 — Sensor suite and action set

**Decision.** Observations (10 channels, fixed order):
5 rangefinder rays at −90°/−45°/0°/+45°/+90° relative to heading
(distance to nearest wall/obstacle, capped and normalized to [0, 1]),
compass (cos θ, sin θ), position beacon (x, y normalized to [−1, 1]),
bumper (1.0 if the last move was blocked). Gaussian sensor noise with the
config's existing `sensor_noise_std` (0.04) is applied to the whole
emission, drawn once per reset/step. Actions: 0 forward, 1 reverse (half
speed), 2 turn left, 3 turn right; moves that would collide leave the
pose unchanged and set the bumper.

**Rationale.** The underlying latent is (x, y, θ) — dimension 3–4 in the
system's terms, inside the validated `true_dim` range, with genuinely
nonlinear position-derived emissions (ray geometry) — rich enough that
frames must actually model it, small enough to learn at reference scale.
Every channel is action-dependent through the pose except the bumper,
which is sparse honest structure (predictable only near walls). Reusing
`sensor_noise_std` keeps the honest irreducible-error floor the reference
world has, with no new config surface. Turn/move as separate discrete
actions is the smallest action set where the action *identity* matters
(the same action has different effects in different poses — what the
per-action transition models exist to capture).

**Alternatives considered.** Differential drive (left/right wheel speeds)
— continuous flavor, needs more actions to discretize honestly. An
egocentric-only suite (no beacon) — makes the latent partially observable
(θ unrecoverable from one step), a research question rather than a demo.
Grid world — cheaper physics but observation channels become near-binary,
much poorer for watching prediction error move.

## R4 — Determinism discipline: one generator, fixed draw order, bounded failure

**Decision.** The rover consumes the run's single seeded generator in a
documented, fixed order. Construction: per obstacle — center (one
`uniform(size=2)` draw), radius (one draw); then 8 spawn poses by
rejection sampling (each attempt: position `uniform(size=2)` + heading
draw), with a hard attempt cap that raises a constraint-naming error when
exceeded (FR-011). Per `reset()`: one spawn-index integer draw, then one
emission-noise draw (`standard_normal(10)`). Per step: physics (no RNG),
then one emission-noise draw. No other draws exist.

**Rationale.** This mirrors the reference world's discipline (construction
prefix, one index draw per reset, one noise draw per emission) so the
engine's downstream draws (frame births, action sampling) stay in a fixed
relative order — the property every byte-identity claim in this repo rests
on (PRA-01 §7.1). Rejection sampling is deterministic per seed because the
attempt sequence is; the cap turns "unsatisfiable layout" into a
deterministic constructor error instead of a hang (spec edge case).

**Alternatives considered.** A separate world-private RNG — unnecessary
(nothing here needs stream isolation) and would break the world-from-seed-
prefix property that snapshots rely on for the reference family. Fixed
hand-authored map — kills the "every seed is a fresh map" charm and hides
the determinism story instead of demonstrating it.

## R5 — The telemetry tap: world-side recording + a pass-through bus factory

**Decision.** `RoverTelemetry` receives two kinds of access, both with
zero run-path cost beyond plain value copies:
1. **Pose stream** — `RoverWorld` calls `tap.record_reset(x, y, θ)` /
   `tap.record_step(x, y, θ, bump)` after each emission: deque appends of
   Python floats (the L1 occupancy-counter precedent: the world owns its
   ground truth and may count it; the engine never knows).
2. **Learning state** — the tap's `bus_factory(processor)` stores the
   `FrameStore` reference and returns the standard
   `InMemorySyncBus(processor)` unchanged, so the engine's bus is
   byte-for-byte the object it would have had anyway.
All derived computation (trail copy, frame scan, scoring) happens in the
HTTP serving thread. Concurrent-mutation races (deque/groups changing
mid-scan) are handled by catch-and-fall-back to the last good snapshot —
never by locks on the run path.

**Rationale.** FR-007's letter is "no RNG, no float work in the run path";
appends of already-computed floats and one attribute assignment at bus
construction are the entire run-path footprint. The bus factory is the
one injectable seam that sees the store without touching per-step code —
using it as a *capture point only* (returning the stock bus) means the
delivery semantics cannot drift. Torn reads cost at most one stale viewer
frame at ≤ 5 Hz polling; a run-path lock would cost every step something
and invert the design's priority (the run is the product, the viewer is a
guest).

**Alternatives considered.** A wrapping Scorer that records at each scan —
byte-identical but only fires at consolidation cadence and entangles the
tap with scoring; rejected. Reading engine internals from the tap thread
via frame hacks — no public surface, brittle; rejected. A snapshot-store
based tap (Doc 06 codec each cycle) — heavyweight, cycle-cadence, and
snapshots are opt-in state, not telemetry; rejected.

## R6 — What the viewer shows is only what the system already measures

**Decision.** The learning panel displays, sampled at poll time from
public read-only store accessors (`frame_states()` +
`WeightedSumScorer.combine` on copies): population size, the per-dim
population histogram, the best (lowest-score) frame's dim and score, and
the best frame's prediction-error EMA as the headline trend — plus the
world panel's step/episode counters. The trend chart is client-side
accumulation of polled values; nothing is smoothed server-side. When the
run ends the tap serves the final canonical summary.

**Rationale.** SC-006 (honest telemetry): every displayed number is a
quantity with an existing definition in PRA-01 — the EMAs are the survival
inputs, the score is the actual selection criterion, best_dim is the
recorded acceptance reading. The best frame's `pred_err_ema` is the most
truthful continuous proxy for "how well does the winning model predict
right now" that exists without touching the engine (the engine's own
per-step `pred_errors` list is internal state; duplicating its computation
outside would be a parallel metric, violating the no-invention rule).

**Alternatives considered.** Serving per-step mean elect prediction error
— requires engine changes or recomputation (rejected as above). Showing
map_fraction/loss events — available in principle from the same scan but
noisy to explain; deferred to keep the first panel legible.

## R7 — Viewer transport: stdlib HTTP + one self-contained page + polling

**Decision.** `start_viewer(tap, port)` runs a
`ThreadingHTTPServer` (daemon threads) bound to `127.0.0.1`, serving
exactly three routes: `/` (the HTML page, shipped as package data and
read via `importlib.resources`), `/layout` (static world geometry JSON,
fetched once), `/state` (the tap snapshot JSON, polled every ~250 ms).
The page is one file: inline CSS/JS, canvas rendering, no external
resources, no build step. Port 0 binds an ephemeral port; the actual URL
is always returned/printed. Requesting a busy port fails with a clear
message.

**Rationale.** FR-006/SC-005: `http.server` + polling is the entire
transport the demo needs at 4 Hz for one viewer; WebSockets/SSE would add
either dependencies or hand-rolled protocol code — cost without benefit
at this rate. `127.0.0.1` binding states the truth (this is a local demo,
not a service). Splitting `/layout` from `/state` keeps the poll payload
small (trail + counters + learning readings, no obstacle list every
tick).

**Alternatives considered.** SSE over `http.server` — keeps a thread per
client pinned and complicates shutdown; polling is simpler and testable
with plain `urllib`. Writing JSON to a file and viewing with a static
page — breaks the one-command story (needs a second server or file://
CORS pain).

## R8 — Pacing lives in the world, not the viewer

**Decision.** `RoverWorld` accepts `step_delay` (seconds; default 0). The
CLI maps `--fps N` to `step_delay = 1/N` (default 50; `--fps 0` disables).
The delay is a `time.sleep` after the step's emission — wall-clock only.
The viewer has no influence on pacing whatsoever.

**Rationale.** Watchability is a property of the *demo run* (a human
needs ~tens of steps per second), not of the observer — conflating the
two would make the viewer perturb the run by design. Sleep consumes no
RNG and performs no float work on run state; byte-identity under pacing
is integration-tested (FR-009). Default 50 steps/s puts the full
reference schedule (25 warmup episodes + 50 cycles × 6 episodes × 40
steps = 13 000 steps) at ≈ 4.3 minutes — inside the five-minute exit
criterion end to end, with the prediction-error trend visibly moving in
the first minute.

**Alternatives considered.** Viewer-driven pacing (server slows the run
while clients are connected) — violates non-perturbation categorically.
Pacing in the engine — engine changes are off the table.

## R9 — A dedicated `pra-rover` command; the rover stays out of `Config.world`

**Decision.** Ship a new console script `pra-rover` (in
`pra.examples.rover.cli`) rather than a `pra-validate rover` subcommand,
and do NOT add `"rover"` to `Config.world`/`make_world`.

**Rationale.** `pra-validate` is the measurement harness: multi-seed,
verdict-producing, run-judge-exit. The rover is an *experience*:
single-seed, long-running, serving HTTP, holding the process open for
watching. Folding a server into the harness CLI would blur the promise
each tool makes. `Config.world` is the validation-world family whose
members carry degenerate-dial byte-identity obligations and snapshot
semantics (feature 005); the rover is an example mounted through the
library seam, exactly as a user's own world would be — which is the
better teaching, too. The library mount (`Engine(cfg,
world_factory=make_rover_body)`) remains one line for anyone (including
A4 drive research) who wants rover runs under harness machinery.

**Alternatives considered.** `pra-validate rover` — rejected per above;
also `--strict`/report semantics make no sense for a demo. A
`python -m pra.examples.rover` module runner only — kept as a bonus
(`cli.main` is `__main__`-callable) but the named script is the
five-minute path.

## R10 — What "watch frames learn the map" honestly means at B1

**Decision.** The demo runs the pinned random policy (the validation
baseline). The claim the viewer makes — stated on the page — is:
observations from the rover's sensors are being predicted better over
time by a self-restructuring population of frames, live before your eyes
(falling best-frame prediction-error EMA, population settling, best_dim
stabilizing). The demo does NOT claim the rover *navigates*: action
selection is random; nothing is goal-seeking yet.

**Rationale.** Honesty rule. A random-walking rover whose *brain
telemetry* visibly improves is exactly what the validated system does and
is compelling without overclaiming. Directed behavior (curiosity/
competence drives on the rover) is A4's measured work; the CLI's summary
prints the single-seed "demo, not a validated claim" caveat the harness
uses for single-seed runs.

**Alternatives considered.** Shipping the demo with a drive enabled by
default — tempting visually, but T7's own history (novelty-seeking losing
to random in uniform worlds) says drive behavior on a new world is a
research result, not a default; it would also break "the demo is the
validated baseline configuration".
