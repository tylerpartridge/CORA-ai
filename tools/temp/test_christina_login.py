#!/usr/bin/env python
"""Test Christina's login"""
import requests

def test_christina_login():
    print("Testing Christina's Login")
    print("=" * 60)
    
    login_data = {
        "email": "cpartridge00@gmail.com",
        "password": "Test12345678!",
        "remember_me": True
    }
    
    print(f"Email: {login_data['email']}")
    print(f"Password: {'*' * len(login_data['password'])}")
    print()
    
    response = requests.post("http://localhost:8000/api/auth/login", json=login_data)
    
    if response.status_code == 200:
        result = response.json()
        print("[SUCCESS] Login successful!")
        print(f"  Token: {result.get('access_token', '')[:30]}...")
        print(f"  Type: {result.get('token_type')}")
        print(f"  Expires in: {result.get('expires_in')} seconds")
        print()
        print("Christina can now:")
        print("  1. Access the dashboard at http://localhost:8000/dashboard")
        print("  2. Create expenses, projects, and reports")
        print("  3. Use all CORA features")
        return True
    else:
        print(f"[FAILED] Login failed: {response.status_code}")
        print(f"  Error: {response.text}")
        return False

if __name__ == "__main__":
    test_christina_login()