# Feature 027 — wire protocol and channel contract (normative)

## Wire protocol `pra-mc/1`

Newline-delimited JSON over TCP; one request line → one response line;
the Python side never pipelines. Every response carries `"ok": true` or
`"ok": false, "error": "<message>"` (an error response raises
AnatomyError verbatim on the client).

| op | request fields | response fields |
|---|---|---|
| `hello` | `version` | `version`, `channels` (name → width), `spawn` (true once the bot is in the world) |
| `tick` | `commands` (list of preset mappings, may be empty), `tick_ms` | `tick` (0-based index), `channels` (name → list of floats, every declared channel every tick) |
| `state` | — | `world` (opaque JSON dict; the live bridge returns `{"live": true, "tick": k}` — class-4 semantics) |
| `load_state` | `world` | — (live bridge accepts a `live` marker and restores nothing but the tick counter — stated class-4 semantics) |
| `bye` | — | — (connection closes after the response) |

Version mismatch at `hello` is loud on both sides. The bridge serves
exactly one client at a time; a second connection is refused.

## Channel contract (the meaning of every observation dimension)

The bridge implements this table; changing it changes the anatomy
(Doc 02 §3.3) and is a spec change. There is no fake side of this
seam (owner's rule, 2026-08-13): the table is proven live by
`examples/minecraft/contract_check.py`.

| channel | width | values (all float64) |
|---|---|---|
| `pose` | 5 | ((x−x₀)/64, (z−z₀)/64, (y−64)/64) each clipped to [−1, 1] with (x₀, z₀) the spawn column; sin(yaw); cos(yaw) |
| `vitals` | 2 | health/20, food/20 — both in [0, 1] |
| `env` | 4 | block-light at feet /15; sin(ϑ); cos(ϑ) with ϑ = 2π·(time_of_day/24000); raining ? 1 : 0 |
| `blocks` | 3 | solid at feet-level one block ahead ? 1 : 0; solid at eye-level one block ahead ? 1 : 0; air below the block ahead ? 1 : 0 |
| `mining` | 1 | dig progress of the held intention, 0..1 (the cracks, sensed) — *feature 033* |
| `pocket` | 4 | pocket aggregates: min(total,64)/64; min(kinds,9)/9; min(placeable,64)/64; min(other,64)/64 — *feature 033* |
| `hand` | 6 | held kind: present ? 1 : 0; placeable ? 1 : 0; min(count,64)/64; sig0; sig1; sig2 — *feature 033* |
| `grid` | 7 | staged/4; offer ? 1 : 0; offer placeable ? 1 : 0; min(offer count,64)/64; offer sig0..2 — *feature 033* |

"Ahead" is the unit grid step nearest the bot's yaw. obs_dim = 14 for
the feature-027 body; **32 with the property body (feature 033)**:
`mining` [14], `pocket` [15:19], `hand` [19:25], `grid` [25:32]. The
channel labels above ARE the contract and travel in `anatomy_meta`.

**No material classes exist anywhere** (feature 033, the owner's
argument): identity reaches the brain only as *properties* — placeable
= the item maps to a block, the game's own fact (logs, gravel, moss
are placeable; sticks are not) — and as an *appearance signature*:
sha256 of the item name (utf-8), digest bytes 0..2, each byte/127.5 − 1
∈ [−1, 1]. Stable, distinguishing, semantics-free
(`pra.anatomy.minecraft.protocol.item_signature` is the reference). Categories are the brain's to form.
A body that does not declare a channel ignores it (the transport reads
declared topics only) — the protocol version stays `pra-mc/1`.

## Commands (preset mappings; unknown keys are a loud bridge error)

`{"forward": 1}` `{"back": 1}` `{"turn_left": 1}` `{"turn_right": 1}`
`{"jump_forward": 1}` `{"dig_ahead": 1}` `{"place_ahead": 1}` `{}` (idle)
`{"hold_next": 1}` `{"grid_put": 1}` `{"grid_take": 1}`
`{"take_result": 1}` — *feature 031* (which removed feature 030's
`craft_planks`/`craft_sticks` macros: skills, not primitives)

Movement commands hold their control for the tick's `tick_ms` and then
stop; turns are 45° exact; dig/place target the feet-level block one
step ahead (the same block `blocks[0]` reads). n_actions = 8 for the
feature-027 body; **12 with the builder's body** (ids 0–7 are the
027 set unchanged; 8 `hold_next`, 9 `grid_put`, 10 `grid_take`,
11 `take_result`).

