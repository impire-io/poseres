# Contract amendment (feature 030): the builder's body delta to pra-mc/1

Applied to the normative table in
`specs/027-minecraft-body/contracts/minecraft-adapter.md` (which states
that changing it is a spec change — this is that change). The protocol
version stays `pra-mc/1`: the channel table grows; commands grow; no
existing field changes shape. A body that does not declare the new
channel is unaffected (the transport reads declared topics only).

## Channel table: one new row

| channel | width | values (all float64) |
|---|---|---|
| `inventory` | 5 | min(blocks,64)/64; min(logs,64)/64; min(planks,64)/64; min(sticks,64)/64; held-item placeable ? 1 : 0 |

Classes (both bridges, identical meaning): **blocks** = mined placeable
blocks (dirt/stone families); **logs** = any `*_log`; **planks** = any
`*_planks`; **sticks** = `stick`. Items outside the four classes are
not counted (coarse by design). `held-item placeable` = the item that a
`place_ahead` would consume exists (blocks or planks).

C1 anatomy with the builder's body: obs_dim **19**, `inventory` at
slice [14:19]. The 027 body (obs_dim 14) remains valid and ignores the
channel.

## Commands: two new presets, one amended

`{"craft_planks": 1}` — 1 log → 4 planks (species by name transform,
first species in inventory); insufficient input → no-op, one tick
consumed.
`{"craft_sticks": 1}` — 2 planks → 4 sticks; insufficient input →
no-op.
`{"place_ahead": 1}` — **amended**: consumes one placeable item, mined
blocks first then planks; empty pocket → no-op. (This is what the live
bridge already did; the fake now agrees — the amendment records
existing live semantics as normative.)

n_actions with the builder's body: **10**. Craft actions are bounded by
the tick budget like dig/place; an abandoned craft is a world fact.

## Fake-world additions (the gate must contain the chain)

The fake sketch gains wood columns (feet-level solid, class log when
dug) so `dig → craft_planks → craft_sticks → place` is fully
exercisable in-repo; digging a stone/wall column yields one `blocks`;
digging a wood column yields one `logs`; place consumes per the
amendment. `state`/`load_state` carry the inventory dict — class-1
resume includes it.
