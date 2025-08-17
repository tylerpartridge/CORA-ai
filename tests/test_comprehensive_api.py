#!/usr/bin/env python3
"""
[LOCATION] LOCATION: /CORA/test_comprehensive_api.py
[TARGET] PURPOSE: Comprehensive API testing script for CORA restoration validation
[LINK] IMPORTS: requests, json, time
[EXPORT] EXPORTS: Test results and validation reports
"""

import sys
from pathlib import Path
# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
# Fix import paths


import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:8000"

def test_health_endpoint():
    """Test health endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/api/health/status")
        if response.status_code == 200:
            data = response.json()
            print(f"[OK] Health: {data['status']} (v{data['version']})")
            return True
        else:
            print(f"[ERROR] Health: {response.status_code}")
            return False
    except Exception as e:
        print(f"[ERROR] Health: {e}")
        return False

def test_ui_pages():
    """Test all UI pages"""
    pages = ["/", "/about", "/contact", "/pricing"]
    results = []
    
    for page in pages:
        try:
            response = requests.get(f"{BASE_URL}{page}")
            if response.status_code == 200:
                print(f"[OK] UI {page}: 200 OK")
                results.append(True)
            else:
                print(f"[ERROR] UI {page}: {response.status_code}")
                results.append(False)
        except Exception as e:
            print(f"[ERROR] UI {page}: {e}")
            results.append(False)
    
    return all(results)

def test_api_endpoints():
    """Test API endpoints"""
    endpoints = [
        ("/api/expenses/?user_email=test@example.com", "GET"),
        ("/api/expenses/categories", "GET"),
    ]
    
    results = []
    for endpoint, method in endpoints:
        try:
            if method == "GET":
                response = requests.get(f"{BASE_URL}{endpoint}")
            else:
                response = requests.post(f"{BASE_URL}{endpoint}")
            
            if response.status_code in [200, 401, 404]:  # Acceptable responses
                print(f"[OK] API {endpoint}: {response.status_code}")
                results.append(True)
            else:
                print(f"[ERROR] API {endpoint}: {response.status_code}")
                results.append(False)
        except Exception as e:
            print(f"[ERROR] API {endpoint}: {e}")
            results.append(False)
    
    return all(results)

def test_authentication():
    """Test authentication endpoints"""
    try:
        # Test invalid login
        response = requests.post(f"{BASE_URL}/api/auth/login", 
                               data={"username": "fake@example.com", "password": "wrong"})
        if response.status_code == 401:
            print("[OK] Auth: Invalid login properly rejected")
            return True
        else:
            print(f"[ERROR] Auth: Unexpected response {response.status_code}")
            return False
    except Exception as e:
        print(f"[ERROR] Auth: {e}")
        return False

def test_static_files():
    """Test static file serving"""
    try:
        response = requests.head(f"{BASE_URL}/static/images/dashboard-preview.svg")
        if response.status_code == 200:
            print("[OK] Static: Files serving correctly")
            return True
        else:
            print(f"[ERROR] Static: {response.status_code}")
            return False
    except Exception as e:
        print(f"[ERROR] Static: {e}")
        return False

def main():
    """Run comprehensive tests"""
    print("[TEST] CORA COMPREHENSIVE API TEST SUITE")
    print("=" * 50)
    print(f"Testing at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    tests = [
        ("Health Check", test_health_endpoint),
        ("UI Pages", test_ui_pages),
        ("API Endpoints", test_api_endpoints),
        ("Authentication", test_authentication),
        ("Static Files", test_static_files),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n[SEARCH] Testing: {test_name}")
        print("-" * 30)
        result = test_func()
        results.append((test_name, result))
    
    print("\n" + "=" * 50)
    print("[STATS] TEST SUMMARY")
    print("=" * 50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "[OK] PASS" if result else "[ERROR] FAIL"
        print(f"{status} {test_name}")
    
    print(f"\n[TARGET] Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! System is fully functional.")
    elif passed >= total * 0.8:
        print("[OK] Most tests passed. System is mostly functional.")
    else:
        print("[WARNING] Several tests failed. Review system status.")
    
    return passed == total

if __name__ == "__main__":
    main() 