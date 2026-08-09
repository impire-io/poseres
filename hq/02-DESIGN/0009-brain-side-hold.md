# 09 — The brain-side hold (graduated research, episode 0074)

**Status:** measured design, not yet built as src. Everything below runs
today on shipped components plus ~15 lines of caller-side composition; a
src build (a shipped potential helper) is optional convenience, licensed
but not demanded.

## What was measured

The stay/want/finish composition holds position and completes chains with
**no ground-truth access**: median dwell 98.22% (hold-only), 23/24 full
chains (full composition), on 24 seeds at H = 5,000 (episode 0074;
reference: the clone-oracle hold at 99.98% and 24/24). Movement models
start cold and converge from ε-exploration within ~1,000 steps.

## The design

A deployment composes the policy entirely from shipped seams:

- **Engine**: `Config(event_head_eta=0.5, ...)` — the head learns and
  persists (feature 040, Doc 0005 §4.4).
- **Policy**: `CompletionItchPolicy(params, kappa=0.25, progress_index=…,
  pocket_index=…, potential_of=hold)` with the hold closed over the
  policy's own context (capture `context` in a subclass or wrapper before
  delegation):

  ```
  Φ̂(a) = SCALE · Chebyshev( (obs[x] + Δ̂ₐ[x], obs[z] + Δ̂ₐ[z]),
                             (goal[x], goal[z]) )
  hold(a) = λ · (−Φ̂(a)),   λ = 0.25 (measured), SCALE = the anatomy's
                            position normalization (64 at C1)
  ```

  `Δ̂ₐ` = `context.predict_event_delta(a)`; the term contributes 0 when
  the head is off (delta is None).
- **The goal**: the position channels of a *remembered observation* — at
  C1, the teaching protocol's recorded goal observation (the E2.0
  instrument). Functionally: any stored observation whose position marks
  "the work" can serve; nothing about the term is Minecraft-specific.

## Constraints the measurements impose

- The hold needs the head **on** and benefits from a head that has seen
  movement; a cold head costs roughly the first fifth of a 5,000-step
  run before the hold reaches ceiling. Teaching that exercises movement
  would close that window (untested — a c1d design choice).
- Distance must be computed over **position channels in world units**,
  not the full observation (the July obs-form 3.8% failure, scoped by
  episode 0074).
- λ = 0.25 is measured at C1's scales; other anatomies re-pilot the λ
  grid per the goal-homing protocol.

## What this unblocks

**c1d** — the long-run registration of the full composition (drive +
brain-side hold + completion itch) on the observatory, zero scaffolding.
Its open design questions are the run-plan's, not this document's:
teaching-phase content (movement included?), snapshot cadence, and the
0074 reversal watch (does the hold drift after long homeostasis as later
learning overwrites position models — the memory/consolidation
question).
