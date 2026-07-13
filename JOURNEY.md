# The PRA Journey

The narrative record of this project: what was built, what was measured, what
was believed and then refuted, and what each chapter taught. Specs say what the
system *is*; this file says how we *got here* — including the dead ends, because
the refuted hypotheses are as load-bearing as the shipped code.

> **Keeping this file alive:** whenever a feature lands, a research
> investigation concludes, or a load-bearing decision is made, append a chapter
> (or extend the current one). Follow the template at the bottom. Honesty rules
> apply here as everywhere: record what actually happened, including failures,
> reversals, and findings that contradicted expectations. This rule is anchored
> in `AGENTS.md`.

---

## Chapter 1 — Vision and design (up to 2026-06-20)

The goal: a **continuously-learning machine intelligence** — a configurable
body, a fixed innate drive, and a brain (the Pose Resolution Architecture) that
learns and restructures itself online, never trained-then-frozen. The design
was written as seven documents (`design/01`–`07`) with validation-maturity tags
([V] validated / [D] designed / [O] open problem), plus two normative specs:
PRA-01 (the system) and PRA-02 (the acceptance suite T1–T6 + investigatory
T-SCALE). The strategy: validate the risky core in a synthetic world before
building anything else.

## Chapter 2 — Prototypes and the STEP-0 gate (June 2026)

Four throwaway prototypes (`design/validate/pra_sim*.py`) evolved the scoring.
The **STEP-0 gate caught v3 red-handed**: its load-bearing dimensionality
result (T4) passed only at a lucky 18-cycle horizon and collapsed at 30, and
its population grew without bound. Diagnosis: the survival score was gameable —
pose-space prediction (a collapsed frame aces its own trivial pose), cherry-
picked scoring (frames graded only on what they elected to map), no parsimony,
and an eviction threshold scaled in the wrong direction. v4 fixed all four
(observation-space prediction, coverage-fair EMAs, `w_complexity·dim`, a
threshold that *divides* by crowding) and passed T1–T6 honestly.
**Lesson that became the project's constitution: read the spread, not the mean;
judge across horizons, not snapshots; never let the system grade its own
homework.** Commits `8b8c802`, `a6e6c6c`, `31dd186`.

## Chapter 3 — Feature 001: the validation harness + batched core (2026-06-21)

Adopted GitHub Spec Kit (`be5aea9`) and folded harness + real core + batching
into one feature. Built the `pra` package: the batched, `dim`-grouped
FrameGroup kernel (PRA-01 §7.2's hard requirement), five swappable seams (Bus,
Scorer, ProposalPolicy, DecayPolicy, EventSource), deterministic telemetry, and
the `pra-validate` CLI (suite / determinism / scale). The new core reproduced
the v4 oracle's trajectory **near bit-for-bit at ~40× the speed**, byte-identical
on re-run. T1–T6 all PASS at the reference (T4 within-one majority at every
checkpoint: 8/8, 8/8, 6/8). T-SCALE became runnable — and reported `best_dim≈1`
at `true_dim ∈ {20,35,50}`: the scale question was formally open. Commits
`7387bd7` → `d17354c`.

## Chapter 4 — The T-SCALE diagnosis: six scale-invariance rules (2026-06-29 → 07-06)

Why does structure-finding collapse at scale? A new `pra-validate scan`
diagnostic (train one frame per candidate dim with equal experience, measure
honest error) peeled **five compounding layers**, each a constant validated at
the reference scale silently leaving its regime:

1. the world's tanh emission saturating into a sign channel (pre-activation sd
   = √true_dim);
2. the learning rate diverging at obs_dim=60 (the binding constraint that
   masked everything else);
3. the init scale saturating newborn frames;
4. the linear parsimony penalty overwhelming the flattened error span;
5. the maturation window evicting candidates on transient scores (patience
   2/12/24/29 → mean best_dim 4.7/5.7/6.7/10.7 — dose–response).

All six fixes shipped as **reference-preserving effective rules** (every factor
exactly 1 at the reference scale, verified bit-for-bit). One seed climbed to
**dim 18 of a true 20**. The 8-seed scaled reference: medians 8 / 10.5 / 9.5 at
td 20/35/50, minimum 4 across 24 runs — no collapse anywhere. **The finding:
structure-finding survives scale; its convergence *rate* does not** (the ±1
ladder covers ~constant rungs per budget; the [O] proposal policy is the open
lever). Honest side-finding: even the validated system barely beat the
persistence baseline (0.157 vs 0.165) — which led directly to hardening T3 with
a learned-persistence ablation (`9c4db1a`). Also: parallel seed execution
(byte-identity proven), suite 132s → 21s (`c16f76b`). Trail:
`design/validate/SCALE-DIAGNOSIS.md`; commits `02559ca` → `647c50f`.

## Chapter 5 — Feature 002: motivation & action — the system becomes an agent (2026-07-07)

Doc 05 built: Drive seam (pure functions, structurally immutable parameters —
the system cannot rewrite its own drive), curiosity default (windowed learning
progress + novelty with automatic cold-start handover), Policy seam whose
default reproduces the old random draw **exactly** (the T1–T6 gate stayed
byte-identical), one-step curiosity lookahead, multi-drive mechanism, and the
`pra-validate agency` command with the new **T7** verdict. The honest-criterion
story: the planned sign-majority bar was measured first (3/8 — FAIL), found to
be degenerate for continuous margins near zero, and openly replaced with
one-sided noninferiority — the pre-registered claim was "directedness does not
hurt". Result at reference: curious ≈ random (margin −0.006 ± 0.036) — PASS,
equivalence. Commits `5e40bad` → `f6ac721`.

## Chapter 6 — Feature 003: state persistence (2026-07-08)

Doc 06 built: the complete learned state (frame tensors, drive bookkeeping,
counters, summary accumulators, RNG state, config in force) serializes to a
versioned, pickle-free blob through an atomic SnapshotStore seam. The build
exceeded the spec's bar ("a valid continuation"): **a run resumed from any
cycle-boundary snapshot is byte-identical to the uninterrupted run**, in both
policy modes — provable because consolidation boundaries fall between episodes,
so the world (environment, never snapshotted) is re-derived from the seed
prefix while the generator state is overwritten. Opt-in; validated modes stay
byte-frozen and file-free. Commits `03ad67e`, `4391910`.

## Chapter 7 — The agency diagnosis: curiosity loses, competence wins (2026-07-08)

