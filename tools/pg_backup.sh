#!/usr/bin/env bash
set -euo pipefail

# Load DSN
if [[ -f /root/CORA_PROD_PG_DSN.env ]]; then
  # shellcheck disable=SC1091
  source /root/CORA_PROD_PG_DSN.env || true
fi

PG_DSN="${PG_DSN:-${DATABASE_URL:-}}"
BACKUP_DIR="${CORA_PG_BACKUP_DIR:-/var/backups/cora/pg}"
RETENTION_DAYS="${CORA_PG_BACKUP_RETENTION_DAYS:-7}"
LOG_FILE="/var/log/cora_pg_backup.log"

mkdir -p "${BACKUP_DIR}"
chmod 700 "${BACKUP_DIR}"
chown postgres:postgres "${BACKUP_DIR}" || true
touch "${LOG_FILE}" || true

timestamp() { date -u +"%Y-%m-%dT%H:%M:%SZ"; }

echo "[$(timestamp)] START backup to ${BACKUP_DIR}" >>"${LOG_FILE}"

if [[ -z "${PG_DSN}" ]]; then
  echo "[$(timestamp)] ERROR: PG_DSN/DATABASE_URL not set" >>"${LOG_FILE}"
  echo "PG_DSN/DATABASE_URL not set" >&2
  exit 1
fi

fname="cora_pg_$(date +%Y%m%d_%H%M%S).dump"
fpath="${BACKUP_DIR}/${fname}"

# Run pg_dump in custom format (-Fc)
PGCONNECT_TIMEOUT=10 pg_dump -Fc "${PG_DSN}" > "${fpath}"
chmod 600 "${fpath}"
chown postgres:postgres "${fpath}" || true

echo "[$(timestamp)] DONE: ${fpath}" >>"${LOG_FILE}"

# Retention rotation
if [[ "${RETENTION_DAYS}" =~ ^[0-9]+$ ]]; then
  find "${BACKUP_DIR}" -type f -name 'cora_pg_*.dump' -mtime +"${RETENTION_DAYS}" -print -delete >>"${LOG_FILE}" 2>&1 || true
  echo "[$(timestamp)] ROTATION: kept last ${RETENTION_DAYS} days" >>"${LOG_FILE}"
fi

exit 0


