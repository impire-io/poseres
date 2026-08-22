# 0019 — Factored actions: the action side at vocabulary scale

**Status:** design (2026-08-22). Born from research topic
factored-actions (episode 0112) — the language gate's second
prerequisite (episode 0042), measured. Every claim below carries
its measurement; the design question is stated functionally,
explicit enough for `/speckit-specify` when a successor mechanism
is picked up.

## What is measured and settled (the floor this stands on)

- **The flat action side cannot carry a vocabulary.** Per-action
  transition slices and event-head rows train only on their own
  act's executions; experience per act starves as 1/A. At A=1024
  under a 13,000-step budget (~12.7 samples per slice) the flat
  kernel reaches zero — 0/24 seeds — while a perfect-knowledge
  oracle holds the world's ceiling flat within 6% across the same
  rungs: starvation, not task difficulty (0112, Bar F1).
- **The interaction term is what "factored" means.** An anchor that
  concatenates slot and value — `[onehot(slot); value]` — makes the
  linear-in-embedding conditioning span rank slot+1 where the
  world's action family needs rank 2·slots; no shared weights or
  free per-act rows can express *which-slot × which-value*. The
  product anchor `[onehot(slot); onehot(slot)·value]` spans the
  family exactly. Measured both ways: the concatenated edition read
  2.49× worse than a blank slate everywhere; the product edition
  removed the defect entirely (0112, the rank diagnosis).
- **Structure transfers completely.** With exact product anchors and
  everything else stock, a never-executed act's consequence is
  predicted exactly as well as a constantly-executed one's
  (held-out 0.0409 ≡ regular 0.0414 event-head MAE, A=1024) and as
  well as the flat kernel manages after per-act training (0.0375).
  Untried equals practiced — the property language requires,
  demonstrated (0112, Bar F3's measured core).
- **Mobility and lawful parity are in tension.** Three learned
  editions (anchor lr 0.01 → 0.001) bracketed the F0 parity line
  while every frozen sibling passed ~5 reaches/1k higher; a 10×
  rate cut recovered almost nothing. Anchors that start correct
  lose by moving — plausibly knife-edge action votes flipped by any
  blur off the exact structure (0101's lesson, one seam deeper)
  (0112, the mobility wall; Bar F4 blocked by it).
- **Prediction and behavior dissociate at the action seam.** The
  arm that predicts perfectly (frozen, product anchors) wins no
  races from A=64 up; the rank-broken learned arm out-reached it.
  Reach correlated with learning-on, not representation quality —
  the jitter-as-exploration hypothesis is on the record with its
  discriminator (per-arm executed-act histograms) named and unrun
  (0112).
- **Margins for generalization bars belong against trained-knowledge
  ceilings, not cold baselines.** In sparse-delta worlds,
  predicting "no change" is strong: the flat kernel's own trained
  slices reached only 0.69× of the cold baseline, so a 0.5×-of-cold
  clause demanded more than practiced knowledge itself achieves
  (0112, Bar F3's margin lesson).

## The design question

**What action-side mechanism carries a realistic vocabulary for the
teacher-world gate?** The measured constraints any candidate must
satisfy:

1. **Product structure in the conditioning.** The action
   representation must carry slot × value interactions natively —
   for language: *this inflection on this stem*, never stem and
   inflection side by side. Declared structure is body/anatomy
   territory (properties-not-names extends to acts: the body
   declares the slots and values the world's own grammar exposes).
2. **Mobility priced by evidence, not by step.** Exceptions
   (irregulars) require anchors that can move; lawful parity
   requires that they mostly don't. The named candidate:
   surprise-gated anchor movement — the table moves only on
   accumulated prediction surprise for that act, not on every
   gradient. Its gate: pass the F0-style lawful parity AND absorb a
   registered fraction of exceptional acts (the blocked Bar F4,
   re-registered fresh).
3. **Prediction and behavior measured separately.** A mechanism's
   consequence model and its action selection can succeed and fail
   independently; bars must read both, and a selection-side account
   of the frozen arm's reach death (the act-histogram
   discriminator) is open diagnostic ground for whoever builds
   next.
4. **Kernel invariants.** Opt-in, flat default, off bit-exact RNG
   included, the frozen T1–T6 suite untouched — the machinery in
   the trail ran rig-side with a one-hot parity proof (embedded ≡
   flat at machine precision) and a successor should keep that
   proof pattern.

## Definition of done (functional; a follow-up specs from here)

1. A mechanism satisfying constraints 1–2 passes lawful parity
   (F0-style, thresholds frozen at calibration) with mobility ON.
2. On a declared exceptional fraction, it fits the exceptions
   within a registered factor of its lawful error while held-out
   lawful generalization holds (the F4 question, finally
   measurable).
3. Generalization margins registered against the trained-knowledge
   ceiling of the same world and budget.
4. Only then does wiring into the teacher-world experiment
   (episode 0042's remaining prerequisites: sequence observation
   encoding; competence-vs-approval already substantially mapped by
   the praise arc) become a feature question.
