#!/bin/bash
# c1e two-arm wrapper: ./c1e_wrap2.sh respawn|oneshot
ARM="$1"
if [ "$ARM" != "respawn" ] && [ "$ARM" != "oneshot" ]; then
  echo "usage: c1e_wrap2.sh respawn|oneshot"; exit 2
fi
case "$ARM" in
  respawn) LOG="c1e-a-run-log.txt" ;;
  oneshot) LOG="c1e-b-run-log.txt" ;;
esac
if pgrep -f "[cC]1e_runner.py $ARM" > /dev/null; then
  echo "c1e $ARM already running"; exit 1
fi
cd "$(dirname "$0")"
while true; do
  /Users/calmera/Impire/pra/.venv/bin/python c1e_runner.py "$ARM" >> "$LOG" 2>&1
  if tail -5 "$LOG" | grep -q "C1E_STOPPED"; then break; fi
  sleep 2
done
