# PRA Roadmap

**The thesis:** PRA is an open-source continuously-learning agent brain for
hobbyists and makers — people who want to point a learning system at a world
(a simulation, a game, a robot) and *experiment* with it. "Usable" means:
install in one command, mount a world through the Body API, watch it learn
live, keep what it learned, share it.

**The honest starting point (July 2026):** the core is validated, deterministic,
and byte-reproducible — on small synthetic worlds. The scaled selection
ecology works: three measured rules (fair judge, conveyor correction,
lifetime cap) hold the scaled reference at medians 10/9/9 across true_dim
20/35/50, 24/24 anchored runs, and selection lands stably at the
price-optimal dimensionality at every scale and budget (JOURNEY.md ch.
11–14), and every scaled acceptance criterion is measured — T3's amended
scaled form passes 24/24 (ch. 15–16; the edge over learned persistence is
real in every seed, and thin: ~⅓ of the reference margin, presumably
budget-bound). Still open: the competence drive is validated only for
uniformly-learnable worlds; the engine assumes a single sequential
experience stream and an environment that can `reset()`. Nothing here is hidden — it is the measured state of the
system, and the roadmap is sequenced so that no user-facing milestone ships
ahead of the capability that makes it worth watching.

**No dates.** Milestones are gated on exit criteria, not calendars. Order
within a phase is flexible; order *between* phases mostly is not — the
dependency notes say when it isn't.

---

## Operating principles

1. **Research gates before showcase spends.** A demo of a brain that visibly
   flails makes the project look broken, not promising. Every user-facing
   milestone names the research gate it depends on.
2. **Never lose the instrument panel.** Every new world keeps known ground
   truth, determinism, and steppable time until the science says the brain is
   ready for worlds without them. Real-time worlds (games-as-a-service,
   hardware) come last because they run at 1× and can't be replayed.
3. **Reference-preserving forever.** Every change keeps the validated
   reference behavior byte-identical (the T1–T7 gate). This is the project's
   constitution and it does not relax for product work.
4. **Honest criteria, stated before the work.** Each milestone's exit
   criterion is written down here first; if it proves degenerate it is amended
   openly, never tuned quietly (the T7 precedent).

---

## Phase A — Make the brain worth watching (research)

The bottleneck is the brain, not the plumbing. A1 — which blocked everything
that runs at scale — A2, and A3 are done; A4 is the highest-leverage open
item in the repo, and the ladder's first results added a named open
problem beside it (channel-noise robustness, LADDER-CRITERIA.md L3).

### A1. The seventh scale rule — ✅ done (JOURNEY.md ch. 11–14)
Resolved beyond its original scope. The fair judge (`score_window_steps`)
plus the constant-free conveyor correction retired `survive_threshold_base`
(ch. 11); the diagnosis underneath found lifetime rot, and the eighth rule
(`weight_norm_cap`) eliminated it (ch. 13–14). All three are `pra-validate
scale` defaults, with climbing proposals.
*Exit criterion met:* medians 10/9/9 at td 20/35/50, 24/24 anchored runs,
mature niche populated, no collapse across budgets; reference suite
byte-identical. One criterion was amended openly along the way (principle 4):
"best_dim tracks true_dim" is closed by measurement — the scaled world
carries no true_dim signature, and what T-SCALE honestly claims is that
selection lands at the price-optimal dimensionality, stably.

### A2. T3's persistence clause at scale — ✅ done (JOURNEY.md ch. 15–16)
The last acceptance criterion never measured on the scaled worlds: T3's
strong clause — the system predicts better than a learned
"assume-nothing-changes" baseline — was validated at reference scale only.
*Exit criterion met, in two acts:* as written, T3 **FAILs at td 20 and 35**
(2/8 seeds) — diagnosed as the criterion, not the capability, breaking at
scale (the population-mean measure reads the juvenile conveyor). The
**churn-matched amendment** (pre-registered, per the T7 precedent) then
**PASSed at all three scales, 24/24 paired seeds positive** (margins
+0.021/+0.028/+0.026 — flat across scales, ~⅓ of reference; as-written
counts kept in the record). Every scaled acceptance criterion is now
measured. Trail: `design/validate/T3SCALE-DIAGNOSIS.md`; instrument:
`pra-validate scale --t3` (the quartet).

