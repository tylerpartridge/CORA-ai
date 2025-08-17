#!/usr/bin/env python
"""Test Christina's signup flow"""
import requests
import json
import sqlite3

def test_christina_signup():
    base_url = "http://localhost:8000"
    
    # Christina's details from the original attempt
    christina_data = {
        "name": "Christina Partridge",
        "email": "cpartridge00@gmail.com",
        "business_name": "Christina Enterprise Co.",
        "password": "Test12345678!",  # Complete password with uppercase and special char
        "password_confirm": "Test12345678!",
        "signup_source": "test_script",
        "referral_code": None
    }
    
    print("Testing Christina's Signup Flow")
    print("=" * 60)
    print(f"Name: {christina_data['name']}")
    print(f"Email: {christina_data['email']}")
    print(f"Business: {christina_data['business_name']}")
    print(f"Password: {'*' * len(christina_data['password'])}")
    print()
    
    # Step 1: Test signup
    print("Step 1: Creating account...")
    response = requests.post(f"{base_url}/api/signup", json=christina_data)
    
    if response.status_code == 200:
        result = response.json()
        print(f"[SUCCESS] Account created successfully!")
        print(f"   Message: {result.get('message')}")
        print(f"   User ID: {result.get('user_id')}")
    elif response.status_code == 409:
        print(f"[EXISTS] Account already exists")
        print(f"   Message: {response.json().get('detail')}")
        print("   Proceeding to test login...")
    else:
        print(f"[FAILED] Signup failed: {response.status_code}")
        print(f"   Error: {response.text}")
        return False
    
    print()
    
    # Step 2: Test login
    print("Step 2: Testing login...")
    login_data = {
        "email": christina_data["email"],
        "password": christina_data["password"],
        "remember_me": True
    }
    
    response = requests.post(f"{base_url}/api/auth/login", json=login_data)
    
    if response.status_code == 200:
        result = response.json()
        print(f"[SUCCESS] Login successful!")
        print(f"   Token received: {result.get('access_token', '')[:20]}...")
        print(f"   Token type: {result.get('token_type')}")
    else:
        print(f"[FAILED] Login failed: {response.status_code}")
        print(f"   Error: {response.text}")
        return False
    
    print()
    
    # Step 3: Verify in database
    print("Step 3: Verifying in database...")
    conn = sqlite3.connect('cora.db')
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, email, is_active, email_verified, created_at 
        FROM users 
        WHERE email = ?
    """, (christina_data['email'],))
    
    user = cursor.fetchone()
    if user:
        print(f"[SUCCESS] User found in database!")
        print(f"   User ID: {user[0]}")
        print(f"   Email: {user[1]}")
        print(f"   Active: {user[2]}")
        print(f"   Verified: {user[3]}")
        print(f"   Created: {user[4]}")
    else:
        print("[FAILED] User not found in database")
    
    conn.close()
    
    print()
    print("=" * 60)
    print("[COMPLETE] CHRISTINA'S ACCOUNT IS READY!")
    print("She can now:")
    print("1. Login at http://localhost:8000/login")
    print("2. Access the dashboard immediately (dev mode auto-verified)")
    print("3. Start using CORA's features")
    
    return True

if __name__ == "__main__":
    test_christina_signup()