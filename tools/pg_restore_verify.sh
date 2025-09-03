#!/usr/bin/env bash
set -euo pipefail

# Load DSN
if [[ -f /root/CORA_PROD_PG_DSN.env ]]; then
  # shellcheck disable=SC1091
  source /root/CORA_PROD_PG_DSN.env || true
fi

PG_DSN="${PG_DSN:-${DATABASE_URL:-}}"
BACKUP_DIR="${CORA_PG_BACKUP_DIR:-/var/backups/cora/pg}"
LOG_JSONL="/var/log/cora_pg_restore_verify.jsonl"

ts() { date -u +"%Y-%m-%dT%H:%M:%SZ"; }

if [[ -z "${PG_DSN}" ]]; then
  echo "{\"ts\":\"$(ts)\",\"status\":\"error\",\"message\":\"PG_DSN/DATABASE_URL not set\"}" >>"${LOG_JSONL}"
  echo "PG_DSN/DATABASE_URL not set" >&2
  exit 1
fi

latest_dump=$(ls -1t "${BACKUP_DIR}"/cora_pg_*.dump 2>/dev/null | head -1 || true)
if [[ -z "${latest_dump}" ]]; then
  echo "{\"ts\":\"$(ts)\",\"status\":\"error\",\"message\":\"no dumps found\"}" >>"${LOG_JSONL}"
  echo "No dumps found in ${BACKUP_DIR}" >&2
  exit 1
fi

verify_db="cora_restore_verify_$(date +%Y%m%d_%H%M%S)"

echo "{\"ts\":\"$(ts)\",\"event\":\"restore_verify_start\",\"dump\":\"${latest_dump}\",\"verify_db\":\"${verify_db}\"}" >>"${LOG_JSONL}"

# Create temp DB
sudo -u postgres createdb "${verify_db}" -O postgres

# Restore
sudo -u postgres pg_restore --no-owner --no-privileges --clean --if-exists --dbname="postgresql:///${verify_db}" "${latest_dump}"

# Smoke queries
users_count=$(sudo -u postgres psql "postgresql:///${verify_db}" -Atqc "SELECT COUNT(*) FROM users" 2>/dev/null || echo 0)
ok_users=0
if [[ "${users_count}" =~ ^[0-9]+$ ]] && [[ "${users_count}" -gt 0 ]]; then ok_users=1; fi

echo "{\"ts\":\"$(ts)\",\"event\":\"restore_verify_result\",\"users_count\":${users_count},\"ok_users\":${ok_users}}" >>"${LOG_JSONL}"

# Drop temp DB
sudo -u postgres dropdb "${verify_db}" || true

echo "{\"ts\":\"$(ts)\",\"status\":\"complete\",\"dump\":\"${latest_dump}\"}" >>"${LOG_JSONL}"

exit 0


