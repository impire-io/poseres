# Episode 0050 — The ladder, not the button (2026-07-21)

Hours after feature 030 shipped `craft_planks`/`craft_sticks`, the owner
argued them back out — and won: a macro craft is **a skill wearing a
primitive's clothing**. In Minecraft's own mechanics crafting is a
sequence over a lower interface with epistemically-gated availability
(you figure out what wood is for; some recipes need a crafting table
before they exist at all), and a one-button craft makes the body answer
the question the brain was supposed to be asked. The owner's preference,
recorded as the direction decision: honest low-level primitives over
flattering high-level ones, with hierarchy left to be learned — and a
never-climbed ladder accepted in advance as a publishable null.

Feature 031 (`031-honest-primitives`) is that decision built. The
macros are gone. In their place: **`hold_next`** (cycle the held
material class — selection is the brain's now; 030's auto-pick
placement was itself a mini-macro and is gone too), **`grid_put`** /
**`grid_take`** / **`take_result`** over a 2×2 staging grid, and two
new senses — `hand` (one-hot held class) and `grid` (staged counts +
what the grid currently offers). The offer channels are the load-bearing
design [mechanism-argument, now gate-proven]: vanilla itself shows what
a staging would yield *before* any craft, so staging a log has a
next-tick sensed consequence — the ladder's every rung is individually
learnable one-step structure, and *climbing* it is the open question.
Offers are vanilla-exact (one log exactly → planks; a column-adjacent
plank pair → sticks; a second log kills the offer — itself a learnable
consequence). C1 default: obs 28 / actions 12, ids 0–7 unchanged from
027; the 14/8 legacy stays one flag away (the reversal path). Zero
core edits; the dashboard picked up both new groups and all four labels
with no changes, again.

The pilot decided its one bar and published its context honestly
[measured — pilot-results.md]: learning robust at 28/12 (**8/8**,
median +0.142); the equal-budget exploration tax doubled vs the macro
body (median **−0.115** vs −0.043 — bigger body, bigger tax, on the
record); the new senses move in every seed (48–75 units — hold/stage
give the drive immediate consequences, where 030's pocket sat still in
5/8 seeds); and chance climbs only the first rung: **one accidental
planks-craft in 8×275 undirected steps, zero sticks** — the chance
baseline the long run's emergence claim must now beat. Live smoke PASS
on the real 1.21.11 server: the whole ladder over the wire, both real
crafts confirmed by real inventory deltas; the boot also caught a
bridge load-order bug the parse-only check could not (fixed).

The stated pragmatic seam: live, the staging grid is body furniture — a
virtual grid whose material flows in and out of the real inventory are
real and whose `take_result` executes the real craft, success confirmed
by the world's own count delta (the world stays the authority; declared
in the contract, not discovered later).

Reversal condition: per spec 031 (supersedes 030's) — if the multi-week
run shows the grid primitives effectively unused and improvement
materially below the legacy pilot arm, fall back to
`c1_anatomy(crafting=False)` and return the body/hierarchy question to
research with the run's engagement data as its opening evidence.
Successor experiments, named: the crafting table as the next rung
(placement-prerequisite structure) if the 2×2 ladder shows climbing;
skill discovery → self-registered tools (Doc 02 §5's reserved door) if
it does.

Trail: specs/031-honest-primitives/ (spec e9abc27, plan/tasks, pilot
results; implementation e589b77, pilot+smoke+docs 6cd50e6);
specs/027-minecraft-body/contracts/minecraft-adapter.md second
amendment; pilot/smoke scripts in the session scratchpad.
