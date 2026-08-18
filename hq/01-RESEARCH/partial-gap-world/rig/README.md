# Partial-gap-world rig

The lean-worlds rig (0110, restored from its trail at f05827f) on its
own world (`pgw1-minecraft`, port 25605) with ONE walked variable:
the renewal rate. The larder is frozen at C-1's total-war shape (one
patch, 2 pre-grown melons) plus 2 age-7 stems whose fruit slots the
pre-grown melons block — regrowth starts only when a melon is
consumed. `pgap.py` sets the rung's `random_tick_speed` before every
birth and carries the 0110 meter instruments unchanged (steady-state
below-12 on segments 2–3, eats, starvation). `peer.js` rides along
unchanged (hostile mode only at this topic).

```sh
cd hq/01-RESEARCH/partial-gap-world/rig
docker compose up -d && docker exec pgw1-minecraft rcon-cli list
../../../../.venv/bin/python provision.py       # gamerules once

../../../../.venv/bin/python pgap.py renewal T3  # I0: measured melons/life at each speed
../../../../.venv/bin/python pgap.py solo T12    # the walk, downward: P0 screen
../../../../.venv/bin/python pgap.py hostile T12 # the rung's hostile-86 reading (P1)
# ...on a band hit: write FROZEN.json {"rung": ...} + journal, then
../../../../.venv/bin/python pgap.py hostile2 <rung>   # P2 replicate
../../../../.venv/bin/python pgap.py verdict
```

Freezing is a hand act, journaled: `FROZEN.json` names the rung whose
hostile reading landed in 0.10–0.90; `hostile2` refuses any other.
Status rows in `<rung>-<arm>-status.jsonl`; I0 rows in
`renewal-<rung>.jsonl`; peer acts in `*-peer.log` (archived as
`*-acts.jsonl` when an arm becomes record); world data in `./data/`
(gitignored).
