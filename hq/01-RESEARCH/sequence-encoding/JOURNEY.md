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
