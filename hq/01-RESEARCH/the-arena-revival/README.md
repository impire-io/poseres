# The arena revival — with the ladder in the kernel, does composition pay where the chain outruns the scaffold?

**State:** active
**Started:** 2026-09-27

## Abstract

Episode 0120 built the compositional gate's deciding arena — the
larder loop, live Minecraft, food behind N = 3 laps counted by the
world's own buried machinery, measured position-opaque at the
aliased decision pairs and 6× the probe world's chain — and then
measured that the stack could not walk it: zero chains in every
life, flat and stage-sensing sibling alike, with three gaps isolated
by number (no futility, no process memory, no selection pathway for
stage). Episodes 0121–0123 shipped those three rungs as kernel
features 045/046/047 (v2.3.0–v2.5.0), each off by default and
bit-exact off. This topic revives the arena from design 0021's kit
and takes the readings 0120 could not: first whether the
ladder-equipped stack walks the loop at all (the sibling, stage
sensed, is the positive control; the flat opaque arm the memoryless
reference), then the gate's own M0–M2 comparison — flat against
composed where the life must carry where-it-is. A composition win
beyond spread reopens the gate's shape question with numbers; a
loss on a valid arena moves design 0020's question from WHERE
composition pays to WHETHER this mechanism can; a sibling that
still cannot walk refutes the ladder as sufficient and names the
next gap by its own watch counters.

Provenance, on the record: this registration was opened by an
agent session at the owner's instruction to start the revival. The
bars below are transcribed from the-long-carry's registration
(commit `a4b4386`) and design 0021 — the instrument bars keep their
original pass rules, the ladder dials are the prototype's measured
constants — with the two additions 0123 forces (R1, M0(d)) marked.
Nothing has run. The owner reviews these bars before the first
pilot; amendments are pre-run, with numbers, in JOURNEY.md.

## The question

On the larder loop — a live world that hides chain position AND
whose chains outrun the policy scaffolding's reach — now that the
kernel carries futility, process recipes, and stage-conditional
selection: does a composed tier pay beyond spread at last, and if
so which shape carries, the stacked tower or the identity-bound
reference?

## Pre-registered bars

Protocol spine, common to everything below, exactly as 0120 left it
(`arena.md`, `rig/`): the survival rig's machinery
(`examples/minecraft/survival/arms/n23_runner.py`) pointed at the
arena world (`lc-minecraft`, port 25603, bridge 25591); the body as
the machinery declares it (`c1_anatomy(survival=True)`), deficit
gate OFF, the 5× fabric; the world config pinned (`advance_time` and
`advance_weather` false — the extended theorem of 0120); the
WaypointTeacher as the closed-loop parent; the 45-lesson loop
curriculum (V0 larder-eat / V1 the-lap / V2 turn-in, interleaved,
dose cycle decorrelated by round); hungry-born 6,000-step lives;
N = 3 laps. The sibling body is the flat body plus the one declared
`laps` sense (`frac` = laps/N, appended LAST, env-gated in the
bridge) — byte-identical otherwise.

The ladder dials, identical across every arm that carries them,
recorded pre-run:

- `RecipePolicy(futility_k=200, futility_w=800)` — the prototype's
  measured constants (0120: K = 200 followed steps without pointer
  advance, W = 800 dead; design 0021: the rig's layer fatigue is the
  shipped place-keyed form's degenerate case, so the measured
  crossings carry over). Watch counters `fatigue_events` /
  `revive_events` reported per life.
- `RecipeMemory(process=True)` with `label_index` at the food
  channel — the applauded ending stores the walked path (feature
  046). Watch: recipes stored per teach, process vs acquisition.
- `stage_indices` = the declared stage channel(s) wherever a stage
  exists in the observation — the sibling's `laps` channel (its
  index is the last observation channel); for the composed arms the
  tier's carried context exposed as observation (M0(d)). The flat
  opaque arm has no stage channel to declare and runs `()`.
  `stage_tolerance` at the shipped default 1/128: the `laps` sense
  is quantized at {0, 1/3, 2/3, 1}, so the default separates every
  stage with margin. Watch counter `stage_filtered_events`.

The rig's own layer-fatigue prototype (`LoggingRecipePolicy` in
`rig/lc_runner.py`) is REPLACED by the shipped dials before any
teach runs — the prototype never runs beside the kernel form
(constraint carried from design 0021: every prototype a rig-level
subclass, the kernel untouched by research; the rungs are now
kernel, so the rig uses them as shipped).

- **Bar R0 — the revived arena still binds** (instrument; before any
  brain; the original H0 instruments with their original pass
  rules, re-witnessed because the world is re-provisioned):
  - (a) `mechanism_check.py` PASSES 15/15 on the re-provisioned
    world — counter increments once per lap crossing, gate opens at
    N and only at N, larder entry resets and recloses, drop exit
    returns to the loop, melons regrow, indicator column mirrors
    the count — and records the gait calibration (0120 measured 146
    steps per lap, 4.87 per block; a materially different gait
    re-sizes the life length pre-run, recorded).
  - (b) the decode probe re-reads PASS on fresh walker rows
    (`probe_walk.py` → `decode_probe.py`): the aliased lap pairs
    2v3 and 3v4 as binary linear readouts on the decision span,
    each within its 20-draw within-chain label-permutation chance
    band (0120: 2v3 0.5039 vs 0.5036 ± 0.063). Opacity is a
    world+body property and is re-measured, not assumed.
