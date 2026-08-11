# Head churn — does normalization plus a lower learning rate end the convergence lottery?

**State:** active
**Started:** 2026-08-11

## Abstract

Three gates isolated "the churn": η=0.5 NLMS over 153 correlated quadratic
features keeps overwriting what it learns — six seeds refuse ruin perfectly,
four invert, spread 0.00–1.00 (ep 0091); replay amplifies it (ep 0092).
The ranked-next fix from 0092's diagnosis: **feature normalization + a
lower head η**. This topic runs that fix against the frozen ruin-refusal
target the quadratic head failed, and — per the owner's dials directive —
asks whether η's operating point can stop being a per-regime magic number.
Failure ends this autonomous chain: the other ranked option (targeted
low-order terms) is the owner's call, not a successor here.

## The question

Does feature normalization plus a lower head learning rate deliver
ruin-refusal at the 0090 bar with bargain-lean preserved, ending the
per-seed convergence lottery — without harming the shipped completion-itch
pathway that shares the head?

## Pre-registered bars

The pilot explores the (normalization form, η) grid and publishes its rows;
the confirmatory 24-seed arms run ONE frozen recipe.

- **Bar C1 (headline, inherited from 0090):** ruinous-trade share ≤ 10%
  aggregate on the moving-senses instrument (24 seeds, registered protocol),
  with bargain-lean preserved (median executed rate < average offered rate).
- **Bar C2 (the lottery ends):** ≥ 20/24 seeds individually ≤ 15% ruinous
  (0091 recorded 7/24, spread 0.00–1.00).
- **Bar C3 (no collateral):** life 24/24; reactive-world pacing ≥ 20/24;
  arbitration sharpness ≥ the linear anchor's 0.874.
- **Bar C4 (the composition guard):** the frozen recipe, applied to the
  shipped completion-itch pathway on the taught lab cohort, keeps its
  chains at the recorded 24/24 — the trading fix must not lobotomize the
  worker that shares the head.

## Reversal condition

If no (normalization, η) recipe passes C1–C4, the churn diagnosis is
incomplete — the remaining ranked option (targeted low-order terms) returns
to the owner, and this topic records which ingredient failed and how.

## Verdict

- **Bar C1 — FAIL** [measured]: frozen recipe (raw features, η=0.02, no
  normalization) at 24 seeds: aggregate ruinous share **0.161** vs the
  0.10 bar (211 trades; lean preserved, rate median-of-medians 5). The
  8-seed pilot's perfect 0.000 was the lottery drawing clean.
- **Bar C2 — FAIL** [measured]: 17/24 seeds individually ≤15% (bar 20/24);
  the convergence lottery survives low η.
- **Bar C3 — PASS** [measured]: life 24/24 in both worlds; reactive
  sustained trading 23/24; sharpness 0.997 ≥ 0.874.
- **Bar C4 — PASS at pilot scale** [measured]: the completion-itch pathway
  taught and lived at η=0.02 keeps working (gains 325–427 vs 416–478 at
  0.5, all alive) — dense-event teaching tolerates a slow head.
- **Normalization REFUTED** [measured]: worse in every pairing
  (0.312 vs 0.253 at η=0.5; 0.241 vs 0.191 at η=0.1).
- **The η dial mapped** [measured]: 0.5→0.253, 0.1→0.191, 0.05→0.177,
  0.02→0.161 (lottery intact), 0→zero trades ever. Online learning is
  what drives trading at all [measured]; slow heads go blind where the
  world learns you back (react ruin 0.225 at η=0.02, 8 seeds)
  [measured, named boundary].

The registered reversal fires: no (normalization, η) recipe passes C1–C4.
The churn diagnosis is incomplete; the remaining ranked option (targeted
low-order terms) returns to the owner. [judgment: the tradeoff map itself
— refusal, tracking, and activity cannot all be bought with one global
learning rate — is this topic's real product.]
