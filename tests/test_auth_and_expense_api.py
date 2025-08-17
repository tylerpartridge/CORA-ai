
import sys
from pathlib import Path
# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

# --- Authentication Tests ---
def test_register_stub():
    response = client.post("/api/auth/register", json={
        "email": "testuser@example.com",
        "password": "testpass123",
        "confirm_password": "testpass123"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "not_implemented" or "Registration system" in data["message"]

def test_login_invalid():
    response = client.post("/api/auth/login", data={
        "username": "fakeuser@example.com",
        "password": "wrongpass"
    })
    assert response.status_code == 401
    assert "Incorrect email or password" in response.text

# --- Expense Tests ---
def test_get_expenses_requires_user_email():
    response = client.get("/api/expenses/")
    assert response.status_code == 422  # Missing required query param

def test_get_expenses_valid_user():
    # This test assumes at least one user with expenses exists in the DB
    # Replace 'testuser@example.com' with a real user if needed
    response = client.get("/api/expenses/?user_email=testuser@example.com")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

# Add more CRUD tests as restoration progresses 