# Contested-worlds rig (rung 1: the invisible peer)

The N1 probe world's declared config on its own container and port
(`cw1-minecraft`, 25603) so the C1 and N1 worlds are never touched,
plus the rung-1 instruments: `rung1.py` (the two arms and the verdict)
and `peer.js` (the scripted second body, "rook").

## The exact sequence

```sh
cd hq/01-RESEARCH/contested-worlds/rig
docker compose up -d                       # first boot generates the map
docker exec cw1-minecraft rcon-cli list    # wait until rcon answers
../../../../.venv/bin/python provision.py  # gamerules + melon patches (one-time)

../../../../.venv/bin/python rung1.py solo     # 3 segments x 5,025 steps
../../../../.venv/bin/python rung1.py paired   # same + the peer
../../../../.venv/bin/python rung1.py verdict  # Bar 1, honest numbers
```

`rung1.py` starts and stops its own bridge (port 25591) and, in the
paired arm, its own peer. The subject is the blessed stack exactly
(`n23_committed.py confirm`); the instrument and the Bar 1
operationalization are documented in `rung1.py`'s docstring and
pre-registered in `../README.md`. Status rows land in
`{solo,paired}-status.jsonl`; the peer's act log in
`paired-peer.log`; world data stays in `./data/` (gitignored, like the
C1 world's).

Instrument checks already run against this stack: the live contract
check (`examples/minecraft/contract_check.py --bridge-port 25591`,
CONTRACT OK 2026-08-16) and a 60 s peer smoke run (17 melons dug
across all three patches, escape rules exercised).
