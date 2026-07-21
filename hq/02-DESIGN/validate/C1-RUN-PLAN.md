# C1-RUN-PLAN — the multi-week run, pre-registered (2026-07-21)

Written before boot (constitution II: criteria before the work). The
run's telemetry lands durably in S3 via the observatory (feature 032);
every reading below is computable from those objects.

## Fixed configuration (changing any of these = a new run)

- **Body**: the honest-primitives builder (feature 031) — obs 28 /
  actions 12, `c1_anatomy()` default. Seed **1**. `TICK_MS=250`
  (real-time posture; no `TICK_RATE` world acceleration — the
  emergence question is denominated in brain-steps, and real time is
  the C1 posture episode 0043 named). Snapshot cadence 25 cycles;
  `weight_norm_cap=1.2` (arc 026). Single brain, single bot — the
  world's non-stationarity is weather/daylight/its own edits only
  (multi-brain interaction is a *later, deliberate* experiment).
- **Node**: beno4 via `deploy/` (systemd supervision; resume on
  restart is the proven path).
- **Duration**: ≥ 14 days of accumulated brain-steps (~4.8M steps at
  4 steps/s), restarts included; the calendar may be longer.

## Pre-registered readings

Chance baseline (feature 031 pilot, measured): **~1 accidental
planks-craft per ~2,200 undirected steps; zero sticks in 2,200×8**.

- **R1 — emergence (the headline)**: over the final 7 days, the
  planks-craft rate per step vs the chance baseline. *Emerged* =
  sustained ≥ 10× baseline **and** offer-conditioned taking (fraction
  of `take_result` actions issued while an offer is showing) ≥ 3× the
  unconditional `take_result` rate. *Chance-level* = within ~2× of
  baseline. Anything between is reported as-is. Sticks-crafts are
  reported as counts (any sustained non-zero rate is notable — chance
  produced none).
- **R2 — the ladder's lower rungs**: rates of successful digs,
  held-class changes followed by class-consistent acts (hold→place
  with placeable, hold→grid_put), and place-with-material. Rising
  trends across weeks = rung learning even without full chains.
- **R3 — learning health**: prediction-error trajectory (no rot:
  late-window error must not trend above early plateaus), population
  at its ceiling (expected), frame lifecycle churn from `brain.events`.
- **R4 — reversal reading** (spec 031, supersedes 030): grid
  primitives effectively unused (R2 flat at noise) **and** improvement
  materially below the legacy pilot arm → fall back to
  `c1_anatomy(crafting=False)` for a follow-up run; the engagement
  data opens the hierarchy research arc either way.
- **R5 — operational honesty**: restart count (journalctl), seq-gap
  totals (dash + S3 key ranges), snapshot chain integrity (every
  resume logged against its snapshot id).

## Publication

The S3 objects are the artifact behind every number (constitution II:
public artifacts link their telemetry). The journey episode for the
run reports R1–R5 with spreads/rates, flattering or not.

## Pre-launch gate: CLOSED — soak PASS (2026-07-21, beno4)

961,000 observation steps at the exact launch config (28/12,
continuous, cap on, snapshot cadence 25): improvement **+0.635**
(pred error 0.778 → 0.143 — no rot, still improving at ~1M steps),
final population 29 at the ceiling, and **resume-at-length byte-exact**
(run B resumed from the cycle-2000 snapshot and serialized identically
to the uninterrupted run at cycle 4000). The soak also earned its keep
twice on the way: it exposed a 027-era FakeBridge socket bug at ~367k
requests (fixed, 06d93f3) before any reading counted. One vacuous
field in the soak script (population_tail_stable compared a list to
itself) is disregarded; the error trajectory carries the no-rot
reading. Scripts and raw logs: beno4:~/pra-runs/soak/.

**Launched 2026-07-21** with this plan in force.

## Amendment v2 (2026-07-21, same day): the property body, run `c1b`

The first hours of run v1 surfaced a measured blind-pocket bug (the
name-class filter missed the spawn biome's items) and the log-hardness
blocker; the owner then argued material classifiers and flat action
timeouts out of the body entirely (feature 033, episode 0052). Run v1
(~40.7k steps, run id `c1`) is closed and archived in S3 as a burn-in
observation: its learning was real (pred err 0.967 → 0.198, pop 1 → 16)
but its pocket was blind — not the experiment to spend two weeks on.

**Run v2 config (run id `c1b`, fresh world, launched ~20:55 UTC)**:
the property body — obs 32 / actions 12, classifier-free senses
(properties + sha256 appearance signatures), digging as a held
intention with sensed progress, per-channel labels, ground-truth view.
Everything else unchanged (seed 1, 250 ms, cadence 25, cap on).

**Baseline superseded**: the 031 chance baseline (~1 accidental
planks per ~2,200 steps) was an artifact of instant digs. Re-measured
at the v4 body: **0/8 pilot seeds completed even one dig** (max
progress: 1 tick of 3) — the material chain's chance rate is ≈ 0.
R1 accordingly sharpens: **any sustained material acquisition is above
chance, and any crafting at all is emergence**; the sensed `mining`
progress channel is the ladder's first learnable rung (it rises only
while the intention is held). R2–R5 unchanged; the dig-persistence
rate (consecutive dig_ahead streaks, completed digs) joins R2.
