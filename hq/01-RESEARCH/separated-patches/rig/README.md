# Separated-patches rig

The 0111 rig (restored from its trail at d940e7e) on its own world
(`pgw2-minecraft`, port 25606, bridge 25594) with ONE walked
variable: separation. Two patches — A beside the spawn stand, B due
east at distance D — each holding C-1's total-war larder (2
pre-grown melons, no stems, no renewal). `sep.py` carries the 0110
meter instruments unchanged; `peer.js` rides along (hostile mode).

```sh
cd hq/01-RESEARCH/separated-patches/rig
docker compose up -d && docker exec pgw2-minecraft rcon-cli list
../../../../.venv/bin/python provision.py        # gamerules once

../../../../.venv/bin/python walk.py D12 D24 D48 # the declared walk
# on a band hit: write FROZEN.json {"rung": ...} + journal, then
../../../../.venv/bin/python sep.py hostile2 <rung>   # S2 replicate
../../../../.venv/bin/python sep.py verdict
```

Freezing is a hand act, journaled. Status rows in
`<rung>-<arm>-status.jsonl`; peer acts in `*-peer.log` (archived as
`*-acts.jsonl` when an arm becomes record); world data in `./data/`
(gitignored).
