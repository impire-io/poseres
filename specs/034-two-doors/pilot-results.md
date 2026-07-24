# Feature 034 pilot results — Two Doors E1 (8 seeds, both arms)

**Date**: 2026-07-24 · **Runner**: scratchpad per FR-006 · **Published
before the confirmatory run** (SC-002).

## Protocol as run

- P0 (SC-001) passed first: **45/45** demonstrations complete on seed 1 —
  the 22-action tape produces dig → planks-craft → stick-craft every
  segment (view indices 14 / 17 / 21, byte-stable across segments).
- Detector note (registered here, before the read): the ground-truth view
  does not show the staging grid, and the fake world moves inputs out of
  the pocket at `grid_put` — one step before the result lands — so the
  spec's rise-with-fall pairing never fires on any transition. The
  operational rule is the causal triple over bare increases
  (log-up → planks-up → stick-up in order), which is **exact** here:
  every window starts in a fresh world with an empty pocket, and the only
  mechanical path to a stick is the full chain.
- Pilot: seeds 1–8, taught vs blank, H = 5,000 free-run steps, frontier
  alone, seed-paired.

## Result: the null, at pilot power

| arm | seeds with ≥1 full chain | digs attempted | logs | planks | sticks |
|---|---|---|---|---|---|
| taught | **0/8** (45/45 demos each) | **0** | 0 | 0 | 0 |
| blank | **0/8** | **0** | 0 | 0 | 0 |

Not a single `dig_ahead` engaged a block in 80,000 free-run steps across
both arms (`digging_records = 0`, `max_dig_progress = 0`, every pocket
empty at window end). Both arms drift: ~1,800–2,700 unique positions per
5,000-step window — the runner walks off the feature cluster into the
world's featureless plain and does not return.

**The arms are behaviorally indistinguishable.** Teaching changed nothing
the window can measure.

## Validity check — the graduate really is the taught brain

Seed 1, state continuity across the 45-segment bridge and the free-run
resume: graduate `cycles_done` 45, 966 pred-error samples, **19 frames**;
free-run final `cycles_done` 273, 5,754 samples, population 19→20. The
blank ends at 12–13 frames. The taught free-runner carries the
demonstration-built population — the null is not a broken resume.

## Reading [mechanism-argument — the confirmatory run measures, this explains]

The frontier drive rewards *realized local progress* — error falling —
and scores mastered (flat-low) ground at ~0. Forty-five identical
demonstrations make the demo neighborhood the best-learned region the
brain has ever seen; by graduation the progress has already been
collected. **To a frontier drive, a well-taught lesson is exhausted
territory — the graduate leaves the workshop precisely because the
teaching worked.** This refutes, for realized-progress drives, the
teacher-model rev.2 landscape claim ("the demonstration makes the goal
learnable, which makes it the highest-frontier option"): demonstration
lights the frontier *during* the guided phase and silences it after.
The premise's shape sharpens: drives generate contact with the mechanism
(E0, live world), and teaching plus a mastery-silent drive generates
*flight from* the mechanism (this pilot, offline world).

Context row for honesty: this world is an infinite featureless plain with
one small feature cluster; away from it nothing is diggable and nothing
changes, so no gradient points home. The live world (E0) offers diggable
ground everywhere and frontier still never chained — the two testbeds
fail in the same direction from opposite geometries.

## Decision

Proceed to the registered 24-seed read (US3). The pilot predicts an
honest FAIL of the taught bar (≥6/24), which — per the topic ladder —
is exactly the evidence that authorizes E2 (goal object + bounded fading
λ + one multi-step mechanism).
