#!/usr/bin/env python3
"""
Create a test user for onboarding testing
"""

import requests
import json

# Register a new test user
register_data = {
    "email": "onboarding@test.com",
    "password": "Test123!",
    "confirm_password": "Test123!",
    "first_name": "Test",
    "last_name": "User"
}

print("Registering new test user...")
response = requests.post(
    "http://localhost:8000/api/auth/register",
    json=register_data,
    headers={"Content-Type": "application/json"}
)

if response.status_code == 200:
    print("✅ User registered successfully!")
    
    # Now login to get token
    login_data = {
        "username": "onboarding@test.com",
        "password": "Test123!"
    }
    
    print("Logging in...")
    login_response = requests.post(
        "http://localhost:8000/api/auth/login",
        data=login_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    if login_response.status_code == 200:
        token_data = login_response.json()
        token = token_data.get("access_token")
        print(f"✅ Login successful, token: {token[:20]}...")
        
        # Test onboarding checklist
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        print("\nTesting onboarding checklist...")
        checklist_response = requests.get(
            "http://localhost:8000/api/onboarding/checklist",
            headers=headers
        )
        
        print(f"Status: {checklist_response.status_code}")
        if checklist_response.status_code == 200:
            data = checklist_response.json()
            print("✅ Onboarding checklist working!")
            print(f"User: {data['user_email']}")
            print(f"Progress: {data['completed_count']}/{data['total_count']} ({data['progress_percentage']:.1f}%)")
            print(f"Complete: {data['is_complete']}")
            print(f"Steps: {len(data['steps'])}")
        else:
            print(f"❌ Error: {checklist_response.text}")
    else:
        print(f"❌ Login failed: {login_response.status_code} - {login_response.text}")
else:
    print(f"❌ Registration failed: {response.status_code} - {response.text}") 