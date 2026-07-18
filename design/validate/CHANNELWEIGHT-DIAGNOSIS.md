# Channel-weighting arc — does the named remedy rescue structure-finding from static?

Date: 2026-07-18. Question under test: CHANNELNOISE-DIAGNOSIS closed with a
measured three-leg mechanism and a named, unshipped remedy — **learned
channel weighting**, an in-system per-channel noise-floor treatment feeding
*both* the survival norms and the frame learning path (Outcome §4). This arc
pre-registers, gates, ships (opt-in), and measures that remedy. The target
is the ladder's first open problem: L3 noise mode at σ_d = 1.0, recorded
FAIL (finals [1, 4, 1, 1, 1, 3, 1, 6]; dim-1 collapse in 5/8 seeds), judged
by the unchanged criterion form |best_dim − 3| ≤ 1 in a strict majority at
every checkpoint (18/30/50). The recorded FAIL and its criterion text are
never amended by this arc; a rescue lands as a dated addendum beside them.

Measured constraints inherited from the parent arc (all anchors below are
its recorded numbers):

- **Score-side exclusion alone is insufficient at unit amplitude** — the
  oracle core-only rescoring of the E2b surfaces restores a healthy elbow at
  σ_d = 0.5 (depth up to 0.134) but not at 1.0 (judging-age depth 0.022,
  min back at 1 by age 24), because static entering the shared encoder has
  already flattened the core error at young ages. Any remedy must treat the
  learning path too.
- **The transient is what gets judged**: winners' scores 0.72–0.83 sit above
  the pop-scaled survival bar ≈ 0.49–0.65, so no frame survives its first
  unprotected judgment — a permanent youth conveyor, judged at ages
  (bracketed by the 24- and 48-episode reads) where dim 1 wins.
- **Dose anchors** (median improvement): 0.485 at σ_d = 0.04, ≈ 0.392 at
  0.2 (PASS, 8/8 within-one at @50), 0.198 at 0.5 (instability band),
  0.107 at 1.0 (collapse). Judging-age basin depth: 0.119 at 0.04 vs 0.000
  at 1.0 (age 12). Core learning corruption at 1.0: dim-3 asymptote ratio
  1.61 vs the pre-registered 1.5× bar; intact at ≤ 0.5 (1.02).

## The design under test (frozen here, before any run)

**Estimator — per-channel whiteness, global, learning-free.** Static is
white; core channels carry the world's latent dynamics. On the frame store,
per channel c, updated once per online step (EMA decay β =
`channel_stats_decay`, pinned by P1 from a pre-registered grid; all state
init 0, weights init 1):

    m_c   ← β·m_c + (1−β)·obs_c
    v_c   ← β·v_c + (1−β)·(obs_c − m_c)²
    cov_c ← β·cov_c + (1−β)·(obs_c − m_c)(prev_obs_c − m_c)   [needs prev_obs]
    n_c   ← n_c + 1

Weights recomputed **only at episode starts** (real or virtual — the same
boundary the norm-cap projection uses), never mid-episode:

    ready_c := n_c ≥ ceil(1/(1−β))            [derived, not a new constant]
    ρ̂_c    := clip(cov_c / (v_c + 1e−6), 0, 1)
    w_c     := clip(ρ̂_c / (max over ready ρ̂ + 1e−6), f, 1)  if ready_c else 1
                                               [f = channel_weight_floor]

P1 also decides between this max-normalized shaping and the plain
`clip(ρ̂_c, f, 1)` fallback (decision rule pre-registered in P1). The
estimator reads only the observation stream — never residuals, scores, or
world internals — so down-weighting cannot deadlock its own evidence and no
frame has any handle on the metric it is judged by.

**Application — one weight vector, both legs.** The same w applies to
(a) the survival norms: `fit = ‖(recon − obs)⊙w‖ / (‖obs⊙w‖ + ε)` and the
same form for the honest prediction error — numerator *and* denominator,
so the ratio remains "relative error over the channels that count";
(b) the learning path: the encoder consumes `w⊙obs`, the placement error
becomes `(recon − obs)⊙w` (which silences both the static-target decoder
rows and the static leak back into the shared layers), and the encoder
gradient's outer product uses the weighted input. Judging and learning
never disagree about what a channel is worth. Effort and all pose-space
quantities are untouched.