Material rules (feature 033): **digging is a held
intention** — `dig_ahead` starts breaking the block ahead (or continues
if it is already the target); ANY other command, idle included,
releases the intention and resets the cracks (vanilla: letting go).
`mining` senses the progress fraction; at 1.0 the block breaks and its
item joins the pocket by the game's own drop physics — the pocket
channel reads the truth. There is no behavior-shaping timeout: the
world's own break times bound everything; a 10 s no-progress safety
cap releases an unbreakable target. `hold_next` cycles nothing → the pocket's distinct item kinds
sorted by name → nothing (a ran-out kind reads as nothing and resets
the cycle). `place_ahead` places one item of the **held kind** if the
game says it is placeable; `grid_put` stages one item of the held kind
(column-first, ≤4); `grid_take` returns everything; `take_result`
collects the grid's offer, consuming the staged inputs. The world's
pocket-craft rules (world mechanics, never sensed as names): exactly
one staged `*_log` and nothing else → its species' `*_planks` ×4;
exactly two same-species planks → `stick` ×4; anything else offers
nothing (vanilla-exact matching — a second log kills the offer). Unmet
requirements no-op and consume the tick — world facts, never protocol
errors.

**The staging grid is body furniture** (features 031/033, declared):
live, it is a bridge-side virtual structure whose material flows in
and out of the *real* inventory are real and whose `take_result`
executes the *real* craft, success confirmed by the world's own count
delta (the world is the authority; mismatched reservations re-sync).

**The ground-truth view** (feature 033): every tick response carries a
compact `view` — real position, held item name, real inventory names
and counts, dig progress — forwarded to the feature-015 world-view
channel for the *human* dashboard. The brain never senses it.

**Legacy note**: the feature-027 body (14/8) on this bridge senses its
four channels unchanged; with no way to hold a kind, its `place_ahead`
is inert — the reversal path is watch/move/dig only (stated, spec 033).

## Native-survival instrument (research topic native-survival, 2026-08-11)

**Instrument-grade; folds into the tables above only on promotion.**
Survival mode is opt-in on every surface — bridge `SURVIVAL=1`,
`c1_anatomy(survival=True)` — and a
mismatched stack fails loud at the existing handshake width check. The
shipped 32/12 body is byte-identical with the mode off.

- **`hand` widens to 7**: present; placeable; **edible** ? 1 : 0 — the
  game's own fact (`minecraft-data` foods); min(count,64)/64; sig0..2. obs_dim 33; every shipped offset
  before `hand` unchanged, `hand` [19:26], `grid` [26:33].
- **`use_held` is command 13 (id 12)** — apply the held item, the
  classifier-free mouth: no edibility check in the actuator; what using
  the held item does is the world's to decide, and nourishment reaches
  the brain only through `vitals`. It is a **held intention** with the
  dig's exact grammar: the first `use_held` begins it, further ones
  continue it, ANY other command (idle included) releases it. Live: one
  `activateItem()` and the server's own consume runs (~1.61 s for
  food); the safety release is 120 game ticks. An empty hand no-ops;
  unmet requirements consume the tick — world facts, never protocol
  errors.
- **The view** gains `food`, `health`, `eating` (progress 0..1) in
  survival mode — humans only, never sensed.
- **The progress channel senses the held intention, whatever it is**
  (arms amendment 1): in survival mode `mining` reports a dig's cracks
  OR a use's chew (game ticks/32) — one
  held-intention grammar, so the completion itch can hold the eat
  exactly as it holds the dig. **The chew's clock is the world's
  clock** (distal-senses reteach fix): a consume is 32 SERVER ticks,
  so progress, recycle (36 ticks — a still-held intention chains a
  fresh consume, vanilla's continuous eating), and the safety release
  (120 ticks) key on the game-tick clock and stay honest at any
  `/tick rate`. Digs remain wall-paced (client-computed break times,
  measured at c1e).
- **The distal senses** (topic distal-senses, 2026-08-13; appended
  after `grid`, obs_dim 73, every prior offset unchanged):
  - `drops` (8): the nearest ground item within 8 blocks — present;
    sin/cos of the EGOCENTRIC bearing (cross/dot against the body's
    own forward; sin positive toward the body's **turn_right** side —
    measured at D1, mineflayer's yaw frame is left-handed); min(d,
    8)/8; min(count, 8)/8; the item's appearance signature. Empty:
    all zeros.
  - `glance` (32): eight egocentric sectors, k·45° to the body's
    right of forward, one FEET-LEVEL center-ray each out to 16
    blocks: min-distance-to-solid/16 (1.0 = open) + that surface
    block's appearance signature (zeros when open). A glance, not a
    survey — one ray per sector, the sector centers rotate with yaw.
- **The flood** (topic the-flood, 2026-08-13; `FLOOD=intrusion|gain`
  env beside SURVIVAL, appended last, obs_dim 77): the deficit
  expanded nonlinearly into the observation. Dim 0 is the flood level
  f = ((d − 0.25)/0.75)² for deficit d = 1 − food/20 above θ = 0.25,
  else 0 — silent above 15/20 food, 1.0 at starvation. Dims 1–3 by
  form: **intrusion** = f × per-game-tick pseudo-noise (the item
  signature of the world clock's decimal string — deterministic,
  unpredictable-to-a-linear-head); **gain** = f-scaled
  classifier-free food cues [drops present, drops nearness, held
  edible] — the glance may NOT contribute (naming food would be a
  classifier, 033). FLOOD unset with the flood anatomy = the
  registered ablation body: same width, channel at zeros.
