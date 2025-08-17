#!/usr/bin/env python
"""Test the login API endpoint"""

import requests
import json

# Test login endpoint
login_url = "http://localhost:8001/api/auth/login"

# Try some common test credentials
test_credentials = [
    {"email": "test@coratest.com", "password": "TestPassword123!"},
    {"email": "test@coratest.com", "password": "Password123!"},
    {"email": "test@coratest.com", "password": "password123"},
    {"email": "test@coratest.com", "password": "test123"},
]

print("=== TESTING LOGIN ENDPOINT ===")
print(f"URL: {login_url}")
print("-" * 60)

for creds in test_credentials:
    print(f"\nTrying: {creds['email']} with password: {creds['password']}")
    
    try:
        response = requests.post(
            login_url,
            json=creds,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"SUCCESS! Response: {json.dumps(data, indent=2)}")
            break
        else:
            try:
                error_data = response.json()
                print(f"Failed: {error_data.get('error', 'Unknown error')}")
            except:
                print(f"Failed: {response.text}")
                
    except requests.exceptions.ConnectionError:
        print("ERROR: Cannot connect to server. Is it running on port 8001?")
        break
    except Exception as e:
        print(f"ERROR: {e}")

print("\n" + "=" * 60)
print("INSTRUCTIONS FOR MANUAL TESTING:")
print("1. Start the server if not running: python app.py")
print("2. Go to: http://localhost:8001/login")
print("3. Try logging in with one of these accounts:")
print("   - test@coratest.com")
print("   - chris_jones990099@hotmail.com")
print("4. Common passwords to try:")
print("   - TestPassword123!")
print("   - Password123!")
print("   - password123")