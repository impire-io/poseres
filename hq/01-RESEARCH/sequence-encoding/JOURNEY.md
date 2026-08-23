# Journey — sequence-encoding (started 2026-08-23)

## 2026-08-23 — the echo-teacher world declared, before the rig

On the kernel's EventSource seam, continuous mode, the dial-world
run shape (engine curiosity policy, 24 seeds, ~13k-step budget
floor). Declared mechanics, v1:

- **Tokens:** m = 4; act = emit token (flat actions — A=4, the
  validated regime; vocabulary scale was 0112's question, not
  this one).
- **Targets.** R(P): a seeded template t₀…t₍P₋₁₎ over the m tokens;
  the world tracks phase j; emitting t_j advances, any other token
  is a violation (feedback pulse −1, j resets to 0); acceptance
  after T = 2P conforming tokens (phase must be carried ACROSS
  periods), then the template re-seeds — the redraw novelty. C(n):
  positions 0…n−1 expect token A, positions n…2n−1 expect token B
  (roles seeded from the inventory); acceptance at 2n re-seeds the
  roles.
- **The teacher's voice, in the observation:** a progress channel
  (j/T scaled to [−1,1]) and a pulse channel (+1 on the acceptance
  step, −1 on a violation step, 0 otherwise). Nothing else speaks.
- **Encoding channels per arm:** W-K — the subject's last K emitted
  tokens, scaled, zero-filled at stream start (obs K+2); DK — an
  m-channel recency sum s ← λ·s + onehot(token), λ = 0.5, reported
  as s·(1−λ) ∈ [0,1) (obs m+2); WD — window-4 plus the decay block
  (obs 4+m+2). The encodings are senses: the world computes them,
  the body declares them, the kernel is untouched.
- **Meters:** acceptance per 1k steps on the back half (the
  behavior meter); the RecordingPolicy-style feedback-prediction
  error on the pulse channel as the registered secondary reading.
- **Instruments:** oracle producer (emits t_j / the phase-correct
  role token; ceiling = 1000/(T+1) per rung shape), random floor.
  Both per rung, trail not bars.

Calibration (Q0) starts on R(2) with every encoding arm; the world
may be revised openly here — each revision journaled with numbers —
and freezes with the budget and all thresholds before any
comparison arm. The known risk, stated up front: reset-on-violation
makes random acceptance collapse fast with P (floor ≈ (1/m)^T per
attempt), so if no arm performs at R(2), feedback shaping (e.g., a
partial-credit progress pulse) is the declared first revision
candidate — teacher pedagogy, not kernel surgery.

## 2026-08-23 — Bar Q0 PASS; THE FREEZE: budget, pass rule, instruments-per-rung

R(2), 24 seeds per arm [measured]: curiosity arms W1/W2/W4/W8/DK/WD
read medians 10.0 / 19.7 / 19.8 / 12.0 / 12.0 / 15.7 accepts per 1k
(back half), every arm 24/24 seeds accepting, against a random
floor of 3.077 and an oracle ceiling of exactly 250 (its
arithmetic, zero violations). Every encoding performs; W2/W4 lead;
W8 already shows the width cost (channels without information); the
decay summary learns real structure with no positional window at
all. **Bar Q0 PASS.**

**Frozen from this line on (no ladder rung before this counts):**

- **Budget:** 13,000 world steps per run (nominal n_cycles=18, the
  checkpoint floor), every rung, every family.
- **The pass rule, per rung:** an arm PASSES a rung iff its median
  accept-per-1k (back half, 24 seeds) ≥ **max(3× that rung's
  measured random-floor median, 2.0 absolute)** — the absolute
  floor guarding degenerate 3×~0 floors (the 0110 lesson). An arm
  that does not pass, fails: Q1's two sides read against this one
  line.
- **Instruments per rung:** the random floor and the oracle
  ceiling run at every rung before or beside its arms; readings
  are trail, the floor feeds the rule.
- **World v1 frozen as declared** — no revision was needed;
  feedback shaping stays unused on the record.

## 2026-08-23 — Bar Q1 INVERTS: the wall is not the window; diagnosis open

