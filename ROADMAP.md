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

### A4. The drive blend for non-uniform worlds — ◐ measured; the question transformed (JOURNEY.md ch. 18)
The open curiosity/competence blend (camping risk), measured on the A3
ladder. *Exit as pre-registered:* a drive configuration that beats random
on non-uniform ladder worlds in the majority of seeds at every checkpoint
— **not met at mild noise** (at σ=0.2 every arm misses at least one
horizon; the effect sits inside seed noise), met at strong noise by the
competence family (19/24 seed-horizon wins, margins ~+0.1, no structural
cost). The bigger finding **dissolved the blend question**: both drives'
only per-candidate term is the same novelty statistic, so the weight
simplex collapses to {curiosity, competence, a degenerate tie corner} —
there is no blend surface to tune. What remains of A4 is the predicted-LP
/ per-candidate-learnability lookahead (the Doc 05 [O] design), now the
only live path to a genuine blend. Interim guidance for showcases:
`competence` on strongly non-uniform worlds; nothing directed
demonstrably beats random on mildly non-uniform ones at reference
budgets. Trail: `design/validate/BLEND-DIAGNOSIS.md`.

---

## Phase B — Make it usable (platform)

Phase B is complete (B1–B5); B3/B4 were
engine work that everything in Phase C depends on.

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

---

## Phase C — Worlds makers care about (showcases)

Each showcase is a Body implementation plus a write-up. None ships before its
gate. The point of a showcase is that PRA *visibly does what the repo claims*
— structure-finding and drive-directed learning you can watch.

### C1. Game-over-API showcase (e.g. Artifacts MMO)
A persistent HTTP-API world as the long-horizon demo: one character, learning
continuously for weeks. Cooldowns (3–30s/action) make it a terrible lab and an
acceptable *deployment* — which is exactly the story it tells.
*Gate:* B3 (no reset), B5 (external persistence), A4 (non-uniform drive).
*Exit:* a multi-week continuously-learning run with published telemetry.

### C2. Hardware body (LEGO / Pybricks)
`PybricksSensor`/`PybricksActuator` over BLE; obs_dim ~6–12 fits the validated
range. Snapping a sensor onto a running robot is the physical demo of
`register_sensor`. Reset means a homing routine — solved in design (B3), not
improvised.
*Gate:* B3; a written answer to physical reset; A4 strongly advised (a room
is non-uniform).
*Exit:* a reproducible build guide a maker can follow, plus a video of
mid-run body growth.

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
  restructuring, adaptation without retraining. Not "beat LLMs at language";
  language is not PRA's axis. When the research matures, this claim demands
  honest comparative evaluation against continual-learning and RL baselines,
  run with the same spread-and-horizons discipline as everything else.
  *Precondition:* Phase A complete and the ladder results strong enough that
  a comparison flatters no one unfairly — including PRA.
- **Distributed operation — the path to larger intelligences.** The Doc 02
  bus seam was designed for this from the start; scaling a single brain
  across machines is how the architecture is meant to grow. Sequenced, not
  skipped: A1 (done — a functioning ecology at scale) → B4 (multi-stream experience
  on one machine proves the merged-experience science) → an external bus
  backend (e.g. NATS/JetStream) → multi-machine. Distributing a brain whose
  scale rules are still breaking would distribute the failure.
- **Tool self-invention.** Tagged [O] since the design docs: the registration
  interface exists (Doc 02), the inventing mechanism is unsolved research.
  On the roadmap as a named open problem — the honest form of including it —
  with the A3 ladder as its natural testbed once frames and drives are
  stable there.
- **Vision / high-dimensional input.** Follows the same rule as everything
  else: revisit when the research earns it. A paradigm claim eventually
  requires richer senses; the frame architecture is not there yet, and
  pretending otherwise would put a demo ahead of a capability.

## Non-goals (still)

Benchmark theater (chasing leaderboard SOTA for its own sake — comparative
evaluation above is the honest substitute); any hosted service (this is OSS
you run yourself); competing on language and encyclopedic knowledge — that is
LLMs' home turf and not PRA's axis.

## Standing risks

The brain's ceiling is the product's ceiling — if Phase A stalls, Phase C
honestly cannot ship, and the roadmap says so rather than shipping it anyway.
Single-maintainer risk: mitigated by the spec-kit discipline (every feature
leaves a spec, a plan, and a journal chapter someone else could pick up).
Demo debt: every public artifact links the telemetry behind it, so the
project's claims and its measurements cannot drift apart.

---

*Sequencing summary:* A1–A3 done; A4 measured (its remainder is the
predicted-LP lookahead design); **Phase B complete (B1–B5)** — C1's gate
(B3, B5, A4-guidance) and C2's (B3, physical-reset answer) are open;
C1/C2 next alongside the open research (predicted-LP, channel-noise);
D alongside C; C3 parked.
*This file is load-bearing: changes to it are decisions and belong in
JOURNEY.md like any other.*
