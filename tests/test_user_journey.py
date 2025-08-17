"""
Integration Tests for Complete User Journey
Tests the full flow: signup -> login -> add expense -> categorize -> export
"""

import sys
from pathlib import Path
# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
# Fix import paths


import pytest
import json
from fastapi.testclient import TestClient
from app import app
from models.user import User
from models.expense import Expense
from services.auth_service import create_access_token

client = TestClient(app)

class TestCompleteUserJourney:
    """Test the complete user journey from signup to export"""
    
    def test_full_user_journey(self):
        """Test complete user journey: signup -> expense -> export"""
        
        # Step 1: User Signup
        signup_data = {
            "email": "testuser@example.com",
            "password": "securepassword123",
            "business_name": "Test Business LLC"
        }
        
        response = client.post("/api/auth/register", json=signup_data)
        assert response.status_code == 201
        user_data = response.json()
        assert user_data["email"] == signup_data["email"]
        assert user_data["business_name"] == signup_data["business_name"]
        user_id = user_data["id"]
        
        # Step 2: User Login
        login_data = {
            "email": signup_data["email"],
            "password": signup_data["password"]
        }
        
        response = client.post("/auth/login", data=login_data)
        assert response.status_code == 200
        login_response = response.json()
        assert "access_token" in login_response
        token = login_response["access_token"]
        
        # Step 3: Access Dashboard
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/dashboard", headers=headers)
        assert response.status_code == 200
        dashboard_data = response.json()
        assert "user" in dashboard_data
        assert "expenses" in dashboard_data
        
        # Step 4: Add First Expense
        expense_data = {
            "amount": 45.67,
            "description": "Office supplies from Staples",
            "category": "Office Supplies",
            "date": "2025-01-15",
            "vendor": "Staples",
            "notes": "Paper, pens, and notebooks"
        }
        
        response = client.post("/expenses", json=expense_data, headers=headers)
        assert response.status_code == 201
        expense_response = response.json()
        assert expense_response["amount"] == expense_data["amount"]
        assert expense_response["description"] == expense_data["description"]
        expense_id = expense_response["id"]
        
        # Step 5: View Expense List
        response = client.get("/expenses", headers=headers)
        assert response.status_code == 200
        expenses_list = response.json()
        assert len(expenses_list) == 1
        assert expenses_list[0]["id"] == expense_id
        
        # Step 6: Add Second Expense (Photo Upload Simulation)
        photo_expense_data = {
            "amount": 123.45,
            "description": "Lunch meeting",
            "category": "Meals & Entertainment",
            "date": "2025-01-15",
            "vendor": "Local Restaurant",
            "notes": "Client lunch meeting",
            "photo_url": "https://example.com/receipt.jpg"
        }
        
        response = client.post("/expenses", json=photo_expense_data, headers=headers)
        assert response.status_code == 201
        
        # Step 7: Verify Expense Count
        response = client.get("/expenses", headers=headers)
        assert response.status_code == 200
        expenses_list = response.json()
        assert len(expenses_list) == 2
        
        # Step 8: Test Expense Filtering
        response = client.get("/expenses?category=Office+Supplies", headers=headers)
        assert response.status_code == 200
        filtered_expenses = response.json()
        assert len(filtered_expenses) == 1
        assert filtered_expenses[0]["category"] == "Office Supplies"
        
        # Step 9: Test Expense Search
        response = client.get("/expenses?search=Staples", headers=headers)
        assert response.status_code == 200
        search_results = response.json()
        assert len(search_results) == 1
        assert "Staples" in search_results[0]["vendor"]
        
        # Step 10: Export Expenses
        response = client.get("/expenses/export?format=csv", headers=headers)
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/csv"
        
        # Step 11: Test PDF Export
        response = client.get("/expenses/export?format=pdf", headers=headers)
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/pdf"
        
        # Step 12: Verify Dashboard Summary
        response = client.get("/dashboard", headers=headers)
        assert response.status_code == 200
        dashboard_data = response.json()
        assert "total_expenses" in dashboard_data
        assert "total_amount" in dashboard_data
        assert dashboard_data["total_expenses"] == 2
        assert dashboard_data["total_amount"] == 169.12  # 45.67 + 123.45

class TestUserJourneyErrorHandling:
    """Test error handling throughout the user journey"""
    
    def test_invalid_signup_data(self):
        """Test signup with invalid data"""
        invalid_data = {
            "email": "invalid-email",
            "password": "123",  # Too short
            "business_name": ""
        }
        
        response = client.post("/auth/signup", json=invalid_data)
        assert response.status_code == 422
        
    def test_login_with_wrong_password(self):
        """Test login with incorrect password"""
        # First create user
        signup_data = {
            "email": "testuser2@example.com",
            "password": "correctpassword",
            "business_name": "Test Business"
        }
        client.post("/auth/signup", json=signup_data)
        
        # Try login with wrong password
        login_data = {
            "email": signup_data["email"],
            "password": "wrongpassword"
        }
        
        response = client.post("/auth/login", data=login_data)
        assert response.status_code == 401
        
    def test_expense_creation_without_auth(self):
        """Test creating expense without authentication"""
        expense_data = {
            "amount": 50.00,
            "description": "Test expense",
            "category": "Test"
        }
        
        response = client.post("/expenses", json=expense_data)
        assert response.status_code == 401
        
    def test_invalid_expense_data(self):
        """Test creating expense with invalid data"""
        # First create user and get token
        signup_data = {
            "email": "testuser3@example.com",
            "password": "password123",
            "business_name": "Test Business"
        }
        client.post("/auth/signup", json=signup_data)
        
        login_data = {
            "email": signup_data["email"],
            "password": signup_data["password"]
        }
        response = client.post("/auth/login", data=login_data)
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Try invalid expense
        invalid_expense = {
            "amount": -50.00,  # Negative amount
            "description": "",  # Empty description
            "category": "Invalid Category"
        }
        
        response = client.post("/expenses", json=invalid_expense, headers=headers)
        assert response.status_code == 422

class TestUserJourneyPerformance:
    """Test performance aspects of user journey"""
    
    def test_multiple_expenses_performance(self):
        """Test adding multiple expenses quickly"""
        # Create user
        signup_data = {
            "email": "perftest@example.com",
            "password": "password123",
            "business_name": "Performance Test"
        }
        client.post("/auth/signup", json=signup_data)
        
        login_data = {
            "email": signup_data["email"],
            "password": signup_data["password"]
        }
        response = client.post("/auth/login", data=login_data)
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Add 10 expenses quickly
        for i in range(10):
            expense_data = {
                "amount": 10.00 + i,
                "description": f"Test expense {i}",
                "category": "Test",
                "date": "2025-01-15",
                "vendor": f"Vendor {i}"
            }
            response = client.post("/expenses", json=expense_data, headers=headers)
            assert response.status_code == 201
        
        # Verify all expenses were created
        response = client.get("/expenses", headers=headers)
        assert response.status_code == 200
        expenses = response.json()
        assert len(expenses) == 10

if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 