### A3. The complexity ladder (worlds with ground truth) — ✅ done (JOURNEY.md ch. 17)
A family of synthetic worlds that get *harder in known ways*: non-uniform
learnability (an unlearnable region of latent space), compositional
latents, distractor dimensions — the controlled staircase between
"curated" and "real", every rung keeping true structure known.
*Exit criterion met:* the family ships in-repo (`Config.world`,
`pra-validate ladder`, degenerate dials byte-identical to the reference),
criteria pre-registered, and first results recorded **including failures**:
compositional and structured-distractor rungs PASS (selection lands
part-sized and never buys the distractor); strong region noise widens the
landing spread (dose-dependent, real); **high-amplitude channel static
collapses it** — the ladder's first new open problem, named
channel-noise robustness. One criterion clause (occupancy band) was
amended openly after its distributional assumption was refuted by the
data. Trail: `design/validate/LADDER-CRITERIA.md`.

### A4. The drive blend for non-uniform worlds — ✅ done (JOURNEY.md ch. 18 + 24)
The open curiosity/competence blend (camping risk), measured on the A3
ladder — in two acts. Act one (ch. 18) **dissolved the blend question**:
both drives steer the lookahead with one shared novelty statistic, so no
blend surface existed. Act two (ch. 24) built the missing piece — the
**frontier drive** (realized local learning progress, the first
per-candidate term independent of novelty — Doc 05's predicted-LP [O]
gap, closed) — and re-measured at proper power (24 seeds, the B4
protocol lesson). *Exit criterion met:* **competence and the
frontier+competence blend both beat random in a strict majority of seeds
at every horizon, at both noise dials** (ch. 18's mild-noise equivocation
was statistical power, not capability). Frontier alone is positive and
noninferior everywhere, occupies between the poles (neither camps nor
stares), and matches — does not beat — competence on L1, where avoidance
is simply optimal; the worlds where it should earn its keep
(mastered-then-changing, multi-region learnable) are named future
research. Showcase guidance: `competence` on non-uniform worlds, both
dials. Trails: `BLEND-DIAGNOSIS.md`, `PREDLP-DIAGNOSIS.md`.

---

## Phase B — Make it usable (platform)

Phase B is complete (B1–B7); B3/B4 were engine work that everything in
Phase C depends on. The platform successors added 2026-07-18 (JOURNEY.md
ch. 27) were sequenced strictly B6 → B7 — one transport, built once —
and both landed the same day: **B6**, the external bus backend (ch. 28),
and **B7**, the dashboard that consumes its subjects (ch. 29).

