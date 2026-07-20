# T-SCALE diagnosis — why `best_dim` collapses at high `true_dim`

Date: 2026-06-29. Instrument: `pra-validate scan` (dimension-scan diagnostic,
added for this investigation) plus scratchpad experiments. Question under test:
the build's T-SCALE run at `true_dim ∈ {20,35,50}` reports `best_dim ≈ 1` — is
that a search problem, a scoring problem, a capacity problem, or a world problem?

**Answer: none of the single hypotheses. It is a compound scale-invariance
failure: three separate constants, each validated at the reference scale
(`obs_dim=10`, `hidden_size=12`, `true_dim=3`), silently leave their validated
regime when the dimensions grow.** In causal order:

## 1. The world saturates (world-side)

The emission is `tanh(E·latent)` with pre-activation variance = `true_dim`:

| true_dim | pre-act sd | P(saturated, \|pre\|>2) | P(sign channel, \|pre\|>3) |
|---|---|---|---|
| 3 (reference) | 1.66 | 18% | 8% |
| 20 | 4.49 | 65% | 49% |
| 35 | 5.99 | 73% | 61% |
| 50 | 7.11 | 77% | 67% |

At scale the world is not "the same world, bigger" — it degenerates toward a
binary sign channel whose latent geometry is largely unrecoverable and whose
gradients vanish. Fix (spec change, PRA-02 §1): normalize the emission,
`tanh(E·latent / sqrt(true_dim/3))` — the factor is exactly 1 at the reference
`true_dim=3`, so the validated world is byte-identical and only scaled configs
change regime.

## 2. The learning rate diverges (agent-side, the binding constraint)

`learning_rate=0.03` was validated at `obs_dim=10`. SGD's stability threshold
shrinks as input norms grow (`‖obs‖²` is 6× larger at `obs_dim=60`). Probe at
dim=20/hidden=32, normalized world, fan-in init, 300 episodes, seed 1:

| lr | recon err | honest pred err |
|---|---|---|
| 0.030 | 1.138 (diverging) | 1.124 |
| 0.010 | 0.645 | 0.683 |
| 0.005 | 0.502 | 0.576 |
| 0.002 | **0.335** | **0.381** |

Every earlier flat scan — and the paradoxical "bigger hidden is worse" — was
optimizer divergence, not representational capacity. This was the binding
constraint masking everything else.

## 3. The init scale saturates at birth (agent-side)

`init_weight_scale=0.3` with no fan-in normalization: encoder pre-activation sd
= `0.3·sqrt(obs_dim)` ≈ 2.3 at `obs_dim=60` (saturated at init), and initial
output magnitude grows with `sqrt(hidden)`. Scale-invariant form: per-tensor
`scale = 0.3·sqrt(fan_in_ref / fan_in)`, which reproduces exactly 0.3 at the
reference dims.

## Honest side-finding: prediction ≈ persistence, even at the reference

Baselines for honest obs-space prediction error:

- `true_dim=3` (stock world): identity baseline (predict next = current) =
  **0.165**; the validated live system reaches 0.157. The celebrated T2
  improvement is ~95% *reconstruction* learning; the margin beyond persistence
  is ~5%.
- `true_dim=20` (normalized world): identity = 0.230; an arctanh-linear oracle
  = 0.208. The dynamics signal beyond persistence is intrinsically small.

Implications: (a) at scale the dimensional elbow must be carried by the
**explain/recon term**, not prediction; (b) T3's effort-only ablation pulls
predictions toward *zero* — much weaker than an identity-transition ablation,
so the suite never requires the system to beat persistence. Consider a
PRA-02-level question: add an identity-ablation variant of T3, and/or increase
`action_scale` at scale so actions move observations materially.

## Experiments run (chronological)

1. Scan `true_dim=3`, hidden 12 (sanity): capacity cliff exactly at 1→3
   (pred 1.24→0.58), then a slow overfit decline — the documented shallow elbow.
2. Scan `true_dim=20`, hidden {12,32,64}, stock world: flat ~0.8–1.3 at every
   dim; bigger hidden worse. (Cause, in hindsight: saturation + lr divergence.)
3. Scan `true_dim=20`, hidden {12,32}, normalized world: better absolute errors
   (min 0.755) but still no elbow; min pred at dim 3. (Cause: lr divergence.)
4. lr probe (table above): lr was the binding constraint.
5. Definitive scan — normalized world + fan-in init + lr=0.002, hidden {12,32}:
   **results below.**

## 5. Definitive scan result — the elbow is restored; parsimony is the last layer

Normalized world + fan-in init + lr=0.002, `true_dim=20`, 600 episodes, 3 seeds:

| | hidden=12 | hidden=32 |
|---|---|---|
| dim 1 pred err | 0.694 | 0.868 |
| dim 3 | 0.555 | 0.530 |
| dim 10 | 0.444 | 0.391 |
| dim 16 | 0.437 | 0.349 |
| dim 18 | 0.440 | **0.339** |
| dim 20 | 0.441 | 0.349 |
| dim 25 | 0.441 | 0.327 |
| dim 30 | 0.451 | 0.326 |

- **hidden=12 plateaus at dim ≈ 10–16** — capped by its own hidden width (the
  capacity bottleneck signature, finally visible once lr stopped diverging).
- **hidden=32 keeps improving to dim ≈ 18–25** — the diminishing-returns elbow
  sits at ≈ `true_dim`, shallow exactly as at the validated `true_dim=3`.
  Conclusion: with the three scale-invariance fixes, dimensional structure at
  scale is recoverable, and `hidden_size` must scale ≳ `true_dim`.
- Honest caveat: the best frame (0.326) still does not beat the persistence
  baseline (0.230) at this experience budget — prediction remains decode-floored
  and the dynamics margin stays open.

**Layer 4 — parsimony mis-scale (the remaining open [D] question).** With
`w_complexity=0.04`, the score minimum still lands at dim 3: the error gain from
dim 2→20 (~0.27) cannot outbid a linear penalty of `0.04·17 = 0.68`. The linear
`w_complexity·dim` was matched to the reference regime, where error spans ~0.7
over dims 1–8; at scale the same span stretches over dims 1–25 and the penalty
overwhelms it. Candidate principled fixes (need reference re-validation):
`w_complexity·log(dim)` (MDL-flavored), or an elbow-relative selection rule
(penalize only past the point of diminishing returns). `w_complexity` is exactly
the load-bearing [D] parameter the spec flagged.

## Recommendation (spec changes — decision, not yet applied)

1. **PRA-02 §1 (world):** `emit = tanh(E·latent / sqrt(true_dim/3)) + noise` —
   reference world byte-identical, scaled worlds stay in the validated tanh regime.
2. **PRA-01 §8 ([D] scaling rules, reference-preserving):**
   `learning_rate = 0.03·(10/obs_dim)` (≈0.005 at obs 60; 0.002 measured better —
   sweep the constant), and per-tensor `init_weight_scale = 0.3·sqrt(fan_in_ref/fan_in)`.
3. **Config:** scaled runs set `hidden_size ≳ true_dim` (e.g. `2·true_dim`).
4. **Open [D] research:** re-scale the parsimony term (log-dim or elbow-relative)
   so selection can claim the restored elbow; re-validate T1–T6 at the reference
   after any change.
5. **PRA-02 candidate:** add an identity-transition ablation to T3 (beat
   persistence, not just pull-to-zero), and consider a larger `action_scale` at
   scale so the dynamics signal is material.

After 1–3, re-run `pra-validate scan` (now a first-class command) and, once
parsimony is re-scaled, the live T-SCALE — expecting `best_dim` to track the
elbow rather than collapse to 1.

## 6. Implementation + first live results (2026-06-29, same day)

The recommendations were **implemented** as reference-preserving effective rules
(PRA-01 §8.8, PRA-02 §1.2/§1.3, Doc 07 §9; `src/pra/config.py` effective_*,
world normalization, fan-in init in `FrameGroup.add_frame`, `hidden_size =
2·true_dim` in the scale runner). The lr rule's exponent was refined to 1.5 by a
recipe probe (at `obs_dim=60`, `lr·(10/60)^1.5 ≈ 0.002` dominates the naive
`1/obs_dim` rule ≈ 0.005 at every scanned dim). Reference preservation was
verified bit-for-bit (seed-1 early/late/checkpoints identical to the validated
build) and the full 63-test gate is green.

