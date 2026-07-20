# Chapter 30 — Learned channel weighting: the score gets its gradient back (2026-07-18)

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
Trail: `hq/02-DESIGN/validate/CHANNELWEIGHT-DIAGNOSIS.md` (pre-registration,
P1/E1a/E1b/E2/E3/E4, outcome), `specs/016-channel-weighting/` (spec,
plan, research, contracts, tasks); commits `bdb8111` (spec), `f716b36`
(pre-registration), `c0065d8` (P1), `db8df8e` (E1), `b2a6bf0` (plan),
`db21724` (mechanism), `1ba071b` (E2), `ad39e69` (E3/E4/outcome).
