#!/usr/bin/env python3
"""
Test authentication and database connection
"""

import sys
from pathlib import Path
# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
# Fix import paths


import requests

BASE_URL = "http://localhost:8080"

print("=== Testing CORA Authentication System ===\n")

# 1. Test if server is responding
print("1. Testing server connection...")
try:
    response = requests.get(f"{BASE_URL}/")
    print(f"   [OK] Server responding: {response.status_code}")
except Exception as e:
    print(f"   [ERROR] Server not responding: {e}")
    exit(1)

# 2. Test login endpoint exists
print("\n2. Testing login endpoint...")
try:
    response = requests.post(f"{BASE_URL}/api/auth/login", 
                           data={"username": "test", "password": "test"})
    print(f"   [OK] Login endpoint exists: {response.status_code}")
    if response.status_code != 200:
        print(f"   Response: {response.text[:200]}")
except Exception as e:
    print(f"   [ERROR] Login endpoint error: {e}")

# 3. Test register endpoint
print("\n3. Testing register endpoint...")
try:
    response = requests.get(f"{BASE_URL}/api/auth/register")
    print(f"   Register endpoint: {response.status_code}")
except Exception as e:
    print(f"   [ERROR] Register endpoint error: {e}")

# 4. Check if we can access login page
print("\n4. Testing login page...")
try:
    response = requests.get(f"{BASE_URL}/login")
    if response.status_code == 200:
        print("   [OK] Login page accessible")
        if "login" in response.text.lower():
            print("   [OK] Login form found")
        else:
            print("   [WARNING] Login form might be missing")
    else:
        print(f"   [ERROR] Login page returned: {response.status_code}")
except Exception as e:
    print(f"   [ERROR] Login page error: {e}")

print("\n=== Diagnosis ===")
print("If all tests passed but you still can't login:")
print("1. The database might not have any users")
print("2. The password requirements might be strict")
print("3. There might be a CORS or session issue")
print("\nTry accessing the database directly to check for users.")