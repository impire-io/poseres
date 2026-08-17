# Lean-worlds rig

The 0109 rig (contested-worlds, restored from its trail at 7af05d6)
on its own world (`lw1-minecraft`, port 25604) with a parametric lean
world: `lean.py` builds a declared config at every birth (one patch,
counted melons, counted stems; far sites erased) and carries the
meter instruments (steady-state below-12 on segments 2–3, eats,
starvation loss). `peer.js` and `peers_reading.py` ride along
unchanged for L1/L2.

```sh
cd hq/01-RESEARCH/lean-worlds/rig
docker compose up -d && docker exec lw1-minecraft rcon-cli list
../../../../.venv/bin/python provision.py     # gamerules once

../../../../.venv/bin/python lean.py solo C2   # the walk, downward
../../../../.venv/bin/python lean.py solo C1
../../../../.venv/bin/python lean.py solo C0   # ...freeze at the last L0 pass
../../../../.venv/bin/python lean.py hostile   # L1, reads FROZEN.json
../../../../.venv/bin/python lean.py verdict
```

Status rows in `<config>-<arm>-status.jsonl`; peer acts in
`*-peer.log` (archived as `*-acts.jsonl` when an arm becomes record);
world data in `./data/` (gitignored).
