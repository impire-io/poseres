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
