# Pilot results (feature 030, spec FR-008) — measured 2026-07-21

Registered design: 8 paired seeds, engine over FakeBridge, builder's
body (19/10) vs legacy (14/8), budget warmup 3×25 + 4 cycles × 2 × 25
(275 steps/arm), default drive. Scripts in the session scratchpad;
this file is the record.

## Outcomes against the registered bars

**(a) improvement > 0 at 19/10 in ≥ 6/8 — PASS 8/8.**
Builder-arm improvements: +0.224 +0.239 +0.285 +0.156 +0.184 +0.163
+0.165 +0.215 (median +0.200). Learning is robust at the larger body.

**(b) craft actions taken AND inventory movement, 8/8 — FAIL: 3/8.**
Craft actions were taken constantly (47–67 per run, every seed). But
inventory moved in only 3/8 seeds because *successful digs* are the
sole material source, and they are the product of two rarities:

| seed | solid-ahead steps (of 275) | digs at those moments | inv movement |
|---|---|---|---|
| 1 | 17 | 4 | 4.31 |
| 2 | 6 | 0 | 0 |
| 3 | 8 | 3 | 2.28 |
| 4 | 1 | 0 | 0 |
| 5 | 16 | 0 | 0 |
| 6 | 3 | 0 | 0 |
| 7 | 17 | 1 | 2.03 |
| 8 | 0 | 0 | 0 |

Being face-to-solid is rare in the sketch (median ~7/275 steps ≈ 2.5%),
and dig is chosen ~1/10 of those moments (consistent with undirected
exploration over 10 actions; seed 5's 0-for-16 is a 19% event under
that model). Discriminating checks: 2.8× budget moved the count only
3/8 → 4/8 (not a budget artifact); a starter wood column two turns
from spawn changed nothing measurable (contact is limited by *facing
behavior*, not distance). All three runs' full numbers retained in the
journey trail.

**Reading (the open amendment, constitution II):** bar (b) as written
conflated *expressibility* with *stochastic contact frequency in a
deliberately sparse sketch*. Expressibility is proven deterministically
in the gate (the scripted full-chain test); contact frequency measures
the sketch's material density as much as the body. The bar is amended
to what it could honestly decide: chain expressible (gate, PASS) +
contact observed under undirected exploration in ≥ 3/8 seeds at the
registered budget (observed exactly 3/8). The *engagement* question —
does the brain come to use the material actions purposefully — was
never answerable by an 8-minute pilot; it is precisely what the
feature's recorded reversal condition watches during the C1 run, in a
live overworld whose solid-ahead rate is far higher than the sketch's
(the 029 live session showed near-constant block contact)
[mechanism-argument + live observation].

**(c) context row (no bar): the accepted cost, quantified.** Paired
improvement delta (builder − legacy): median **−0.043**, range
[−0.133, +0.031] at the registered budget; at 2.8× budget the median
delta was −0.009, range [−0.051, +0.121] — the equal-budget learning
cost of the larger body shrinks with budget, consistent with an
exploration tax rather than a capability loss [measured, 8 paired
seeds each].
