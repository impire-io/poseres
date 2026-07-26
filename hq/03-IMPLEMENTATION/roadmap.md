# PRA Roadmap

What is still to be built, in what order, behind which gates. **No dates** —
milestones are gated on exit criteria, not calendars. Completed work lives in
the ledger at the bottom, one line each, with its full story in the journey
episode; the operating principles this plan obeys are the
[constitution](../00-GENESIS/constitution.md), and the ambitions it serves
are in [vision.md](../00-GENESIS/vision.md).

---

## Now — the front

### C1. Live-game showcase — the Minecraft run

The platform is done (feature 027,
[episode 0043](../04-JOURNEY/0043-the-brain-moves-into-minecraft.md)): the
`pra-mc/1` transport on the unchanged 013 seam, the FakeBridge-carried gate,
the mineflayer bridge + compose world + runbook in `examples/minecraft/`,
hard-kill + exact resume measured green. The runway is cleared
([episode 0041](../04-JOURNEY/0041-the-soak-before-the-weeks.md): no
reference-scale rot at 500k steps, resume byte-identical at length, launch
posture GREEN — cap on, ~8 B/step blob growth budgeted, population at the
ceiling in continuous mode).

- *What remains:* **the run itself — the operator's.** One character,
  learning continuously for weeks.
- *Exit:* a multi-week continuously-learning run with **published telemetry**.
- *Named conditional:* the relative-survival bar from the soak stays a
  recorded deferral — revisited if the long run surfaces it.

## Next — showcases

### C2. Hardware body — the physical build

Platform and research gates are both met: the ROS2 adapter
([episode 0026](../04-JOURNEY/0026-the-ros2-adapter.md)) gives hardware and
simulators one seam (continuous single-boot is the hardware mode; a homing
routine is an owner-supplied reset), and learned channel weighting
([episode 0030](../04-JOURNEY/0030-learned-channel-weighting.md)) cleared
the sensor-noise gate.

- *What remains:* the **showcase itself** — a physical build (ROS2 or
  Pybricks-direct), a reproducible build guide a maker can follow, and a
  video of mid-run body growth. The build (CAD, printing, electronics) is
  cheap and may proceed in parallel; the growth video waits for nothing —
  its gates are met.

### C3. Embedded steppable game server — parked

Viable *only* as a tick-steppable fork of a Minecraft-like single binary
(deterministic, faster-than-real-time) — a large systems project. Parked
until C1–C2 prove the showcase pattern and someone (possibly a contributor)
wants to own it; the steppable-tick idea is recorded here so it isn't lost.
*Gate:* everything above, plus a one-page spec before any code.

## Phase D — Make it a product (OSS hygiene)

Mostly parallel to Phase C; cheap individually, decisive together.

- **API stability & v1.0**: freeze the seam surfaces (Body, Sensor/Actuator,
  Drive, SnapshotStore), semantic versioning, deprecation policy.
  *Exit:* v1.0 tag; the seams documented as public API.
- **Docs site**: GETTING-STARTED, the design docs, and a "worlds gallery"
  rendered as a small static site. *Exit:* docs deployed, linked from README.
