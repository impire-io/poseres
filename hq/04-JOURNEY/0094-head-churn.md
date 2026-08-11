# Episode 0094 — The learning-rate map: no single η buys refusal, tracking, and activity (2026-08-11)

The owner's dials directive ("values we decided that the brain should
figure out") sent three retirement topics out in parallel; this is the
first verdict. head-churn ran the churn diagnosis's ranked-next fix —
feature normalization + a lower head learning rate — against the frozen
ruin-refusal bar the quadratic head failed (episodes 0090–0092).

**The verdict: the fix fails honestly, and the failure draws a map.**

- Normalization REFUTED at pilot: worse in every pairing (0.312 vs 0.253
  at η=0.5; 0.241 vs 0.191 at η=0.1) [measured].
- The η line, drift world: 0.5→0.253, 0.1→0.191, 0.05→0.177,
  0.02→**0.161 at 24 seeds** vs the 0.10 bar — C1 FAIL; the lottery
  survives (17/24 clean vs the 20/24 bar — C2 FAIL). The 8-seed pilot's
  perfect 0.000 was the lottery drawing clean — the confirmatory caught
  it [measured].
- η=0 (head frozen after replay schooling): **zero trades, ever** —
  online learning is what drives trading at all [measured].
- η=0.02 where the world learns you back: ruin 0.225 — slow heads trade
  on stale beliefs [measured].
- C3/C4 both green: life 24/24 both worlds, sharpness 0.997; the
  completion-itch pathway tolerates a slow head (dense-event teaching)
  [measured].

What it taught: refusal, tracking, and activity hang on the same dial and
pull in three directions — **no global learning rate buys all three**.
The churn is not a mis-set number; it is the price of tracking with this
head. Third consecutive honest headline failure on this line (0091 quad,
0092 consolidation, 0094 low-η) — the bars keep catching plausible fixes.

Reversal condition: this episode records a registered reversal firing —
it reopens if a (normalization, η) recipe within the registered space is
shown passing C1–C4 at 24 seeds. The named alternative (targeted
low-order terms) is the owner's call and was NOT auto-chained.

Trail: topic head-churn (folder retired); runner `head_churn.py`,
rows `hc-pilot-rows.json` / `hc-confirm-rows.json` / `hc-c4-pilot.json`
in the session scratchpad; pilot published pre-confirmatory in the topic
journey (git history).
