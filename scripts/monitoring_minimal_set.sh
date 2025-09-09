#!/usr/bin/env bash
set -euo pipefail

log_file="/var/log/cora_monitoring_one_shot.log"
touch "$log_file" || true
exec >>"$log_file" 2>&1

echo "[CORA] Monitoring Minimal Set one-shot started at $(date -u +%Y-%m-%dT%H:%M:%SZ)"

# 1) Apply SENTRY_DSN drop-in if DSN file exists
if [[ -f "/root/CORA_SENTRY_DSN.env" ]]; then
  echo "[CORA] SENTRY DSN file present; configuring systemd drop-in"
  install -d -m 0755 /etc/systemd/system/cora.service.d
  cat >/etc/systemd/system/cora.service.d/10-sentry.conf <<'EOF'
[Service]
EnvironmentFile=/root/CORA_SENTRY_DSN.env
EOF
  systemctl daemon-reload
  systemctl restart cora.service || true

  # Send one test event if sentry-sdk available or install temporarily
  if command -v python3 >/dev/null 2>&1; then
    python3 - <<'PY'
import os, sys
dsn = os.getenv('SENTRY_DSN') or os.getenv('CORA_SENTRY_DSN')
if dsn and dsn.startswith('https://'):
    try:
        import sentry_sdk
    except Exception:
        os.system('python3 -m pip install --quiet sentry-sdk')
        import sentry_sdk  # noqa
    from sentry_sdk.integrations.logging import LoggingIntegration
    sentry_sdk.init(dsn=dsn, traces_sample_rate=0.0, environment=os.getenv('ENV','production'))
    try:
        1/0
    except Exception as e:
        sentry_sdk.capture_exception(e)
        print('[CORA] Sentry test event sent')
else:
    print('[CORA] SENTRY_DSN not set; skipping test event')
PY
  fi
else
  echo "[CORA] No SENTRY DSN file; skipping Sentry configuration"
fi

# 2) Internal uptime probe (cron */5)
echo "[CORA] Installing/refreshing internal uptime probe cron"
install -d -m 0755 /usr/local/bin
cat >/usr/local/bin/cora-uptime-probe.sh <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
BASE=${BASE:-http://127.0.0.1:8000}
ts=$(date -u +%Y-%m-%dT%H:%M:%SZ)
code_health=$(curl -s -o /dev/null -w "%{http_code}" "$BASE/health" || echo 000)
code_status=$(curl -s -o /dev/null -w "%{http_code}" "$BASE/api/status" || echo 000)
echo "$ts health=$code_health status=$code_status" >> /var/log/cora_uptime_probe.log
EOF
chmod +x /usr/local/bin/cora-uptime-probe.sh

cat >/etc/cron.d/cora-uptime-probe <<'EOF'
*/5 * * * * root BASE=http://127.0.0.1:8000 /usr/local/bin/cora-uptime-probe.sh
EOF
chmod 0644 /etc/cron.d/cora-uptime-probe
systemctl restart cron || systemctl restart crond || true

# 3) Run local smokes (non-blocking best-effort)
echo "[CORA] Running local smokes (best-effort)"
if [[ -x "/var/www/cora/tools/smoke.sh" ]]; then
  (cd /var/www/cora && ./tools/smoke.sh --base-url http://127.0.0.1:8000 --retries 2 --timeout 5 || true)
fi
if command -v python3 >/dev/null 2>&1 && [[ -f "/var/www/cora/tools/smoke.py" ]]; then
  (cd /var/www/cora && python3 tools/smoke.py --base-url http://127.0.0.1:8000 --retries 2 --timeout 5 --json || true)
fi

echo "[CORA] One-shot complete at $(date -u +%Y-%m-%dT%H:%M:%SZ)"
exit 0

