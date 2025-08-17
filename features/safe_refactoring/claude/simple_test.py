#!/usr/bin/env python3
"""
Simple test to verify basic functionality
"""

def test_imports():
    """Test that basic imports work"""
    print("[TEST] Import Test")
    print("=" * 50)
    
    try:
        import sys
        print("[OK] sys imported")
        
        import os
        print("[OK] os imported")
        
        import json
        print("[OK] json imported")
        
        from pathlib import Path
        print("[OK] pathlib imported")
        
        print("\n[SUCCESS] All basic imports work!")
        return True
        
    except Exception as e:
        print(f"[ERROR] Import failed: {e}")
        return False

def test_file_access():
    """Test file system access"""
    print("\n[TEST] File Access Test")
    print("=" * 50)
    
    try:
        from pathlib import Path
        
        # Check if key files exist
        files_to_check = [
            "app.py",
            "config.py",
            "requirements.txt",
            "cora.db"
        ]
        
        for filename in files_to_check:
            filepath = Path(filename)
            if filepath.exists():
                print(f"[OK] {filename} exists")
            else:
                print(f"[MISSING] {filename} not found")
        
        print("\n[SUCCESS] File access test complete!")
        return True
        
    except Exception as e:
        print(f"[ERROR] File access failed: {e}")
        return False

def test_environment():
    """Test environment setup"""
    print("\n[TEST] Environment Test")
    print("=" * 50)
    
    import sys
    print(f"Python version: {sys.version}")
    print(f"Python executable: {sys.executable}")
    
    import os
    print(f"Current directory: {os.getcwd()}")
    print(f"Environment: {os.getenv('ENVIRONMENT', 'not set')}")
    
    print("\n[SUCCESS] Environment test complete!")
    return True

if __name__ == "__main__":
    print("CORA Simple Test Suite")
    print("=" * 60)
    
    results = []
    results.append(test_imports())
    results.append(test_file_access())
    results.append(test_environment())
    
    print("\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60)
    
    passed = sum(1 for r in results if r)
    failed = len(results) - passed
    
    print(f"Tests passed: {passed}/{len(results)}")
    
    if failed == 0:
        print("\n[SUCCESS] All tests passed!")
    else:
        print(f"\n[WARNING] {failed} tests failed")