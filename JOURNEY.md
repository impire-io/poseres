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

## Where things stand (2026-07-19)

The project now has a product thesis and a milestone-gated plan — **an OSS
continuously-learning brain for hobbyists and makers**, `ROADMAP.md`
(Chapter 10), and the core mechanisms now have an interactive,
simulation-backed explainer for that audience (`explainer/index.html`,
Chapter 37). **The vision was re-broadened on 2026-07-19** (Chapter 42):
language learning reversed from non-goal to gated horizon question (the
teacher-world experiment), seeding/compounding intelligence named as
experiment space, and the working agreement now requires teach-back,
evidence-class tags, and recorded reversal conditions on direction
decisions. **Every design document (02–07) is built and validated** at the
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
named new open problem: channel-noise robustness — diagnosed in Chapter
25 and **closed opt-in in Chapter 30**: learned channel weighting,
feature 016 — L3 noise PASSES at unit amplitude at 24 seeds with the
weighting on; the default-config FAIL stands as the recorded reference). **Phase A closes
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
in the blob). **Hardware and simulators now mount through one seam**
(Chapter 26): the ROS2 adapter (feature 013) makes each topic a
first-class Doc 02 tool — declared anatomy, a control-tick step
discipline (publish → one tick → sample), an explicit hold-last-value
staleness policy with loud bounds — provable end-to-end on an in-package
fake transport (the gate needs no ROS2 anywhere), with a Gazebo rover in
Docker as the stepped, continuous, single-boot worked example; C2's
platform half landed, `requires-python` relaxed to 3.12 on a green
full-gate measurement, and free-running operation is the project's first
openly non-reproducible mode (Doc 06 §5b class 4, stated). **N worlds now
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
24). The camping-costs question is now **measured** (Chapter 31):
camping does cost — the camper recovers worst when the world shifts —
but realized LP does not collect the prize; competence guidance stands.
The predictive-LP form
then stopped at its own pre-registered gate (Chapter 32): no trend
statistic over the current 5-episode error memory can see a regime
change. The observation-space place memory
then failed its own offline gate too (Chapter 33): raw-observation
anchors are not shift-invariant. The emission-shift world then
completed the testbed pair and bracketed the problem with numbers
(Chapter 34: raw-obs places read ~1.5× background on a repaint, < 1× on
a territory move, vs the 4× bar). Action-context anchors then failed the same
gate (Chapter 35) — three spaces, one ~1–2× ceiling — and the diagnosis
moved down a level: the per-step errors-at-visit stream is a *tracking*
signal, and staleness detection needs a *transfer* signal (the
fair-judge lesson, applied to drives). The transfer stream was then
measured (Chapter 36): **the right signal at last** — staleness moves
the right way in all six shift cells on both modes, ratios to 7× where
tracking managed ~1× — but the frozen bars are unmet and the grid ended
still improving. The extended probe then measured the whole plane
(Chapter 38) and **closed the statistic family**: no windowed-median
level statistic on the transfer stream reaches the 4× bracket (best
worst-cell margin 0.21, at the *shallow* corner — the 022 trend was the
floor leg only), the per-frame fallback is structurally censored by
election (stale frames stop electing and leave the reading), and the
signal itself is immediate and real (~2× first-bin contrast, decaying
with relearning): a contrast problem, not a latency problem. The
change-point successor then closed the question end-to-end (Chapter
39): jump and accumulation statistics fail the same way level did —
the weak half of the shift cells never separates from benign
background at honest false-alarm rates (best ROC: 6/6 detection within
four episodes only at ~1.6% false-fire). The election stream — reading
the censor itself, staleness as who goes silent — then failed hardest
(Chapter 40): benign mass-silence events (up to ⅔ of established
frames in one episode, the drive's own movement between regions)
exceed every shift cell's peak. **Four signal families measured on one
testbed, one verdict: no passive statistic separates a world change
from the brain's own nonstationarity — the detector's background is
the brain itself.** The staleness-detection program pauses with its
map complete. **C1's runway is cleared** (Chapter 41): the reference-
scale lifetime question is answered at deployment length — no rot in
500k-step soaks (episodic stationary, continuous decelerating; cap
measured behaviorally free → C1 runs cap-on), resume byte-identical at
500k in every arm, and two honest bar-failures converted to sizing
facts (continuous rides the population ceiling at ~10% wall cost;
snapshot blobs grow ~8 B/step by design — bounded-trace option named
as a future feature). Open threads, in priority order: **C1** (build
and launch — posture green, config notes recorded); **scheduled
probing** (the named active successor: re-visit mastered ground under
a held policy and re-test — detection as a designed experiment, a Doc
05-level feature, when the program resumes); the ch. 39 tolerant-gate
conditional (~1.6% false-fire, if a deployment can afford it); and the
bounded-trace snapshot option (when a deployment's horizon demands
it). Snapshot support for anatomy-resized runs
shipped in Chapter 23. **A live brain now has an off-process presence**
(Chapters 27–28): the platform successors were sequenced (B6 → B7, one
transport built once; NATS-underneath-the-engine rejected on the
byte-identity constitution) and B6 landed the same day — `pra.nats`,
the tap that binds three existing injection seams (world-wrapper
mirror + pause gate, the B1 viewer's store capture, a snapshot-store
wrapper at the C4 write site): telemetry as versioned run-scoped
subjects, snapshots through a JetStream object store (shareable
brains, bought once for Phase D), a three-command control plane with
honestly-deferred snapshot fulfillment — observer safety proven by
byte-identity (attached/absent, outage-long, paused-and-resumed), the
run never waiting on the network, the whole gate on an in-repo fake
transport with zero skips, and the real stack measured green
end-to-end (`examples/nats/demo.py`, nats-server + nats-py 2.15,
then uninstalled and the gate re-run clean). Doc 06 §5b records every
NATS-touching mode's class; experience-in is named class 4 and not
built; inter-brain communication stays reserved subject space. **And
the brain has a face** (Chapter 29): `pra-dash`, a pure consumer of
the documented subjects — simple mode with the world's own view (the
rover mounts its existing three-call telemetry surface onto the bus
unchanged), advanced mode with the census history, honesty counters,
and the four control buttons, replies verbatim; observer safety
re-proven with the whole dashboard attached and polling, and one
instrument bug (per-subject seq-gap counting misreading the shared
mirror family) caught by an actual browser session and fixed with a
regression test. **Phase B is complete, B1–B7.** Next: the C1/C2
showcases, whose C2 research gate is named — learned channel
weighting, because real sensors are the chapter-25 failure mode.

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

