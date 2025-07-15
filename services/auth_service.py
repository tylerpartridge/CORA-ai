#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/services/auth_service.py
🎯 PURPOSE: Authentication service - connects routes to database
🔗 IMPORTS: passlib, jose, models
📤 EXPORTS: auth functions
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from passlib.context import CryptContext
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
import os
import re
import logging
import secrets

from models import User, PasswordResetToken

# Configure logging
logger = logging.getLogger(__name__)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings
SECRET_KEY = os.getenv("SECRET_KEY", secrets.token_urlsafe(32))
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password reset settings
PASSWORD_RESET_TOKEN_EXPIRE_HOURS = 24

# Validation patterns
EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
PASSWORD_MIN_LENGTH = 8

# Custom exceptions
class AuthenticationError(Exception):
    """Base authentication exception"""
    pass

class InvalidCredentialsError(AuthenticationError):
    """Raised when credentials are invalid"""
    pass

class UserAlreadyExistsError(AuthenticationError):
    """Raised when trying to create duplicate user"""
    pass

class TokenValidationError(AuthenticationError):
    """Raised when token validation fails"""
    pass

class PasswordResetError(AuthenticationError):
    """Raised when password reset fails"""
    pass

class ValidationError(Exception):
    """Input validation exception"""
    def __init__(self, errors: Dict[str, str]):
        self.errors = errors
        super().__init__(str(errors))

# Input validation functions
def validate_email(email: str) -> Dict[str, str]:
    """Validate email format and return errors if any"""
    errors = {}
    
    if not email:
        errors["email"] = "Email is required"
    elif not EMAIL_PATTERN.match(email):
        errors["email"] = "Invalid email format"
    elif len(email) > 255:
        errors["email"] = "Email too long (max 255 characters)"
    
    return errors

def validate_password(password: str, confirm_password: Optional[str] = None) -> Dict[str, str]:
    """Validate password strength and return errors if any"""
    errors = {}
    
    if not password:
        errors["password"] = "Password is required"
    elif len(password) < PASSWORD_MIN_LENGTH:
        errors["password"] = f"Password must be at least {PASSWORD_MIN_LENGTH} characters"
    elif len(password) > 128:
        errors["password"] = "Password too long (max 128 characters)"
    else:
        # Check password complexity
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)
        
        if not (has_upper and has_lower and has_digit):
            errors["password"] = "Password must contain uppercase, lowercase, and numbers"
    
    # Validate confirmation if provided
    if confirm_password is not None and password != confirm_password:
        errors["confirm_password"] = "Passwords do not match"
    
    return errors

def validate_user_input(email: str, password: str, confirm_password: Optional[str] = None) -> None:
    """Validate user registration/login input"""
    errors = {}
    
    # Validate email
    email_errors = validate_email(email)
    if email_errors:
        errors.update(email_errors)
    
    # Validate password
    password_errors = validate_password(password, confirm_password)
    if password_errors:
        errors.update(password_errors)
    
    if errors:
        raise ValidationError(errors)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)

def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    """Authenticate user with email and password with enhanced error handling"""
    try:
        # Validate input
        validate_user_input(email, password)
        
        # Query user
        user = db.query(User).filter(User.email == email).first()
        if not user:
            logger.warning(f"Authentication failed: User not found for email {email}")
            raise InvalidCredentialsError("Invalid email or password")
        
        # Verify password
        if not verify_password(password, user.hashed_password):
            logger.warning(f"Authentication failed: Invalid password for email {email}")
            raise InvalidCredentialsError("Invalid email or password")
        
        # Check if user is active
        if hasattr(user, 'is_active') and user.is_active != "true":
            logger.warning(f"Authentication failed: Inactive user {email}")
            raise AuthenticationError("Account is inactive")
        
        logger.info(f"User {email} authenticated successfully")
        return user
        
    except ValidationError:
        # Re-raise validation errors
        raise
    except InvalidCredentialsError:
        # Re-raise credential errors
        raise
    except SQLAlchemyError as e:
        logger.error(f"Database error during authentication: {str(e)}")
        raise AuthenticationError("Authentication service temporarily unavailable")
    except Exception as e:
        logger.error(f"Unexpected error during authentication: {str(e)}")
        raise AuthenticationError("Authentication failed")

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token with error handling"""
    try:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    except Exception as e:
        logger.error(f"Failed to create access token: {str(e)}")
        raise AuthenticationError("Failed to generate authentication token")

def create_user(db: Session, email: str, password: str) -> User:
    """Create new user with comprehensive error handling"""
    try:
        # Validate input
        validate_user_input(email, password)
        
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == email).first()
        if existing_user:
            logger.warning(f"Attempt to create duplicate user: {email}")
            raise UserAlreadyExistsError(f"User with email {email} already exists")
        
        # Hash password
        hashed_password = get_password_hash(password)
        
        # Create user
        db_user = User(
            email=email,
            hashed_password=hashed_password,
            is_active="true"
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        logger.info(f"New user created: {email}")
        return db_user
        
    except ValidationError:
        # Re-raise validation errors
        raise
    except UserAlreadyExistsError:
        # Re-raise user exists errors
        raise
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Database integrity error creating user: {str(e)}")
        raise UserAlreadyExistsError("User already exists")
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error creating user: {str(e)}")
        raise AuthenticationError("Failed to create user account")
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error creating user: {str(e)}")
        raise AuthenticationError("Failed to create user account")

def verify_token(token: str) -> Optional[str]:
    """Verify JWT token and return user email with enhanced error handling"""
    try:
        if not token:
            raise TokenValidationError("No token provided")
            
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        
        if email is None:
            logger.error("Token missing 'sub' claim")
            raise TokenValidationError("Invalid token structure")
            
        # Validate email format in token
        if not EMAIL_PATTERN.match(email):
            logger.error(f"Invalid email in token: {email}")
            raise TokenValidationError("Invalid token content")
            
        return email
        
    except jwt.ExpiredSignatureError:
        logger.warning("Token has expired")
        raise TokenValidationError("Token has expired")
    except jwt.InvalidTokenError as e:
        logger.warning(f"Invalid token: {str(e)}")
        raise TokenValidationError("Invalid token")
    except JWTError as e:
        logger.error(f"JWT error: {str(e)}")
        raise TokenValidationError("Token validation failed")
    except Exception as e:
        logger.error(f"Unexpected error verifying token: {str(e)}")
        raise TokenValidationError("Token validation failed")

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Get user by email with error handling"""
    try:
        # Validate email format
        email_errors = validate_email(email)
        if email_errors:
            logger.warning(f"Invalid email format for lookup: {email}")
            return None
            
        user = db.query(User).filter(User.email == email).first()
        return user
        
    except SQLAlchemyError as e:
        logger.error(f"Database error getting user by email: {str(e)}")
        raise AuthenticationError("Failed to retrieve user information")
    except Exception as e:
        logger.error(f"Unexpected error getting user by email: {str(e)}")
        raise AuthenticationError("Failed to retrieve user information")

