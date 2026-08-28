# Journey — the-long-carry (started 2026-08-26)

## 2026-08-28 — the arena designed before any build: the larder loop; one pre-run amendment

**Amendment 1 (pre-run, factual):** the README's protocol spine
said "design 0015's body at obs 86 / 13" — the same error 0119's
amendment 2 corrected in its own README. The rig's machinery
declares `c1_anatomy(survival=True)`: obs 73 / 13 actions (no
flood, no aim channel), re-verified against the anatomy module
today (the n23_runner's `# 33` comment is stale; the summed widths
are authoritative). Corrected before any build; arm-symmetric
either way.

**The design theorem, forced by the body [mechanism-argument]:**
the body senses absolute pose (spawn-relative x, z, y, yaw), so any
arena whose chain stages live at different places hands the stage
to a linear readout on pose alone — H0(a) would rightly fail it. A
station-relay candidate (collect here, deliver there) was
considered and discarded on exactly this ground. Under an absolute
pose sense, global opacity forces LOOP geometry: every stage
traverses the same places and only history distinguishes them.
Stage = lap count.

**The candidate, registered in `arena.md` before any provisioning:**
the larder loop — a single-file bedrock circuit (~110 steps/lap),
N = 3 laps counted by the world itself (buried command-block
zone-latch onto a scoreboard; pure-redstone fallback named, choice
flagged to the owner), a bent branch at the junction hiding a solid
2-high gate that opens at lap N and resets+recloses on larder
entry, the probe kit's melon patch inside, drop-ledge one-way exit.
Chain ≈ 380–440 steps ≥ 3× the probe world's; ~14 perfect chains
per 6,000-step life. The junction is the aliased decision point —
same pose, same walls, empty hand, different correct action per
lap. The memoryless tax is the branch round-trip peek (~50–60
steps), smooth, never fatal (the 0119 meter lesson). The
channel-by-channel audit over the real 73 marks two WATCH rows
(food decay, day clock — global time correlates present in any
live arena) for the shuffled-label control to arbitrate; the probe
span (decision span only — branch and larder excluded, the peek
being a priced part of the task, not a leak) is registered in
arena.md with its reason, pre-run. Sibling sense: width-1 `laps`
frac read from the world's own counter via a buried indicator
column. Build order: provision → mechanism check by scripted
walker (instrument before behavior) → flat teach + pilots (H0(a))
→ sibling (H0(b,c)) → only then the 0119 scaffolding and the arms.

## 2026-08-28 — the arena is real and its contract holds: MECHANISM PASS, 15/15

The larder loop exists on a live server (rig/: own compose world,
lc-minecraft on 25603, bridge on 25591) and the scripted walker —
never the kernel — verified the world's own contract end to end
[measured, rig/mechanism-report.json]: the lap counter counts
exactly once per taught-direction crossing (1, 2, 3); the gate
stays obsidian through laps 1–2 and is air at lap 3; larder entry
resets the count to 0 and the gate recloses; the buried indicator
column rises and falls with the count; dig→collect→eat lands on the
larder's melons (7 slices, food 15→20); the exit drop returns the
body to the loop (feet −58 → −60) and is one-way (max jump reach
−58.7); and counting resumes after the chain (fresh lap reads 1).

**Gait calibration [measured]:** 146 steps/lap (4.87 steps/block at
the 5× fabric) — slower than the V1 tape's ~4, so the chain is
DEEPER than designed: ≈ 620–650 steps end to end, ≥ 6× the probe
world's forage chain, ~9 perfect chains per 6,000-step life.
arena.md's numbers corrected from the report.

Two build lessons, both folded into `arena_provision.py`: **a
1-block step-up needs 3-high clearance over its approach cell** —
the jump arc bonks a 2-high ceiling (walker run 1 wedged at the
gate cell); and **melon blocks are unclimbable walls under a 2-high
ceiling** (walker run 2 wedged on the patch), which contains the
body usefully but constrains in-larder pathing. The gate is
obsidian, not stone: stone is only ~150 steps of barehanded digging
— a breach path for a persistent digger; obsidian is ~5,000,
effectively never.

## 2026-08-28 — flat teach 45/45; pilot life 1 reads zero; amendment 2 (probe rows), pre-probe

**Two rig decisions, registered in `lc_runner.py` before its teach
ran:** the parent's hands go closed-loop (a WaypointTeacher steering
from the body's own pose and solid_ahead channels — the 146-step lap
outruns the d23 open-loop tape grammar), and every lesson runs a
uniform 340-step episode, idle-padded, so the engine config never
varies across the taught chain's resume. Curriculum: V0 larder-eat
(the d23 V0 relocated), V1 the-lap, V2 turn-in with the counter
preset to 2 by classroom prep (teach-time rcon, the registered
allowance).

**The flat teach landed 45/45 [measured]:** 7 retries, every one a
V2 first-attempt eat-miss (`done=True eats=0 laps=0` — walk and
world contract clean, the eat jittered), one lesson needing its
third attempt. Mechanism read: V2 arrives at the dig by navigation
with residual pose scatter; V0's teleported stand never missed.
Demo spans as designed: V0 89 obs, V1 ~140–155, V2 ~250.

**Pilot life 1, the first behavioral datum [measured]:** the taught
flat rig, hungry-born, 6,000 steps — zero lap crossings, zero
chains, zero eats; one branch peek; out_of_context 3,099; food
20→6, no starvation loss. The flat rig as taught does not circulate
the loop unaided. Not a verdict: H0(c)'s discriminating pair exists
exactly to classify this — sibling succeeds ⇒ the gap is the memory
demand; sibling fails too ⇒ the task is too hard for non-memory
reasons and the rebuild clause fires.

**Amendment 2 (instrument, registered BEFORE the decode probe
runs):** with zero crossings the pilot rows carry a single lap
label, and H0(a)'s probe cannot read a one-class dataset. Opacity
is a world+body property, policy-independent, so the probe's rows
come from the scripted walker driving real chains through the live
body (`probe_walk.py`), recording the same 73 channels the body
senses. The probe's question, span, labels, and chance band are
unchanged; pilot rows stay in the record as the behavioral
baseline.
