---
name: "anatomy-mapping"
description: "Derive an anatomy (sensors, actuators, channel contract) for a target world using the Doc 0012 mapping process — world-facts inventory, loop closure, pairability audit, senses from gaps, instrument bars."
argument-hint: "<world> — the target environment (e.g. 'minecraft survival', 'a ROS2 rover', 'a trading arena'), plus any goals the life must live"
compatibility: "Requires hq/02-DESIGN/0012-anatomy-from-world.md"
metadata:
  author: "pra-hq"
user-invocable: true
disable-model-invocation: false
---

## User Input

```text
$ARGUMENTS
```

Parse `$ARGUMENTS` as the target world and, if given, the goal loops
the life must live. If no goals are named, ask for them — step 2
cannot be guessed.

## Steps

Read `hq/02-DESIGN/0012-anatomy-from-world.md` first; it is the
authority and carries each rule's measured provenance. Then produce
one artifact per step, in order, as a single mapping document
(`anatomy-map-<world>.md` in the caller's chosen location — a research
topic folder if this is for a gate):

1. **World-facts inventory** — a table of the world's OWN facts:
   state, events, accepted actions, and each action's native duration
   AND where that time is computed (client wall clock vs world tick —
   measure, don't assume). No invented facts, no names-as-classes.

2. **Loop table** — for each goal, the full chain act → consequence →
   … → pay, every arrow in world facts.

3. **Pairability audit** — for every arrow: does the sensed
   consequence land within one control tick? Mark each failure with
   its shape (delayed pay / long act / split sample) and its Doc 0012
   fix (intermediary sense / held intention with sensed progress /
   skew-tolerant detector).

4. **Sense drafts** — for each gap, a SensorSpec in the house grammar:
   properties + appearance signatures, egocentric geometry for
   anything spatial (sign conventions marked "measure at D1"), meters
   normalized [0, 1], every aggregate's saturation cap declared.

5. **Actuator drafts** — one command grammar: instantaneous vs held
   intentions (start/continue/release-by-any/safety cap); enumerate
   all body-side virtual state and how a classroom resets it.

6. **Scale + drive-band check** — the new obs_dim against the config
   scale rules; for each sense that must drive behavior, the itch
   magnitude it can feed vs the drive band (Doc 0011: 0.06–0.15), and
   what teaching must weigh for it to clear.

7. **Contract + instrument plan** — the channel table amendment
   (opt-in mode, width-checked handshake), what the fake/sketch
   carries (SHAPE only — behavioral evidence is live-world only, the
   GENESIS rule), and a D1-style "the senses are real" live reading:
   known configurations, known movements, expected values.

8. **Teaching plan** — lessons that exercise every new sense, meters
   witnessed moving, classroom hygiene (clean pocket, normalized
   virtual state, world admin between readings only).

Do NOT write code in this skill's pass — the output is the mapping
document. Building the bridges/specs/tests from it is its own task
(and for a research gate, registration of bars comes first).
