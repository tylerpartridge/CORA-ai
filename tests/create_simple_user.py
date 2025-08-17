#!/usr/bin/env python3
"""
Simple script to create a test user for dashboard access
"""

import requests
import json

BASE_URL = "http://localhost:8080"

# Register a new user
def create_user():
    """Create a test user via the API"""
    
    user_data = {
        "email": "dashboard@test.com",
        "password": "TestPass123",
        "confirm_password": "TestPass123"
    }
    
    print("Creating user: dashboard@test.com")
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/register", json=user_data)
        
        if response.status_code == 200:
            print("[SUCCESS] User created successfully!")
            print("\nYou can now login with:")
            print("  Email: dashboard@test.com")
            print("  Password: TestPass123")
            return True
        else:
            print(f"[FAILED] Failed to create user: {response.status_code}")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"Error: {e}")
        print("\nMake sure the server is running on port 8080")
        return False

if __name__ == "__main__":
    print("=== Creating Test User for Dashboard ===\n")
    
    if create_user():
        print("\n[SUCCESS] Now go to http://localhost:8080/login")
        print("  and login with the credentials above to see the dashboard.")
    else:
        print("\n[FAILED] Failed to create user. Check if:")
        print("  1. Server is running on port 8080")
        print("  2. Database is initialized")
        print("  3. No user with this email already exists")