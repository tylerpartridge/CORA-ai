#!/usr/bin/env bash
set -euo pipefail
echo "[INFRA] checking nginx"; systemctl is-active --quiet nginx && echo ok || echo "not running"
echo "[INFRA] ports 80/443:"; ss -ltnp | awk '/:80 |:443 /{print}' || true
echo "[INFRA] DB hints:"; grep -RniE 'DATABASE_URL|sqlite|postgres' /var/www/cora | head || true
