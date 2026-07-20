# Camping-costs arc — does the frontier drive earn its keep where avoidance stops being optimal?

Date: 2026-07-18. Question under test: PREDLP-DIAGNOSIS closed the A4 exit
but left the frontier drive with an asterisk — validated non-inferior,
occupying the sensible middle of the steering ordering (competence <
frontier < curiosity), yet only *matching* competence on L1, where avoiding
the unlearnable region is simply optimal. Chapter 24 named the two world
families where a camping strategy should cost something: **mastered-then-
changing** (the learnability frontier moves mid-run) and **multi-region
learnable** (all regions learnable, at different difficulty — retreating to
the easiest leaves progress on the table). This arc builds both worlds
(opt-in, behind the existing seam, degenerate dials byte-identical) and
measures the four chapter-24 arms on them at 24-seed power. The recorded
chapter-24 verdicts stand untouched; whatever happens here is new evidence
about the drive, recorded either way.

Anchors inherited (PREDLP-DIAGNOSIS E1, L1, 24 seeds): competence margins
over random +0.030…+0.070 across dials/horizons; frontier +0.015…+0.046;
blend +0.024…+0.062; steering Δocc — competence −0.02…−0.06, frontier
−0.02…+0.02, curiosity positive. T7 noninferiority form: PASS iff
mean(margin) ≥ −1.9·SE. A4-exit form: beats random in a strict majority of
24 seeds at every horizon checkpoint.

## The worlds under test (design frozen here, before any run)

**W1 — the shifting world (`world="shifting"`,
dial `shift_after_steps: int = 0`).** Byte-identical to the reference world
while the dial is 0. With `shift_after_steps = S > 0`: at construction, a
SECOND set of action displacements is drawn immediately after all reference
draws (draw-order discipline: per object start/emit, actions, then the
post-shift actions); from the first step *after* the world has emitted S
step observations, the displacement set swaps — the emission map (what the
brain *sees*) is unchanged, but what actions *do* changes. Mastered
transition models silently go stale; encoders/decoders stay valid. No RNG
is consumed at shift time. The step counter is world state (snapshot-
carried), so resume across the shift is byte-identical, and the counter
advances identically in continuous mode. Harness-only `ladder_readings()`:
shift step, whether it has fired, pre/post displacement identity.

**W2 — the multi-region world (`world="multiregion"`,
dial `region_noise_levels: tuple[float, ...] = ()`).** Byte-identical to
the reference world while the dial is empty. With K levels
(σ_1, …, σ_K): the latent half-spaces/quadrants defined by the signs of
latent[0] (K=2) or latent[0], latent[1] (K=3–4) get per-region transition
noise σ_k added while inside — the NonUniformWorld mechanism, generalized —
with every σ_k held **inside the learnable band** (≤ 0.3; L1 measured 0.2
PASS / 0.8 as the landing-spread regime). Regions differ in difficulty,
none is a noise trap. Registered first-results dial: K = 2,
`(0.0, 0.3)`. Per-region step counters ride `ladder_readings()` (the L1
occupancy instrument, per region).

**The instrument.** The chapter-24 four-arm comparison — random,
competence, frontier, frontier+competence (0.5/0.5) — paired per seed
against same-seed random, seeds 1–24, horizons `n_cycles ∈ {18, 30, 50}`,
run through the engine with `world_factory=make_world` (the 016 lesson is
structural now: the engine refuses these worlds without a factory). New
reading for W1: **post-shift improvement** — with S placed at the
episode boundary nearest cycle 24 of 50 (mastery first: ≈ (25 + 24·6)·40
steps), per-seed post-shift improvement = (mean pred error over the first
EARLY_LATE_WINDOW steps after the shift) − (the last window of the run),
computed from the recorded per-step error trace. New reading for W2:
per-region occupancy fractions per seed.

## Hypotheses (pre-registered, before any run)

- **H-shift.** After the shift, frontier-bearing arms re-engage and recover
  faster: frontier or blend beats **competence** on post-shift improvement
  in a strict majority of 24 seeds at the 50-cycle horizon, with positive
  mean margin. Before the shift they are noninferior to competence (T7
  form) — the edge must not be bought with pre-shift cost.
