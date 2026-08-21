# Journey — factored-actions (started 2026-08-21)

## 2026-08-21 — the dial world declared, before the rig

The world implements the kernel's own `EventSource` seam
(`reset()/step(action)`, `pra/world/event_source.py`) — a lab world
in the T-suite tradition, seconds per run, no Minecraft. Declared
mechanics, v1:

- **State:** B dials, each in a position `p ∈ [0, m)`; one standing
  target pattern of B positions. Rungs: (B, m) =
  (3,4) / (8,8) / (16,16) / (32,32) → A = B·m ∈
  {12, 64, 256, 1024}.
- **Act:** flat index `a = d·m + p` = "set dial d to position p";
  deterministic snap. The product structure (dial × position) is the
  declared factorization — the stem × inflection miniature.
- **Observation** (`obs_dim = 3B`): per dial, three channels —
  its position scaled to [−1, 1], the target's position scaled the
  same, and a match flag (±1). At the calibration rung obs_dim = 9,
  beside the validated reference scale (10).
- **Reach:** when all B dials match the target, the target redraws
  (seeded); the redraw is the world's only novelty, so seeking
  matches is drive behavior, not reward — there is no reward wire,
  as everywhere. **Reach rate = redraws per 1,000 steps**, read on
  the back half of a run (the front half is the hungry-born
  transient of this world).
- **Held-out mask (F3):** a seeded 10% of acts is excluded from the
  policy's candidate set for the whole run; at test each is
  force-executed once from matched states and scored on
  first-execution prediction error.
- **Irregulars (F4):** a seeded 10% of acts (disjoint from F3's
  mask) snap dial d to a permuted position π(p) ≠ p — the
  compositional rule broken by exception, the is/was/went miniature.
  Off at calibration; on only in F4 arms.

**Ladder revision, before the rig exists (2026-08-21, same day):**
the declared ladder grew B and m together ((3,4)→(32,32)), which
confounds the axis under test — more dials is a longer assembly
horizon for ANY mechanism, so a reach collapse at A=1024 could be
horizon difficulty wearing the vocabulary's clothes. Revised:
**B = 4 dials at every rung, m ∈ {3, 16, 64, 256}** → A ∈
{12, 64, 256, 1024} exactly, obs_dim = 12 at every rung. Across the
whole ladder the world, the observation, and the task horizon are
identical; the single thing that changes is the size of the act
inventory. The factored anchor becomes `[onehot₄(d); p scaled]`,
dimension 5, constant across rungs. Nothing had run when this
revision landed.

**Calibration phase, declared:** flat at A=12 must first *perform*
on this world — one-step lookahead chasing redraws is not guaranteed
viable, and if flat-12 cannot work the world is miscalibrated, not
the kernel. The world may be revised openly during calibration (each
revision journaled here with its numbers); the moment flat-12
performs, the world config, the per-rung experience budget, and the
F0 parity thresholds freeze in this file, and **no comparison arm
run before that freeze counts** (the registered standing guard).
Machinery for the variant arms (shared transition conditioned on an
action vector; anchors `[structure of d ; scaled p]`; opt-in config;
off bit-exact) gets its own journaled entry when built — before any
variant arm runs.

## 2026-08-21 — the variant machinery declared, before it is built

The variant lives **rig-side, zero src changes** (the second-body
precedent, stronger here: the frozen suite cannot even see the
machinery). `rig/embed.py`: `EmbeddedFrameGroup(FrameGroup)`
replaces the per-action transition slices `T1 (F,A,H,D)` /
`T2 (F,A,D,H)` with bilinear forms over an action embedding
`e_a ∈ R^E` — `W1e (F,H,D,E)`, `W2e (F,D,H,E)`, biases likewise —
so parameters are O(E), every executed act trains the shared
tensors (the starvation axis under test), and similar acts share
gradients. The store subclass carries the event-head variant the
same way (`(E, obs, obs+1)` instead of `(A, obs, obs+1)`) and the
anchor table `e_a = [onehot₄(d); p scaled]` (E = 5): **frozen** arm
= table constant; **learned** arm = table receives gradient too.
Wiring: the rig rebinds the engine's module-level `FrameStore` name
for variant runs — instrument code, on the trail like every runner.

Declared self-test, built before any variant arm: with **one-hot
anchors (E = A)** the bilinear form reduces exactly to per-action
slice selection, so the embedded machinery must reproduce the flat
kernel's structure — the rig's internal parity check that the new
math is the old math when the embedding carries no structure.
Selection stays exact brute-force argmax (the Doc 06 seam decision:
no index until a profile demands one); F3's mask is a candidate
filter at the policy seam.

**Self-test result [measured]:** PASS — one-hot embedded equals flat
to machine precision after 200 interleaved updates (transition) and
300 (event head), all actions checked.

## 2026-08-21 — THE FREEZE: world, budget, and F0 thresholds, before any comparison arm

Calibration read at m=3 (A=12), 24 seeds each, one budget
[measured]:

