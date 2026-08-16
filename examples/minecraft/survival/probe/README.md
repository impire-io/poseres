# Native-survival probe kit (bar N1)

The declared world plus the instrument that reads it. No harness meter
anywhere: no drain constant, no pay constant, no taper, no stipend, no
steward — the world's own food/health channels under the world's own
clock (20 TPS; no tick-rate call is made).

## The exact sequence

```sh
cd hq/01-RESEARCH/native-survival/probe
docker compose up -d                       # first boot generates the map
# wait until rcon answers:
docker exec n1-minecraft rcon-cli list
../../../../.venv/bin/python provision.py  # gamerules + melon patches (one-time)
SURVIVAL=1 MC_PORT=25602 BRIDGE_PORT=25590 BOT_NAME=pra \
  node ../../../../examples/minecraft/bridge/bridge.js > bridge.log 2>&1 &
../../../../.venv/bin/python n1_probe.py   # ~20-40 min to the floor
```

`n1-rows.jsonl` carries every tick (food, health, pos, pocket, held,
the live edible flag); `n1-summary.json` the published reading. The
world data stays in `./data/` (gitignored, like the C1 world's).
