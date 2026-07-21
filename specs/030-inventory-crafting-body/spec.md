# Feature Specification: The Builder's Body — Inventory Sense and Crafting for C1

**Feature Branch**: `030-inventory-crafting-body`
**Created**: 2026-07-21
**Status**: Draft
**Input**: User description: "Inventory sense and crafting for the C1 Minecraft body: coarse fixed-width inventory channels (world-held state sensed per tick, no memory machinery), curated craft preset actions made learnable by the inventory sense, contract amendment + bridge + validated resize path"

## Overview

The C1 body can already change its world — dig and place — but it cannot
sense what it carries, and it cannot transform materials. That caps the
learnable structure at a two-step chain (dig fills an unseen pocket, place
spends it). This feature grows the body to a **builder's body**: a coarse,
fixed-width **inventory sense** (the world holds the state; the body reads
it every tick — a sensor, not a memory system, per the standing
sensing-over-remembering principle from the place-memory and scout arcs),
and two **curated craft actions** (logs → planks, planks → sticks) whose
consequences land exactly in that new sense, making them learnable the
same way dig/place are.

It also closes an honesty gap found while specifying: the in-repo fake
bridge lets `place_ahead` create blocks from nothing, while the live
bridge already requires held material. The amended contract makes
placement **materially honest in both bridges**: place consumes from the
inventory, and the fake gains wood sources so the full chain
(dig log → craft planks → craft sticks → place planks) exists in the
world that carries the quality gate.

**The owner's decision, recorded (2026-07-21):** this ships *before* the
multi-week C1 run — the earlier posture (gate on the 14/8 body's
`place_ahead` evidence) is overridden so the long run happens in line
with the project's ambitions, with the exploration-cost risk of a larger
body (obs 14→19, actions 8→10) accepted knowingly. The legacy 14/8 body
stays constructible behind one anatomy flag, which is what makes the
reversal condition executable.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - The brain senses what it carries (Priority: P1)

The bot digs a block and, on the very next tick, its inventory channels
move: the brain *sees* its pocket fill. The observer watching the Brain
tab sees a new named `inventory` group appear — with zero dashboard
changes, because the body declares itself (feature 029).

**Why this priority**: the sense is the prerequisite that makes every
other action in this feature learnable; crafting without it is noise.

**Independent Test**: in the fake world, dig a stone column and assert
the placeable-count channel rises on the next tick; dig a wood column
and assert the log channel rises; channels are fixed-width, in [0, 1],
and identical in meaning across fake and live bridges (contract table).

**Acceptance Scenarios**:

1. **Given** the fake world with the bot facing a stone column, **When**
   it digs, **Then** `inventory[0]` (placeable blocks) rises by exactly
   one unit of the declared normalization on the next tick.
2. **Given** a fresh boot, **When** the anatomy is constructed, **Then**
   obs_dim is 19 with the `inventory` group at slice [14:19], and the
   Brain tab's metadata carries it without any dashboard edit.
3. **Given** the legacy flag, **When** the 14/8 anatomy is constructed,
   **Then** it is exactly the feature-027 body (the reversal path).

---

### User Story 2 - Crafting, learnable because it is visible (Priority: P1)

The bot executes `craft_planks` holding a log: the log count falls, the
planks count jumps — a consequence in its own senses. With no log, the
action no-ops (a world fact, like digging bedrock). Same for
`craft_sticks` from planks.

**Why this priority**: crafting is the capability the owner asked for;
it and the sense land together or the actions are unlearnable.

**Independent Test**: scripted command sequences against the fake bridge
assert the exact material arithmetic (1 log → 4 planks; 2 planks → 4
sticks; insufficient input → byte-identical no-op); the live bridge
accepts both commands and reports ok under the same protocol.

**Acceptance Scenarios**:

1. **Given** ≥1 log in inventory, **When** `craft_planks` executes,
   **Then** logs −1, planks +4, on the next tick's channels.
2. **Given** zero logs, **When** `craft_planks` executes, **Then**
   nothing changes — no error, no protocol noise, one tick consumed.
3. **Given** the full chain in the fake world (a diggable wood column
   within reach), **When** dig → craft_planks → craft_sticks runs
   scripted, **Then** every intermediate is visible in the channels.

---

### User Story 3 - Placement becomes materially honest (Priority: P2)

`place_ahead` now consumes a placeable item (mined blocks first, then
planks) and no-ops with an empty pocket — in **both** bridges. The fake
world stops minting matter, matching the live bridge's existing
semantics, so what the gate proves is what the live world does.

**Why this priority**: it is the honesty fix the spec work uncovered;
without it the fake gate over-promises what the live body can do.

**Independent Test**: fake-bridge place with empty inventory is a no-op;
after digging one block, place succeeds exactly once; the 027
byte-identity and exact-resume suites hold under the amended semantics
(inventory travels in the state seam).

**Acceptance Scenarios**:

1. **Given** an empty inventory, **When** `place_ahead` executes,
   **Then** the world is unchanged (fake and live agree).
