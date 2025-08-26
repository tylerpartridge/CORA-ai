#!/usr/bin/env bash
set -euo pipefail

ROOT="/var/www/cora"
SERVICE="cora.service"
WAIT="${WAIT:-60}"  # seconds
BASE="http://127.0.0.1:8000"
# Try these in order; absolute or relative OK
HEALTH_CANDIDATES=(
  "${HEALTH_URL:-/healthz}"
  "/health"
  "/status"
  "/api/healthz"
  "/api/health"
  "/"
  "/docs"
)

normalize_url() {
  case "$1" in
    http://*|https://*) echo "$1" ;;
    /*)                 echo "${BASE}$1" ;;
    *)                  echo "${BASE}/$1" ;;
  esac
}

echo "▶ Restarting $SERVICE …"
systemctl restart "$SERVICE"

echo "⏳ Waiting up to ${WAIT}s for health …"
end=$((SECONDS + WAIT))
ok=0
while [ $SECONDS -lt $end ]; do
  for cand in "${HEALTH_CANDIDATES[@]}"; do
    url="$(normalize_url "$cand")"
    code="$(curl -fsS -o /dev/null -w '%{http_code}' "$url" || echo 000)"
    if [ "$code" = "200" ]; then
      # optional JSON check for { "ok": true } if endpoint returns JSON
      if curl -fsS "$url" 2>/dev/null | grep -q '"ok"[[:space:]]*:[[:space:]]*true'; then
        echo "✅ Health OK at $url (json ok:true)"
        ok=1; break 2
      fi
      echo "✅ Health OK at $url (HTTP 200)"
      ok=1; break 2
    fi
  done
  sleep 2
done

if [ $ok -ne 1 ]; then
  echo "❌ Health check failed after ${WAIT}s (tried: ${HEALTH_CANDIDATES[*]})"
  echo "--- last 60 lines of service logs ---"
  journalctl -u "$SERVICE" -n 60 --no-pager || true
  exit 1
fi

echo "🧪 Running infra verify …"
cd "$ROOT"
./tools/verify_infra.sh

echo "✅ Verify PASSED"
echo "✔ Done."