**Opt-in, reference-preserving.** `channel_weight_floor = 0.0` is the
default and means **off**: no estimator state, no extra float work, no RNG
anywhere (the feature consumes zero random draws even when on — every
ON-vs-OFF comparison below is exactly paired per seed). Telemetry
`pred_error_early/late/improvement` keep their unweighted all-channel
definitions (dose curves stay comparable to the parent arc); the weighted
quantities are the per-frame survival EMAs — the numbers the ecology
actually judges. Estimator state (m, v, cov, n, w) is snapshot state when
on (additive-optional keys; feature-off blobs bit-identical to the
pre-feature format).

**The transport argument (the sharp prediction this arc tests first).**
With core weights 1 and static weights f = 0.2, at σ_d = 1.0: the encoder
sees static at amplitude 0.2; the weighted placement error on a static
channel has amplitude ≈ 0.2 (its target is scaled where recon ≈ its mean);
the weighted norms carry static at (0.2)² in numerator and denominator —
each the same magnitude the *unweighted* system sees at σ_d = 0.2, which E1
measured as a clean PASS. The remedy is not tuned toward green; it
transports the system into an operating point already measured green. If
this is right, oracle weights at floor 0.2 must reproduce ≈ the recorded
σ_d = 0.2 behavior at σ_d = 1.0. E1a tests exactly that, before any
estimator code exists.

## Hypotheses (pre-registered, before any run)

- **H-transport (E1a/E1b).** Oracle per-channel weights (1 core | f static)
  applied to both legs restore the judging-age score gradient at σ_d = 1.0
  and let frames mature in live runs; at f = 0.2 the frozen surfaces land
  ≈ the recorded σ_d = 0.2 surfaces.
- **H-whiteness (P1, E2).** Lag-1 autocorrelation separates static from
  core channels within the first cycles at every dose at or above the
  instability band, and never suppresses a structured channel on worlds
  with no static (reference world, structured mode).
- **H-rescue (E3).** The *learned* weights, produced in-system during live
  runs, flip L3 noise at σ_d = 1.0 to PASS under the unchanged criterion,
  break the conveyor (mature frames appear), and restore the dose curve
  toward its floor-limited ceiling.
- **H-no-harm (E4).** With the feature ON, every currently-passing verdict
  stays PASS and paired continuous measures degrade ≤ 0.05; with the
  feature OFF, everything is byte-identical.

## P1 — estimator separability & drift (scratchpad; protocol pre-registered)

Drive three worlds under the pinned random policy with the exact estimator
arithmetic (standalone script, no src changes): the distractor world in
noise mode (recorded rung dials, σ_d ∈ {0.1, 0.2, 0.5, 1.0}), structured
mode, and the reference world. β ∈ {0.98, 0.99, 0.995}; per-channel ρ̂ and
induced-w trajectories, both shapings, seeds 1–3.

**Accept** (pins β and shaping): min-core-ρ̂ − max-static-ρ̂ ≥ 0.5 within 10
episodes at every dose ≥ 0.1; on the reference world and structured mode,
min induced core weight ≥ 0.9 at every post-ready read. Prefer the smallest
β that passes (fastest adaptation); if max-normalized shaping puts any core
channel below 0.9, switch to plain clip. Post-convergence drift read:
max per-episode Δw after warmup, recorded (informative; large drift is a
design smell to record, not a bar).

## E1a — oracle both-legs gate (scratchpad; BEFORE any estimator code)

The parent arc's E2b frozen-surface instrument (equal-experience frames,
dims {1, 2, 3, 4, 6, 8}, trained at the live effective rate, frozen,
evaluated 10 episodes) re-run with **fixed oracle weights** — 1 on the 10
core channels, f on the 10 static channels — applied to both legs during
training *and* evaluation. Grid: f ∈ {0, 0.1, 0.2, 0.3}, σ_d ∈ {0.5, 1.0},
train ages {12, 24, 48} episodes, seeds 1–3. Surfaces scored at the
effective parsimony price (0.02/dim at obs_dim = 20), on the weighted norm.

**PASS bar (any f in the grid):**

- σ_d = 1.0: weighted score-surface minimum ∈ {3, 4} at ages 12 AND 24
  with basin depth (score(1) − score(min)) ≥ **0.06** at both [anchors:
  healthy 0.119; failed score-side-only 0.022; 3× the 0.02/dim price];
  at age 48 the full span exceeds 0.06 [failure anchor: 0.015,
  gradient-free].
- σ_d = 0.5: minimum ∈ {3, 4} at all three ages, depth ≥ 0.06 [score-side
  oracle already reached 0.134 — both legs must not undercut the floor bar].
