#!/usr/bin/env python3
"""Test all CORA endpoints"""

import requests
import json
from datetime import datetime

# Base URL for testing
BASE_URL = "http://127.0.0.1:8002"

def test_endpoint(name, method, endpoint, data=None, files=None):
    """Test a single endpoint"""
    url = f"{BASE_URL}{endpoint}"
    try:
        if method == "GET":
            response = requests.get(url, timeout=5)
        elif method == "POST":
            if files:
                response = requests.post(url, files=files, data=data, timeout=5)
            else:
                response = requests.post(url, data=data, timeout=5)
        
        status = "PASS" if response.status_code < 400 else "FAIL"
        print(f"{status} {name:30} [{method:4}] {endpoint:30} - Status: {response.status_code}")
        
        # Try to print response content
        try:
            if response.headers.get('content-type', '').startswith('application/json'):
                print(f"  Response: {json.dumps(response.json(), indent=2)}")
            else:
                # For HTML responses, just show first 100 chars
                content = response.text[:100].replace('\n', ' ')
                print(f"  Response: {content}...")
        except:
            print(f"  Response: {response.text[:100]}...")
            
        return response.status_code < 400
    except requests.exceptions.ConnectionError:
        print(f"FAIL {name:30} [{method:4}] {endpoint:30} - Connection refused")
        return False
    except requests.exceptions.Timeout:
        print(f"FAIL {name:30} [{method:4}] {endpoint:30} - Timeout")
        return False
    except Exception as e:
        print(f"FAIL {name:30} [{method:4}] {endpoint:30} - Error: {str(e)}")
        return False

def main():
    print("=" * 80)
    print(f"CORA API Endpoint Test - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    # Test endpoints
    results = []
    
    # Basic endpoints
    print("\n[Basic Endpoints]")
    results.append(test_endpoint("Health Check", "GET", "/health"))
    results.append(test_endpoint("Home Page", "GET", "/"))
    results.append(test_endpoint("API Docs", "GET", "/api/docs"))
    results.append(test_endpoint("API Redoc", "GET", "/api/redoc"))
    
    # Email capture
    print("\n[Email Capture]")
    results.append(test_endpoint("Email Capture", "POST", "/api/v1/capture-email", 
                                data={"email": "test@example.com"}))
    
    # Static files
    print("\n[Static Files]")
    results.append(test_endpoint("Robots.txt", "GET", "/static/robots.txt"))
    results.append(test_endpoint("Logo Image", "GET", "/static/images/logos/cora-logo.png"))
    
    # Non-existent endpoints (should 404)
    print("\n[Non-existent Endpoints - Should Return 404]")
    test_endpoint("Login (Not Impl)", "GET", "/login")
    test_endpoint("Dashboard (Not Impl)", "GET", "/dashboard")
    test_endpoint("API Users (Not Impl)", "GET", "/api/v1/users")
    
    # Summary
    print("\n" + "=" * 80)
    working = sum(results)
    total = len(results)
    print(f"Summary: {working}/{total} endpoints working ({working/total*100:.1f}%)")
    print("=" * 80)

if __name__ == "__main__":
    main()