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
