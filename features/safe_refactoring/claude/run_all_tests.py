#!/usr/bin/env python3
"""
Run all tests and report which ones pass/fail
"""

import subprocess
import sys
from pathlib import Path
import time

def run_test(test_file):
    """Run a single test file"""
    try:
        result = subprocess.run(
            [sys.executable, str(test_file)],
            capture_output=True,
            text=True,
            timeout=5,
            env={'PYTHONIOENCODING': 'utf-8'}
        )
        
        # Check for success indicators
        output = result.stdout + result.stderr
        
        if "PASSED" in output or "OK" in output or result.returncode == 0:
            if "FAILED" not in output and "ERROR" not in output:
                return "PASS", None
        
        # Look for specific error types
        if "ModuleNotFoundError" in output:
            missing = output.split("'")[1] if "'" in output else "unknown"
            return "IMPORT_ERROR", f"Missing: {missing}"
        elif "AttributeError" in output:
            return "ATTRIBUTE_ERROR", "Attribute missing"
        elif "ConnectionError" in output or "Connection refused" in output:
            return "CONNECTION_ERROR", "Service not running"
        elif "OperationalError" in output:
            return "DB_ERROR", "Database issue"
        elif "AssertionError" in output:
            return "ASSERTION", "Test assertion failed"
        else:
            return "FAIL", "Unknown error"
            
    except subprocess.TimeoutExpired:
        return "TIMEOUT", "Test hung"
    except Exception as e:
        return "CRASH", str(e)

def main():
    print("CORA Comprehensive Test Runner")
    print("=" * 60)
    
    # Find all test files
    test_files = []
    test_files.extend(Path("tests").glob("test_*.py"))
    test_files.extend(Path(".").glob("test_*.py"))
    
    # Filter out some we know won't work
    skip_patterns = ['test_stripe', 'test_quickbooks', 'test_plaid']
    test_files = [f for f in test_files if not any(p in f.name for p in skip_patterns)]
    
    print(f"Running {len(test_files)} test files...\n")
    
    results = {
        "PASS": [],
        "FAIL": [],
        "IMPORT_ERROR": [],
        "ATTRIBUTE_ERROR": [],
        "CONNECTION_ERROR": [],
        "DB_ERROR": [],
        "ASSERTION": [],
        "TIMEOUT": [],
        "CRASH": []
    }
    
    for i, test_file in enumerate(test_files, 1):
        print(f"[{i}/{len(test_files)}] {test_file.name}...", end=" ")
        status, error = run_test(test_file)
        results[status].append((test_file.name, error))
        
        if status == "PASS":
            print("[PASS]")
        else:
            print(f"[{status}]")
            if error and len(error) < 50:
                print(f"      {error}")
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    total = len(test_files)
    passed = len(results["PASS"])
    
    print(f"Total Tests: {total}")
    print(f"Passed: {passed} ({passed/total*100:.1f}%)")
    print(f"Failed: {total - passed} ({(total-passed)/total*100:.1f}%)")
    
    print("\nBreakdown:")
    for status, tests in results.items():
        if tests:
            print(f"  {status}: {len(tests)}")
    
    if results["PASS"]:
        print("\n✅ PASSING TESTS:")
        for name, _ in results["PASS"]:
            print(f"  - {name}")
    
    print("\n❌ TOP ISSUES:")
    issues = {}
    for status in ["IMPORT_ERROR", "CONNECTION_ERROR", "DB_ERROR"]:
        for name, error in results[status]:
            if error:
                key = error.split(":")[0] if ":" in error else error
                if key not in issues:
                    issues[key] = 0
                issues[key] += 1
    
    for issue, count in sorted(issues.items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"  - {issue}: {count} tests")
    
    return passed, total - passed

if __name__ == "__main__":
    passed, failed = main()
    print(f"\n{'='*60}")
    if passed > 0:
        print(f"✅ {passed} tests are working!")
    if failed > 0:
        print(f"🔧 {failed} tests need fixes")
    print("=" * 60)