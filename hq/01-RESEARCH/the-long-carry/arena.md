# The arena design — the larder loop (H0 candidate, registered before any build)

Written 2026-08-28, before any provisioning or run. This document is
the H0 build's registration: the geometry, the counting mechanism,
the channel-by-channel opacity audit against the rig's real body, the
sibling sense, the probe protocol operationalized, and the dials with
their escalation path. Numbers recorded here that later prove wrong
are corrected openly in JOURNEY.md, never silently.

## The design theorem (what the body forces)

The rig's body — `c1_anatomy(survival=True)`, obs 73 / 13 actions
(0119 amendment-2's correction, re-verified against the anatomy
module today) — carries an absolute pose sense: spawn-anchor-relative
x, z, y and yaw. Therefore **any arena whose chain stages happen at
different places is not opaque**: a linear readout on pose alone
decodes the stage, and H0(a)'s probe rightly fails it. A
station-relay design (collect here, deliver there) was considered
and discarded on exactly this ground — each leg lives at its own
(x, z), so pose identifies the leg even where the decision-relevant
state is hidden.

The consequence, stated as the design rule: **under an absolute pose
sense, global opacity forces loop geometry.** Every chain stage must
traverse the same places, so that at each step the whole observation
— pose included — is indistinguishable across stages, and the only
thing distinguishing stage k from stage k+1 is history. Long-horizon
+ position-opaque ⇒ laps of a closed course, stage = lap count.

## The larder loop

A closed single-file corridor circuit; the chain is N laps followed
by a turn-in; the world itself counts the laps and opens the larder
gate on lap N; eating resets the count. All of it world furniture,
provisioned once — no steward, no harness meter, nothing outside the
game touches the world after provisioning (the probe kit's
standard).

```
      ┌───────────────────────────┐
      │  ......................   │   corridor: 1 wide, 2 high,
      │  .   ┌─────────────┐  .   │   bedrock walls/floor/roof,
      │  .   │             │  .   │   uniform glowstone lighting
      │  .   │   (inner    │  .   │
      │  .   │    block)   │  .   │   J: the junction (aliased
      │  .   │             │  J───┼─?─ decision point) — branch
      │  .   └─────────────┘  .   │   corridor, bent, ~12 blocks
      │  ......................   │   ? : the gate (2-high stone
      └───────────────────────────┘       fill = closed; air = open)
                                   ┌──────┐
                     gate ──── ? ──│larder│ melon patch, probe-kit
                                   │  ▼   │ pattern; drop-ledge exit
                                   └──►───┘ back to loop (one-way)
```

