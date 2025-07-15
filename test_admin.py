#!/usr/bin/env python3
"""
Test admin endpoints
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
    
    # Test admin stats
    print("\n1. Testing admin stats...")
    stats_response = requests.get(
        "http://localhost:8000/api/admin/stats",
        headers=headers
    )
    
    print(f"Status: {stats_response.status_code}")
    if stats_response.status_code == 200:
        data = stats_response.json()
        print("✅ Admin stats working!")
        print(f"Total Users: {data['total_users']}")
        print(f"Active Users: {data['active_users']}")
        print(f"Total Expenses: {data['total_expenses']}")
        print(f"Feedback Count: {data['feedback_count']}")
    else:
        print(f"❌ Error: {stats_response.text}")
    
    # Test users list
    print("\n2. Testing users list...")
    users_response = requests.get(
        "http://localhost:8000/api/admin/users",
        headers=headers
    )
    
    print(f"Status: {users_response.status_code}")
    if users_response.status_code == 200:
        users = users_response.json()
        print(f"✅ Users list working! Found {len(users)} users")
        for user in users:
            print(f"  - {user['email']} (Active: {user['is_active']})")
    else:
        print(f"❌ Error: {users_response.text}")
    
    # Test feedback list
    print("\n3. Testing feedback list...")
    feedback_response = requests.get(
        "http://localhost:8000/api/admin/feedback",
        headers=headers
    )
    
    print(f"Status: {feedback_response.status_code}")
    if feedback_response.status_code == 200:
        feedback = feedback_response.json()
        print(f"✅ Feedback list working! Found {len(feedback)} feedback items")
        for item in feedback:
            print(f"  - {item['category']}: {item['message'][:50]}...")
    else:
        print(f"❌ Error: {feedback_response.text}")
    
    # Test onboarding stats
    print("\n4. Testing onboarding stats...")
    onboarding_response = requests.get(
        "http://localhost:8000/api/admin/onboarding-stats",
        headers=headers
    )
    
    print(f"Status: {onboarding_response.status_code}")
    if onboarding_response.status_code == 200:
        data = onboarding_response.json()
        print("✅ Onboarding stats working!")
        print(f"Completed: {data['completed_onboarding']}")
        print(f"Pending: {data['pending_onboarding']}")
        print(f"Completion Rate: {data['onboarding_completion_rate']}%")
    else:
        print(f"❌ Error: {onboarding_response.text}")
    
    # Test user details
    print("\n5. Testing user details...")
    user_details_response = requests.get(
        "http://localhost:8000/api/admin/user/onboarding@test.com",
        headers=headers
    )
    
    print(f"Status: {user_details_response.status_code}")
    if user_details_response.status_code == 200:
        data = user_details_response.json()
        print("✅ User details working!")
        print(f"User: {data['user']['email']}")
        print(f"Stats: {data['stats']['expense_count']} expenses, ${data['stats']['total_spent']} total")
    else:
        print(f"❌ Error: {user_details_response.text}")
        
else:
    print(f"❌ Login failed: {login_response.status_code} - {login_response.text}") 