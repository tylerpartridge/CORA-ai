#!/usr/bin/env python3
"""
Comprehensive CORA system test
"""
import requests
import json
import sys
import time
from urllib.parse import urljoin

BASE_URL = "http://127.0.0.1:8000"

def test_endpoint(method, endpoint, expected_status=200, data=None, headers=None):
    """Test a single endpoint with specified method"""
    url = urljoin(BASE_URL, endpoint)
    try:
        if method.upper() == "GET":
            response = requests.get(url, timeout=10, headers=headers)
        elif method.upper() == "POST":
            response = requests.post(url, json=data, timeout=10, headers=headers)
        else:
            return {"endpoint": endpoint, "success": False, "error": f"Unsupported method: {method}"}
        
        success = response.status_code == expected_status
        return {
            "endpoint": endpoint,
            "method": method,
            "status_code": response.status_code,
            "success": success,
            "response_size": len(response.content),
            "error": None if success else f"Expected {expected_status}, got {response.status_code}"
        }
    except Exception as e:
        return {
            "endpoint": endpoint,
            "method": method,
            "status_code": None,
            "success": False,
            "response_size": 0,
            "error": str(e)
        }

def main():
    """Run comprehensive system tests"""
    print("CORA System Comprehensive Test")
    print("=" * 50)
    
    # Test cases: (method, endpoint, expected_status, description)
    test_cases = [
        # Public pages
        ("GET", "/", 200, "Landing page"),
        ("GET", "/features", 200, "Features page"),
        ("GET", "/pricing", 200, "Pricing page"),
        ("GET", "/how-it-works", 200, "How it works page"),
        ("GET", "/login", 200, "Login page"),
        ("GET", "/signup", 200, "Signup page"),
        
        # API endpoints
        ("GET", "/health", 200, "Health check"),
        ("GET", "/api/status", 200, "Status endpoint"),
        ("GET", "/api/health/detailed", 200, "Detailed health check"),
        
        # Auth endpoints (should return appropriate responses)
        ("GET", "/api/admin/stats", 401, "Admin stats (unauthorized)"),
        ("GET", "/dashboard", 302, "Dashboard redirect"),
        
        # Static files
        ("GET", "/robots.txt", 200, "Robots.txt"),
        
        # API forms (should handle missing data gracefully)
        ("POST", "/api/v1/capture-email", 422, "Email capture without data"),
        ("POST", "/api/contact", 422, "Contact form without data"),
    ]
    
    results = []
    passed = 0
    failed = 0
    
    for method, endpoint, expected_status, description in test_cases:
        print(f"Testing: {description}...")
        result = test_endpoint(method, endpoint, expected_status)
        results.append({**result, "description": description})
        
        if result["success"]:
            print(f"  PASS: {method} {endpoint} -> {result['status_code']}")
            passed += 1
        else:
            print(f"  FAIL: {method} {endpoint} -> {result['status_code']} ({result['error']})")
            failed += 1
    
    print(f"\nTest Summary:")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Total:  {passed + failed}")
    
    if failed == 0:
        print("\nAll tests passed! System is healthy.")
        return 0
    else:
        print(f"\n{failed} tests failed. System needs attention.")
        return 1

if __name__ == "__main__":
    sys.exit(main())