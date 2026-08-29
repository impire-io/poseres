# 0021 — The long carry: the gate's arena and the mechanism ladder

**Status:** design (2026-08-29). Born from research topic
the-long-carry (episode
[0120](../04-JOURNEY/0120-the-long-carry.md)) — episode 0119's
named successor, run to its honest stop. This document holds two
things: the compositional gate's deciding arena as a standing,
revivable instrument, and the measured mechanism ladder that must
be climbed before that arena can read the gate's question. Every
claim carries its measurement.

## What is measured and settled

- **The arena exists and binds.** The larder loop: a live-Minecraft
  world whose food chain is N = 3 laps of a closed course counted
  by the world's own machinery, ≈ 620–650 steps per chain at the
  measured gait — 6× the probe world's forage chain. Opacity is
  measured, not assumed: a linear readout on the decision span
  reads the aliased lap pairs at dead chance (2v3: 0.5039 vs
  control 0.5036 ± 0.063; 3v4 within band), and the world's counter
  was exact across all 22 brain-driven lives (episode 0120).
- **Two arena-design theorems, earned by failed reads:** under an
  absolute pose sense, global opacity forces LOOP geometry — chain
  stages must revisit the same places, or pose decodes the stage;
  and any monotone exogenous SENSED signal is a progress channel —
  the day clock and weather decoded the lap ordinal through the sky
  until pinned by world config. Any future opaque arena inherits
  both.
- **The wild stack cannot express stage-conditional behavior, with
  the blocking gaps isolated to three mechanisms** (0120, measured
  behavior + code trail): futility absent (repaired at prototype —
  see below), process memory absent (recipes require a pocket gain;
  a taught path is unstorable as behavior), and stage-conditional
  selection absent (a sense reaches recipe selection only through
  terminal drive value; the sibling's declared lap sense was
  structurally inert). With all three absent, flat and
  position-sensing arms read identically zero at n = 8 — and
  composed tiers would read through the same inert pathways.

## The feature candidates (the ladder, in kernel grain)

1. **Futility — progress-keyed disengagement.** The stalled-pointer
   signal RecipePolicy already computes must erode the following
   behavior. Prototype of record (rig-level, measured): layer
   fatigue — K = 200 followed steps without pointer advance puts
   the recipe layer dead for W = 800 steps, then it revives; this
   abolished a 4,672-step futile press, birthed the re-check
   cadence from the constants alone, and produced the arena's first
   brain-driven crossings. Two refuted forms with numbers: naive
   per-recipe erosion (boundary thrash, 556 die/revive events) and
   its hysteresis fix (cohort fallback among near-identical
   recipes). The promoted form should be **place-keyed**: a dying
   recipe's stalled subgoal poisons every recipe currently pointing
   there — required the moment process recipes exist, or the lap
   recipe dies with the stalled turn-in cohort.
2. **Process recipes — a vocabulary for gainless demonstrations.**
   `RecipeMemory.add_demonstration` stores nothing without a pocket
   gain (feature 041's core assumption: recipe = demonstrated
   acquisition). Long-horizon worlds demand demonstrated PROCESS —
   do-this-then-that with no immediate gain. A process recipe's
   terminal is its last observation; its worth question (what makes
   a path worth walking when nothing is acquired) is the design's
   open core, adjacent to the completion itch's existing grammar.
3. **Stage-conditional selection.** A pathway by which observation
   context (sensed stage — or, for composed tiers, carried stage)
   modulates WHICH recipe is eligible, not just which terminal is
   valuable. Without it, the gate's comparison cannot read: this is
   the pathway a winning composed arm would speak through.

## The arena's revival kit

Commit `a4b4386` holds the full rig under
`hq/01-RESEARCH/the-long-carry/rig/` (removed at graduation; git
history keeps it): docker-compose (lc-minecraft:25603),
`arena_provision.py` (idempotent build: course, counter, gate,
larder, indicator column, pinned sky), `mechanism_check.py` (the
15-check contract walker + gait calibration),
`lc_runner.py` (teach/lives/rounds with the closed-loop
WaypointTeacher, the loop curriculum, and the futility prototype),
`decode_probe.py` (the decision-pair opacity probe),
`probe_walk.py` (walker-driven probe rows). The bridge's `laps`
sense ships in `examples/minecraft/bridge/bridge.js`, env-gated
(`LAPS="x,y,z"`), default off, appended LAST — the flood/aim/peers
pattern. Teaches are ~25 min, lives ~6 min at the 5× fabric.

## The standing caution, carried from 0020

Do not build the gate's shape into the kernel: the lab ordering did
not transfer (0119), and the deciding arena — this one — cannot
read until the ladder is climbed. When M0–M2 run here, the 0119
scaffolding (commit 4171779) composes onto this world unchanged,
and 0120's reversal conditions govern: a current-stack life
completing chains beyond spread demotes the ladder to dials; a
beyond-spread composition win reopens the gate's shape question
with those numbers.

## Constraints carried forward

Nothing faked: the arena is a real server, real body, real food
economy, world machinery in-game only (command blocks as world
furniture, buried, never in any observation). Instrument bars
before behavior bars; amendments only pre-run with forcing numbers;
senses world-declared and opt-in; the kernel untouched by research
(every prototype a rig-level subclass).