### B1. The watchable world (`examples/` + live viewer) — ✅ done (JOURNEY.md ch. 20)
An in-repo 2D rover world with a built-in web viewer: `pip install poseres`,
one command, a browser tab opens, you watch frames learn the map. Deterministic,
resettable, zero extra dependencies. This — not any branded game — is the
getting-started experience.
*Exit criterion met (feature 006):* `pra-rover` — a 2D rover world (5-ray
rangefinder / compass / gps / bumper anatomy at the validated reference
widths) through the Body seam on the unchanged engine, with a stdlib live
viewer. Install → watching in under five minutes (default paced run
≈ 4.3 min end to end); the example run is byte-reproducible — tested,
including viewer-on ≡ viewer-off under live polling. The demo claims
*predicting*, never *navigating* (the policy is the pinned random
baseline; directed behavior is A4's measured work).

### B2. The Gymnasium adapter — ✅ done (JOURNEY.md ch. 19)
A `GymnasiumBody` (optional dependency) mounts any Gymnasium environment
with a discrete action space and Box observations behind the existing body
seam. The episode-termination mismatch is resolved explicitly: immediate
seeded respawn inside the fixed-length PRA episode, terminal observation
discarded, respawns counted (the boundary is honestly unpredictable —
and shrinks with competence).
*Exit criterion met:* CartPole worked example in `examples/` (runs the
reference schedule in ~3 s/seed, proves its own byte-identity); adapter
contract tests cover conformance, every rejection path, and the respawn
mechanics; the termination decision is documented with rejected
alternatives (specs/007-gymnasium-adapter/research.md R2). Deferred with
owners: Box actions (future), reward-as-sensor (future), episode
semantics (B3), external-world snapshots (B5).

### B3. Continuous operation (no `reset()`) — ✅ done (JOURNEY.md ch. 21)
Virtual episode boundaries for worlds that cannot restart — the prerequisite
for MMOs, hardware, and anything persistent. Changes engine semantics, so it
got its written design first (specs/008, research R1–R10), including what
consolidation boundaries mean without resets (nothing — the slow loop was
always a cadence in experience), the reproducibility story (episodic modes
byte-frozen; continuous deterministic per seed; resume exact via the new
optional world-state capture protocol, loud failure without it), and
single-boot-as-contract for hardware (the C2 answer, guard-world-tested).
*Exit criterion met:* a world that raises on any second reset runs the full
schedule to a byte-reproducible summary; validated modes untouched. The
first reading is recorded with a finding: the mode is healthy on bounded
worlds (rover: no degradation), while the reference world — an unbounded
latent walk — drifts and saturates when run unbroken (improvement −0.17,
best_dim → 1, 8/8 seeds): **continuous deployments need recurrent worlds**,
the stated guidance for C1/C2.

### B4. Multi-stream experience (N worlds, one brain) — ✅ done (JOURNEY.md ch. 22)
Parallel world instances feeding one brain — the bus seam's moment, and the
only honest answer to "learning is too slow" (parallelism beats wall-clock
only in steppable worlds). Design-first (specs/009 research R1–R8):
randomness split by ownership (per-stream spawn-key generators for
exploration; one merge-order brain generator), K worlds of one structure by
identical construction seeding, episode round-robin merge, consolidation
cadence in total experience.
*Exit criterion met — with a protocol lesson recorded:* the pre-registered
8-seed comparison FAILed on a statistical flaw (its "paired" margins pair
nothing across generator realizations; underpowered), diagnosed and
amended openly; at 24 seeds K ∈ {2, 4} **matches the single-stream
baseline per unit of experience** (margins ≈ −0.004/−0.003, noninferiority
PASS both). Determinism story as named: per-stream seeds, merged
deterministically; K=1 byte-identical. K>1 snapshots → B5. Trail:
`specs/009-multi-stream/reading.md`.

### B5. Snapshot completeness — ✅ done (JOURNEY.md ch. 23)
Snapshots of anatomy-resized runs (the deferred Doc 06 format-version
follow-up), a stated persistence story for external worlds, and the
multi-stream capture debt from B4 — all paid under one principle: code
from the caller, state from the blob.
*Exit criterion met:* resize → snapshot → resume is byte-identical (grown
dims recorded and verified; wrong anatomy fails loudly); the per-world-class
guarantees — including what is **not** guaranteed (live services, hardware)
— are written down in Doc 06 §5b; Gymnasium runs resume exactly in episodic
mode via the capture-required marker; multi-stream runs snapshot all stream
positions. Bonus repair: a pre-existing one-ULP resume-exactness bug
(frame-group order lost to sorting in the blob) found by this feature's
tests and fixed — group order now travels as lived.

### B6. External bus backend (NATS/JetStream) — ✅ done (JOURNEY.md ch. 28)
The next link in the distributed-operation chain (A1 → B4 → **this** →
multi-machine). The framing that was considered and rejected (JOURNEY.md
ch. 27): NATS *underneath* the engine. The fast loop is a batched
in-process kernel whose validation story is byte-identity; a network hop
inside it breaks both throughput and the T1–T7 gate. NATS enters **at
the seams**, opt-in, with the reference paths byte-frozen — the same
pattern as every feature since 001:

- **Bus backend** (Doc 02's stated purpose): run telemetry fanned out as
  subjects, so any external process can tap a live brain without touching
  the run path — the B1 viewer discipline, generalized off-process.
- **Snapshot transport**: the SnapshotStore seam backed by a JetStream
  object store. This is also Phase D's "shareable brains" transport,
  bought once.
- **Control plane**: request/reply for pause / snapshot / inspect —
  the management surface B7 and any future fleet tooling sit on.
- **Inter-brain communication** (broadcast / anycast / unicast): named as
  the horizon this enables, deliberately *not* in this item's exit —
  brain-to-brain semantics are research, not plumbing.

The determinism line is drawn in the spec before code: telemetry **out**
is observer-safe (the B1 viewer precedent — non-perturbation proven by
byte-identity tests); experience **in** over a network is a Doc 06 §5b
class-4 mode (openly non-reproducible), stated up front, never
discovered.
*Gate:* B4 (done). Design-first: spec-kit feature with the seam
inventory and the determinism boundary written before code.
*Exit criteria met (feature 014):* `pra.nats` — one tap binding three
existing injection seams (a delegating world wrapper with the pause
gate, the B1 viewer's `bus_factory` capture, a snapshot-store wrapper at
the C4 write site), a versioned run-scoped subject scheme (`pra.v1.…`),
a JetStream object-store `SnapshotStore` backend, and a three-command
control plane with honest deferred snapshot fulfillment. Reference suite
byte-identical with the backend absent *and* attached (same-seed
two-run tests, incl. multi-stream continuous); the run never waits on
the network (bounded buffer, derived drop counts, outage tests); a
paused-and-resumed run completes byte-identical to a never-paused one;
snapshot round-trip and cross-store resume equivalence proven at
reference and scaled-blob sizes; every gate test runs on the in-repo
fake transport — no NATS library or server, zero skips. The real stack
measured, not hoped: `examples/nats/demo.py` ran green end-to-end
(discovery, live telemetry off-process, pause frozen + verified,
snapshot fulfilled at the C4 boundary and pulled back from JetStream,
decoded, all proofs pass) against nats-server with `nats-py` 2.15.
Doc 06 §5b records the class of every NATS-touching mode.

### B7. Web dashboard / monitor — ✅ done (JOURNEY.md ch. 29)
The B1 viewer generalized: one dashboard for any PRA brain, consuming the
B6 telemetry subjects and control plane — never a second transport. Two
modes: **simple** (what the brain is doing, for a person standing in
front of it) and **advanced** (population census, best_dim trajectory,
score surfaces, per-frame detail — the researcher's instrument panel).
Honest split of its two purposes: the *monitor* half is an instrument
and ships here; the *"show what makes PRA unique"* half is a showcase
spend and obeys principle 1 — published demo material inherits C1/C2's
gates.
*Gate:* B6 (met).
*Exit criteria met (feature 015):* `pra.dash` + `pra-dash` — a pure
consumer of the documented B6 surface (subjects, three control commands,
discovery; structurally nothing else), serving one self-contained page
with simple and advanced modes. The named gap closed additively on the
tap: a world-view telemetry family (`tele.view.static`/`.live`) whose
adapter speaks the rover's existing three-call telemetry surface, so the
rover mounted unchanged. Observer safety re-proven at this layer:
byte-identity with the dashboard attached and hammered by a polling
thread (reference world, rover-with-view, multi-stream continuous,
attach/detach mid-run), pause-through-the-dashboard byte-identical to
never-paused, every control error reply surfaced verbatim. The real
stack measured: `dashboard_demo.py` green end-to-end (world view
consumed and served, pause frozen at step 145, snapshot fulfilled
through the dashboard's own endpoint), and both modes verified rendering
in an actual browser — arena, obstacles, pose, live trail, census
history, histogram, counters. One instrument bug caught by that browser
session and fixed with a regression test: per-subject seq-gap counting
misread the shared mirror family as drops. Zero engine edits; gate
NATS-free, server-free, browser-free, zero skips.

---

## Phase C — Worlds makers care about (showcases)

Each showcase is a Body implementation plus a write-up. None ships before its
gate. The point of a showcase is that PRA *visibly does what the repo claims*
— structure-finding and drive-directed learning you can watch.

### C1. Live-game showcase — Minecraft (world chosen 2026-07-20)
A persistent live-game world as the long-horizon demo: one character,
learning continuously for weeks. Originally sketched as a cooldown
HTTP game (e.g. Artifacts MMO); the owner chose a small self-hosted
Minecraft server instead — easier to run (Docker), richer to live in,
same story: a deployment, not a lab.
*Gate:* B3 (no reset), B5 (external persistence), A4 (non-uniform drive).
*Exit:* a multi-week continuously-learning run with published telemetry.
*Platform half DONE (feature 027, JOURNEY ch. 43):* the pra-mc/1
transport on the unchanged 013 seam, FakeBridge-carried gate, mineflayer
bridge + compose world + runbook (`examples/minecraft/`), real stack
measured green including hard-kill + exact resume; launch posture and
config notes from arc 026 applied. The run itself is the operator's.

### C2. Hardware body (LEGO / Pybricks)
`PybricksSensor`/`PybricksActuator` over BLE; obs_dim ~6–12 fits the validated
range. Snapping a sensor onto a running robot is the physical demo of
`register_sensor`. Reset means a homing routine — solved in design (B3), not
improvised.
*Gate:* B3; a written answer to physical reset; A4 strongly advised (a room
is non-uniform).
*Exit:* a reproducible build guide a maker can follow, plus a video of
mid-run body growth.
*Platform landed (feature 013, JOURNEY ch. 26):* the **ROS2 adapter**
generalizes this slot — topic sensors/actuators as first-class body tools,
the control-tick step semantics, an explicit staleness policy, continuous
single-boot operation, and a Gazebo worked example in Docker (stepped, so
the instrument panel survives). The written answer to physical reset is
recorded: continuous mode is the hardware mode; a homing routine is an
owner-supplied reset mechanism. Free-running operation is the project's
first openly non-reproducible mode (Doc 06 §5b class 4, stated). What
remains of C2 is the *showcase* itself — a physical build, its guide, and
the mid-run growth video — on whichever body (ROS2 or Pybricks-direct) the
build uses.
*Showcase gate sharpened (2026-07-18, JOURNEY.md ch. 27):* real sensors
carry noisy channels — the Gazebo lidar already NaN-poisoned a run
(ch. 26), and channel static at sensor amplitude collapses selection
(ch. 25). **Learned channel weighting** is therefore a de facto research
gate for the physical showcase, not an unrelated open item. The build
itself (CAD, printing, electronics) is cheap and may proceed in
parallel; the growth video waits for the brain that survives real
sensor noise.

### C3. Embedded steppable game server (parked)
The Minecraft-like single binary — viable *only* as a tick-steppable fork
(deterministic, faster-than-real-time), which is a large systems project.
Parked until Phase C1–C2 prove the showcase pattern and someone (possibly a
contributor) wants to own it. The steppable-tick idea is recorded here so it
isn't lost.
*Gate:* everything above, plus a one-page spec before any code.

---

## Phase D — Make it a product (OSS hygiene)

Mostly parallel to Phase C; cheap individually, decisive together.

- **API stability & v1.0**: freeze the seam surfaces (Body, Sensor/Actuator,
  Drive, SnapshotStore), semantic versioning, deprecation policy.
  *Exit:* v1.0 tag; the seams documented as public API.
- **Docs site**: GETTING-STARTED, the design docs, and a "worlds gallery"
  rendered as a small static site. *Exit:* docs deployed, linked from README.
- **Shareable brains**: snapshots as portable artifacts ("here's my rover
  brain after 100k steps — load it"). Depends on B5. *Exit:* a snapshot
  published by one person loads and runs for another, verified.
- **Contribution surface**: CONTRIBUTING.md, good-first-issue labels on
  world/sensor/actuator implementations — the natural contributor on-ramp is
  *new bodies*, not core changes. *Exit:* first external world contribution
  merged.
- **Show, then tell**: a demo video per showcase, published with its honest
  telemetry. No demo outruns its measured capability.

---

## Horizon ambitions (beyond the phases, deliberately ungated by dates)

These are where the project is *pointed*, amended in from the original
non-goals list (see JOURNEY.md Chapter 10): they shape design decisions today
even though none is a schedulable milestone.

- **An alternative paradigm of intelligence.** PRA's long-range claim is
  against *frozen* intelligence — the trained-then-deployed model — on the
  axis where that paradigm is structurally weak: continual learning, online
  restructuring, adaptation without retraining. PRA does not compete with
  frozen LLMs at *being* a language model; whether a PRA brain can *learn*
  language from lived interaction is a gated horizon question (below,
  amended 2026-07-19 — JOURNEY.md ch. 42). When the research matures, this claim demands
  honest comparative evaluation against continual-learning and RL baselines,
  run with the same spread-and-horizons discipline as everything else.
  *Precondition:* Phase A complete and the ladder results strong enough that
  a comparison flatters no one unfairly — including PRA.
- **Distributed operation — the path to larger intelligences.** The Doc 02
  bus seam was designed for this from the start; scaling a single brain
  across machines is how the architecture is meant to grow. Sequenced, not
  skipped: A1 (done — a functioning ecology at scale) → B4 (done — multi-stream
  experience on one machine proves the merged-experience science) → the external
  bus backend (**done — B6**, feature 014: telemetry, snapshots, and control
  over NATS, the fast loop untouched) → multi-machine. The remaining link is
  the researched one: distributing the *brain itself* — inter-brain and
  cross-machine delivery semantics — which B6 deliberately excluded as
  research, not plumbing.
- **Tool self-invention.** Tagged [O] since the design docs: the registration
  interface exists (Doc 02), the inventing mechanism is unsolved research.
  On the roadmap as a named open problem — the honest form of including it —
  with the A3 ladder as its natural testbed once frames and drives are
  stable there.
- **Vision / high-dimensional input.** Follows the same rule as everything
  else: revisit when the research earns it. A paradigm claim eventually
  requires richer senses; the frame architecture is not there yet, and
  pretending otherwise would put a demo ahead of a capability.
- **Language as a learnable world** (added 2026-07-19, reversing the
  2026-07-08 exclusion — JOURNEY.md ch. 42). The founding bet
  (`design/validate/pose-resolution-architecture.md`: the same machinery
  for physical objects and abstract concepts) makes language a *world to
  learn*, not a rival's turf. The named first gate: the **teacher-world
  experiment** — observation = sentence-so-far plus teacher feedback
  (feedback is world state, not a new reward channel; the teacher is an
  object in the world), action = emit token (character-level first, ~30
  actions), an LLM as the interactive teacher (which also makes the world
  recurrent, satisfying the B3 finding). Three prerequisite decisions
  before it can run: whether the competence drive alone pulls toward
  teacher approval (predicting disapproval ≠ avoiding it — an unmeasured
  hypothesis: a systematic teacher makes sensible utterances more
  *predictable*), per-action transition slices vs realistic vocabularies
  (a mechanism gap — factored/embedded actions are kernel research, to be
  derisked small, not scaled through), and the observation encoding for
  unbounded sequences. Pre-registered prediction in ch. 42. No language
  showcase before the gate reads — the constitution applies.
- **Seeding / compounding intelligence** — ✅ **measured (feature 028,
  JOURNEY ch. 44, 2026-07-20); all three bars PASS.** The claim held: a
  snapshotted brain used as a *seed* gives the next a real head start (B1,
  +871, 21/24), the head start is *relevant transfer* not mere maturity (B2,
  +1186, 19/24 — the equal-experience unrelated-world control is if anything
  mildly *worse* than blank at a strict competence line), and it **survives
  chaining across a body-growing resize and does not shrink** (C1: seeded
  beats fresh 24/24 on the grown map, delta +177 — the head start slightly
  *grew* B→C). 24 paired seeds, rover map A→B→(+1-sensor resize)→C, three
  arms (seeded / fresh / permuted-rover maturity control), time-to-competence
  at a strict fresh-plateau line. Built as orchestration over the unchanged
  engine (no core edits). **Reversal condition untriggered — earned
  persistence is exonerated** (it protects the transferred frames for free,
  so the second-round seed-protection ideas below stay parked: no measured
  forgetting to protect against). One criterion amended openly (the pilot
  refuted the p=0.5-of-gap θ rule as degenerate; θ is now a fresh-arm-only
  strict line, full θ-sweep reported). Trail:
  `design/validate/SEEDING-DIAGNOSIS.md`. Named successors: resize-*magnitude*
  dependence, deeper chains (A→B→C→D), non-rover worlds; and the parked
  second-round seed-protection rule (age-modulated plasticity paired with an
  eviction-grace rule) — tested only *if* a future arm measurably forgets,
  facing PRA's two forgetting channels (weight drift AND eviction). Feeds the
  language-as-world horizon (seeded brains as a building block).

## Non-goals (still)

Benchmark theater (chasing leaderboard SOTA for its own sake — comparative
evaluation above is the honest substitute); any hosted service (this is OSS
you run yourself); competing with frozen LLMs on encyclopedic recall — a
stored-knowledge property, not a learning property. *Language learning* is
no longer on this list: it moved to Horizon ambitions on 2026-07-19 as a
gated research question (the 2026-07-08 exclusion reversed — JOURNEY.md
ch. 42).

## Standing risks

The brain's ceiling is the product's ceiling — if Phase A stalls, Phase C
honestly cannot ship, and the roadmap says so rather than shipping it anyway.
Single-maintainer risk: mitigated by the spec-kit discipline (every feature
leaves a spec, a plan, and a journal chapter someone else could pick up).
Demo debt: every public artifact links the telemetry behind it, so the
project's claims and its measurements cannot drift apart.

---

*Sequencing summary:* **Phase A complete (A1–A4)**; **Phase B complete
(B1–B7)** — B6 (NATS at the seams, feature 014) and B7 (the dashboard,
feature 015) both landed 2026-07-18 — C1's gate (B3, B5, A4-guidance) and C2's (B3,
physical-reset answer) are open; **C2's platform half landed** (the ROS2
adapter, feature 013 — hardware and simulators through one seam; the
showcase build/video remains) and **its research gate is cleared**:
learned channel weighting landed 2026-07-18 (feature 016,
CHANNELWEIGHT-DIAGNOSIS — L3 noise PASSES at unit amplitude at 24 seeds,
opt-in; the recorded default-config FAIL stands as the reference); the
**camping-costs question is measured** (feature 017, CAMPING-DIAGNOSIS,
2026-07-18): camping does cost — the camper recovers worst when the
world shifts — but realized LP does not collect the prize (post-shift
edge equals random's; multi-region steering pays a cost), so competence
guidance stands; the predictive-LP form was then gated before code
(arc 018, SCOUT-DIAGNOSIS, 2026-07-18) and **stopped at its gate**: no
half-comparison over the current 200-entry err@visit FIFO can detect a
regime change (the baseline is forgotten in ~5 episodes), so the
successor is a representation feature; the observation-space form of
that memory then also stopped at its offline gate (arc 019,
PLACEMEM-DIAGNOSIS, 2026-07-18): raw-observation places are **not
shift-invariant** — a dynamics shift moves where the brain goes, so
mastered anchors are not revisited — and the successor is now
two-part; the emission-shift world then completed the testbed pair
(arc 020) and action-context anchors failed the same gate (arc 021,
CONTEXTMEM-DIAGNOSIS) — **three eliminated spaces, one ~1–2× ceiling,
and a signal-level diagnosis**: per-step errors-at-visit are a tracking
signal — and the transfer stream measured next (arc 022,
TRANSFERSIG-DIAGNOSIS) **is the right signal**: direction universal on
both shift modes, ratios to 7× where tracking managed ~1×; the extended
probe (arc 023, TRANSFERSTALE-DIAGNOSIS) then measured the full
(resolution × window) plane and **closed the windowed-median family**
(best margin 0.21 at the shallow corner, ~5× short; the per-frame
fallback censored by election), the change-point arc (024,
CHANGEPOINT-DIAGNOSIS) closed jump and accumulation (best ROC 6/6
within four episodes at ~1.6% false-fire), and the election-stream arc
(025, ELECTSTREAM-DIAGNOSIS) closed the censor-read too (benign
mass-silence from the drive's own movement exceeds every shift cell's
peak) — **four families, one testbed, one verdict: the detector's
background is the brain itself; the staleness-detection program
pauses with its map complete**, successor named (scheduled probing —
active re-visit under a held policy; a Doc 05-level feature), the
tolerant gate a recorded conditional;
**C1 is the front and its runway is cleared** (arc 026,
C1SOAK-DIAGNOSIS: no reference-scale rot at 500k steps, resume
byte-identical at length, launch posture GREEN with config notes —
cap on, ~8 B/step blob growth budgeted, population at the ceiling in
continuous mode; the relative survival bar stays a named conditional
deferral); D alongside C; C3 parked.
*This file is load-bearing: changes to it are decisions and belong in
JOURNEY.md like any other.*