The scaled T7 measurement failed: novelty-directed curiosity was
*systematically worse* than random at td=20 (margin −0.062, better in 1/8, 87%
directed). Five controlled experiments hunted the mechanism, refuting four
hypotheses with data: tanh-saturation walk (flat), fit-gate starvation (the
curious arm maps *more*), preference reshaping (two candidate shapes turned out
order-isomorphic — no help), action-marginal skew and walk extent (both ≈
random). The decisive control: a **content-free** state-coupled policy is
neutral (+0.014), while the **inverted** preference — familiarity-seeking —
beats random (+0.067, better in 6/8). The harm was the *content* of the novelty
preference: in a uniformly learnable world, spreading experience thin is a pure
cost and concentrated practice a pure gain. The remedy was already anticipated
by Doc 05 §5: a **CompetenceDrive** (mastery + familiarity), shipped in the
drive registry, selected by pure configuration — **T7 PASS at both scales,
beating random in 6/8 seeds at each (+0.064 scaled, +0.027 reference)** — the
project's first measured net-positive directed exploration. Open [O]:
the curiosity/competence blend for worlds with unlearnable regions (camping
risk), predicted-learning-progress lookahead. Trail:
`design/validate/AGENCY-DIAGNOSIS.md`; commits `1953832`, `41cfed2`.

## Chapter 8 — Feature 004: anatomy & body — the design is fully built (2026-07-08)

Doc 02, the last unbuilt design document (its Bus half was already validated in
feature 001), landed as the body layer: Sensor/Actuator interfaces, a Body
composing observations by fixed-order concatenation and routing a
disjoint-union action space, and a ToolRegistry whose registrations defer to
the slow loop and apply through the Doc 03 §7 **frame I/O resize** — learned
weights preserved bit-for-bit, fresh trailing slices at the §8.8 effective
scale, draws from the single generator in a fixed order. The integration
insight kept it small: the Body implements the existing EventSource seam, so a
world mounted through it is **byte-identical** to the direct connection (tested,
SC-001), and the only engine change is an inert duck-typed hook. Mid-run growth
works: register a sensor + actuator at a consolidation boundary, obs_dim
10→13 and n_actions 4→6, every frame adapted without forgetting, the run
completing deterministically. Deferred with loud edges: snapshots of resized
runs (Doc 06 format-version follow-up), in-process timeouts, tool
self-invention [O]. Trail: `specs/004-anatomy-body/`; commits `536baee`, and
the implementation commit following it.

---

## Where things stand (2026-07-13)

The project now has a product thesis and a milestone-gated plan — **an OSS
continuously-learning brain for hobbyists and makers**, `ROADMAP.md`
(Chapter 10). **Every design document (02–07) is built and validated** at the
reference scale: the batched sensorimotor core + structural learning (Docs
03/04), the anatomy/body layer with runtime tools (Doc 02), motivation &
action with the competence drive (Doc 05), state persistence (Doc 06), and
the honest harness (T1–T7, determinism, scale, scan, agency) with parallel
seed execution. **The scaled selection ecology now works** (Chapters 9 and
11): the fair judge (`score_window_steps`) + the constant-free conveyor
correction (the seventh scale rule) + climbing proposals are the
`pra-validate scale` defaults, and the scaled reference is 24/24 anchored
runs with `best_dim` invariant to budget and proposal policy. The inter-age
successor dissolved under measurement (Chapter 12); the scorer arc found the
rot (Chapter 13); and the eighth rule fixed it and closed the T-SCALE
question (Chapter 14): **the honest scaled ecology stands on three measured
legs** (fair judge, conveyor correction, lifetime cap `weight_norm_cap` —
all `pra-validate scale` defaults, with climbing proposals), the capped
scaled reference is **medians 10 / 9 / 9 at true_dim 20/35/50, 24/24
anchored**, and the scaled world measurably carries no `true_dim` signature —
the parsimony weight is a *price*, and selection lands at the price-optimal
dimensionality, stably, at every scale and budget. **Every scaled
acceptance criterion is now measured** (Chapters 15–16): T3 as written
FAILs at td 20/35 — the criterion, not the capability, breaks at scale
(the population-mean measure reads the juvenile conveyor) — and the
pre-registered churn-matched amendment **PASSes at all three scales,
24/24 paired seeds positive**, with the persistence edge real in every
seed and thin (~⅓ of reference, flat across scales, presumably
budget-bound). **The complexity ladder is built and measured**
(Chapter 17): three opt-in worlds behind the existing seam, degenerate
dials byte-identical, criteria pre-registered — first results: selection
lands *part-sized* on compositional worlds and ignores structured
distractors (PASS), strong region noise widens the landing
(dose-dependent), and high-amplitude channel static collapses it (the
named new open problem: **channel-noise robustness**). **Phase A closes
with the frontier drive** (Chapter 24): the per-candidate learnability
signal predicted-LP demanded exists (realized local progress —
`"frontier"` in the drive registry), the blend surface is real for the
first time, and at 24-seed power the A4 exit is met — competence and the
frontier blend beat random at every horizon, both noise dials; frontier
matches competence where avoidance is optimal and is the named candidate
for worlds where camping costs. **Phase B is
complete** (Chapter 23): snapshots now cover grown bodies,
capture-required worlds (episodic Gymnasium resume is exact), and
multi-stream runs, with per-world-class guarantees written down in Doc
06 §5b — and the feature's tests caught and fixed a one-ULP
resume-exactness bug as old as feature 003 (group order lost to sorting
in the blob). **N worlds now
feed one brain** (Chapter 22): `n_streams=K` runs K explorers of one
world structure merged deterministically, cadence in total experience —
measured safe (24-seed noninferiority: merged experience matches focused
experience per observation), with a protocol lesson recorded (pairing
bars require actually-paired arms; ROADMAP B4 closed, K>1 snapshots to
B5). **Worlds that
cannot restart are now first-class** (Chapter 21): opt-in continuous
mode — single engine-enforced boot, virtual episode boundaries carrying
every validated mechanism, exact resume via the optional world-state
capture protocol; healthy on bounded worlds, and the recorded reading
teaches that continuous deployments need recurrent worlds (the reference
world drifts and saturates when run unbroken — an instrument property,
now written down); ROADMAP B3 closed. **The
getting-started experience exists** (Chapter 20): `pra-rover` — a 2D
rover body of named parts on the unchanged engine with a stdlib live
viewer, install to watching in under five minutes, byte-reproducible
with the viewer on; ROADMAP B1 closed. **The first
external-world adapter is in** (Chapter 19): any Discrete-action /
Box-observation Gymnasium environment mounts through the existing body
seam (`GymnasiumBody`, optional `gym` extra) with explicit
respawn-on-termination semantics and byte-identical seeded runs —
CartPole worked example in `examples/`, ROADMAP B2 closed. **The blend
question is measured and dissolved** (Chapter 18): the drive pair shares
one novelty statistic, so no blend surface exists — competence wins
where non-uniformity bites (19/24 at strong noise, no structural cost),
nothing directed beats random at mild noise, and the pre-registered A4
exit was met by no configuration — later met at proper power (Chapter
24). Open research, in priority order: **channel-noise robustness**
(diagnosis in progress), frontier-vs-competence on worlds where camping
costs (mastered-then-changing, multi-region learnable), fully
*predictive* LP (a per-candidate error model; the frontier's realized
form is its baseline), the elect-gating question, and (design-level,
when a deployment demands it) whether reference-scale long lifetimes
eventually need the cap too. Snapshot support for anatomy-resized runs
shipped in Chapter 23.

