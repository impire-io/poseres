# The larder-loop rig (topic the-arena-revival; built by the-long-carry, episode 0120)

The arena world plus its instruments. Design: [`../arena.md`](../arena.md).
World data stays in `./data/` (gitignored, like the probe world's).

## Bring-up

```sh
cd hq/01-RESEARCH/the-arena-revival/rig
docker compose up -d                      # first boot generates the map
docker exec lc-minecraft rcon-cli list    # wait until rcon answers
../../../../.venv/bin/python arena_provision.py   # one-time
SURVIVAL=1 MC_PORT=25603 BRIDGE_PORT=25591 BOT_NAME=pra SPAWN_ANCHOR=0,0 \
  node ../../../../examples/minecraft/bridge/bridge.js > bridge.log 2>&1 &
../../../../.venv/bin/python mechanism_check.py   # instrument before behavior
```

`mechanism_check.py` is the scripted walker (never the kernel): it
verifies the world's own contract — counting, gate, reset, indicator,
mouth, one-way drop — and records the gait calibration in
`mechanism-report.json`. Every H0 number in `../arena.md` is sized
from that report, not from estimates.

## Revival (2026-09-27)

Scripts restored verbatim from commit `a4b4386` (this rig) and
`4171779` (`compose.py`, `opaque_runner.py`, `snap_test.py` — the
0119 composed scaffolding). 0120's readings stay in history; the
revival re-measures (README bar R0). The pre-pilot adaptations —
shipped ladder dials in place of the prototype, path re-pointing,
the `seq` import — are listed in `../JOURNEY.md` and recorded there
as they land.