## Chapter 25 — Channel noise: the score loses its gradient before the brain loses its structure (2026-07-14)

The ladder's first open problem (L3 noise mode: half the observation
carrying unit static; best_dim collapses to 1 in 5/8 seeds) got its
diagnosis, run in a parallel worktree alongside chapter 24's arc. A new
inert dial (`distractor_noise_std`, 1.0 = the recorded behavior,
byte-guarded) made the amplitude sweepable: harmless at sensor scale
(0.04 — PASS), verdict flicker from 0.1, robust break between 0.2 and
0.5, collapse at 1.0 — a widening instability band, not a threshold
(median improvement falls monotonically 0.485 → 0.107). The mechanism
is a measured three-leg compound: irreducible channel floors compress
the per-dim error span 6.5× (real, insufficient alone — the frozen
score minimum never reaches dim 1); unit static corrupts core learning
itself through the shared encoder (dim-3 asymptote ratio 1.61, over the
pre-registered 1.5× bar; intact at ≤ 0.5); and the floor holds every
frame's score above the absolute survival bar (winners 0.72–0.83 vs
bar ≈ 0.49–0.65), so nothing matures — a permanent conveyor judged at
ages where the transient surface is price-dominated and dim 1 wins
(judging-age basin depth 0.000 at σ=1.0 vs 0.119 at 0.04). Refuted:
election starvation (map fractions healthy throughout) and the
one-cause compression story. The remedy is named, not shipped, for a
measured reason: perfect score-side channel exclusion (computed from
the probe data) rescues σ=0.5 but not 1.0 — the encoder input path
needs the same treatment — so the fix is **learned channel weighting**
(an in-system per-channel floor estimator feeding both the survival
norm and the encoder), a real feature, not a dial. Trail:
`design/validate/CHANNELNOISE-DIAGNOSIS.md`; the dose–response dial
ships inert with byte-identity tests.

## Chapter 26 — Feature 013: the ROS2 adapter — robots are message streams, so topics became tools (2026-07-14)

