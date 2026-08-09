# Brain-side hold — can the event head's own movement predictions replace the clone-step Φ?

**State:** active
**Started:** 2026-08-09

## Abstract

The measured stay/want/finish composition (episodes 0069–0073) carries one
piece of laboratory scaffolding: the hold's potential Φ reads the position
*after* a candidate action from a deep-copied world — a clone oracle no
deployed brain can have. Everything else is brain-side and shipped (feature
040). This topic asks whether the shipped event head — which predicts
per-action observation deltas, position channels included — can supply
Φ̂ from the brain's own model: predicted next position against the taught
goal observation's position, in the clone's exact units. A PASS removes the
last scaffold, makes the full composition deployable, and unblocks
registering a c1d long run; a FAIL isolates movement prediction as the next
build. Opened under the owner's delegated autonomy ("can we do all in
parallel and autonomous?", 2026-08-09).

## The question

Does replacing the clone-step Φ with the head-derived
Φ̂(a) = 64 · Chebyshev(obs[x,z] + Δ̂ₐ[x,z], goal[x,z]) — goal = the taught
goal observation's position channels, everything else unchanged — preserve
the hold and the composition's chains at pre-registered power?

## Pre-registered bars

Protocol: the 24 G5 graduates (33-dim, event heads trained through the 45
demonstrations — note the tape contains turns but **never** forward/back, so
movement models start cold and must learn online from ε-exploration during
the run), H = 5,000, fresh worlds, λ = 0.25 (the clone-measured operating
point; Φ̂ is in the clone's world units, so the scale carries). Reference
rows standing: clone-Φ hold measured 99.98% dwell / zero departures
(episode 0069); clone-Φ + itch on this cohort measured 24/24 chains (G5's
V0 arm).

- **Bar H1a — the hold survives de-scaffolding:** hold-only arm (shipped
  `CompletionItchPolicy` with κ = 0, potential = Φ̂): **median dwell ≥ 20%**
  across 24 seeds (goal-homing's original bar; the clone reference is the
  ceiling, not the bar).
- **Bar H1b — the composition survives:** full brain-side arm (κ = 0.25,
  the shipped itch + Φ̂ hold): **≥ 6/24 seeds complete a full
  log→planks→sticks chain** (the arc's standing chain bar; the clone
  reference on this cohort is 24/24).

Context rows (no bar): dwell over the first vs last 1,000 steps (the online
movement-learning curve), departures/returns, logs/sticks totals, and the
same rows for the clone arm where standing.

## Reversal condition

The direction assumes one-step position prediction is the hold's only
missing brain-side piece. It reverses if H1a fails while a diagnostic shows
the head's movement predictions accurate (error ≪ one step) — that would
mean the hold needs more than local position foresight (e.g., the wander
happens before learning converges and never recovers), making curriculum or
memory, not prediction, the gap. A pass with collapsed chains (H1a PASS,
H1b FAIL) sends the interference question to the itch seam, not this
topic's premise.

## Verdict

**Both bars PASS [measured, 2026-08-09, 308 s for both arms]** — the
clone-step Φ is replaced by the brain's own model, and the last piece of
laboratory scaffolding in the stay/want/finish composition falls.

- **H1a — the hold: PASS, median dwell 98.22%** (bar ≥ 20%; the clone
  reference 99.98%). The online learning curve is the mechanism, visible:
  median dwell 91.5% over the first 1,000 steps rising to **100.0%** over
  the last 1,000 — the head's movement models (never shown forward/back in
  teaching) converge from ε-exploration inside the first fifth of the run
  and then hold at the clone's level `[measured]`.
- **H1b — the composition: PASS 23/24 chains** (bar ≥ 6/24; the clone
  reference on this cohort 24/24), 647 logs, 1,919 sticks. The full
  composition — frames' drive, head-derived hold, head-driven completion
  itch — runs with **no ground-truth access anywhere**: every term reads
  the brain's own senses, memories, and learned predictions `[measured]`.
- What this closes `[judgment]`: the deployability gap named at the
  topic's opening. Every component of the measured behavior is shipped
  (feature 040) or taught (the goal observation); a c1d long run of the
  full composition is now registrable with zero scaffolding.

Reversal condition standing as registered; nothing fired.
