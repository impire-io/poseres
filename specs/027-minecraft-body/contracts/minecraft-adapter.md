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
| `inventory` | 5 | min(blocks,64)/64; min(logs,64)/64; min(planks,64)/64; min(sticks,64)/64; a `place_ahead` has material to consume ? 1 : 0 — *amended by feature 030* |

"Ahead" is the unit grid step nearest the bot's yaw. obs_dim = 14 for
the feature-027 body; **19 with the builder's body (feature 030)**,
`inventory` at slice [14:19]. Material classes (both bridges,
identical): blocks = mined placeable blocks (dirt/stone families);
logs = any `*_log`; planks = any `*_planks`; sticks = `stick`; items
outside the classes are not counted. A body that does not declare the
`inventory` channel ignores it (the transport reads declared topics
only) — the protocol version stays `pra-mc/1`.

## Commands (preset mappings; unknown keys are a loud bridge error)

`{"forward": 1}` `{"back": 1}` `{"turn_left": 1}` `{"turn_right": 1}`
`{"jump_forward": 1}` `{"dig_ahead": 1}` `{"place_ahead": 1}` `{}` (idle)
`{"craft_planks": 1}` `{"craft_sticks": 1}` — *feature 030*

Movement commands hold their control for the tick's `tick_ms` and then
stop; turns are 45° exact; dig/place target the feet-level block one
step ahead (the same block `blocks[0]` reads). n_actions = 8 for the
feature-027 body; **10 with the builder's body**.

Material arithmetic (feature 030, both bridges): digging a wood column
yields one log, any other diggable column one placeable block;
`craft_planks` = 1 log → 4 planks (species by name transform, first
species in inventory); `craft_sticks` = 2 planks → 4 sticks;
`place_ahead` **consumes** one placeable item (mined blocks first, then
planks) and no-ops on an empty pocket — this records the live bridge's
existing behavior as normative (the fake previously minted matter; it
no longer does). Unmet requirements no-op and consume the tick — world
facts, never protocol errors. Craft is bounded by the tick budget like
dig/place.
