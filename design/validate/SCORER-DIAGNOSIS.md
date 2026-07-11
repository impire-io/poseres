# Scorer diagnosis — can the basin be made informative?

Date: 2026-07-11. Question under test: INTERAGE-DIAGNOSIS established that
the scaled `best_dim` landing is set by a **flat score basin** (span ≈ 0.02
across dims 6–16 under the fair judge; the frozen surface is similarly flat
12–16), so selection has no gradient toward the honest optimum. The open [D]
question flagged since SCALE-DIAGNOSIS layer 4: parsimony vs marginal
information — re-shape the score so the basin is informative, or establish
honestly that it cannot be.

## The fork, pre-registered

The basin's flatness has two candidate causes with opposite remedies:

- **F-A (experience-limited).** The marginal one-step predictive value of
  dims beyond ~10–16 is real but unlearnable at the measured budgets (600
  episodes; transition parameters grow ~dim², and the scaled learning rate
  shrinks the effective sample count). Prediction: with 4× and 16× training,
  the honest error minimum moves toward `true_dim` and the basin deepens.
  Consequence: the scorer needs **no redefinition** — `best_dim` is the
  budget-optimal dimensionality, an honest and defensible quantity; the
  frontier becomes making the *ecology* track the deepening basin as anchors
  accumulate lifetime experience (entry-at-maturity is then the binding
  filter to re-examine).
- **F-B (signal-saturated).** One-step prediction error at the sensor noise
  floor genuinely cannot distinguish dim 12 from dim 20 in this world, at any
  budget. Prediction: the minimum and the basin shape barely move at 16×.
  Consequence: parsimony reshaping (log-dim) cannot help — it re-tilts a
  flat surface; the honest levers are **elbow-relative selection** (pick the
  smallest dim within ε of the best error — a selection-rule change, robust
  to flat basins) or a longer-horizon prediction target (a deeper Doc 03
  change); and "`best_dim` ≈ `true_dim` at scale" is recorded as unreachable
  under one-step scoring.

## E1 — experience dose–response of the honest surface

`pra-validate scan` (frozen judge, effective lr), td=20, hidden=40, dims
4–32, seeds 1–3, `train_episodes ∈ {600, 2400, 9600}` (600 = the recorded
THRESHOLD-DIAGNOSIS baseline: pred min at 24, score min at 12, basin span
~0.01 across 8–16).

**At 2400 (4×) — the error surface is experience-limited, the score surface
is parsimony-pinned:**

| dim | pred | recon | score |
|---|---|---|---|
| 8 | 0.310 | 0.290 | 0.353 |
| 12 | 0.284 | 0.258 | **0.351** |
| 16 | 0.265 | 0.233 | 0.356 |
| 20 | 0.254 | 0.212 | 0.366 |
| 24 | **0.249** | 0.197 | 0.383 |
| 28 | 0.249 | 0.183 | 0.403 |

The pred minimum moved 24 → 28 and deepened everywhere (dim-20 pred
0.335 → 0.254) — F-A's error-side prediction confirmed. But the **score**
minimum stays at 12: the marginal error gain 12→20 grew from 0.031 (600) to
0.038 (2400) while the linear parsimony charge is 0.053 — the charge wins at
every measured budget, and the trend suggests it keeps winning at the
asymptote. The basin question is a parsimony-shape question after all.

**At 9600 (16×) — a new finding jumps the queue: long-horizon training
degradation.** Consistent across all 3 seeds, dims 8–24 roughly double their
error vs 2400 (dim 8: 0.31 → 0.49; dim 20: 0.25 → 0.53) while dim 32 keeps
improving (0.256 → 0.230):

| seed | pred err by dim (4 / 8 / 12 / 16 / 20 / 24 / 28 / 32) |
|---|---|
| 1 | 0.32 / 0.47 / 0.50 / 0.50 / 0.50 / 0.55 / 0.50 / **0.24** |
| 2 | 0.43 / 0.58 / 0.49 / 0.53 / 0.58 / 0.59 / 0.62 / **0.24** |
| 3 | 0.39 / 0.43 / 0.46 / 0.47 / 0.52 / 0.52 / 0.22 / **0.21** |

For a system whose premise is *continuously-learning, never
trained-then-frozen*, mid-capacity frames rotting under constant-lr continual
training is more important than the basin that motivated this arc. The fork
gains a third branch:

- **F-C (stability-limited):** past some lifetime, constant-lr SGD leaves its
  stable regime (candidate mechanism: slow weight growth → saturation /
  oscillation) — an *eighth-rule-class* problem (lifetime lr schedule or
  weight control), and a caveat on live anchors' longevity (the E4′ censuses
  show healthy old anchors, but through the eviction filter — survivor bias).

## E2 — longevity probe: the mechanism is weight-norm runaway

Frozen honest eval + total weight norm every 400 episodes to 9600, dims
{4, 12, 20, 32}, seeds 1–2. The signature is exact and replicated:

