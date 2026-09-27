#!/bin/sh
# Start (or restart) the arena bridge on port 25591.
#   ./bridge_up.sh        flat body only — R0's probe rows must not carry the counter
#   ./bridge_up.sh laps   the laps sense published from the indicator column (teaches, lives)
# Logs to bridge.log (gitignored). Waits until the bridge listens.
set -eu
cd "$(dirname "$0")"
old=$(lsof -ti tcp:25591 2>/dev/null || true)
[ -n "$old" ] && { echo "stopping old bridge pid(s) $old"; kill $old; sleep 2; }
laps=""
[ "${1:-}" = "laps" ] && laps="25,-63,10"   # INDICATOR (25,-63), first cell z=10, three cells along +z
SURVIVAL=1 MC_PORT=25603 BRIDGE_PORT=25591 BOT_NAME=pra SPAWN_ANCHOR=0,0 LAPS="$laps" \
  nohup node ../../../../examples/minecraft/bridge/bridge.js > bridge.log 2>&1 &
echo "bridge pid $! (LAPS='$laps')"
for i in $(seq 1 40); do
  if lsof -ti tcp:25591 >/dev/null 2>&1; then echo "bridge listening on 25591"; tail -3 bridge.log; exit 0; fi
  sleep 1.5
done
echo "BRIDGE DID NOT COME UP"; tail -20 bridge.log; exit 1