The question was C2's, generalized: one adapter for everything that speaks
ROS2 — Gazebo, Webots, real hardware — instead of a one-off body per
device. The shape deliberately inverts 007: a Gymnasium env is *one world
object*, so 007 wrapped it as one EventSource; a robot is *N independent
message streams*, so each topic became a first-class Doc 02 tool
(`TopicSensor`/`CommandActuator` around a `Transport` seam), which keeps
mid-run `register_sensor` — snapping a sensor onto a running robot — alive
for free. The named design decision is **time**: one engine step is
publish → advance exactly one control tick → sample every sensor's latest
cached message, with the tick owned by the body (never an actuator, so the
one-tick-per-step invariant survives any registered tool) and asserted
against a journaling fake transport, not assumed. Its companion is the
**staleness policy**: hold-last-value with per-sensor counters outside the
learning surface, a startup gate before the first observation, and a loud
bound — which promptly fired in anger *during the feature's own authoring*:
the quickstart's scripted world ran dry at 6,000 ticks because the default
schedule actually consumes 13,001 (325 episodes — `effective_n_cycles`
stretches to the last horizon checkpoint — a wrong-arithmetic trap the
guard caught exactly as designed). Determinism claims are split honestly:
the adapter carries **zero randomness** (simpler than 007's pure state
read — the only honest claim is conditional, so the right amount is none;
byte-identity proven on scripted streams), while free-running operation is
the project's first openly non-reproducible mode (Doc 06 §5b class 4, now
naming this adapter). Two firsts in the plumbing: rclpy has no honest pip
extra (it ships with ROS distributions), so the entire quality gate runs
on the in-package `FakeTransport` — and `requires-python` was relaxed to
3.12 the project's way: the full gate, byte-frozen baseline included, run
green on CPython 3.12.8 *first*, because Jazzy's rclpy binds to Ubuntu
24.04's interpreter. The worked example — a minimal diff-drive rover
(5-beam lidar, odometry, cmd_vel) in a Gazebo arena, stepped through the
bridged `ControlWorld` service, continuous single-boot — was built and run
end-to-end in its Docker container during the feature, and the first real
run earned its keep: it surfaced **non-finite lidar beams** (+inf no-hit,
−inf below-min-range, NaN invalid) silently NaN-poisoning the whole
prediction-error surface — the summary read `nan early → nan late` while
the exit code smiled. The contract was amended openly (research R5): the
adapter now rejects non-finite deliveries loudly, naming the fix (a
sanitizing callable `extract`, which is what the example's lidar clamp
does — to the sensor's own range bounds). The rerun prints finite,
honest numbers. One ROS-classic snag also recorded: ROS setup scripts
violate `set -u`. C2's platform half is landed; the physical build,
guide, and growth video remain the showcase.
Trail: `specs/013-ros2-adapter/` (spec, plan, research R1–R9, contracts,
quickstart), `examples/ros2/`.

## Chapter 27 — The platform successors: NATS at the seams, the dashboard behind it, and the robot's real gate (2026-07-18)

A sequencing decision, not a build — recorded because roadmap changes are
decisions. Three candidate directions were on the table: put NATS
"underneath" PRA as its storage and messaging substrate, build a web
dashboard/monitor, and start the physical robot. Examining them against
the repo's own record reordered all three.

The NATS direction survived; its framing did not. **Rejected: NATS
underneath the engine.** The fast loop is a batched in-process kernel
(~60k obs×frame evals/s, feature 001) whose entire validation story is
byte-identity — a network hop inside it would break throughput and the
T1–T7 gate at once. What the architecture actually permits — and what the
horizon-ambitions chain (A1 → B4 → external bus backend → multi-machine)
had already named as the step after B4, which closed in chapter 22 — is
**NATS at the seams, opt-in, reference byte-frozen**: the Doc 02 bus as
telemetry subjects, the SnapshotStore over a JetStream object store
(Phase D's shareable-brains transport, bought once), a request/reply
control plane, with inter-brain communication named as the horizon this
enables but excluded from the exit. The determinism line is pre-drawn:
telemetry *out* is observer-safe (the B1 viewer precedent); experience
*in* over a network joins free-running ROS2 as a Doc 06 §5b class-4
mode, stated up front. Scheduled as **B6**, design-first.

The dashboard turned out to be half-built and half-mis-sequenced: the B1
viewer already proved the observer discipline (byte-identity with the
viewer attached), and the dashboard's natural data source is B6's
subjects — building it first would mean building the transport twice.
Scheduled as **B7, gated on B6**, with its two purposes split honestly:
the monitor half (simple + advanced modes) is an instrument; the
"show what makes PRA unique" half is a showcase spend under principle 1.

The robot was never a new item — it is C2's remaining showcase half
(the platform landed as feature 013) — but writing it down surfaced its
real gate: chapter 26's Gazebo lidar NaN-poisoned a run, chapter 25
measured channel static collapsing selection, and a physical robot's
sensors are exactly that world. **Learned channel weighting is a de
facto research gate for the C2 showcase**, now stated in the roadmap;
the CAD/electronics build may proceed in parallel because hardware is
cheap and the brain is the bottleneck. Nothing was built in this
chapter; the tracking system remains the existing one (roadmap exit
criteria + spec-kit + this file) — a separate workflow tool was
considered and rejected as duplication. Trail: `ROADMAP.md` diff (B6,
B7, C2 note, sequencing summary); committed with this chapter.

## Chapter 28 — NATS at the seams: the off-process window that provably isn't there (2026-07-18)

B6 landed the same day it was scheduled — spec, plan, build, and the
real-stack proof in one sitting. The feature gives a live run an
off-process presence over NATS/JetStream: telemetry fanned out under a
versioned run-scoped subject scheme (`pra.v1.run.<id>.…`), snapshots
through a JetStream object store behind the existing four-method store
seam (Phase D's shareable-brains transport, bought once), and a
three-command request/reply control plane (inspect, pause/resume,
snapshot) — all opt-in, all through existing injection seams, zero
edits under `core/`, `harness/`, `persistence/`, or `config.py`.

**The design died once before it was born, on a read fact.** The
obvious shape — wrap the Doc 02 bus and mirror its published events —
observes nothing: the engine's hot loop drives the batched
`FrameProcessor` directly, and `Bus.publish` is only the contract-test
path (`bus.py`'s own docstring says so). What the B1 viewer had
actually proven was subtler: capture references at injection time,
mirror plain values on the run path, derive everything on a background
thread. `NatsTap` generalizes exactly that, binding three seams — a
delegating world wrapper (the per-step mirror *and* the pause gate: one
`Event.is_set` check, two integer increments, one small copy, one
bounded-deque append per step; no RNG, no floats, no locks), the
viewer's `bus_factory` store capture (the census derives off-path with
torn-read fallback), and a delegating snapshot-store wrapper at the
engine's C4 write site. Observer safety is proven, not argued:
same-seed runs with the backend absent and attached are
byte-identical, including multi-stream continuous, including a
transport that is down for the run's whole life (drops derived from
sequence gaps — the honesty meter), including a paused-then-resumed
run against a never-paused one.

**The honest decision of the chapter is the snapshot command.** A
snapshot is only well-defined at C4 — no external thread can force one
mid-cycle without tearing the state Doc 06 exists to protect — so
snapshot-on-request is *deferred fulfillment*: the reply arrives when
the engine's own cadence write is observed, and unconfigured runs get
an immediate error naming what is missing. Payloads carry no
wall-clock time (sequence numbers and the run's own counters only), so
the fake-transport journals are byte-deterministic and the contract
tests compare them as bytes.

The gate runs entirely on an in-repo fake transport — no NATS library,
no server, zero skips (the 013 pattern; unlike rclpy, `nats-py` is
pip-installable, so the `[nats]` extra honestly exists). The real
stack was **measured, not hoped**: `examples/nats/demo.py` ran green
end-to-end on first attempt against a local `nats-server -js` with
`nats-py` 2.15 — discovery, live telemetry in a second process, pause
frozen and verified twice, snapshot fulfilled at the C4 boundary
(`snap-000000000300-00002`), pulled back from JetStream and decoded as
a real brain, all proofs pass — then the library was uninstalled and
the full gate re-run clean without it. Doc 06 §5b now records every
NATS-touching mode's reproducibility class, with experience-in named
class 4 and *not built*, and inter-brain communication left as reserved
subject space (`pra.v1.brain.*`) — research, not plumbing. B7's gate is
met. Trail: `specs/014-nats-bus-backend/` (spec, plan, research R1–R9,
data-model, contracts, quickstart, tasks), `src/pra/nats/`,
`examples/nats/`; commits `30a1952` (spec), `49ea413` (plan),
`18447c2` (tasks), and the implementation commits following.

## Chapter 29 — One face for any brain: the dashboard, and the browser that caught a bug (2026-07-18)

B7 landed hours after its gate opened, closing Phase B. The dashboard
is contractually a *pure consumer* of the B6 surface — `pra.dash`
imports the subject names and the transport protocol and structurally
nothing else, collecting the promise B6's SC-006 made (that B7 could be
built against the documented scheme without reading B6's source). One
`DashboardModel` turns received payloads into per-run state (identity,
authoritative state, monotonic liveness, bounded census history, the
honesty counters, snapshot notices); one stdlib server serves a single
self-contained page (`pra-dash`); simple mode is for a person standing
in front of the brain, advanced mode is the researcher's instrument
panel with the four control buttons and every reply — B6's error
grammar included — surfaced verbatim.

The roadmap's named gap closed on the tap's side of the fence, where
observer safety is provable: a **world-view telemetry family**
(`tele.view.static` once + heartbeat, `tele.view.live` per record)
whose adapter exposes exactly the three-call surface the rover world
has spoken since feature 006 (`attach_layout` / `record_reset` /
`record_step`) — so the rover mounted on the bus **unchanged**, and
the B1 viewer's world now renders from any machine. Observer safety
was re-proven at the new layer: byte-identity with the whole dashboard
attached and hammered by a polling thread (reference, rover-with-view,
multi-stream continuous, attach-and-detach mid-run), and
pause-through-the-dashboard byte-identical to never-paused.

The chapter's recorded lesson: **the browser is an instrument too.**
The headless real-stack demo passed on the first run (world view
consumed and served, pause frozen at step 145, snapshot fulfilled
through the dashboard's own endpoint) — but opening the page in an
actual browser showed `SEQ GAPS 1171` on a run with zero drops. The
model had derived gaps from `tele.step` sequence numbers alone, and
the tap's mirror family is *shared* — steps, episodes, views, and
snapshots interleave one sequence, so every step legitimately skips.
Gap detection now runs on the union of the family (regression test
recorded), which is exactly the kind of honest-instrument bug the
endpoint tests could never see: the data was correct; the *reading* of
it lied. Both modes were then verified rendering live — arena,
obstacles, pose, trail, census history, histogram, counters. Phase B
closes with the brain watchable, manageable, and shareable from
anywhere, and the whole gate still needs no NATS, no server, and no
browser. Trail: `specs/015-web-dashboard/` (spec, plan, research
R1–R7, data-model, contracts, quickstart, tasks), `src/pra/dash/`,
`examples/nats/dashboard_demo.py`; commits `5b91d90` (spec), `d45baf3`
(plan), `a9ce3a3` (tasks), and the implementation commits following.

## Chapter 30 — Learned channel weighting: the score gets its gradient back (2026-07-18)

The remedy chapter 25 named got built, and the arc ran gate-first: the
pre-registration froze every bar and exit *before* any run, the oracle
experiment ran *before* any estimator code existed, and the design's
spine was never a tuning knob — the **transport argument** (static
weighted at floor 0.2 makes every computation at unit amplitude
operation-for-operation equivalent to σ_d = 0.2, an operating point
already measured PASS) was a sharp falsifiable prediction, and it held:
oracle weights on both legs reproduced the σ_d = 0.2 surfaces at
σ_d = 1.0 (same minima, depth ratios 1.04–1.16), healed the encoder
corruption (core error 0.98–1.02× the healthy baseline vs 1.61×
corrupted), and broke the conveyor live (8/8 seeds). The estimator that
then earned the oracle's job is deliberately dumb: per-channel **lag-1
autocorrelation** of the raw observation stream — learning-free (no
circular dependence on the learner it rescues), un-gameable (no frame
state touches the metric frames are judged by), and amplitude-invariant
(P1 measured identical separation margins at every dose — the exact
failure mode of the residual-ratio alternative, structurally absent).
One weight vector feeds both legs, recomputed only at episode
boundaries, floor-clipped: **full exclusion is measured worse** (f = 0
lets spare capacity ride free and the parsimony price can't hold the
elbow — min 8 at age 24, dose-invariantly). The result: **L3 noise
PASSES at unit amplitude under the unchanged criterion at 24-seed power**
(21/18/20 of 24 within one at every checkpoint), the whole dose grid
passes at 8 seeds, 24/24 conveyor broken (winners 0.23–0.37 under bars
0.39–0.61 where the record has 0.72–0.83 above them), and E4 measures no
harm anywhere — with one flip in the good direction: L1@0.8's recorded
brain-finding FAIL (region noise widening the landing) passes with
weighting on, twin-match 4/8 → 8/8. The recorded L3 FAIL stands
untouched; the rescue is a dated addendum beside it, opt-in
(`channel_weight_floor = 0.2`).

Reversals and letters faced, kept in the record: the arc's own first E1b
run measured **the wrong world** — a bare `Engine` builds the reference
world regardless of `Config.world`, and only the shipped mechanism's
smoke run exposed it (twenty live weights near 1.0 are impossible
against real static); the engine now refuses the combination, and the
void table stays in the trail beside the corrected one. Three clause
letters broke against their own earlier results and were amended openly
(the σ0.5 age-48 min the healthy anchors themselves don't meet; dose
monotonicity that amplitude-invariance had already made impossible; a
no-suppression bar calibrated on 5 reads applied to a 50-read order
statistic — resolved by measuring harm, and there was none). Two
informative improvement bars missed by 0.006/0.014 against constants
derived on the other construction stream — recorded, not re-derived. And
the pairing story got its honest footnote: the feature draws zero RNG,
but a weighted election can shift a no-map birth and re-align the shared
generator — measured tiny (paired occupancies match to ~0.01).

What it opened: C2's research gate is cleared — the robot showcase no
longer waits on the brain flailing in static. The relative survival bar
(D1) stays a named conditional deferral (its trigger never fired); the
whiteness×floor hybrid is the named successor if a world with
correlated-but-unpredictable channels enters the ladder; and the L1@0.8
flip suggests the weighting has something to say about region noise too.
Trail: `design/validate/CHANNELWEIGHT-DIAGNOSIS.md` (pre-registration,
P1/E1a/E1b/E2/E3/E4, outcome), `specs/016-channel-weighting/` (spec,
plan, research, contracts, tasks); commits `bdb8111` (spec), `f716b36`
(pre-registration), `c0065d8` (P1), `db8df8e` (E1), `b2a6bf0` (plan),
`db21724` (mechanism), `1ba071b` (E2), `ad39e69` (E3/E4/outcome).

## Chapter 31 — The camping bill arrives, and nobody collects it (2026-07-18)

Chapter 24 left the frontier drive with an asterisk: validated
non-inferior, but only *matching* competence on worlds where avoidance
is optimal. This arc built the two worlds the asterisk named — a
**shifting world** (the reference until S emitted steps, then the
action-displacement set swaps to one drawn at construction: emission
unchanged, mastered transition knowledge silently stale, zero RNG at
shift time) and a **multi-region world** (the L1 mechanism generalized
to per-region noise levels, all inside the learnable band — difficulty
without noise traps) — both opt-in behind the world seam, byte-identical
when off, snapshot-safe across the shift. Then the chapter-24 instrument
ran on them: 4 arms × 3 horizons × 24 seeds × 2 worlds, 576 runs,
against bars frozen before any run.

The worlds did their jobs — and produced the arc's cleanest fact:
**camping measurably costs.** Post-shift, competence — the camper — has
the *worst* recovery of all four arms (median post-shift improvement
+0.038 vs random's +0.070); even undirected exploration handles a moved
world better than a drive parked on banked mastery. But the drive built
to collect that prize doesn't: frontier's letter-PASS over competence
post-shift (14/24, +0.027) is exactly random's edge (17/24, +0.027) — a
pre-registered context row that converts a passing letter into an
honest null. On the multi-region world the frontier steers precisely as
designed (harder-region occupancy above competence at every horizon,
14/15/14 of 24) and *pays* for the visits (noninferiority FAIL at two
horizons — X2, steering with a cost). The vs-random sanity clause
failed on both worlds, and its diagnosis was already on file: the BLEND
arc's regime rule — directedness pays in proportion to how much the
world punishes indiscriminate experience — and these all-learnable
worlds barely punish it. Recorded as clause calibration: on mild
worlds, register competence-relative bars, not random-relative ones.

What it taught: realized local progress is a **lagging indicator** —
progress already banked near a candidate says nothing about progress
still available there, so the signal arrives after the frontier has
moved. The successor sharpens accordingly: fully *predictive* LP (a
per-candidate error model), which now has two purpose-built testbeds
and recorded baselines waiting. Doc 05 guidance is unchanged by
measurement — competence stands, its one measured weakness (worst
post-shift recovery) not yet exploitable by anything in the registry.
Trail: `design/validate/CAMPING-DIAGNOSIS.md` (pre-registration, E0–E2,
outcome), `specs/017-camping-worlds/`; commits `314750a` (spec),
`8d5f4dc` (pre-registration), `e8c7726` (worlds), `9e8ea1c` (results +
outcome).

## Chapter 32 — The scout that never left camp: a gate does its job (2026-07-18)

The shortest arc in the record, and deliberately so. Chapter 31 named
the frontier's failure mechanism — realized LP is a lagging indicator —
and the obvious fix wrote itself: the **scout drive**, the same
2k-neighbor statistic with the halves swapped (`max(0, newer − older)`),
positive where local error has *risen* — stale knowledge, the shift
signature — zero on flat-high noise and flat-low mastery, no new
constants. The pre-registration froze the bars competence- AND
random-relative (the chapter-31 clause lesson), pointed the arc at the
frozen 017 grid as an exactly-paired baseline, and put one probe in
front of all code: P1, the signal shapes on *real traces*, with X0
saying stop if the mirror can't see the shift.

It can't — and the reason is worth more than the drive would have been.
On live frontier-arm traces the scout median is zero everywhere,
post-shift included, while the frontier median is positive everywhere —
**including on mastered pre-shift ground** (0.03–0.07). Fine-grained
bins show the shift is not invisible (scout fires on 26% of post-shift
reads, maxima ~3× background in the memory-straddle window) but not
separable: it also fires pre-shift, and the frontier reads positive
straight through. The cause is representation, not arithmetic: the
err@visit memory is a **200-entry sliding FIFO (~5 episodes)** — the
pre-shift baseline is forgotten within ~200 steps of the shift, and the
window's residual recent-trend noise feeds both statistics wherever
global error drifts. A retrospective light on chapter 24, recorded
openly: part of the frontier's recorded signal was this same
sliding-window trend, one more reason its live edges matched random's.

The arc stopped at X0 with **zero src changes** — the pre-registered
complete deliverable. What it bought: the successor is now measured,
not conjectured — predictive LP needs **place-indexed, long-horizon
error memory** (slow decay, spatially anchored: "what error was here
when I knew this region" must survive long enough to compare with "what
error is here now"), a Doc 05 design feature with its own
snapshot/scale surface. The 017 worlds and their 576-run grid still
wait as its testbed. Doc 05 guidance unchanged: competence stands.
Trail: `design/validate/SCOUT-DIAGNOSIS.md` (pre-registration, P1,
outcome), `specs/018-predictive-lp/spec.md`; commits `2e90c99`
(spec + pre-registration), and this close.

## Chapter 33 — Places that move: the map fails its gate, and names its successor twice over (2026-07-18)

The chapter-32 successor got its arc: a place-indexed error memory — K
anchor observations allocated deterministically from episode starts,
each holding a fast error EMA and the running *minimum* of that EMA
("the best I ever knew this place"), staleness = fast − best, one new
constant, the scout drive reading it. The pre-registration put an
offline gate in front of all code: replay the frozen arithmetic over
captured live traces and demand post-shift staleness separate from
pre-shift and benign background by 4×.

It failed — informatively, twice. As registered, benign ground read
~0.1 staleness (a running min under fast smoothing skims the lucky lows
of a spiky error series) and, the tell, **post-shift staleness was
LOWER than pre-shift in all three seeds.** One design revision was
allowed by an openly-recorded amendment of the exit (the house's
bounded-revision norm from the 016 arc; bars untouched): constant-free
double smoothing. It changed nothing — because the binding break is not
arithmetic. **A displacement shift moves where the brain goes**: the
visited observation distribution itself changes, post-shift traffic
rarely returns to the anchors whose minima encode pre-shift mastery,
and a place-anchored comparison has nothing to compare.
Raw-observation places are not shift-invariant in this world family.

The arc closed at X0 with zero src changes — the second gate-stop in a
row, both priced in by their pre-registrations as complete
deliverables. What this one bought: the successor is now posed sharply,
in two parts — error memory anchored in a **shift-invariant space**
(the frame's own pose/encoding survives the 017 shift; raw observations
do not) with **spike-robust per-cell statistics** (median-of-means, not
EMA minima) — plus a testbed note: the shifting world confounds
"knowledge went stale" with "territory changed", so an emission-shift
world (dynamics fixed, appearance changed) belongs on the ladder before
the next detector design. Doc 05 guidance unchanged: competence stands.
Trail: `design/validate/PLACEMEM-DIAGNOSIS.md`;
`specs/019-place-memory/spec.md`; commit `f79ee57` and this close.

## Chapter 34 — The repainted world: the testbed pair closes, and brackets the problem (2026-07-18)

Chapter 33's debt was a world, and it cost one dial: `shift_mode` on the
shifting world. `"dynamics"` stays the recorded 017 behavior
byte-identically; `"emission"` swaps the per-object emission matrices at
the boundary (drawn at construction after all other draws, zero RNG at
shift time) while displacements never change — appearance moves,
territory does not. Swap semantics, dynamics invariance, and state
capture across the shift are unit-tested; the whole gate stays green.

The arc's pre-registered first read completed the picture with a
baseline the next design must beat, and its prediction was honestly
left open between two mechanisms — both turned out true in parts. The
raw-observation place memory (the ch. 33 replay, revision-1 arithmetic,
recorded as such) reads the emission shift *directionally* — post-shift
staleness rises in 2/3 seeds (0.172/0.178 vs ~0.11 background), the
opposite sign from the dynamics shift's 3/3 post-below-pre — because a
repaint leaves every post-shift observation landing on *some* mastered
anchor, while a territory move leaves mastered anchors unvisited. But
sensing is not detecting: ~1.5× background against the 4× bar, one seed
flat. **The testbed pair now brackets the design space with numbers**:
a shift-invariant error memory must clear 4× separation on both modes,
from measured starting points of ~1.5× (emission) and < 1× (dynamics).
That — pose/encoding anchors with spike-robust per-cell statistics,
judged against this bracket — is the successor arc, unchanged in name,
now fully instrumented. Trail: `design/validate/EMSHIFT-DIAGNOSIS.md`;
`specs/020-emission-shift/spec.md`; commit `3500576` and this close.

## Chapter 35 — Three spaces, one ceiling: the signal was the problem all along (2026-07-18)

The third anchor space for staleness detection was the most elegant and
the cheapest to test: index error memory by the brain's own last-m
actions — a space the world cannot move by construction, with
spike-robust cells (windowed medians, running best-median) replacing
the arithmetic that had painted phantom staleness. The offline gate ran
the frozen (m, W) grid over captured traces from BOTH shift modes plus
the benign floor, against the chapter-34 bracket.

Every grid point failed. Emission mode separates directionally but
weakly (~1.5–2×, never 4×); dynamics mode stays blind (~1×); the benign
floor never approaches zero. And with that, three consecutive
eliminations — sliding FIFOs (ch. 32), observation places (ch. 33),
action contexts (ch. 35) — share one ceiling, which is the tell: **the
anchor space was never the problem. The signal is.** Per-step
errors-at-visit are a *tracking* error: they move with ecology churn,
election composition, and ongoing learning everywhere, and that
within-life nonstationarity is background no indexing scheme can
cancel. The project learned exactly this lesson once before, one level
down — all-step EMAs score tracking, not structure, and the remedy was
the fair judge scoring episode-start transfer. The staleness program
needs the same move at the drive level: a **transfer-error stream**
(episode-start prediction errors, read before within-episode adaptation
masks the damage) as the input to any staleness memory, with all three
eliminated spaces available for retry once the signal is right.

Third gate-stop in a row, each cheaper than the last (this one reused
every instrument and wrote no src), and jointly they bought what a
lucky pass never could: measured brackets on both world modes, three
eliminated representations, and a signal-level diagnosis with an
in-house precedent for the fix. Doc 05 guidance unchanged — competence
stands. Trail: `design/validate/CONTEXTMEM-DIAGNOSIS.md`;
`specs/021-context-memory/spec.md`; commit `bba601a` and this close.

## Chapter 36 — The vein is found: transfer errors carry what tracking drowns (2026-07-18)

The fourth staleness gate, and the first to strike signal. The arc
changed nothing but the input: the same cell arithmetic and the same
chapter-34 bracket, computed on the **transfer stream** — errors at the
first K = 5 steps of each episode, the fair judge's own recorded
constant reused — instead of the all-step tracking stream that three
anchor spaces had failed on identically. At the best frozen setting
(two-action context cells, window 16), staleness moved the right way in
**all six** shift cells on **both** world-change modes — the tracking
stream never once managed direction on a dynamics shift — with ratios
2.5–7.2× (dynamics) and 1.5–3.3× (emission) against a benign floor that
collapsed monotonically as cells deepened (0.163 → 0.027 across the
grid). The frozen bars are still unmet: two seeds sit at ~1.5× and the
floor is not 4×-cleared, and the grid ended exactly where its own trend
was still improving. Extending it post hoc would be the tuning the
discipline forbids, so the arc closed at X0 — the fourth consecutive
zero-src gate-stop — with the successor probe named *from the measured
trend*: richer context cells and longer windows on the transfer stream,
pre-registered fresh, with per-frame transfer error as the fallback
space. The staleness program's map is now clean: right signal
(transfer), known direction (slower, higher-resolution statistics),
testbeds and brackets standing ready. Doc 05 guidance unchanged —
competence stands. Trail: `design/validate/TRANSFERSIG-DIAGNOSIS.md`;
commits `51173f0` (pre-registration), `a75e18d` (result + outcome).

## Chapter 37 — The mechanisms, playable: an interactive explainer that runs the real math (2026-07-18)

The question was communication, not capability: could the core mechanisms
be *shown* rather than described — honestly, to the hobbyist audience the
product thesis names? `explainer/index.html` is a single self-contained
page with nine live sections (loop, triplet, frame, coverage-fair
scoring, parsimony price, spawn-and-select, drives, channel weighting,
persistence), each backed by a browser simulation running the Doc 03–06
update equations — tanh nets with per-element gradient clipping,
observation-space prediction error, coverage-fair EMAs, the falling
population-scaled threshold, the five-array whiteness estimator, JSON
snapshot/restore — at demo scale (smaller nets, faster EMA clocks),
verified headless in Node before shipping.

Building it re-derived three recorded findings the hard way. The first
demo ecology reproduced the youth conveyor exactly (threshold below any
achievable score; 660 evictions, zero mature frames) until the bar and
protection window were retuned — and a fit gate below a newborn's
starting error blocked bootstrap entirely, the demo-scale shadow of
young-frame protection. The channel-static demo refused to fake the
collapse at single-frame scale (world-channel learning was fine); what
honestly reproduces is the *judge-side floor* — unweighted survival fit
0.44 vs 0.30 weighted against a 0.35 bar, so the page shows maturity
rescue, not learning rescue. And the corridor drive demo could not be
tuned to make realized-LP curiosity hold the frontier: it drifts to the
noisy TV (0.72–0.95 occupancy) while competence avoids it entirely — so
the page says so, matching the −0.062/+0.067 record instead of
prettifying it. Verified: dim ordering on a true-dim-3 world, price
winner moving 5→3→1 with `w_complexity`, cheat-vs-honest EMA gap, ρ̂
separation (world 0.8–0.9, static ≤0.11, weights at floor), bit-identical
resume over 150 resumed steps. Trail: `explainer/index.html`; this close.
(Numbering note: authored as "Chapter 35" in a parallel session while
chapters 35–36 landed on main; renumbered mechanically to 37 at merge,
content untouched.)

## Chapter 38 — The plane is measured: level statistics close, two doors open (2026-07-19)

The 022 successor ran exactly as named: richer context cells (phase,
ctx3/ctx4, context⊗phase) and longer windows (to W=64) on the transfer
stream, at a reading-count-parity post span (6760..10600), with per-frame
transfer error as the frozen fallback and — new — a held-out confirmation
tier so a 32-setting grid could not buy a pass by search. The I0
instrument-reproduction gate fired first (XI): the recorded 022 decimals
do not reproduce under the registered arithmetic or five nearby variants
— but every recorded *conclusion* does (direction universal, monotone
benign collapse 0.180→0.030 vs recorded 0.163→0.027, bars unmet, floor
as blocker), the residue is most consistent with an unrecorded join
detail in the retired 022 scratchpad, and the reconciliation was
committed before any extended number was read. The instrument of record
is now written down.

The extension itself refuted the trend it was built to ride. The benign
floor does keep falling with resolution (to 0.010) but the post-shift
response dies faster; the worst-cell margin (post ÷ max(4·pre, 4·benign))
is maximized at the *shallow* corner — ctx1/W8, 0.21, ~5× short — so
022's "grid ended still improving" was the floor leg only, and no
windowed-median level statistic on this stream reaches the 4× bracket.
The per-frame fallback failed more sharply: directionally dead (post ≈
pre, one emission seed *falls*), because **election censors the signal**
— frames the shift hurt stop clearing the fit gate and leave the reading
population. Meanwhile the trajectory read shows the signal itself is
immediate and real: first-bin elevation on all six cells at ~2× the
trailing background, decaying over ~6–16 cycles as the brain relearns.
No latency problem — a contrast problem.

Fifth consecutive zero-src gate-stop, and the successors are named by
the numbers: a **self-normalized change-point form** on the same
transfer stream (judged by hit/false-alarm counts on the testbed pair,
bars pre-registered fresh), and the **election stream as the fallback
space** — staleness as who goes silent, not whose error rises. Doc 05
guidance unchanged: competence stands. Trail:
`design/validate/TRANSFERSTALE-DIAGNOSIS.md`; commits `d1cf02d`
(pre-registration), `34ac8c6` (I0 reconciliation), `8fd7d52` (close).

## Chapter 39 — Not the statistic: the population transfer read closes end-to-end (2026-07-19)

The ch. 38 successor ran the same day, on the same fourteen traces (the
instrument of record, reused verbatim): a change-point probe — does the
jump against the stream's *own recent past* separate, where level bars
against a cross-world floor could not? Hit/false-alarm bars were frozen
fresh (fire in the first two post-shift cycles on all six cells, zero
false alarms pre-shift and benign; 023's held-out confirmation tier
kept), with Z-jump (median/MAD window contrast) as P1 and Page–Hinkley
accumulation as the frozen fallback.

Both closed at X0, and together they finish the question. Z-jump is
structurally blocked: at every window shape the background's largest
excursion (z ≈ 2–7) exceeds the weakest shift cells' peaks (z ≈ 1–2) —
no threshold, in or out of the grid, could separate. Page–Hinkley
measures the whole trade instead: 6/6 detection within four episodes at
the sensitive corner, but at a ~1.6% false-fire rate; every
near-zero-false-alarm setting detects at most one cell. Three statistic
families — level (ch. 38), jump, accumulation — now share one verdict
on one testbed: the weak half of the shift cells is statistically
indistinguishable from benign background in the population transfer
stream. It was never the statistic. The recorded conditional (a
tolerant ~2%-false-fire gate for a drive that can afford wasted
exploration) is named, not smuggled in; the front door is now the
**election stream** — staleness as who goes silent, the mechanism P2 of
ch. 38 exposed, and the cheapest instrument in the program (the engine
already counts elections). Doc 05 guidance unchanged: competence
stands. Trail: `design/validate/CHANGEPOINT-DIAGNOSIS.md`; commits
`6537743` (pre-registration), `05b6f25` (close).

## Chapter 40 — Reading the censor: the fourth family closes and the map is complete (2026-07-19)

Chapter 38 exposed the censorship mechanism — frames a shift hurts stop
electing and vanish from every error statistic — and chapter 39 named
the election stream itself as the front door: staleness as *who goes
silent*. This arc read it. The 023 captures already carried the full
per-step electing-id stream; a lifecycle extension (birth/evict events,
proven non-perturbing by byte-identity against all fourteen 023 trace
files) supplied aliveness, and the silence statistic was frozen first:
the fraction of established frames (electing in every one of the last
M episodes) that go completely quiet in an episode while still alive —
eviction excluded as the ecology's own response, hit/false-alarm bars
and the held-out tier inherited from 024.

It failed hardest of all — X0 at every setting, and for the first time
not even the strong cells separate. Emission shifts silence a third to
half of established frames; the *benign* world silences up to
two-thirds in a single episode, because the drive moves the policy
between regions and an episode spent elsewhere silences the other
region's specialists en masse — and the pre-shift reference world's
ecology churn does the same. The mapped-drop fallback inherited the
identical trade (5/6 hits only at 51–69 false alarms). The readings
are invariant to the statistic's own dials; the verdict is not a
tuning accident.

Four signal families — error level, error jump, error accumulation,
election silence — now stand measured on one frozen testbed with one
shared verdict: **no passive statistic separates a world change from
the brain's own nonstationarity at honest false-alarm rates. The
detector's background is the brain itself.** The successor the numbers
name is active, not passive: **scheduled probing** — deliberately
re-visit mastered ground under a held policy and re-test, detection as
a designed experiment (a Doc 05-level feature with its own costs and
no-harm surface). The ch. 39 tolerant gate stays recorded for
deployments that can afford ~1.6% false fires, and Doc 05's guidance
never depended on detection: competence stands. With the map complete
the detection program pauses, and the roadmap's front returns to C1.
Trail: `design/validate/ELECTSTREAM-DIAGNOSIS.md`; commits `1881dfc`
(pre-registration), `bc05ba6` (close).

## Chapter 41 — The soak before the weeks: C1's deferred questions answered in an afternoon (2026-07-19)

With the staleness program paused and C1 the front, two recorded
deferrals sat under the multi-week run: does reference-scale weight rot
appear at deployment lengths (the ch. 14 open tail), and what does the
ch. 21 drift caveat mean for an unbroken run? Rather than discover the
answers at week two of a live deployment, arc 026 paid for them in
compute: sixteen 500,200-step runs (the C1 cooldown arithmetic),
episodic × continuous, cap off × on, competence drive, instrumented
entirely through snapshots — plus four resumed half-runs to exercise
the persistence guarantee at length.

The headline: **no rot at reference scale over a C1 lifetime.**
Episodic norms are stationary; continuous norms grow slowly and
decelerate but have not plateaued by 500k steps — and since the cap-on
controls show capping is behaviorally free (identical early/late
errors to three decimals), the recorded recommendation is simply to
run C1 with the cap on and close the tail. **Resume is byte-identical
at 500k steps in all four arms** — Doc 06's constitution, now
exercised at deployment length. Two frozen bars failed honestly and
both diagnoses came back "by construction, not defect": continuous
mode fills the population budget and rides it forever at max_frames +
spawn_per_cycle (the evict-then-spawn ordering; measured wall cost of
a ceiling-full brain: ~10%), and snapshot blobs grow ~8 bytes/step
without bound because the per-step error trace is deliberately carried
in-state (feature 003) — 2–20 MB over a three-month C1 run, tolerable,
with a bounded-trace snapshot option named as a future feature that
must first resolve its Doc 06 semantics. Zero src changes; the
mis-anchored bars are recorded as such with the numbers beside them.
**C1 launch posture: GREEN** — cap on, snapshot cadence sized to the
growth, population budgeted at the ceiling. Trail:
`design/validate/C1SOAK-DIAGNOSIS.md`; commits `8ff6808`
(pre-registration), `53437b0` (close).

## Chapter 42 — The vision re-broadened: language returns as a gated horizon (2026-07-19)

Not a build or a measurement — a direction decision, recorded with its
reversal conditions. Daan reviewed the project's trajectory and judged
that the iterative narrowing had drifted past his intent: the 2026-07-08
thesis ("not vs LLMs on language"; hobbyist scope) had hardened into
ROADMAP language that steered every session away from ambitions he still
holds. The restated belief: PRA is an alternative intelligence approach —
a continuously-learning brain that can be snapshotted and **cloned as a
seed** so knowledge compounds across brains, works in **huge worlds**,
and — per the founding bet in `pose-resolution-architecture.md` (one
machinery for physical objects and abstract concepts) — should be able
to **learn language** from lived interaction. The session also surfaced
a working-agreement problem: direction decisions had been argued past
Daan's ability to independently check them. The standing correctives,
applied from this chapter forward: teach-back before load-bearing
decisions, claims tagged by evidence class (measured / mechanism-argument
/ judgment; only measured closes a debate), every direction decision
recorded with what would change our minds, and an adversarial pass on
vision-level calls.

**What was reversed:** the Non-goals line "competing on language …
not PRA's axis" — language learning moved to Horizon ambitions as a
gated research question. **What stands:** no competing with frozen LLMs
on encyclopedic recall; research gates before showcases; no demo
outruns measured capability.

**The named gates.** Language: the teacher-world experiment
(observation = sentence-so-far + teacher-feedback-as-world-state,
action = emit token, LLM as interactive teacher), behind three
prerequisite decisions (competence-drive-vs-approval hypothesis,
factored/embedded actions for large vocabularies, sequence observation
encoding). Pre-registered prediction, stated before any run: the current
kernel captures surface statistics and plateaus short of syntax, because
nothing in it composes — if wrong, the vision gets much cheaper; if
right, hierarchical frames become the next named gate. Seeding: the
three-armed compounding experiment (seeded / fresh / maturity control,
then a resize hop), margin must survive two hops; if seeded loses or
margins shrink hop-over-hop, earned persistence is the suspect and "seed
brains" leaves the vision language until diagnosed.

**What would change our minds back:** a teacher-world reading showing no
traction beyond surface statistics *and* no nameable mechanism from the
factored-action / hierarchical-frame research — then language returns to
Non-goals with the numbers beside it. Housekeeping recorded:
NEXT-STEPS.md marked historical (superseded by this file + ROADMAP.md).
Trail: ROADMAP.md (Horizon ambitions, Non-goals); this conversation.

## Chapter template (append below)

```markdown
## Chapter N — <title> (<dates>)

<What happened, in a few sentences: the question, what was built/measured,
the honest outcome with key numbers.>
<What was refuted or reversed, if anything.>
<What it taught / what it opened.> Trail: <docs>; commits <hashes>.
```
