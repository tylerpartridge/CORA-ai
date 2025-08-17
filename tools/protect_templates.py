#!/usr/bin/env python3
"""
TEMPLATE PROTECTION SYSTEM
Prevents AI scripts from corrupting template files
"""
import os
import hashlib
import json
from datetime import datetime
from pathlib import Path

PROTECTED_FILES = [
    'web/templates/features.html',
    'web/templates/pricing.html', 
    'web/templates/how-it-works.html',
    'web/templates/index.html',
    'web/templates/contact.html',
    'web/templates/reviews.html'
]

CHECKSUM_FILE = 'template_checksums.json'
LOCKFILE = 'TEMPLATE_LOCKFILE.md'

def calculate_checksum(filepath):
    """Calculate SHA256 checksum of a file"""
    with open(filepath, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()

def save_checksums():
    """Save current checksums of protected files"""
    checksums = {}
    for filepath in PROTECTED_FILES:
        if os.path.exists(filepath):
            checksums[filepath] = {
                'checksum': calculate_checksum(filepath),
                'size': os.path.getsize(filepath),
                'timestamp': datetime.now().isoformat()
            }
            print(f"[OK] Protected: {filepath} ({checksums[filepath]['size']} bytes)")
    
    with open(CHECKSUM_FILE, 'w') as f:
        json.dump(checksums, f, indent=2)
    
    print(f"\n[SAVED] Checksums saved to {CHECKSUM_FILE}")
    return checksums

def verify_integrity():
    """Verify files haven't been corrupted"""
    if not os.path.exists(CHECKSUM_FILE):
        print("[WARNING] No checksums found. Creating initial checksums...")
        save_checksums()
        return True
    
    with open(CHECKSUM_FILE, 'r') as f:
        saved_checksums = json.load(f)
    
    all_good = True
    for filepath, data in saved_checksums.items():
        if os.path.exists(filepath):
            current_checksum = calculate_checksum(filepath)
            current_size = os.path.getsize(filepath)
            
            if current_checksum != data['checksum']:
                print(f"[CORRUPTED] {filepath}")
                print(f"   Expected size: {data['size']} bytes")
                print(f"   Current size: {current_size} bytes")
                print(f"   Last good: {data['timestamp']}")
                all_good = False
            else:
                print(f"[OK] {filepath}")
    
    return all_good

def create_lockfile():
    """Create lockfile to warn other AIs"""
    if os.path.exists(LOCKFILE):
        print(f"[LOCKED] Lockfile already exists")
        return
    
    with open(LOCKFILE, 'w') as f:
        f.write(f"""# TEMPLATES PROTECTED
        
**Protected by**: Template Protection System
**Date**: {datetime.now().isoformat()}

## DO NOT MODIFY PROTECTED TEMPLATES

The template files are protected by checksum verification.
Any modification will be detected and reported.

## Protected Files:
{chr(10).join(['- ' + f for f in PROTECTED_FILES])}

## To make changes:
1. Disable protection with: python tools/protect_templates.py --disable
2. Make your changes
3. Re-enable with: python tools/protect_templates.py --enable
""")
    print(f"[LOCKED] Lockfile created")

if __name__ == "__main__":
    import sys
    
    print("=" * 50)
    print("TEMPLATE PROTECTION SYSTEM")
    print("=" * 50)
    
    if '--disable' in sys.argv:
        if os.path.exists(LOCKFILE):
            os.remove(LOCKFILE)
            print("[UNLOCKED] Protection disabled")
    elif '--verify' in sys.argv:
        if verify_integrity():
            print("\n[SUCCESS] All templates intact")
        else:
            print("\n[ERROR] TEMPLATE CORRUPTION DETECTED!")
            print("Run recovery script or restore from backups")
    else:
        # Default: enable protection
        save_checksums()
        create_lockfile()
        print("\n[PROTECTED] Template protection enabled")