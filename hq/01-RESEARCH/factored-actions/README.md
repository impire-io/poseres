# Factored actions — can the action side carry a vocabulary, and predict acts it has never taken?

**State:** active
**Started:** 2026-08-21

## Abstract

The language gate (episode 0042) named three prerequisite decisions;
this topic runs the second: factored/embedded actions for realistic
vocabularies. The kernel's action side is flat — per-action
transition tensors (`T1 (A,H,D)`, `T2 (A,D,H)` per frame), a
per-action event head (`A × obs_dim × obs_dim+1`), O(A) argmax
enumeration, and index-gated learning where an executed act trains
only its own slice, so per-act experience scales as 1/A. Validated
up to A=13; language needs A ≈ 10³ single emissions, where memory,
selection cost, and above all per-slice data starvation are expected
to fail. The candidate mechanism, refined in the owner conversation
of 2026-08-21: **action embeddings initialized at factored anchors**
— one shared transition conditioned on a learned action vector,
whose initial geometry comes free from declared product structure
(dial × position; stem × inflection), with learning free to move
exceptions off their anchors (the is/was/went regime). A decisive
answer either makes the teacher-world experiment runnable on its
action side, or gives 0042's plateau prediction its first measured
support — either outcome moves the vision. Owner's direction:
substance before showcase.

## The question

Can the kernel's action side carry ~10³ acts — via action embeddings
initialized at factored anchors, learning on or off — matching flat
where flat is validated, retaining its own performance where flat
starves, and predicting the consequences of acts it has never
executed?

## The arms

The three arms differ by exactly one thing — whether structure is
learned:

| arm | transition | structure |
|---|---|---|
| **flat** | current kernel, per-action slices | none (the baseline that must break) |
| **factored-frozen** | shared, conditioned on action vector | embeddings pinned at compositional anchors, never trained |
| **embedded-learned** | shared, conditioned on action vector | same anchors as init, learning on |

Everything the frozen arm can do came free from declared structure;
everything the learned arm does beyond it is what learning earned.
Parsimony rules: if frozen matches learned everywhere, the cheaper
mechanism wins.

## Pre-registered bars

Common protocol: the **dial world** — B dials × m positions, act =
"set dial d to position p" (A = B·m), observation = dial states +
target pattern, deterministic ground truth, no Minecraft. Vocabulary
ladder A ∈ {12, 64, 256, 1024} (3×4, 8×8, 16×16, 32×32). 24 seeds
per arm; spreads, never bare means. One experience budget per rung,
identical across arms. The world's exact mechanics, the budget, and
the F0-derived thresholds are frozen in JOURNEY.md at the end of the
calibration phase, **before any comparison arm runs** (the 0110
pre-arm pattern); a comparison arm run before its thresholds froze
does not count. All new machinery is opt-in; flat is the default;
off is bit-exact, RNG stream included; the frozen T1–T6 suite is
untouched (constitution I).

- **Bar F0 — parity where flat is validated:** at A=12, each variant
  arm matches flat on target-reach rate and prediction error within
  the seed spread (exact clauses frozen at calibration). New
  machinery may do no harm at the scale the kernel already owns.
- **Bar F1 — the premise is real:** flat at A=1024, at the frozen
  budget, retains < 0.5× its own calibrated A=12 reach rate. If
  flat holds, no machinery is licensed — the topic closes carrying
  the negative result and the 10³ premise dies.
- **Bar F2 — the mechanism carries (headline):** at A=1024, a
  variant arm retains ≥ 0.8× its own A=12 reach rate at the same
  frozen budget where flat fails F1.
- **Bar F3 — unseen acts (the substantial claim):** a registered
  10% of acts (drawn per seed) are masked from selection during
  training, then force-executed once each from matched states. The
  variant's median first-execution prediction error over held-out
  acts is ≤ 0.5× flat's cold-start baseline, and beats it on ≥ 80%
  of held-out acts, paired per seed. Flat's slice for an unexecuted
  act is untrained by construction — any transfer is structure the
  mechanism added. This is the property language requires.
