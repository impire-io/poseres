# JOURNEY — the-arena-revival (opened 2026-09-27)

## 2026-09-27 — topic opened; the kit restored from history; nothing run

Opened at the owner's instruction to start the revival, by an agent
session, after features 045–047 shipped (episodes 0121–0123) and
main was pushed with tags v2.3.0–v2.5.0. No pilot, no teach, no
life has run; the bars in README.md await the owner's review.

**Restored, verbatim, from git history (design 0021's revival kit):**

- From `a4b4386` (the-long-carry, the consolidated n = 8):
  `arena.md` (the arena's registration, theorems, opacity audit,
  probe span, curriculum, dials) and `rig/` — `README.md`,
  `docker-compose.yml` (lc-minecraft:25603), `arena_provision.py`,
  `mechanism_check.py`, `lc_runner.py`, `decode_probe.py`,
  `probe_walk.py`. The topic's READINGS (`flat-lives*.jsonl`,
  `sib-lives*.jsonl`, `mechanism-report.json`, `decode-report*.json`)
  stay at `a4b4386` as 0120's evidence; the revival re-measures
  (bar R0) rather than inheriting.
- From `4171779` (the-opaque-world, the n = 16 verdict): the 0119
  composed scaffolding — `rig/compose.py`, `rig/opaque_runner.py`,
  `rig/snap_test.py` — for M0–M2.

**Pre-pilot tasks found while restoring (rig work, no kernel
change; each recorded here when done):**

1. `rig/lc_runner.py`: `LoggingRecipePolicy` carries the
   layer-fatigue PROTOTYPE (K = 200 / W = 800, rig-level). Replace
   with the shipped dials — `RecipePolicy(futility_k=200,
   futility_w=800, stage_indices=…, stage_tolerance=1/128)` — and
   `RecipeMemory(…, process=True)`; keep the per-life logging. The
   sibling arm declares `stage_indices=(obs_dim − 1,)` (the `laps`
   channel is appended last by `set_arm_body`); the flat arm
   declares `()`.
2. `rig/compose.py` imports `seq` (the echo-teacher world module
   from the sequence-encoding / compositional-frames rigs — history
   at `71db89b`, `619b80c`). Restore `seq.py` beside it or trim the
   import to what the live composed tier needs — decided when M0 is
   prepared, recorded here.
3. `rig/opaque_runner.py` hard-codes the old checkout path
   (`/Users/calmera/Impire/pra/...`) for the shared machinery and
   targets the probe world; re-point to `HERE.parents[3] /
   "examples/minecraft/survival/arms"` (the `lc_runner.py` idiom)
   and to `lc-minecraft` / bridge 25591 before M0.
4. M0(d): expose the composed tier's carried context as declared
   stage channel(s) at the rig level so `stage_indices` can read
   it — the pathway design 0021 names for composed tiers; the
   mechanism is rig work to be designed and recorded before M0
   reads.
5. Bring-up order stays `rig/README.md`'s: compose up → provision →
   bridge (`SURVIVAL=1 MC_PORT=25603 BRIDGE_PORT=25591`, plus
   `LAPS="x,y,z"` for the sibling's column) → `mechanism_check.py`
   (R0(a)) → walker rows + decode probe (R0(b)) → sibling teach and
   lives (R1) → M0 → arms.

Machine state at opening: `docker`, `node`, and the rebuilt
`.venv` (Python 3.13, full gate green: 748 passed, none skipped)
are present; the arena world data is not (first `docker compose
up` regenerates and re-provisions it — the provision script is
idempotent).

## 2026-09-27 — the owner's call: run it. Amendment 1 pre-run; the rig adapted; nothing measured yet

**The owner's call [judgment, the owner's]:** "Go with the arena. Let's
run it." The bars stand as registered above; the arena is the single
live research thread. Recorded before any server command.

**Amendment 1 (pre-run, the curriculum's counter preset) [mechanism-
argument]:** V1-the-lap cycles its counter preset 0 → 1 → 2 across its
fifteen lessons (five at each stage) instead of 0120's fixed 0. Reason:
stage-conditional selection (047) makes a recipe eligible only where
its demonstrated stage trajectory stood — a lap demonstrated at
laps = 0 is out of context at laps = 1 and 2, so with the fixed preset
rung 3 would have no partition to read on the loop and the sibling
would read as if the rung were absent. arena.md registered V1 as
"counter set below N"; 0120 pinned it at 0 because nothing then read
the stage. The lesson gate becomes laps == preset + 1. V0 and V2 are
unchanged (V2 at 2, the turn-in). Same curriculum for both arms.