## Recurring principles (what the journey keeps teaching)

- **Diagnose before fixing; one variable at a time.** Both diagnoses found the
  true mechanism only after refuting the obvious story with data.
- **Reference-preserving changes.** Every scale rule and every new layer keeps
  the validated behavior byte-identical; regressions are structurally
  impossible, not merely unlikely.
- **Honest criteria, amended openly.** When a pass-bar proved degenerate
  (T7), it was replaced in the open with the raw numbers recorded — never
  tuned quietly until green.
- **Negative results are results.** "Curiosity hurts at scale" produced the
  project's best positive finding one experiment later.

## Chapter 9 — The proposal diagnosis: the ladder was never the bottleneck (2026-07-08)

Took up SCALE-DIAGNOSIS's successor problem (a): can the [O] proposal seam
make rung *count*, not rung patience, the thing that shrinks? A jump-size
dose–response in the live engine (td=20, fixed 500-cycle budget, 8 seeds, six
arms) answered the question asked: selection at scale is **waste-limited, not
reach-limited** — wider explore bands (+8→+32) move nothing (far candidates
die on their transient), while forbidding proposals at or below the incumbent
doubles the fixed-budget median (13.0 vs 6.5, better in 7/8 paired seeds).
The winner, `ClimbingProposalPolicy` (every proposal in `(best, best+4]`),
climbs ~1 rung per maturation window.

Then the full-length confirmation caught the screen being flattering: at 2000
cycles the climbers ride past the truth to `best_dim` 62–74 ≈ `obs_dim` —
the 500-cycle "four seeds at 18–20" was a **lucky-horizon snapshot**, the v3
failure mode, caught this time by the protocol built after v3. Three
mechanism hunts followed, two refuted with data (post-learning EMA grading:
real but flat ~0.02; end-of-episode EMA sampling: flatters everyone, inverts
nothing — the extended scan to dim 80 shows a *healthy* score surface,
minimum at dim 12–16). What stood was arithmetic plus a census (the Doc 06
persistence seam as instrument): every scaled run is a **two-caste ecology**
— a standing conveyor of exactly `spawn_per_cycle × patience` protected
juveniles, plus a mature niche that only dims ≲ 12 can enter, because the
absolute survival bar sits below the achievable at-maturity score of
everything larger. The control's scaled medians (8/10.5/9.5) were never the
score-surface elbow: they are the **maturation filter** — which dims can
train under the bar within one protection window. Under the climbing policy
the niche is empty (census: 29/29 juveniles, zero mature) and `best_dim`
ratchets with the proposals themselves, decoupled from the world.
**`survive_threshold_base` is the seventh scale-variant constant**, named and
open (a reference-preserving effective rule is the candidate); the climbing
policy ships opt-in, correct-once-the-bar-scales; the scan instrument now
trains at the effective learning rate (it probed the divergent regime at
scale). Chapter lesson, again from a new direction: a faster search is also a
sharper instrument — the slow ladder wasn't finding the truth, it was too
slow to reveal that nothing was. Full-scale confirmation across all three
scales: one rate (~0.8–1 rung per maturation window) explains all 24 runs —
best_dim 62–74 / 26–34 / 12–25 at td 20/35/50 (69/29/17 windows), overshooting
a truth of 20 threefold and falling far short of a truth of 50; the td=35
median of 28.5 would have read as a breakthrough in isolation, which is the
whole argument for the multi-scale protocol. Trail:
`design/validate/PROPOSAL-DIAGNOSIS.md`; committed together with this chapter.

## Chapter 10 — The product thesis: an OSS brain for makers (2026-07-08)

The question was not technical: what is PRA *for*? Until now the honest answer
was "an academic exercise" — every document specified the system, none named a
user. Decision: **PRA is an OSS product for hobbyists and makers** — install in
one command, mount a world through the Body API, watch it learn live, keep and
share what it learned. Explored and rejected along the way: Minecraft-first
onboarding (setup friction + real-time non-determinism + the brain isn't ready
to look good in it), an MMO (Artifacts) as a lab (3–30s enforced cooldowns —
kept instead as a future long-horizon *deployment* showcase), and an embedded
Go game server (viable only as a tick-steppable fork; parked with the idea
recorded). The load-bearing sequencing principle that fell out: **research
gates before showcase spends** — the bottleneck is the brain, not the
plumbing, so no user-facing milestone ships ahead of the capability that makes
it worth watching. The plan is `ROADMAP.md` (milestone-gated, no dates);
`GETTING-STARTED.md` shipped alongside it as the first Phase-B artifact.
Amended same day: the original non-goals list was partly wrong. Distributed
operation (the Doc 02 bus seam's purpose), tool self-invention ([O] since the
design docs), and the long-range paradigm claim are *horizon ambitions*, not
non-goals — with the positioning sharpened: PRA competes with **frozen**
intelligence (trained-then-deployed) on continual learning and online
restructuring, not with LLMs on language. Remaining non-goals: benchmark
theater, hosted services, language/knowledge competition.
Trail: `ROADMAP.md`, `GETTING-STARTED.md`; commit follows.

## Chapter 11 — The threshold diagnosis: the fair judge and the conveyor (2026-07-10 → 07-11)

