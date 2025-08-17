#!/usr/bin/env python3
"""Simple dashboard authentication test"""

import requests
import json

# Base URL
BASE_URL = "http://localhost:8001"

def test_login_and_dashboard():
    """Test login flow and dashboard access"""
    
    session = requests.Session()
    
    # Test with a known user - create one first
    print("\n1. Creating a new test user...")
    signup_data = {
        "name": "Dashboard Test",
        "email": "dashtest@example.com",  
        "business_name": "Test Construction Co",
        "password": "TestPass123!"
    }
    
    signup_response = session.post(f"{BASE_URL}/api/auth/signup", json=signup_data)
    print(f"Signup status: {signup_response.status_code}")
    
    if signup_response.status_code == 200:
        print("✅ User created successfully")
    elif signup_response.status_code == 400:
        print("User might already exist, trying login...")
    
    # Now try to login
    print("\n2. Testing login...")
    login_data = {
        "email": "dashtest@example.com",
        "password": "TestPass123!"
    }
    
    login_response = session.post(f"{BASE_URL}/api/auth/login", json=login_data)
    print(f"Login status: {login_response.status_code}")
    
    if login_response.status_code == 200:
        print("✅ Login successful!")
        login_result = login_response.json()
        print(f"  Response data: {login_result}")
        print(f"  Cookies received: {session.cookies.get_dict()}")
        
        # Test dashboard endpoints
        print("\n3. Testing dashboard endpoints...")
        endpoints = [
            "/api/dashboard/summary",
            "/api/dashboard/metrics?period=month",
            "/api/dashboard/insights",
            "/api/dashboard/jobs",
            "/api/dashboard/expenses/recent"
        ]
        
        for endpoint in endpoints:
            print(f"\n  Testing {endpoint}...")
            response = session.get(f"{BASE_URL}{endpoint}")
            print(f"    Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                # Show a sample of the data
                if isinstance(data, dict):
                    print(f"    ✅ Success! Keys: {list(data.keys())[:5]}")
                elif isinstance(data, list):
                    print(f"    ✅ Success! {len(data)} items returned")
            else:
                error_text = response.text[:200]
                print(f"    ❌ Error: {error_text}")
                
                # If we get a 401, there's an auth problem
                if response.status_code == 401:
                    print("\n    🔍 Debugging 401 error...")
                    print(f"    Request cookies: {session.cookies.get_dict()}")
                    print(f"    Response headers: {dict(response.headers)}")
                    
        return True
    else:
        print(f"❌ Login failed!")
        print(f"  Status: {login_response.status_code}")
        print(f"  Response: {login_response.text[:500]}")
        return False

if __name__ == "__main__":
    print("="*60)
    print("CORA Dashboard Authentication Test")
    print("="*60)
    
    if test_login_and_dashboard():
        print("\n" + "="*60)
        print("✅ Dashboard authentication test complete!")
        print("="*60)
    else:
        print("\n" + "="*60)  
        print("❌ Dashboard authentication needs investigation")
        print("="*60)