def generate_password_reset_token() -> str:
    """Generate a secure random token for password reset"""
    return secrets.token_urlsafe(32)

def create_password_reset_token(db: Session, email: str) -> Optional[str]:
    """Create a password reset token for the given email"""
    try:
        # Check if user exists
        user = db.query(User).filter(User.email == email).first()
        if not user:
            logger.warning(f"Password reset requested for non-existent email: {email}")
            return None
        
        # Invalidate any existing tokens for this email
        db.query(PasswordResetToken).filter(
            PasswordResetToken.email == email,
            PasswordResetToken.used == "false"
        ).update({"used": "true"})
        
        # Generate new token
        token = generate_password_reset_token()
        expires_at = datetime.utcnow() + timedelta(hours=PASSWORD_RESET_TOKEN_EXPIRE_HOURS)
        
        # Create token record
        reset_token = PasswordResetToken(
            email=email,
            token=token,
            expires_at=expires_at,
            used="false"
        )
        
        db.add(reset_token)
        db.commit()
        
        logger.info(f"Password reset token created for {email}")
        return token
        
    except SQLAlchemyError as e:
        logger.error(f"Database error creating password reset token: {str(e)}")
        db.rollback()
        raise PasswordResetError("Failed to create password reset token")
    except Exception as e:
        logger.error(f"Unexpected error creating password reset token: {str(e)}")
        raise PasswordResetError("Failed to create password reset token")

def validate_password_reset_token(db: Session, token: str) -> Optional[str]:
    """Validate a password reset token and return the associated email"""
    try:
        # Find the token
        reset_token = db.query(PasswordResetToken).filter(
            PasswordResetToken.token == token,
            PasswordResetToken.used == "false"
        ).first()
        
        if not reset_token:
            logger.warning(f"Invalid or used password reset token: {token[:10]}...")
            return None
        
        # Check if token is expired
        if reset_token.expires_at < datetime.utcnow():
            logger.warning(f"Expired password reset token: {token[:10]}...")
            # Mark as used
            reset_token.used = "true"
            db.commit()
            return None
        
        logger.info(f"Valid password reset token for {reset_token.email}")
        return reset_token.email
        
    except SQLAlchemyError as e:
        logger.error(f"Database error validating password reset token: {str(e)}")
        raise PasswordResetError("Failed to validate password reset token")
    except Exception as e:
        logger.error(f"Unexpected error validating password reset token: {str(e)}")
        raise PasswordResetError("Failed to validate password reset token")

def reset_password_with_token(db: Session, token: str, new_password: str) -> bool:
    """Reset password using a valid token"""
    try:
        # Validate the token
        email = validate_password_reset_token(db, token)
        if not email:
            return False
        
        # Validate new password
        validate_user_input(email, new_password)
        
        # Update user password
        user = db.query(User).filter(User.email == email).first()
        if not user:
            logger.error(f"User not found for password reset: {email}")
            return False
        
        # Hash new password
        hashed_password = get_password_hash(new_password)
        user.hashed_password = hashed_password
        
        # Mark token as used
        reset_token = db.query(PasswordResetToken).filter(
            PasswordResetToken.token == token
        ).first()
        if reset_token:
            reset_token.used = "true"
        
        db.commit()
        
        logger.info(f"Password reset successful for {email}")
        return True
        
    except ValidationError:
        # Re-raise validation errors
        raise
    except SQLAlchemyError as e:
        logger.error(f"Database error during password reset: {str(e)}")
        db.rollback()
        raise PasswordResetError("Failed to reset password")
    except Exception as e:
        logger.error(f"Unexpected error during password reset: {str(e)}")
        raise PasswordResetError("Failed to reset password")