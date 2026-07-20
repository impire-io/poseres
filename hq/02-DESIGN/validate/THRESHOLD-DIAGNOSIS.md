# Threshold diagnosis — the seventh scale rule (the survival bar)

Date: 2026-07-10. Question under test: PROPOSAL-DIAGNOSIS established that at
scale the absolute survival bar (`survive_threshold_base`, Doc 04 §5.3) sits
below the achievable at-maturity score of every dim past ~12, so the mature
niche is marginal-to-empty, selection is governed by the maturation filter
rather than the (healthy) score surface, and `best_dim` under a fast proposal
policy tracks the budget rather than the world. Design the
**reference-preserving effective rule** for the bar (PRA-01 §8.8 pattern:
factor exactly 1 at `obs_dim = 10`, dependent only on quantities the system
can see — never `true_dim`), verify with the census instrument that the
mature niche reopens, and re-ask T-SCALE with `ClimbingProposalPolicy` on the
functioning ecology.

## What the bar must do (from the census evidence)

At the reference (`obs_dim = 10`): mature scores ≈ 0.23–0.37 sit far under
the pop-scaled bar (≈ 0.65 at typical populations) — a wide mature niche; the
bar's only job is rejecting junk. At `obs_dim = 60`: the bar at realistic
populations is 0.36–0.40 while elbow-dim candidates (12–24) reach ≈ 0.42–0.48
by the end of their protection window — the niche admits only dims ≲ 12. The
rule must restore the reference *relationship* (bar comfortably above the
at-maturity score of elbow-dim candidates, below junk), while keeping T5's
self-limiting property: a bar too generous admits everything, and the
population runs to the hard cap.

Success signature, pre-registered: with the rule in force and the climbing
policy un-throttled, (i) the census shows a populated mature niche at the
elbow dims with long-lived anchors, (ii) the `best_dim` ratchet **stalls at
the score-surface elbow** instead of tracking the window budget, (iii) the
population stays self-limited well below `max_frames`.

## Experiments

- **E1 — elbow position per scale** (`pra-validate scan`, now training at the
  effective learning rate, at td=35/hidden=70 and td=50/hidden=100, 600
  episodes, 3 seeds): where *should* selection land at each scale, and how
  does the achievable score floor move with `obs_dim`?
- **E2 — bar dose–response in vivo** (climbing policy, td=20, 500 cycles,
  seeds 1–8, `survive_threshold_base = 0.8·f`, f ∈ {1.0, 1.25, 1.5, 2.0},
  census in every run): which factor reopens the niche without unbounding the
  population? The winning factor at `obs_dim = 60` fixes the exponent of the
  candidate form `0.8·(obs_dim/10)^p` (p = ln f\*/ln 6).
- **E3 — reference preservation**: structural (factor 1 at the reference);
  guarded by `tests/integration/test_baseline_unchanged.py` and the full gate.
- **E4 — the re-ask**: full T-SCALE (2000 cycles, seeds 1–8, td 20/35/50)
  with the rule + climbing policy, census per run, judged against E1's
  elbows — the first scaled `best_dim` reading that can say something true
  about the world.

## E1 result — the elbow does NOT track the truth at scale

| scale | score minimum | honest-pred minimum | flat region (pred, ±σ) |
|---|---|---|---|
| td=20, obs=60, hidden=40 | dim 12 (0.413) | dim 24 (0.335) | 16–30 |
| td=35, obs=105, hidden=70 | **dim 16** (0.374) | dim 16 (0.338) | 16–32 |
| td=50, obs=150, hidden=100 | **dim 16** (0.378) | dim 16 (0.360) | 12–32 |

At 600 episodes of equal experience, honest prediction error flattens past
dim ~16 at every scale: the marginal predictive value of dims beyond ~16 is
smaller than the effective parsimony charge, so the scorer's own optimum sits
at 12–16 **regardless of whether the world has 20, 35, or 50 dimensions**.

Two consequences, recorded before E2/E4 to keep the criteria honest:

