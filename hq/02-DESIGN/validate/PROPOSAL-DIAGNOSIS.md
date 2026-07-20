# Proposal diagnosis — making rung count, not rung patience, shrink

Date: 2026-07-08. Question under test: SCALE-DIAGNOSIS §8 closed the scale
validation with its successor problem: in a fixed cycle budget the ±1-ish
selection ladder covers a similar absolute number of rungs at every scale
(patience per rung grows with `obs_dim`; the budget doesn't), so the scaled
reference stalls at `best_dim` medians 8 / 10.5 / 9.5 against `true_dim`
20 / 35 / 50. Can the **[O] proposal-policy seam** (PRA-01 §6.5) — the
component the design always expected to change at high dimensionality — raise
the climb *rate*, with no change to any other component?

## Hypotheses

- **H-A (proposal-limited).** The scale policy in force (`HighDimProposalPolicy`:
  exploit `+{0,1,2}` at p=0.75, explore `U[best, best+8]`) wastes maturation
  windows on candidates at or below the incumbent dimensionality; proposals
  concentrated *above* `best_dim` climb faster. Prediction: `best_dim` at a
  fixed budget rises as upward mass/reach grows.
- **H-B (survival-limited).** A candidate born far above the incumbent cannot
  out-score it within the patience window no matter how it was proposed
  (its training transient is judged against a mature incumbent), so jump size
  has a hard ceiling and proposals are not the binding lever. Prediction:
  flat or declining `best_dim` as jump reach grows.

## Experiment — in-vivo jump-size dose–response

Real engine, only the ProposalPolicy substituted (the seam's own guarantee),
`true_dim=20` (`obs_dim=60`, `hidden=40`, auto patience 29), **fixed 500-cycle
budget** ≈ 17 maturation windows — deliberately the window-starved regime that
`true_dim=50` occupies at full length (2000/116 ≈ 17), so a policy that wins
here attacks exactly the regime where the reference is stuck. Seeds 1–8,
identical across arms; medians and spreads read per the house rule.

**Round 1 — reach and concentration:**

| arm | proposal rule | best_dim per seed | median | max |
|---|---|---|---|---|
| band4 | explore `U[best, best+4]` | [7, 9, 7, 11, 6, 6, 6, 5] | 6.5 | 11 |
| control | explore `U[best, best+8]` (in force) | [6, 9, 5, 9, 7, 6, 7, 5] | 6.5 | 9 |
| band16 | explore `U[best, best+16]` | [7, 11, 8, 9, 6, 5, 7, 7] | 7.0 | 11 |
| band32 | explore `U[best, best+32]` | [10, 8, 6, 7, 6, 6, 7, 6] | 6.5 | 10 |
| uponly8 | exploit `+{1,2}`, explore `U[best+1, best+8]` | [10, 23, 7, 11, 5, 4, 15, 7] | **8.5** | 23 |
| geom | explore `best + 2^k`, k≤4 | [7, 4, 7, 5, 6, 6, 11, 6] | 6.0 | 11 |

Two readings, one per hypothesis:

1. **Reach is dead weight** (H-B confirmed *for far jumps*): quadrupling the
   explore band (+8 → +32) moves the median not at all. Candidates born far
   above the incumbent die on their transient, exactly as the maturation-window
   analysis predicts (SCALE-DIAGNOSIS §7).
2. **Waste is the lever** (H-A confirmed *for the near-above band*): the one
   arm that forbids proposals at or below `best_dim` — same maximum reach as
   the control — lifts the median 6.5 → 8.5 (better in 6/8 paired seeds) with
   climbs to 15 and 23. The control's exploit mass at `+0` and explore mass at
   `≤ best` re-tread rungs the incumbent already owns; every such spawn burns
   one of the ~17 windows.

Trajectory shape agrees: control seeds plateau by cycle 100–200 (e.g. seed 1:
8, 7, 6, 6, 6 at cycles 100..500); uponly8's climbing seeds are **still rising
at budget end** (seed 2: 6, 11, 13, 17, 23) — the ladder is windows-starved,
not equilibrium-stuck, under an upward-only proposal.

**Round 2 — how tight can the upward band be?**

| arm | proposal rule | best_dim per seed | median | max |
|---|---|---|---|---|
| **uponly4** | exploit `+{1,2}`, explore `U[best+1, best+4]` | [19, 20, 8, 18, 5, 7, 18, 6] | **13.0** | 20 |
| uponly8 | (round 1) | [10, 23, 7, 11, 5, 4, 15, 7] | 8.5 | 23 |
| uponly16 | exploit `+{1,2}`, explore `U[best+1, best+16]` | [21, 23, 4, 10, 6, 5, 21, 5] | 8.0 | 23 |
| pureup2 | always `+{1,2}` | [27, 23, 5, 12, 5, 5, 22, 6] | 9.0 | 27 |

The dose–response in band width is clean: 4 → 8 → 16 gives medians
13.0 → 8.5 → 8.0, and the no-band variant (pure `+{1,2}`) drops back to 9.0.
The sweet spot is a **tight just-above band**: every proposal in
`(best, best+4]`. At a budget where the old reference's best-ever median was
6.5, uponly4 puts **four of eight seeds at 18–20 — at or within-one of the
true dimensionality — in 500 cycles**, and beats the control in 7/8 paired
seeds. Versus pureup2, the +3/+4 explore jumps let the ladder skip rungs
without leaving the survivable crossing distance.

## Mechanism (what the grid establishes)

A spawned candidate can fail two ways: **re-tread** (born at ≤ best, it can
never displace the incumbent — a wasted window) or **overreach** (born too far
above, its transient loses to the mature incumbent at eviction — a dead
candidate). The in-force policy spent most of its mass on both failure modes.
The viable move is the narrow band just above the incumbent, `+1..+4` at this
scale — far enough to make progress, near enough that `patience ≈ 29` cycles
of training out-scores the incumbent's parsimony handicap. Selection dynamics
were never reach-limited; they were **waste-limited**.

## Honest caveats

- **Late system prediction error rises in climbing arms** (control 0.399 →
  uponly4 0.415, population mean over electing frames). This is a composition
  artifact, not degraded structure: a population that never stops climbing
  always carries fresh candidates on their transient, and the telemetry
  averages them in. The scan (SCALE-DIAGNOSIS §5) already established that
  *per-frame* honest error falls monotonically to the elbow as dim grows at
  equal experience.
- **Overshoot past the elbow** (23, 27 at `true_dim=20`): with no downward
  mass, `best_dim` can ride past the parsimony elbow before eviction corrects
  it. The recorded scan elbow at td=20 is broad (~12–22), so single-unit
  overshoot is within its width; the medians are the headline, and T4 at scale
  was never judged on exact equality.
- **Stalled seeds remain** in every arm (seeds 5/6/8 sit at 4–7): the climb is
  still a high-variance stochastic search; upward-only proposals raise the
  climb *rate* but do not remove the variance. 8 seeds; paired-seed reads
  quoted throughout.

## Full-scale confirmation — the screen was a lucky-horizon snapshot

Protocol: 2000-cycle schedules, td ∈ {20, 35, 50}, seeds 1–8, only the policy
substituted. Control = the recorded scaled reference (PRA-02 §4), re-certified
exact under this driver (td=20 seed 1 → `best_dim` 8, matching the recorded
spread's first entry bit-for-bit).

**td=20 result: `best_dim` = [71, 74, 9, 62, 7, 7, 68, 5]** (control:
[8, 18, 6, 9, 8, 6, 13, 4], median 8).

The climbing seeds did not stop at the truth — given 69 maturation windows
instead of the screen's 17, four seeds rode past `true_dim=20` to 62–74,
i.e. into `dim ≈ obs_dim` territory. The screen's "four seeds at 18–20" was a
**budget-truncated snapshot**: the climb happened to be passing the true
dimensionality when the 500-cycle horizon cut it off — precisely the v3/T4
failure mode this project's constitution exists to catch (judge across
horizons, not snapshots), caught this time by the confirmation protocol.

Two separate facts must not be conflated:

1. **The policy claim survives:** upward-only proposals in a tight band do
   raise the climb *rate* — roughly one rung per maturation window while
   climbing (≈ (74−5)/69 windows), versus the control's ~constant handful of
   rungs per budget. The waste-limited mechanism reading stands.
2. **The system claim fails:** with the climb un-throttled, `best_dim` tracks
   the **budget**, not the world. Selection is only "finding" the true
   dimensionality under the slow policy because the search never reaches the
   region where the score surface misbehaves. The scaled score surface —
   already suspect in SCALE-DIAGNOSIS §5 (pred err at dims 25/30 sat *below*
   the dim-18 "elbow"; layer 4 flagged the parsimony re-scale as open [D]) —
   has no minimum anywhere near `true_dim` under the effective parsimony
   `0.04·(10/60) ≈ 0.0067/dim`.

Also visible in the spread: the **early-lock-in bimodality**. Seeds either
climb from the first windows and never stop (62–74), or miss the early
crossings and freeze (5–9) — a young incumbent is beatable within one patience
window, a mature one is not, so the first few windows decide the whole run.

## Score-surface probe — the "no elbow at scale" hypothesis is REFUTED

`pra-validate scan` at td=20, hidden=40, dims 4–80, 600 train episodes, seeds
1–3. (The scan harness applies `cfg.learning_rate` raw while the live system
trains at `effective_learning_rate` — the effective value 0.00204 was passed
explicitly; instrument fix candidate.)

| dim | honest pred err | recon err | score (w/ parsimony) |
|---|---|---|---|
| 4 | 0.447 | 0.426 | 0.463 |
| 8 | 0.373 | 0.350 | 0.415 |
| 12 | 0.349 | 0.317 | **0.413 ← min score** |
| 16 | 0.340 | 0.294 | 0.424 |
| 20 | 0.336 | 0.269 | 0.436 |
| 24 | **0.335 ← min pred** | 0.257 | 0.456 |
| 30 | 0.346 | 0.239 | 0.493 |
| 40 | 0.360 | 0.232 | 0.563 |
| 50 | 0.373 | 0.228 | 0.634 |
| 60 | 0.378 | 0.221 | 0.699 |
| 70 | 0.386 | 0.222 | 0.770 |
| 80 | 0.391 | 0.228 | 0.843 |

The equal-experience score surface is **healthy**: a clean minimum at dim
12–16, honest prediction bottoming at 24 and *worsening* past it, and a dim-70
frame scoring 0.77 — nearly twice the elbow's 0.41. The live system crowned
dim-71/74 frames anyway. So the failure is not the score *surface* but the
score *measurement* in the live loop: live selection sees numbers the frozen
scan does not.

## Mechanism hunt 1 — "graded on the sample it just trained on": REFUTED

`FrameStore.online_step` updates `pred_err_ema` with `honest_pred_err` on
**post-learning weights** for the very transition the frame just trained on
(frame.py; the comment says so). Hypothesis: the one-sample deflation grows
with capacity and inverts the live surface. Direct probe (scan-style
training, per-transition error measured before and after the
`learn_transition` step, dims {8, 12, 20, 40, 70}, 3 seeds):

| dim | pred pre-learn | pred post-learn | score(pre) | score(post) |
|---|---|---|---|---|
| 8 | 0.284 | 0.265 | 0.327 | 0.317 |
| 12 | 0.279 | 0.262 | 0.340 | 0.332 |
| 20 | 0.292 | 0.278 | 0.388 | 0.380 |
| 40 | 0.331 | 0.317 | 0.527 | 0.520 |
| 70 | 0.364 | 0.344 | 0.740 | 0.730 |

The deflation is real but **flat (~0.02 at every dim)** and the post-learn
score keeps its minimum at low dim. Refuted as the channel — recorded because
the ordering is still a (small) self-grading wrinkle, but it does not explain
dim-74 winners.

## Mechanism hunt 2 — end-of-episode EMA sampling: REFUTED (for mature frames)

The live EMA (decay 0.9 ≈ last ~10 events) is read at consolidation, right
after an episode ends; a continually-learning frame adapts within the episode
to the current object, so late-episode error sits far below the across-episode
mean. Hypothesis: capacity buys context-tracking, context-tracking has no
elbow, and the EMA samples exactly the tracked regime. Probe (live-order EMA
simulated over the stream, read at episode ends, dims {8,12,20,40,70}, 3
seeds):

| dim | EMA@episode-end + parsimony | early-step err | late-step err |
|---|---|---|---|
| 8 | **0.271** | 0.385 | 0.203 |
| 12 | 0.294 | 0.363 | 0.210 |
| 20 | 0.349 | 0.365 | 0.233 |
| 40 | 0.493 | 0.402 | 0.279 |
| 70 | 0.702 | 0.424 | 0.302 |

Context-tracking is real (late-step error ≈ half the early-step error at every
dim) and end-of-episode sampling flatters *everyone* — but it does **not**
invert the elbow: the sampled score still worsens monotonically past dim 8.
No scoring channel makes a *mature* high-dim frame beat a mature low-dim one.

## Mechanism hunt 3 — the eviction arithmetic: nothing mature can survive

What the two refutations leave standing is a constraint, not a channel: with
effective parsimony `0.04·(10/60) ≈ 0.0067/dim`, a dim-74 frame carries a
0.494 complexity charge — **already over the population-30 soft threshold
(0.8/(1+0.04·26) ≈ 0.392) at zero error**. A mature dim-74 cannot legally
exist. Worse: even the best achievable mature score at this scale (dim 12,
honest ≈ 0.41 with parsimony) is **over the same threshold**. If the
population sits near ~30, *the entire mature population is evictable at every
cycle* — the ecology has no viable equilibrium, survival is youth protection
plus `min_frames`, and "best" is read from a rolling cast of protected young
transients whose EMAs still ride the `ema_init=0.9 → equilibrium` descent
(flattered further by the end-of-episode sampling above). Under a climbing
policy the conveyor is stocked exclusively with ever-higher dims — so
`best_dim` ratchets with the *proposals*, decoupled from the score surface
entirely. The control policy lives in the same churn but its conveyor is
stocked near the honest elbow, which is why it *looked* converged.

## The census — CONFIRMED: a two-caste ecology, and the climbed niche is empty

Instrument: the Doc 06 persistence seam (snapshot at the final cycle), dumping
every live frame's dim, age, EMAs, and survival score against the threshold in
force. td=20, 500 cycles, seeds 1–2, climbing policy vs control:

| run | pop | protected young | mature | best_dim read from |
|---|---|---|---|---|
| climbing, seed 1 | 29 | **29** | **0** | juvenile (dim 19, age 26, score 0.425 — over the 0.400 bar) |
| climbing, seed 2 | 29 | **29** | **0** | juvenile (dim 20, age 25) |
| control, seed 1 | 35 | 29 | 6 (all under bar) | **anchor: dim 6, age 343, score 0.233** |
| control, seed 2 | 33 | 29 | 4 (all under bar) | anchor: dim 9, age 31, score 0.330 |

The arithmetic is exact: 29 protected juveniles = `spawn_per_cycle=1` ×
`patience=29` — a standing conveyor that exists in **every** scaled run,
control included. The ecology has two castes: the conveyor, and a **marginal
mature niche** whose entry test is *score at age 29 under the absolute
population-scaled bar* (~0.36–0.40 here). In the control, only low dims —
which train fast and pay little parsimony — pass; once in, an anchor trains
for hundreds of cycles and becomes unassailable (0.233 at age 343). Under the
climbing policy the conveyor is stocked at dims ≥ 19 where the parsimony
charge alone (≥ 0.13) eats the headroom: **nothing ever matures**, `best` is
always a protected juvenile, and each window's proposals anchor on the last
best juvenile — a pure proposal-ratchet, decoupled from the world.

This also explains the stall/climb bimodality: a run stalls iff an early
candidate matures into an anchor before the conveyor outruns maturation;
past dim ~19 the ratchet can never be caught by an anchor again.

## Outcome — what this investigation actually found

1. **Original question (climb rate):** answered and standing. Selection at
   scale is waste-limited, not reach-limited; upward-only tight-band proposals
   (`ClimbingProposalPolicy`, every proposal in `(best, best+4]`) double the
   fixed-budget median and climb ~1 rung per maturation window.
2. **But the policy exposed a deeper defect it cannot ship past:** at scale
   the **maturation filter — juvenile score at `age = patience` vs the
   absolute survival bar — governs structure, not the score surface** (which
   the scan proves healthy: minimum at dim 12–16, dim 70 scoring 0.77). The
   scaled reference's `best_dim` medians measure *which dims can train under
   the bar within one protection window* — a speed filter that happens to
   correlate with the elbow at low dims. `survive_threshold_base = 0.8` was
   validated at `obs_dim=10`, where mature scores (~0.37) sit far under the
   pop-scaled bar (~0.65); at `obs_dim=60` the achievable juvenile score at
   maturity (~0.42+) sits **above** the bar (~0.36–0.40) for every dim past
   ~12 — the **seventh scale-variant constant**, in the same family as
   SCALE-DIAGNOSIS's six. Until the bar scales (a reference-preserving
   `effective_survive_threshold_base` rule is the natural candidate — factor
   exactly 1 at the reference, admitting the honest-elbow dims at maturity at
   scale), no proposal policy's scaled `best_dim` is a statement about the
   world.
3. **Refuted along the way** (all with data, above): "bigger jumps climb
   faster", "the scaled score surface has no elbow", "the pred EMA's
   post-learning grading inverts selection", "end-of-episode EMA sampling
   inverts selection".
4. **Instrument findings:** the scan harness trains at raw `learning_rate`
   while the live system uses `effective_learning_rate` (fix shipped with
   this investigation); the persistence seam doubles as a population census
   instrument (this document's decisive probe).

**Disposition:** `ClimbingProposalPolicy` ships as an opt-in variant (it is
the correct policy *once the ecology is fixed*, and the measurement instrument
that found the defect); the scale runner's default stays the wide-band policy
so the recorded scaled reference remains the honest baseline. The successor
problem, in priority order: the threshold scale rule (seventh), then re-ask
the proposal question on a functioning ecology.

## Full-scale confirmation appendix — budget-tracking confirmed at every scale

The pre-registered prediction (made after the td=20 reading, before 35/50
finished): under the climbing policy `best_dim ≈ birth + windows × rung-rate`,
irrespective of the truth. The full protocol (2000 cycles, seeds 1–8):

| td | windows (2000/patience) | climbing best_dim per seed | median | control median | truth |
|---|---|---|---|---|---|
| 20 | 69 | [71, 74, 9, 62, 7, 7, 68, 5] | 35.5 | 8 | 20 — **overshot 3×** |
| 35 | 29 | [34, 27, 26, 32, 29, 32, 28, 16] | 28.5 | 10.5 | 35 — "near" by coincidence |
| 50 | 17 | [19, 12, 22, 19, 14, 19, 16, 25] | 19.0 | 9.5 | 50 — far short, no overshoot |

One rate explains all 24 runs: **~0.8–1 rung per maturation window** (td=20
climbers: (68–74 − 5)/69 ≈ 0.9–1.0; td=35: (26–34 − 5)/29 ≈ 0.7–1.0; td=50:
(12–25 − 5)/17 ≈ 0.4–1.2). The td=35 reading is the cautionary exhibit: in
isolation, "median 28.5 against a truth of 35, up from 10.5" would have read
as a breakthrough — the budget simply ran out near the truth. Only the
three-scale protocol exposes that the number tracks the window count, not the
world. Note also: the stall/climb bimodality exists only at td=20 (3/8 stalled
seeds; anchors can still form there) — at td=35/50 every seed climbs (min 16 /
12), consistent with the census: the mature niche shrinks with scale, so
nothing anchors and the conveyor runs unopposed.
