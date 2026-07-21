#!/usr/bin/env bash
# One-command C1 stack (feature 027): world + NATS + bridge + brain, with
# pra-dash opened in the browser and your Minecraft client flipped to
# spectator next to the bot the moment you join. See README.md
# ("One command, watching included").
#
# Usage: ./up.sh [run_c1.py args...]      # e.g. ./up.sh --seed 1
# Env:   BOT_NAME (pra), BRIDGE_PORT (25580), DASH_PORT (8600),
#        NATS_URL (nats://127.0.0.1:4222), OPEN_CLIENT (1), SPECTATE (1)

set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../.." && pwd)"
LOGS="$HERE/logs"
mkdir -p "$LOGS"

BOT_NAME="${BOT_NAME:-pra}"
BRIDGE_PORT="${BRIDGE_PORT:-25580}"
DASH_PORT="${DASH_PORT:-8600}"
NATS_URL="${NATS_URL:-nats://127.0.0.1:4222}"
NATS_PORT="${NATS_URL##*:}"
OPEN_CLIENT="${OPEN_CLIENT:-1}"
SPECTATE="${SPECTATE:-1}"

PY="$ROOT/.venv/bin/python"
DASH="$ROOT/.venv/bin/pra-dash"

say() { printf 'up: %s\n' "$*"; }
die() {
  printf 'up: %s\n' "$*" >&2
  exit 1
}

port_open() { nc -z 127.0.0.1 "$1" >/dev/null 2>&1; }

wait_port() { # port label timeout_seconds
  local deadline=$(($(date +%s) + $3))
  until port_open "$1"; do
    [ "$(date +%s)" -ge "$deadline" ] && die "$2 did not open port $1 in time (logs: $LOGS)"
    sleep 1
  done
}

dc() { docker compose --project-directory "$HERE" "$@"; }
rcon() { dc exec -T minecraft rcon-cli "$@"; }

# Flip any human who joins to spectator, parked next to the bot and facing
# it. The bot is a player too, so it is pre-seeded into the seen set.
watch_players() {
  local seen=" $BOT_NAME " line names name
  while true; do
    line="$(rcon list 2>/dev/null | tail -n 1)" || line=""
    names="$(printf '%s' "${line#*:}" | tr ',' ' ')"
    for name in $names; do
      case "$seen" in *" $name "*) continue ;; esac
      seen="$seen$name "
      rcon "gamemode spectator $name" >/dev/null 2>&1 || true
      rcon "execute at $BOT_NAME run tp $name ~2 ~3 ~2 facing entity $BOT_NAME eyes" >/dev/null 2>&1 ||
        rcon "tp $name $BOT_NAME" >/dev/null 2>&1 || true
      rcon "say $name is spectating $BOT_NAME - F5 for third person, left-click $BOT_NAME for its eyes" \
        >/dev/null 2>&1 || true
      say "spectator: '$name' joined -> spectator mode, teleported to '$BOT_NAME'"
    done
    sleep 3
  done
}

PIDS=()
STARTED_NATS=0
cleanup() {
  trap - EXIT INT TERM
  local pid
  for pid in ${PIDS[@]+"${PIDS[@]}"}; do
    kill "$pid" >/dev/null 2>&1 || true
  done
  wait >/dev/null 2>&1 || true
  local extras=""
  [ "$STARTED_NATS" = 1 ] && extras=", nats"
  say "down: stopped what this script started (bridge, dash, watcher$extras)"
  say "down: the world container keeps running - 'docker compose down' in examples/minecraft stops it"
}
trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM

[ -x "$PY" ] || die "repo venv missing at $ROOT/.venv (see GETTING-STARTED.md)"
[ -x "$DASH" ] || die "pra-dash not installed in the venv - pip install -e '.[nats]'"
"$PY" -c "import nats" >/dev/null 2>&1 ||
  die "the NATS client library is missing - $ROOT/.venv/bin/pip install -e '.[nats]'"
command -v docker >/dev/null 2>&1 || die "docker is required for the world server"
command -v node >/dev/null 2>&1 || die "node is required for the bridge"
command -v nc >/dev/null 2>&1 || die "nc is required for readiness checks"

# 1. The world. First boot generates the map (~1-2 min); rcon answering
#    means the server is fully up, which is what the bridge needs.
say "world: docker compose up -d"
dc up -d
deadline=$(($(date +%s) + 300))
until rcon list >/dev/null 2>&1; do
  [ "$(date +%s)" -ge "$deadline" ] &&
    die "world not ready after 5 min - 'docker compose logs -f' in examples/minecraft"
  sleep 2
done
say "world: ready on :25565"

# 2. NATS - reuse a running server, otherwise start one with JetStream
#    (the snapshot-on-request object store needs it).
if port_open "$NATS_PORT"; then
  say "nats: reusing the server on :$NATS_PORT"
else
  command -v nats-server >/dev/null 2>&1 ||
    die "nothing on :$NATS_PORT and no nats-server binary (brew install nats-server)"
  say "nats: starting nats-server -js on :$NATS_PORT"
  nats-server -js -p "$NATS_PORT" >"$LOGS/nats.log" 2>&1 &
  PIDS+=($!)
  STARTED_NATS=1
  wait_port "$NATS_PORT" "nats-server" 15
fi

# 3. The bridge. It does not retry: the world must already be up (it is).
if port_open "$BRIDGE_PORT"; then
  say "bridge: reusing the listener on :$BRIDGE_PORT"
else
  [ -d "$HERE/bridge/node_modules" ] || (cd "$HERE/bridge" && npm install)
  say "bridge: spawning bot '$BOT_NAME'"
  BOT_NAME="$BOT_NAME" BRIDGE_PORT="$BRIDGE_PORT" \
    node "$HERE/bridge/bridge.js" >"$LOGS/bridge.log" 2>&1 &
  PIDS+=($!)
  wait_port "$BRIDGE_PORT" "bridge" 60
fi

# 4. The dashboard, opened in the browser.
if port_open "$DASH_PORT"; then
  say "dash: reusing http://127.0.0.1:$DASH_PORT"
else
  "$DASH" --url "$NATS_URL" --port "$DASH_PORT" >"$LOGS/dash.log" 2>&1 &
  PIDS+=($!)
  wait_port "$DASH_PORT" "pra-dash" 30
  say "dash: http://127.0.0.1:$DASH_PORT"
fi
if [ "$OPEN_CLIENT" = 1 ] && command -v open >/dev/null 2>&1; then
  open "http://127.0.0.1:$DASH_PORT" || true
fi

# 5. The Minecraft client - the launcher opens; joining is the one click
#    that cannot be automated. The watcher takes over from there.
if [ "$OPEN_CLIENT" = 1 ]; then
  if open -a Minecraft >/dev/null 2>&1; then
    say "client: launcher opened - Play, then Multiplayer (add 127.0.0.1:25565 once)"
  else
    say "client: Minecraft.app not found - join 127.0.0.1:25565 from any 1.21.11 client"
  fi
fi
if [ "$SPECTATE" = 1 ]; then
  watch_players &
  PIDS+=($!)
  say "spectator: when you join you'll be flipped to spectator next to '$BOT_NAME'"
fi

# 6. The brain, in the foreground: Ctrl-C stops the run (resume by
#    rerunning - snapshots are in c1-snapshots/ at the repo root).
say "brain: run_c1.py --nats $NATS_URL $*"
cd "$ROOT"
rc=0
"$PY" examples/minecraft/run_c1.py --nats "$NATS_URL" "$@" || rc=$?
exit "$rc"