The R-family ladder, 24 seeds per arm, frozen rule [measured]:
R(4) — every arm FAILS the 2.0 line (best: W2 at 0.462 median,
22/24 touching; W4, with a window wide enough by construction,
reads 0.0 median, 10/24); R(8) and R(16) — **0/24 for every arm**,
floors at 0.0, oracles at their exact arithmetic (125.1 / 62.5 /
31.2). W-K fails P ≤ K: the registered Q1-inversion clause fires —
the window arithmetic is not what binds, and no Q2/Q3 claim may be
made before the mechanism is diagnosed.

What the rows already show beneath the dark meter [measured]:
violations per step — random reads 0.750 at every rung (the
guessing arithmetic, 1 − 1/m, exactly); curiosity arms read
0.531–0.678 at every rung INCLUDING R(16). The kernel is learning
real structure everywhere; the acceptance meter demands 2P
consecutive corrects with reset-on-violation — fidelity exponential
in T — and partial competence reads as zero. The whole-obs
pred_late column cannot arbitrate encodings (it falls with obs
width and with violation-frozen worlds: W1 reads best everywhere for
the wrong reason); the registered pulse-channel reading needs a
per-channel instrument the rig does not yet carry.

Diagnosis in flight, one variable at a time: the budget
discriminator (W4/W2 at R(4), ~24k steps, 8 seeds) separates
"learning is slow" from "learning plateaus" — the amendment differs
accordingly (per-rung budget scaling vs a graded meter: violation
rate against its exact floor 0.750 and ceiling 0.0, plus the
pulse-channel prediction instrument). Any amendment lands here with
these numbers before any rung re-runs.

## 2026-08-23 — the diagnosis lands: plateau, not budget; width, not window — Amendment 1

The budget discriminator [measured]: at ~25,000 steps (≈2× budget),
W4@R(4) reads violations/step 0.654 vs 0.656 at 13k — unchanged —
and acceptance 0.04; W2 reads 0.575 vs 0.601, acceptance 0.68.
**Learning plateaus**; the budget is not the binder. And the width
reading holds everywhere: W2 beats W4 at R(4) on both meters, W1/W2
lead every rung, W8 trails every rung — **the kernel pays more for
observation width than it gains from positional sufficiency at this
scale.** Three measured facts now compose the diagnosis: the
acceptance meter demands exp(T) fidelity (partial competence reads
zero); learning plateaus at 0.53–0.68 violations/step; width
dominates information content in cross-arm comparisons.

**Amendment 1 — the instrument, registered with these numbers,
before any rung re-runs:**

- **Graded meter:** conformity = 1 − violations/step, exact floor
  0.250 (random's arithmetic), ceiling 1.0 (the oracle's measured
  zero). Acceptance stays reported where it reads (R(2), C(2)).
- **The pulse instrument:** a rig-side recording wrapper (the
  Minecraft RecordingPolicy pattern) captures the frames'
  per-channel one-step prediction error; the PULSE channel's error —
  anticipating the teacher's answer — is the encoding-information
  probe, independent of task completion.
- **Bars restated on the amended instrument, the width confound
  killed by design:** Q1′ — within-arm, cross-rung: W-K's pulse
  error rises from P ≤ K to P > K (same arm, same width, only the
  dependency grows past the window); Q2′ — DK (m+2 channels,
  unbounded horizon) beats W8 (K+2 = 10 channels, bounded) on pulse
  error at R(16) — narrower AND longer-horizon, both axes honest;
  Q3′ — the counting reading on pulse error at C(n), same
  within-arm and DK-vs-window comparisons. Exact thresholds frozen
  from the re-run's R(2) block before the ladder rungs are read
  (the standing pattern).

## 2026-08-23 — the counting family, original meter: the decay summary leads the structure it matches

