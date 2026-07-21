# Data Model: The Builder's Body (feature 030)

## The anatomy (declaration is configuration)

```python
c1_anatomy(crafting=True)   # default: the builder's body
# sensors:  pose(5) vitals(2) env(4) blocks(3) inventory(5)  -> obs_dim 19
# actuator: control presets forward, back, turn_left, turn_right,
#           jump_forward, dig_ahead, place_ahead, idle,
#           craft_planks, craft_sticks                        -> n_actions 10

c1_anatomy(crafting=False)  # the exact feature-027 body: 14 / 8 (reversal path)
```

`C1_OBS_DIM`/`C1_N_ACTIONS` follow the default (19/10). The dashboard
needs nothing: the 029 metadata path derives the `inventory` group at
[14:19] and the craft labels from this declaration.

## The inventory channel (both bridges, identical)

| index | meaning | range |
|---|---|---|
| 0 | mined placeable blocks, min(n,64)/64 | [0,1] |
| 1 | logs, min(n,64)/64 | [0,1] |
| 2 | planks, min(n,64)/64 | [0,1] |
| 3 | sticks, min(n,64)/64 | [0,1] |
| 4 | a `place_ahead` has material to consume | {0,1} |

## Material arithmetic (the commands' contract)

| command | requires | effect |
|---|---|---|
| `dig_ahead` (stone/wall column) | diggable ahead | blocks +1 |
| `dig_ahead` (wood column) | diggable ahead | logs +1 |
| `craft_planks` | logs ≥ 1 | logs −1, planks +4 |
| `craft_sticks` | planks ≥ 2 | planks −2, sticks +4 |
| `place_ahead` | blocks+planks ≥ 1 | blocks −1 (else planks −1), world +1 block |
| any, unmet requirement | — | no-op, one tick consumed |

## Fake state seam (class-1 resume, feature 027 §state)

`state_dict` gains `"inventory": {"blocks": int, "logs": int,
"planks": int, "sticks": int}`; `load_state` restores it exactly.
Wood columns are a fixed frozenset in the sketch (like walls/pits);
dug wood columns travel in the existing `dug` set.

## Pilot record shape (published in the journey episode)

Per seed (8 paired): improvement (both arms), craft-action counts,
Σ|Δinventory| observed, final population. Bars: spec FR-008 (a) ≥6/8
improvement > 0 at 19/10; (b) 8/8 craft-taken with inventory movement;
(c) paired comparison = context row.
