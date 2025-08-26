# CORA Backup & Restore System

## 🛡️ Protection Against File Loss

This system was created after losing critical AI awareness files (AI_WORK_LOG.md, AI_DISCUSSION_SPACE.md) due to GitHub size limits and cleanup scripts.

## Quick Start

### Immediate Backup
```bash
# One command backup
./tools/cora.sh backup now

# Or directly
bash tools/backup_cora.sh now
```

### Natural Language Triggers
When you say:
- "let's backup our system"
- "backup and end session"  
- "take a snapshot"
- "protect our work"

The AI will run: `cora backup auto`

## Features

### 🔒 Immutable Backups
- Stored in `/var/backups/cora/` (outside project)
- Protected with `chattr +i` (cannot be modified/deleted)
- Timestamped: `YYYYMMDD-HHMMSS-<git-sha>`

### 📦 What Gets Backed Up
**Critical Files (always):**
- AI_WORK_LOG.md
- AI_DISCUSSION_SPACE.md  
- BOOTUP.md
- MVP_REQUIREMENTS.md
- All .db files (SQLite)

**Full Backup Includes:**
- Complete project code
- Configuration files
- Logs (capped at 50MB)
- System metadata

**Excluded:**
- node_modules/
- venv/
- __pycache__/
- .git/

### 🚨 Size Protection
- Pre-push hook checks for files >50MB
- Automatic backup before git push
- Large files tracked separately

## Commands

### Backup Operations
```bash
# Create backup
cora backup now

# Verify integrity
cora backup verify 20250823-143022-abc123

# List all backups
cora backup list

# Check system status
cora status

# Protect critical files
cora protect
```

### Restore Process

#### Quick Restore (Critical Files Only)
```bash
# 1. Find your backup
cora backup list

# 2. Verify it's intact
cora backup verify <backup-id>

# 3. Restore critical files
cp /var/backups/cora/<backup-id>/critical/* /mnt/host/c/CORA/
```

#### Full System Restore
```bash
# 1. Verify backup
cora backup verify <backup-id>

# 2. Stop services
pm2 stop cora

# 3. Backup current state (safety)
mv /mnt/host/c/CORA /mnt/host/c/CORA.old

# 4. Extract full backup
cd /mnt/host/c/
tar -xzf /var/backups/cora/<backup-id>/cora-full.tar.gz

# 5. Restore database
cp /var/backups/cora/<backup-id>/db/* /mnt/host/c/CORA/

# 6. Restart services  
pm2 start cora
```

## Automated Backups

### Git Pre-Push Hook
Automatically backs up before pushing if large files detected:
```bash
# Located at: .git/hooks/pre-push
# Triggers on: git push
# Action: Backs up files >50MB
```

### Scheduled Backups (Optional)
```bash
# Add to crontab
15 2 * * * /mnt/host/c/CORA/tools/cora.sh backup now
```

## Remote Storage Setup

### DigitalOcean Spaces
```bash
# Install rclone
apt-get install rclone

# Configure (interactive)
rclone config
# - Choose "s3"
# - Provider: DigitalOcean Spaces
# - Add credentials
# - Name remote: "spaces"

# Test
rclone ls spaces:cora-backups/
```

### Environment Variables
Create `/etc/cora/backup.env`:
```bash
SPACES_ACCESS_KEY=your_key
SPACES_SECRET_KEY=your_secret
SPACES_ENDPOINT=nyc3.digitaloceanspaces.com
BACKUP_BUCKET=cora-backups
```

## Recovery Scenarios

### Scenario 1: Accidental File Deletion
```bash
# File deleted by cleanup script
cora backup list                    # Find recent backup
cora restore <backup-id>            # Get restore commands
cp /var/backups/cora/<id>/critical/AI_WORK_LOG.md ./
```

### Scenario 2: Git Push Failed (Large Files)
```bash
# Pre-push hook will:
1. Detect large files
2. Run automatic backup
3. Show which files to add to .gitignore
4. Let you proceed safely
```

### Scenario 3: Complete System Failure
```bash
# From fresh server
1. Pull from git
2. Download from Spaces: rclone copy spaces:cora-backups/prod/<date>/<id>/ /tmp/restore/
3. Extract and restore
```

## Backup Report Structure

Each backup creates:
```
/var/backups/cora/<timestamp>-<sha>/
├── MANIFEST.txt          # System info
├── SHA256SUMS.txt       # Integrity checks
├── REPORT.json          # Metadata
├── LARGE_FILES.txt      # Files >50MB
├── critical/            # Critical files
│   ├── AI_WORK_LOG.md
│   ├── AI_DISCUSSION_SPACE.md
│   └── *.db
├── db/                  # Database backups
└── cora-full.tar.gz    # Complete archive
```

## Monitoring

### Check Backup Status
```bash
# Recent backups
cora status

# Verify specific backup
cora backup verify <id>

# Check logs
tail -f /var/log/cora-backup.log
```

### File Size Monitoring
```bash
# Find large files
find /mnt/host/c/CORA -type f -size +50M

# Check critical file sizes
du -h AI_WORK_LOG.md AI_DISCUSSION_SPACE.md
```

## Automated Backup System

### Systemd Timers (Production)
The system includes automated backup via systemd timers:
- **cora-save.timer**: Every 15 minutes (autosave checkpoints)
- **cora-backup.timer**: Daily at 3:15 AM (full system backup)

### Save Wrapper
`tools/save.sh` provides intelligent fallback:
- Uses Python `save_engine.py` if available (smart saves with git diff)
- Falls back to tar-based oneshot if Python not present
- Always creates checkpoint in `/var/backups/cora/progress/`

### Manual Commands
```bash
# Run save (uses wrapper)
bash tools/save.sh

# Check timer status
systemctl status cora-save.timer
systemctl status cora-backup.timer

# View recent saves
ls -la /var/backups/cora/progress/$(date +%Y/%m/%d)/
```

## Best Practices

1. **Before Major Changes**: Run `cora save` or `bash tools/save.sh`
2. **End of Session**: Say "save our progress" 
3. **Weekly**: Check that timers are active with `systemctl list-timers`
4. **Large Files**: Let rotation handle with `cora rotate`
5. **Critical Files**: Protected with `chattr +a` (append-only)

## Troubleshooting

### Backup Fails
```bash
# Check permissions
ls -la /var/backups/cora/

# Check disk space
df -h

# Review logs
tail -100 /var/log/cora-backup.log
```

### Cannot Push to Git
```bash
# Pre-push hook will guide you
# Or manually:
cora backup now
git push
```

### File Missing
```bash
# Check all backup locations
cora backup list
ls -la /mnt/host/c/CORA/backups/
rclone ls spaces:cora-backups/
```

## Important Notes

⚠️ **NEVER DELETE**:
- `/var/backups/cora/` directory
- Files in `backups/` directory  
- Any file marked with `chattr +i`

✅ **ALWAYS BACKUP**:
- Before cleanup scripts
- Before git operations
- Before ending sessions
- When AI_*.md files grow large

🔒 **IMMUTABLE MEANS**: Once created, backups cannot be modified or deleted accidentally

---

*Created: 2025-08-23 after critical file loss incident*
*Purpose: Prevent future data loss from size limits or cleanup scripts*