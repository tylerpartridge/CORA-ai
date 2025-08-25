#!/usr/bin/env bash
set -euo pipefail
WAIT=${WAIT:-45}

echo "== Restarting app =="
systemctl restart cora.service

echo "== Waiting for :8000 (up to ${WAIT}s) =="
for ((i=1; i<=WAIT; i++)); do
  if curl -sf http://127.0.0.1:8000/healthz | grep -Eq '"ok":[[:space:]]*true'; then
    echo "App is up (healthz ok) after ${i}s"
    break
  fi
  sleep 1
  if [ "$i" -eq "$WAIT" ]; then
    echo "App did not come up within ${WAIT}s — showing recent logs"
    journalctl -u cora.service -n 120 --no-pager || true
  fi
done

echo "== Service status =="
systemctl --no-pager --full status cora.service | head -n 20 || true

echo "== Listeners =="
ss -ltnp | egrep '(:8000 )|(:80 )|(:443 )' || true

echo "== App direct (:8000) =="
curl -sSI http://127.0.0.1:8000/ | head -1 || true
curl -sS  http://127.0.0.1:8000/healthz || true; echo

echo "== Nginx -> app (local) =="
curl -sSI http://127.0.0.1/         | head -1 || true
curl -sSI http://127.0.0.1/expenses | head -1 || true

echo "== Public (Cloudflare) =="
curl -sSI https://coraai.tech/         | head -1 || true
curl -sSI https://coraai.tech/expenses | head -1 || true