Took up Chapter 9's successor: make the scaled selection ecology real. The
first idea — scale the survival bar with a fitted power law — died twice,
each time to a pre-registered measurement. Raising the bar alone reopened the
mature niche and handed it to tracking-flattered low dims (best_dim *fell* to
4–7): the training-stream EMA is the third form of self-graded homework, the
*when* hole that coverage-fair (which) and observation-space (where) scoring
left open. The fix is the **fair judge** (`score_window_steps`): survival
EMAs advance only on episode-start steps, scoring transfer, not tracking. The
judge alone made things worse (nothing reached the bar; the ratchet ran
faster than ever) — the two fixes only work as a pair. The paired power law
(exponent fit at obs 60, confirmed at 105) then failed its extrapolation test
at obs=150 — and the failure's arithmetic named the true mechanism: the
population-scaled threshold was counting `spawn_per_cycle × patience`
**unevictable juveniles**, a conveyor that grows as `(obs/10)^1.5` and
tightens the bar for the frames that can be evicted. Excluding it —
`effective_survive_threshold_pop_baseline`, the **seventh scale rule,
constant-free** — restored the ecology at all three scales with residual
factor exactly 1.0. The recorded re-ask (2000 cycles, shipped defaults:
fair judge + conveyor correction + climbing proposals): **24/24 runs
anchored**, populations self-limited, `best_dim` medians 6 / 8 / 8.5 at
true_dim 20/35/50 — invariant to budget and to the proposal distribution.
Honest framing: lower numbers than the superseded conveyor readings, and the
first that mean anything. Remaining gap to the frozen-eval elbow (12–16) is
the named successor: fair inter-age comparison (the incumbent-lifetime
advantage in niche entry), ahead of the scorer-level question the elbow scans
exposed (the honest optimum sits at 12–16 regardless of the world's true
dimensionality at these budgets). Trail:
`design/validate/THRESHOLD-DIAGNOSIS.md`; committed together with this
chapter.

## Chapter 12 — The inter-age diagnosis: a successor problem dissolves (2026-07-11)

Chapter 11's named successor — fair inter-age comparison — died to its own
discriminating experiment in an afternoon. The premise: niche entry favors
fast-training low dims, and incumbents hold tenure by lifetime advantage,
pinning the scaled landing (6–8.5) below the frozen-eval elbow (12–16).
Measured (fair-judge score surface at equal experience, two horizons, plus
per-dim time-to-asymptote): **time-to-asymptote is flat in dim** (~330
episodes everywhere — no entry-race rigging exists), the fair judge's own
minimum is 10–12 (not 12–16: ~2–4 dims of residual window flattery), and —
the real finding — **the basin is flat**: dims 6–16 span 0.024 in asymptotic
score, the same order as seed noise and a couple of parsimony increments.
The E4′ trajectories confirm no tenure lock at all: `best_dim` churns freely
among 10–17 mature frames (11→10→12→10→6→13→13→7 in one seed). The landing
level was never an age asymmetry; it is the low edge of a gradient-free
basin. No remedy shipped — a dim-scaled maturation window would have fixed a
refuted mechanism. The frontier, now with the measurement that makes it
concrete: **the scorer** (Doc 03 §6) — make the basin informative (re-shaped
parsimony, elbow-relative selection, or a frozen shared-window judge), a
design-level [D] investigation with reference revalidation. Negative results
are results; this one cost one experiment. Trail:
`design/validate/INTERAGE-DIAGNOSIS.md`; committed together with this
chapter.

## Chapter 13 — The scorer diagnosis finds the rot: lifetime stability is the real frontier (2026-07-11)

Opened to answer "can the flat score basin be made informative?" and closed
having found something that outranks the question. The experience
dose–response first split the basin cleanly: the *error* surface is
experience-limited (4× training moved the honest prediction minimum to dim
28 and deepened it everywhere), but the *score* minimum stays
parsimony-pinned at 12 — the linear charge outruns the marginal gain at
every measured budget. Then the 16× scan broke the pattern: dims 8–24
**roughly doubled their error** between 2400 and 9600 episodes, consistently
across seeds. The longevity probe pinned the mechanism with both hands:
frozen honest error bottoms exactly where the weight norm turns from healthy
compression (20→18) to runaway growth (18→29), onset ≈ 400–800 live cycles
at obs=60, capacity-dependent — mid dims rot, dim 4 and dim 32 largely do
not. Rereading the E4′ censuses against the rot profile closed the loop:
the live scaled ecology's anchors sit at dims 4–8 — the rot-resistant dims —
and the "inter-age downward drift" is the rot differential compounding.
**Constant-lr continual learning is lifetime-bounded, the long-run ecology
selects for rot-resistance rather than structure quality, and every scaled
best_dim reading is downstream of this.** No fix shipped in this chapter —
the diagnosis is the deliverable; the named successor is the eighth
rule-class problem, lifetime stability, with per-tensor max-norm control as
the reference- and premise-preserving candidate (no freezing; the system
stays never-trained-then-frozen). Trail:
`design/validate/SCORER-DIAGNOSIS.md`; committed together with this chapter.

## Chapter 14 — The eighth rule and the price of a dimension (2026-07-11)

Two arcs closed in one day, each finishing the other. First the rot fix:
per-tensor max-norm control (`weight_norm_cap`), designed from Chapter 13's
measured mechanism — stateless closed-form caps at `1.2·E‖W_init‖`, biases
exempt, projected at episode starts, magnitude only (the never-trained-then-
frozen premise survives intact). The dose–response was clean (∞ rots, 1.5
attenuates, 1.2 eliminates — capped frames end 9600-episode runs at their
best-ever error, and the immune dims are untouched), and the payoff was
intervention-grade: moving *only* this mechanism lifted the td=20 scaled
landing from median 6 to 10 — onto the fair-judge basin minimum — with the
budget-drift gone, and the lift across scales ordered exactly by rot
exposure (+4 / +1 / +0.5). The capped scaled reference: **medians 10 / 9 / 9
at true_dim 20/35/50, 24/24 anchored.** The honest scaled ecology now stands
on three measured legs — fair judge, conveyor correction, lifetime cap —
each refuted as sufficient alone.

Then the parsimony re-ask on the rot-free ground the cap created, and the
retirement it forced: the long-trained honest error surface **falls
monotonically to the capacity ceiling in both components and both seeds** —
the scaled world's intrinsic dimensionality leaves no signature for any
penalty shape to find (nonlinear emission: a 20-dim latent's image is not a
20-dim linear object). "Does best_dim track true_dim at scale" is closed by
measurement: it cannot, and should not. The parsimony weight is a **price**
— selection buys dimensions while the marginal error gain exceeds it — and
the capped ecology already sits exactly at that operating point (measured
marginal gain crosses the 0.0067/dim price at dims 8–12; the landing is 10).
What T-SCALE can honestly claim, and now measures at every scale and budget:
**selection lands at the price-optimal dimensionality, stably.** That is the
finding the investigatory suite existed to produce. Trails:
`design/validate/LONGEVITY-DIAGNOSIS.md`, SCORER-DIAGNOSIS epilogue;
committed together with this chapter.