**Live T-SCALE, default 50-cycle schedule** (13k steps/seed — far short of the
spec's millions):

| true_dim | best_dim per seed (was, before fixes) |
|---|---|
| 20 | [5, 5, 4] (was ≈1) |
| 35 | [3, 4, 3] (was ≈1) |
| 50 | [4, 5, 4] (was ≈1) |

The collapse is gone, but live selection lands well below the elbow the scan
proves recoverable (~12–22 at `true_dim=20`). Working hypothesis (the next open
question): **selection-ladder dynamics** — frames are born at dims 2–6 and climb
by ±1-ish proposals; each rung's candidate must out-score mature incumbents
within `min_age_cycles = 2` of protection while being drastically undertrained
relative to them; 50 cycles gives the ladder ~50 spawn opportunities for a
~10-rung climb. A lengthened schedule (which PRA-02 §3.3 prescribes for scaled
runs anyway) gives the ladder time; candidate-training-time scaling
(`min_age_cycles` growing with dim) is the follow-up lever if length alone is
insufficient. Long-schedule (1000-cycle) result: see below.

## 7. Layer 5 — maturation time (the fifth scale-variant constant)

**Schedule length alone does nothing:** 1000 cycles (20× the training, 240k
steps/seed) lands at exactly the same `[5, 5, 4]`. The ladder is not slow — it
is in a stable equilibrium. Mechanism: a candidate is evictable after
`min_age_cycles = 2`, but at the scaled learning rate its error is still on its
*transient* (score ≈ 0.85) far above its asymptote (≈ 0.44); eviction judges the
transient, so every high-dim candidate dies young. `min_age_cycles = 2` was
validated where convergence is ~15× faster — the *time axis* was scale-variant
too.

**Dose–response confirms the lever** (td=20, 500 cycles, 3 seeds):

| min_age_cycles | best_dim per seed | mean |
|---|---|---|
| 2 (raw) | [5, 5, 4] | 4.7 |
| 12 | [7, 5, 5] | 5.7 |
| 24 | [8, 7, 5] | 6.7 |

Selection climbs exactly as fast as candidates are allowed to prove themselves.
Candidate rule (same pattern as the others, factor 1 at reference):
`min_age_cycles · (obs_dim/10)^1.5 ≈ 29` at obs 60 — matching the lr rule's
time-scale inverse (training slows by the factor the lr shrank).

**Decisive run (patience 29, 2000 cycles, td=20, 3 seeds): `best_dim = [8, 18, 6]`.**
One seed climbed to 18 — **within-one of the true 20**. The ladder has no
equilibrium ceiling: given scale-matched patience and a long enough schedule, the
unmodified spawn-and-select mechanism reaches the world's dimensional elbow. The
climb is a slow, HIGH-VARIANCE stochastic search (the other seeds sat at 8 and 6
after 2000 cycles); full dose–response: patience 2/12/24/29 → mean 4.7/5.7/6.7/10.7,
max 5/7/8/18.

The rule is now **implemented** as `Config.effective_min_age_cycles` (the sixth
reference-preserving effective rule; factor exactly 1 at the reference) and
propagated to PRA-01 §8.8 / Doc 07 §9. **Conclusion of the diagnosis: every layer
of the collapse was calibration, not architecture. The remaining open frontier is
search *speed/variance* — the [O] proposal-policy seam (candidates that jump
toward promising dimensionalities instead of inching ±1), and/or longer
schedules, exactly where the design anticipated innovation would concentrate.

## 8. Closing measurement — the scaled reference result (2026-07-07)

Full T-SCALE with all six rules, 2000-cycle schedules, 3 seeds, 1.44M observation
steps per dimensionality (4.8 hours wall-clock total):

| true_dim | best_dim per seed | patience (auto) | throughput | wall |
|---|---|---|---|---|
| 20 | [8, 18, 6] | 29 | 31,788/s | 25 min |
| 35 | [8, 14, 10] | 69 | 21,808/s | 74 min |
| 50 | [8, 9, 10] | 116 | 14,694/s | 187 min |

No collapse at any scale; every seed finds multi-dimensional structure (recall:
all of these were ≈1 before the rules). The climbed fraction falls with scale —
the ladder covers a similar absolute number of rungs in a fixed cycle budget
because patience per rung grows while the budget doesn't. **Structure-finding
survives scale; its convergence rate does not.** That sentence is the research
finding this validation phase existed to produce, now recorded in PRA-02 §4
T-SCALE as the scaled reference result. The validation chapter is closed; the
successor problems are (a) the [O] high-dim proposal policy (make rung count,
not rung patience, the thing that shrinks) and (b) T3's persistence clause at
scale (untested there; the reference measurement is 6/8).

**8-seed confirmation (same day, parallel seed execution):** td 20/35/50 →
[8, 18, 6, 9, 8, 6, 13, 4] / [8, 14, 10, 11, 13, 8, 16, 10] /
[8, 9, 10, 11, 9, 9, 12, 10]; medians 8 / 10.5 / 9.5; minimum across all 24
runs = 4 (no collapse anywhere). The first three entries of each spread exactly
reproduce the 3-seed run — determinism visible in the data. Spread shape
sharpens the mechanism reading: **wide at td=20** (4–18; ~69 maturation windows
— the climb is a high-variance stochastic search) and **tight at td=50** (8–12;
~17 windows — uniformly window-starved). Parallel throughput 229k obs×frame
evals/s at td=20 (7× sequential); 24 runs in 3.1 h wall.

## Epilogue (2026-07-08)

Successor problem (a) was taken up the next day and produced its own trail:
`PROPOSAL-DIAGNOSIS.md`. Short version: an upward-only tight-band proposal
policy does make rung count shrink (~1 rung per maturation window, 2× the
fixed-budget median) — and, un-throttled, exposed the **seventh scale-variant
constant**: `survive_threshold_base` is an absolute bar that at scale sits
below the achievable at-maturity score of every dim past ~12, so the mature
niche is marginal-to-empty and the spreads above read the *maturation filter*
(which dims can train under the bar within one protection window), not the
score surface. The six rules above stand; the seventh is named and open.
