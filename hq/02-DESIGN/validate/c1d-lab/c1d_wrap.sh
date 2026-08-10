#!/bin/sh
cd "$(dirname "$0")"
if pgrep -f "[cC]1d_runner.py" >/dev/null; then echo "already running"; exit 1; fi
while true; do
  /Users/calmera/Impire/pra/.venv/bin/python c1d_runner.py >> c1d-run-log.txt 2>&1
  if tail -3 c1d-run-log.txt | grep -q "C1D_STOPPED"; then break; fi
  sleep 2
done
echo WRAPPER-DONE
