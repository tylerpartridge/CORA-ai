#!/usr/bin/env python3
"""
🗂️ SAFE BACKUP CLEANUP ANALYZER
📁 LOCATION: /CORA/features/performance_optimization/claude/backup_cleanup_analyzer.py
⚠️ PURPOSE: Analyze backup files for safe archival (turtle-pace cleanup)
"""

import os
import re
from datetime import datetime, timedelta
from pathlib import Path

def analyze_backup_files():
    """Carefully analyze backup files for potential cleanup"""
    backup_dir = "/mnt/host/c/CORA/backups"
    
    print("BACKUP FILE ANALYSIS - Safe & Slow Approach")
    print("=" * 50)
    
    if not os.path.exists(backup_dir):
        print(f"Backup directory not found: {backup_dir}")
        return
    
    backup_files = []
    
    # Find all backup files
    for item in os.listdir(backup_dir):
        if item.endswith('.zip.enc') or item.endswith('.db'):
            file_path = os.path.join(backup_dir, item)
            file_stat = os.stat(file_path)
            file_size = file_stat.st_size
            mod_time = datetime.fromtimestamp(file_stat.st_mtime)
            
            # Extract date from filename if possible
            date_match = re.search(r'(\d{8})_(\d{6})', item)
            if date_match:
                try:
                    file_date = datetime.strptime(f"{date_match.group(1)}_{date_match.group(2)}", "%Y%m%d_%H%M%S")
                except:
                    file_date = mod_time
            else:
                file_date = mod_time
            
            backup_files.append({
                'name': item,
                'path': file_path,
                'size': file_size,
                'size_kb': file_size // 1024,
                'date': file_date,
                'mod_time': mod_time,
                'age_days': (datetime.now() - file_date).days
            })
    
    # Sort by date (oldest first)
    backup_files.sort(key=lambda x: x['date'])
    
    print(f"\\nFound {len(backup_files)} backup files")
    print(f"Date range: {backup_files[0]['date'].strftime('%Y-%m-%d')} to {backup_files[-1]['date'].strftime('%Y-%m-%d')}")
    
    # Calculate total size
    total_size_mb = sum(f['size'] for f in backup_files) // (1024 * 1024)
    print(f"Total size: {total_size_mb}MB")
    
    # Analyze by age groups
    now = datetime.now()
    age_groups = {
        'very_old': [],      # > 30 days
        'old': [],           # 15-30 days  
        'recent': [],        # 7-15 days
        'current': []        # < 7 days
    }
    
    for backup in backup_files:
        age = backup['age_days']
        if age > 30:
            age_groups['very_old'].append(backup)
        elif age > 15:
            age_groups['old'].append(backup)
        elif age > 7:
            age_groups['recent'].append(backup)
        else:
            age_groups['current'].append(backup)
    
    # Report by age groups
    print("\\nBACKUP ANALYSIS BY AGE:")
    print("-" * 30)
    
    for group_name, group_files in age_groups.items():
        if group_files:
            group_size = sum(f['size_kb'] for f in group_files)
            print(f"\\n{group_name.upper().replace('_', ' ')} ({len(group_files)} files, {group_size}KB):")
            
            for backup in group_files[:5]:  # Show first 5
                print(f"  {backup['name']} ({backup['size_kb']}KB, {backup['age_days']} days old)")
            
            if len(group_files) > 5:
                print(f"  ... and {len(group_files) - 5} more files")
    
    # Conservative cleanup recommendations
    print("\\nSAFE CLEANUP RECOMMENDATIONS (Turtle Approach):")
    print("-" * 45)
    
    # Only suggest very old backups for archival, and be conservative
    very_old_backups = age_groups['very_old']
    if len(very_old_backups) > 10:  # Keep at least 10 even if very old
        candidates_for_archival = very_old_backups[:-10]  # Keep the newest 10 of the very old
        
        if candidates_for_archival:
            total_savings = sum(f['size_kb'] for f in candidates_for_archival)
            print(f"Consider archiving {len(candidates_for_archival)} very old backups:")
            print(f"  Age range: {candidates_for_archival[0]['age_days']}-{candidates_for_archival[-1]['age_days']} days old")
            print(f"  Potential space saved: {total_savings}KB")
            print(f"  Recommended action: Move to /backups/archived/very_old/")
            
            print("\\n  Sample files to archive:")
            for backup in candidates_for_archival[:3]:
                print(f"    {backup['name']} ({backup['age_days']} days old)")
        else:
            print("No files recommended for archival at this time.")
    else:
        print("Conservative approach: Keep all backups (not enough very old files).")
    
    print("\\nSAFETY NOTES:")
    print("- Never delete backup files, only archive them")  
    print("- Keep at least 10 backups of each age group")
    print("- Test restore process before archiving")
    print("- Archive = move to subdirectory, don't remove")

def create_safe_archival_script():
    """Create a safe script for archiving old backups"""
    script_content = '''#!/usr/bin/env python3
"""
Safe backup archival script - Turtle-pace approach
Only archives very old backups (>45 days) and keeps plenty of safety copies
"""

import os
import shutil
from datetime import datetime, timedelta
from pathlib import Path

# SAFETY FIRST - Conservative settings
DRY_RUN = True  # Always start with dry run
MIN_AGE_DAYS = 45  # Only archive files older than 45 days
MIN_KEEP_COUNT = 15  # Always keep at least 15 backups

def safe_archive_old_backups():
    backup_dir = Path("/mnt/host/c/CORA/backups")
    archive_dir = backup_dir / "archived" / "very_old"
    
    if DRY_RUN:
        print("DRY RUN MODE - No files will be moved")
    
    # Create archive directory if needed
    if not DRY_RUN:
        archive_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Archiving very old backups (>{MIN_AGE_DAYS} days)")
    print(f"Will keep at least {MIN_KEEP_COUNT} newest backups")
    
    # Implementation would go here...
    print("Script template created - implement carefully!")

if __name__ == "__main__":
    safe_archive_old_backups()
'''
    
    script_path = "/mnt/host/c/CORA/features/performance_optimization/claude/safe_backup_archival.py"
    with open(script_path, 'w') as f:
        f.write(script_content)
    
    print(f"\\nCreated safe archival script: {script_path}")
    print("Remember: Always test in dry-run mode first!")

if __name__ == "__main__":
    analyze_backup_files()
    create_safe_archival_script()