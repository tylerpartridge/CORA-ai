#!/usr/bin/env python3
"""
Clean up backup and duplicate files
"""

import os
from pathlib import Path
from datetime import datetime

def find_backup_files():
    """Find all backup/duplicate files"""
    patterns = [
        '*_backup.py',
        '*_backup2.py',
        '*_OLD.html',
        '*_old.py',
        '*.bak',
        '*.backup',
        '*.orig',
        '*_copy.py',
        '*_BACKUP_*.py',
        '*_original.py',
        '*.unicode_backup'
    ]
    
    backup_files = []
    root = Path('.')
    
    for pattern in patterns:
        backup_files.extend(root.rglob(pattern))
    
    # Filter out archive directories
    backup_files = [f for f in backup_files 
                   if 'archive' not in str(f).lower() 
                   and 'backup' not in str(f.parent).lower()]
    
    return backup_files

def categorize_files(files):
    """Categorize backup files by type"""
    categories = {
        'Python backups': [],
        'HTML backups': [],
        'Unicode backups': [],
        'Other backups': []
    }
    
    for f in files:
        if f.suffix == '.py':
            categories['Python backups'].append(f)
        elif f.suffix == '.html':
            categories['HTML backups'].append(f)
        elif 'unicode_backup' in str(f):
            categories['Unicode backups'].append(f)
        else:
            categories['Other backups'].append(f)
    
    return categories

def main():
    print("Backup File Cleanup Tool")
    print("=" * 60)
    
    # Find backup files
    backup_files = find_backup_files()
    
    if not backup_files:
        print("No backup files found!")
        return
    
    print(f"Found {len(backup_files)} backup files\n")
    
    # Categorize
    categories = categorize_files(backup_files)
    
    # Show by category
    total_size = 0
    for category, files in categories.items():
        if files:
            print(f"{category}: {len(files)} files")
            size = sum(f.stat().st_size for f in files)
            total_size += size
            print(f"  Size: {size / 1024:.1f} KB")
            
            # Show first 3 files
            for f in files[:3]:
                print(f"    - {f}")
            if len(files) > 3:
                print(f"    ... and {len(files) - 3} more")
            print()
    
    print(f"Total space used: {total_size / 1024:.1f} KB")
    print("\n" + "=" * 60)
    
    # Create cleanup script
    cleanup_script = Path('features/safe_refactoring/claude/DELETE_BACKUPS.sh')
    with open(cleanup_script, 'w') as f:
        f.write("#!/bin/bash\n")
        f.write("# Backup deletion script\n")
        f.write(f"# Generated: {datetime.now()}\n")
        f.write("# Run this to delete all backup files\n\n")
        
        for file in backup_files:
            # Use forward slashes for cross-platform
            file_path = str(file).replace('\\', '/')
            f.write(f'rm "{file_path}"\n')
        
        f.write(f"\necho 'Deleted {len(backup_files)} backup files'\n")
    
    print("Cleanup script created: features/safe_refactoring/claude/DELETE_BACKUPS.sh")
    print("\nTo delete all backup files, run:")
    print("  bash features/safe_refactoring/claude/DELETE_BACKUPS.sh")
    
    # Also create a Python version
    py_script = Path('features/safe_refactoring/claude/delete_backups.py')
    with open(py_script, 'w') as f:
        f.write("#!/usr/bin/env python3\n")
        f.write('"""Delete all backup files"""\n\n')
        f.write("from pathlib import Path\n\n")
        f.write("files_to_delete = [\n")
        for file in backup_files:
            f.write(f"    Path('{file}'),\n")
        f.write("]\n\n")
        f.write("deleted = 0\n")
        f.write("for f in files_to_delete:\n")
        f.write("    if f.exists():\n")
        f.write("        f.unlink()\n")
        f.write("        deleted += 1\n")
        f.write("        print(f'Deleted: {f}')\n")
        f.write(f"\nprint(f'\\nDeleted {{deleted}} files')\n")
    
    print("Python script created: features/safe_refactoring/claude/delete_backups.py")

if __name__ == "__main__":
    main()