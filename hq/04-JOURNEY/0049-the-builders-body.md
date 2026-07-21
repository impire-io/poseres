# Episode 0049 — The builder's body (2026-07-21)

Feature 030 (`030-inventory-crafting-body`): the C1 Minecraft body grew
from watcher-digger to builder. A width-5 **inventory sense** (mined
blocks / logs / planks / sticks counts + a place-has-material bit — the
world holds the state, the body re-reads it every tick; a sensor, not a
memory system, per the arcs-018/019 sensing-over-remembering lesson) and
two **pocket craft actions** (1 log → 4 planks; 2 planks → 4 sticks),
landing obs 14→19, actions 8→10 as the C1 default, with the exact
feature-027 body one flag away (`c1_anatomy(crafting=False)`). Zero
brain-side edits beyond the anatomy declaration [measured — no core or
dash diffs]; the 029 metadata path put the new group and craft labels on
the dashboard with no dashboard changes, as promised.

**The direction decision, recorded (working agreement):** the owner
overrode the previous evidence gate ("wait for the 14/8 run's
place_ahead behavior") — the builder's body ships *before* the
multi-week run, exploration cost accepted knowingly ("aware of the
consequences… it puts us in line of our ambitions"). The adversarial
case was argued first; the reversal condition is executable and stands
in the spec: if the long run shows the material actions effectively
unused and improvement materially below the 14/8 pilot arm, fall back
to the legacy flag and return the body question to research.

**Specifying found an honesty bug:** the fake bridge let `place_ahead`
mint blocks from nothing while the live bridge already required held
material [measured — fake.py vs bridge.js]. The amended contract makes
placement materially honest in both bridges (place consumes,
blocks-then-planks), and the fake gained wood columns so the full chain
(dig log → craft planks → craft sticks → place) is deterministically
exercisable in the gate — proven step-by-step, with a mid-chain
snapshot round-trip byte-exact.

**The pre-registered pilot decided its bars honestly** (8 paired seeds,
275 steps/arm; pilot-results.md carries every number): bar (a) —
learning robust at 19/10 — **PASS 8/8** (median improvement +0.200).
Bar (b) — craft taken + inventory movement in 8/8 — **FAIL as written,
3/8**, and the diagnosis is the valuable part [measured]: face-to-solid
moments are ~2.5% of steps in the sparse sketch and dig is chosen ~1/10
of them (undirected exploration over 10 actions), so material contact
is the product of two rarities; 2.8× budget moved it only to 4/8 and a
starter block moved nothing — the bar had conflated *expressibility*
(proven deterministically in the gate) with *stochastic contact
frequency in a deliberately sparse world*, and was amended openly. The
engagement question the bar wanted to ask is exactly what the reversal
condition watches during the C1 run, in an overworld whose solid-ahead
rate is far higher than the sketch's [mechanism-argument + the 029 live
session's constant block contact]. Context row (c), the accepted cost
quantified: equal-budget improvement delta (builder − legacy) median
**−0.043** at the registered budget, shrinking to −0.009 at 2.8× — an
exploration tax, not a capability loss [measured].

**Live smoke PASS** against the real 1.21.11 server: hello declares the
inventory channel; 8 given oak logs read exactly 8/64; `craft_planks`
→ logs 7, planks 4; `craft_sticks` → planks 2, sticks 4; the placeable
bit tracked truthfully throughout.

Reversal condition: as recorded in the spec (owner-accepted risk) — if
the multi-week C1 run shows craft/place effectively unused and
improvement materially below the legacy arm, the run falls back to
`c1_anatomy(crafting=False)` (snapshots do not cross the switch,
stated) and the body question returns to research.

Trail: specs/030-inventory-crafting-body/ (spec cdb92ca, plan 07f7e76,
implementation 099ec34, pilot+docs 70f39ab);
specs/027-minecraft-body/contracts/minecraft-adapter.md amended in
place; pilot scripts in the session scratchpad, results in
specs/030-inventory-crafting-body/pilot-results.md.