- **Loop:** inner rectangle sized so one lap ≈ 25–30 blocks of
  travel ≈ 100–120 action-steps at the measured gait (~4 steps per
  block, the V1 tape's calibration). Four corners; single-file so
  locomotion and tapes are near-deterministic.
- **The junction J:** one tile of the loop where the branch corridor
  leaves it. On laps 1..N−1 the correct action is to continue the
  loop; on lap N it is to turn into the branch. The branch is bent
  so the gate is NOT in any sightline from J — glance at J reads
  identical geometry on every lap. This is the aliased decision
  point, one per lap: same pose, same walls, same empty hand, a
  different correct action by history alone.
- **The gate:** a 2-high stone fill at the branch's far end; opened
  (set to air) by the world's counter at lap N; closed and reset by
  larder entry. Solid blocks — no sightline through, closed or open,
  until the body is inside the branch. Checking the gate without the
  carry costs a full branch round-trip (~50–60 steps) per wasted
  peek: the memoryless tax the meters read.
- **The larder:** a small chamber with the probe kit's melon patch
  pattern (hydrated farmland, age-7 stems, day-one melon stock — the
  game's own regrowth). Exit is a 2-block drop back onto the loop:
  one-way by the body's jump reach, so every chain re-enters the
  loop at the same tile heading the same way.
- **The counter (world-side, invisible):** a scoreboard driven by
  repeating command blocks doing zone-latch edge detection — when
  the player enters the lap-line zone with latch 0: laps += 1, latch
  1; on leaving the zone: latch 0. At laps ≥ N a conditional block
  fills the gate to air; a larder-entry zone sets laps 0 and closes
  the gate behind (the body is already inside; it leaves by the
  drop). Command blocks are buried in bedrock, out of every
  sightline and never in the observation. A pure-redstone
  T-flip-flop cascade is the fallback if command blocks are vetoed
  as world furniture — same contract, worse reliability at the 5×
  fabric; the choice is the owner's, flagged now.
- **Dig-proofing:** all course structure is bedrock (unbreakable),
  so `dig_ahead` cannot tunnel through the design; the only diggable
  blocks anywhere are the larder's melons.

**Chain length at the defaults:** N = 3 laps × ~110 steps + branch +
larder ≈ 380–440 steps — ≥ 3× the probe world's ~100-step forage
chain (H0(b)) with margin, and ~14 perfect chains per 6,000-step
life (the meter keeps its granularity).

## The opacity audit (channel by channel, the rig's 73)

| Sense (width) | Reading across laps | Verdict |
|---|---|---|
| pose (5) | identical each lap by loop construction | opaque by design |
| vitals (2) | food declines slowly with elapsed time → weak stage correlate within a chain | WATCH — the shuffled-label control decides |
| env (4) | lighting uniform by construction; sin/cos day clock is a global time correlate | WATCH — chain starts spread across day phases decorrelate it |
| blocks (3) | same corridor geometry every lap | opaque |
| mining (1) | no digging anywhere on the course (bedrock); active only in the larder, post-gate | opaque on the probe span |
| pocket (4), hand (7), grid (7) | the chain is pure locomotion — nothing is collected, held, or staged until the larder | opaque on the probe span |
| drops (8) | no ground items on the course (item-kill hygiene between lives as in the rig) | opaque |
| glance (32) | same walls every lap; the gate shielded from J by the bend; larder shielded entirely | opaque by geometry — verified empirically, not assumed |

The two WATCH rows are honest global time correlates that exist in
ANY live arena (hunger and the day clock advance with every step).
They are exactly what the shuffled-label control in the probe is
for: if stage decodes only as well as it decodes from relabeled
time, position is not being sensed — time is. The probe's verdict
rule below handles this; if they alone push decode beyond the
control spread, the reading and the numbers go to JOURNEY.md and the
bar is amended openly (a food-frozen classroom variant of the probe
is the named fallback instrument).

## The probe span, registered now

H0(a)'s decode probe is trained and scored on the **decision span**:
every step on the loop up to and including the junction tile, over
all laps of all recorded chains. Steps inside the branch and the
larder are excluded, and the exclusion is registered here, pre-run,
with its reason: past the junction the lap's decision is already
committed, and inside the branch the gate state is legitimately
visible (that visibility is the peek-tax, a priced part of the task,
not a leak). Aliasing exhibit alongside the probe: the per-channel
mean gap between junction-window observations on lap 1 vs lap N−1
vs lap N, reported raw.

Probe form: multinomial linear readout, observation → lap index
(1..N), fit on recorded flat-rig lives with ground-truth lap labels
from the world's own scoreboard (runner telemetry via rcon, logged
beside the rows, never fed to the body). Verdict: PASS if held-out
accuracy sits within the spread of the same probe fit on 5
lap-label shuffles (the chance band); the raw accuracies are
recorded either way.

## The sibling sense (H0(c))

One declared sense, width 1: `laps` — `frac` = laps_done / N,
saturating at 1.0 while the gate stands open. The special case
restored: the echo world's progress channel, relocated. Implemented
without new machinery on the world side: the counter's command
blocks mirror the scoreboard into a buried indicator column (k lap
⇒ k gold blocks at a fixed buried location); the bridge reads the
column with its world API and publishes the fraction — the bridge
reads the world's own counter, the body senses it as any other
declared channel. The flat body never gets the channel; the sibling
body is `c1_anatomy(survival=True)` + this one sense, everything
else byte-identical.

## The curriculum sketch (d23 discipline, relocated)

45 lessons, three interleaved variants, eat-heavy where eating
happens, hunger-dose cycle decorrelated from variants, every lesson
gated (the d23 gates relocated to this course), classroom prep by
rcon exactly as the rig does today (tp to stand, set world state,
dose, clear):

- **V0 — the larder:** stand inside the larder, melon one ahead: dig,
  collect, hold, eat (the d23 V0 relocated; the mouth lesson).
- **V1 — the lap:** stand before the junction mid-loop, counter set
  below N (rcon scoreboard — classroom prep, teach-time only): walk
  the corridor THROUGH the junction and onward — the continue
  action at the aliased point.
- **V2 — the turn-in:** same stand, counter set to N−1, one lap to
  run: walk the lap, turn into the branch at J, through the open
  gate, into the larder, eat (the full closing act).

Tapes are deterministic corridor walks (FWD runs, TR×2 corners) —
the V1/V2 tape grammar already in the rig. Whether 45 lessons of
this grammar suffice for the composed arms is itself an M0-adjacent
reading; the count is held at 45 for arm-symmetry with the record.

## Dials and the escalation path (pre-registered)

- **N (laps): 3** at H0. If the flat arm matches its sibling — the
  scaffold's reach is longer than 0119 measured — escalation is N
  first (3 → 5 → 8), loop length second; always pre-run, never
  mid-comparison (the README's reversal condition).
- **Loop length: ~110 steps/lap.** Sized to hit H0(b)'s ≥ 3× floor
  at N = 3 with margin.
- **Peek tax: ~50–60 steps** (branch round-trip). If pilot lives
  show a check-every-lap policy erasing the gap, the branch
  lengthens or the antechamber becomes drop-in/detour-out (a
  sharper, still non-fatal tax) — decided on pilot numbers, before
  H0(c) reads, recorded in JOURNEY.md.
- **Life length: 6,000 steps** (the d23-calibrated default) unless
  the measured chain length forces longer — fixed at H0 PASS,
  before any arm's teach, per the README.

## Build plan (the order of work)

1. `arena_provision.py` — the course, the counter, the larder, the
   indicator column; one-time, idempotent, in the probe kit's
   setblock idiom. A fresh superflat world beside the probe world's
   compose file (same server image, own port), so the probe world
   stays untouched for any 0119-protocol repeat.
2. **Mechanism check (instrument bar, before any brain):** a
   scripted tape walker — not the kernel — runs laps and verifies
   the world's own contract: counter increments once per lap
   crossing, gate opens at N and only at N, larder entry resets and
   recloses, drop exit returns to the loop, melons regrow. Bars in
   the 0112 style: instrument before behavior. The same walker
   records the gait calibration (steps per block at the 5× fabric)
   that sizes the loop numbers above.
3. **Flat teach + pilot lives** on the opaque course; the decode
   probe and aliasing exhibit read from these rows (H0(a)).
4. **Sibling teach + lives**, same tapes plus the sense; H0(b) chain
   length measured from its completions; H0(c) read at n = 8 per
   side, same seeds, same doses.
5. Only after H0 PASS: resurrect the 0119 composed scaffolding
   (commit 4171779) onto this arena — M0, then the arms.

Scripts live in the session scratchpad while they churn (the
constitution's rule); they land in this folder's `rig/` when their
readings are cited, exactly as the-opaque-world did it.
