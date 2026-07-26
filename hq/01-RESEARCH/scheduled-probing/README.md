# Can a scheduled, held-policy probe of mastered ground detect a world change that no passive statistic could separate from the brain's own nonstationarity?

**State:** active
**Started:** 2026-07-26

## Abstract

Four passive signal families — error level, error jump, error
accumulation, election silence — closed on one frozen testbed with one
verdict: no passive statistic separates a world change from the brain's
own nonstationarity at honest false-alarm rates; the detector's
background is the brain itself (chapters 36–40). Chapter 40 named the
successor the numbers point to: **active** detection — deliberately
re-visit mastered ground under a held policy and re-test, detection as
a designed experiment. This topic measures whether removing the
policy-movement confound *by construction* (same start state, same
action script, same ground) lifts post-shift contrast past the 4×
bracket every passive read missed, and whether that contrast supports a
zero-false-alarm decision rule. A decisive PASS opens a Doc 05-level
feature (probing as an opt-in engine capability with a measured no-harm
surface); a decisive FAIL closes the detection program for the current
brain — active and passive both measured — leaving the chapter-39
tolerant gate (~1.6% false-fire) as the only recorded deployment option.

## The question

When the brain re-visits ground it has mastered — same episode start,
same recorded action sequence, drive held for the probe — does its
prediction error on that ground separate a genuine world change from
its own relearning, churn, and drift, at the bars the passive program
was held to?

## Pre-registered bars

Testbed inherited from arcs 022–025: the h100 worlds, both shift modes
(**emission** and **dynamics**), shift injected at step 6760
(episode 169; 40-step episodes); detection window = episode-ends in
6760..7240 (twelve post-shift episodes); screening tier = seeds 1–3 +
multiregion s1, confirmation tier = seeds 4–6 + multiregion s2 (read
only on a screening pass); **six shift cells per tier** = 2 modes × 3
seeds. Because probing is active, these are **fresh live runs**, not
reads of the frozen 023 captures — each shift arm gets a benign twin
(same seed, no shift, run to step 24000) carrying the false-alarm
exposure.

**The probe protocol (frozen before any run):** at the end of
episode 130 (the mastery point), record the episode's start state, its
40-step action sequence, and its per-step prediction errors (the
**reference trace**; its median error = the baseline B). A **probe** =
one scheduled episode in which the drive is held and the recorded
action sequence is replayed from the episode reset; the probe reading
R = median per-step prediction error over the replayed steps; the
**contrast** C = R ÷ B. Probe cadence: every 10 episodes from
episode 140 (pre-shift probes at 140, 150, 160; post-shift probes at
170, 180, … — the first two fall inside the detection window). Medians
of even length are the mean of the middle pair (house rule). If the
pilot shows the episode-130 mastery point immature (reference errors
not yet settled), the point may be moved **earlier-registered, openly,
before any shift-cell reading** — never after one.

- **Bar P0 — existence of probe contrast** (the discriminating gate):
  on the screening tier, the **first post-shift probe** reads C ≥ 4 in
  ALL SIX shift cells, AND every pre-shift probe (shift arms) and every
  probe in the full benign tier reads C < 2. Both clauses must then
  reproduce on the confirmation tier. The 4× bracket and the
  benign-floor clause are the passive program's bars, inherited so the
  active read is judged on the same scale it must beat (best passive:
  weak cells ~1.5×, benign floor never 4×-cleared).
- **Bar P1 — the decision rule** (run only if P0 passes): freeze a fire
  threshold θ on C and keep the registered cadence; the 024 bar form
  verbatim — the ONE frozen setting must fire within the first two
  post-shift probes in ALL SIX cells AND fire ZERO times across all
  pre-shift probes and the full benign tier, screening then
  confirmation, no per-world tuning.
- **Bar P2 — the no-harm surface** (run only if P1 passes; the gate
  that opens the design doc): with probing on at the registered cadence
  vs off, 24 paired seeds on the reference world are **noninferior** on
  final competence per observation (the B4 noninferiority form), and
  the probe budget is stated (probes as a fraction of steps, plus any
  measured competence delta with spreads). The eventual feature is
  opt-in with byte-identity when off (constitution I) — enforced at
  spec time, stated here.

Instrumentation note: the scripted-action injection this protocol needs
existed in the feature-034 demonstration machinery; runners live in the
session scratchpad and are rebuilt from the committed record when lost
(done twice before, proven by replication gates — the discipline, not
the files, is the instrument).

## Reversal condition

This topic assumes active revisit can succeed where passive reading
failed *because* the background was the drive moving the policy —
remove the movement, keep the signal. Evidence that reverses it: P0
failing — in particular, the strong cells (those the transfer stream
already read at 3–7×) failing to reach 4× under a held-policy replay,
or pre-shift/benign probes themselves drifting past 2× (the brain's own
relearning contaminating even scripted revisit). Either reading extends
the chapter-40 verdict to active reads: the detection question closes
for the current brain, and the recorded deployment options remain the
chapter-39 tolerant gate and Doc 05's drive-level guidance (competence
stands — it never depended on detection).

## Verdict

- **Bar P0 — FAIL, both clauses** [measured]. Clause (a): the first
  post-shift probe read C = 0.84–1.76 across all six screening cells
  against the ≥ 4 bar (dynamics 1.08/0.87/0.84; emission
  1.33/1.76/0.92). Clause (b): pre-shift probes all pass (max 1.65)
  but the benign tier does not — no-shift twin s3 reads 2.41, and
  multiregion s1 violates six times across 49 probes, to 2.80. The
  benign band (max 2.80) sits above the entire shift band (max 1.76).
  Confirmation tier not run (registered read-only-on-pass).
- **Bar P1 — not run** (conditional on P0). Moot by overlap
  [measured]: no θ separates bands that have crossed; the pre-frozen
  θ = 3.0 was never applied.
- **Bar P2 — not run** (conditional on P1).
- **Mechanism** [measured]: relearning completes inside one episode
  (first shifted episode collapses early→late 0.21–0.64 → 0.05–0.22;
  one dynamics seed at floor within its first 40 shifted steps);
  election censoring survives the held policy (emission arms halve
  their electing census on the probe route, 14.0 → 6.5); the raw
  one-step error has < 4× headroom over its own noise floor
  (B 0.07–0.19; best reading anywhere: 3.9×, gone the next episode).
- **Verdict** [judgment]: the reversal condition fired on both legs.
  The chapter-40 verdict extends to active reads: the detector's
  background is the brain itself, and its window is the brain's own
  relearning speed. The staleness signal lives ~10–30 steps; the
  earliest scheduled revisit arrives an episode late. The instrument
  controlled everything it promised (I1–I4 PASS) and the reading
  still cannot separate.
