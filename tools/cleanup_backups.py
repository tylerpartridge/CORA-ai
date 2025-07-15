#!/usr/bin/env python3
"""
Cleanup script for all backup files
- Dry-run by default: shows what would be moved
- Archive mode: moves files to system temp dir for 24-hour safety net
"""

import os
import shutil
import sys
import tempfile
from datetime import datetime

# All backup directories to clean
BACKUP_DIRS = [
    os.path.join('.mind', 'backups'),
    os.path.join('.mind', 'backups', 'file_splitting'),
    os.path.join('.mind', 'backups', 'import_cleanup'),
    os.path.join('.mind', 'backup'),
]

ARCHIVE_DIR = os.path.join(tempfile.gettempdir(), f'cora-backup-archive-{datetime.now().strftime("%Y%m%d_%H%M%S")}')

def cleanup_backups(dry_run=True):
    total_files = 0
    total_moved = 0
    
    print("=== COMPREHENSIVE BACKUP CLEANUP ===")
    
    for backup_dir in BACKUP_DIRS:
        if not os.path.exists(backup_dir):
            print(f"Directory {backup_dir} does not exist, skipping...")
            continue
            
        files = []
        for root, dirs, files_in_dir in os.walk(backup_dir):
            for file in files_in_dir:
                if os.path.isfile(os.path.join(root, file)):
                    files.append(os.path.join(root, file))
        
        if not files:
            print(f"No files found in {backup_dir}")
            continue
            
        print(f"\nFound {len(files)} files in {backup_dir}")
        total_files += len(files)
        
        if dry_run:
            print("Dry run mode: No files will be moved.")
            for f in files[:5]:  # Show first 5 files
                print(f"  Would move: {f}")
            if len(files) > 5:
                print(f"  ...and {len(files)-5} more.")
        else:
            # Archive mode
            os.makedirs(ARCHIVE_DIR, exist_ok=True)
            moved = 0
            for f in files:
                try:
                    # Create relative path structure in archive
                    rel_path = os.path.relpath(f, '.')
                    archive_path = os.path.join(ARCHIVE_DIR, rel_path)
                    os.makedirs(os.path.dirname(archive_path), exist_ok=True)
                    shutil.move(f, archive_path)
                    moved += 1
                except Exception as e:
                    print(f"  ERROR moving {f}: {e}")
            
            print(f"Moved {moved} files from {backup_dir}")
            total_moved += moved
    
    print(f"\n=== SUMMARY ===")
    print(f"Total files found: {total_files}")
    if not dry_run:
        print(f"Total files moved: {total_moved}")
        print(f"Archive location: {ARCHIVE_DIR}")
    else:
        print("Run with --archive to actually move files.")

if __name__ == "__main__":
    dry_run = "--archive" not in sys.argv
    cleanup_backups(dry_run) 