Roadmap consequence, recorded with the Chapter 10 docs bundle as it ships:
A1 (the seventh scale rule) is closed by chapters 11–14 and marked done in
`ROADMAP.md`; **T3's persistence clause at scale enters as the new top
Phase-A gate (A2)**, with the ladder and the drive blend renumbered A3/A4.

## Chapter 15 — T3 at scale: the criterion breaks before the capability does (2026-07-11 → 07-12)

Took up ROADMAP A2 the day it was named: T3's persistence clause — genuine
prediction must beat a *learned* "nothing changes" predictor, the suite's
strong claim — had never been measured on the scaled worlds. The instrument
came first, reference-preserving by construction: `pra-validate scale --t3`
runs the exact reference triad (predictive + effort-only + identity, same
seed offsets, same evaluator as the suite — PRA-02 §2 verbatim) under the
scaled ecology defaults, opt-in, with the validated paths byte-identical
(regression-tested). Protocol pre-registered in the trail doc before the
run: 2000 cycles, seeds 1–8, td 20/35/50 — the capped scaled reference
protocol. The run cross-validated the instrument for free: the predictive
arm reproduced the anchored reference `best_dim` spreads seed-for-seed at
all three scales.

The verdicts, as written: **FAIL at td=20 and td=35** (identity clause 2/8,
margins −0.054 ± 0.075 / −0.030 ± 0.039), PASS at td=50 by the thinnest
majority (5/8, mean margin still negative) — the scaled ecology's measured
improvement sits at the learned-persistence floor, versus +0.067 (6/8) at
reference. The effort clause never contested (8/8 everywhere). Before
concluding "no dynamics learning at scale," the one confound had to die:
T3's measure averages honest error over **every electing frame**, and the
scaled predictive ecology carries a standing juvenile conveyor
(29/68/116 protected juveniles at td 20/35/50) while the no-consolidation
ablation arms have zero churn. The one-variable discriminator — predictive
training under the identity arm's exact semantics (same `seed+18888`
worlds, no consolidation), only the training target differing — flipped the
sign: **churn-matched, prediction beats persistence 6/6** (td 20 and 35,
margins +0.013 to +0.044). The FAIL is substantially **measurement
composition, not a capability cliff** — the same instrument-vs-scale lesson
as the maturation filter and the fair judge, now surfacing in the
acceptance suite itself. Recorded without smoothing: the frame-level edge
is *thin* (~⅓ of reference, presumably budget-bound at the scaled effective
learning rate), and the cross-scale margin trend is **not** explained by
juvenile fraction alone (it predicts the wrong ordering; elect-gating is
the named candidate — open). Verdicts stand as measured; the successor is
named, not improvised: a **churn-matched scaled form of T3**, designed
openly as a criterion amendment per the T7 precedent. Trail:
`design/validate/T3SCALE-DIAGNOSIS.md`; committed with this chapter.

## Chapter 16 — The amendment pays: churn-matched T3 passes 24/24 at scale (2026-07-12)

Chapter 15's named successor, resolved the same arc. The amendment was
**pre-registered before the run** with its falsification stated (paired
margins ≤ 0 in half the seeds at any scale would kill the capability
story): the scaled T3 keeps the weak clause from the triad and replaces
the strong clause with the diagnosis's own discriminator — a fourth arm
per seed, *predictive* training under the identity arm's exact semantics
(same `seed + 18888` world, no consolidation), paired against the identity
arm so the only difference is the training target. The instrument became
the quartet (`scale --t3`, still opt-in, validated paths byte-identical);
the reference T3 is untouched.

The full-protocol result: **PASS at all three scales, 24/24 paired seeds
positive** — margins +0.021 ± 0.011 / +0.028 ± 0.008 / +0.026 ± 0.015 at
td 20/35/50, with the as-written counts (2/8, 2/8, 5/8) kept beside them
permanently and the triad half reproducing Chapter 15's tables
byte-for-byte. Two things the quartet settled: the paired margin is **flat
across scales** — so the as-written cross-scale trend was entirely a
composition-pollution gradient (why pollution shrinks as the conveyor
grows remains the open elect-gating note, now decoupled from the
criterion); and the thin edge is now a *quantity* (~+0.025 at scale vs
+0.067 at reference, uniform, every seed) rather than a doubt. **A2
closes with every scaled acceptance criterion measured**, and the
project's instrument-vs-scale lesson now has its acceptance-suite
chapter: when a criterion breaks at scale, diagnose which broke — the
claim or the measure — then amend the measure openly and let the claim be
retested. Trail: `T3SCALE-DIAGNOSIS.md` (amendment + result sections);
committed with this chapter.

---

## Chapter 17 — Feature 005: the complexity ladder — every failure names its cause (2026-07-13)

ROADMAP A3, spec-kit flow start to finish in one arc (spec → plan → tasks
→ implement → first results). Three opt-in worlds, each **one known
difficulty axis** off the validated staircase, behind the existing
`EventSource` seam with zero engine changes: `nonuniform` (a half-space
region of latent space with irreducibly random transitions — the A4
noisy-TV/camping testbed, with world-side occupancy counters),
`compositional` (factored dynamics via mask-after-draw under the joint
emission, so parts never leak through channels), `distractor` (appended
channels from an autonomous drift latent, dial to pure noise). One
load-bearing spec amendment before planning: non-uniformity must be
**state-dependent** (a region policies can seek or avoid), not channel
noise — channel noise is exposure-constant under every policy and
measures nothing about drives; it folded into the distractor dial
instead. Every rung's degenerate dial is **byte-identical** to the
reference world (integration-tested — the discipline that also guards
the deliberate duplication of the byte-frozen reference core), ground
truth lives behind a harness-only accessor, and `pra-validate ladder`
runs pre-registered criteria (LADDER-CRITERIA.md, committed before
results) as investigatory verdicts. 193 tests green, 36 new.

