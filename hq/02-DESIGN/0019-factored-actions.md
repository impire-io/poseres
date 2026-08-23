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
2. **Mobility priced by evidence, not by step — MEASURED (episode
   0114).** The mechanism: a per-act prediction-error EMA `E_a`
   (α = 0.1) beside the store's global EMA `G`; the anchor row
   receives its clipped gradient only while `E_a > θ·G` (θ = 2).
   Measured: lawful parity at the frozen arm's own level (SG0
   15.077 vs the wall's 10.2–10.6), slot-breaking exceptions
   absorbed at 1.559× own lawful error with untried ≡ practiced at
   1.002 — 24/24 seeds on both clauses — while the pinned control
   fails the same clause at 2.379. Gate economy: ~23 moves per
   lawful life vs ~1,100 on the exception world. Known cost, open
   door: the gated arm's absolute lawful error runs ~1.8× the
   frozen control's; hysteresis, per-slot gates, or post-move
   re-freezing are the named candidates, and the dials (α, θ) were
   never swept. Protocol inheritance: exception worlds must break
   the SLOT (claimed slot ≠ acted slot) — value-only exceptions
   dilute into channel averages and cannot discriminate mechanisms
   (0114 Amendment 1).
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

1. ~~A mechanism satisfying constraints 1–2 passes lawful parity
   with mobility ON~~ — **met** (episode 0114, Bar SG0).
2. ~~On a declared exceptional fraction, it fits the exceptions
   within a registered factor of its lawful error while held-out
   lawful generalization holds~~ — **met** (episode 0114, Bars
   SG1′/SG2′, 24/24 both clauses against a failing pinned control).
3. Generalization margins registered against the trained-knowledge
   ceiling of the same world and budget — a standing rule for every
   successor registration, not a one-time gate.
4. Wiring into the teacher-world experiment is now gated only on
   episode 0042's remaining prerequisite — observation encoding for
   unbounded sequences (competence-vs-approval was substantially
   mapped by the praise arc). The mobility premium (~1.8× lawful
   error) is a named optimization door, not a blocker.