- **Shareable brains**: snapshots as portable artifacts ("here's my rover
  brain after 100k steps — load it"). *Exit:* a snapshot published by one
  person loads and runs for another, verified.
- **Contribution surface**: CONTRIBUTING.md, good-first-issue labels on
  world/sensor/actuator implementations — the natural contributor on-ramp is
  *new bodies*, not core changes. *Exit:* first external world contribution
  merged.
- **Show, then tell**: a demo video per showcase, published with its honest
  telemetry. No demo outruns its measured capability (constitution IV).
- **The book**: the long-form narrative (`book/` — four parts drafted;
  contract in `book/STYLE.md`; decision recorded in
  [episode 0047](../04-JOURNEY/0047-the-book-decision.md)). Part 5
  (teachers) waits on the teacher-world research candidate. *Exit:* every
  chapter through the STYLE revision checklist, the REVISIT backlog
  arbitrated by the maintainer, and the numbers audit re-verified against
  the repo at publication date.

## Research candidates (gated; each becomes a `/research-start` topic when picked up)

Named open questions, none scheduled. The ambitions they serve are in
[vision.md](../00-GENESIS/vision.md); what's listed here is the concrete
next experiment each one is gated behind.

- **Language — the teacher-world gate**
  ([episode 0042](../04-JOURNEY/0042-the-vision-re-broadened.md)):
  observation = sentence-so-far + teacher feedback as world state, action =
  emit token, an LLM as the interactive teacher. Three prerequisite
  decisions before it can run: competence-drive-vs-approval (unmeasured
  hypothesis: a systematic teacher makes sensible utterances more
  predictable), factored/embedded actions for realistic vocabularies
  (kernel research — derisk small), and observation encoding for unbounded
  sequences. Pre-registered prediction in 0042: the current kernel plateaus
  short of syntax. No language showcase before the gate reads.
- **Staleness detection — closed, passive and active**
  ([episode 0059](../04-JOURNEY/0059-scheduled-probing.md)): scheduled
  probing, the active successor, failed its registered gate — the benign
  band crossed above the shift band under total route control; the
  detector's window is the brain's own relearning speed. The ch. 39
  tolerant gate (~1.6% false-fire) stays the recorded deployment
  conditional; reopening requires an episode-0059 named door with a fresh
  registered gate, or a brain that measurably relearns slower than one
  episode.
- **Distributing the brain itself** — the remaining link of the chain
  A1 → B4 → B6 → multi-machine: inter-brain and cross-machine delivery
  semantics (broadcast / anycast / unicast), which B6 deliberately excluded
  as research, not plumbing.
- **Seeding successors**
  ([episode 0044](../04-JOURNEY/0044-brain-seeding.md)): resize-*magnitude*
  dependence, deeper chains (A→B→C→D), non-rover worlds. Parked conditional:
  the second-round seed-protection rule (age-modulated plasticity +
  eviction-grace) — tested only *if* a future arm measurably forgets, facing
  both forgetting channels (weight drift AND eviction).
- **Tool self-invention** — tagged [O] since the design docs: the
  registration interface exists (Doc 02), the inventing mechanism is
  unsolved; the A3 ladder is its natural testbed.
- **Vision / high-dimensional input** — revisit when the research earns it;
  the frame architecture is not there yet.
- **Comparative evaluation** vs continual-learning and RL baselines, with
  the same spread-and-horizons discipline as everything else.
  *Precondition:* ladder results strong enough that the comparison flatters
  no one unfairly — including PRA.
- **Platform deferrals** (small, owners recorded in their specs): Gymnasium
  Box actions; reward-as-sensor.

## Standing risks

The brain's ceiling is the product's ceiling — if the research stalls,
showcases honestly cannot ship, and this file says so rather than shipping
them anyway. Single-maintainer risk: mitigated by the spec-kit + journey
discipline (every feature leaves a spec, a plan, and an episode someone else
could pick up). Demo debt: every public artifact links the telemetry behind
it, so the project's claims and its measurements cannot drift apart.

---

## Done — the ledger

One line per landed milestone; the full story (numbers, refutations,
amendments) is in the linked episode. Letters are stable — code comments
like "ROADMAP A3" resolve here.

| Item | What landed | Episode(s) |
|---|---|---|
| A1 | Seventh + eighth scale rules: fair judge, conveyor correction, lifetime cap — scaled ecology anchored 24/24 | [0011](../04-JOURNEY/0011-the-threshold-diagnosis.md)–[0014](../04-JOURNEY/0014-the-eighth-rule.md) |
| A2 | T3 at scale: churn-matched amendment PASSes 24/24 at all scales | [0015](../04-JOURNEY/0015-t3-at-scale.md)–[0016](../04-JOURNEY/0016-the-amendment-pays.md) |
| A3 | Complexity ladder: three ground-truth worlds, criteria pre-registered, failures named | [0017](../04-JOURNEY/0017-the-complexity-ladder.md) |
| A4 | Drive blend dissolved → frontier drive; exit met at 24-seed power | [0018](../04-JOURNEY/0018-the-blend-dissolves.md), [0024](../04-JOURNEY/0024-the-frontier-drive.md) |
| B1 | Watchable rover world + live viewer (feature 006) | [0020](../04-JOURNEY/0020-the-watchable-rover-world.md) |
| B2 | Gymnasium adapter (feature 007) | [0019](../04-JOURNEY/0019-the-gymnasium-adapter.md) |
| B3 | Continuous operation, no reset (feature 008) — finding: continuous deployments need recurrent worlds | [0021](../04-JOURNEY/0021-continuous-operation.md) |
| B4 | Multi-stream: N worlds, one brain (feature 009) | [0022](../04-JOURNEY/0022-multi-stream.md) |
| B5 | Snapshot completeness incl. grown bodies + external worlds (feature 010) | [0023](../04-JOURNEY/0023-snapshot-completeness.md) |
| B6 | NATS at the seams: telemetry, snapshots, control plane (feature 014) | [0028](../04-JOURNEY/0028-nats-at-the-seams.md) |
| B7 | Web dashboard, pure consumer of the B6 surface (feature 015) | [0029](../04-JOURNEY/0029-one-face-for-any-brain.md) |
| C2-platform | ROS2 adapter (feature 013) + channel weighting research gate (feature 016) | [0026](../04-JOURNEY/0026-the-ros2-adapter.md), [0030](../04-JOURNEY/0030-learned-channel-weighting.md) |
| C1-platform | Minecraft body + bridge, launch-ready (feature 027) + soak (arc 026) | [0043](../04-JOURNEY/0043-the-brain-moves-into-minecraft.md), [0041](../04-JOURNEY/0041-the-soak-before-the-weeks.md) |
| C1-watching | Brain telemetry family + introspection dashboard (feature 029); one-command stack `up.sh` with auto-spectate + `TICK_RATE` | [0048](../04-JOURNEY/0048-the-brain-gets-a-window.md) |
| C1-body | The builder's body (feature 030): inventory sense + pocket crafting, materially honest placement (owner's call, reversal recorded) | [0049](../04-JOURNEY/0049-the-builders-body.md) |
| C1-primitives | Honest primitives (feature 031): macros out, held-class selection + sensed staging grid in; 28/12 default, crafting = emergence question with a measured chance baseline | [0050](../04-JOURNEY/0050-the-ladder-not-the-button.md) |
| C1-observatory | The observatory (feature 032): three layers on beno4, pra-flush buffer→S3 durability, systemd supervision, run pre-registered (C1-RUN-PLAN) | [0051](../04-JOURNEY/0051-the-observatory.md) |
| C1-senses | The property body (feature 033): classifier-free senses (properties + signatures), dig as held intention with sensed progress, labeled channels + ground truth | [0052](../04-JOURNEY/0052-senses-without-my-ontology.md) |
| C1-drive | Competence-alone camped on stasis (idle 26.7%, mechanism); drive switched to FrontierDrive, run `c1b`→`c1c` fresh; anti-idle since measured GREEN (E0b, idle 3.1% — reversal not fired) | [0053](../04-JOURNEY/0053-the-brain-that-preferred-to-stand-still.md), [0054](../04-JOURNEY/0054-two-doors-one-graduate-who-walks-away.md) |
| Goals-E0/E1 | Self-set-goals rungs measured (feature 034): E0 zero chains in 328k live steps (premise stands); E1 demonstration-alone FAILs at power (taught 0/24, zero dig completions — frontier flees mastered lessons); E2 goal-object rung authorized | [0054](../04-JOURNEY/0054-two-doors-one-graduate-who-walks-away.md) |
| Goals-E2.0 | Dwell gate FAILs at power (0/24 at 20%; λ-bias orbits ~13× but can't hold) → goal-object-via-λ paused by its own reversal; context rows deliver the first deliberate chains ever (2 full across 42 goal-biased runs vs zero from frontier-alone anywhere); drawing-board fork is the owner's | [0055](../04-JOURNEY/0055-the-first-deliberate-chains.md) |
| Goals-E2.0h | Horizon read FAILs as registered: C(H) flat at 1/24 from 5k to 40k — chains decided in the departure window, λ never re-captures; λ-on-one-step-lookahead exhausted for holding and rate; instrument rebuilt from record, P0 replication green; fork narrows to E2.0b homing / E3 verdict-channel / park | [0056](../04-JOURNEY/0056-a-floor-not-a-rate.md) |
| Goals-E3.0 | Verdict-sensation gate FAILs at the precursor: approval pulses provably in the stream 45×, expectation forms in 14/24 (bar 18) with 5 seeds anti-predictive; behavior on the frozen prediction (V=M=0/24 — sensing ≠ wanting from the approval side); refutation predictor-shaped (event-sensitive predictor = named successor); fork now E2.0b or park | [0057](../04-JOURNEY/0057-approval-without-expectation.md) |
| Goals-parked | Topic parked by the owner (lifecycle: abandoned; folder retired): five gates all decided by their registered bars; standing result = the existence proof (knowledge + weak wanting produced the record's only deliberate chains); E2.0b the unexplored door; c1c the reopening watch | [0058](../04-JOURNEY/0058-self-set-goals.md) |
| Research arcs | Camping bill; scout, place-memory, emission-shift, context-memory, transfer-signal, staleness, change-point, election-stream (program paused, map complete); seeding measured | [0031](../04-JOURNEY/0031-the-camping-bill.md)–[0040](../04-JOURNEY/0040-reading-the-censor.md), [0044](../04-JOURNEY/0044-brain-seeding.md) |
| Probing | Scheduled probing measured and closed: P0 FAIL both clauses (shift band ≤ 1.76× vs the 4× bar; benign probes to 2.80× above it), mechanism measured (relearning inside one episode; censoring survives held policy) — staleness detection closed passive+active | [0059](../04-JOURNEY/0059-scheduled-probing.md) |

*This file is load-bearing: changes to it are decisions and belong in
the journey (`../04-JOURNEY/`) as episodes like any other.*
