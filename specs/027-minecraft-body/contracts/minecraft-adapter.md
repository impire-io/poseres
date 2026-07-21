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
| `inventory` | 5 | min(blocks,64)/64; min(logs,64)/64; min(planks,64)/64; min(sticks,64)/64; the held class is placeable ? 1 : 0 — *amended by features 030/031* |
| `hand` | 4 | held class one-hot: blocks; logs; planks; sticks (all 0 = holding nothing) — *feature 031* |
| `grid` | 5 | staged/4; staged logs/4; staged planks/4; result-is-planks ? 1 : 0; result-is-sticks ? 1 : 0 — *feature 031* |

"Ahead" is the unit grid step nearest the bot's yaw. obs_dim = 14 for
the feature-027 body; **28 with the builder's body (features 030/031)**:
`inventory` [14:19], `hand` [19:23], `grid` [23:28]. Material classes
(both bridges, identical): blocks = mined placeable blocks (dirt/stone
families); logs = any `*_log`; planks = any `*_planks`; sticks =
`stick`; items outside the classes are not counted. A body that does
not declare a channel ignores it (the transport reads declared topics
only) — the protocol version stays `pra-mc/1`.

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

Material rules (features 030/031, both bridges): digging a wood column
yields one log, any other diggable column one placeable block.
`hold_next` cycles the held class none → blocks → logs → planks →
sticks → none regardless of counts (holding an empty class is a valid,
sensed state). `place_ahead` **consumes one item of the held class**
if placeable (blocks, planks) and no-ops otherwise — selection is the
brain's. `grid_put` moves one item of the held class into the staging
grid, column-first (top-left, bottom-left, top-right, bottom-right),
no-op when nothing suitable is held, the pocket lacks it, or the grid
is full (4). `grid_take` returns all staged items to the pocket.
`take_result` collects the grid's offer, consuming the recipe inputs.
Offers are vanilla-exact: exactly one staged log and nothing else →
planks (+4, the log consumed); exactly two planks, column-adjacent,
nothing else → sticks (+4, both consumed); anything else — mixed
classes, a second log, a lone plank — offers nothing. Unmet
requirements no-op and consume the tick — world facts, never protocol
errors.

**The staging grid is body furniture** (feature 031, declared): live,
it is a bridge-side virtual structure whose material flows in and out
of the *real* inventory are real and whose `take_result` executes the
*real* craft (then re-syncs; on any mismatch with the real inventory
the craft no-ops and the grid re-syncs — the world is the authority).
Fake, the grid is world state in the class-1 seam. Same convention
class as "ahead is the column nearest yaw".
