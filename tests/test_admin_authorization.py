#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/tests/test_admin_authorization.py
🎯 PURPOSE: Test admin authorization to ensure proper access control
🔗 IMPORTS: FastAPI test client, auth service
📤 EXPORTS: Admin authorization test results
"""

import sys
from pathlib import Path
# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
# Fix import paths


import os
import sys
import requests
from fastapi.testclient import TestClient

# Add the parent directory to the path to import app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from services.auth_service import create_access_token

def test_admin_authorization():
    """Test admin authorization endpoints"""
    
    client = TestClient(app)
    
    # Test data
    admin_email = os.getenv("ADMIN_EMAIL", "admin@coraai.tech")
    admin_password = os.getenv("ADMIN_PASSWORD", "AdminPassword123!")
    regular_email = "testuser@example.com"
    regular_password = "TestPassword123!"
    
    print("🔒 Testing Admin Authorization...")
    print(f"   Admin: {admin_email}")
    print(f"   Regular: {regular_email}")
    
    # Test 1: Regular user should be denied admin access
    print("\n📋 Test 1: Regular user accessing admin endpoints")
    
    # Create regular user token
    regular_token = create_access_token(data={"sub": regular_email})
    regular_headers = {"Authorization": f"Bearer {regular_token}"}
    
    admin_endpoints = [
        "/api/admin/stats",
        "/api/admin/users", 
        "/api/admin/feedback",
        "/api/admin/onboarding-stats",
        "/api/admin/activity"
    ]
    
    for endpoint in admin_endpoints:
        response = client.get(endpoint, headers=regular_headers)
        if response.status_code == 403:
            print(f"   ✅ {endpoint}: Properly denied (403)")
        else:
            print(f"   ❌ {endpoint}: Should be denied, got {response.status_code}")
    
    # Test 2: Admin user should have access
    print("\n📋 Test 2: Admin user accessing admin endpoints")
    
    # Create admin user token
    admin_token = create_access_token(data={"sub": admin_email})
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    
    for endpoint in admin_endpoints:
        response = client.get(endpoint, headers=admin_headers)
        if response.status_code == 200:
            print(f"   ✅ {endpoint}: Properly allowed (200)")
        else:
            print(f"   ❌ {endpoint}: Should be allowed, got {response.status_code}")
    
    # Test 3: Unauthenticated requests should be denied
    print("\n📋 Test 3: Unauthenticated requests to admin endpoints")
    
    for endpoint in admin_endpoints:
        response = client.get(endpoint)
        if response.status_code == 401:
            print(f"   ✅ {endpoint}: Properly denied (401)")
        else:
            print(f"   ❌ {endpoint}: Should be denied, got {response.status_code}")
    
    # Test 4: Test specific admin functionality
    print("\n📋 Test 4: Testing specific admin functionality")
    
    # Test user details endpoint
    test_user_email = "testuser@example.com"
    user_details_endpoint = f"/api/admin/user/{test_user_email}"
    
    # Regular user should be denied
    response = client.get(user_details_endpoint, headers=regular_headers)
    if response.status_code == 403:
        print(f"   ✅ User details: Regular user properly denied")
    else:
        print(f"   ❌ User details: Regular user should be denied, got {response.status_code}")
    
    # Admin user should have access
    response = client.get(user_details_endpoint, headers=admin_headers)
    if response.status_code == 200:
        print(f"   ✅ User details: Admin user properly allowed")
    else:
        print(f"   ❌ User details: Admin user should be allowed, got {response.status_code}")
    
    print("\n✅ Admin authorization tests complete!")

def test_admin_user_creation():
    """Test admin user creation and verification"""
    
    print("\n👤 Testing Admin User Creation...")
    
    # This would typically test the admin user creation process
    # For now, we'll just verify the admin user exists in the database
    
    from models import get_db, User
    
    db = next(get_db())
    try:
        admin_email = os.getenv("ADMIN_EMAIL", "admin@coraai.tech")
        admin_user = db.query(User).filter(User.email == admin_email).first()
        
        if admin_user and admin_user.is_admin:
            print(f"   ✅ Admin user {admin_email} exists and has admin privileges")
        elif admin_user:
            print(f"   ⚠️  User {admin_email} exists but is not admin")
        else:
            print(f"   ❌ Admin user {admin_email} not found")
            
    except Exception as e:
        print(f"   ❌ Error checking admin user: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    print("🚀 Starting Admin Authorization Tests...")
    
    test_admin_authorization()
    test_admin_user_creation()
    
    print("\n📋 Test Summary:")
    print("   - All admin endpoints should return 403 for regular users")
    print("   - All admin endpoints should return 200 for admin users")
    print("   - All admin endpoints should return 401 for unauthenticated requests")
    print("   - Admin user should exist in database with is_admin=True") 