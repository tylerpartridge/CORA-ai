#!/usr/bin/env python3
"""
API Endpoint Testing Script
Tests critical API endpoints that frontend depends on
"""

import requests
import json
import sys

# Base URL for local testing
BASE_URL = "http://localhost:8000"

def test_endpoint(method, path, data=None, headers=None):
    """Test a single endpoint"""
    try:
        url = f"{BASE_URL}{path}"
        
        if method == "GET":
            response = requests.get(url, headers=headers, timeout=5)
        elif method == "POST":
            response = requests.post(url, json=data, headers=headers, timeout=5)
        else:
            return False, f"Unsupported method: {method}"
            
        return response.status_code, response.text[:200]
    except requests.exceptions.ConnectionError:
        return None, "Server not running on port 8000"
    except requests.exceptions.Timeout:
        return None, "Request timed out"
    except Exception as e:
        return None, str(e)

def main():
    print("\n" + "="*50)
    print("API ENDPOINT TESTING")
    print("="*50 + "\n")
    
    # Define critical endpoints to test
    endpoints = [
        ("GET", "/health", None, "Health check"),
        ("GET", "/api/expenses", None, "List expenses"),
        ("GET", "/api/profit-intelligence/insights", None, "Get insights"),
        ("POST", "/api/v1/capture-email", {"email": "test@example.com"}, "Email capture"),
        ("GET", "/api/auth/status", None, "Auth status"),
    ]
    
    results = []
    for method, path, data, description in endpoints:
        print(f"Testing: {description} ({method} {path})")
        status, response = test_endpoint(method, path, data)
        
        if status is None:
            print(f"  [FAIL] {response}")
            results.append(False)
        elif 200 <= status < 300:
            print(f"  [OK] Status {status}")
            results.append(True)
        elif status == 401:
            print(f"  [INFO] Status {status} - Authentication required")
            results.append(True)  # This is expected for protected endpoints
        elif status == 404:
            print(f"  [WARN] Status {status} - Endpoint not found")
            results.append(False)
        else:
            print(f"  [FAIL] Status {status}")
            results.append(False)
    
    print("\n" + "="*50)
    passed = sum(results)
    total = len(results)
    print(f"API Tests Passed: {passed}/{total}")
    
    if passed == total:
        print("[OK] All API endpoints responsive")
    elif passed > total / 2:
        print("[WARN] Some API endpoints have issues")
    else:
        print("[FAIL] Most API endpoints are failing")
    
    print("="*50 + "\n")

if __name__ == "__main__":
    main()