- **dim 20** (both seeds): error bottoms at ~0.22–0.24 around 2400–4800
  episodes while |W| *compresses* (20 → 18 — the healthy phase); then |W|
  turns and grows monotonically (18 → 27–29) while error climbs to 0.45–0.57.
  The error turn and the norm turn coincide.
- **dim 12**: same pattern, onset similar, |W| 16 → 22–25, error
  0.25 → 0.40–0.55.
- **dim 32**: |W| decreases monotonically (25 → 21); error still improving at
  9600. No rot.
- **dim 4**: |W| creeps (11 → 14); error noisy-flat — mild to no rot.

**Onset ≈ 2400–4800 episodes (≈ 400–800 live cycles) at `obs_dim = 60`,
capacity-dependent** (mid dims rot; the largest and smallest largely do not).

## The live system has been living with this

The E4′ censuses, reread against the rot profile: td=20 anchors sit at dims
4–8 — precisely the rot-resistant dims — with scores 0.28–0.42 at ages
≈ 2000 cycles (12,000 episodes, deep in the rot zone for dims 10–24). At
td=35/50 the smaller effective learning rate delays onset roughly past the
run length, and the anchors are visibly healthier (0.21–0.26). The causal
chain, now with every link measured:

**constant-lr weight runaway → mid-dim rot after ~400–800 cycles → long-run
selection favors rot-resistant low dims → the scaled landing at 6–8 and its
slow downward drift with budget.**

This retro-explains, without contradicting, the two prior arcs: the INTERAGE
basin (measured at 600 episodes — pre-rot) is genuinely flat *there*, but the
long-run landing is rot-driven selection, not basin-edge settling; and the
"inter-age drift" is the rot differential compounding.

## Outcome

1. **The scorer question's honest answer: it is downstream of the rot
   question.** The score minimum is parsimony-pinned at every measured
   budget (the linear charge outruns the marginal error gain), but no
   parsimony reshaping is worth doing while mid-capacity frames rot out of
   the contest after 400–800 cycles. Fix lifetime stability first, then
   re-measure the basin — the landing may resolve upward on its own.
2. **The eighth-rule-class successor, named: lifetime stability.** The
   measured mechanism (norm runaway after a healthy compression phase)
   suggests a reference-preserving, premise-preserving candidate:
   **per-tensor max-norm control** — a cap safely above all reference-scale
   excursions (dormant at the reference and during any frame's healthy
   phase; byte-identity preserved), engaging only in the runaway regime,
   constraining magnitude while leaving ongoing adaptation free (no
   freezing; the system stays never-trained-then-frozen). Alternatives
   (per-age lr decay = gradual freezing) trade against the project's
   continual-learning premise and are second choices.
3. `best_dim ≈ true_dim` at scale remains out of reach under one-step
   scoring even absent rot (the 2400-episode surface's parsimony arithmetic);
   whether to re-shape parsimony is deferred until a rot-free re-measurement
   exists.

## Epilogue — the rot-free re-ask: nothing marks the truth, and that is the answer (2026-07-11)

With the LONGEVITY cap in force (rot eliminated), the long-experience
equal-experience surface at td=20 (dims 4–40, 19,200 episodes, frozen honest
eval, 2 seeds):

| dim | pred (s1/s2) | recon (s1/s2) |
|---|---|---|
| 12 | 0.268 / 0.278 | 0.247 / 0.259 |
| 20 | 0.255 / 0.256 | 0.223 / 0.227 |
| 28 | 0.218 / 0.231 | 0.179 / 0.195 |
| 40 | **0.202 / 0.212** | **0.146 / 0.157** |

Both components decrease **monotonically to the capacity ceiling**
(dim 40 = hidden width), in both seeds, with near-constant marginal gain
≈ 0.003/dim from 12 to 40. The world's intrinsic dimensionality (20) leaves
**no signature on either error surface** — plausibly inherent: under the
nonlinear tanh emission, the latent's image is not a 20-dim linear object,
so no pose dimensionality "completes" it below capacity. Consequences:

1. **No parsimony shape can recover "best_dim = true_dim"** — there is no
   feature for any penalty to select. Reshaping (log-dim, elbow-relative) is
   pointless here and is dropped.
2. **The linear penalty is a *price*, not a truth-finder.** Selection buys
   dimensions while the marginal error gain exceeds `w_complexity`
   (effective 0.0067/dim at obs=60). The measured marginal gain crosses that
   price at dims ~8–12 — and the capped ecology's landing is median 10:
   **selection already sits exactly at the operating point the price
   implies.** The three-legged ecology is faithful to the score's economics.
3. **T-SCALE's question is answered by retirement.** "Does best_dim track
   true_dim at scale" assumed a signature the world does not emit. The honest
   successor question — "does selection land at the price-optimal
   dimensionality, stably, at every scale and budget" — is what the fixed
   ecology now demonstrably does. Raising `w_complexity` buys smaller
   structure; lowering it buys error; the choice is a deployment economy,
   not a discovery.

(Reference-scale T4 is untouched: at td=3/obs=10 the surface does have a
knee near 3 — small worlds under mild nonlinearity still mark their
dimensionality; the scaled worlds do not.)
