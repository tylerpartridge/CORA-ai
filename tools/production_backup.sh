#!/bin/bash
# Production Backup Script
# Created: 2025-08-20
# Purpose: Backup production database and critical files

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/var/www/backups/$TIMESTAMP"

echo "🔄 Starting production backup..."

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup database
echo "📊 Backing up database..."
cp /var/www/cora/cora.db $BACKUP_DIR/cora.db
cp /var/www/cora/data/cora.db $BACKUP_DIR/data_cora.db 2>/dev/null || true

# Backup environment files
echo "🔐 Backing up config..."
cp /var/www/cora/.env $BACKUP_DIR/.env 2>/dev/null || true
cp /var/www/cora/.env.production $BACKUP_DIR/.env.production 2>/dev/null || true

# Backup user uploads
echo "📸 Backing up uploads..."
cp -r /var/www/cora/uploads $BACKUP_DIR/uploads 2>/dev/null || true
cp -r /var/www/cora/receipts $BACKUP_DIR/receipts 2>/dev/null || true

# Create backup manifest
echo "📝 Creating manifest..."
cat > $BACKUP_DIR/manifest.txt << EOF
Backup Created: $TIMESTAMP
Server: coraai.tech
Files Backed Up:
- cora.db (main database)
- .env files (config)
- uploads/ (user files)
- receipts/ (receipt images)
EOF

# Compress backup
echo "🗜️ Compressing backup..."
cd /var/www/backups
tar -czf backup_$TIMESTAMP.tar.gz $TIMESTAMP/

# Clean up uncompressed files
rm -rf $TIMESTAMP/

# Keep only last 7 backups
echo "🧹 Cleaning old backups..."
ls -t backup_*.tar.gz | tail -n +8 | xargs rm -f 2>/dev/null || true

echo "✅ Backup complete: /var/www/backups/backup_$TIMESTAMP.tar.gz"

# Show backup size
du -h /var/www/backups/backup_$TIMESTAMP.tar.gz