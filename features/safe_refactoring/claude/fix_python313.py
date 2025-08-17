#!/usr/bin/env python3
"""
Quick fix for Python 3.13 + eventlet incompatibility
This temporarily disables Sentry to get tests running
"""

import os
import shutil
from datetime import datetime

def fix_sentry_import():
    """Comment out Sentry imports to fix Python 3.13 issue"""
    
    app_file = "/mnt/host/c/CORA/app.py"
    backup_file = f"/mnt/host/c/CORA/app_py_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
    
    # Create backup
    print(f"Creating backup: {backup_file}")
    shutil.copy2(app_file, backup_file)
    
    # Read the file
    with open(app_file, 'r') as f:
        lines = f.readlines()
    
    # Comment out problematic imports
    modified = False
    for i, line in enumerate(lines):
        if line.strip().startswith('import sentry_sdk'):
            lines[i] = f"# {line}"  # Comment out
            modified = True
            print(f"Commented out line {i+1}: {line.strip()}")
        elif line.strip().startswith('from sentry_sdk'):
            lines[i] = f"# {line}"  # Comment out
            modified = True
            print(f"Commented out line {i+1}: {line.strip()}")
    
    if modified:
        # Write back
        with open(app_file, 'w') as f:
            f.writelines(lines)
        print(f"\n✅ Fixed! Sentry imports commented out.")
        print(f"Backup saved to: {backup_file}")
        print("\nTo restore:")
        print(f"  cp {backup_file} {app_file}")
    else:
        print("No changes needed - imports already commented or not found")
    
    return modified

def test_server_startup():
    """Test if server can start now"""
    print("\n Testing server startup...")
    import subprocess
    result = subprocess.run(
        ["python", "app.py"],
        capture_output=True,
        text=True,
        timeout=5
    )
    
    if "Uvicorn running" in result.stdout or "Started server" in result.stdout:
        print("✅ Server starts successfully!")
        return True
    else:
        print("❌ Server still has issues:")
        print(result.stderr[:500])
        return False

if __name__ == "__main__":
    print("Python 3.13 + eventlet Fix Script")
    print("=" * 40)
    print("This will temporarily disable Sentry to fix the eventlet issue\n")
    
    response = input("Proceed? (y/n): ")
    if response.lower() == 'y':
        if fix_sentry_import():
            test_server_startup()
    else:
        print("Cancelled")