1. **The pre-registered E4 target changes meaning.** A faithful selection
   ecology lands at the score-surface minimum (~12–16 everywhere) and stalls;
   it does not — and under this scorer *should not* — track `true_dim`.
   Whether the scorer ought to value the world's full dimensionality more
   (parsimony weight vs marginal information at scale) is a legitimate open
   [D] question for Doc 03 §6 — a *different* investigation. This one makes
   selection faithful to the surface it has.
2. The old maturation-filter medians (8 / 10.5 / 9.5) were below even these
   elbows — the filter binds at ~8–12, under the surface's own optimum, at
   every scale.

Also relevant to the rule: the achievable elbow score barely moves with scale
(0.41 / 0.37 / 0.38 — patience grows superlinearly, so bigger-scale
candidates arrive at maturity better-trained against a flat error floor),
while the bar (0.36–0.40 at typical populations) is scale-blind. The needed
correction factor at `obs_dim=60` may therefore be modest (~1.2–1.5) and
roughly flat-to-slowly-growing in `obs_dim` — E2 measures it directly.

## E2 result — the pure bar-raise is REFUTED: the niche opens and is conquered by the wrong dims

Climbing policy, td=20, 500 cycles, seeds 1–8, census in every run:

| f (bar ×) | best_dim per seed | median | pop | mature per seed | mature dims |
|---|---|---|---|---|---|
| 1.00 | [19, 20, 8, 18, 5, 7, 18, 6] | 13.0 | 29–42 | 0–13 | mostly none |
| 1.25 | [7, 6, 5, 6, 4, 4, 6, 5] | **5.5** | 40–58 | 11–29 | 3–9 |
| 1.50 | [5, 7, 4, 4, 5, 4, 8, 4] | 4.5 | 47–78 | 18–49 | 3–12 |
| 2.00 | [6, 6, 5, 6, 5, 4, 5, 5] | 5.0 | 78–104 | 49–75 | 3–9 |

Raising the bar does reopen the mature niche — and the niche is immediately
**colonized by the fastest-training dims (3–9)**, freezing `best_dim` at 4–7,
*below* the f=1.0 maturation-filter medians. Mechanism (connects to
PROPOSAL-DIAGNOSIS hunt 2): the niche entry race and the incumbency contest
are judged on the **live** score surface — the end-of-episode EMA of the
training stream — whose minimum sits at dim ≈ 8 (within-episode tracking
flatters low dims slightly more) and whose incumbents enjoy an unbounded
lifetime-training advantage (anchors at 0.23–0.30 that no at-maturity
candidate of any dim can touch). The honest frozen surface (minimum 12–16) is
not the surface the ecology breathes. At f=1.0 the churn was accidentally
load-bearing: permanent eviction prevented low-dim lock-in and let the
proposal conveyor push upward.

**The finding: the ecology needs two fixes, not one — a fair judge and an
open niche.** An absolute-score contest between a lifetime-trained incumbent
and a patience-trained candidate cannot express "this dimensionality is
better"; it expresses "this frame is currently better", conflating capacity,
training time, and tracking flattery. This is the constitution's
self-graded-homework class of bug in its third and subtlest form: the
training-stream EMA grades frames on data they are simultaneously adapting
to — coverage-fairness fixed *which* events, observation-space fixed *where*,
and the remaining hole is *when*.

## E3 — the fair judge: episode-start scoring × bar factor

The fair judge is already visible in the hunt-2 probe: error on the **first
steps of each episode** — before within-episode adaptation contaminates the
reading — ranks dims like the honest scan (early-step minimum at dim 12–20 vs
EMA-at-end minimum at ~8). It is also the *behaviorally meaningful* test:
transfer to a fresh context, not tracking of the current one. Experiment:
EMAs advance only on the first K=5 steps of each episode (learning, election,
telemetry untouched), crossed with bar factor f ∈ {1.0, 1.5, 2.0} (honest
scores are higher — no flattery — so the niche may need a larger f), climbing
policy, censuses. Pre-registered: the niche opens at some f and is won by
dims 12–20, where the ratchet stalls.

Result (climbing policy, td=20, 500 cycles, seeds 1–8):