- **Bar R1 — the ladder walks the loop** (instrument for M; the
  reading 0120 could not take — NEW, forced by 0121–0123): the
  SIBLING body, taught on the 45-lesson curriculum with all three
  rungs on (dials above, `stage_indices` = the `laps` channel),
  then n = 8 hungry-born 6,000-step lives, seeds and dose cycle as
  0120's rounds. Primary meter: chain completions (full-chain
  eats). PASS = chains beyond life spread above the 0120 sibling
  baseline (zero in 8/8 lives — `sib-lives.jsonl` at `a4b4386`);
  crossings, peeks, disengagements, dead steps,
  `stage_filtered_events`, recipes stored (process / acquisition)
  reported alongside. FAIL = the ladder is not sufficient even with
  the stage sensed; each rung's watch counters localize which rung
  is inert, recorded — and M1 does NOT read (it would be
  zero-vs-zero again, the 0120 lesson). Escalating the arena (N,
  loop length) is not the response to an R1 FAIL: the world stays,
  the brain must learn (the owner's steer, 0120 amendment 5).
  Alongside, reported not gating: the FLAT opaque arm with rungs 1
  and 2 on (no stage channel exists to declare) runs the same 8
  lives as the memoryless reference — its chains, if any, price the
  peek-tax route the arena was built to tax.
- **Bar M0 — the scaffolding is live-real on the arena**
  (instrument; the 0119/0120 bars re-read here): (a) tier-2 alive
  and mapping ≥ 0.95 of steps through teach and lives; (b) the
  cross-tier arbiter holds the policy predictor on ≥ 5% of directed
  steps in at least one life segment (0119 measured 31–52%); (c)
  composed state round-trips encode→decode→encode byte-identically
  as the blob+sidecar pair, and a life resumed from snapshot
  continues tier-2 intact; (d) NEW, forced by 0123 — the composed
  tier's carried context is exposed as declared stage channel(s)
  (rig-level, no kernel change) and `stage_filtered_events` reads
  nonzero in a taught life, else rung 3 is inert for the composed
  arms and M1 would read through the same dead pathway 0120
  measured. A FAIL here is an instrument finding that blocks the
  comparison until routed.
- **Bar M1 — the headline: composition pays where the carry
  binds.** Arms flat / tower / bind-pred, every arm with the ladder
  on (flat: rungs 1–2; composed: all three with the carried stage
  as the stage channel); teaches land with flat's first (the T0
  discipline), then 8 hungry-born lives per arm interleaved
  round-robin by round against world drift, same tapes, same hunger
  dosing, same seeds. Primary meter: chain completions per arm.
  Secondary, reported not gating: deepest chain stage reached,
  first-completion latency. PASS = at least one composed arm beats
  flat beyond life spread — 0119's and 0120's standing condition
  fires and the gate's shape question reopens with these numbers.
  FAIL with R0/R1 valid = composition as prototyped does not buy
  carried state at exactly the demand that motivated the gate — a
  mechanism finding for design 0020, not just a shape one. *Noise
  clause, registered now (the 9a725ed precedent):* if at n = 8
  every pairwise difference on the primary meter sits inside one
  paired SE, scale to n = 16 with the verdict rule declared before
  any scaled round reads; still inside spread at n = 16 = a
  measured indistinguishable, not a null to re-roll.
- **Bar M2 — the shape** (reads only if M1 passes): bind-pred vs
  tower on the primary meter beyond life spread decides which shape
  carries where carrying is the task. Standing secondary either way,
  inherited from 0119: a beyond-spread tower-BEHIND-flat separation
  graduates 0119's nominal inversion into a measured cost of imposed
  hierarchy in the wild.

## Reversal condition

Carried forward unchanged from 0120 and 0123, plus this topic's own:

- **The ladder's necessity** (0120): a taught life of the flat arm
  with the ladder OFF completing chains beyond spread on the larder
  loop reopens the necessity claim — the gaps were dials, not
  architecture. The 0120 record (flat, 8 lives, zero chains, before
  any futility) stands as that baseline; it is not re-run unless
  the world changes.
- **The eligibility form** (0123): a revival reading where hard
  eligibility is the wrong shape — taught lives where the
  demonstrated partition strands the body, stage drift beyond
  tolerance leaving zero eligible recipes for whole phases while a
  soft preference would have walked — reopens the eligibility form
  with those numbers.
- **The gate** (0119 → 0120, standing): a beyond-spread composition
  win here reopens the gate's shape question with these numbers and
  this world; a composition loss on a valid arena (R0, R1, M0 all
  green) is the strongest evidence yet that the composed-frame
  prototype does not buy carried state, and design 0020's open
  question moves from WHERE composition pays to WHETHER this
  mechanism can.
- **This topic's direction:** if R1 FAILS on the sibling, the
  assumption that the three rungs suffice for stage-conditional
  behavior is refuted; the topic records which rung the counters
  convict and stops before M1 — the next gap becomes its own
  registration, not an amendment here.

## Verdict

<Empty until graduation. Filled by /research-graduate: PASS/FAIL per
bar with the honest numbers, each load-bearing claim tagged
[measured] / [mechanism-argument] / [judgment].>