First results (one instrument run, 103 s, six dial sets): **the ladder
works exactly as designed — each verdict is attributable.**
L2 **PASS** at both factorizations, with the census answering the
pre-stated open question: selection lands **part-sized** (best_dim 2–4,
populations at the part scales, no seed buying the Σd_k = 6 monolith) —
the parsimony finding recurring compositionally. L3 structured **PASS**
(selection never buys a *predictable* distractor), but L3 noise **FAIL**:
half the observation carrying unit-scale static collapses the landing to
dim 1 in 5/8 seeds — **channel-noise robustness**, the ladder's first new
open problem, named with its reproducible failing configuration. L1
FAILed as written and the diagnosis split it honestly: the structure
clauses pass at mild noise (7/8, 8/8) and genuinely degrade at strong
noise (4/8 — dose-dependent, real); what broke at mild noise was the
**criterion's occupancy band** — per-world occupancy is drift-dominated
and bimodal (each world's four fixed displacements carry a net latent
drift that dwarfs episode starts), not concentrated at the analytic ½.
Amended openly per the T7 precedent (numbers kept; the amended clause
certifies what A4 actually needs: per-seed occupancy baselines,
non-degenerate); amended verdicts from the same table: mild PASS, strong
FAIL. Chapter lesson, now thrice-learned and once pre-empted: write the
criterion first, and when it breaks, diagnose *which* broke — the claim
or the measure — before touching either. Trail:
`design/validate/LADDER-CRITERIA.md`; A4 is unblocked with its baselines
in hand.

## Chapter 18 — The blend dissolves: one novelty statistic, three behaviors (2026-07-13)

ROADMAP A4, taken up the day A3 unblocked it, pre-registered before the
data (BLEND-DIAGNOSIS.md): on the L1 noisy-region world, does curiosity
stare at the noise (H-stare), does competence camp away from it (H-camp),
and does any curiosity/competence blend beat both poles (H-blend — the
Doc 05 §5 open question)? 288 runs: six drive arms × two noise strengths
× three horizons × eight seeds, margins paired against the same-seed
random arm, occupancy from the feature-005 world-side counters.

The anomaly was the finding: **blend-75 reproduced pure curiosity
bit-for-bit across all 48 runs.** The mechanism sits in the drive forms
plus one policy line — the only per-candidate term either drive has is
the *same* novelty statistic ν (curiosity adds +ν; competence adds
`max(0, 1−ν)`; LP and mastery are history-shaped, candidate-constant),
so a weighted sum's candidate ordering reduces to `sign(w_cur − w_comp)`
wherever ν ≤ 1, and equal weights make every candidate tie — which the
lookahead's ascending strict-`>` scan collapses to action 0. **The blend
axis has no surface to tune**: {curiosity, competence, a degenerate tie
corner} is the whole simplex. H-blend dissolved by mechanism; blend-50's
grid-best strong-noise numbers are a degenerate-policy artifact
(mostly-fixed-action drift = maximally predictable experience — and a
warning about reading blend grids without mechanism checks).

