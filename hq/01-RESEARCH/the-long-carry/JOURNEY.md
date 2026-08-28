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

## 2026-08-28 — the WATCH rows fire: first H0(a) read FAILS through the sky; two amendments, both pre-re-read

**The registered 3-class probe read, as-is [measured, walker rows,
6 chains]:** true held-out accuracy 0.5205 vs chance band 0.3538 ±
0.0708 (2-SD bound 0.495) — FAIL as read. The junction exhibit
named the carriers: env.sin_time gap 1.12, env.rain 0.84,
env.cos_time 0.35 — the day clock and the weather (it genuinely
rained mid-recording). The arena.md WATCH row fired exactly as
registered.

**Amendment 3 (world config, the design theorem extended):** any
monotone exogenous SENSED signal is a progress channel — the day
clock decodes a within-chain ordinal the same way the echo world's
progress channel handed over sequence position, just through the
sky. The arena pins `advance_time false` (noon) and
`advance_weather false` (clear) in `arena_provision.py`; the env
channels become constants and carry nothing. Re-recorded under the
pinned sky: the junction gaps collapse (top channel pose.sin_yaw
0.17, vitals.food 0.04) — the world-side leaks are dead
[measured].

**But the re-read still sits at 0.52 vs bound 0.505, and the
analysis says the remainder is label structure, not sensing
[mechanism-argument, numbers recorded]:** (a) the exit drop lands
mid-ring, so the pre-first-crossing phase ("lap 1") covers only
the half-ring back to the lap line — position legitimately
identifies it (441/895/1328 label counts: half a lap), which is
arena topology, not through-wall sensing; (b) the label cap at 3
merged crossings-2 with crossings-3 — but the gate opens at
crossings ≥ 3, so THE aliased junction decision is exactly
crossings 2 vs 3 on identical cells, which the capped labels
cannot see.

**Amendment 4 (the probe's decision-pair form, registered BEFORE
it runs):** labels uncapped to 1..4 (4 = post-third-crossing, the
turn-in approach). The H0(a) verdict moves to the two aliased
pairs — 2-vs-3 and 3-vs-4 — each read as a binary linear probe on
the steps of those labels restricted to the CELL SUPPORT both
labels visit (so route topology cannot cheaply separate), with the
chance band from 20 within-chain label-swap permutations, PASS =
within band per pair. The 3-class number stays reported as
context. The registered question — can a linear readout tell WHICH
LAP from the body's observation where the world demands different
actions — is unchanged; the pairs are its exact decision form.

**H0(a) PASS under amendment 4 [measured, pinned-sky walker rows,
6 chains, decode-report.json]:** pair 2v3 (the full-ring aliased
laps, 1,773 steps over 30 shared cells) true 0.5039 vs control
0.5036 ± 0.0633 — dead chance; pair 3v4 (the turn-in approach, 882
steps, 15 shared cells) true 0.518 vs 0.5016 ± 0.0113 — within
band. Context multi-class 0.361 vs 0.240 ± 0.057, the excess fully
carried by label-1's half-ring topology (explained above, on
record). Junction exhibit top gaps: pose.sin/cos_yaw 0.27/0.24 —
the walker's own turn at the junction tile, behavioral, small.
**The arena is opaque where it must be: the aliased decision pairs
read at chance to a linear readout on the decision span.** One rig
lesson rode along: the waypoint follower's 45° heading quantization
preserves arrival offsets, so wall contact can wedge the bbox on a
block corner with solid_ahead reading 0 (measured at both an inner
and an outer corner) — goto() now carries a deflect-and-push
unstick, and probe_walk's 6 chains ran clean through it.

## 2026-08-28 — the sibling built; the H0(c) schedule registered before any comparison life

**The laps sense is live [measured]:** the bridge gains an
env-gated, default-off `LAPS="x,y,z"` sense in the flood/aim/peers
pattern — width 1, appended LAST, reading the arena's buried
indicator column with the bot's world API (the world's own counter
as world state; smoke test: score 2 → 0.667, score 0 → 0). The
sibling body is declared IN THE RIG — `c1_anatomy(survival=True)` +
the one sense, obs 74/13 — no kernel or anatomy-module change. The
bridge runs LAPS-enabled for BOTH arms; the flat body simply does
not declare the topic, so its observation is unchanged and the
declared sense stays the only variable.

