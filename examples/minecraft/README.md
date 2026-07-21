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

Join the server from the launcher — your client version must match the
server pin (**1.21.11**, not the latest 26.x release: see "Version pins"
below). In the launcher: Installations → New installation → version
`1.21.11`, Play, then Multiplayer → add `127.0.0.1:25565` once. The
stack flips you to **spectator** and teleports you next to the bot,
camera facing it: press F5 to orbit it in third person,
left-click the bot to see through its eyes (Shift to detach). Spectators
are invisible, don't collide, and can't touch blocks — the experiment
cannot tell you are there.

Ctrl-C stops the brain and tears down what the script started (bridge,
dash, watcher, nats if it launched one); the world container keeps
running for fast resume (`docker compose down` here stops it too).
Knobs (env vars): `BOT_NAME`, `BRIDGE_PORT`, `DASH_PORT`, `NATS_URL`,
`OPEN_CLIENT=0` (no launcher/browser), `SPECTATE=0` (never touch your
gamemode), `TICK_RATE` (see below). Stage logs land in `logs/`.

## Accelerating the run

    TICK_RATE=80 ./up.sh --tick-ms 62      # ~4x wall-clock compression

Two paired knobs. `TICK_RATE` sets the world's simulation speed
(vanilla `/tick rate`; 20 = normal) and re-asserts it on every boot,
because the server resets to 20 TPS on restart — measured. It scales
everything the server simulates: day/night, weather, growth, mob
behavior — the rhythms the bot's env channels sense. `--tick-ms`
(default 250) sets the brain's step cadence; lowering it gives
proportionally more brain steps per hour. For a coherent factor-F
acceleration, scale both together: tick rate `20*F`, tick-ms `250/F`.

The one honest exception: the bot's *body* is paced by mineflayer in
real wall-clock time, so walking and digging do not speed up — at
factor F the body is effectively F× slower relative to the world and
to the brain's sampling, and a shorter tick budget means less motion
(and more abandoned digs) per step. That is a different embodiment,
not a broken one — but pick a factor once and keep it for the whole
run, and expect measurements from accelerated runs to differ from the
250 ms posture. Measured green at 40 TPS / 100 ms; per-tick headroom
at this world size suggests ~4–8× is workable.

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

`docker-compose.yml` pins `VERSION: "1.21.11"`; the bridge pins
`mineflayer ^4.20`. They move together: pick a server version mineflayer
supports (https://github.com/PrismarineJS/mineflayer#features), update
both, restart the stack. The brain side is version-agnostic (it speaks
only pra-mc/1 to the bridge).

Why not the current Minecraft release (26.x, the year-based scheme that
replaced 1.21.x in 2026): mineflayer's protocol support ends at 1.21.11
as of 2026-07, and a vanilla client can only join a server of exactly
its own version. So the stack sits at the newest version mineflayer
speaks, and a spectator joins with a matching launcher installation
(two clicks, see above). When mineflayer adds 26.x, bump both pins.

## What the bot senses and does

The channel contract (specs/027-minecraft-body/contracts/): position
relative to spawn + facing (5), health/food (2), light/time/rain (4),
and a three-bit read of the block column ahead (3) — obs_dim 14.
Actions: forward, back, turn left/right 45°, jump-forward, dig ahead,
place ahead, idle. Dig/place act on exactly the block the `blocks`
channel reads: act and sense line up by construction.
