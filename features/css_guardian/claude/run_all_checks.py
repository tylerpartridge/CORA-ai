#!/usr/bin/env python3
"""
CSS Guardian - Complete Check Suite
Runs all CSS health checks to prevent another navbar incident
"""

import sys
import subprocess
from pathlib import Path

def run_check(name, command):
    """Run a check and report results"""
    print(f"\n{'='*60}")
    print(f"Running: {name}")
    print('='*60)
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print("Errors:", result.stderr)
        return result.returncode == 0
    except Exception as e:
        print(f"Error running {name}: {e}")
        return False

def main():
    """Run all CSS Guardian checks"""
    print("\n" + "="*70)
    print(" CSS GUARDIAN - COMPLETE SYSTEM CHECK ".center(70))
    print("="*70)
    print("\nPreventing CSS conflicts since the Great Navbar Incident of 2025-08-12")
    
    checks = [
        ("CSS Conflict Detector", "python features/css_guardian/claude/css_conflict_detector.py"),
        ("JavaScript Style Monitor", "python features/css_guardian/claude/js_style_monitor.py"),
        ("Pre-commit CSS Check", "bash features/css_guardian/claude/pre_commit_css_check.sh"),
        ("Navbar Consistency Check", "python check_nav.py"),
    ]
    
    results = {}
    for name, command in checks:
        # Check if script exists before running
        script_path = command.split()[-1]
        if Path(script_path).exists():
            results[name] = run_check(name, command)
        else:
            print(f"\nSkipping {name} - script not found: {script_path}")
            results[name] = None
    
    # Summary
    print("\n" + "="*70)
    print(" SUMMARY ".center(70))
    print("="*70)
    
    passed = sum(1 for r in results.values() if r is True)
    failed = sum(1 for r in results.values() if r is False)
    skipped = sum(1 for r in results.values() if r is None)
    
    for name, result in results.items():
        if result is True:
            status = "✅ PASSED"
        elif result is False:
            status = "❌ FAILED"
        else:
            status = "⏭️ SKIPPED"
        print(f"{name}: {status}")
    
    print(f"\nTotal: {passed} passed, {failed} failed, {skipped} skipped")
    
    if failed > 0:
        print("\n⚠️ CSS ISSUES DETECTED - Please resolve before deploying")
        print("\nLessons from the Navbar Incident:")
        print("1. Single source of truth prevents conflicts")
        print("2. px units are immune to zoom interference")
        print("3. JavaScript can override any CSS")
        print("4. Multiple causes need multiple fixes")
        return 1
    else:
        print("\n✅ ALL CSS CHECKS PASSED - System is healthy!")
        print("\nThe navbar incident will never happen again! 🛡️")
        return 0

if __name__ == "__main__":
    sys.exit(main())