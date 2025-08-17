#!/usr/bin/env python3
"""
Quick health check for CORA system
Run this to verify critical components are intact
"""

import os
import sys

def check_file_size(filepath, min_size, description):
    """Check if a file exists and meets minimum size requirement"""
    # Try both paths for Windows/WSL compatibility
    if os.path.exists(filepath):
        full_path = filepath
    else:
        full_path = f"/mnt/host/c/CORA/{filepath}"
    if not os.path.exists(full_path):
        return f"[MISSING] {description} ({filepath})"
    
    size = os.path.getsize(full_path)
    size_kb = size / 1024
    
    if size < min_size:
        return f"[SMALL] {description} is {size_kb:.1f}KB, expected >{min_size/1024:.0f}KB"
    
    return f"[OK] {description} ({size_kb:.1f}KB)"

def main():
    print("\nCORA HEALTH CHECK\n" + "="*50)
    
    # Critical pages with expected minimum sizes (in bytes)
    critical_pages = [
        ("web/templates/index.html", 180000, "Landing page"),
        ("web/templates/features.html", 100000, "Features page"),
        ("web/templates/dashboard.html", 20000, "Dashboard"),
        ("web/templates/pricing.html", 90000, "Pricing page"),
        ("web/templates/login.html", 15000, "Login page"),
        ("web/templates/signup.html", 20000, "Signup page"),
    ]
    
    print("\nCritical Pages:")
    issues = 0
    for filepath, min_size, description in critical_pages:
        result = check_file_size(filepath, min_size, description)
        print(f"  {result}")
        if "MISSING" in result or "SMALL" in result:
            issues += 1
    
    # Summary
    print("\n" + "="*50)
    if issues == 0:
        print("OK: SYSTEM HEALTHY - All checks passed!")
    else:
        print(f"WARNING: ISSUES FOUND: {issues} problems need attention")
        sys.exit(1)

if __name__ == "__main__":
    main()