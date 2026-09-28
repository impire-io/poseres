#!/bin/sh
# Amendment 4 — arm sap, eight lives on the sibling's teach. Detached (nohup), logs to r2.log.
set -u
cd "$(dirname "$0")"
PY=../../../../.venv/bin/python
FROM=${1:-1}; TO=${2:-8}
echo "[$(date +%T)] R2 begins: bridge (laps on)"
./bridge_up.sh laps || exit 1
sleep 10
echo "[$(date +%T)] recipes sap"
$PY lc_runner.py recipes sap > recipes-sap.json && $PY -c "import json;d=json.load(open('recipes-sap.json'));print('sap recipes', d['recipes'], 'process', d['process_recipes'])"
echo "[$(date +%T)] lives sap $FROM..$TO"
$PY lc_runner.py lives sap $FROM $TO
echo "[$(date +%T)] R2 lives exit=$?"
echo "[$(date +%T)] R2 done"
