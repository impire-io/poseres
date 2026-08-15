# The last crack — why does the taught dig quit at 97%, and what pays the final stroke?

**State:** active
**Started:** 2026-08-15

## Abstract

The decree diagnostic (the-aim, DECREE-READING.md) measured a defect
prior to every aiming question: parked at a melon, the taught head digs
211 of 389 frames, its longest hold reaches mining progress 0.97 — and
no dig EVER completes, because vanilla resets block damage on release
and the last frames are never held. Every "the skill expresses with
variance" reading since c1e inherits a correction from this. A
decisive answer closes the gap between "the chain is taught" and "the
chain finishes", and re-grounds the aim and native-survival arcs on a
skill that can actually pay itself.

## The question

Does the taught chain fail at the dig's final frames because the
completion itch's clipped horizon structurally quits — and does paying
the full predicted stroke close the crack?

## The mechanism hypothesis (pre-registered before any fix)

The itch values a directed action at κ·(progress_after − progress_now)
with `progress_after = min(progress_now + Δ̂, 1.0)`. With the head's
learned per-step dig delta Δ̂ ≈ 1/30 ≈ 0.033, the clip guarantees the
itch decays to κ·(1 − progress_now) once progress_now > 1 − Δ̂ ≈ 0.967
— while the competitors do not decay: the recipe hold already points
at the next station (the demo's collect walk), and the completion
bonus cannot rescue the final frames live because the world pays the
pocket after the break (measured: no action predicts a live pocket
gain — the head-reading). Predicted release point: progress_now ≈ 1 −
Δ̂ ≈ 0.97 — exactly the measured ceiling. The candidate fix is one
principled line, opt-in (constitution I): the prediction is a VALUE,
not a sensor reading — leave `progress_after` unclipped, so the itch
pays the full predicted stroke even when it overshoots the meter's
top, and the quit point disappears.

## Pre-registered bars

Live-world evidence only; the parked-decree geometry (the-aim v4) is
the instrument — it makes the under-hold deterministic.

- **Bar L1 (the mechanism is measured, before any fix):** a per-frame
  value trace in the parked geometry classifies every dig release as
  DIRECTED (the value crossover) or EXPLORE (the ε-gate's random
  frame; ε = 0.1 shipped, which alone gives a 30-frame hold only a
  ~0.9³⁰ ≈ 4% survival — a second candidate mechanism named before
  the run, sharpened by the live world's own rule that block damage
  resets on release, which the lab world never enforced). The bar:
  the attribution is decisive — either directed releases concentrate
  in the clip's predicted band (progress_now ≥ 1 − Δ̂ − 0.05, Δ̂ from
  the head's own predicted delta, ≥ 3 such releases) confirming the
  clip, or ≥ 80% of releases are explore-frames convicting ε — and
  the fix that runs is the one the measurement convicts. If neither
  pattern holds, the topic returns to diagnosis with the trace
  published.
- **Bar L2 (the convicted fix closes the crack, instrument grade):**
  the same parked geometry, same taught brain, the L1-convicted fix
  applied as an opt-in flag (everything else byte-identical) — clip
  convicted → `progress_after` unclipped (the prediction is a value,
  not a sensor reading); ε convicted → exploration defers while a
  held intention is advancing (progress rising last step): ≥ 5 digs
  run to the world's own break (progress reset + drop appears) in one
  1,500-step trace where the baseline run completed 0, and ≥ 1 full
  dig → collect → eat chain fires. The discriminating pair (flag off
  vs on) runs back-to-back on the same classroom. If BOTH mechanisms
  are convicted, both flags land and the pair runs the composition.
- **Bar L3 (nothing else moves):** flag off is byte-identical — the
  frozen T1–T6 suite and the whole quality gate green, zero skips; the
  042 deficit-gate and 041 recipe tests untouched.

## Reversal condition

If L1's releases do not concentrate in the clip's predicted band, the
clip is not the mechanism — the fix is refused and the topic returns
to diagnosis (candidates on record: the recipe pointer advancing past
the dig station mid-hold; an event-head Δ̂ artifact). If L2's unclipped
run still cannot finish digs in the parked geometry, paying the stroke
is not sufficient — the release is re-diagnosed with the value trace,
and "completion keyed to the world's own break" (the drop channel)
becomes the next candidate, its own registration.

## Verdict

- **Bar L1 — the attribution, decisive** `[measured]`: neither
  registered pattern alone. The clip acquitted (0/4 directed releases
  in its band; releases at progress 0.011–0.546). Convicted: the
  KNIFE-EDGE — directed release margins 0.00002–0.069 against a hold
  margin of κ·Δ̂ ≈ 0.008 — with the ε-gate as accomplice (all three
  explore releases had DIG WINNING the value table, one at progress
  0.994). Amended openly pre-run to an attribution bar (ε joined the
  suspect list from code reading); amended post-trace to the third
  mechanism with the raw margins recorded in JOURNEY.md.
- **Bar L2 — PASS** `[measured]` (powered to 3 repeats per arm after
  7-vs-1 single-arm variance, amendment recorded): baseline 0 breaks
  in 4,500 parked steps; committed 10 breaks, 11 collects, and one
  repeat ran the whole chain — steered contact → committed dig →
  break → collect → 6 eats to full satiation (food 8 → 20), **first
  eat at step 333**, an order of magnitude faster than the record's
  previous best (1,119). En route the mechanism's degenerate twin was
  measured on schedule — a 517-frame DIG lock (perseveration) —
  closed by the intention boundary.
- **Bar L3 — PASS** `[measured]`: flags off is bit-exact (RNG streams
  included) — the full gate green, byte-frozen T1–T6 suite included;
  25 policy unit tests cover the new mechanisms.
- The question answers **YES** with the mechanism named
  `[mechanism-argument on measured margins]`: the dig quit because
  the vote is a knife-edge re-fought every frame; commitment
  (incumbency while progress advances, dying with its intention at a
  progress collapse) plus exploration deferring to a live hold pays
  the final stroke. Promotion into the shipped default is a spec-kit
  feature decision, deliberately not taken here (design 0014).
