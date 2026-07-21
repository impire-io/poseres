#!/usr/bin/env bash
# Idempotent observatory provisioning (feature 032). Run ON the node, from
# the repo root (e.g. /home/calmera/pra). Safe to re-run after every code
# sync — it reinstalls the package, refreshes units, and leaves running
# experiments alone. See deploy/README.md for the runbook.

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
say() { printf 'provision: %s\n' "$*"; }

# 1. venv + package (nats for tap/dash/flush, s3 for the sink)
if [ ! -x "$ROOT/.venv/bin/python" ]; then
  say "creating venv"
  python3 -m venv "$ROOT/.venv"
fi
say "installing poseres[nats,s3] (editable)"
"$ROOT/.venv/bin/pip" install -q -e "${ROOT}[nats,s3]"

# 2. the bridge's node dependencies
if [ ! -d "$ROOT/examples/minecraft/bridge/node_modules" ]; then
  say "npm install (bridge)"
  (cd "$ROOT/examples/minecraft/bridge" && npm install --silent)
fi

# 3. experiment + s3 configuration under /etc/pra (never overwrite s3.env)
sudo mkdir -p /etc/pra
for env_file in "$ROOT"/deploy/experiments/*.env; do
  sudo cp "$env_file" "/etc/pra/$(basename "$env_file")"
done
if [ ! -f /etc/pra/s3.env ]; then
  sudo cp "$ROOT/deploy/s3.env.default" /etc/pra/s3.env
  say "installed default s3.env (on-node MinIO) — edit /etc/pra/s3.env for real S3"
fi

# 3b. bind address: the tailscale IP when present (tailnet-wide dashboard
# and spectating with zero LAN/public exposure), else localhost-only
BIND_IP="$(tailscale ip -4 2>/dev/null | head -1 || true)"
BIND_IP="${BIND_IP:-127.0.0.1}"
printf 'PRA_BIND_IP=%s\n' "$BIND_IP" > "$ROOT/deploy/infra/.env"
printf 'DASH_HOST=%s\n' "$BIND_IP" | sudo tee /etc/pra/dash.env > /dev/null
say "bind address: $BIND_IP (dashboard :8600, minecraft :25565)"

# 4. run directories (snapshot stores per experiment)
mkdir -p /home/calmera/pra-runs/c1/snapshots /home/calmera/pra-runs/c1-smoke/snapshots

# 5. systemd units
sudo cp "$ROOT"/deploy/units/*.service /etc/systemd/system/
sudo systemctl daemon-reload

# 6. infrastructure (compose) + shared observability
say "docker compose up (infra: nats, minecraft, minio)"
docker compose --project-directory "$ROOT/deploy/infra" up -d
sudo systemctl enable --now pra-dash.service pra-flush.service

say "done. start the experiment with:"
say "  sudo systemctl enable --now pra-bridge@c1 pra-brain@c1"
say "watch: journalctl -fu pra-brain@c1   dashboard: ssh -L 8600:localhost:8600 <node>"