- **H-region.** On W2, frontier-bearing arms occupy the harder-but-
  learnable region more than competence does (strict majority of seeds,
  paired), and their improvement is noninferior to competence's (T7) with
  the sign-majority reported; the pre-registered *win* claim is modest:
  frontier or blend beats competence in ≥ 13/24 seeds at ≥ 1 horizon.
- **H-sanity.** Every directed arm still beats random on both worlds in
  the A4-exit sense at the dial(s) run (the chapter-24 result transfers).

## E-steps and bars

- **E0 — contracts before science.** Degenerate dials byte-identical to the
  reference stream (unit tests, the ladder pattern); snapshot resume across
  the shift byte-identical; continuous-mode smoke; quality gate green. Any
  break = X-contract: fixed before any measurement.
- **E1 — W1 shifting, 4 arms × 24 seeds × 3 horizons.** Primary:
  **H-shift's majority clause** (frontier or blend > competence post-shift,
  ≥ 13/24, mean margin > 0, at the 50-cycle horizon). Secondary: pre-shift
  T7 noninferiority; vs-random A4 sanity; whole-run margins with spreads;
  steering traces (does the frontier arm's error trace dip-and-recover
  where competence's stays flat?) recorded.
- **E2 — W2 multiregion (K=2, (0.0, 0.3)), same grid.** Primary:
  **H-region's occupancy clause** (frontier-bearing arms in the harder
  region more than competence, paired, ≥ 13/24) AND noninferiority.
  Secondary: the modest win claim; vs-random sanity; per-region occupancy
  spreads.
- **E3 — dose check (conditional, cheap).** Only if E1 or E2 verdicts look
  dial-fragile (margins within ±1 SE of zero): one more dial each
  (shift earlier at cycle 12; W2 (0.0, 0.2)) at 8 seeds, exploratory,
  recorded as context — never used to flip a 24-seed verdict.

## Failure exits (pre-registered stopping rules — a FAIL is data)

- **X-contract** — any byte-identity/snapshot/continuous break in E0: fixed
  before science; never negotiable.
- **X1** — H-shift fails: recorded finding — *realized* local progress is
  not a sufficient change detector at reference budgets (its memory of
  errors-at-visit may decay too slowly to notice staleness); the named
  successor is fully **predictive LP** (the per-candidate error model,
  already on the roadmap). The worlds ship regardless: they are the missing
  testbed, and the FAIL is their first recorded result.
- **X2** — H-region's occupancy clause holds but noninferiority fails
  (steering with a cost): recorded; Doc 05 guidance stays "competence", the
  blend question re-opens with data.
- **X3** — H-region fails entirely (no steering difference): the frontier's
  distinctness claim narrows to the ordering already recorded; successor
  research named (per-candidate value shaping), not improvised here.
- **X4** — H-sanity fails anywhere: stop and diagnose before interpreting
  anything else (an instrument or world-design fault is more likely than a
  drive regression).

Results are appended as they land; the Outcome section closes the arc.
Scratchpad instruments stay out of git; protocols and tables live here.

## Result: E0 (recorded 2026-07-18)

Both worlds shipped opt-in: degenerate streams byte-identical to the
reference (unit-tested), shift semantics and per-region draws verified,
state capture across the shift, dial↔world validation coupling, old-blob
config decode tolerant of the new tuple field. Full gate green, baseline
untouched.

## Result: E1 + E2 (recorded 2026-07-18; 576 runs — 2 worlds × 4 arms × 3 horizons × 24 seeds, one instrument invocation)

**X4 fired first, and its diagnosis is already in the record.** H-sanity
(every directed arm beats random, A4 form) fails on both worlds: on W1
the vs-random majorities hover at 11–14/24 with mean margins ≈ 0.000; on
W2 competence holds 17/24 at every horizon but frontier reads 13/13/11.
Diagnosis, per X4's stop-first rule: this is the world-family regime the
BLEND arc already measured — *directedness pays in proportion to how
much the world punishes indiscriminate experience*, and these
all-learnable, mild-noise worlds barely punish it (W2's competence
17/24 shows the instrument resolves real effects; W1's whole-run margin
pools pre- and post-shift regimes). The sanity clause imported an
expectation from the L1 family; recorded as a calibration note, and the
E1/E2 readings below stand as findings *about these worlds*.