2. **Given** a snapshot mid-chain (logs and planks in pocket), **When**
   the run resumes in fake mode, **Then** the byte-identity class-1
   guarantee holds — inventory included.

---

### Edge Cases

- **Counts beyond the normalization cap**: channels clip (min(count, 64)/64)
  — a full pocket reads 1.0 and stays 1.0; the contract states it.
- **Unknown items** (live): anything outside the four declared classes is
  simply not counted — coarse by design, like the three-bit blocks read.
- **Wood species** (live): all `*_log` count as logs, all `*_planks` as
  planks; crafting maps species (oak_log → oak_planks) via name
  transform, first species found wins.
- **Craft timeout** (live): `bot.craft` is bounded by the tick budget
  like dig/place — an abandoned craft is a world fact.
- **Old snapshots**: a 14-dim C1 snapshot does not resume into a 19-dim
  config — the existing config-in-force check fails loudly; stated (the
  operator has not started the long run).
- **The dashboard**: needs zero changes — this feature is the first
  consumer of 029's metadata-driven promise, and the acceptance test
  asserts it.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The channel contract MUST gain an `inventory` channel of
  width 5: normalized counts of placeable blocks, logs, planks, sticks
  (each min(count, 64)/64) and a held-item-placeable bit — identical
  meaning in both bridges; the amended table lives in the feature-027
  contract with the amendment noted.
- **FR-002**: The command set MUST gain `craft_planks` and
  `craft_sticks` presets (actions 8 → 10) with the exact arithmetic:
  1 log → 4 planks; 2 planks → 4 sticks; insufficient input → no-op.
- **FR-003**: `place_ahead` MUST consume one placeable item (mined
  blocks first, then planks) and MUST no-op on an empty pocket, in both
  bridges; the fake world MUST contain diggable wood sources so the full
  material chain exists in the gate.
- **FR-004**: The C1 anatomy MUST default to the 19/10 builder's body;
  the 14/8 feature-027 body MUST stay constructible via one flag
  (`c1_anatomy(crafting=False)`) — the reversal path.
- **FR-005**: Inventory MUST travel in the fake state seam: fake-mode
  snapshot/resume stays class-1 byte-identical, mid-chain included.
- **FR-006**: The bridge MUST keep serving bodies that do not declare
  the inventory channel (the transport reads declared topics only —
  measured); no protocol version bump.
- **FR-007**: The brain-side integration MUST be zero-edit: anatomy
  declaration + bridges only; no engine, tap, or dashboard changes
  (the 029 metadata path carries the new group and labels).
- **FR-008**: A **pre-registered learnability pilot** MUST run before
  the feature is called done and its numbers reported honestly
  (constitution II): 8 paired seeds, fake world, short budget —
  (a) improvement > 0 in ≥ 6/8 seeds at 19/10; (b) craft actions taken
  and inventory channels move in every seed; (c) the 19/10 vs 14/8
  paired improvement comparison reported as a context row (no bar — the
  cost is accepted; the numbers must still be on the record).

### Key Entities

- **Inventory channel**: width-5 fixed slice [14:19]; the world's pocket
  read per tick.
- **Material classes**: placeable-blocks (dirt/stone family), logs,
  planks, sticks — the four the body's actions can produce or consume.
- **Craft presets**: two new single-key commands on the existing control
  actuator; labels auto-derive for the dashboard.
- **The legacy body**: `crafting=False` → exactly feature 027's 14/8.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Every material action's consequence is visible in the
  channels on the next tick, proven by scripted fake-bridge sequences
  covering the full chain (dig log → planks → sticks → place).
- **SC-002**: The fake and live bridges agree on the amended contract:
  the fake gate's command/channel semantics match what the live bridge
  executes (live smoke: both craft commands accepted and material
  arithmetic observed against a real server).
- **SC-003**: Fake-mode byte-identity and exact-resume suites pass with
  inventory in the state seam; the reference byte-frozen suite is
  untouched (zero core edits).
- **SC-004**: The Brain tab shows the `inventory` group and both craft
  labels with **zero dashboard-code changes**.
- **SC-005**: The pilot's pre-registered bars (FR-008 a/b) PASS and the
  paired 19/10-vs-14/8 numbers are published in the journey episode —
  including if they are unflattering.

## Assumptions

- **Curated, not general**: two recipes, four material classes. The 2×2
  pocket-craft recipes need no crafting table; tables/tools are a named
  future step, not scope creep here.
- **Peaceful posture unchanged**: no eating action (food does not drain
  at peaceful); vitals stay sensed-only.
- **Coarse classes are the design, not a shortcut**: same philosophy as
  the three-bit blocks read — act-aligned, learnable, fixed-width.
- **Reversal condition (owner-accepted risk)**: if the multi-week C1 run
  shows the 10-action body failing to engage its material actions —
  craft/place effectively unused and prediction improvement materially
  below the 14/8 pilot arm — the run falls back to
  `c1_anatomy(crafting=False)` (one flag, snapshots incompatible across
  the switch, stated) and the body question returns to research.
