# C1E — the real life at 5×, pre-registered (2026-08-11, before launch)

> **CLOSED 2026-08-11** by the owner's manual stop (arm A) after arm B's
> death by rule; readings and the verdict in the closing section at the
> bottom; the archive in `c1e-run/`; the story is episode 0096.

The ladder's top rung ("yes, go with the ladder"; the road resumed:
"go for B2′ → c1e"): the measured stay/want/finish composition living
in the **real vanilla world** — full game rules, real physics, real
drops — at the calibrated multiplier **M\* = 5** (fast-real-bridge
B2′: primitives 20/20 at 5×, posture 5.19, the fixed geometry of
episode 0078). c1c asked whether crafting emerges unaided at 1× (no);
c1d asked whether the taught composition endures in the lab (yes,
75,359 chains); **c1e asks whether the taught composition lives in
reality at speed.**

## The life

- **World**: a fresh isolated vanilla 1.21.11 flat world (never
  c1c's, never the calibration litter), `/tick rate 100`, RCON. The
  harness stewards a **teaching grove** near spawn: oak columns
  rebuilt on the c1d regrowth rule (a dug column regrows after 2,000
  game ticks, by scheduled rcon setblock) — the world's renewal, one
  rule, recorded in every row.
- **Brain**: fresh seed 1, 33-dim (the C1 property body + the energy
  channel), `event_head_eta = 0.5` — taught **in the real world at
  1×** by the P0 protocol (45 wood-chain segments at the grove
  through the fixed bridge), then released.
- **Policy** (all shipped, zero ground truth): frames' drive +
  brain-side hold (Doc 0009, goal = the taught work position from
  the demonstrations) + `CompletionItchPolicy` (κ = 0.25, λ = 0.25).
- **The meter**: harness-side energy channel, G4's flat pay (+0.1
  per gain-tick), drain 0.0005 with the G4b taper (weaned by game
  tick 3,000-equivalent of its life) — the c1d childhood, in
  reality.
- **Pace**: `tick_ms = 50` (the B2′ posture law), ~20 brain-steps/s,
  ~5.2 game ticks per step.

## Execution

Segmented resume-chain exactly as c1d (snapshot to disk per segment,
crash-resumable; status rows to `c1e-status.jsonl`; the wrapper
guards double-launch). **Target 2,000,000 steps** (~28 wall-hours at
the measured pace) — ~10× c1c's *elected* life density at a tenth of
its wall time. Real-world honesty rows: bridge disconnects/rejoins,
server TPS spot-checks, grove-stewardship actions — all logged.

## Pre-registered readings (the c1d set, in reality)

- **R1 — endurance of election**: full chains per 200k-step decile.
- **R2 — hold drift**: dwell near the grove per decile.
- **R3 — head stability**: prediction-error EMA per segment.
- **R4 — the life**: survival, energy trajectory, the weaning window.
- **R5 — the miser watch**: roaming and work mix per decile.
- **R6 — reality's tax (new)**: dig-completion rate in the wild vs
  B2′'s 20/20; bridge/server incidents; any world event the lab
  never had (mobs, weather, drops lost).

## Stop rules (frozen)

1. **Death** — energy zero: stop, full report.
2. **Goal** — ≥ 2,000 full chains **and** ≥ 1,000,000 steps:
   graduation; stop, full report.
3. **Futility** — zero chains across 500,000 consecutive steps after
   childhood: stop, full report.
4. **Manual** — `c1e-STOP` file or the owner's word; graceful at the
   next segment boundary, resumable.
5. Otherwise: run to 2,000,000.

## Dashboard & watch

The c1d pattern: per-segment rows feed the tablet dashboard
(private artifact, updated at decile boundaries and on request); a
monitor watches MILESTONE / STOPPED / death / error lines and pushes
on anything actionable.

## Attempt 1 — death by rule 1, and amendment 1 (2026-08-11)

