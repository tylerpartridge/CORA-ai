#!/usr/bin/env python
"""Test the referral system and show what's happening"""
import requests
import json

# Test credentials
email = "cpartridge00@gmail.com"
password = "Test12345678!"  # Update this to your actual password if different

print("=" * 60)
print("TESTING CORA REFERRAL SYSTEM")
print("=" * 60)

# Step 1: Login
print("\n1. ATTEMPTING LOGIN...")
login_response = requests.post(
    "http://localhost:8000/api/login",
    json={"email": email, "password": password}
)

if login_response.status_code == 200:
    print(f"   SUCCESS: Login successful!")
    token = login_response.json().get('access_token')
    print(f"   Token received: {token[:20]}..." if token else "   No token in response")
    
    # Step 2: Get referral code
    print("\n2. GETTING REFERRAL CODE...")
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    
    referral_response = requests.get(
        "http://localhost:8000/api/referral/my-code",
        headers=headers
    )
    
    if referral_response.status_code == 200:
        data = referral_response.json()
        print(f"   SUCCESS: Referral code retrieved!")
        print(f"   Your code: {data.get('code', 'NOT FOUND')}")
        print(f"   Your link: {data.get('link', 'NOT FOUND')}")
        print(f"   Successful referrals: {data.get('successful_referrals', 0)}")
    else:
        print(f"   FAILED to get referral code: {referral_response.status_code}")
        print(f"   Response: {referral_response.text[:200]}")
        
else:
    print(f"   FAILED: Login failed with status {login_response.status_code}")
    print(f"   Response: {login_response.text[:200]}")
    print("\n   TROUBLESHOOTING:")
    print("   1. Make sure the password is correct")
    print("   2. Check if the server is running")
    print("   3. Verify the account is active and verified")

print("\n" + "=" * 60)
print("HOW TO USE THE REFERRAL SYSTEM:")
print("=" * 60)
print("1. Login at http://localhost:8000/login")
print("2. Visit http://localhost:8000/referral")
print("3. You should see your unique referral code and link")
print("4. Share the link to get referral credit")
print("\nNOTE: If you see 'undefined' on the page, you're not logged in!")
print("=" * 60)