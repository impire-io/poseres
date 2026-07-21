# C1: a brain in Minecraft, for weeks

One character on a small self-hosted server, learning continuously —
the ROADMAP C1 showcase on the feature-027 adapter. Three processes:
the server (Docker), the bridge (Node + mineflayer), the brain (this
repo). Each can restart independently; the brain resumes exactly from
its latest snapshot.

## One command, watching included

    ./up.sh                    # from examples/minecraft/; extra args go
                               # to run_c1.py, e.g. ./up.sh --seed 1

Brings up the whole stack in dependency order, each stage gated on a
readiness check: the world (Docker), a NATS server (reused if one is
already on :4222), the bridge, `pra-dash` (opened in your browser), the
Minecraft launcher, and finally the brain in the foreground with
telemetry on.

Join the server from the launcher (Multiplayer → add `127.0.0.1:25565`
once) and the stack flips you to **spectator** and teleports you next to
the bot, camera facing it: press F5 to orbit it in third person,
left-click the bot to see through its eyes (Shift to detach). Spectators
are invisible, don't collide, and can't touch blocks — the experiment
cannot tell you are there.

Ctrl-C stops the brain and tears down what the script started (bridge,
dash, watcher, nats if it launched one); the world container keeps
running for fast resume (`docker compose down` here stops it too).
Knobs (env vars): `BOT_NAME`, `BRIDGE_PORT`, `DASH_PORT`, `NATS_URL`,
`OPEN_CLIENT=0` (no launcher/browser), `SPECTATE=0` (never touch your
gamemode). Stage logs land in `logs/`.

## Start (by hand)

    # 1. the world (first boot generates the map: ~1-2 minutes)
    docker compose up -d

    # 2. the bridge (waits for the server, spawns the bot, then listens)
    cd bridge && npm install && node bridge.js

    # 3. the brain (from the repo root, in the venv)
    python examples/minecraft/run_c1.py

Add `--nats nats://127.0.0.1:4222` (with a nats-server running; see
`examples/nats/`) to publish telemetry and watch with `pra-dash`.

## Stop / resume / restart

- **Brain**: Ctrl-C any time. Work since the last snapshot is lost
  (default cadence: 25 cycles = 6 000 steps ≈ 25 min at 250 ms/tick).
  Rerun `run_c1.py` — it resumes from the newest snapshot in
  `c1-snapshots/`. Keep `--seed` fixed across resumes (it is checked).
- **Bridge / server**: restart freely while the brain is *stopped*; the
  brain reconnects at its next start. If either dies while the brain is
  running, the brain fails loudly by design — restart the stack and
  rerun (FR-004).
- The brain's state resumes byte-exactly; the *world* resumes wherever
  the live server is — stated openly (Doc 06 §5b class 4). In the
  in-repo FakeBridge mode (the test suite), both resume exactly.

## Configuration notes (arc 026, C1SOAK-DIAGNOSIS)

- `weight_norm_cap=1.2` is on: measured behaviorally free, closes the
  long-lifetime tail.
- Snapshot blobs grow ~8 bytes/step (the in-state error trace, by
  design): ~2–20 MB over a multi-month run at these tick rates.
- Expect the frame population to ride its ceiling (`max_frames`) in
  continuous mode, at ~10% wall cost — measured, normal.

## Version pins

`docker-compose.yml` pins `VERSION: "1.21.1"`; the bridge pins
`mineflayer ^4.20`. They move together: pick a server version mineflayer
supports (https://github.com/PrismarineJS/mineflayer#features), update
both, restart the stack. The brain side is version-agnostic (it speaks
only pra-mc/1 to the bridge).

## What the bot senses and does

The channel contract (specs/027-minecraft-body/contracts/): position
relative to spawn + facing (5), health/food (2), light/time/rain (4),
and a three-bit read of the block column ahead (3) — obs_dim 14.
Actions: forward, back, turn left/right 45°, jump-forward, dig ahead,
place ahead, idle. Dig/place act on exactly the block the `blocks`
channel reads: act and sense line up by construction.
