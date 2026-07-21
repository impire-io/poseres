# Implementation Plan: The Property Body

**Branch**: `033-property-body` | **Date**: 2026-07-21 | **Spec**: [spec.md](spec.md)

## Summary

Fourth body revision, third contract amendment. Channel set:
pose(5) vitals(2) env(4) blocks(3, unchanged) **mining(1)** **pocket(4)**
**hand(6)** **grid(7)** = obs 32; the same 12 actions with `hold_next`
cycling distinct pocket kinds. Everything classifier-free: properties
(the game's own facts) + sha256 appearance signatures, identical across
bridges. Dig becomes start/continue/cancel with sensed progress. Labels
ride the existing 029 metadata; ground truth rides the existing 015
world-view channel. Zero core edits (fifth feature running).

## Technical context (deltas from 031/032)

- **specs.py**: `SensorSpec` gains optional `labels`; `TopicSensor`
  exposes them; `Body.anatomy_meta` includes `labels` per group.
- **anatomy.py**: v4 declaration with labels; `crafting=False` still
  the exact 027 body (widths unchanged there — the new channels are new
  names, which is why `blocks` stays 3 wide and progress is its own
  `mining` channel: a legacy body declaring blocks(3) must keep
  matching the bridge's table).
- **fake.py**: item names become vanilla-ish ("cobblestone",
  "oak_log", "oak_planks", "stick") so signatures are real; inventory
  is name→count; dig durations per material (3 ticks mineral, 12
  wood); `digging` (target, progress) in world state + state seam;
  view dict in the tick response for parity.
- **transport.py**: optional `on_view` callback; tick forwards the
  response's `view` when present.
- **run_c1.py**: wires `on_view` to `tap.world_view("minecraft")` when
  telemetry is on.
- **bridge.js**: property/signature sampling from the real inventory;
  held-kind cycling (sorted distinct names); virtual grid stages kinds;
  offers by the world-rule table (species-preserving name transform);
  dig via un-awaited `bot.dig` + `bot.digTime` progress + 10 s
  no-progress cap; `view` in every tick.
- **dash/page.html**: one new view renderer (kind "minecraft" → Ground
  Truth panel); labels light up existing charts automatically.
- **Contract**: third amendment in the 027 file (tables with labels,
  signature spec, dig semantics, world-rule recipes, view field, legacy
  notes).

## Constitution check

I PASS (no core edits; reference untouched). II PASS (pilot bars fixed
in spec FR-006 pre-implementation; the material-cliff context stated
before measurement). III applied (the live run's blind-pocket bug is
the diagnosis driving D1). IV recorded (three owner arguments, argued
adversarially in-conversation; reversal inherited from 031 with the
legacy-place note). V PASS (fake keeps determinism; durations are tick
arithmetic). VI applies.

## Verification

Gate (fake-carried, all suites amended) → pilot re-baseline (8 paired
seeds, scratchpad) → deploy to beno4 → live smoke (signatures vs real
inventory; setblock a log ahead, break it by held digs) → stop v3 run,
wipe world + snapshots, RUN_ID=c1b, amend C1-RUN-PLAN, relaunch, confirm
stepping + labels + ground truth on the dashboard.
