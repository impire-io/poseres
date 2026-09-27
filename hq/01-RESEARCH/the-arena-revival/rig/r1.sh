#!/bin/sh
# Bar R1 — the ladder walks the loop. Detached (nohup), logs to r1.log.
#   bridge with the laps sense -> teach flat -> teach sib -> what each teach
#   stored -> rounds 1..8 (flat and sib interleaved against world drift).
# Every phase is resumable: teach resumes at its last completed lesson,
# rounds skip lives already on record (lc_runner's own bookkeeping).
set -u
cd "$(dirname "$0")"
PY=../../../../.venv/bin/python
FROM=${1:-1}; TO=${2:-8}
echo "[$(date +%T)] R1 begins: bridge (laps on)"
./bridge_up.sh laps || exit 1
sleep 10
for arm in flat sib; do
  echo "[$(date +%T)] teach $arm"
  $PY lc_runner.py teach $arm || { echo "[$(date +%T)] TEACH $arm FAILED"; exit 1; }
  echo "[$(date +%T)] recipes $arm"
  $PY lc_runner.py recipes $arm > recipes-$arm.json && $PY -c "import json;d=json.load(open('recipes-$arm.json'));print('$arm recipes', d['recipes'], 'process', d['process_recipes'])"
done
echo "[$(date +%T)] rounds $FROM..$TO"
$PY lc_runner.py rounds $FROM $TO
echo "[$(date +%T)] R1 rounds exit=$?"
echo "[$(date +%T)] R1 done"
