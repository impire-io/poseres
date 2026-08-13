# 0012 — Anatomy from world: the mapping process

**Status:** design (owner-directed, 2026-08-13). The brain is generic;
capability walks in through the body (the senses-first rule, GENESIS).
This document is the structured process for deriving an anatomy — the
sensors, actuators, and channel contract — from any target world, so a
person who wants to mount the brain in a specific environment can form
a body that makes sense for that world. Run it by hand today; the
skill `/anatomy-mapping` walks it; every step is written to be
mechanized later. Each rule below carries the measurement that taught
it — none of this is theory.

## The process

### 1. Inventory the world's own facts

Enumerate what the world itself tracks and emits, without inventing
anything: state (positions, meters, inventories, entity lists,
weather, clocks), events, accepted actions, and — critically — every
action's NATIVE duration and where that time is computed (client wall
clock vs world tick: c1e amendment 1 measured Minecraft digs are
client-wall-clock while eats are server-tick; the tape had to know).
The inventory is a table: fact, owner (world/body), units, update
timing. Never import names or classes — identity enters only as
properties and appearance signatures (feature 033, the owner's
argument).

### 2. Name the loops the life must close

For each goal the life is supposed to live (eat, build, trade, reach),
write the full chain act → consequence → … → pay, in world facts.
Example, native survival: dig → block breaks → drop exists on the
ground → walk near → pocket gains → hold → consume → food rises.
Every arrow is a claim the anatomy must make learnable.

### 3. The pairability audit (the one-step rule)

The event head learns one-step pairings: prev-observation, action,
next-observation. For EVERY arrow in every loop, ask: does the sensed
consequence land within one control tick of the act, in a channel the
body carries? Three failure shapes, each measured, each with its fix:

- **Delayed pay** → add a sense that makes the intermediary VISIBLE.
  Minecraft pays the pocket seconds after the break; the head's best
  pocket-gain prediction was +0.0020 against a 1/128 threshold — no
  completion ever fired and the deficit gate was connected to nothing
  (HEAD-READING). The drop on the ground was the invisible
  intermediary; the drops sense makes collecting a seeable,
  completable act.
- **Acts longer than a tick** → held intentions with SENSED progress
  on the progress channel, whatever the intention (dig cracks,
  feature 033; the chew, arms amendment 1 — 0 eats became eats the
  day the chew got cracks).
- **Split samples** → consequence channels that update on different
  ticks (food vs inventory at 50 ms) need skew-tolerant detectors at
  the harness (arms amendment 3), never tighter thresholds.

### 4. Senses from the gaps

Each unpaired arrow becomes a channel, in the house grammar:

- **Properties, not names**: the world's own facts (placeable, edible,
  counts) plus an appearance signature (sha256 of the identity string,
  bytes 0..2 → [−1, 1]) — stable, distinguishing, semantics-free.
  Categories are the brain's to form.
- **Egocentric geometry for anything spatial**: bearings and sector
  distances in the body's OWN frame, so a turn moves the world across
  the senses — that is what makes walk-toward-the-seen learnable (the
  glance, the drops sense; verified rotating at D1). Declare the sign
  convention from measurement, not intention (D1 found mineflayer's
  yaw frame left-handed).
- **Meters normalized [0, 1]**; the deficit gate is defined against
  that range (feature 042).
- **Aggregates saturate honestly — declare the cap.** The pocket
  channel's min(n, 64)/64 pinned a 155-item life at 1.0 and starved
  its meter invisibly (c1e run 3). A cap is fine; an undeclared cap
  is a future defect.

### 5. Actuators as intentions

One command grammar: instantaneous acts fire in a tick; anything
longer is a held intention — first command begins, further ones
continue, ANY other releases, a safety cap bounds a going-nowhere
hold. Body-side virtual state (a held kind, a staging grid) must be
enumerated and RESETTABLE by the classroom: bridge-virtual state
survives world resets and even pocket clears (arms amendment 2 — the
held NAME revalidated after a dig and silently inverted a lesson).

### 6. Scale and drive-band check

New channels move obs_dim: check the config's scale-invariant rules
(learning rate, parsimony) still apply, and — the dial that actually
decides behavior — whether the itch terms the new senses enable can
CLEAR the drive band (0.06–0.15, Doc 0011). A sense that feeds a
+0.007 itch is drowned by drives regardless of correctness (the chew
before eat-heavier teaching). If a signal must win sometimes, budget
its taught magnitude like you budget the channel itself.

### 7. Instrument-grade first; nothing is faked

New anatomy lands as an opt-in mode; the handshake's width checks make
mismatched stacks fail loudly at boot. There is NO fake world at any
layer (the owner's rule, hardened 2026-08-13 after three arcs of
fake-blessed behavior broke live): the adapter contract is proven by a
live contract check against the real environment, and behavioral
evidence comes from lives and probes in that environment. Promotion
into the shipped default happens only on measured bars.

### 8. Teach what the senses afford

Every new sense gets lessons that exercise it (walk to a seen melon,
collect a seen drop); every meter is witnessed MOVING during teaching
(hungry teaching, episode 0083 — a meter taught flat is a channel the
head never learns); classrooms are clean-roomed (pocket cleared, hand
normalized, world admin only BETWEEN readings).

### 9. Instrument bars before behavior bars

Before any behavioral gate runs, a D1-style live reading proves the
senses are real: correct values at known configurations, correct
motion under known movements (sectors rotate, bearings track turns,
distances shrink on approach). Only then do behavior bars mean
anything — a behavior bar over an unproven sense measures nothing.

## Toward automation

Mechanizable today: given a step-1 inventory (a small YAML of facts,
actions, timings), drafting the channel table, SensorSpec/ActuatorSpec
lists, the contract table, and the D1 reading skeleton is template
work — the skill does it. Judgment still human: naming the loops
(step 2) and choosing the minimal sense for a gap (step 4). The next
tool rung: a world-probe harness that connects to the environment,
executes each action, diffs the world's own state stream, and drafts
the step-1 inventory and step-3 audit automatically — the measured
timings (wall vs tick) fall out of the probe for free.
