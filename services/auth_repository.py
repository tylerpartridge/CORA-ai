#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/services/auth_repository.py
🎯 PURPOSE: Database operations for authentication
🔗 IMPORTS: sqlalchemy, models
📤 EXPORTS: Database access functions
"""

from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
import logging

from models import User, PasswordResetToken

# Configure logging
logger = logging.getLogger(__name__)

# Custom exceptions
class AuthenticationError(Exception):
    """Base authentication exception"""
    pass

class InvalidCredentialsError(AuthenticationError):
    """Raised when credentials are invalid"""
    pass


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Get user by email address"""
    try:
        if not email:
            return None
            
        user = db.query(User).filter(User.email == email).first()
        
        if user:
            logger.debug(f"User found for email: {email}")
        else:
            logger.debug(f"No user found for email: {email}")
            
        return user
        
    except SQLAlchemyError as e:
        logger.error(f"Database error getting user by email {email}: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error getting user by email {email}: {str(e)}")
        return None


def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    """Authenticate user with email and password"""
    try:
        # Import here to avoid circular dependency
        from services.auth_user import verify_password
        
        # Log authentication attempt without revealing sensitive info
        logger.info(f"Authentication attempt for user: {email}")
        
        # Get user from database
        user = get_user_by_email(db, email)
        if not user:
            logger.warning(f"Authentication failed - user not found: {email}")
            return None
        
        # Verify password
        if not verify_password(password, user.hashed_password):
            logger.warning(f"Authentication failed - invalid password for: {email}")
            return None
        
        # Check if user is active (SQLite stores booleans as strings)
        if user.is_active != "true":
            logger.warning(f"Authentication failed - inactive user: {email}")
            return None
        
        # Update last login
        try:
            user.last_login = datetime.utcnow()
            db.commit()
        except SQLAlchemyError as e:
            # Don't fail authentication if we can't update last login
            logger.error(f"Failed to update last login for {email}: {str(e)}")
            db.rollback()
        
        logger.info(f"Authentication successful for user: {email}")
        return user
        
    except Exception as e:
        logger.error(f"Unexpected error during authentication for {email}: {str(e)}")
        return None


def validate_password_reset_token(db: Session, token: str) -> Optional[str]:
    """Validate password reset token and return user email if valid"""
    try:
        if not token:
            logger.warning("Password reset validation attempted with no token")
            raise InvalidCredentialsError("No reset token provided")
        
        # Find unused, non-expired token
        reset_token = db.query(PasswordResetToken).filter(
            PasswordResetToken.token == token,
            PasswordResetToken.used == "false",
            PasswordResetToken.expires_at > datetime.utcnow()
        ).first()
        
        if not reset_token:
            logger.warning(f"Invalid or expired password reset token attempted")
            raise InvalidCredentialsError("Invalid or expired reset token")
        
        logger.info(f"Valid password reset token for {reset_token.email}")
        return reset_token.email
        
    except InvalidCredentialsError:
        # Re-raise validation errors
        raise
    except SQLAlchemyError as e:
        logger.error(f"Database error validating password reset token: {str(e)}")
        raise AuthenticationError("Failed to validate reset token")
    except Exception as e:
        logger.error(f"Unexpected error validating password reset token: {str(e)}")
        raise AuthenticationError("Failed to validate reset token")