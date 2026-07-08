# Agency diagnosis — why directed curiosity hurts at scale

Date: 2026-07-08. Question under test: the scaled T7 measurement (PRA-02 §4)
showed directed curiosity is *systematically worse* than random exploration at
`true_dim=20` (mean margin −0.062 vs noninferiority bound −0.046, better in
1/8 seeds, 87% directed actions) while being statistically equivalent at the
reference scale. Why — and what is the principled remedy?

## Hypothesis (from the T7 mechanism reading)

With one-step lookahead, the learning-progress term is history-shaped and
near-constant across the 4 candidate actions, so action ranking is driven
entirely by the **novelty of the predicted next observation** — the policy is a
pure novelty maximizer. Predicted consequences at scale:

1. **Outward walk into saturation.** Maximizing unfamiliarity drives the hidden
   latent outward; pre-activations grow; the tanh emission saturates; the agent
   literally walks into the hard/unlearnable frontier faster than it can learn
   it. Observable proxy (no hidden-state leak): the fraction of observation
   components with `|obs| > tanh(2) ≈ 0.964` should be higher in the curious
   arm than the random arm, growing over the run.
2. **Dose–response.** The harm should shrink monotonically as
   `exploration_epsilon` rises (diluting directedness), reaching ≈0 at ε=1.0.

## Experiments

- **E1 — saturation telemetry** (4 seeds, curious ε∈{0.1,…,1.0} vs random):
  results below.
- **E2 — ε dose–response** (same runs): results below.
- **E3 — remedy candidates** (8 seeds, T7 noninferiority machinery), all
  injected through the shipped Drive/config seams with zero code changes:
  - *goldilocks*: novelty preference reshaped to peak at mid-unfamiliarity
    (`4·n·(1−n)` — the zone-of-proximal-development form);
  - *safety counter-drive*: unmodified curiosity **plus** a second fixed
    terminal drive `−2·max(0, novelty−0.5)` — Doc 05 §5's literal remedy ("a
    safety drive that penalizes states the system cannot predict at all"),
    combined via the multi-drive mechanism;
  - *ε=0.5*: stock curiosity, more random dilution (the dumb control).

## E1 result — the saturation hypothesis is REFUTED

Observation-saturation fraction (mean of 4 seeds, early vs late thirds):

| arm | sat early | sat late | late pred err |
|---|---|---|---|
| random | 0.575 | 0.574 | 0.425 |
| curious ε=0.1 | 0.574 | 0.570 | 0.523 |
| curious ε=0.4 | 0.573 | 0.571 | 0.472 |
| curious ε=0.7 | 0.572 | 0.575 | 0.451 |
| curious ε=1.0 | 0.576 | 0.575 | 0.438 |

Saturation is flat across arms and time — the curious agent does **not** walk
into saturated territory. In hindsight the outward walk is structurally
impossible: every 40-step episode resets the latent to an object start, so
there is no room to drift. Prediction 1 falsified; the harm is real (late
error 0.523 vs 0.425) but flows through another channel.

## E2 result — dose–response CONFIRMED

Mean T7 margin by exploration ε (4 seeds): **−0.094 → −0.043 → −0.023 →
−0.010** at ε = 0.1 / 0.4 / 0.7 / 1.0 (directed fraction 87% → 58% → 29% → 0%).
Monotone in directedness; ≈0 when fully diluted. Directed novelty-seeking *is*
the cause — the question is the channel.

## Revised hypothesis — the fit gate starves learning: also REFUTED (E3)

Prediction was a depressed `mean_map_fraction` in the curious arm. Measured
(8 seeds): curious **0.818** vs random **0.780** — the curious arm maps *more*,
not less. Gate starvation is not the channel.

## E3 result — reshaping the novelty preference does not fix it

T7 margins vs the random arm (8 seeds, noninferiority bound −1.9·SE):

| variant | mean margin | better | verdict |
|---|---|---|---|
| stock curiosity (ε=0.1) | −0.0620 ± 0.068 | 1/8 | FAIL |
| goldilocks `4n(1−n)` | −0.0607 ± 0.067 | 2/8 | FAIL |
| safety counter-drive `−2·max(0,n−0.5)` | −0.0607 ± 0.067 | 2/8 | FAIL |
| stock with ε=0.5 (dilution control) | −0.0216 ± 0.076 | 4/8 | PASS |

