#!/usr/bin/env python3
"""
Test feedback endpoint
"""

import requests
import json

# Login to get token
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
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Test feedback submission
    feedback_data = {
        "category": "onboarding",
        "message": "The onboarding process was very smooth and intuitive. I love the checklist feature!",
        "rating": 5
    }
    
    print("\nSubmitting feedback...")
    feedback_response = requests.post(
        "http://localhost:8000/api/onboarding/feedback",
        json=feedback_data,
        headers=headers
    )
    
    print(f"Status: {feedback_response.status_code}")
    if feedback_response.status_code == 200:
        data = feedback_response.json()
        print("✅ Feedback submitted successfully!")
        print(f"Feedback ID: {data['id']}")
        print(f"Category: {data['category']}")
        print(f"Rating: {data['rating']}")
        print(f"Message: {data['message'][:50]}...")
    else:
        print(f"❌ Error: {feedback_response.text}")
else:
    print(f"❌ Login failed: {login_response.status_code} - {login_response.text}") 