**The run**: teaching passed 45/45 (every stick craft asserted). The
life died at **life-tick 4250** — the exact zero-income death point
(the taper's cumulative drain reaches 1.0 at precisely 4250):
**not one pocket gain in the entire childhood** [measured]. Segment
row: 10,011 steps, 2 chains (both post-death), 38 logs / 48 sticks
at segment end, dwell 0.24, 14.8 steps/s, 1,163 instant dig aborts
in the bridge log.

**The post-mortem probe** (three arms against the still-live world,
raw rows in `c1e-attempt1/c1e-probe.json`) [measured]:

- Pinned pure dig hold: dug in **60 steps (3.11 s wall)**, 0 aborts.
- Wild posture (offset stand + yaw error): dug in 61 steps, 0
  aborts — **no posture penalty, no target-flap**.
- The tape's own shape (14 digs + 8 idles, repeated): dug only after
  3 cycles ≈ 60 dig-steps total.

**Diagnosis**: a dig's duration is set by the *client* at wall-clock
1× — ~3.0 s regardless of the world's `/tick rate`. The tape taught
a **14-step dig run**: 3.5 s at teaching pace (250 ms — enough), but
**0.7 s at life pace (50 ms) — under a quarter of what a dig needs**.
The taught skill was unexpressable at the pace it was released into;
the childhood earned nothing and the meter ran out. The 38 post-death
logs are the completion itch *extending* runs to ~60 held steps once
it locked onto the sensed mining-progress channel — the composition
can do the work; the tape's temporal shape couldn't. This is R6 —
reality's tax — delivered in segment 1.

**Amendment 1 — one temporal fabric** (before attempt 2, fresh world
and fresh brain): teaching moves into the life's own fabric (5×
world, 50 ms steps, same as release); the dig run becomes **70
consecutive held digs** (measured 60 + margin; the bridge releases a
hold on any non-dig command, idles included); the craft tail keeps
attempt 1's wall spacing (one op per 250 ms) as four idles after
each op. Meter, wean, stop rules, target, and readings all
unchanged.

**Second finding, same post-mortem — the drop flies away at 5×**
[measured]: the 106-step tape still failed teaching (0 stick crafts,
3/3 attempts). A watched dig showed the break completing but the
drop **far-scattering past pickup range** — resting up to 2.5 blocks
away — then despawning (60 s wall at 5×). Grid: at `/tick rate 20`
pickup while standing is **4/4**; at `/tick rate 100` it is **2/4**,
with lost drops resting at z 10.2–10.6, x 8.0–9.9. At 1× the drop
pops to the breaker's feet; at 5× it outruns the pickup box about
half the time — more of reality's tax.

**Amendment 1b — the tape teaches collection**: after the dig run,
the lesson walks into the drop zone and back (9 forward + 9 back,
~1.9 blocks — the probes' collect-walk); tape 22 → **124 steps**
(70 digs, 18 collect-walk, 35 spaced craft ops, 1 idle), piloted
green end-to-end (log by step 69, planks by 102, 4 sticks by 122).
Because a drop can still rest outside the collect lane (~1 in 3 of
the far-scatters), a lesson that fails its stick-craft assertion is
**repeated, up to 3 attempts** — the parent demonstrating again; a
failed attempt leaves no trace in the taught state. Teaching fails
hard if any lesson needs more than 3.

Runner mechanics, same change-set: the engine's episode length
follows the tape (the inherited config carried the old tape's 22 and
silently truncated every 124-step lesson to its first 22 digs —
caught before any brain was taught); life segments are 81 cycles
(10,044 steps), keeping the registered ~10k-step segment size.

## Attempt 2 — death by rule 1 again, at the same corpse line (2026-08-11)

Teaching under amendments 1/1b passed **45/45 with zero repeated
lessons**. The life died at **life-tick 4260** — attempt 1 died at
4250, and 4250 is the exact zero-income corpse line — so this
childhood, too, earned at most a sliver [measured]. Segment row:
10,045 steps, 2 chains (post-death, last at step 7703), **46 logs
and 21 stick-crafts gained** — nearly all in the post-death half,
an income rate of roughly one gain per 86 steps there, more than
twice break-even (one per 200).

**Reading**: the taught skill is now expressable and the economy is
sustainable — but the behavior takes ~5,000 steps to lock in, and
the lab-calibrated childhood (taper 1500→3000, zero-income corpse at
4250) ends ~1,500–2,000 steps too soon for reality. The lab's
release-to-expression delay was ~zero; reality's is not. Both deaths
are the same measurement.

**Instrument fault found in the readings** [measured]: the dwell
statistic computes distance from the LAB world's wood coordinates
(−1, 0), not the grove (8.5, 8.5) — R2 dwell numbers from attempts
1 and 2 (0.24, 0.0) are meaningless and are struck. Re-key before
any attempt 3, and log the first-income step per segment.

**The childhood dial in reality is the owner's call** (precedent:
G4/G4b — "re-dose is a design decision, not autonomous"). Named
options, none launched: (a) re-dose the wean from the measured
expression delay (e.g., taper completing ~9,000 — the lab's 3,000
scaled by the ~3× wall-clock factor reality has shown everywhere —
registered as amendment 2, fresh world and brain); (b) a diagnostic
life with no meter death first, to measure expression delay
precisely; (c) accept the double death as c1e's verdict and close.

