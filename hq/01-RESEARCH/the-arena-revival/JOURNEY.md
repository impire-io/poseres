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