C(2), 24 seeds per arm, frozen rule [measured]: every arm passes
(floor 3.077, oracle 250 exact) and **DK leads the whole field at
25.538** — above W2 (19.692) and W4 (18.769), 8.3× floor — while
the same DK placed mid-field on phase structure (12.0 at R(2)).
The count-holding encoding leads the count-requiring structure:
the first cross-arm encoding discrimination in the topic's data,
on behavior, before the pulse instrument even reads. W8's width
cost repeats (6.0); WD middles (10.0). C(4): dark for every arm
(best 0.615 against the 2.0 line, floor 0.000) — the T=8 meter
cliff exactly where the R(4) diagnosis put it; Q3 as originally
registered reads FAIL on acceptance, and the amended Q3′ pulse
reading is in flight.

## 2026-08-23 — THE PULSE FREEZE: R(2) baselines and the difference-in-differences clauses

R(2) record block, 24 seeds per arm [measured]: pulse-error medians
W1 0.2297, W2 0.2782, W4 0.3480, W8 0.3718, DK 0.2985, WD 0.3457 —
the width cost appears in anticipation too. Stated confound, on the
record before any claim: pulse dynamics are behavior-coupled (each
arm's own violations make its own pulse stream), so raw cross-arm
levels are not clean; every amended clause reads a CHANGE in
advantage or degradation, anchored at each arm's own R(2)/C(2)
baseline. Margin 0.03 ≈ half the R(2) seed-spread width, frozen.

**Frozen clauses (no ladder claim before this line):**

- **Q1′ (the window edge, within arm):** for W4 — [pulse(R8) −
  pulse(R4)] must exceed [pulse(R4) − pulse(R2)] by ≥ 0.03; for W8 —
  [pulse(R16) − pulse(R8)] must exceed [pulse(R8) − pulse(R4)] by
  ≥ 0.03. The degradation must STEP at the arm's own window edge,
  same arm, same width throughout. (W2's edge has no covered pair —
  trail only.)
- **Q2′ (beyond-window, phase):** DK's advantage over W8,
  A = pulse(W8) − pulse(DK), must satisfy A(R16) ≥ A(R2) + 0.03 —
  the narrower, longer-horizon sense must GAIN advantage exactly
  where the period outgrows every window.
- **Q3′ (beyond-window, counting):** [pulse(W4) − pulse(DK)] at
  C(4) must exceed the same difference at C(2) by ≥ 0.03.

## 2026-08-23 — Q3′ FAILS as frozen, and the failure names the instrument's limit

The counting pulse block [measured]: at C(2), DK's advantage over
W4 is 0.0522 (pulse 0.2437 vs 0.2959) — the largest cross-arm gap
in the data, matching DK's behavioral lead. At C(4) every arm's
pulse error COLLAPSES (W1 0.069, W2 0.060, DK 0.085, W4 0.088, WD
0.080, W8 0.199): a subject violating ~65% of steps makes a pulse
stream that is mostly "violation again" — trivially predictable.
Advantage growth reads −0.0497 against the +0.03 clause: **FAIL as
frozen**, with the mechanism visible: the behavior-coupling
confound named at the freeze does not tint hard rungs, it DOMINATES
them. Anticipation probes cannot arbitrate encodings across gross
behavior differences; they read cleanly only at comparable
competence — where DK's counting advantage is real [measured].
Q1′/Q2′ read next against the same expectation when the R(8)/R(16)
block lands; the same collapse mechanics likely apply, and the
clauses read as frozen either way.

## 2026-08-23 — Q1′/Q2′ read; the topic's measuring is done

The R(8)/R(16) pulse block [measured]: every narrow arm collapses
to ~0.12 at hard rungs (the trivial-stream artifact, as at C(4));
W8 alone stays high (0.29). **Q1′ FAIL as frozen** — no window-edge
step is visible through the collapse (W4's apparent step-excess is
the artifact's sign; W8's is negative). **Q2′ PASS as frozen** —
DK's advantage over W8 grows +0.1001 (0.0732 → 0.1733) against the
0.03 clause — with the interpretation caveat stated: the growth
measures width-under-load at least as much as horizon, since W8 is
the one arm the collapse does not make trivially predictable. No
further instrument editions: a third probe fitted to these
dynamics would be instrument-fishing, and the world has said what
it can say.