**Schedule, registered now:** flat pilot lives 1–3 ran under the
UNPINNED sky (before amendment 3) and cannot pair with sibling
lives; they move aside as the pre-pin pilot record
(flat-lives-prepin.jsonl), their zero baseline standing as
reported. The H0(c) comparison runs fresh: rounds 1–8, one flat
life and one sib life per round, interleaved round-robin against
world drift (the 0119 amendment-1 precedent), all under the pinned
sky, same doses, same seeds, paired by round. H0(b) reads its
chain length from the sib arm's completed lives, per the README.

## 2026-08-28 — H0(c) does NOT separate: both arms zero; the rebuild clause fires with a sharp diagnosis

**The read [measured, rounds 1–3, both arms, pinned sky]:** every
life zero — flat 0/0/0 and sib 0/0/0 on crossings, chains, and
eats; every life carried 1–2 false completions and out_of_context
4.2–5.7k of 6,000. The run was stopped after three witnessed pairs
rather than eight, recorded openly with the reason: lives are
fixed-seed from the same taught brain with no cross-life learning,
so further rounds sample only world jitter around an outcome three
pairs already witnessed at exactly zero–zero; the registered n = 8
belongs to the SEPARATION read, which cannot arise here.
Bar H0(c) FAILS on its own second branch: the sibling failing too
means the task is too hard for non-memory reasons — rebuild openly,
no comparison reads until H0 passes.

**The diagnosis, from the traces [measured]:** the failure is NOT
locomotion. Sib life 1 walked from the stand along the north row,
into the branch, and parked at (15,8) — one cell before the closed
gate — for 4,672 of 6,000 steps (dwell map in the npz; the obsidian
dig-proofing earned its keep). The policy expressed the V2 turn-in
recipe from birth, with the laps channel reading 0.0 the entire
life against the demo context's 0.667+: **recipe selection ignores
the stage signal even when the stage is sensed** — one channel of
74 carries no weight in context matching, so the closing recipe
fires on the wrong lap and the recipe hold pins the body at the
gate. The flat arm fails the same way minus the sense (its zeros
are over-determined).

**What this means for the topic [judgment, stated for the owner]:**
the arena passes opacity (H0(a)) and depth (chain ≈ 640 steps,
6×), but the wild policy stack cannot express stage-conditional
behavior through recipe selection even with the stage IN the
observation. That cuts deeper than the arena: 0119 measured that
frames speak only through drive valuation of one-step predictions —
if the scaffold cannot act on a sensed stage signal, a composed
tier carrying the same signal has no behavioral path to a win
through this scaffold either. The rebuild fork (owner's direction
call): (a) rebuild the WORLD easier — bring food into distal reach
so the seen-forage machinery engages, narrowing the carry demand to
one aliased choice with everything else affordance-driven; (b)
rebuild the INSTRUMENT — make the sibling's sense enter where
selection actually happens, at the cost of hand-building the
pathway the composed arms would also need; (c) re-scope the gate's
question to the mechanism that CAN carry stage into behavior
(prediction-driven arbitration, not recipe selection), which is a
kernel-side research direction, not an arena patch.

## 2026-08-28 — the owner's steer: the world stays; the brain must learn futility. Amendment 5, pre-run

**The owner's direction (in session):** narrowing the world makes
the test less representative — "our brain should be able to figure
out that pushing something a lot of times with no effect is
useless." The 4,672-step gate dwell is not a flaw to design around;
it is the measured deficiency itself.

**The mechanism reading, from the recipe source [measured in
code]:** (a) recipe selection is a stateless per-step argmax —
`drive_value_of(terminal) + label_beta·label` — with no
disconfirmation pathway anywhere; worth is written by demonstration
and never eroded by futility. (b) The gate-park is nearest-step
parroting: V2's north-row leg passes through the birth stand, so
the policy adopts the recipe mid-path; at the closed gate the
subgoal is the recorded step BEYOND it, in-context, pointer
stalled, hold pulling forever — and the stall signal already exists
(`advance_events` froze) feeding nothing. (c) V1's lap
demonstrations were never stored: `add_demonstration` requires a
pocket gain, so process-only demonstrations are unrepresentable as
recipes. (d) The sibling sense is structurally inert in this
stack: a sense reaches selection only through the terminal's drive
value, and V2's terminal was recorded after larder entry — the
world's own reset had already zeroed the laps channel. The sib
zero is mechanically over-determined.