**The rig adapted (`rig/lc_runner.py`), no kernel change:**

- The layer-fatigue prototype (`LoggingRecipePolicy` with K/W, dead
  layer, `dead_steps`) is deleted. The policy is the shipped
  `RecipePolicy` with the README's dials — `futility_k=200`,
  `futility_w=800`, `stage_indices=(obs_dim − 1,)` for the sibling (the
  laps channel, appended last) and `()` for flat, `stage_tolerance =
  1/128` — plus telemetry only: the probe's observation log and
  `wander_steps` (steps with no recipe selected).
- `RecipeMemory(..., process=True)` for every arm: V0 and V2 store as
  acquisitions (a dig collects), V1 as process recipes (no gain, food
  label positive; terminal = the latest max-food step — the shipped
  046 rule, not re-designed here; the `recipes` phase prints what each
  teach actually stored so the R1 reading carries it).
- Life rows now report `recipes`, `process_recipes`, `stage_indices`,
  `fatigue_events`, `revive_events`, `stage_filtered_events`,
  `wander_steps` in place of the prototype's `disengagements` /
  `dead_steps`.
- `rig/bridge_up.sh` starts the bridge with or without the laps sense
  (`LAPS=25,-63,10`, the indicator column's first cell). R0's probe
  rows are recorded with the sense OFF — the flat body's observation,
  as 0120's were — else the probe would decode the counter trivially.

**Bring-up order (from `rig/README.md`):** compose up → provision →
bridge (laps off) → `mechanism_check.py` (R0a) → `probe_walk.py 6` +
`decode_probe.py walk` (R0b) → bridge (laps on) → `teach flat`,
`teach sib` → `recipes` readout → `rounds 1 8` (R1: sib the bar, flat
the reference, interleaved against drift as 0120's rounds were).

## 2026-09-27 — Bar R0 PASS: the revived arena binds, both instruments reproduce 0120

Server up from a fresh superflat (`docker compose up`, world regenerated,
`arena_provision.py` idempotent; gate obsidian, laps 0, `advance_time` /
`advance_weather` false, time 6000). Bridge with the laps sense OFF.

**R0(a) — mechanism check PASS 15/15 [measured, `rig/mechanism-report.json`]:**
counter 1/2/3 once per crossing, gate closed through laps 1–2 and open at
3, larder entry resets and recloses, indicator column rises and falls,
dig → collect → eat lands, the exit drop returns to the loop and is
one-way, counting resumes. Gait: lap steps 136 / 147 / 147, **147 steps
per lap, 4.9 per block** (0120: 146, 4.87). Life length stays 6,000.

**R0(b) — decode probe PASS [measured, `rig/decode-report.json`]:** six
walker chains, 3,924 steps, 2,671 on the decision span over 7 chains
(labels 1–4: 438 / 890 / 889 / 454). The aliased pairs as binary linear
readouts: **2v3 true 0.508 vs control 0.4982 ± 0.0354; 3v4 true 0.519 vs
0.4988 ± 0.0118** — both within the 2-sd band (0120: 0.5039 vs 0.5036 ±
0.063; 0.518 vs 0.5016 ± 0.0113). Multiclass context 0.36 vs 0.2442 ±
0.0566, the half-ring topology of label 1 as before. Chain ≈ 640 steps
(646 / 628 / 634 / 612 / 627 between walker chains), 6× the probe world.

The arena is the arena. R1 begins: bridge restarted with the laps sense
(`LAPS=25,-63,10`), `teach flat`, `teach sib`, the `recipes` readout,
then `rounds 1 8` — via `rig/r1.sh`, detached, log in `r1.log`.

## 2026-09-27 — the flat teach fails at lesson 30; the cause measured; amendment 2 (the parent's hands)

**What happened [measured, `rig/r1.log`]:** flat teach lessons 1–23 landed
first try; V2-turn-in at segs 24 and 27 needed a second attempt
(`done=True eats=0 laps=0`); seg 30 failed all three attempts the same
way — the body reached the larder (the counter reset to 0) and no dig
landed. The bridge log carried one line per failed attempt: `dig ended
early: Digging aborted after 2,127–2,229 ms` — a dig that started and
was released unfinished by the tail's first FWD after 40 dig ticks.

**The diagnosis, live, with the mechanism walker
[measured, `rig/dig_probe*.py`]:**

- The lesson melon breaks in **30 ticks (1.55 s)** from the ground, in
  every body state — as-is (food 0, health 1), healed (20/20), starved
  (food 6) — and in **29–30 ticks** when the dig begins on the arrival
  tick after walking the step-ups into the larder exactly as V2's last
  waypoints do. Body state and arrival momentum are not the cause.
- A dig that begins **mid-jump takes 145 ticks (7.51 s)** — mineflayer's
  not-on-ground rule, 5× the break time, computed once at the dig's
  start. Four idle ticks after the jump restore **29 ticks (1.50 s)**.
  Two trials each, identical to the tick.
- The teacher auto-jumps whenever `solid_ahead` reads solid, and on the
  last half-block before the melon the solid block ahead IS the melon.
  When the approach's gait phase lands a tick in that window, the dig
  begins airborne and 40 dig ticks (~2.2 s wall) cannot finish a 7.5 s
  dig. Intermittent by phase (0/7 early V2 lessons, then 1/2, 1/2, 3/3)
  — the walker never hit it because it idles a tick before digging.

**Amendment 2 (pre-run for the sibling; rig-level, the parent's hands,
identical across arms):** `V0_TAIL` begins with four IDLE ticks before
the 40 DIG ticks — the walker's idiom. The FLAT TEACH IS RESTARTED FROM
LESSON 1 so both arms carry byte-identical tapes (the registered spine:
same tapes, same seeds); the 29 lessons taught with the old tail are
discarded, their `r1.log` kept. The world is untouched. Server health
during the failure: no "Can't keep up" in the server log, container at
~14% CPU, tick rate 100 as set.

## 2026-09-27 — the flat teach lands 45/45; the recipes readout catches a curriculum artifact; amendment 3

**Flat teach (attempt 2, settled tail) [measured, `rig/r1-attempt2.log`]:**
45/45, zero retries — amendment 2 holds.

**The `recipes` readout [measured, `rig/recipes-flat-attempt2.json` and
the per-demo table]:** 39 recipes from 45 demonstrations; 15 V0 and 15
V2 stored as acquisitions, **9 of 15 taught laps stored as process
recipes**. The six unstored laps are exactly the demonstrations whose
food channel read 0.000 throughout — every preset-0 lap (5/5, all under
the full hunger dose) and one preset-1 lap (k = 23, medium dose on an
already-emptied body). The stored laps read food 0.05–0.80.

Two things on the record:

1. **A finding about the shipped door [measured]:** the process door
   (046) requires a strictly positive label, and here the label is the
   food channel; a starving body's demonstration carries no applause
   and stores nothing — 6/15 taught laps discarded by the rule, not by
   the world. Design 0021 said the applauded ending "closes 0120's
   fifteen unstorable laps"; on this rig it closes nine of them. Not
   redesigned here (the kernel is untouched by research); carried to
   the verdict.
2. **A curriculum artifact of amendment 1 [mechanism-argument on the
   numbers above]:** the dose cycle is indexed by the same lesson
   ordinal as the V1 preset cycle, both with period 3, so preset 0 was
   always taught under the full dose — the sibling would have entered
   every life (born at laps = 0) with NO lap recipe in stage, and R1
   would have measured the curriculum, not the ladder.

**Amendment 3 (pre-run, both arms):** V1's preset follows a Latin-square
schedule over its ordinal j, `(j + j // 3) % 3`, so each preset meets
every dose: preset 0 at doses {0, 2, 1, 0, 2}, preset 1 at {1, 0, 2, 1,
0}, preset 2 at {2, 1, 0, 2, 1}. Expect ≥ 3 stored laps per stage
(light and medium doses), fewer where a medium dose meets an emptied
body. Both teaches restart from lesson 1 (identical tapes); the
sibling's partial teach (lessons 1–~8) is discarded. World untouched.

## 2026-09-27 — flat teach (attempt 3) 45/45; the readout under amendment 3

**[measured, `rig/recipes-flat.json` + per-demo table]:** 40 recipes from
45 demonstrations — 15 V0 and 15 V2 acquisitions, **10 of 15 laps as
process recipes: preset 0 → 3/5, preset 1 → 3/5, preset 2 → 4/5**. The
five unstored laps are exactly the five full-dose lessons (food 0.000
throughout); every light- and medium-dose lap stored (food max 0.05–0.80).
Every stage has lap recipes in context. The sibling teach runs on the
same tapes; its readout adds the stage values each recipe's steps stood
at.

## 2026-09-27 — sibling teach 45/45; the eligibility partition as stored; rounds begin 23:19

**[measured, `rig/recipes-sib.json`]:** 40 recipes, 10 process — the same
counts as flat (identical tapes, identical doses). The stage values each
recipe's steps stood at (the laps channel, k/3), i.e. where rung 3 will
hold it eligible:

- 15 × V0 larder-eat (acquisition): {0.0} — the larder, after reset.
- 15 × V2 turn-in (acquisition): {0.0, 0.667, 1.0} — from the stand at
  laps 2, the crossing to 3 (gate open), the larder's reset to 0.
- 10 × V1 the-lap (process): 3 at {0.0, 0.333} (preset 0), 3 at {0.333,
  0.667} (preset 1), 4 at {0.667, 1.0} (preset 2); lengths 139–141 —
  the terminal is the lap's end (food constant across a lap, so the
  latest-max-food rule lands on the last step) and the stored path is
  the whole lap.

So at birth (laps 0) the sibling has three lap recipes, fifteen larder
recipes and fifteen turn-ins in stage; at 1/3 and 2/3 only laps; at 1.0
laps (preset 2's tail) and the turn-ins. What the policy does with that
partition — and what place-keyed futility does at the closed gate — is
what the eight rounds read. `rounds 1 8` started 23:19; flat life 1
first.

## 2026-09-27 — round 1 read: the sibling walks one lap and parks at the loop's closure; the pointer is the mechanism

**Flat life 1 [measured, `rig/flat-lives.jsonl`]:** crossings 1, chains 0,
branch visits 1, eats 0; 1,650 of 6,000 steps in the gate cell (15, 8) —
the 0120 press, now with futility: 2 poisons created, 2 expired
(K = 200 / W = 800 as dialed); out-of-context 3,524. The memoryless
reference behaves as 0120's flat rows did, plus the peek loop.

**Sibling life 1 [measured, `rig/sib-lives.jsonl`, `mc/sib-life1.npz`]:**
crossings 1, chains 0, branch visits 0, eats 0. The laps channel went
0 → 1/3 at step 1,755 — one clean taught lap from birth, the stage
filter live throughout (`stage_filtered_events` 6,000; out-of-context
611 vs flat's 3,524). Then **4,128 of the remaining 4,245 steps in cell
(0, 0)** — the loop's northwest corner, the lap line just crossed — with
`fatigue_events` 0 and `advance_events` 430.

**The mechanism, reconstructed from the stored demonstrations at the
parked observation (laps 1/3, body at (0.35, 0.65)) [measured, offline,
the shipped arithmetic]:** six recipes are stage-eligible — the three
preset-1 laps (stages {1/3, 2/3}: the lap the body should now walk) and
the three preset-0 laps (stages {0, 1/3}: the lap just completed). The
shipped pointer (nearest step by position, plus one) resolves EVERY one
of them to its last steps: nearest 136–138 of ~140, pointed places
(0, 0) and (0, 1) — the body's own cell and its neighbour, at 0.02–0.09
blocks. The loop's start and end coincide at this corner, so a
position-only pointer at the closure sees the END of the next lap, not
its beginning; the hold pulls to where the body already stands.

Why futility never fired [mechanism-argument on code + numbers]: the
pointer index `_prev_ptr` is one scalar shared across recipes, so a
selection flip between a 139- and a 140-step lap (ptr 137 → 138) counts
as an advance and resets the place-keyed stall — 430 "advances" while
parked, 0 stalls reaching K. Place-keyed futility as shipped is defeated
by argmax flicker among near-identical recipes of unequal length.

What a **stage-aware pointer** does at the same observation [measured,
offline]: restricting the nearest-step search to the recipe's
stage-matched steps sends the three preset-1 laps to step 1 → place
(3, 0) — forward, the next lap — while the preset-0 laps still point at
their ends (0, 0)/(0, 1). Exactly the successor 0123 named as "awaiting
an arena reading": pointer-local matching / stage-aware pointing. The
reading is in after one life; the eight registered rounds run on as
registered (no amendment mid-comparison). A rig-level prototype of the
stage-aware pointer with per-recipe pointer tracking is built beside
the runner (`rig/sap_policy.py`) and verified on the parked state
offline; it does NOT run in these rounds — whether it runs is the next
registration's question, per this topic's direction clause.

## 2026-09-27/28 — rounds 2–3: the flat arm passes the gate for the first time in the arena's record; no eat

**Rows [measured, `rig/*-lives.jsonl`]:** flat 2 — crossings 1, chains 0,
peeks 0, 1 poison; sib 2 — crossings 0, chains 0, 3 wasted peeks, 1
poison/1 revive, out-of-context 3,830 (pulled to the closed gate by the
larder recipes' post-reset steps, which stand at stage 0 too). **Flat 3
— crossings 3, gate passed, larder entered, eats 0.**

**Flat life 3's trace [measured, `mc/flat-life3.npz`]:** crossings at
steps 1,548 / 3,339 / 4,561 (the brain's own laps, ~1,200–1,800 steps
each against the walker's 147); in the gate cell at step 4,986 with the
gate open; ONE larder entry at step 5,039 (the row's `chains: 3` is the
box-boundary toggling at z = 12.0 — two re-entries within 20 steps; the
runner's reconstruction over-counts, and the verdict will count gate
passages from the traces instead). Inside: 961 steps left, spent at
(15, 12) / (14, 12) / (14, 13) — the entry cells — with the mining
channel above zero on 158 steps and peaking at 0.625: digging that never
finished a block; food stayed 4; no collect, no eat. The first
brain-driven passage through the gate in the arena's record (0120: zero
entries in 22 lives), on the arm WITHOUT a stage sense, under futility +
process recipes; the chain's last act — dig, collect, eat in the larder,
taught fifteen times as V0 — did not land in the ~900 steps it had.

Reading for the bar: by the registered primary meter (full-chain eats)
flat 3 is 0; by 0120's `chains` meter (gate-guaranteed entries) it is
1. Both are reported at the verdict. Rounds continue unchanged.

## 2026-09-28 — Bar R1 read at the registered n = 8: FAIL as measured. The ladder is in the kernel and the body still cannot walk the loop; the pointer is convicted

**The rows [measured, `rig/flat-lives.jsonl`, `rig/sib-lives.jsonl`,
`rig/r1-verdict.json`; rounds 1–8 interleaved flat/sib, 23:19–01:02]:**

| arm | life | crossings | gate passages | eats | wasted peeks | poisons | out-of-context | where the life went (cell, steps) |
|---|---|---|---|---|---|---|---|---|
| flat | 1 | 1 | 0 | 0 | 1 | 2 | 3,524 | gate cell (15,8), 1,650 |
| flat | 2 | 1 | 0 | 0 | 0 | 1 | 3,548 | corner (9,6), 2,652 |
| flat | 3 | 3 | **1** | 0 | 0 | 1 | 2,469 | corner (9,6), 648 |
| flat | 4 | 0 | 0 | 0 | 2 | 0 | 3,977 | gate cell, 4,351 |
| flat | 5 | 2 | 0 | 0 | 0 | 0 | 2,629 | corner (9,6), 1,685 |
| flat | 6 | 4 | 0 | 0 | 0 | 0 | 2,664 | corner (9,6), 1,433 |
| flat | 7 | 0 | 0 | 0 | 3 | 0 | 4,472 | gate cell, 4,073 |
| flat | 8 | 1 | 0 | 0 | 1 | 2 | 3,265 | gate cell, 2,461 |
| sib | 1 | 1 | 0 | 0 | 0 | 0 | 611 | closure (0,0), 4,128 |
| sib | 2 | 0 | 0 | 0 | 3 | 1 | 3,830 | gate cell, 3,952 |
| sib | 3 | 1 | 0 | 0 | 0 | 0 | 1,102 | closure (0,0), 3,496 |
| sib | 4 | 1 | 0 | 0 | 0 | 2 | 2,763 | corner (9,6), 1,138 |
| sib | 5 | 1 | 0 | 0 | 0 | 0 | 612 | closure (0,0), 4,176 |
| sib | 6 | 1 | 0 | 0 | 0 | 0 | 1,787 | closure (0,0), 2,334 |
| sib | 7 | 1 | 0 | 0 | 0 | 2 | 619 | closure (0,0), 4,571 |
| sib | 8 | 0 | 0 | 0 | 2 | 2 | 4,531 | gate cell, 3,334 |

Paired by round, sib − flat: **full-chain eats 0 − 0 in every round**
(the registered primary meter; the 0120 sibling baseline of zero
stands); gate passages −0.12 ± 0.12 SE (flat 1, sib 0); lap crossings
−0.75 ± 0.49; wasted peeks −0.25 ± 0.65; poisons +0.12 ± 0.48; **out-
of-context −1,337 ± 581** (the one separation beyond 2 SE — the stage
filter keeps the sibling on in-context recipes). `stage_filtered_events`
5,200–6,000 per sibling life (the filter live every step); process
recipes 10/40 in every life; `wander_steps` 0 in all 16 lives (with 40
recipes and place-keyed poison, some recipe is always eligible — the
wander phase the 0120 prototype produced never occurs under the shipped
form). World counter vs pos-trace reconstruction: exact in 16/16 lives.

**Bar R1: FAIL as measured.** The sibling — stage sensed, all three rungs
on — completes zero chains in 8/8 lives, as 0120's sibling did without
the rungs. Its behavior is bimodal and the same in every life of each
mode: **6/8 lives walk exactly one taught lap from birth (first crossing
at ~1,700–2,500 steps) and then park at the loop's closure cell (0,0) for
2,300–4,600 steps; 2/8 lives never lap — pulled from birth to the closed
gate by the larder recipes (whose post-reset steps stand at stage 0
too), peeking 2–3 times.** The flat reference is more varied (0–4
crossings; one life laps three times, passes the open gate, enters the
larder and fails to finish a dig in its last 961 steps; one life laps
four times with the gate open and never turns in) and no better.

**Which rung the counters convict [mechanism-argument on measured
behavior + the offline reconstruction of 2026-09-27]:** none of the
three as shipped is inert — futility poisons where a stall accumulates
(0–2 per life, both arms), process recipes exist (10) and are selected
(the sibling's one lap IS a process recipe walked, stage-filtered, from
birth to the line), and the stage filter partitions eligibility every
step. What fails is downstream of all three: **the pointer.** At the
loop's closure every eligible lap recipe — the next stage's included —
resolves by position to its own last step (nearest 136–138 of 140,
pointed places (0,0)/(0,1) at 0.02–0.09 blocks), so the hold keeps the
body where it stands; and the shared pointer index turns argmax flicker
among 139-/140-step laps into "advances" that reset the place-keyed
stall, so futility cannot rescue it (0 poisons in 5 of the 6 parked
lives; the 2 poisons in life 7 fired elsewhere). This is the successor
0123 named and deliberately did not build — pointer-local / stage-aware
pointing — now with an arena reading: a stage-aware pointer sends the
three next-stage laps forward to (3,0) at that very observation
(`rig/sap_policy.py`, verified offline, not run). A second kernel-grain
finding rides along: place-keyed futility's stall tracker keys advance
on a single `_prev_ptr` shared across recipes.

**Reversal conditions checked:** the ladder's necessity — no flat life
with the ladder OFF was run (the 0120 baseline stands, zero in 8); with
the ladder ON flat completed zero chains in 8, so nothing reopens it.
The eligibility form (0123) — the sibling was never stranded by hard
eligibility: in every parked life eligible recipes existed and were
selected; the shape is not convicted, the pointer is. The gate (0119/
0120) — unread; M0–M2 do not run (zero-vs-zero would read at any n).

**Standing, per this topic's direction clause:** R1 FAIL → the topic
stops before M1 and records the convicted mechanism. The next gap is
named with numbers and a verified prototype: stage-aware pointing on
the recipe policy (the pointer's nearest-step search restricted to
stage-matched steps; per-recipe pointer tracking for the stall). Whether
it runs as this topic's amendment 4 (the-long-carry's futility
precedent, one rig-level subclass, the same 8 rounds) or as its own
registration is the owner's call; the rig, the taught brains
(`mc/flat-*`, `mc/sib-*`) and the world are kept for either.

Ops: server and bridge stopped 01:05 (`docker compose stop`; world data
kept in `rig/data/`); no "Can't keep up" in the server log all night;
15.6–15.9 steps/s throughout, 16 lives × 6,000 steps, zero crashes.
