# Episode 0052 — Senses without my ontology (2026-07-21)

The first hours of the multi-week run were an audit, and the owner read
it better than its builder. Three arguments, all accepted (feature 033,
`033-property-body`):

1. **"Why do you need material classifiers?"** The four named classes
   were my taxonomy in the body's senses — and measurably broken: the
   live bot carried 12 real items (pale moss, gravel, a dripleaf —
   spawn was near a Pale Garden) while its pocket channels read 0.0
   forever, because my name-filter knew only "dirt" and "stone"
   [measured — real inventory vs channel telemetry]. Any name list is
   somebody's opinion. Now: **properties** (placeable = the item maps
   to a block — the game's own fact, which also fixed my vanilla
   deviation: logs and gravel ARE placeable, sticks are not) plus a
   stable **appearance signature** (sha256 of the item name → 3 dims,
   identical cross-bridge, verified live cross-language). Categories
   are the brain's to form — literally now.
2. **"The action budget cannot be a flat timeout."** The 1-second
   bound had made logs (3 s bare-handed) unmineable — the crafting
   question was structurally dead on arrival. Digging is now a **held
   intention**: start/continue on `dig_ahead`, released by anything
   else, with a sensed `mining` progress channel (vanilla's cracks)
   and only a 10 s no-progress safety cap. Persistence became world
   physics and a learnable skill in one move.
3. **"We need a better understanding of what the channels are."**
   Per-channel labels now travel in the metadata (the 029 format
   always supported them; no body had filled them in) — `env.sin_time`,
   `hand.placeable`, `mining.progress` — and the dashboard gained a
   **ground-truth panel** (the 015 world-view channel): real item
   names, held item, position, dig progress, right next to what the
   brain senses of them. Two truths, one screen.

The body is now obs 32 / actions 12 (fourth revision, third contract
amendment, zero core edits — sixth feature running). The pilot
re-baseline [measured, pilot-results.md]: learning robust **8/8** at
32/12 (median +0.184); the equal-budget tax came back down to −0.044
(from 031's −0.115 — structured senses appear to pay for their dims);
and the persistence cliff is real: **0/8 seeds completed even one dig
by chance** (max progress: one tick of three) — the material chain's
chance rate is ≈ 0, so in the long run *any* sustained material
acquisition is above chance and any crafting is unambiguous emergence.

The live smoke earned its keep again: the held-intention dig
**self-aborted at one tick** because mineflayer counts `forceLook` and
control-state writes as movement — invisible to the fake, found only
by digging a real log on the real server (`forceLook: "ignore"` + no
control clearing while the intention is held; then: progress 0 → 0.95
across held ticks, diggingCompleted, drop collected) [measured]. Run
v1 (`c1`, ~40.7k steps) was closed and archived — real learning
(pred err 0.967 → 0.198, pop 1 → 16), blind pocket, stated — and **run
v2 (`c1b`) launched the same evening on a fresh world**: 32 labeled
dims live, ground truth flowing, the pre-registration amended before
boot (C1-RUN-PLAN v2).

Reversal condition: unchanged from 031 (the 14/8 legacy flag), noting
the legacy body on the v4 bridge cannot place — the reversal is about
learning viability. The named successors stand: the crafting table
rung if the ladder shows climbing; skill discovery → self-registered
tools if it climbs well.

Trail: specs/033-property-body/ (spec/plan, pilot-results); the 027
contract's third amendment; commits through 87f0e32 + the run-plan
amendment; smoke scripts in the session scratchpad; run v1 archive
under S3 `pra/v1/c1/`, run v2 live under `pra/v1/c1b/`.