**Amendment 5 (the spine's policy, pre-run, forced by the numbers
above):** the life policy gains FUTILITY EROSION, rig-level (a
RecipePolicy subclass, no kernel change), identical across arms:
per-recipe stall counters (+1 per selected step without pointer
advance; −0.25 per unselected step; reset to 0 on advance);
recipes with stall ≥ K = 300 go temporarily dead; all dead →
selection None → the curiosity wanderer resumes. Slow forgiveness
means dead recipes revive and get re-checked — the peek cadence
emerges from the futility constants rather than being scripted.
Constants are first-guess dials, registered now. Predictions
registered before the run: the body abandons the gate within
~hundreds of steps (disengagement latency measurable); drift
wandering on a small closed course crosses the lap line; the world
counts; the gate opens; a revived V2 succeeds — nonzero chains even
blind, wasteful; the prior no-futility rounds stand as the
baseline record (renamed *-nofut). Whether the sibling sense can
separate AFTER futility exists is the re-read — and if it cannot,
that is the next measured finding, not a failure of the arena.

**Refinement, one life later [measured, flat-fut life 1]:** the
per-recipe erosion form is inadequate two ways, both visible in its
first life — boundary thrash (556 disengagement events, a 50% duty
cycle at the kill line: die at 300, forgive to 299.75, revive,
re-select) and, deeper, COHORT FALLBACK: the memory holds ~15
near-identical turn-in recipes, so when one dies the argmax falls
to its twin pulling to the same gate — the body still spent
4,972/6,000 steps at (15,8) even as advance went 5× and
out_of_context halved. The failure is the FOLLOWING behavior, not
one recipe's identity, so the refined form is layer fatigue: K =
200 consecutive followed steps without pointer advance puts the
whole recipe layer dead for W = 800 steps (curiosity wanders), then
it revives and re-checks — the peek cadence emerges from (K, W) ≈
one gate-check per ~1,000 steps, ~6 per life. Registered before the
re-run; the aborted round's rows discarded (one flat life, its
numbers kept here).

## 2026-08-28 — layer fatigue witnessed: the deficiency repaired, the peek loop born, chains still zero

**Rounds 1–3 under layer fatigue [measured, paired]:** flat
crossings/chains/peeks 1/0/0, 0/0/3, 0/0/2; sib 1/0/0, 0/0/2,
0/0/0. Gate-parking is ABOLISHED (no branch dwell anywhere;
disengagements 4–6/life; dead_steps 2.4–4.4k ≈ the (K, W)
cadence); the peek loop the arena prices EMERGED (revive → walk to
gate → find it shut → fatigue → wander); and the first
brain-driven lap crossings in the arena's record landed (one per
arm, round 1). The owner's named deficiency — pushing without
effect — is repaired at the prototype level. But chains stay zero
in every life: the curiosity wanderer drifts ~1 crossing/6,000
steps and cannot bank three crossings between peeks, and the sib
sense remains selection-inert — no separation.

**The two load-bearing gaps, now isolated with numbers
[mechanism-argument on measured behavior]:** (1) **process memory
does not exist** — V1's lap demonstrations were never storable
(recipes require a pocket gain), so the taught lap lives only in
kernel fast-weights with no behavioral carrier; the body was
taught the lap fifteen times and cannot follow it. (2) **futility
must be place-keyed, not layer-keyed, once process recipes
exist** — layer fatigue kills the lap recipe together with the
stalled turn-in cohort; the per-recipe form survived the lap but
fell to cohort fallback; the clean shape is "this PLACE is
futile": a dying recipe's stalled subgoal poisons every recipe
currently pointing there. Both are rig-prototypable; both are, if
they pay, kernel feature candidates in the recipe head's own
grain.
