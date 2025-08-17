"""
Comprehensive Authentication Tests
Tests for registration, login, logout, password reset, and JWT tokens
"""

import sys
from pathlib import Path
# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
# Fix import paths


import pytest
from datetime import datetime, timedelta
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
import jwt

from services.auth_service import create_access_token, verify_password, get_password_hash
from models import User


class TestRegistration:
    """Test user registration functionality"""
    
    @pytest.mark.auth
    def test_register_success(self, client: TestClient, test_db: Session):
        """Test successful user registration"""
        response = client.post(
            "/api/auth/register",
            json={
                "email": "newuser@example.com",
                "password": "SecurePass123!",
                "company_name": "New Construction Co",
                "full_name": "New User"
            }
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["email"] == "newuser@example.com"
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        
        # Verify user in database
        user = test_db.query(User).filter(User.email == "newuser@example.com").first()
        assert user is not None
        assert user.company_name == "New Construction Co"
        assert user.is_active is True
    
    @pytest.mark.auth
    def test_register_duplicate_email(self, client: TestClient, test_user: dict):
        """Test registration with existing email"""
        response = client.post(
            "/api/auth/register",
            json={
                "email": test_user["user"].email,
                "password": "AnotherPass123!",
                "company_name": "Another Co",
                "full_name": "Another User"
            }
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "already registered" in response.json()["detail"].lower()
    
    @pytest.mark.auth
    @pytest.mark.parametrize("invalid_email", [
        "notanemail",
        "@example.com",
        "user@",
        "user@.com",
        "",
        "user space@example.com"
    ])
    def test_register_invalid_email(self, client: TestClient, invalid_email: str):
        """Test registration with invalid email formats"""
        response = client.post(
            "/api/auth/register",
            json={
                "email": invalid_email,
                "password": "ValidPass123!",
                "company_name": "Test Co",
                "full_name": "Test User"
            }
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    @pytest.mark.auth
    @pytest.mark.parametrize("weak_password", [
        "short",           # Too short
        "NoNumbers!",      # No numbers
        "nouppercase123!", # No uppercase
        "NOLOWERCASE123!", # No lowercase
        "NoSpecialChar123" # No special characters
    ])
    def test_register_weak_password(self, client: TestClient, weak_password: str):
        """Test registration with weak passwords"""
        response = client.post(
            "/api/auth/register",
            json={
                "email": "user@example.com",
                "password": weak_password,
                "company_name": "Test Co",
                "full_name": "Test User"
            }
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "password" in response.json()["detail"].lower()


class TestLogin:
    """Test login functionality"""
    
    @pytest.mark.auth
    def test_login_success(self, client: TestClient, test_user: dict):
        """Test successful login"""
        response = client.post(
            "/api/auth/login",
            data={
                "username": test_user["user"].email,
                "password": test_user["password"]
            }
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        
        # Verify token is valid
        token_data = jwt.decode(
            data["access_token"],
            options={"verify_signature": False}
        )
        assert token_data["sub"] == test_user["user"].email
    
    @pytest.mark.auth
    def test_login_wrong_password(self, client: TestClient, test_user: dict):
        """Test login with wrong password"""
        response = client.post(
            "/api/auth/login",
            data={
                "username": test_user["user"].email,
                "password": "WrongPassword123!"
            }
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "incorrect" in response.json()["detail"].lower()
    
    @pytest.mark.auth
    def test_login_nonexistent_user(self, client: TestClient):
        """Test login with non-existent user"""
        response = client.post(
            "/api/auth/login",
            data={
                "username": "nonexistent@example.com",
                "password": "SomePassword123!"
            }
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    @pytest.mark.auth
    def test_login_inactive_user(self, client: TestClient, test_db: Session):
        """Test login with inactive user"""
        # Create inactive user
        user = User(
            email="inactive@example.com",
            hashed_password=get_password_hash("Password123!"),
            company_name="Inactive Co",
            is_active=False
        )
        test_db.add(user)
        test_db.commit()
        
        response = client.post(
            "/api/auth/login",
            data={
                "username": "inactive@example.com",
                "password": "Password123!"
            }
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "inactive" in response.json()["detail"].lower()


class TestProtectedRoutes:
    """Test authentication on protected routes"""
    
    @pytest.mark.auth
    def test_protected_route_with_token(self, authenticated_client: TestClient):
        """Test accessing protected route with valid token"""
        response = authenticated_client.get("/api/users/me")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "email" in data
    
    @pytest.mark.auth
    def test_protected_route_without_token(self, client: TestClient):
        """Test accessing protected route without token"""
        response = client.get("/api/users/me")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "not authenticated" in response.json()["detail"].lower()
    
    @pytest.mark.auth
    def test_protected_route_with_invalid_token(self, client: TestClient):
        """Test accessing protected route with invalid token"""
        client.headers = {"Authorization": "Bearer invalid_token_here"}
        response = client.get("/api/users/me")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    @pytest.mark.auth
    def test_protected_route_with_expired_token(self, client: TestClient):
        """Test accessing protected route with expired token"""
        # Create expired token
        expired_token = create_access_token(
            data={"sub": "test@example.com"},
            expires_delta=timedelta(seconds=-1)
        )
        
        client.headers = {"Authorization": f"Bearer {expired_token}"}
        response = client.get("/api/users/me")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestPasswordReset:
    """Test password reset functionality"""
    
    @pytest.mark.auth
    def test_request_password_reset(self, client: TestClient, test_user: dict):
        """Test requesting password reset"""
        response = client.post(
            "/api/auth/forgot-password",
            json={"email": test_user["user"].email}
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert "email sent" in response.json()["message"].lower()
    
    @pytest.mark.auth
    def test_request_password_reset_nonexistent_user(self, client: TestClient):
        """Test password reset for non-existent user"""
        response = client.post(
            "/api/auth/forgot-password",
            json={"email": "nonexistent@example.com"}
        )
        
        # Should return success to prevent email enumeration
        assert response.status_code == status.HTTP_200_OK
    
    @pytest.mark.auth
    def test_reset_password_with_token(self, client: TestClient, test_user: dict):
        """Test resetting password with valid token"""
        # Create reset token
        reset_token = create_access_token(
            data={"sub": test_user["user"].email, "type": "password_reset"},
            expires_delta=timedelta(hours=1)
        )
        
        response = client.post(
            f"/api/auth/reset-password",
            json={
                "token": reset_token,
                "new_password": "NewSecurePass123!"
            }
        )
        
        assert response.status_code == status.HTTP_200_OK
        
        # Try logging in with new password
        login_response = client.post(
            "/api/auth/login",
            data={
                "username": test_user["user"].email,
                "password": "NewSecurePass123!"
            }
        )
        
        assert login_response.status_code == status.HTTP_200_OK


class TestLogout:
    """Test logout functionality"""
    
    @pytest.mark.auth
    def test_logout(self, authenticated_client: TestClient):
        """Test user logout"""
        response = authenticated_client.post("/api/auth/logout")
        
        assert response.status_code == status.HTTP_200_OK
        assert "logged out" in response.json()["message"].lower()


class TestTokenRefresh:
    """Test token refresh functionality"""
    
    @pytest.mark.auth
    def test_refresh_token(self, authenticated_client: TestClient, test_user: dict):
        """Test refreshing access token"""
        response = authenticated_client.post("/api/auth/refresh")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        
        # Verify new token is different
        assert data["access_token"] != test_user["access_token"]


class TestAccountVerification:
    """Test email verification functionality"""
    
    @pytest.mark.auth
    def test_send_verification_email(self, authenticated_client: TestClient):
        """Test sending verification email"""
        response = authenticated_client.post("/api/auth/send-verification")
        
        assert response.status_code == status.HTTP_200_OK
        assert "verification email sent" in response.json()["message"].lower()
    
    @pytest.mark.auth
    def test_verify_email(self, client: TestClient, test_db: Session):
        """Test email verification with token"""
        # Create unverified user
        user = User(
            email="unverified@example.com",
            hashed_password=get_password_hash("Password123!"),
            company_name="Unverified Co",
            is_verified=False
        )
        test_db.add(user)
        test_db.commit()
        
        # Create verification token
        verify_token = create_access_token(
            data={"sub": user.email, "type": "email_verification"},
            expires_delta=timedelta(hours=24)
        )
        
        response = client.get(f"/api/auth/verify-email?token={verify_token}")
        
        assert response.status_code == status.HTTP_200_OK
        
        # Check user is verified
        test_db.refresh(user)
        assert user.is_verified is True


class TestRateLimiting:
    """Test rate limiting on auth endpoints"""
    
    @pytest.mark.auth
    @pytest.mark.slow
    def test_login_rate_limiting(self, client: TestClient):
        """Test rate limiting on login endpoint"""
        # Make multiple rapid login attempts
        for i in range(10):
            response = client.post(
                "/api/auth/login",
                data={
                    "username": f"user{i}@example.com",
                    "password": "Password123!"
                }
            )
        
        # Should eventually get rate limited
        # Note: This assumes rate limiting is configured
        # Adjust based on your actual rate limit settings
        pass  # Implement based on your rate limiting configuration


class TestSecurityHeaders:
    """Test security headers on auth responses"""
    
    @pytest.mark.auth
    @pytest.mark.security
    def test_security_headers_present(self, client: TestClient):
        """Test that security headers are present"""
        response = client.post(
            "/api/auth/login",
            data={
                "username": "test@example.com",
                "password": "Password123!"
            }
        )
        
        # Check for security headers
        assert "X-Content-Type-Options" in response.headers
        assert response.headers["X-Content-Type-Options"] == "nosniff"
        
        assert "X-Frame-Options" in response.headers
        assert response.headers["X-Frame-Options"] == "DENY"
        
        # CORS headers should be properly configured
        # Add more header checks based on your configuration