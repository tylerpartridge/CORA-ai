#!/usr/bin/env python3
"""
Safe cleanup of legacy and duplicate files in CORA
Run AFTER backup_before_cleanup.py
"""

import os
import sys
import shutil
from pathlib import Path
from datetime import datetime
import json

# Fix Unicode on Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

def confirm_action(message):
    """Ask for user confirmation"""
    response = input(f"\n[?] {message} [y/N]: ")
    return response.lower() == 'y'

def cleanup_legacy_files():
    """Perform safe cleanup of identified legacy files"""
    
    print("[LAUNCH] CORA Legacy File Cleanup")
    print("=================================\n")
    
    # Track what we're cleaning
    cleanup_log = {
        "timestamp": datetime.now().strftime("%Y%m%d_%H%M%S"),
        "removed_files": [],
        "removed_dirs": [],
        "errors": []
    }
    
    # 1. Check for backup first
    backup_exists = any(Path("backups").glob("cora_pre_cleanup_backup_*.zip"))
    if not backup_exists:
        print("[ERROR] No backup found! Run backup_before_cleanup.py first!")
        return
    
    print("[OK] Backup detected, proceeding with cleanup...\n")
    
    # 2. Remove duplicate web/web directory
    duplicate_web = Path("web/web")
    if duplicate_web.exists():
        print(f"[FOUND] Duplicate directory: {duplicate_web}")
        if confirm_action("Remove duplicate web/web directory?"):
            try:
                shutil.rmtree(duplicate_web)
                cleanup_log["removed_dirs"].append(str(duplicate_web))
                print("[OK] Removed duplicate web/web directory")
            except Exception as e:
                print(f"[ERROR] Failed to remove: {e}")
                cleanup_log["errors"].append(f"Failed to remove {duplicate_web}: {e}")
    
    # 3. Clean up conflicting middleware files
    print("\n[CHECK] Middleware files...")
    
    # Security headers - keep enhanced version
    old_security_files = [
        "middleware/security_headers.py",
        "middleware/security_headers_fixed.py"
    ]
    
    for file in old_security_files:
        if Path(file).exists():
            print(f"[FOUND] Old security header file: {file}")
            if confirm_action(f"Remove {file}? (keeping security_headers_enhanced.py)"):
                try:
                    Path(file).unlink()
                    cleanup_log["removed_files"].append(file)
                    print(f"[OK] Removed {file}")
                except Exception as e:
                    print(f"[ERROR] Failed to remove: {e}")
                    cleanup_log["errors"].append(f"Failed to remove {file}: {e}")
    
    # 4. Consolidate rate limiting (this needs manual review)
    print("\n[WARN] Rate limiting files need manual consolidation:")
    rate_files = [
        "middleware/rate_limit.py",
        "middleware/rate_limiter.py", 
        "middleware/rate_limiting.py"
    ]
    
    existing_rate_files = [f for f in rate_files if Path(f).exists()]
    if len(existing_rate_files) > 1:
        print("[INFO] Multiple rate limiting files found:")
        for f in existing_rate_files:
            print(f"  - {f}")
        print("[ACTION] Review app.py imports and consolidate manually")
    
    # 5. Remove duplicate email script
    old_email_script = Path("send_beta_welcome_emails.py")
    if old_email_script.exists():
        print(f"\n[FOUND] Old email script: {old_email_script}")
        if confirm_action("Remove old email script? (keeping _fixed version)"):
            try:
                old_email_script.unlink()
                cleanup_log["removed_files"].append(str(old_email_script))
                print("[OK] Removed old email script")
            except Exception as e:
                print(f"[ERROR] Failed to remove: {e}")
                cleanup_log["errors"].append(f"Failed to remove {old_email_script}: {e}")
    
    # 6. Archive old fix scripts
    print("\n[CHECK] Old fix scripts...")
    fix_scripts = list(Path("tools").glob("fix_*.py"))
    
    if fix_scripts:
        print(f"[FOUND] {len(fix_scripts)} fix scripts")
        if confirm_action("Move fix scripts to tools/archive/?"):
            archive_dir = Path("tools/archive")
            archive_dir.mkdir(exist_ok=True)
            
            for script in fix_scripts:
                try:
                    dest = archive_dir / script.name
                    shutil.move(str(script), str(dest))
                    cleanup_log["removed_files"].append(f"{script} -> {dest}")
                    print(f"[OK] Archived {script.name}")
                except Exception as e:
                    print(f"[ERROR] Failed to move {script}: {e}")
                    cleanup_log["errors"].append(f"Failed to move {script}: {e}")
    
    # 7. Update app.py imports
    print("\n[INFO] App.py imports need updating:")
    print("  - Line 40: Change to use security_headers_enhanced")
    print("  - Lines 39 & 49: Consolidate rate limiting imports")
    print("[ACTION] Update these manually after reviewing the files")
    
    # Save cleanup log
    log_path = Path("backups") / f"cleanup_log_{cleanup_log['timestamp']}.json"
    with open(log_path, 'w') as f:
        json.dump(cleanup_log, f, indent=2)
    
    print(f"\n[LOG] Cleanup log saved to: {log_path}")
    
    # Summary
    print("\n[SUMMARY] Cleanup Results:")
    print(f"  [OK] Removed {len(cleanup_log['removed_files'])} files")
    print(f"  [OK] Removed {len(cleanup_log['removed_dirs'])} directories")
    if cleanup_log['errors']:
        print(f"  [WARN] {len(cleanup_log['errors'])} errors occurred")
    
    print("\n[PIN] Next Steps:")
    print("1. Manually consolidate rate limiting middleware")
    print("2. Update app.py imports")
    print("3. Test the application")
    print("4. Delete backup only after confirming everything works")

if __name__ == "__main__":
    cleanup_legacy_files()