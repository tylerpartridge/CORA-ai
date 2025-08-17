#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/utils/validation.py
🎯 PURPOSE: Centralized validation utilities and custom validators
🔗 IMPORTS: pydantic, re, datetime, typing
📤 EXPORTS: ValidationError, custom validators, validation utilities
"""

import re
import logging
from datetime import datetime, date
from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, validator, ValidationError, Field
try:
    from pydantic.types import EmailStr
except ImportError:
    from pydantic import EmailStr
try:
    import phonenumbers
    PHONENUMBERS_AVAILABLE = True
except ImportError:
    PHONENUMBERS_AVAILABLE = False

logger = logging.getLogger("cora.validation")

class ValidationError(Exception):
    """Custom validation error with detailed information"""
    def __init__(self, field: str, message: str, code: str = "VALIDATION_ERROR"):
        self.field = field
        self.message = message
        self.code = code
        super().__init__(self.message)

class ValidationUtils:
    """Centralized validation utilities"""
    
    # Common regex patterns
    PATTERNS = {
        'phone': r'^\+?1?\d{9,15}$',
        'zip_code': r'^\d{5}(-\d{4})?$',
        'currency_code': r'^[A-Z]{3}$',
        'business_name': r'^[a-zA-Z0-9\s\-\.&,]+$',
        'job_id': r'^[A-Z0-9\-_]+$',
        'amount': r'^\d+(\.\d{1,2})?$',
        'percentage': r'^\d+(\.\d{1,2})?%?$',
        'url': r'^https?://[^\s/$.?#].[^\s]*$',
        'file_extension': r'\.(jpg|jpeg|png|pdf|doc|docx|xls|xlsx)$'
    }
    
    # Validation limits
    LIMITS = {
        'name_min': 2,
        'name_max': 100,
        'email_max': 254,
        'password_min': 10,
        'password_max': 128,
        'description_max': 1000,
        'amount_max': 999999999,  # $9,999,999.99
        'phone_max': 20,
        'business_name_max': 200,
        'job_name_max': 150,
        'vendor_max': 100,
        'category_max': 50
    }
    
    @staticmethod
    def validate_email(email: str) -> str:
        """Validate and normalize email address"""
        if not email or not isinstance(email, str):
            raise ValidationError("email", "Email is required and must be a string")
        
        email = email.strip().lower()
        
        if len(email) > ValidationUtils.LIMITS['email_max']:
            raise ValidationError("email", f"Email must be {ValidationUtils.LIMITS['email_max']} characters or less")
        
        # Basic email format validation
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            raise ValidationError("email", "Invalid email format")
        
        # Check for common email typos
        domain = email.split('@')[1] if '@' in email else ''
        common_typos = {
            'gmai.com': 'gmail.com',
            'gmial.com': 'gmail.com', 
            'gmail.co': 'gmail.com',
            'gmil.com': 'gmail.com',
            'hotmai.com': 'hotmail.com',
            'hotmal.com': 'hotmail.com',
            'hotmial.com': 'hotmail.com',
            'hotmil.com': 'hotmail.com',
            'yahooo.com': 'yahoo.com',
            'yaho.com': 'yahoo.com',
            'outlok.com': 'outlook.com',
            'outloo.com': 'outlook.com',
            'iclod.com': 'icloud.com',
            'icloud.co': 'icloud.com',
        }
        
        if domain in common_typos:
            suggestion = email.replace(domain, common_typos[domain])
            raise ValidationError("email", f"Did you mean {suggestion}? Common typo detected.")
        
        return email
    
    @staticmethod
    def validate_password(password: str, confirm_password: Optional[str] = None) -> str:
        """Validate password strength and confirmation"""
        if not password or not isinstance(password, str):
            raise ValidationError("password", "Password is required and must be a string")
        
        if len(password) < ValidationUtils.LIMITS['password_min']:
            raise ValidationError("password", f"Password must be at least {ValidationUtils.LIMITS['password_min']} characters")
        
        if len(password) > ValidationUtils.LIMITS['password_max']:
            raise ValidationError("password", f"Password must be {ValidationUtils.LIMITS['password_max']} characters or less")
        
        # Password strength requirements
        if not re.search(r'[A-Z]', password):
            raise ValidationError("password", "Password must contain at least one uppercase letter")
        
        if not re.search(r'[a-z]', password):
            raise ValidationError("password", "Password must contain at least one lowercase letter")
        
        if not re.search(r'\d', password):
            raise ValidationError("password", "Password must contain at least one number")
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise ValidationError("password", "Password must contain at least one special character")
        
        # Check confirmation if provided
        if confirm_password is not None and password != confirm_password:
            raise ValidationError("confirm_password", "Passwords do not match")
        
        return password
    
    @staticmethod
    def validate_phone(phone: str) -> str:
        """Validate and format phone number"""
        if not phone:
            return ""
        
        phone = str(phone).strip()
        
        # Remove all non-digit characters except +
        cleaned = re.sub(r'[^\d+]', '', phone)
        
        if len(cleaned) > ValidationUtils.LIMITS['phone_max']:
            raise ValidationError("phone", f"Phone number must be {ValidationUtils.LIMITS['phone_max']} characters or less")
        
        # Try to parse with phonenumbers library
        try:
            if PHONENUMBERS_AVAILABLE:
                if not cleaned.startswith('+'):
                    # Assume US number if no country code
                    cleaned = '+1' + cleaned
                parsed = phonenumbers.parse(cleaned)
                if not phonenumbers.is_valid_number(parsed):
                    raise ValidationError("phone", "Invalid phone number")
                return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
            else:
                # Fallback when phonenumbers library not available
                raise Exception("Use basic validation")
        except Exception:
            # Fallback to basic validation
            if not re.match(ValidationUtils.PATTERNS['phone'], cleaned):
                raise ValidationError("phone", "Invalid phone number format")
            return cleaned
    
    @staticmethod
    def validate_amount(amount: Union[int, float, str], currency: str = "USD") -> int:
        """Validate and convert amount to cents"""
        if amount is None:
            raise ValidationError("amount", "Amount is required")
        
        try:
            # Convert to float first
            if isinstance(amount, str):
                amount = float(amount.replace('$', '').replace(',', ''))
            else:
                amount = float(amount)
        except (ValueError, TypeError):
            raise ValidationError("amount", "Invalid amount format")
        
        if amount <= 0:
            raise ValidationError("amount", "Amount must be greater than 0")
        
        if amount > ValidationUtils.LIMITS['amount_max']:
            raise ValidationError("amount", f"Amount cannot exceed {ValidationUtils.LIMITS['amount_max']}")
        
        # Convert to cents (integer)
        cents = int(round(amount * 100))
        
        # Validate currency
        if currency and not re.match(ValidationUtils.PATTERNS['currency_code'], currency):
            raise ValidationError("currency", "Invalid currency code")
        
        return cents
    
    @staticmethod
    def validate_business_name(name: str) -> str:
        """Validate business name"""
        if not name or not isinstance(name, str):
            raise ValidationError("business_name", "Business name is required and must be a string")
        
        name = name.strip()
        
        if len(name) < ValidationUtils.LIMITS['name_min']:
            raise ValidationError("business_name", f"Business name must be at least {ValidationUtils.LIMITS['name_min']} characters")
        
        if len(name) > ValidationUtils.LIMITS['business_name_max']:
            raise ValidationError("business_name", f"Business name must be {ValidationUtils.LIMITS['business_name_max']} characters or less")
        
        if not re.match(ValidationUtils.PATTERNS['business_name'], name):
            raise ValidationError("business_name", "Business name contains invalid characters")
        
        return name
    
    @staticmethod
    def validate_job_name(name: str) -> str:
        """Validate job name"""
        if not name:
            return ""
        
        name = str(name).strip()
        
        if len(name) > ValidationUtils.LIMITS['job_name_max']:
            raise ValidationError("job_name", f"Job name must be {ValidationUtils.LIMITS['job_name_max']} characters or less")
        
        return name
    
    @staticmethod
    def validate_vendor(vendor: str) -> str:
        """Validate vendor name"""
        if not vendor:
            return ""
        
        vendor = str(vendor).strip()
        
        if len(vendor) > ValidationUtils.LIMITS['vendor_max']:
            raise ValidationError("vendor", f"Vendor name must be {ValidationUtils.LIMITS['vendor_max']} characters or less")
        
        return vendor
    
    @staticmethod
    def validate_description(description: str, field_name: str = "description") -> str:
        """Validate description text"""
        if not description or not isinstance(description, str):
            raise ValidationError(field_name, f"{field_name.title()} is required and must be a string")
        
        description = description.strip()
        
        if len(description) > ValidationUtils.LIMITS['description_max']:
            raise ValidationError(field_name, f"{field_name.title()} must be {ValidationUtils.LIMITS['description_max']} characters or less")
        
        return description
    
    @staticmethod
    def validate_url(url: str, field_name: str = "url") -> str:
        """Validate URL format"""
        if not url:
            return ""
        
        url = str(url).strip()
        
        if not re.match(ValidationUtils.PATTERNS['url'], url):
            raise ValidationError(field_name, f"Invalid {field_name} format")
        
        return url
    
    @staticmethod
    def validate_file_extension(filename: str, allowed_extensions: List[str] = None) -> str:
        """Validate file extension"""
        if not filename:
            return ""
        
        if allowed_extensions is None:
            allowed_extensions = ['jpg', 'jpeg', 'png', 'pdf', 'doc', 'docx', 'xls', 'xlsx']
        
        filename = str(filename).lower()
        
        if not any(filename.endswith(ext) for ext in allowed_extensions):
            raise ValidationError("file", f"File type not allowed. Allowed types: {', '.join(allowed_extensions)}")
        
        return filename
    
    @staticmethod
    def validate_date_range(start_date: date, end_date: date, field_name: str = "date_range") -> None:
        """Validate date range"""
        if start_date and end_date and start_date > end_date:
            raise ValidationError(field_name, "Start date cannot be after end date")
    
    @staticmethod
    def sanitize_input(text: str, max_length: int = 1000) -> str:
        """Sanitize user input to prevent injection attacks"""
        if not text:
            return ""
        
        # Remove potentially dangerous characters
        sanitized = re.sub(r'[<>"\']', '', str(text))
        
        # Limit length
        if len(sanitized) > max_length:
            sanitized = sanitized[:max_length]
        
        return sanitized.strip()

# Custom Pydantic validators for use in models
def validate_email_field(v: str) -> str:
    """Pydantic validator for email fields"""
    return ValidationUtils.validate_email(v)

def validate_password_field(v: str) -> str:
    """Pydantic validator for password fields"""
    return ValidationUtils.validate_password(v)

def validate_phone_field(v: str) -> str:
    """Pydantic validator for phone fields"""
    return ValidationUtils.validate_phone(v)

def validate_amount_field(v: Union[int, float, str]) -> int:
    """Pydantic validator for amount fields"""
    return ValidationUtils.validate_amount(v)

def validate_business_name_field(v: str) -> str:
    """Pydantic validator for business name fields"""
    return ValidationUtils.validate_business_name(v)

def validate_description_field(v: str) -> str:
    """Pydantic validator for description fields"""
    return ValidationUtils.validate_description(v)

# Base model with common validation
class ValidatedBaseModel(BaseModel):
    """Base model with enhanced validation and error handling"""
    
    class Config:
        validate_assignment = True
        extra = "forbid"  # Reject extra fields
        use_enum_values = True
    
    def __init__(self, **data):
        try:
            super().__init__(**data)
        except Exception as e:
            # Handle both Pydantic ValidationError and our custom ValidationError
            if hasattr(e, 'errors') and callable(e.errors):
                # Pydantic ValidationError
                errors = []
                for error in e.errors():
                    field = error['loc'][0] if error['loc'] else 'unknown'
                    message = error['msg']
                    errors.append(ValidationError(field, message))
                
                if len(errors) == 1:
                    raise errors[0]
                else:
                    # Multiple errors - raise the first one
                    raise errors[0]
            else:
                # Re-raise other exceptions
                raise

# Validation error response model
class ValidationErrorResponse(BaseModel):
    """Standard validation error response"""
    error: str
    field: str
    code: str
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.now)

def format_validation_error(error: ValidationError) -> ValidationErrorResponse:
    """Format validation error for API response"""
    return ValidationErrorResponse(
        error=error.message,
        field=error.field,
        code=error.code,
        details={"field": error.field, "message": error.message}
    )

# Module-level exports for direct import
validate_email = ValidationUtils.validate_email
validate_password = ValidationUtils.validate_password
validate_phone = ValidationUtils.validate_phone
validate_amount = ValidationUtils.validate_amount
validate_business_name = ValidationUtils.validate_business_name
validate_job_name = ValidationUtils.validate_job_name
validate_vendor = ValidationUtils.validate_vendor
validate_description = ValidationUtils.validate_description
validate_url = ValidationUtils.validate_url
validate_file_extension = ValidationUtils.validate_file_extension
validate_date_range = ValidationUtils.validate_date_range
sanitize_input = ValidationUtils.sanitize_input 