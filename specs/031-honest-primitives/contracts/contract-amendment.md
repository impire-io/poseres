# Contract amendment (feature 031): honest primitives delta to pra-mc/1

Applied to `specs/027-minecraft-body/contracts/minecraft-adapter.md`
(the second amendment; the first was feature 030). Protocol stays
`pra-mc/1`; the channel table grows two rows; the command set swaps the
two macro crafts for four grid primitives; placement becomes held-based.

## Channels: two new rows, one redefinition

| channel | width | values (all float64) |
|---|---|---|
| `hand` | 4 | held class one-hot: blocks; logs; planks; sticks (all 0 = holding nothing) — *feature 031* |
| `grid` | 5 | staged/4; staged logs/4; staged planks/4; result-is-planks ? 1 : 0; result-is-sticks ? 1 : 0 — *feature 031* |

`inventory[4]` is redefined: *the held class is placeable* (blocks or
planks held) — selection is the brain's, so the bit reports the hand,
not an auto-pick. Builder anatomy: obs_dim **28** — inventory [14:19],
hand [19:23], grid [23:28].

## Commands

Removed: `craft_planks`, `craft_sticks` (the 030 macros — skills, not
primitives). Added:

`{"hold_next": 1}` — cycle held class none → blocks → logs → planks →
sticks → none, regardless of counts (holding an empty class is a valid
sensed state).
`{"grid_put": 1}` — move one item of the held class from the pocket
into the staging grid, column-first (top-left, bottom-left, top-right,
bottom-right); no-op if nothing suitable held, none in pocket, or grid
full.
`{"grid_take": 1}` — return all staged items to the pocket.
`{"take_result": 1}` — collect the grid's current offer, consuming the
recipe inputs; no-op if no offer.

`{"place_ahead": 1}` — **amended**: places one item of the *held*
class if placeable (blocks, planks); no-op otherwise. (030's
blocks-then-planks auto-pick is removed — it was a mini-macro.)

n_actions **12**; ids 0–7 are the 027 set unchanged; 8 `hold_next`,
9 `grid_put`, 10 `grid_take`, 11 `take_result`.

## The grid's result rules (both bridges, vanilla's own)

- exactly **one** log staged, nothing else → offer **planks**; take
  consumes it → +4 planks. (Vanilla-exact: a second staged log makes
  the offer *disappear* — grid contents must match the recipe exactly,
  which is itself a learnable consequence.)
- exactly **two** planks staged, column-adjacent (column-first fill
  guarantees the first two are), nothing else → offer **sticks**; take
  consumes both → +4 sticks.
- anything else (mixed classes, single plank, blocks, sticks, three+
  items) → no offer; `take_result` no-ops.

## Body furniture, declared

The staging grid is the body's, not the server's: live, it is a
virtual structure whose material flows in and out of the **real**
inventory are real and whose `take_result` executes the **real** craft
(then re-syncs from the real inventory; on any mismatch the craft
no-ops and the grid re-syncs — the world is the authority). Fake, the
grid is world state and travels in the class-1 seam (`held`, `grid` in
`state`/`load_state`). Same convention class as "ahead is the column
nearest yaw"; stated here so it is never discovered.
