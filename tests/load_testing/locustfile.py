#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/tests/load_testing/locustfile.py
🎯 PURPOSE: Load testing configuration for CORA application
🔗 IMPORTS: Locust, requests, json, random
📤 EXPORTS: UserBehavior class for load testing
"""

import json
import random
import time
import os
from locust import HttpUser, task, between, events
from typing import Dict, Any

class CORAUser(HttpUser):
    """Simulates a real CORA user performing typical actions"""
    
    wait_time = between(1, 3)  # Wait 1-3 seconds between requests
    
    def on_start(self):
        """Setup user session - login and get auth token"""
        self.auth_token = None
        self.user_id = None
        self.expense_categories = []
        
        # Login or register
        if random.choice([True, False]):  # 50% chance to register
            self.register_user()
        else:
            self.login_user()
        
        # Get expense categories
        self.get_expense_categories()
    
    def register_user(self):
        """Register a new user"""
        email = f"testuser{random.randint(1000, 9999)}@loadtest.com"
        password = os.getenv("LOAD_TEST_PASSWORD", "testpassword123")
        
        response = self.client.post("/api/auth/register", json={
            "email": email,
            "password": password,
            "first_name": f"Test{random.randint(1, 100)}",
            "last_name": f"User{random.randint(1, 100)}"
        })
        
        if response.status_code == 200:
            data = response.json()
            self.auth_token = data.get("access_token")
            self.user_id = data.get("user_id")
            print(f"✅ Registered user: {email}")
        else:
            print(f"❌ Registration failed: {response.status_code}")
    
    def login_user(self):
        """Login with existing test user"""
        test_password = os.getenv("LOAD_TEST_PASSWORD", "testpassword123")
        test_users = [
            {"email": "testuser1@loadtest.com", "password": test_password},
            {"email": "testuser2@loadtest.com", "password": test_password},
            {"email": "testuser3@loadtest.com", "password": test_password},
        ]
        
        user = random.choice(test_users)
        response = self.client.post("/api/auth/login", json=user)
        
        if response.status_code == 200:
            data = response.json()
            self.auth_token = data.get("access_token")
            self.user_id = data.get("user_id")
            print(f"✅ Logged in user: {user['email']}")
        else:
            print(f"❌ Login failed: {response.status_code}")
    
    def get_expense_categories(self):
        """Get available expense categories"""
        if not self.auth_token:
            return
        
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        response = self.client.get("/api/expenses/categories", headers=headers)
        
        if response.status_code == 200:
            self.expense_categories = response.json()
    
    @task(3)
    def view_dashboard(self):
        """View dashboard - most common action"""
        if not self.auth_token:
            return
        
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        self.client.get("/dashboard", headers=headers, name="View Dashboard")
    
    @task(2)
    def list_expenses(self):
        """List user expenses"""
        if not self.auth_token:
            return
        
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        params = {
            "page": random.randint(1, 5),
            "limit": random.choice([10, 20, 50])
        }
        self.client.get("/api/expenses", headers=headers, params=params, name="List Expenses")
    
    @task(2)
    def create_expense(self):
        """Create a new expense"""
        if not self.auth_token or not self.expense_categories:
            return
        
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        # Random expense data
        categories = [cat["name"] for cat in self.expense_categories]
        expense_data = {
            "amount": round(random.uniform(10.0, 500.0), 2),
            "description": f"Load test expense {random.randint(1, 1000)}",
            "category": random.choice(categories),
            "date": "2025-01-15",
            "vendor": f"Vendor {random.randint(1, 100)}"
        }
        
        self.client.post("/api/expenses", json=expense_data, headers=headers, name="Create Expense")
    
    @task(1)
    def upload_receipt(self):
        """Upload a receipt (simulated)"""
        if not self.auth_token:
            return
        
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        # Simulate receipt upload with minimal file
        files = {
            'file': ('receipt.jpg', b'fake_image_data', 'image/jpeg')
        }
        
        self.client.post("/api/receipts/upload", files=files, headers=headers, name="Upload Receipt")
    
    @task(1)
    def get_expense_stats(self):
        """Get expense statistics"""
        if not self.auth_token:
            return
        
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        self.client.get("/api/expenses/stats", headers=headers, name="Get Expense Stats")
    
    @task(1)
    def export_expenses(self):
        """Export expenses to CSV"""
        if not self.auth_token:
            return
        
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        params = {"format": "csv"}
        self.client.get("/api/expenses/export", headers=headers, params=params, name="Export Expenses")
    
    @task(1)
    def view_receipt_stats(self):
        """View receipt processing statistics"""
        if not self.auth_token:
            return
        
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        self.client.get("/api/receipts/stats", headers=headers, name="Get Receipt Stats")
    
    @task(1)
    def health_check(self):
        """Health check endpoint"""
        self.client.get("/health", name="Health Check")
    
    @task(1)
    def api_status(self):
        """API status endpoint"""
        self.client.get("/api/status", name="API Status")

class AdminUser(HttpUser):
    """Simulates admin user actions"""
    
    wait_time = between(2, 5)
    
    def on_start(self):
        """Admin login"""
        self.auth_token = None
        self.login_admin()
    
    def login_admin(self):
        """Login as admin"""
        response = self.client.post("/api/auth/login", json={
            "email": "admin@coraai.tech",
            "password": "admin123"
        })
        
        if response.status_code == 200:
            data = response.json()
            self.auth_token = data.get("access_token")
            print("✅ Admin logged in")
    
    @task(2)
    def view_admin_dashboard(self):
        """View admin dashboard"""
        if not self.auth_token:
            return
        
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        self.client.get("/admin", headers=headers, name="Admin Dashboard")
    
    @task(1)
    def get_user_stats(self):
        """Get user statistics"""
        if not self.auth_token:
            return
        
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        self.client.get("/api/admin/users/stats", headers=headers, name="User Stats")
    
    @task(1)
    def get_system_metrics(self):
        """Get system metrics"""
        if not self.auth_token:
            return
        
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        self.client.get("/api/admin/system/metrics", headers=headers, name="System Metrics")

# Event listeners for monitoring
@events.request.add_listener
def my_request_handler(request_type, name, response_time, response_length, response, context, exception, start_time, url, **kwargs):
    """Log request details for analysis"""
    if exception:
        print(f"❌ Request failed: {name} - {exception}")
    elif response.status_code >= 400:
        print(f"⚠️ Request error: {name} - {response.status_code}")

@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Called when test starts"""
    print("🚀 Load test starting...")

@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Called when test stops"""
    print("🏁 Load test completed!") 