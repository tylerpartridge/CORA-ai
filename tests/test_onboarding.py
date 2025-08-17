#!/usr/bin/env python3
"""
Test script for onboarding endpoints
"""

import sys
from pathlib import Path
# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
# Fix import paths


import requests
import json

# Test login to get fresh token
login_data = {
    "username": "test2@example.com",
    "password": "TestPassword123"
}

print("Logging in...")
response = requests.post(
    "http://localhost:8000/api/auth/login",
    data=login_data,
    headers={"Content-Type": "application/x-www-form-urlencoded"}
)

if response.status_code == 200:
    token_data = response.json()
    token = token_data.get("access_token")
    print(f"[OK] Login successful, token: {token[:20]}...")
    
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
        print("[OK] Onboarding checklist working!")
        print(f"User: {data['user_email']}")
        print(f"Progress: {data['completed_count']}/{data['total_count']} ({data['progress_percentage']:.1f}%)")
        print(f"Complete: {data['is_complete']}")
    else:
        print(f"[ERROR] Error: {checklist_response.text}")
else:
    print(f"[ERROR] Login failed: {response.status_code} - {response.text}") 