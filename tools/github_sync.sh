#!/bin/bash
# GitHub Sync Script - Keep production in sync
# Created: 2025-08-20

echo "🔄 Syncing with GitHub..."

cd /var/www/cora

# Stash any local changes
git stash

# Pull latest from GitHub
git pull origin main

# Apply stashed changes if any
git stash pop 2>/dev/null || true

# Push any local commits
git push origin main 2>/dev/null || true

# Show current status
echo "📊 Current status:"
git log --oneline -5
echo ""
echo "✅ GitHub sync complete"