| f (bar ×) | best_dim per seed | median | mature per seed | anchors (dim@age) |
|---|---|---|---|---|
| 1.00 | [36, 33, 31, 30, 31, 33, 34, 32] | 32.5 | all 0 | none — pure ratchet |
| 1.50 | [13, 33, 10, 12, 29, 9, 9, 8] | 11.0 | 0–9 | 5/8 seeds: 8–13 @ 408–478 |
| 2.00 | [11, 8, 7, 8, 10, 9, 9, 10] | **9.0** | 15–28 | **8/8 seeds: 7–11 @ 353–496** |

Three readings:

1. **The fair judge alone makes things worse** (f=1.00): honest scores are
   higher than flattered ones, so nothing reaches the bar, the churn is total,
   and the ratchet runs *faster* (median 32.5 in 17 windows). The two fixes
   are genuinely coupled — neither works alone.
2. **Judge + open niche = the first functioning ecology at scale** (f=2.00):
   every seed forms a long-lived anchor (ages 353–496 of 500 cycles), the
   ratchet stalls at the anchor, the population self-limits at 44–57 (cap
   200). The pre-registered signature appears.
3. **A one-notch shortfall, honestly recorded:** anchors sit at dims 7–11,
   below the frozen-scan elbow (12–16). K=5 still admits five steps of
   within-episode adaptation — the episode-start surface's own minimum is
   ~8–12 (hunt-2 probe), and the ecology lands faithfully on *that* surface.
   The judge is fair about *when*, but a within-episode window can never be
   the frozen judge; the residual gap is the price of scoring on-stream.
   (K=2 probe follows.)

## The judge's sharpness limit, and what the residual gap is

K=2 (score only the first transition of each episode) changes nothing:
medians 8.5 / 8.5 / 9.0 at f 1.5 / 2.0 / 2.5, anchors still at dims 6–12.
The window is not the binding contamination. The residual one-notch gap to
the frozen elbow (12–16) is **niche entry order**: dims ~8–11 reach
anchor-grade scores fastest within one protection window, first-movers take
tenure, and the lifetime-training advantage defends them. A fair
*inter-age* comparison (judging a candidate against what the incumbent
scored at the same age, or against a frozen shared-window eval) is a third,
deeper asymmetry — named here as the successor problem, out of scope for
this rule. K=5 is kept (same outcome as K=2, smoother EMA).

## The exponent — fit at obs=60, confirmed at obs=105

td=35 (obs=105), K=5, 1000 cycles (≈14 windows), climbing policy, seeds 1–8:

| f (bar ×) | best_dim median | mature | ecology |
|---|---|---|---|
| 1.50 | 28.0 | 0 everywhere | pure ratchet; conveyor overflows the cap (pop to 382, protected) |
| 2.00 | 20.5 | 0–5 | under-provisioned: 5/8 still ratcheting |
| **2.50** | **9.0** | 15–29, **8/8 anchored** @ ages 791–961 | pop bounded 83–97 |
| 3.00 | 8.0 | 35–49 | anchored but over-open (low dims accumulate) |

`f*(obs=60) = 2.0` and `f*(obs=105) = 2.5` fit one power law through the
reference anchor (factor 1 at obs=10): **p = 0.387 and 0.390** — the rule is
`survive_threshold_base · (obs_dim/10)^0.39`. Note the two working ecologies
land at the *same* `best_dim` level (~9) at both scales, budget-independent
(anchors form early and hold) — the scale-invariant landing the old ecology
never had. The obs=150 leg of E4 is the extrapolation test (predicted factor
2.87).

## Shipped form (production, gate-green before E4)

- `Config.score_window_steps` (default 0 — byte-identical pinned behavior;
  K>0 = survival EMAs advance only on the first K steps of each episode;
  learning, election, and telemetry untouched on gated steps).
- `Config.effective_survive_threshold_base` — **conditional** effective rule
  (unlike the six unconditional §8.8 rules, and for a measured reason: E2):
  `0.8·(obs_dim/10)^0.39` only when `score_window_steps > 0`, raw otherwise,
  raw at the reference always. Consumed by `PopulationScaledDecayPolicy`.
- Self-consistency: the rule reproduces both measured factors (6^0.39 = 2.01,
  10.5^0.39 = 2.50).

## E4 — the re-ask: two scales confirm, the extrapolation scale under-provisions

Production path (`score_window_steps=5`, the 0.39 rule, climbing policy),
2000 cycles, seeds 1–8, census per run:

| td | rule factor | best_dim per seed | median | anchored | pop |
|---|---|---|---|---|---|
| 20 | 2.01 (fit) | [13, 6, 7, 11, 8, 5, 5, 10] | 7.5 | **8/8** (tenures to 2000) | 45–58 |
| 35 | 2.50 (confirmed) | [10, 5, 11, 9, 11, 8, 9, 7] | 9.0 | **8/8** (tenures 1608–1978) | 86–98 |
| 50 | 2.87 (extrapolated) | [12, 12, 12, 19, 11, 15, 16, 21] | 13.5 | **3/8** | 116–434 (overflow) |

td=20/35: the pre-registered signature in full — anchored, self-limited, and
**budget-invariant** (td=35 median 9.0 at 2000 cycles = the 1000-cycle grid's
9.0; td=20 populations identical at 4× budget). One honest wrinkle at td=20:
the median drifted 9.0 → 7.5 from 500 to 2000 cycles — the inter-age
asymmetry's cost compounding with budget (the longest-trained low-dim anchors
creep ahead; successor problem, already named).

td=50: the pure power law **under-extrapolates** — 5/8 seeds never anchor
(the marginal-regime signature: wobbling trajectories, conveyor overflow to
pop 434). Diagnosis, from the arithmetic that failed: the population-scaled
divisor `1 + 0.04·(pop − 4)` punishes the bar for the **structurally
necessary conveyor** of protected juveniles, whose size is
`spawn_per_cycle × patience ∝ (obs/10)^1.5` — frames that cannot be evicted
tighten the bar for the frames that can. That term bends the needed factor
away from any clean power of `obs_dim` (measured f\*: 2.0 → 2.5 → >2.87 with
a steepening slope).

## The conveyor correction — scale the baseline, not just the base

The principled form drops out of the diagnosis: the pop-scaled threshold
exists so eviction paces spawn *among evictable frames*; the protected
conveyor should not crowd the bar. Candidate rule:
`effective_survive_threshold_pop_baseline = pop_baseline +
spawn_per_cycle·(effective_min_age_cycles − min_age_cycles)` — exactly the
raw baseline at the reference (patience raw there), and at scale the divisor
counts only the beyond-conveyor population. Back-solving the measured working
bars through the corrected divisor leaves residual base factors ≈ 1.0–1.3
across all three scales (vs 2.0/2.5/>2.9 uncorrected) — most of the
"seventh rule" variance was conveyor crowding all along. Dose grids at all
three scales re-measure the residual under the corrected baseline.

**Result — the residual is 1.0 everywhere. The rule is constant-free:**

| td | budget (windows) | residual f | best_dim per seed | median | anchored | pop |
|---|---|---|---|---|---|---|
| 20 | 500c (17) | **1.00** | [10, 9, 7, 8, 7, 7, 7, 7] | 7.0 | 8/8 (tenures 457–496) | 39–46 |
| 35 | 1000c (14) | **1.00** | [9, 9, 7, 10, 11, 7, 10, 6] | 9.0 | 8/8 (tenures 868–977) | 86–91 |
| 50 | 1000c (8.6) | **1.00** | [6, 9, 8, 7, 11, 8, 9, 7] | 8.0 | 8/8 (tenures 813–990) | 136–141 |

Larger residuals (1.25/1.5) change nothing but the niche width and the
population — the dose–response is flat above 1.0 at every scale. No fitted
constant survives in the rule; the fitted power law was a curve drawn through
conveyor crowding.

**Conditionality control (K=40 ≈ all-step judge, correction on, td=20):**
the ecology still anchors 8/8 — but at the tracking-flattered surface's
minimum (anchors 4–7, median 6.0) instead of the fair judge's 6–11 (median
7.0). The correction is only *faithful* with the fair judge; it stays gated
on `score_window_steps > 0`.

## Shipped form (final; supersedes the power law above)

- `Config.score_window_steps` (default 0 — byte-identical pinned behavior).
- `Config.effective_survive_threshold_pop_baseline =
  survive_threshold_pop_baseline + spawn_per_cycle ·
  (effective_min_age_cycles − min_age_cycles)` when `score_window_steps > 0`;
  raw otherwise; raw at the reference always (patience is raw there).
  Constant-free. Consumed by `PopulationScaledDecayPolicy`.
  `effective_survive_threshold_base` is **deleted** — the base stays raw.
