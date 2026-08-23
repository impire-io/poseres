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
