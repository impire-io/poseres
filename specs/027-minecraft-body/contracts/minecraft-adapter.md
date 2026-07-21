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
| `state` | — | `world` (opaque JSON dict; FakeBridge: full world state; live bridge: `{"live": true, "tick": k}`) |
| `load_state` | `world` | — (live bridge accepts a `live` marker and restores nothing but the tick counter — stated class-4 semantics) |
| `bye` | — | — (connection closes after the response) |

Version mismatch at `hello` is loud on both sides. The bridge serves
exactly one client at a time; a second connection is refused.

## Channel contract (the meaning of every observation dimension)

Both bridges implement this table identically; changing it changes the
anatomy (Doc 02 §3.3) and is a spec change.

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
∈ [−1, 1]. Identical in both bridges by construction; stable,
distinguishing, semantics-free. Categories are the brain's to form.
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

Material rules (feature 033, both bridges): **digging is a held
intention** — `dig_ahead` starts breaking the block ahead (or continues
if it is already the target); ANY other command, idle included,
releases the intention and resets the cracks (vanilla: letting go).
`mining` senses the progress fraction; at 1.0 the block breaks and its
item joins the pocket (fake: immediately; live: by the game's own drop
physics — the pocket channel reads the truth either way). There is no
behavior-shaping timeout: the world's own break times bound everything
(fake, vanilla-proportioned at the 250 ms posture: mineral 3 ticks,
wood 12); live, a 10 s no-progress safety cap releases an unbreakable
target. `hold_next` cycles nothing → the pocket's distinct item kinds
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
Fake, the grid is world state in the class-1 seam.

**The ground-truth view** (feature 033): every tick response carries a
compact `view` — real position, held item name, real inventory names
and counts, dig progress — forwarded to the feature-015 world-view
channel for the *human* dashboard. The brain never senses it.

**Legacy note**: the feature-027 body (14/8) on this bridge senses its
four channels unchanged; with no way to hold a kind, its `place_ahead`
is inert — the reversal path is watch/move/dig only (stated, spec 033).
