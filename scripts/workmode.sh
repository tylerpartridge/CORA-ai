#!/usr/bin/env bash
set -euo pipefail

ROOT="/var/www/cora"
SERVICE="cora.service"
WAIT="${WAIT:-45}"                          # seconds to wait for health
HEALTH_URL="${HEALTH_URL:-http://127.0.0.1:8000/healthz}"

echo "▶ Restarting $SERVICE …"
systemctl restart "$SERVICE"

echo "⏳ Waiting up to ${WAIT}s for health …"
end=$((SECONDS + WAIT))
ok=0
while [ $SECONDS -lt $end ]; do
  if curl -fsS "$HEALTH_URL" | grep -q '"ok":[[:space:]]*true'; then ok=1; break; fi
  sleep 2
done

if [ $ok -ne 1 ]; then
  echo "❌ Health check failed after ${WAIT}s"
  echo "--- last 60 lines of service logs ---"
  journalctl -u "$SERVICE" -n 60 --no-pager || true
  exit 1
fi
echo "✅ Health OK"

echo "🧪 Running infra verify …"
cd "$ROOT"
./tools/verify_infra.sh

echo "✅ Verify PASSED"
echo "✔ Done."