The poles behaved as the pre-registration predicted, with one honest
refutation: curiosity IS pulled toward the region where the noise is
strong (Δoccupancy +1–2 points at σ=0.8, negative at σ=0.2 — mild noise
isn't novel enough to attract) but its margins never went meaningfully
negative — the LP term's flatness in unlearnable regions caps the
noisy-TV damage exactly as Doc 05 §3.1 designed (H-stare: attraction
confirmed, harm refuted). Competence avoids the region (−4 to −10
points) and **wins where the noise bites** (σ=0.8: margins +0.09–0.13,
signs 7/8, 5/8, 7/8, best_dim unharmed — the camping degeneracy did not
materialize). The pre-registered A4 exit (majority of seeds at every
horizon, both dials) was **met by no configuration**: at mild noise the
directed-vs-random effect sits inside seed noise at reference budgets.
Recorded as measured. What remains of A4 is the predicted-LP lookahead —
a per-candidate *learnability* signal, the only live path to a genuine
blend; interim showcase guidance is `competence` on strongly non-uniform
worlds. Trail: `design/validate/BLEND-DIAGNOSIS.md`; committed with this
chapter.

## Chapter 19 — Feature 007: the Gymnasium adapter — hundreds of worlds through one seam (2026-07-13)

ROADMAP B2 asked for a small thing with one hard question inside it: mount
any Gymnasium environment as a PRA body (~50 lines of adapter), and resolve
the episode mismatch — PRA episodes are fixed-length, Gymnasium episodes end
themselves — *explicitly*. Built as a pure leaf: `GymnasiumWorld` (an
`EventSource` over `gymnasium.Env` — Discrete actions, Box observations
flattened C-order to float64, reward and termination flags never crossing
the seam) composed through the **existing** `WorldSensor`/`WorldActuator`
pair into `GymnasiumBody` — the feature-004 pattern replayed, and the 004
world-through-body byte-equivalence replayed with it (tested: body-mounted ≡
direct-mounted, byte-identical). Zero engine, config, or harness edits; the
dependency is a new `gym` extra (and lives in `dev`, so the gate runs the
adapter tests always — none skipped).

The termination decision: **immediate seeded respawn**. On
`terminated`/`truncated` the adapter reseeds and resets mid-step, returns
the fresh observation as the step's outcome, discards the terminal
observation, and counts the respawn. The consequence is documented rather
than hidden: the boundary transition is irreducibly unpredictable — the
ladder's unlearnable-region property, localized at episode boundaries — and
it is *competence-dependent* (a policy that keeps the pole up respawns
less), so the noise floor shrinks as mastery grows. The alternatives died on
honesty grounds: Gymnasium-1.0-style delayed autoreset silently voids one
action per boundary (a false action→outcome pairing is worse than an honest
teleport), and freezing until the PRA episode ends would feed mostly-frozen
episodes under early random policies (CartPole falls in ~20 steps).

Determinism came down to one constraint: the engine's generator must not be
perturbed — a single extra draw at mount would shift every downstream birth
and action in any composed mode. The adapter therefore derives its seed
entropy from a **pure state read** of the run generator (a pure function of
the run seed; verified no-draw) and seeds env reset *k* from
`SeedSequence(E, spawn_key=(k,))`, one counter across episode starts and
respawns. Measured on CartPole-v1: the full reference schedule runs in
~3 s/seed and reproduces byte-identically; under the pinned random policy
the example run respawns 473 times across 13 000 steps (~3.6% of
transitions carry the boundary noise). The worked example
(`examples/cartpole.py`, the newcomer's second stop) prints the honest
summary and *proves* its own determinism by re-running its seed. One honest
non-claim recorded with it: on CartPole under the random baseline, selection
lands at `best_dim` 1 — an observation, not a validated criterion; no
Gymnasium world has acceptance criteria yet, and the example says what the
brain is doing (prediction, not reward-seeking) so nobody mistakes it for an
RL demo.

What it opened: B2's exit criterion is met (worked example, contract tests,
termination decision documented), and the deferrals are named with owners —
Box-action support and reward-as-sensor (future adapter work), engine-side
episode semantics (B3), snapshot/resume of externally-stateful worlds (B5:
a Gymnasium env cannot be re-derived from the seed stream, so v1 documents
the limitation loudly instead of shipping silent divergence). Built in a
parallel worktree by a second session alongside chapters 17–18's work.
Trail: `specs/007-gymnasium-adapter/` (spec, research R1–R7, contracts);
`src/pra/anatomy/gymnasium_body.py`; `examples/cartpole.py`; commits
909355d, e8ccbe7, 8b6dff6, b998316.

## Chapter 20 — Feature 006: the watchable rover world — the product is the watching (2026-07-13)

ROADMAP B1, spec-kit flow in one arc (spec → plan → tasks → implement).
The first artifact whose product is a person standing in front of it: a
deterministic 2D rover world (arena, five seeded circular obstacles, a
rover with pose) built as a **body of named parts** — 5-ray rangefinder,
compass, position beacon, bumper, one drive actuator — composed by the
Doc 02 anatomy layer into exactly the validated reference widths
(obs_dim 10 / n_actions 4, where every scale-rule factor is 1, on
purpose), mounted on the unchanged engine through `world_factory`. One
command, `pra-rover`, serves a built-in live viewer (stdlib
`http.server` + one self-contained canvas page, zero new dependencies):
the rover wanders under the pinned random policy while the brain's own
quantities move on screen — best-frame prediction-error EMA falling,
population breathing, best_dim settling. B1 is the anatomy layer's first
real showcase beyond 1:1 delegation: a newcomer reading the rover source
reads the integration surface they would use for their own hardware.

The load-bearing design decision was **who is allowed to touch the run**.
The viewer observes without perturbing: the world records its own pose
stream (the L1 occupancy-counter precedent — plain value appends, no RNG,
no float work, no locks on the run path), the tap's `bus_factory` captures
the live FrameStore reference while returning the **stock** bus unchanged,
and every derived computation happens in the serving thread on copies,
with torn-read fallback instead of run-path locks. Pacing (`--fps`,
default 50 steps/s ≈ 4.3 min for the full reference schedule) lives in
the *world*, never the viewer — watchability is a property of the demo
run, not of being watched. Byte-identity is proven three ways in tests:
re-run ≡ re-run, viewer-on-under-live-HTTP-polling ≡ viewer-off, paced ≡
unpaced. 223 tests green in the feature worktree (30 new), the
byte-frozen baseline untouched, nothing outside `pra.examples` edited but
two inert pyproject lines.

Honest numbers from the shipped instrument (single seeds, labeled as
such, unthrottled full runs ≈ 4.6 s): seed 1/2/3 pred-error improvement
0.190/0.280/0.203, best_dim 2/2/2, final populations 15/19/13 — the
brain genuinely learns the rover's sensor stream, and the parsimony
finding recurs on a spatial world: the latent is (x, y, θ) ≈ 3–4
dimensional, and selection again lands at the price-optimal 2, not the
"true" size (SCORER-DIAGNOSIS, now seen on a world with real geometry).
Deliberately out of scope, stated in the spec: drive-directed rover
watching is A4's measured work (the demo claims *predicting*, never
*navigating*); rover-run snapshot/resume byte-identity is unclaimed and
untested; the anatomy is fixed at reference widths. What it opened: the
getting-started experience now exists (`pip install poseres && pra-rover`
— install to watching in well under five minutes), and the rover is a
ready-made testbed body for the Gymnasium adapter's comparisons and A4's
directed policies. Built in a parallel worktree by a second session
alongside chapters 17–19's work. Trail: `specs/006-rover-world/` (spec,
research R1–R10, contracts); commits ddeabc2, c1b0468, 1be4d34, ddf70e6,
0665554.

## Chapter 21 — Feature 008: continuous operation — the slow loop was always a cadence (2026-07-13)

ROADMAP B3, the first engine-semantics change since the anatomy layer, and
the roadmap demanded the design in writing first. The design's core
finding made the implementation almost disappear: **every episode-keyed
mechanism already keys off the transition-chain break and the within-span
index** — the norm cap projects when `prev_obs is None`, the fair judge
counts `t < K`, warmup counts spans, consolidation was always "every N
episodes of experience," never "after N resets." So continuous mode is
one changed line in the episode loop (reset → carry the trailing
observation, which episodic mode discards) plus an engine-enforced
**single boot** — `reset()` called exactly once, the world's one chance
to prepare (a homing routine, a login): the contract C2 was promised,
proven against a guard world that raises on any second call. Virtual
episodes carry everything else untouched; zero store/scorer/drive/body
edits.

The design surfaced one real problem before code did: continuous resume
cannot ride Doc 06's world-from-seed rule (a world's mid-run state is the
product of its whole action history). Answer: an optional world-state
capture protocol (`state_dict`/`load_state_dict` — in-repo worlds
implement it in a few lines; the Body delegates per-instance; the
snapshot blob gains an optional entry written only in continuous mode, so
episodic blobs carry no trace and old blobs decode unchanged), and a loud
capture-time failure for worlds that can't — external-world capture stays
B5's, named. The spec's original "seed-derivable" resume claim was
amended openly when the design refuted it.

The reading (pre-registered guess, half wrong, recorded): on the
**reference world** continuous operation collapses learning — improvement
−0.17 mean, `best_dim` → 1, 8/8 seeds — because the unbounded latent walk
drifts and the tanh emission saturates; the guess predicted the
improvement hit but called structure "less affected," and it collapsed
hardest (parsimony working correctly on a degenerated world). The
discriminator run settled the attribution: on the **bounded** rover arena
continuous mode is healthy (improvement in-band, `best_dim` 2/2/2, no
collapse). The mode works; **continuous deployments need recurrent
worlds** — the reference world is an episodic instrument, and the
guidance for C1/C2 is now written down with a reproducible drift
signature. Gate: 267 tests green (18 new). Trail:
`specs/008-continuous-operation/` (spec with its open amendment, research
R1–R10, contracts, reading.md).

## Chapter 22 — Feature 009: multi-stream — the merge does no harm, and a protocol gets caught (2026-07-13)

