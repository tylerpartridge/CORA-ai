#!/usr/bin/env python3
"""
Test runner for CORA - finds and runs all tests
Shows which ones pass and which fail
"""

import os
import sys
import subprocess
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

def find_test_files():
    """Find all test files in the project"""
    test_files = []
    
    # Check tests directory
    tests_dir = Path("/mnt/host/c/CORA/tests")
    if tests_dir.exists():
        test_files.extend(tests_dir.glob("test_*.py"))
    
    # Check root directory
    root_dir = Path("/mnt/host/c/CORA")
    test_files.extend(root_dir.glob("test_*.py"))
    
    return sorted(test_files)

def run_test(test_file):
    """Run a single test file and return result"""
    try:
        result = subprocess.run(
            [sys.executable, str(test_file)],
            capture_output=True,
            text=True,
            timeout=10,
            env={**os.environ, 'PYTHONIOENCODING': 'utf-8'}
        )
        
        if result.returncode == 0:
            # Check if it actually ran tests or just imported
            if "test" in result.stdout.lower() or "pass" in result.stdout.lower():
                return "PASS", None
            else:
                return "NO_TESTS", "File executed but no tests found"
        else:
            # Extract error message
            error_lines = result.stderr.split('\n') if result.stderr else result.stdout.split('\n')
            for line in error_lines:
                if "Error" in line or "error" in line:
                    return "FAIL", line.strip()
            return "FAIL", "Unknown error"
            
    except subprocess.TimeoutExpired:
        return "TIMEOUT", "Test took too long"
    except Exception as e:
        return "ERROR", str(e)

def main():
    print("CORA Test Runner")
    print("=" * 60)
    
    test_files = find_test_files()
    print(f"Found {len(test_files)} test files\n")
    
    results = {
        "PASS": [],
        "FAIL": [],
        "NO_TESTS": [],
        "TIMEOUT": [],
        "ERROR": []
    }
    
    for test_file in test_files:
        print(f"Running {test_file.name}...", end=" ")
        status, error = run_test(test_file)
        results[status].append((test_file.name, error))
        
        if status == "PASS":
            print("[OK]")
        elif status == "NO_TESTS":
            print("[NO TESTS]")
        else:
            print(f"[{status}]")
            if error:
                print(f"  Error: {error}")
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    print(f"Total tests: {len(test_files)}")
    print(f"Passed: {len(results['PASS'])}")
    print(f"Failed: {len(results['FAIL'])}")
    print(f"No tests: {len(results['NO_TESTS'])}")
    print(f"Timeout: {len(results['TIMEOUT'])}")
    print(f"Error: {len(results['ERROR'])}")
    
    if results['FAIL']:
        print("\nFailed tests:")
        for name, error in results['FAIL']:
            print(f"  - {name}: {error}")
    
    # Common issues
    print("\nCommon Issues Found:")
    issues = set()
    for status in ['FAIL', 'ERROR']:
        for _, error in results[status]:
            if error:
                if "ModuleNotFoundError" in error:
                    issues.add("Import errors - modules not found")
                elif "UnicodeEncodeError" in error:
                    issues.add("Unicode encoding issues")
                elif "ImportError" in error:
                    issues.add("Import errors - circular or missing")
                elif "AttributeError" in error:
                    issues.add("Attribute errors - missing methods/properties")
    
    for issue in issues:
        print(f"  - {issue}")
    
    return len(results['PASS']), len(results['FAIL'])

if __name__ == "__main__":
    passed, failed = main()
    sys.exit(0 if failed == 0 else 1)