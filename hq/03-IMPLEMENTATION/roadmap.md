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

- *What remains:* nothing — **the run is over and read**
  ([episode 0068](../04-JOURNEY/0068-the-run-has-spoken.md)): `c1c`
  closed 2026-08-08 at 16.61 days of brain-steps; no emergence (zero
  offers ever), one mined log in a week-1 material era that died,
  reversal watches unfired, R4 fallback unfired.
- *Exit:* the multi-week run happened and its R1–R5 read is recorded;
  "**published telemetry**" is the remaining half — the S3 objects
  live on beno4 only. Post-run queue: snapshot prune, flush
  `--snapshot-dir` fix, TimeoutError root-cause, land the rescued
  tail, publish.
- *Named conditional:* the relative-survival bar from the soak stays a
  recorded deferral — the long run did not surface it.

## Next — showcases

### C2. Hardware body — parked (2026-07-26, owner's call)

Platform and research gates are both met and stay met: the ROS2 adapter
([episode 0026](../04-JOURNEY/0026-the-ros2-adapter.md)) gives hardware and
simulators one seam (continuous single-boot is the hardware mode; a homing
routine is an owner-supplied reset), and learned channel weighting
([episode 0030](../04-JOURNEY/0030-learned-channel-weighting.md)) cleared
the sensor-noise gate. **Parked as a priority call, not a gate**
([episode 0060](../04-JOURNEY/0060-c2-parked-phase-d-active.md)): Phase D
runs first while the C1 run soaks. Un-parks on the owner's call; the
episode names the readings that should prompt a revisit.

- *What remains (unchanged):* the **showcase itself** — a physical build
  (ROS2 or Pybricks-direct), a reproducible build guide a maker can
  follow, and a video of mid-run body growth.

### C3. Embedded steppable game server — parked

Viable *only* as a tick-steppable fork of a Minecraft-like single binary
(deterministic, faster-than-real-time) — a large systems project. Parked
until C1–C2 prove the showcase pattern and someone (possibly a contributor)
wants to own it; the steppable-tick idea is recorded here so it isn't lost.
*Gate:* everything above, plus a one-page spec before any code.

## Phase D — Make it a product (OSS hygiene)

Mostly parallel to Phase C; cheap individually, decisive together.
**Active since 2026-07-26**
([episode 0060](../04-JOURNEY/0060-c2-parked-phase-d-active.md)): the
owner moved Phase D ahead of C2 while the C1 run soaks. First item in
flight: **API stability & v1.0** — frozen seams first, so the docs
site, shareable brains, and the contribution surface all document a
surface that no longer moves.

- **API stability & v1.0 — LANDED**
  ([episode 0061](../04-JOURNEY/0061-the-surface-freezes.md), feature 035):
  110 elements across six families frozen as Doc 0008 + a machine-checked
  inventory with a surface guard in the gate; semver + deprecation policy
  published; `v1.0.0` tagged. *Exit met:* v1.0 tag; the seams documented
  as public API.
- **Docs site — LANDED**
  ([episode 0062](../04-JOURNEY/0062-the-docs-site.md), feature 036):
  Pages site built from `docs/` + `hq/02-DESIGN` at deploy time (zero
  duplication), worlds gallery with recorded FAILs stated, rot-guard
  test in the gate. *Exit:* linked from README; **deploy pending the
  owner's Pages enablement** (one click or one gh call, episode 0062).
- **Shareable brains — LANDED**
  ([episode 0064](../04-JOURNEY/0064-shareable-brains.md), feature 037):
  `pra-brain` export/inspect/import over the untouched blob, sha256 +
  version verification, deterministic artifact. *Exit met:* cross-person
  load verified by test AND end-to-end shell run, resume byte-identical.
- **Contribution surface — BUILT, exit pending-external**
  ([episode 0063](../04-JOURNEY/0063-the-contribution-surface.md),
  feature 038): CONTRIBUTING.md against the frozen seams, issue/PR
  templates, five labels + four API-verified good-first-issue drafts.
  *Exit* ("first external world contribution merged") awaits an external
  human — recorded, not claimed.
