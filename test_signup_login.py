#!/usr/bin/env python
"""Test signup and login flow"""
import requests
import json
import time
import random

def test_signup_login_flow():
    base_url = "http://localhost:8000"
    test_email = f"test_{random.randint(1000,9999)}@example.com"
    test_password = "TestPassword123!"
    
    print(f"Testing signup/login flow with email: {test_email}")
    
    # 1. Test signup
    print("\n1. Testing signup...")
    signup_data = {
        "name": "Test User",
        "email": test_email,
        "business_name": "Test Construction Co",
        "password": test_password,
        "password_confirm": test_password,
        "signup_source": "test",
        "referral_code": None
    }
    
    response = requests.post(f"{base_url}/api/signup", json=signup_data)
    print(f"   Signup response: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"   Result: {result.get('message', 'Success')}")
        print(f"   User ID: {result.get('user_id', 'N/A')}")
    else:
        print(f"   Error: {response.text}")
        return False
    
    # 2. Test login
    print("\n2. Testing login...")
    time.sleep(1)  # Small delay
    
    login_data = {
        "email": test_email,
        "password": test_password,
        "remember_me": False
    }
    
    response = requests.post(f"{base_url}/api/auth/login", json=login_data)
    print(f"   Login response: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"   Success: {result.get('success', False)}")
        print(f"   Message: {result.get('message', 'N/A')}")
        if 'access_token' in result:
            print(f"   Token received: {result['access_token'][:20]}...")
            return True
    else:
        print(f"   Error: {response.text}")
        return False
    
    return False

if __name__ == "__main__":
    success = test_signup_login_flow()
    if success:
        print("\n[SUCCESS] Signup and login flow working correctly!")
    else:
        print("\n[FAILED] Signup/login flow has issues")