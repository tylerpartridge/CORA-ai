#!/usr/bin/env python3
"""
Backup CORA system before legacy file cleanup
Creates timestamped backup of entire system
"""

import os
import sys
import shutil
import zipfile
from datetime import datetime
from pathlib import Path
import json

# Fix Unicode on Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

def create_backup():
    """Create comprehensive backup before cleanup operation"""
    
    # Get timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"cora_pre_cleanup_backup_{timestamp}"
    
    # Create backup directory
    backup_dir = Path("backups")
    backup_dir.mkdir(exist_ok=True)
    
    # Full backup path
    backup_path = backup_dir / backup_name
    
    print(f"[LOCK] Creating backup: {backup_name}")
    print("[BOX] This will backup the entire CORA system...")
    
    # Define what to backup
    source_dir = Path(".")
    
    # Items to exclude from backup
    exclude_patterns = [
        "backups/",  # Don't backup previous backups
        "__pycache__",
        "*.pyc",
        ".git/",
        "venv/",
        "env/",
        ".env",
        "node_modules/",
        "*.log",
        "logs/",
        ".pytest_cache/",
        "*.tmp"
    ]
    
    # Create list of files to backup
    backup_manifest = {
        "timestamp": timestamp,
        "purpose": "Pre-cleanup backup before removing legacy files",
        "files_backed_up": [],
        "total_size": 0
    }
    
    # Create zip file
    zip_path = f"{backup_path}.zip"
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(source_dir):
            # Remove excluded directories
            dirs[:] = [d for d in dirs if not any(pattern.rstrip('/') == d for pattern in exclude_patterns)]
            
            for file in files:
                file_path = Path(root) / file
                relative_path = file_path.relative_to(source_dir)
                
                # Skip excluded patterns
                skip = False
                for pattern in exclude_patterns:
                    if pattern.endswith('/'):
                        continue
                    if file_path.match(pattern) or file.endswith(pattern.lstrip('*')):
                        skip = True
                        break
                
                if skip:
                    continue
                
                # Add file to zip
                try:
                    zipf.write(file_path, relative_path)
                    file_size = file_path.stat().st_size
                    backup_manifest["files_backed_up"].append(str(relative_path))
                    backup_manifest["total_size"] += file_size
                    
                    # Progress indicator
                    if len(backup_manifest["files_backed_up"]) % 100 == 0:
                        print(f"  [FILE] Backed up {len(backup_manifest['files_backed_up'])} files...")
                        
                except Exception as e:
                    print(f"  [WARN] Skipped {relative_path}: {str(e)}")
    
    # Save manifest
    manifest_path = backup_dir / f"{backup_name}_manifest.json"
    with open(manifest_path, 'w') as f:
        json.dump(backup_manifest, f, indent=2)
    
    # Calculate final size
    zip_size = Path(zip_path).stat().st_size / (1024 * 1024)  # MB
    
    print("\n[OK] Backup Complete!")
    print(f"[BOX] Backup location: {zip_path}")
    print(f"[DOC] Manifest: {manifest_path}")
    print(f"[STAT] Files backed up: {len(backup_manifest['files_backed_up'])}")
    print(f"[DISK] Backup size: {zip_size:.2f} MB")
    print(f"\n[INFO] Original size: {backup_manifest['total_size'] / (1024 * 1024):.2f} MB")
    print(f"[ZIP] Compression ratio: {(1 - zip_size / (backup_manifest['total_size'] / (1024 * 1024))) * 100:.1f}%")
    
    # Create restore script
    restore_script = backup_dir / f"{backup_name}_restore.py"
    with open(restore_script, 'w') as f:
        f.write(f'''#!/usr/bin/env python3
"""
Restore script for backup: {backup_name}
Created: {timestamp}
"""

import zipfile
import os
from pathlib import Path

def restore():
    backup_path = "{zip_path}"
    target_dir = "."
    
    if not os.path.exists(backup_path):
        print("[ERROR] Backup file not found!")
        return
        
    response = input(f"[WARN] This will restore CORA to state from {timestamp}. Continue? [y/N]: ")
    if response.lower() != 'y':
        print("[ERROR] Restore cancelled")
        return
        
    print("[BOX] Extracting backup...")
    with zipfile.ZipFile(backup_path, 'r') as zipf:
        zipf.extractall(target_dir)
    
    print("[OK] Restore complete!")

if __name__ == "__main__":
    restore()
''')
    
    os.chmod(restore_script, 0o755)
    print(f"\n[TOOL] Restore script created: {restore_script}")
    
    return zip_path, manifest_path

if __name__ == "__main__":
    print("[LAUNCH] CORA Pre-Cleanup Backup Tool")
    print("======================================\n")
    
    try:
        zip_path, manifest_path = create_backup()
        
        print("\n[PIN] Next Steps:")
        print("1. [OK] Backup created successfully")
        print("2. [CLEAN] You can now safely run the cleanup")
        print("3. [RESTORE] If anything goes wrong, use the restore script")
        print("\n[TIP] Keep this backup until you're sure the cleanup was successful!")
        
    except Exception as e:
        print(f"\n[ERROR] Backup failed: {str(e)}")
        print("[WARN] Do not proceed with cleanup until backup succeeds!")