- **Show, then tell — deferred by constitution IV**
  ([episode 0065](../04-JOURNEY/0065-phase-d-in-a-day.md)): a C1 demo
  video before the c1c R1–R5 read lands would be a demo outrunning
  measured capability. **The read is in**
  ([episode 0068](../04-JOURNEY/0068-the-run-has-spoken.md)) — the
  deferral lifts on the owner's call; each showcase's video publishes
  with its honest telemetry (and the honest headline is "no emergence,
  one mined log").
- **The book**: the long-form narrative (`book/` — four parts drafted;
  contract in `book/STYLE.md`; decision recorded in
  [episode 0047](../04-JOURNEY/0047-the-book-decision.md)). The drafts
  are published on impire.io, draft-labeled
  ([episode 0066](../04-JOURNEY/0066-book-draft-on-website.md)). Part 5
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
| Goals-reopened | The ladder climbed in one night (motivation-stack topic): E2.0b homing holds 99.98% with zero departures, zero chains (presence ≠ election); G1 hold+itch PASSES both bars (24/24 dig, 6/24 chains — first bar-level elected chains); G1L learnable itch FAILS both and isolates signal fidelity as the bottleneck (0→11→24 dose-response); G3 event pathway PASSES all three bars (pred error 0.0612→0.0081, 24/24 dig, 13/24 chains — double the oracle) — src build licensed (owner's call), G5 unblocked | [0069](../04-JOURNEY/0069-goal-homing.md)–[0071](../04-JOURNEY/0071-wanting-follows-expecting.md) |
| Event-pathway | Feature 040 ships the G3 mechanism (v1.2.0, additive surface): event head as FrameStore-owned brain state (`event_head_eta`, snapshots, resize, byte-identical off) + `CompletionItchPolicy` with the learnable completion rule and honesty counters; G3 confirmatory reproduced on shipped components row-for-row (behavioral identity — 0071's reversal condition closed) | [0072](../04-JOURNEY/0072-the-event-pathway-ships.md) |
| Goals-G5 | Approval revisited: July's E3.0 refutation reversed at ceiling — the shipped head expects the verdict pulse perfectly (24/24 both bars, 1.000 at-tick / 0.000 off; frames context row = July's exact 18/24, 14/24); teaching the predictor erases cold start (V0 chains 24/24 vs G3's 13/24); the approval-anticipation term backfires (the post-approval hangover: −70% praise earned at κ₅ 0.25, avoidant log-hoarding at dose) — E3.1 reopens with a measured hazard list, owner conversation first | [0073](../04-JOURNEY/0073-the-hangover.md) |
| Hold-brainside | The last scaffold falls: head-predicted positions replace the clone Φ (H1a dwell 98.22%, movement models converge from ε in <1k steps; H1b 23/24 chains with no ground truth in the loop) — the composition is deployable, c1d registrable; design in Doc 0009 | [0074](../04-JOURNEY/0074-brain-side-hold.md) |
| Mirrored-map | Rung 2's blocker answered: aheadColumn mirrored in z + half-block-shifted since 027 (c1c sensed a mirrored world; lab world self-consistent, all gates stand); fix probed 20/20+20/20 stable, 10/10 drift, 10/10 at 5×, zero aborts; B2′ grid on fixed geometry = the remaining formality before c1e | [0078](../04-JOURNEY/0078-the-mirrored-map.md) |
| C1d-lab | The provisioned life endures: 75,359 chains at 25M steps, zero deaths, stopped by the pre-registered goal rule (as amended openly pre-fire); endurance flat per 5M fifth (15.2k/15.5k/15.3k/14.5k/14.8k, last fifth rising), dwell ≥99.97% every fifth, head EMA bounded over ~25M updates, energy min 0.855 exactly in the weaning window, no chainless segment in 500; run archive + final brain committed | [0079](../04-JOURNEY/0079-the-provisioned-life.md) |
| Recipe-choice | The menu measured (topic recipe-choice, all bars PASS): ten recipes, label off → rotation 24/24 by novelty decay (~5% switch, zero thrash, menu out-counts the specialist 170.5 vs 143.5); β 0.5 → selection monoculture 24/24 (label dwarfs the drive's value scale — command, not nudge; chains 18/24 = recipe-reach's twin number reproduced); Doc 0010 menu section; named next: value-weighted economy, β dose curve | [0080](../04-JOURNEY/0080-the-menu.md) |
| Praise-dose | The nudge regime measured (topic praise-dose, D1 PASS at ceiling): β 0.02 → praised modal 24/24, monoculture 0/24, chains 24/24 at share 0.49; the cliff to command at β ≈ 0.05–0.1, where the label crosses the drive's 0.06–0.15 value band; Doc 0010 dose dial [V] | [0081](../04-JOURNEY/0081-the-whisper-and-the-cliff.md) |
| Value-economy | Registered prediction confirmed (topic value-economy): survival pressure alone does not re-price the menu (nourishing share 0.382 lean vs 0.366 flat, 1.5× line unmet; 24/24 alive, 24/24 chains; E1 amended openly pre-arms with pilot numbers); the decoupling measured — praise commands hands, not mouth (junk-commanded arm alive 24/24 on side-chains); deficit→value coupling named [O] in Doc 0010 | [0082](../04-JOURNEY/0082-the-drive-cannot-smell-calories.md) |
| Deficit-coupling | The emergency appetite measured (topic deficit-coupling, split verdict recorded honestly): H1 aggregate repricing FAIL at 1.41× vs the frozen 1.5×; H2 survival PASS (+4 lives, 20/24 vs 16/24); H3 sated curiosity PASS (rotation 22/24, chains 24/24); the dial monotone (food share 0.43→0.74 with deficit; uncoupled crisis diet = baseline); constant taste eats more on average yet dies as often as no coupling — timing beats volume; coupling stays instrument-grade, promotion needs a timing-primary bar (Doc 0010) | [0083](../04-JOURNEY/0083-the-emergency-appetite.md) |
| Recipe-ships | Feature 041/v1.3.0: praise label on the shipped itch (completion-only reads, bit-exact off) + RecipeMemory/RecipePolicy; closure rerun row-identical 24/24 (second exact closure); Doc 0010 | [0077](../04-JOURNEY/0077-the-recipe-ships.md) |
| Recipe+G4b | The owner's designs measured true: recipe memory (taught order, no hand ladder) passes all three bars — transmission 24/24 vs the label's 0/24, chains at bar, recipe-led 20/24; the tapered childhood passes both — frontier dies at the predicted 4,250 exactly, composition 24/24 alive and working | [0076](../04-JOURNEY/0076-the-steps-not-just-the-ingredients.md) |
| Goals-E3.1+G4 | Praise-as-label: safe (chains 22/24, no hangover) and inert (0/24 transmission at every β — one-step reach blocks the walk to the applauded context; E2.1 upgrades to layer-5 prerequisite). The meter: frontier starves at median 2,001 (M1 PASS); composition 24/24 working but 10/24 alive — the runway races learning (provisioning is the named coupling); prediction ledger's first over-predictions | [0075](../04-JOURNEY/0075-the-label-and-the-meter.md) |
| Research arcs | Camping bill; scout, place-memory, emission-shift, context-memory, transfer-signal, staleness, change-point, election-stream (program paused, map complete); seeding measured | [0031](../04-JOURNEY/0031-the-camping-bill.md)–[0040](../04-JOURNEY/0040-reading-the-censor.md), [0044](../04-JOURNEY/0044-brain-seeding.md) |
| D-api | API stability & v1.0 (feature 035): public surface frozen as Doc 0008 + machine-checked inventory, surface guard in the gate, semver + deprecation policy, `v1.0.0` tag — zero behavior change | [0061](../04-JOURNEY/0061-the-surface-freezes.md) |
| Probing | Scheduled probing measured and closed: P0 FAIL both clauses (shift band ≤ 1.76× vs the 4× bar; benign probes to 2.80× above it), mechanism measured (relearning inside one episode; censoring survives held policy) — staleness detection closed passive+active | [0059](../04-JOURNEY/0059-scheduled-probing.md) |

*This file is load-bearing: changes to it are decisions and belong in
the journey (`../04-JOURNEY/`) as episodes like any other.*
