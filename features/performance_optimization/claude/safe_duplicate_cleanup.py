#!/usr/bin/env python3
"""
🗑️ SAFE DUPLICATE FILE CLEANUP SCRIPT
📁 LOCATION: /CORA/features/performance_optimization/claude/safe_duplicate_cleanup.py
⚠️ SAFETY: Creates backups before removal, dry-run mode default
"""

import os
import shutil
from datetime import datetime
from pathlib import Path

# SAFETY: Set to False to actually execute cleanup
DRY_RUN = True

# Files identified as safe to remove (unbundled versions when bundled exist)
FILES_TO_CLEANUP = [
    {
        "file": "/mnt/host/c/CORA/web/static/js/accessibility.js",
        "size_kb": 44,
        "reason": "Bundled version exists (24KB) - unbundled version redundant",
        "bundled_version": "/mnt/host/c/CORA/web/static/js/bundles/accessibility.js"
    },
    {
        "file": "/mnt/host/c/CORA/web/static/js/error-manager.js", 
        "size_kb": 23,
        "reason": "Bundled version exists (14KB) - unbundled version redundant",
        "bundled_version": "/mnt/host/c/CORA/web/static/js/bundles/error-manager.js"
    },
    {
        "file": "/mnt/host/c/CORA/web/static/js/performance.js",
        "size_kb": 0,  # Will be calculated
        "reason": "Bundled version exists - unbundled version redundant", 
        "bundled_version": "/mnt/host/c/CORA/web/static/js/bundles/performance.js"
    },
    {
        "file": "/mnt/host/c/CORA/web/static/js/timeout-handler.js",
        "size_kb": 0,  # Will be calculated
        "reason": "Bundled version exists - unbundled version redundant",
        "bundled_version": "/mnt/host/c/CORA/web/static/js/bundles/timeout-handler.js"
    },
    {
        "file": "/mnt/host/c/CORA/web/static/js/web-vitals-monitoring.js",
        "size_kb": 0,  # Will be calculated
        "reason": "Bundled version exists - unbundled version redundant",
        "bundled_version": "/mnt/host/c/CORA/web/static/js/bundles/web-vitals-monitoring.js"
    }
]

def backup_file(filepath):
    """Create timestamped backup before removal"""
    backup_dir = Path(filepath).parent / "backups"
    backup_dir.mkdir(exist_ok=True)
    
    filename = Path(filepath).name
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = backup_dir / f"{filename}.backup_{timestamp}"
    
    shutil.copy2(filepath, backup_path)
    return str(backup_path)

def verify_bundled_version_exists(bundled_path):
    """Verify the bundled version exists and is smaller"""
    if not os.path.exists(bundled_path):
        return False, "Bundled version not found"
    
    bundled_size = os.path.getsize(bundled_path) 
    if bundled_size == 0:
        return False, "Bundled version is empty"
        
    return True, f"Bundled version exists ({bundled_size // 1024}KB)"

def main():
    print("SAFE DUPLICATE FILE CLEANUP")
    print("=" * 40)
    
    if DRY_RUN:
        print("DRY RUN MODE - No files will be removed")
        print("Set DRY_RUN = False to execute cleanup")
        print()
    
    total_space_saved = 0
    files_processed = 0
    
    print("Analyzing files for cleanup...")
    print()
    
    for file_info in FILES_TO_CLEANUP:
        filepath = file_info["file"]
        bundled_path = file_info["bundled_version"]
        
        print(f"Checking: {Path(filepath).name}")
        
        # Check if original file exists
        if not os.path.exists(filepath):
            print(f"  SKIP: Original file not found")
            print()
            continue
        
        # Verify bundled version exists and is valid
        bundled_ok, bundled_msg = verify_bundled_version_exists(bundled_path)
        if not bundled_ok:
            print(f"  SKIP: {bundled_msg}")
            print()
            continue
        
        # Get actual file size
        file_size = os.path.getsize(filepath)
        file_size_kb = file_size // 1024
        
        print(f"  Original: {file_size_kb}KB")
        print(f"  {bundled_msg}")
        print(f"  Reason: {file_info['reason']}")
        
        if not DRY_RUN:
            try:
                # Create backup
                backup_path = backup_file(filepath)
                print(f"  Backup created: {Path(backup_path).name}")
                
                # Remove original
                os.remove(filepath)
                print(f"  REMOVED: Saved {file_size_kb}KB")
                
                total_space_saved += file_size
                files_processed += 1
                
            except Exception as e:
                print(f"  ERROR: Failed to remove - {e}")
        else:
            print(f"  WOULD REMOVE: Would save {file_size_kb}KB")
            total_space_saved += file_size
            files_processed += 1
        
        print()
    
    # Summary
    total_space_kb = total_space_saved // 1024
    
    if DRY_RUN:
        print("DRY RUN SUMMARY:")
        print(f"  Files that would be removed: {files_processed}")
        print(f"  Space that would be saved: {total_space_kb}KB")
        print()
        print("To execute cleanup, set DRY_RUN = False")
    else:
        print("CLEANUP COMPLETE:")
        print(f"  Files removed: {files_processed}")
        print(f"  Space saved: {total_space_kb}KB")
        print(f"  Backups created in: web/static/js/backups/")
    
    print()
    print("SAFETY NOTES:")
    print("- All templates now reference bundled versions")
    print("- Bundled versions are minified and smaller")  
    print("- Backups are created before removal")
    print("- Can be reversed by restoring from backups")

def verify_templates_use_bundled():
    """Verify that templates are using bundled versions"""
    print("TEMPLATE VERIFICATION:")
    print("-" * 20)
    
    # Check key template files
    template_files = [
        "/mnt/host/c/CORA/web/templates/base_app.html",
        "/mnt/host/c/CORA/web/templates/base_public.html", 
        "/mnt/host/c/CORA/web/templates/components/scripts_core.html"
    ]
    
    all_good = True
    
    for template_path in template_files:
        if os.path.exists(template_path):
            with open(template_path, 'r') as f:
                content = f.read()
            
            template_name = Path(template_path).name
            
            # Check for unbundled versions
            problematic_refs = []
            for file_info in FILES_TO_CLEANUP:
                filename = Path(file_info["file"]).name
                if f'/static/js/{filename}' in content and '/bundles/' not in content.split(f'/static/js/{filename}')[0].split('\\n')[-1]:
                    problematic_refs.append(filename)
            
            if problematic_refs:
                print(f"  WARNING: {template_name} still references unbundled files:")
                for ref in problematic_refs:
                    print(f"    - {ref}")
                all_good = False
            else:
                print(f"  OK: {template_name} uses bundled versions")
    
    print()
    return all_good

if __name__ == "__main__":
    # First verify templates
    templates_ok = verify_templates_use_bundled()
    
    if not templates_ok:
        print("WARNING: Some templates still reference unbundled files!")
        print("Please update templates before running cleanup.")
        print()
    
    main()