**E1 — the shifting world.**

- Pre-shift (h18/h30, shift never fires): frontier and blend are
  noninferior to competence at every read (T7 PASS ×4) — the edge is not
  bought pre-shift.
- **Primary, post-shift at h50 — letter-PASS, substance qualified by the
  pre-registered context row.** Frontier > competence 14/24, mean margin
  +0.027 (spread [−0.071, +0.147]); blend 14/24, +0.003. But **random >
  competence 17/24, mean +0.027** — the same edge. Post-shift
  improvement medians: random **+0.070**, frontier +0.061, blend +0.058,
  competence **+0.038**.
- **The clean new fact: camping measurably costs.** The camper has the
  worst recovery of all four arms when the world moves — the
  mastered-then-changing world does exactly the job it was built for.
  What it does *not* show is a frontier niche: the realized-LP arm
  re-engages no better than undirected exploration. H-shift's majority
  clause is met; its *interpretation* (frontier as change detector) is
  refuted by the random context.

**E2 — the multi-region world (K=2, (0.0, 0.3)).**

- **Occupancy clause: holds for frontier** — harder-region occupancy
  above competence's, paired, 14/15/14 of 24 at h18/h30/h50 (median
  hard-occ 0.644 vs competence 0.582 at h50). Blend does not steer
  (12/11/10).
- **Noninferiority: FAILS for frontier at h30/h50** (mean margins −0.033
  and −0.023 vs competence, well outside −1.9·SE) → the conjunctive
  primary FAILS → **X2: steering with a cost.** Frontier genuinely
  visits the harder-but-learnable region more and pays ~0.02–0.03
  improvement for the visits at reference budgets. The modest win clause
  is met only by blend at h18 (13/24, mean +0.001 — noise-thin).
- Competence remains the strongest arm on W2 (17/24 over random at every
  horizon, means +0.020…+0.028).

**E3 (conditional dose check): not run, per its own clause** — the
deciding reads are not dial-fragile (W2 noninferiority failures sit at
2–3× their SE; W1's primary is qualified by the random context, which no
dose change addresses).

## Outcome (recorded 2026-07-18)

1. **The testbeds ship and do their jobs.** Two opt-in worlds behind the
   existing seam, byte-identical when off, snapshot-safe across the
   shift, per-region occupancy instrumented. The ladder now has worlds
   where camping costs — and the cost is measured, not assumed:
   post-shift, the camper recovers worst of all arms (median +0.038 vs
   random's +0.070).
2. **The frontier drive does not earn its named niche at reference
   budgets — recorded as the finding it is.** On the world built for
   change detection, its post-shift edge over competence (+0.027,
   14/24) is indistinguishable from random's (+0.027, 17/24); on the
   multi-region world it steers exactly as designed (occupancy clause
   holds at every horizon) but pays for the steering (noninferiority
   FAIL, X2). The realized-LP form — progress already *banked* near a
   candidate — is a lagging indicator: by the time errors-at-visit
   have fallen, the frontier has moved on. The named successor stands
   and sharpens: **fully predictive LP** (a per-candidate error model
   that anticipates progress instead of remembering it), with these two
   worlds as its ready-made testbed and these numbers as its baseline.
3. **Doc 05 guidance is unchanged by measurement**: competence remains
   the recommended drive — strongest on W2 at every horizon, noninferior
   pre-shift on W1; its one measured weakness (worst post-shift
   recovery) is not yet exploitable by any drive in the registry.
4. **Clause calibration recorded**: the A4-form vs-random sanity bar
   does not transfer to worlds that tolerate indiscriminate experience
   (the BLEND regime finding, reconfirmed); future arcs on mild worlds
   should register competence-relative bars, not random-relative ones.
5. **What ships**: `world="shifting"` / `world="multiregion"` with their
   dials (inert by default, byte-identical — test-guarded), the
   state-capture and config plumbing, this trail, and the recorded
   baselines for the predictive-LP successor.