- **Corruption heal**: the leg-B-weighted core-restricted dim-3 error at
  ages 12–24 within **1.2×** its σ_d = 0.04 unweighted same-age value
  [asymptote anchors: 1.61 corrupted, 1.02 intact].

**Sharp transport prediction, recorded pass/fail alongside the bar:** the
f = 0.2, σ_d = 1.0 surfaces ≈ the recorded σ_d = 0.2 surfaces (minimum
location equal; depth within a factor of 2).

## E1b — live oracle corroboration (scratchpad monkeypatch; only if E1a passes)

Fixed oracle weights in a live engine (both legs), L3 noise at the recorded
rung dials, σ_d = 1.0, f = the best E1a floor, seeds 1–8, standard
schedule. **Bar**: ≥ 1 mature frame past its protection window in the final
population in ≥ 5/8 seeds, AND the per-seed winner `best_score` below that
seed's pop-scaled survival bar in ≥ 5/8 [anchors: winners 0.72–0.83 vs bar
0.49–0.65; today zero mature frames in every seed].

## The shipping shape (after the E1 gate, before E2)

The mechanism lands opt-in in `src/pra` with the full test set in the same
commit: estimator state on the frame store; w threaded through encode /
fit / honest-pred / placement / transition learning with `None` = the
textually-current expressions (zero float work off); config
`channel_weight_floor` (default 0.0 = off) and `channel_stats_decay`
(default = P1's β) with validation; snapshot round-trip; resize behavior
(new channels enter at w = 1 until ready). Byte-identity guards: pinned
seed-1 baseline, determinism, explicit-inert-config summary equality,
feature-off blob format equality, twin-engine ON/OFF same-seed identical
world streams (no-RNG proof). Constraint recorded: telemetry norms stay
unweighted (C2 above); summary fields appear only when ON.

## E2 — estimator identification (shipped estimator; protocol pre-registered)

Live runs with weighting ON, per-cycle weight traces recorded, seeds 1–8:
noise mode σ_d ∈ {0.04, 0.1, 0.2, 0.5, 1.0} (recorded rung dials),
structured mode, reference world.

**Bars:**

- **Separation**: at σ_d ∈ {0.2, 0.5, 1.0}, full rank separation (every
  static ρ̂ below every core ρ̂) by checkpoint 18 in ≥ 7/8 seeds, sustained
  at 30 and 50; median (core − static) ρ̂ margin monotone in σ_d over
  {0.1, 0.2, 0.5, 1.0}.
- **No core suppression**: on the reference world, structured mode, and
  noise mode at σ_d ≤ 0.1 (static ≈ sensor noise — separation is *not*
  required there): no core channel weight < 0.9 at any post-ready cycle,
  8/8 seeds. At σ_d ∈ {0.5, 1.0}: no core channel weight < 0.9 at judging
  ages (the protection-window cycles). A violation is exit X2.

## E3 — live rescue (the primary; protocol pre-registered)

Ladder L3 noise through the shipped instrument at the **recorded rung
dials** (`distractor_dim = 3, distractor_channels = 10` — the recorded
FAIL's own construction stream, not the parent arc's `distractor_dim = 1`
replicate), weighting ON at f = 0.2 (or E1a's best floor if it differs,
recorded before running), β from P1.

- **Exploratory**: seeds 1–8, σ_d ∈ {0.04, 0.1, 0.2, 0.5, 1.0}.
- **Confirmatory** (only if exploratory shows ≥ 5/8 at σ_d = 1.0): seeds
  1–24 at σ_d ∈ {0.5, 1.0}, judged on the full 24 (strict majority
  ≥ 13/24) — the predicted-LP power discipline.

**Primary criterion**: L3 noise **PASS at σ_d = 1.0** under the unchanged
criterion form, at 24 seeds, every checkpoint.

**Secondary (informative, spreads always reported):**

- Unweighted median improvement ≥ **0.15** at σ_d = 1.0 and ≥ **0.25** at
  0.5. Ceiling derivation, recorded now: at σ_d = 1.0 the unweighted
  telemetry norm keeps the irreducible static floor in both numerator and
  denominator — early ≈ 1.03 and best-achievable late ≈ 0.80 from the
  parent arc's frozen tables — so the achievable improvement ceiling is
  ≈ 0.23; the 0.15 bar is ≈ 65% of ceiling [collapse anchor 0.107; band
  anchor at 0.5 is 0.198].
- Conveyor broken: ≥ 1 mature unprotected frame in the final population in
  a strict majority of seeds at 1.0; per-seed winner score vs pop-scaled
  bar tabulated.
- Learned-weights frozen surface (scratchpad, seeds 1–3, σ_d = 1.0): score
  minimum ∈ {3, 4} with depth ≥ 0.06 at ages 12/24; young-age core dim-3
  ratio vs the 0.04 arm ≤ 1.2 (corruption healed by *learned* weights, not
  just oracle ones).
- Band behavior: 0.2 and 0.04 stay PASS at 8 seeds; 0.1's recorded flicker
  becoming PASS is desirable and recorded, not gated.

## E4 — no-harm (protocol pre-registered)

**OFF half (permanent tests, land with the code):** pinned seed-1 baseline
values; determinism; explicit-inert config summary byte-equal to default;
feature-off snapshot blobs bit-identical to the pre-016 format; ladder
degenerate-dial streams unchanged.

**ON half (paired per seed — the feature consumes no RNG, so ON/OFF see
identical event streams; 8 seeds carry real power for paired reads):**

- σ_d = 0.04 noise mode, ON vs OFF: PASS retained at every checkpoint;
  per-seed improvement(ON) ≥ improvement(OFF) − 0.05 in ≥ 6/8 seeds
  [anchor: OFF median 0.485].
- Structured mode ON: PASS retained [anchor 8/8, 7/8, 8/8]; same paired
  clause.
- L1 (amended-clause dial) and L2 (both factorizations) ON: recorded
  verdicts unchanged.
- Reference world ON: no criterion flips; E2's uniform-weight reading
  re-checked.
- Snapshot ON: mid-run round-trip, continuation byte-identical to
  uninterrupted.
- Multi-stream K = 2 and continuous mode ON: smoke (runs, deterministic).
  Deep interaction study: out of scope, named.

**"No regression" in one sentence**: every currently-PASS verdict stays
PASS under its recorded criterion form, all paired drops ≤ 0.05 in strict
majority, all byte-identity checks bit-exact.

## D1 — the relative survival bar (conditional; stays a named deferral)

The parent arc's second named leg — a survival bar with a notion of
achievable error — is **not** built in this arc (it interacts with the
seventh scale rule and would destroy attribution). **Trigger, exact**:
activate its successor pre-registration iff (a) E1b fails despite E1a
passing, OR (b) E3's primary fails at σ_d = 1.0 while the learned-weights
frozen surface shows a restored gradient (min ∈ {3, 4}, depth ≥ 0.06 at
ages 12/24) and the winners still sit above the pop-scaled bar in a strict
majority — the signature isolating the absolute bar as the residual
binding cause. If it fires, the successor doc must explicitly re-verify
the conveyor-correction conditionality (THRESHOLD-DIAGNOSIS).

## Failure exits (pre-registered stopping rules — a FAIL is data)

- **X0** — E1a fails at both 1.0 and 0.5: the both-legs mechanism story is
  incomplete. Arc stops before any estimator code; the finding + a named
  successor (conveyor re-diagnosis) are the complete deliverable.
- **X0-rescope** — E1a fails at 1.0 only: primary re-scoped to PASS at
  σ_d = 0.5 (24 seeds); 1.0 recorded as beyond this mechanism; D1 promoted.
- **X0b** — E1a passes, E1b fails: ship the estimator under the re-scoped
  primary; D1 trigger (a) has fired.
- **X1** — the estimator cannot separate at σ_d = 1.0: at most **2**
  recorded design revisions (P1's shaping fallback, then the hybrid
  whiteness×floor form) before the confirmatory stage; then stop, record
  the traces, name the successor.
- **X2** — core misclassification at low dose (E2 no-suppression fails or
  E4's 0.04 arm regresses): ship-blocked; fix openly or stop with the
  estimator landed as an inert instrument plus the finding.
- **X3** — partial rescue (0.5 yes, 1.0 no at 24 seeds): **honest FAIL of
  the primary; the L3 criterion is not amended** (the amendment route
  requires showing the clause tested a wrong assumption — the parent arc
  proved the 1.0 collapse is real, so that route is closed). Record the
  measured dose ceiling, the oracle-vs-learned gap, and evaluate D1(b).
- **X4** — any E4 regression: ship-blocked regardless of E3.
- **X5** — any byte-identity break: a bug, never negotiable; fixed before
  anything else proceeds.

Results are appended to this document as they land; the Outcome section
closes the arc. Scratchpad instruments stay out of git; their protocols
and tables live here.
