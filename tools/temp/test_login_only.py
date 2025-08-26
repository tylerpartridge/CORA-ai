#!/usr/bin/env python
"""Test login with existing user"""
import requests
import json

def test_login():
    base_url = "http://localhost:8000"
    test_email = "test_8662@example.com"  # User we already created
    test_password = "TestPassword123!"
    
    print(f"Testing login with existing user: {test_email}")
    
    login_data = {
        "email": test_email,
        "password": test_password,
        "remember_me": False
    }
    
    response = requests.post(f"{base_url}/api/auth/login", json=login_data)
    print(f"Login response: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"Success: {result.get('success', False)}")
        print(f"Message: {result.get('message', 'N/A')}")
        if 'access_token' in result:
            print(f"Token received: {result['access_token'][:20]}...")
            return True
    else:
        print(f"Error: {response.text}")
        return False
    
    return False

if __name__ == "__main__":
    success = test_login()
    if success:
        print("\n[SUCCESS] Login working!")
    else:
        print("\n[FAILED] Login not working")