- `run_scale` now defaults scaled runs to the honest ecology:
  `score_window_steps = 5` (when the base config doesn't set it) and
  `ClimbingProposalPolicy` proposals.

## E4′ — the recorded re-ask (shipped ecology, 2000 cycles, td 20/35/50)

The shipped configuration exactly (`score_window_steps=5` → conveyor
correction active, climbing proposals), seeds 1–8, census per run:

| td | best_dim per seed | median | anchored | anchor tenures | pop |
|---|---|---|---|---|---|
| 20 | [7, 6, 4, 8, 7, 6, 6, 5] | 6.0 | **8/8** | 394–2000 (7 of 8 ≥ 1957) | 39–46 |
| 35 | [6, 9, 9, 8, 12, 7, 8, 6] | 8.0 | **8/8** | 1453–1970 | 87–92 |
| 50 | [6, 9, 10, 9, 9, 8, 7, 8] | 8.5 | **8/8** | 1774–1992 | 136–142 |

Every pre-registered signature holds at every scale: anchored (24/24 runs),
population self-limited and budget-invariant (identical to the 500/1000-cycle
grids), `best_dim` scale-invariant (6–8.5) and budget-invariant (td=50:
8.0 → 8.5 from 1000 → 2000 cycles). The small downward drift at td=20
(7.0 → 6.0 over 4× budget) is the inter-age asymmetry compounding — the
named successor, visible and bounded, not a collapse.

## Outcome

1. **The seventh scale rule is structural and constant-free**: the
   population-scaled eviction threshold must not count the youth-protected
   conveyor. `effective_survive_threshold_pop_baseline = pop_baseline +
   spawn_per_cycle·(effective_min_age_cycles − min_age_cycles)`, conditional
   on the fair judge. A fitted base-exponent form (0.39 power law) was
   shipped provisionally, under-extrapolated at the third scale, and is
   deleted — recorded here as the intermediate that the extrapolation test
   caught.
2. **The fair judge (`score_window_steps`) closes the *when* hole in
   honest scoring**: coverage-fairness fixed *which* events, observation-space
   fixed *where*; episode-start scoring fixes *when* — structural transfer,
   not within-episode tracking. Conditionality measured both ways (the bar
   fix without the judge lands flattered; the judge without the bar fix
   ratchets faster than ever).
3. **T-SCALE now says something true**: `best_dim` is a stable property of
   anchored structure (24/24), invariant to budget and scale — the first
   scaled readings decoupled from both the window budget and the proposal
   distribution. Honest framing of the *level*: medians 6–8.5 sit below the
   frozen-eval elbow (12–16) by the inter-age asymmetry, and *numerically*
   below the old conveyor readings (8/10.5/9.5) — which were higher but
   meant nothing. The criterion did not move to make a number look better;
   the number became meaningful and smaller.
4. **Named successors**, in order: fair inter-age comparison (candidate vs
   incumbent-at-same-age, or periodic frozen-window evaluation — closes the
   6–8.5 → 12–16 gap and the slow downward drift); then the scorer-level
   question E1 exposed (parsimony vs marginal information: the honest elbow
   itself sits at 12–16 regardless of a 20/35/50-dim world at these
   experience budgets).

Instruments that made this diagnosable: the census (Doc 06 persistence seam),
the dimension scan at effective lr, and pre-registered dose–response grids
with per-run censuses. Every hypothesis that died, died to data: the pure
bar-raise (E2), the sharper-window judge (K=2), the fitted power law (E4
td=50), and the unconditional form (K=40 control).

## Epilogue (2026-07-11, same day)

Successor (4a) was taken up immediately and **dissolved by one experiment**
(`INTERAGE-DIAGNOSIS.md`): time-to-asymptote is flat in dim, `best_dim`
churns freely among mature frames, and the landing level is set by the
flatness of the fair-judge score basin (span ≈ 0.02 across dims 6–16) — the
scorer question (4b), now with the measurement that makes it concrete, is
the open frontier.