Notes: (a) stock reproduced the recorded scaled T7 margin exactly —
determinism visible through the experiment chain; (b) goldilocks and the
safety counter-drive are **order-isomorphic** (both rank candidates by distance
below/above n=0.5 symmetrically), so they select identical actions and produce
bit-identical runs — one experiment, not two; (c) the only PASS is heavy
dilution, i.e. *less directedness*, not *better directedness*.

## E4 result — walk-structure hypotheses REFUTED as well

| arm | action entropy (1=uniform) | mean episode walk extent |
|---|---|---|
| random | 1.000 | 7.72 |
| curious ε=0.1 | 0.998 | 7.92 |

The curious arm's *marginal* action distribution is essentially uniform and its
walks are barely longer (+2.6%). Every macro-statistic now matches the random
arm — saturation (E1), map fraction (E3, actually higher), action marginals and
walk extent (E4) — yet its late prediction error is far worse (0.523 vs 0.425).

## Remaining hypothesis — the state–action COUPLING itself

A directed policy makes the action a deterministic function of the state. Even
with uniform marginals, this couples *which action is trained where*
(partitioning each per-action transition model's data by the argmax regions)
and decorrelates the training stream relative to a random walk's naturally
redundant, locally-repeated data — plausibly degrading online SGD at a fixed
learning rate. Discriminating experiment (E5): (a) **anti-novelty** — same
coupling, opposite content; (b) **hash policy** — a content-free deterministic
state→action map (no lookahead, no drive, uniform-ish marginals). If the hash
policy fails like stock curiosity, coupling per se is the harm and no
preference reshaping can rescue the one-step lookahead; if it passes, the
novelty content is the poison.

## E5 result — coupling is harmless; the CONTENT is the poison

T7 margins vs random (8 seeds, same-batch random arm):

| policy | mean margin | late err (random 0.406) | verdict |
|---|---|---|---|
| stock (novelty-max) | −0.0620 ± 0.068 | 0.487 | FAIL |
| hash policy (content-free coupling) | +0.0139 ± 0.026 | 0.422 | PASS (neutral) |
| **anti-novelty (familiarity-max)** | **+0.0666 ± 0.070** | **0.358** | **PASS — better in 6/8** |

The decorrelation/coupling hypothesis is refuted (the hash policy is neutral),
and the harm gradient runs exactly along the novelty axis: novelty-seeking
−0.062, neutral +0.014, novelty-avoiding **+0.067**. Familiarity-directed
exploration is the first directed policy to *beat* random in this project.

## Conclusion

In this world — uniformly learnable, no unlearnable-noise regions, no hidden
treasure — spreading experience thin (novelty-seeking) is a pure cost, and
concentrating practice where the model already has data (familiarity-seeking)
is a pure gain for online SGD with fixed capacity and learning rate. The
one-step learning-progress term cannot arbitrate (it is constant across
candidates), so the lookahead's whole preference reduces to the novelty axis —
and at scale the profitable direction is the **competence** pole, exactly the
counter-drive design Doc 05 §5 anticipated ("rewards mastering — driving
prediction error low and keeping it low"). At the reference scale the axis is
flat (T7 equivalence), so nothing there is contradicted.

Honest caveats: (1) this is a property of the world as much as of the drive —
in worlds with unlearnable noise regions, pure familiarity-seeking risks the
camping degeneracy §5 warns about, and the curiosity/competence *blend* is the
open tuning question; (2) one-step lookahead remains myopic; predicted-LP
valuation would need a per-candidate learnability signal, a Doc 05 [O] design
question, not built.

## Remedy (implemented)

Ship the `CompetenceDrive` (id `"competence"`): value = mastery
(`max(0, 1 − recent mean pred error)`, the "keeping it low" reading) +
familiarity (`1 − novelty`, the per-candidate term that steers the lookahead),
registered in the drive registry so the scaled configuration is pure config —
`drive_weights=(("competence", 1.0),)` — with the base build's default
(curiosity-only) and every validated byte untouched.

**Verification (shipped drive, T7 machinery, 8 seeds, 87%/77% directed):**

| scale | mean margin vs random | bound | better | verdict |
|---|---|---|---|---|
| td=20 (obs 60, hidden 40) | **+0.0638 ± SE 0.0295** | −0.0560 | 6/8 | **PASS** |
| reference td=3 | **+0.0267 ± SE 0.0176** | −0.0335 | 6/8 | **PASS** |

The competence-directed agent beats random at BOTH scales — at the reference it
is positive where curiosity was merely neutral (−0.006). Implementation note
caught by the verification: the engine hands drives a `deque` history — the
first CompetenceDrive draft sliced it directly (TypeError, seeds silently
surfacing as failed); fixed and locked by a deque case in the unit test.
