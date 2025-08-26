#!/usr/bin/env python
"""Test SendGrid email sending"""
import os
from dotenv import load_dotenv
import requests

# Load environment variables
load_dotenv()

SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY", "")
FROM_EMAIL = os.getenv("FROM_EMAIL", "noreply@coraai.tech")

print("Testing SendGrid configuration...")
print(f"API Key found: {'Yes' if SENDGRID_API_KEY else 'No'}")
print(f"API Key starts with 'SG.': {'Yes' if SENDGRID_API_KEY.startswith('SG.') else 'No'}")
print(f"FROM_EMAIL: {FROM_EMAIL}")

# Test API key validity
if SENDGRID_API_KEY:
    print("\nTesting API key validity...")
    response = requests.get(
        "https://api.sendgrid.com/v3/user/profile",
        headers={
            "Authorization": f"Bearer {SENDGRID_API_KEY}",
            "Content-Type": "application/json"
        }
    )
    
    if response.status_code == 200:
        print("[OK] API Key is valid!")
        profile = response.json()
        print(f"  Account type: {profile.get('type', 'Unknown')}")
        print(f"  Email: {profile.get('email', 'Unknown')}")
    elif response.status_code == 401:
        print("[FAIL] API Key is invalid or expired")
    else:
        print(f"[FAIL] Unexpected response: {response.status_code}")
        print(f"  Response: {response.text}")
else:
    print("[FAIL] No SendGrid API key found in environment")

# Test if we can send (without actually sending)
print("\nEmail service configuration:")
print(f"  Would send from: {FROM_EMAIL}")
print(f"  Email verification would be: {'REQUIRED' if SENDGRID_API_KEY else 'DISABLED (auto-verify)'}")