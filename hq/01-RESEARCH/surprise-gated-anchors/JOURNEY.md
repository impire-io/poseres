# Journey — surprise-gated-anchors (started 2026-08-23)

## 2026-08-23 — the mechanism built; the gate freezes itself in a lawful world

Rig restored from the 0112 trail (dial.py, embed.py at dbab45f);
`SurpriseGatedAnchors` added as declared (per-act EMA α 0.1, gate
E_a > 2·G, v2 product anchors, lr 0.01); the one-hot parity
self-test re-run — PASS at machine precision. Smoke (m=3, short
run): the gate opened **27 times in 38,579 observations** — lawful
acts converge below the gate and the table stays put, the design
intent visible before any arm. Arms next per the registration: SG0
(gated, m=3, 24 seeds, the frozen F0 thresholds), then SG1
(f4-gated, m=256) and SG2 (f4-frozen-v2 control, m=256).

## 2026-08-23 — Bar SG0: PASS — the wall is gone when mobility is priced by evidence

Against the unchanged frozen thresholds (median ≥ 10.385, min >
6.923, pred_late ≤ 0.803), 24 seeds [measured]: gated reads
**11.692 / 15.077 / 22.769**, pred_late 0.566 — at the frozen-v2
arm's own level (15.538), worst seed above frozen's worst (11.7 vs
10.3), where step-priced mobility bracketed 10.2–10.6 across three
editions. The gate opened a median of 23.5 times per life (max 44)
out of tens of thousands of observations: the anchors are mobile in
principle and still in practice, and parity holds. Evidence-priced
mobility passes the wall that step-pricing hit three times. SG1
(f4-gated, m=256) and SG2 (f4-frozen-v2 control) launch as parallel
chains per the registration.

## 2026-08-23 — Bar SG2 FAILS as registered: the exceptions were too easy, and the reversal routes the amendment

The frozen-v2 control on the F4 world [measured]: regular 0.0474,
irregular 0.0787, held-out 0.0458 — irregular/regular ratio median
**1.573** (min 1.204), 19/24 seeds INSIDE the 2× clause the control
was required to fail. The registered reversal for exactly this case
routes: amend the exceptions openly with the numbers before
re-running. The numbers say why they were absorbable: a wrong
POSITION on the claimed dial writes its whole error into one of
twelve probed channels (the MAE dilutes it ~12×), and the shared
tensors, trained by the irregular act's own repeated executions,
absorb the mean shift.

**Amendment 1 — the exceptions, before any amended arm runs:** an
irregular act now breaks the SLOT, not just the value — the anchor
claims (d, p), the world does (d̂ ≠ d, π(p)): the prediction fires
on a channel where nothing happens and misses the channel where
something does, a two-channel semantic break no channel-averaging
can dilute and no shared-tensor mean-shift can absorb — while
remaining fully learnable by anchor movement (the true anchor is
[onehot(d̂); onehot(d̂)·π(p)], inside the table's own space).
Fraction (10%), protocol, thresholds, and both clauses unchanged.
The SG1 arm currently in flight ran the old exceptions and lands as
trail; SG1′ and SG2′ re-run on the amended world.

## 2026-08-23 — Bar SG2′ PASS: on slot-breaking exceptions, pinned anchors finally fail

The frozen-v2 control on the amended world [measured]: regular
0.0602, irregular **0.1441**, held-out 0.0627 — irr/reg median
**2.379** (min 1.76), only 3/24 seeds inside the 2× clause. The
control fails the irregular clause as the bar requires, while its
lawful structure transfer holds (held-out 1.04× regular). Amendment
1 did what it was registered to do: the exception now lives where
no channel-averaging dilutes it and no mean-shift absorbs it, and a
table that cannot move cannot fit it. The discrimination is real;
Bar SG2 (amended) PASS. Everything now rides on SG1′ — whether the
gate opens exactly there.

## 2026-08-23 — Bar SG1′ PASS 24/24 on both clauses: the gate opens exactly where the world breaks its rules

The gated arm on the amended world [measured]: regular 0.1096,
irregular 0.1686, held-out 0.1105. Irregular/regular median
**1.559** (max 1.905) — **24/24 seeds inside the 2× clause** the
frozen control fails at 2.379; held-out/regular median **1.002**
(max 1.154) — **24/24 inside 1.25×**, untried ≡ practiced intact
under exceptions. Gate moves median 1,104: mobility spent where
surprise accumulates, withheld where the world is lawful (23 moves
per lawful life at SG0). On the record beside the ratios: the gated
arm's absolute lawful error (0.110) runs ~1.8× the frozen control's
(0.060) — mobility's absolute price persists and the bars, margined
against own error per the 0112 lesson, pass with that stated.

**The board: SG0 PASS, SG1 (amended) PASS, SG2 (amended) PASS.**
Evidence-priced mobility passes the wall step-pricing hit three
times, absorbs the exceptions pinned anchors cannot, and keeps the
structure-transfer property whole. The mechanism design 0019's
constraint 2 named is measured.
