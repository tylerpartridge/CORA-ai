#!/usr/bin/env bash
set -euo pipefail
repo="/var/www/cora"
ts="$(date -u +%Y%m%d-%H%M%S)"
day="$(date -u +%Y/%m/%d)"
ckpt_dir="/var/backups/cora/progress/${day}/ckpt-${ts}"
mkdir -p "$ckpt_dir"

# git context (best-effort)
if git -C "$repo" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  git -C "$repo" rev-parse --short HEAD > "${ckpt_dir}/commit.txt" || true
  git -C "$repo" status -s > "${ckpt_dir}/status.txt" || true
  git -C "$repo" diff > "${ckpt_dir}/patch.diff" || true
fi

# repo snapshot (exclude big/ephemeral stuff)
tar -czf "${ckpt_dir}/repo.tgz" \
  --warning=no-file-changed \
  --exclude='.git' \
  --exclude='node_modules' \
  --exclude='venv' \
  --exclude='__pycache__' \
  --exclude='*.db' --exclude='*.db-*' \
  --exclude='logs/*.log*' \
  -C "$repo" .

# record manifest
{
  echo "checkpoint: ${ckpt_dir}"
  echo "timestamp:  $(date -u -Is)"
  echo "repo:       ${repo}"
} > "${ckpt_dir}/MANIFEST.txt"

# append to awareness log (append-only flag allows this)
printf "Saved checkpoint: %s at %s UTC\n" "${ckpt_dir}" "$(date -u -Is)" \
  | tee -a "${repo}/docs/ai-awareness/AI_WORK_LOG.md" >/dev/null

echo "✅ checkpoint created at: ${ckpt_dir}"
