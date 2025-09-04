#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/services/auth_user.py
🎯 PURPOSE: User creation, update, and password management
🔗 IMPORTS: passlib, models, validation
📤 EXPORTS: User management functions
"""

from datetime import datetime
from typing import Optional
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
import logging
import os

from models import User

# Configure logging
logger = logging.getLogger(__name__)

# Password hashing - Updated to fix bcrypt warning
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=12)

# Import centralized config
from config import config

# Password settings
PASSWORD_MIN_LENGTH = config.PASSWORD_MIN_LENGTH

# Custom exceptions (shared with other auth modules)
class AuthenticationError(Exception):
    """Base authentication exception"""
    pass

class UserAlreadyExistsError(AuthenticationError):
    """Raised when trying to create duplicate user"""
    pass

class InvalidCredentialsError(AuthenticationError):
    """Raised when credentials are invalid"""
    pass


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password for storing in database"""
    return pwd_context.hash(password)


def create_user(db: Session, email: str, password: str, timezone: Optional[str] = "America/New_York", currency: Optional[str] = "USD") -> User:
    """Create new user with comprehensive error handling"""
    try:
        # Import validation here to avoid circular dependency
        from services.auth_validation import validate_user_input
        
        # Validate input
        validate_user_input(email, password)
        
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == email).first()
        if existing_user:
            logger.warning(f"Attempt to create duplicate user: {email}")
            raise UserAlreadyExistsError(f"User with email {email} already exists")
        
        # Hash password
        hashed_password = get_password_hash(password)
        
        # Check if we're in development mode or email service is not configured
        sendgrid_key = os.getenv("SENDGRID_API_KEY", "")
        dev_mode = os.getenv("ENVIRONMENT", "development") == "development"
        
        # In development mode, allow immediate login even with SendGrid configured
        # This helps with testing while still sending verification emails
        if dev_mode:
            # Development mode: allow immediate access
            is_active = "true"
            email_verified = "true"  # Mark as verified for immediate access
            logger.info(f"User {email} created - auto-verified for development mode")
        elif sendgrid_key and sendgrid_key.startswith("SG."):
            # Production with SendGrid: require email verification
            is_active = "false"
            email_verified = "false"
            logger.info(f"User {email} created - email verification required")
        else:
            # No email service: auto-verify
            is_active = "true"
            email_verified = "true"
            logger.info(f"Auto-verifying user {email} (email service not configured)")
        
        # Create user
        db_user = User(
            email=email,
            hashed_password=hashed_password,
            is_active=is_active,
            email_verified=email_verified,
            timezone=timezone,
            currency=currency
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        logger.info(f"New user created: {email}")
        return db_user
        
    except UserAlreadyExistsError:
        # Re-raise user exists errors
        raise
    except ValueError as e:
        # Re-raise validation errors
        raise
    except IntegrityError as e:
        # Handle database integrity errors
        logger.error(f"Database integrity error creating user {email}: {str(e)}")
        db.rollback()
        if "UNIQUE constraint failed" in str(e) or "duplicate key" in str(e).lower():
            raise UserAlreadyExistsError(f"User with email {email} already exists")
        raise AuthenticationError("Failed to create user account")
    except SQLAlchemyError as e:
        # Handle other database errors
        logger.error(f"Database error creating user {email}: {str(e)}")
        db.rollback()
        raise AuthenticationError("Failed to create user account")
    except Exception as e:
        # Handle unexpected errors
        logger.error(f"Unexpected error creating user {email}: {str(e)}")
        db.rollback()
        raise AuthenticationError("Failed to create user account")


def reset_password_with_token(db: Session, token: str, new_password: str) -> bool:
    """Reset user password using valid token"""
    try:
        from models import PasswordResetToken
        from services.auth_validation import validate_password_reset_token
        
        # Validate token and get email
        email = validate_password_reset_token(db, token)
        if not email:
            return False
        
        # Get user
        user = db.query(User).filter(User.email == email).first()
        if not user:
            logger.error(f"User not found for password reset: {email}")
            return False
        
        # Update password
        user.hashed_password = get_password_hash(new_password)
        
        # Mark token as used
        reset_token = db.query(PasswordResetToken).filter(
            PasswordResetToken.token == token
        ).first()
        if reset_token:
            reset_token.used = "true"
        
        db.commit()
        
        logger.info(f"Password reset successfully for {email}")
        return True
        
    except SQLAlchemyError as e:
        logger.error(f"Database error during password reset: {str(e)}")
        db.rollback()
        return False
    except Exception as e:
        logger.error(f"Unexpected error during password reset: {str(e)}")
        db.rollback()
        return False