| arm | reach/1k back-half: min / median / max | seeds reaching |
|---|---|---|
| flat (curiosity) | 8.308 / **12.615** / 17.077 | 24/24 |
| random floor | 5.385 / **6.923** / 9.385 | 24/24 |

Flat performs: median ≥ 1.5× the random median (12.615 vs 10.385
required) and flat's minimum seed (8.308) clears the random median —
the directed policy's whole distribution sits above the floor's
center. Frames' pred_error_late median 0.6423; populations alive
(median 6). The modest margin is the tiny inventory: at m=3 chance
assembles patterns often; the knowledge component of reach grows
with m, which is the ladder's whole point.

**Frozen, from this line on (no comparison arm before this counts):**

- **World:** the declared dial world v1 with the revised ladder
  (B=4; m ∈ {3, 16, 64, 256}; obs 12; reach = redraw; rejection
  redraw). No further world revision without a journaled amendment.
- **Budget:** 13,000 world steps per run (nominal n_cycles=18; the
  horizon-checkpoint floor of 50 effective cycles — measured
  identical across all 48 calibration runs). Same budget at every
  rung: at A=1024 that is ~12.7 executed acts per flat slice, the
  starvation regime F1 exists to read.
- **F0 parity thresholds (variant arms at m=3, 24 seeds):** PASS iff
  back-half reach median ≥ **10.385** (1.5× random median, the same
  clause flat met), minimum seed > **6.923** (random median, mirror
  of flat's own showing), and frames' pred_error_late median ≤
  **0.803** (1.25× flat's 0.6423).
- **F1 baseline:** flat's own A=12 reach median **12.615** — F1
  requires flat at A=1024 median < **6.31** (0.5×).
- **F2:** a variant at A=1024 retains ≥ 0.8× its own A=12 median.

Arm order, declared: F0 first (m=3 frozen + learned) — no larger
rung runs for a variant until its parity passes; flat's rungs
(m=16, 64, 256) may run any time after this freeze.

## 2026-08-21 — Bar F0: both variants PASS; the anchors help before they scale

Against the frozen thresholds (median ≥ 10.385, min > 6.923,
pred_late ≤ 0.803), 24 seeds each [measured]:

| arm | reach/1k: min / median / max | pred_late | F0 |
|---|---|---|---|
| flat (the calibration read) | 8.308 / 12.615 / 17.077 | 0.6423 | — |
| **frozen** | 11.538 / **14.462** / 21.077 | 0.5642 | **PASS** |
| **learned** | 8.308 / **10.615** / 12.154 | 0.5246 | **PASS** (median by 0.23) |

Two early readings worth naming. The frozen arm does not merely
match flat — its whole distribution sits above (worst seed 11.5 vs
flat's median 12.6): compositional anchors pay at twelve acts
already, where the shared tensors see every act's experience. And
the learned arm is WORSE than frozen here (10.6 vs 14.5): gradient
on an anchor table that was already correct is pure drift cost at
this scale — the 0091–0094 churn lesson showing up exactly where
theory put it. Whether learning earns its keep is F4's question
(exceptions), not this rung's. Both variants licensed to scale per
the declared order.

## 2026-08-21 — the middle rungs: the inversion, flat's collapse, and the ceiling that stays up

The m=16 (A=64) grid, 24 seeds each [measured]:

| arm | reach/1k: min / median / max | reaching |
|---|---|---|
| flat | 0.154 / 1.538 / 2.769 | 24/24 |
| frozen | 0.000 / **0.000** / 0.154 | 4/24 |
| learned | 0.615 / **1.846** / 3.077 | 24/24 |

**The m=3 picture inverts.** The frozen arm COLLAPSES at sixteen
positions: the hand-declared anchor (position as one scalar) makes
the effective transition linear along an axis the encoder's pose
geometry evidently is not, and with the table pinned nothing can
bend to fit. The learned arm — same anchors at birth, gradient on —
now LEADS the rung (median 1.85, every seed reaching, its worst
seed above flat's floor): learning the embedding earns its keep two
rungs before F4 was supposed to ask. Flat drops 8× from its own
m=3 reading (203 samples per slice). At m=64 (A=256) flat is
effectively dead [measured]: median 0.000, 8/24 seeds ever reach,
51 samples per slice — collapse two rungs before the registered
F1 test.

**The ceiling instrument** (perfect-knowledge oracle, trail):
370.0 / 267.1 / 254.2 / 251.1 median reaches per 1k at
m = 3/16/64/256, spreads within ±2%. One drop from m=3 (the
small-inventory luck component) and then **flat within 6% from
m=16 to m=256** — the world stays exactly as winnable while the
learners starve. Flat's collapse is knowledge starvation, not task
scaling.

## 2026-08-21 — the m=64 variants land: frozen is terminal, learned survives starving

The mid-ladder completes, 24 seeds each [measured]: frozen at m=64
reads 0.000 / 0.000 / 0.000 with **0/24 seeds ever reaching** — the
pinned-anchor collapse is terminal, not a dip. Learned reads 0.000 /
**0.308** / 0.923 with **21/24 seeds reaching** — starving (6× down
from its own m=16 while the ceiling holds flat) but alive where flat
is dead (8/24) and frozen is gone. The full mid-ladder ordering:
learned > flat > frozen from m=16 on, the exact inversion of m=3.

Read against the amended F2 honestly, before m=256 reports: learned
already sits far below 0.8× its m=16 anchor at m=64, so F2′ is
heading toward FAIL even for the survivor — the mechanism as built
buys *survival and relative advantage*, not retention, at the frozen
budget. The bar reads as registered when the 1024 rows land; no
re-anchoring. What the mechanism is actually worth then hangs on
Bar F3: predicting acts never taken, the property none of this
reach-counting can substitute for.

## 2026-08-21 — F3/F4 instrumentation built; the completable-target rule

Built while the m=256 F1/F2 chain runs, smoke-tested at m=3, no
special arm run yet: the seeded special sets (10% held-out, 10%
disjoint irregular with π(p) ≠ p, drawn from a dedicated stream),
`MaskedCuriosityPolicy` (held-out acts excluded from exploit argmax
AND the ε/immature random path — a masked act is never executed),
irregular effects in the world, store capture, and the probe
(event head primary when on, best-fit frame's decoded prediction as
trail, scored against the world's analytic truth from seeded states,
rejecting states where the act would complete the pattern and
randomize the truth).

The smoke caught a world bug worth the record: masking an act also
made targets REQUIRING it uncompletable — the world stalled chasing
impossible patterns (flat-3 masked: 7 reaches vs 132 unmasked), and
irregulars had the mirror problem (a position no act's real effect
lands on). **The completable-target rule, now part of the declared
F3/F4 world config:** per dial, the target pool is the image of the
allowed acts under their real effects; the plain world's pool is
untouched. Post-fix smoke: masked and masked+irregular arms run
healthy. Exact F3/F4 arm protocol (event-head eta, probe state
count, which arms) will be declared here before those arms run.

## 2026-08-22 — the top rung: F1 PASS, F2 FAIL both forms; the F3/F4 protocol declared

The A=1024 triple, 24 seeds each, the frozen 13,000-step budget
[measured]:

| arm | reach/1k: min / median / max | reaching |
|---|---|---|
| flat | 0.000 / **0.000** / 0.000 | **0/24** |
| frozen | 0.000 / 0.000 / 0.000 | 0/24 |
| learned | 0.000 / 0.000 / 0.308 | **9/24** |

**Bar F1 PASS** [measured]: flat at A=1024 reads 0.000 against the
6.31 line — total collapse at ~12.7 samples per slice, the
starvation premise confirmed at its registered site. **Bar F2 FAIL,
amended and original alike** [measured]: learned is the only arm
with any life at the top rung (9/24 seeds, max 0.308) but its median
is 0.000 against F2′'s 1.477 line. The registered reversal (F0+F2
failing for both variants) does NOT fire — F0 passed. The reach
story closes here: the embedding buys survival and relative
advantage at every scaled rung, never retention, at this budget.
What remains is the topic's substantial claim, which reach cannot
measure: prediction.

**The F3/F4 arm protocol, declared before those arms run:** event
head ON at the shipped operating point (η = 0.5, Doc 0011) in all
special arms; mask 10% with the completable-target rule; probe = 20
seeded states per act (completion states rejected), event-head MAE
against the world's analytic truth primary, best-fit frame's
decoded prediction as trail; per-act error arrays kept for the
registered per-seed pairing; a seeded 100-act regular sample per
seed as the reference error level. Arms at m=256, 24 seeds each:
**f3-flat** and **f3-learned** (mask only — the F3 pair; flat's
held-out slices are untrained by construction, its probe IS the
cold-start baseline); **f4-learned** and **f4-frozen** (mask +
disjoint 10% irregulars — the F4 pair, where a pinned anchor
cannot move to fit an exception and a learned one can).

**Amendment 1 — Bar F2's denominator, registered BEFORE any m=256
arm runs.** As registered, F2 normalizes the A=1024 reading to the
arm's own A=12 median. The numbers above show that anchor is
degenerate: the m=3 rung's reach is dominated by the luck component
the oracle exposes (ceiling 370 there vs ~253 everywhere else), and
every learning arm drops ≥ 6× crossing to m=16 while the ceiling
drops 1.4× — demanding 0.8× the m=3 reading at m=256 asks for
3.4% of ceiling from mechanisms whose best scaled showing is 0.7%.
The 0110 precedent (the degenerate ratio clause, floored pre-arm)
applies. **F2 as amended: at m=256, a variant's median reach ≥
0.8× its own m=16 median, valid only while the oracle ceiling at
m=256 is within 10% of its m=16 reading (measured: −6%, valid), and
flat at m=256 must fail the same retention.** The original F2 stays
on the record and will be reported at graduation beside the amended
form. Nothing at m=256 has run when this lands.