## Amendment 2 — the owner's design: lives versus provisioning (2026-08-11)

The owner's call, verbatim intent: *"when we die, we need to respawn
but keep the brain intact — that's the equivalent of playing games,
and we will learn over time. Raising childhood optimizes for a
one-shot, which might be valuable as well. Try out both and see what
works best."* Two arms, registered before launch, fresh isolated
worlds, fresh seed-1 brains, identical teaching (amendments 1/1b).

**Arm A — respawn (the game frame)**: on energy zero the death is
*recorded, not terminal*: the pocket is cleared and drops killed
(death's price — wealth lost, knowledge kept), the body respawns at
the stand (the bed), energy resets to 1.0, and a fresh per-life
childhood begins (the lab taper, grace 1,500 / full drain at 3,000;
zero-income corpse at life-tick 4,250 — every life gets the same
allowance). The brain is never touched. Death does not stop the run.

**Arm B — one-shot (the provisioned childhood)**: the taper is the
lab dose scaled by reality's measured ~3× wall-clock factor — grace
4,500, full drain at 9,000; zero-income corpse ≈ life-tick 8,743,
comfortably past the measured ~5,000-step expression delay. Death
stops the run, as originally registered.

**Common stop rules** (both arms): goal (≥ 2,000 chains and ≥ 1M
steps), futility (500,000 chainless steps past childhood — 3,000 /
9,000 per arm), manual stop file, target 2,000,000 steps.

**Frozen decision rule**: Arm A succeeds if it reaches goal or
target with **zero deaths in its final 1,000,000 steps**. Arm B
succeeds if it reaches goal or target without dying. If both
succeed, the better design is the one with more full chains at
stop (tie-break: fewer steps to 1,000 chains). If one succeeds, it
is the design. If neither, both post-mortems return to design.

**New reading R7 — lives** (arm A's signature): deaths, life
lengths, and **first-income step per life** — the game frame
predicts first-income falls across lives (learning survives death).
Instrument fixes, same change-set: the dwell reading re-keyed to
the grove (8.5, 8.5, Chebyshev ≤ 2 — R2's lab-coordinate fault
struck above), first-income logged per life in every row, per-arm
status/snapshot/log files (`c1e-a-*`, `c1e-b-*`).

## Two-arm run 1 — the same corpse line four times, and the diagnosis (2026-08-11)

First segments, both arms [measured]:

- **Arm A**: deaths 2, life lengths [4250, 4250] — both at the
  per-life zero-income corpse line; first-income per life
  **[13, −1, −1]**: life 1 earned at birth (crafting the pocket
  teaching left behind), lives 2 and 3 (respawned poor) earned
  nothing at all. Grove dwell (re-keyed, now honest): **3%**.
- **Arm B**: died at **exactly 8,743** — the tripled childhood's own
  zero-income corpse line. First income at tick 7 (the same birth
  burst), 48 log-gains and 12 stick-crafts across the segment —
  concentrated at birth and *after* death (last chain step 9,721);
  nothing in the entire drain window. Grove dwell 0%. Stopped by
  rule 1; one-shot run 1 is over.

**Diagnosis** [mechanism-argument, with the arc's own precedent]:
every death in c1e so far sits at an exact zero-income line, and
work reliably resumes when the energy channel stops moving (post-
death in attempt 2 and arm B; never within arm A's short lives).
Teaching runs every lesson at full energy — the brain has **never
witnessed the meter move**. Once the drain starts, the energy
channel walks out of the taught distribution and expression
collapses; when the channel freezes again, the world reads familiar
and the skill returns. This is episode 0083's hungry-teaching
lesson and episode 0090's moving-senses rule — a sense that changes
outside the brain's control must be in the witnessed variety — and
this registration failed to carry hungry teaching over. Both arms
share the defect, so run 1 was not the fair comparison the design
calls for. Reversal condition: if hungry-taught arms still die at
their exact corpse lines, this diagnosis is wrong and the childhood
question returns to the owner.

**Amendment 3 — hungry teaching, both arms** (the 0083 protocol,
restored): lesson starting energy cycles **1.0 / 0.7 / 0.4** across
the 45 lessons (15 each, interleaved); gains during a lesson raise
the meter by its own rule, so eating-raises-energy is witnessed
too. Everything else — arms, tapers, stop rules, decision rule,
readings — unchanged. Fresh worlds, fresh brains, run 2.

## Run 2 — the reversal fires, and the real fault is measured (2026-08-11)

Run 2 under hungry teaching was **statistically identical to run 1**
[measured]: arm A lives [4250, 4250], first-income [11, −1, −1],
grove dwell 1%; arm B dead at exactly 8,743, dwell 0%. The
registered reversal condition fired — the energy-channel diagnosis
is refuted (amendment 3 stays: it is protocol-correct per 0083 and
cost nothing, but it was not the disease).

**The fault, measured on arm B's idle world**: the bridge's pose
channels are *spawn-anchor-relative* — `(x − anchor.x)/64` with the
anchor captured at the bot's first spawn — while the registered
goal file was hand-computed as *absolute* `8.5/64`. Solving anchor
from a live tick (true position vs pose channels): anchor ≈
(−8.5, −7.5), so the goal the hold was given lands at world
**(0, 1) — eleven blocks from the grove**. The bot was found parked
at (1.3, 0.1): **the brain-side hold works; it was aimed wrong in
every real run.** Every c1e death — attempts 1–2, runs 1–2, both
arms — is one mechanism: the composition held its body faithfully
eleven blocks from its only food. The childhood question dissolves;
this is the mirrored-map family (episode 0078), a coordinate-frame
fault at the seam.

Open counter puzzle, flagged honestly: run-1/2 rows show 44–48
oak_log gain events with dwell ≤3%, which cannot be grove
dig-collect cycles; the inventory-event counters likely include
held-item cycling or consumption artifacts [mechanism-argument] —
resolve in run-3 readings before trusting logs/sticks columns.

**Amendment 4 — the goal is the taught stand's own senses**: the
goal file is no longer hand-computed; at release the runner reads
the pose channels at the stand (the taught work position, as the
brain senses it) and writes the per-arm goal from them. A resumed
run keeps its existing goal file. Everything else unchanged. Fresh
worlds, fresh brains, run 3.

## Run 3 — the hold holds, and three more defects surface (2026-08-11)

Amendment 4 verified immediately [measured]: grove dwell went from
1–3% to **98–100%** in both arms — the hold now holds at the true
grove. And the first genuine lives-curve appeared: arm A first-income
per life **[9, −1, 207]** — life 1 fed from its inherited pocket,
life 2 (born poor) starved without earning, life 3 (born poor) fed
itself within 207 ticks. Learning survives death — the game frame's
signature, visible once the hold was aimed right.

Then arm B died at exactly 8,743 *with* dwell 0.99 and first income
at tick 70 — which exposed the next layer:

- **The wealth sense saturates** [measured]: the bridge's pocket-
  total channel is `min(n, 64)/64`. Arm B was born carrying the
  teaching surplus; its true pocket read **155 items, channel
  pinned at 1.0** — 51 real digs invisible to the meter, death at
  the exact zero-income line. The rich starve because wealth blinds
  the sense that pays them. (This also resolves the run-1/2 counter
  puzzle in kind: derived counters and the meter disagreed because
  the sense and the world diverge past 64.)
- **The runner wiped the world each segment** [measured, mine]: the
  per-segment resume nulled `world_state` — a boundary pattern
  correct once (at release) hoisted wrongly into the loop — so
  every segment granted a fresh childhood and erased the lives
  ledger (segment 2's arithmetic: 4250+4250+1544 = exactly the
  segment's steps). c1d's runner nulls only at the boundary.
- **Snapshot cadence misaligned** [measured, mine]: a flat 81-cycle
  cadence does not divide the post-teach offset (45 cycles), so
  segment 1's only snapshot landed mid-segment and the resume
  dropped 45 brain-cycles.
- **The pedestal** [measured, behavior]: the bot placed planks in
  its own stand cell and neighbors; each respawn then landed it on
  top, one block up, where its own drops fall vertically out of
  pickup range. Real 3-D behavior the lab never had — recorded as
  R6 material.

**Amendment 5 — the meter pays on the world's record**: the
registered meter ("pocket-total gains") is paid from the world's
own inventory count (unbounded), not the saturating sensed proxy —
the world knows what you acquired; the sense may be myopic. The
saturation itself stands as an R6/moving-senses finding: the
brain's *wealth sense* still saturates at 64, and what that does to
its behavior is part of what the run measures.

**Runner repairs, same change-set**: world state rides the resume
chain (the null stays only at the release boundary); snapshots land
exactly on segment ends (`snapshot_every_n_cycles = n_cycles`); the
world keeps the bed clear at each respawn (the steward's charter
extended to the bed cell). Fresh worlds, fresh brains, run 4.

## The close — readings against the registered set (2026-08-11)

Run 4 (all five amendments live) is the measured run; earlier attempts
are instrument history recorded above.

- **R1 endurance**: arm B 9 chains in 20k steps (one life); arm A 10
  chains, all inside the first ~97k of 140,617 steps — election
  COLLAPSED after ~10 segments (segments 11–14: 0 chains, 2–4 logs).
- **R2 hold drift** (re-keyed to the grove): **0.98–1.00 in every
  segment of both arms** — the brain-side hold, once aimed by the
  body's own senses, holds in reality exactly as it did in the lab.
  The strongest positive result of the run.
- **R3 head stability**: pred-error EMA 0.0018–0.0165 across all
  segments — the shipped head models reality comfortably.
- **R4 the life**: arm B dead at life-tick 14,398 (5,655 past its
  zero-income line — an economic death: it crafted its stockpile
  instead of digging, then starved; the pantry death). Arm A: 28
  deaths in 140k steps, life lengths 4,250–5,105 (median ~4,635 —
  each life earns 1–4 pays past the corpse line, then starves).
- **R5 miser watch**: inverted — unique positions 4–20 per segment;
  no roaming at all. The registered worry (wandering) was never the
  disease; fixation was.
- **R6 reality's tax** (the run's richest product, all measured):
  digs are client-side wall-clock (~3.0 s at any /tick rate); drops
  far-scatter past pickup at 5× (~half lost, despawning in 60 s
  wall); pose channels are spawn-anchor-relative; the wealth sense
  saturates at 64 items; the bot built a pedestal in its own bed
  cell; item-drop physics, craft round-trips, and connection
  lifecycle all differ from the lab. Process tax: two attempts, four
  runs, five amendments to field one honest experiment.
- **R7 lives** (the game frame's registered signature): first-income
  per life NEVER trended down — [1611, 333, 140, 999, 9, 1217, 1973,
  1695] over the last eight lives. Brain-intact respawn did not
  accumulate competence: each death cleared the crafting stock, and
  ~140k steps of online learning eroded the taught skill (the churn,
  measured in reality). Arm A was heading to futility when stopped.

**Decision rule**: neither arm succeeded → both post-mortems return
to design, as frozen. The design conversation returned the deeper
verdict (the owner's question, the same evening): the scenario was
the tangent — a synthetic metabolism, hand-amended five times, in a
world whose native survival economy (hunger, food, health, death,
respawn) was deliberately switched off; a hold that made exploration
the enemy in a world with nothing to explore. The composition's parts
all worked (hold, head, itch, teaching); the life we asked them to
live was the lab wearing reality's skin. Successor direction (owner's
call, not registered here): the native-survival reframe — the world's
own meter, food as pay, exploration as foraging.
