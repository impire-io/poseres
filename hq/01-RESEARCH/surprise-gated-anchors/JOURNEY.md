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
