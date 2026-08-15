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
  value trace in the parked geometry shows, at the release frames, the
  DIG action's total value crossing below the chosen competitor's
  exactly in the clip's predicted band (progress_now ≥ 1 − Δ̂ − 0.05,
  with Δ̂ read from the head's own predicted delta), on ≥ 3 distinct
  releases in one 1,500-step trace. If releases scatter uniformly over
  progress instead, the mechanism hypothesis is wrong and the fix does
  not run.
- **Bar L2 (the fix closes the crack, instrument grade):** the same
  parked geometry, same taught brain, itch unclipped (opt-in flag,
  everything else byte-identical): ≥ 5 digs run to the world's own
  break (progress reset + drop appears) in one 1,500-step trace where
  the clipped run completed 0, and ≥ 1 full dig → collect → eat chain
  fires. The discriminating pair (flag off vs on) runs back-to-back on
  the same classroom.
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

<Empty until graduation.>