ROADMAP B4, design-first: K world instances of one hidden structure
(identical construction seeding, per-stream generators assigned
afterward from spawn keys), K independent explorers, one brain, merged
by a fixed episode round-robin (`e mod K`). The design's two load-bearing
choices: **randomness split by ownership** (stream generators carry world
noise and policy exploration; the brain generator carries
births/proposals/decay, consumed in merge order — the roadmap's
"per-stream seeds, merged deterministically" made concrete), and
**cadence in total experience** (consolidation counts merged episodes,
so equal schedules mean equal experience at every K — chapter 21's
lesson now doing load-bearing work). Every within-episode mechanism is
episode-local and therefore stream-local for free; K=1 is the untouched
validated path (frozen baseline still green through the loop refactor);
K>1 snapshots fail loudly naming B5. Pre-registered before measuring:
episodic streams under the random policy are near-exchangeable — the
reference-world comparison is the *null case*; continuous mode is where
streams genuinely differ.

The measurement then caught the measurer. The pre-registered 8-seed
comparison **FAILed its noninferiority bar** (mean margins −0.040/−0.046
at K=2/4, just past the bounds) — against the pre-registered null. The
diagnosis found the flaw in the protocol, not the regime: the bar
borrowed T7's *paired* form, but a K>1 run necessarily uses different
generator realizations than K=1, so the "paired" margins were unpaired
differences of two seed-noise draws (spread ≈ √2 × the improvement std —
the exact unpaired signature) and eight seeds were underpowered. At 24
seeds the margins collapse to ≈ 0 (−0.0044 and −0.0030, bounds −0.025
and −0.030): **noninferiority PASSES at both K** — merged experience
matches focused experience per observation, the safety result B4 needed,
and the null confirmed. Both protocols and the amendment are in the
record (specs/009-multi-stream/reading.md), plus the general lesson, now
written down: a pairing bar is only as good as what the arms actually
share; cross-realization comparisons need unpaired power stated up
front. The continuous-rover reading (K explorers at K positions of one
arena) is recorded investigatory at n=3 — the substantive multi-stream
research (directed policies, longer horizons, world-side wall-clock
parallelism, the external bus backend) now has its instrument. Gate: 277
tests green (10 new). Fourth feature closed in one day; Phase B has one
item left (B5, holding three named snapshot debts).

## Chapter 23 — Feature 010: snapshot completeness — three debts, one principle, one caught bug (2026-07-13)

ROADMAP B5, the Phase B finisher. Three features had each left one named
hole in the persistence story; all three closed under one principle —
**code from the caller, state from the blob**: grown bodies record and
verify their *current* dimensions (the resuming factory supplies the
grown parts, because tools are code; wrong anatomy fails loudly);
capture-required worlds declare `snapshot_needs_state` and their state
travels in every snapshot (the Gymnasium adapter's reset counter — one
integer at a C4 boundary fully determines every future reseed, so
episodic Gymnasium resume went from silently-divergent to exact,
conditional on the env's own seeded determinism, stated); multi-stream
runs snapshot all stream positions (per-stream generators, world states
where the class requires them, carried observations, the merge
position). Every format addition is optional-with-absent-default —
unresized, K=1, derivable-world blobs are unchanged — and the
feature-009 config rejection is lifted. Doc 06 §5b is the exit's
documentation artifact: what snapshots guarantee per world class,
including the honest fourth class (live services, hardware: **no
world-state guarantee**; the brain persists, the world re-attaches at
boot).

The feature's tests then caught something older than the feature: a
plain-world resume on a fresh schedule diverged from its uninterrupted
run by **one ULP** in `pred_error_late`. The diagnosis walked the usual
ladder — capture doesn't perturb (control), plain worlds diverge too
(control), pre-010 code diverges too (stash control) — and landed on
group order: the blob recorded frame groups *sorted by dim* while the
live store holds them in *birth order*, and group iteration order feeds
per-step float accumulation, so restored runs summed in a different
order. Doc 06's core promise (resume ≡ uninterrupted, in bytes) had a
one-ULP hole since feature 003, invisible to every schedule tested until
now. Fixed by recording group order as lived; old blobs decode
unchanged (their order was lost at write time). The lesson joins the
collection: *byte-identity claims are only as strong as the orders they
preserve* — sorting is a mutation too. Gate: 285 tests green (8 net new).
Phase B closes: the platform the showcases need — watchable, mountable,
unbroken, parallel, persistent — exists end to end.

## Chapter 24 — The frontier drive: A4 closes at proper power (2026-07-14)

Chapter 18 ended with a dissolution and a named remainder: no blend
surface existed because curiosity and competence steer the lookahead
with one shared novelty statistic, and the only live path was a
per-candidate *learnability* signal (Doc 05's predicted-LP [O]).
Pre-registered and built in one arc (PREDLP-DIAGNOSIS, branch 012): the
**frontier drive** — pair the observation memory with the error recorded
at each visit, and value a lookahead candidate by whether error near it
has been *falling* (older-half minus newer-half of its k nearest
remembered neighbors, clamped at zero). Unlearnable regions read
flat-high → 0 (the noisy-TV guard, per-candidate for the first time);
mastered regions flat-low → 0 (no camping); frontiers positive. Pure
floats, no RNG, opt-in through the drive registry; the random baseline
untouched by construction; agency snapshots extend additively.

The measurement applied chapter 22's power lesson by pre-registration:
24 seeds, 4 arms × 2 dials × 3 horizons, 576 runs. Three findings:
**(1) The A4 exit criterion is met** — competence and the
frontier+competence blend beat random in a strict majority at every
horizon, both dials; chapter 18's mild-noise equivocation was
statistical power, not capability, and the roadmap's Phase A closes
with it. **(2) Frontier works exactly as designed and loses honestly
here**: positive and noninferior everywhere, occupancy between the
poles (competence −0.05 < frontier ≈ 0 < curiosity +0.01, the
registered ordering), but on a world whose unlearnable half is best
simply avoided, avoidance wins — frontier matches competence (5/6
noninferior), beats it nowhere. Recorded without spin; the worlds where
anti-camping should pay (mastered-then-changing, multi-region
learnable) are the named next tests, now properly instrumented.
**(3) The blend is finally real** — the independence of the frontier
term is unit-pinned, so `drive_weights` blends are no longer degenerate
relabelings. Gate green throughout; trail:
`design/validate/PREDLP-DIAGNOSIS.md`.

## Chapter template (append below)

```markdown
## Chapter N — <title> (<dates>)

<What happened, in a few sentences: the question, what was built/measured,
the honest outcome with key numbers.>
<What was refuted or reversed, if anything.>
<What it taught / what it opened.> Trail: <docs>; commits <hashes>.
```