- **Bar F4 — exceptions without wrecking the lawful (the verb
  probe):** a registered 10% of acts (drawn per seed, disjoint from
  F3's mask) have exceptional consequences that break the
  compositional rule. The embedded-learned arm's final prediction
  error on irregular acts lands within 2× its regular-act error
  while its F3 clause on regulars still passes. The frozen arm is
  expected to fail this bar (its anchors cannot move); if frozen
  passes too, learning earned nothing and parsimony takes the
  verdict.

Instrument readings, trail not bars: snap-fidelity (fraction of
selections where nearest-anchor lookup equals exact argmax — exact
brute-force is the referee, per the Doc 06 seam decision: no vector
index until a profile demands one) and embedding drift (anchor
displacement over training, regulars vs irregulars — the 0091–0094
churn lessons watching the new learned representation).

## Reversal condition

- **F1 fails** (flat does not break at 10³ under the frozen budget):
  the starvation/enumeration premise is refuted at this scale; no
  machinery is licensed; the language gate's action prerequisite
  closes with "flat suffices at 10³" and reopens only at a larger
  registered scale.
- **F0 + F2 fail for both variants** (no mechanism both preserves
  validated-scale behavior and survives 10³): the kernel's action
  side cannot carry a vocabulary by factoring or embedding; episode
  0042's pre-registered plateau prediction gains its first measured
  support on the action axis; hierarchical action/frame research
  becomes the named next gate; the topic graduates abandoned with
  the numbers.
- Standing guard: no comparison-arm claim enters JOURNEY.md unless
  its thresholds were frozen before the arm ran; instrument readings
  (snap-fidelity, drift) are trail and carry no bar weight.

## Verdict

Graduated **to design**, 2026-08-22, on the owner's call — neither
registered reversal fired; the topic closed with its bars read and
its mechanisms mapped. Design
[0019](../../02-DESIGN/0019-factored-actions.md).

- **Bar F0 — PASS for the licensing arms** [measured]: frozen-v1
  14.462, frozen-v2 15.538, learned-v1 10.615 against the frozen
  10.385/6.923/0.803 clauses. Learned-v2 (10.154) and learned-v3
  (10.308, anchor lr 0.001) FAIL the median clause — three editions
  bracketing one line while every frozen sibling reads 14.5–15.5:
  the mobility wall. Even near-zero anchor movement costs parity in
  a lawful world [measured, three editions].
- **Bar F1 — PASS** [measured]: flat at A=1024 reads 0.000 (0/24
  seeds, ~12.7 samples per slice) against the 6.31 line. The
  per-action kernel cannot carry a vocabulary at this budget.
- **Bar F2 — FAIL, original and amended, every arm** [measured]:
  best top-rung showing learned-v1's 9/24 seeds at max 0.308,
  median 0.000 vs the amended 1.477 line. The embedding buys
  survival and relative advantage (learned > flat > frozen from
  m=16 on), never retention.
- **Bar F3 — FAIL as registered, both editions; the property
  measured in v2** [measured]: v1 read 2.49× WORSE than cold —
  diagnosed as rank, not starvation (the linear-in-embedding family
  over [onehot(d); p] spans rank B+1 where the world's action
  family needs 2B [mechanism-argument, corroborated by the v1 F4
  pair's uniformly flat errors]). v2 (the product anchor
  [onehot(d); onehot(d)·p]): held-out 0.0409 ≡ regular 0.0414 ≈
  flat-trained 0.0375 — an untried act predicts exactly as well as
  a practiced one — at 0.779× cold with 86% median per-act wins,
  against clauses (0.5×, 80% every seed) that flat's own trained
  slices (0.69× cold) could not pass: measured overreach in the
  registered margin, reported, not amended post-hoc.
- **Bar F4 — BLOCKED** [measured]: no mobility edition passed the
  F0 gate the declared order requires; the v1 pair rode as trail
  and read uniformly blind (irr/reg 1.00–1.09), as the rank cap
  predicts. The mobility–parity tension is the finding;
  surprise-gated anchor movement is the named door.

Load-bearing claims: per-act experience starves as 1/A and kills
flat exactly on schedule [measured]; **the interaction term is what
"factored" means** — concatenated slot+value anchors are provably
rank-deficient, product anchors span the family exactly
[mechanism-argument + measured]; **structure transfers completely**
— never-executed ≡ constantly-executed under exact anchors
[measured]; prediction and behavior dissociate — the arm that
predicts perfectly wins no races, and reach correlates with
learning-on, not anchor quality (jitter-as-exploration hypothesis
[judgment], discriminator named, unrun); margins for generalization
bars must be set against trained-knowledge ceilings, not cold
baselines [measured — the F3 lesson]. Confounds as journaled: one
world geometry; the oracle-flat ceiling from m=16 up; 13,000-step
budget frozen throughout.
