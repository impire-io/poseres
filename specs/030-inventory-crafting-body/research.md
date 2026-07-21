# Research: The Builder's Body (feature 030)

Decisions with rationale and alternatives. Evidence classes:
**[measured]** = read/verified in the repo this session,
**[mechanism-argument]** = reasoned, attackable by reasoning.

## D1. Inventory is a sensor, not a memory system

**Decision**: the bridge reads the bot's inventory every tick and emits
it as a fixed-width channel; the brain re-senses, never stores.

**Rationale**: the world (Minecraft server / fake `_World`) already
holds this state authoritatively and forever — the exact situation the
sensing-over-remembering principle covers. The two attempts to bolt
remembered state onto the brain both failed their pre-registered gates
**[measured — arcs 018/019, episodes 0032/0033]**; the two quantities
the body already senses this way (health, food) are the working
precedent.

**Alternatives considered**: an in-brain inventory estimator (rejected:
invents a memory mechanism to approximate state the world serves
exactly); raw 36-slot × item-id channels (rejected: obs explosion far
past the validated envelope, unlearnable alignment).

## D2. Encoding: four material classes + a held bit, width 5

**Decision**: `[blocks, logs, planks, sticks] as min(count,64)/64` +
`held_is_placeable`. Slice [14:19]; obs_dim 19.

**Rationale**: classes are **act-aligned** — each is producible or
consumable by an action the body has (dig → blocks/logs; craft →
planks/sticks; place ← blocks/planks), so every channel can carry
consequence signal. Same coarseness philosophy as the three-bit blocks
read (027 R3). 64 = one stack — the natural saturation.
**[mechanism-argument]**

**Alternatives**: per-species channels (rejected: cardinality without
new learnable structure); unbounded counts (rejected: unnormalized
channels break the [−1,1] posture of every other channel).

## D3. Placement becomes materially honest — a parity fix, not a new rule

**Decision**: `place_ahead` consumes blocks-then-planks and no-ops on
empty, in both bridges; the fake gains wood columns so the full chain
exists in the gate world.

**Rationale**: the live bridge **already** refuses to place with
nothing held/equippable (bridge.js:172-175 **[measured]**); the fake
mints matter (fake.py:91-95 **[measured]**). The gate was proving a
more permissive world than the live one — amending the fake to match
is the honest direction. Consequence accepted openly: 027's
byte-identity tests re-baseline under the amended semantics (the fake
is deterministic; the tests recompute, no goldens break).

**Alternatives**: leave the fake permissive (rejected: gate
over-promises); make the live bridge permissive via creative-mode gifts
(rejected: survival material flow is the learnable structure the
feature exists to expose).

## D4. Crafting: two pocket recipes, name-transform species mapping

**Decision**: `craft_planks` (1 log → 4 planks), `craft_sticks`
(2 planks → 4 sticks) as presets on the existing control actuator;
live side resolves species by `X_log → X_planks` name transform, first
species in inventory wins, `bot.recipesFor` + `bot.craft` bounded by
the tick budget like dig/place.

**Rationale**: both are 2×2 pocket recipes — no crafting table, no new
world furniture; together with dig and place they close the first real
material chain. One actuator keeps routing/labels trivial (labels
auto-derive for the 029 dashboard). Failures are world facts (the 027
command philosophy) — insufficient input no-ops.
**[mechanism-argument]**

**Alternatives**: crafting table + tools (rejected for v1: adds
placement furniture and a much deeper chain before any evidence the
brain chains at all — named future step); a separate `craft` actuator
(rejected: no routing benefit, one more contract concept).

## D5. Compatibility: no protocol bump, no brain edits

**Decision**: the bridge always serves the `inventory` channel; bodies
that don't declare it ignore it. pra-mc/1 stays.

**Rationale**: `MinecraftTransport` validates only that every
*declared* sensor topic is present in the tick payload
(transport.py:156 **[measured]**) — extra channels are invisible to a
14/8 body. `hello`'s channel table is informative, not exhaustive-
matched **[measured — transport checks emptiness/shape only]**. The
legacy body therefore runs against the new bridges unchanged, which is
what makes the reversal condition executable at zero notice.

## D6. The pilot: pre-registered, paired, published

**Decision** (bars fixed in spec FR-008 before any implementation):
8 paired seeds, engine over FakeBridge, short budget (the
`test_minecraft_fake_run.py` harness shape); arms `crafting=True`
(19/10) vs `crafting=False` (14/8), same seeds.
(a) 19/10 improvement > 0 in ≥ 6/8 — bar;
(b) craft actions taken and inventory channels move in 8/8 — bar;
(c) paired improvement comparison — context row, published, no bar
(the cost is the owner's accepted risk; the number still goes on the
record, camping-worlds precedent **[measured — episode 0031 pattern]**).
Experiments run in the session scratchpad; conclusions land in the
journey episode (constitution III).
