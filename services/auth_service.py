#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/services/auth_service.py
🎯 PURPOSE: Authentication service facade - orchestrates auth modules
🔗 IMPORTS: auth_user, auth_tokens, auth_repository, auth_validation
📤 EXPORTS: All auth functions (backward compatibility)
"""

import warnings
import logging

# Suppress bcrypt version warning - Comprehensive approach
warnings.filterwarnings("ignore", message=".*error reading bcrypt version.*", category=UserWarning)
warnings.filterwarnings("ignore", message=".*trapped.*", category=UserWarning)
warnings.filterwarnings("ignore", message=".*bcrypt.*", category=UserWarning)

# Suppress passlib bcrypt warnings
logging.getLogger("passlib.handlers.bcrypt").setLevel(logging.ERROR)

# Configure logging
logger = logging.getLogger(__name__)

# =============================================================================
# Re-export all functions from split modules for backward compatibility
# =============================================================================

# User management functions from auth_user.py
from services.auth_user import (
    verify_password,
    get_password_hash,
    create_user,
    reset_password_with_token,
    # Exception classes
    AuthenticationError,
    UserAlreadyExistsError,
    InvalidCredentialsError
)

# Token management functions from auth_tokens.py
from services.auth_tokens import (
    create_access_token,
    verify_token,
    generate_password_reset_token,
    create_password_reset_token,
    create_email_verification_token,
    verify_email_token,
    # Exception classes
    TokenValidationError,
    PasswordResetError
)

# Database operations from auth_repository.py
from services.auth_repository import (
    get_user_by_email,
    authenticate_user,
    validate_password_reset_token
)

# Validation functions from auth_validation.py
from services.auth_validation import (
    validate_email,
    validate_password,
    validate_user_input,
    ValidationError
)

# =============================================================================
# Legacy imports for backward compatibility
# =============================================================================

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from passlib.context import CryptContext
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
import os
import re
import secrets

from models import User, PasswordResetToken, EmailVerificationToken

# Import centralized config
from config import config

# Legacy configuration exports (some code might reference these directly)
SECRET_KEY = config.SECRET_KEY or config.get_secure_fallback("SECRET_KEY")
ALGORITHM = config.JWT_ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = config.ACCESS_TOKEN_EXPIRE_MINUTES
PASSWORD_RESET_TOKEN_EXPIRE_HOURS = config.PASSWORD_RESET_TOKEN_EXPIRE_HOURS

# Legacy validation patterns
EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
PASSWORD_MIN_LENGTH = config.PASSWORD_MIN_LENGTH

# Legacy password context (some tests might use this directly)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=12)

# =============================================================================
# Module information
# =============================================================================

__all__ = [
    # User management
    'verify_password',
    'get_password_hash',
    'create_user',
    'reset_password_with_token',
    
    # Token management
    'create_access_token',
    'verify_token',
    'generate_password_reset_token',
    'create_password_reset_token',
    'create_email_verification_token',
    'verify_email_token',
    
    # Database operations
    'get_user_by_email',
    'authenticate_user',
    'validate_password_reset_token',
    
    # Validation
    'validate_email',
    'validate_password',
    'validate_user_input',
    
    # Exception classes
    'AuthenticationError',
    'UserAlreadyExistsError',
    'InvalidCredentialsError',
    'TokenValidationError',
    'PasswordResetError',
    'ValidationError',
    
    # Legacy exports
    'pwd_context',
    'SECRET_KEY',
    'ALGORITHM',
    'ACCESS_TOKEN_EXPIRE_MINUTES',
    'PASSWORD_RESET_TOKEN_EXPIRE_HOURS',
    'EMAIL_PATTERN',
    'PASSWORD_MIN_LENGTH'
]

# Log module initialization
logger.info("Auth service facade loaded - using split module architecture")