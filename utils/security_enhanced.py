#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/utils/security_enhanced.py
🎯 PURPOSE: Enhanced security utilities for input validation, SQL injection prevention, and XSS protection
🔗 IMPORTS: re, html, urllib.parse
📤 EXPORTS: SecurityUtils, sanitize_input, validate_sql_safe, prevent_xss
"""

import re
import html
import urllib.parse
from typing import Union, Dict, Any, Optional, List
from utils.error_handler import ValidationException

class SecurityUtils:
    """Enhanced security utilities for CORA application"""
    
    # SQL injection patterns to detect
    SQL_INJECTION_PATTERNS = [
        r"(\b(union|select|insert|update|delete|drop|create|alter|exec|execute|script)\b)",
        r"(\b(or|and)\b\s+\d+\s*[=<>])",
        r"(\b(union|select)\b\s+.*\bfrom\b)",
        r"(\b(union|select)\b\s+.*\bwhere\b)",
        r"(--|#|\/\*|\*\/)",
        r"(\bxp_cmdshell\b|\bsp_executesql\b)",
        r"(\bwaitfor\b\s+delay)",
        r"(\bchar\s*\()",
        r"(\bcast\s*\()",
        r"(\bconvert\s*\()",
        r"(\b@@\w+\b)",
        r"(\b0x[0-9a-fA-F]+\b)",
        r"(\b(union|select)\b\s+.*\binformation_schema\b)",
        r"(\b(union|select)\b\s+.*\bsys\b)",
    ]
    
    # XSS patterns to detect
    XSS_PATTERNS = [
        r"<script[^>]*>.*?</script>",
        r"<iframe[^>]*>.*?</iframe>",
        r"<object[^>]*>.*?</object>",
        r"<embed[^>]*>.*?</embed>",
        r"<form[^>]*>.*?</form>",
        r"<input[^>]*>",
        r"<textarea[^>]*>.*?</textarea>",
        r"<select[^>]*>.*?</select>",
        r"<button[^>]*>.*?</button>",
        r"<link[^>]*>",
        r"<meta[^>]*>",
        r"<style[^>]*>.*?</style>",
        r"javascript:",
        r"vbscript:",
        r"data:",
        r"on\w+\s*=",
        r"expression\s*\(",
        r"eval\s*\(",
        r"setTimeout\s*\(",
        r"setInterval\s*\(",
    ]
    
    @staticmethod
    def sanitize_input(text: str, max_length: int = 1000, allow_html: bool = False) -> str:
        """
        Enhanced input sanitization with multiple security layers
        
        Args:
            text: Input text to sanitize
            max_length: Maximum allowed length
            allow_html: Whether to allow safe HTML tags
            
        Returns:
            Sanitized text
            
        Raises:
            ValidationException: If input contains malicious content
        """
        if not text:
            return ""
        
        # Convert to string if needed
        text = str(text)
        
        # Check for SQL injection patterns
        SecurityUtils._check_sql_injection(text)
        
        # Check for XSS patterns
        SecurityUtils._check_xss_patterns(text)
        
        # Length validation
        if len(text) > max_length:
            raise ValidationException(
                f"Input too long. Maximum {max_length} characters allowed.",
                "input_length"
            )
        
        if allow_html:
            # Basic HTML sanitization (without bleach dependency)
            sanitized = SecurityUtils._sanitize_html_basic(text)
        else:
            # Remove all HTML tags and entities
            sanitized = html.escape(text)
        
        return sanitized.strip()
    
    @staticmethod
    def validate_sql_safe(value: str, field_name: str = "input") -> str:
        """
        Validate that input is safe for SQL operations
        
        Args:
            value: Value to validate
            field_name: Name of the field for error messages
            
        Returns:
            Validated value
            
        Raises:
            ValidationException: If SQL injection detected
        """
        if not value:
            return value
        
        value = str(value)
        
        # Check for SQL injection patterns
        SecurityUtils._check_sql_injection(value, field_name)
        
        # Additional SQL safety checks
        if any(char in value for char in [';', '--', '/*', '*/', 'xp_', 'sp_']):
            raise ValidationException(
                f"Invalid characters detected in {field_name}",
                field_name
            )
        
        return value
    
    @staticmethod
    def prevent_xss(text: str, field_name: str = "input") -> str:
        """
        Prevent XSS attacks in user input
        
        Args:
            text: Text to sanitize
            field_name: Name of the field for error messages
            
        Returns:
            XSS-safe text
            
        Raises:
            ValidationException: If XSS patterns detected
        """
        if not text:
            return text
        
        text = str(text)
        
        # Check for XSS patterns
        SecurityUtils._check_xss_patterns(text, field_name)
        
        # HTML encode the text
        return html.escape(text)
    
    @staticmethod
    def sanitize_url(url: str, allowed_schemes: List[str] = None) -> str:
        """
        Sanitize and validate URLs
        
        Args:
            url: URL to sanitize
            allowed_schemes: List of allowed URL schemes (default: http, https)
            
        Returns:
            Sanitized URL
            
        Raises:
            ValidationException: If URL is invalid or contains malicious content
        """
        if not url:
            return url
        
        if allowed_schemes is None:
            allowed_schemes = ['http', 'https']
        
        # Parse URL
        try:
            parsed = urllib.parse.urlparse(url)
        except Exception:
            raise ValidationException("Invalid URL format", "url")
        
        # Check scheme
        if parsed.scheme not in allowed_schemes:
            raise ValidationException(
                f"URL scheme not allowed. Allowed: {', '.join(allowed_schemes)}",
                "url"
            )
        
        # Check for malicious content in URL
        SecurityUtils._check_sql_injection(url, "url")
        SecurityUtils._check_xss_patterns(url, "url")
        
        return url
    
    @staticmethod
    def validate_file_upload(filename: str, allowed_extensions: List[str] = None) -> str:
        """
        Validate file uploads for security
        
        Args:
            filename: Filename to validate
            allowed_extensions: List of allowed file extensions
            
        Returns:
            Validated filename
            
        Raises:
            ValidationException: If filename is unsafe
        """
        if not filename:
            raise ValidationException("Filename is required", "filename")
        
        if allowed_extensions is None:
            allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.pdf', '.doc', '.docx']
        
        # Check for path traversal
        if '..' in filename or '/' in filename or '\\' in filename:
            raise ValidationException("Invalid filename", "filename")
        
        # Check extension
        if not any(filename.lower().endswith(ext.lower()) for ext in allowed_extensions):
            raise ValidationException(
                f"File type not allowed. Allowed: {', '.join(allowed_extensions)}",
                "filename"
            )
        
        # Check for malicious content
        SecurityUtils._check_sql_injection(filename, "filename")
        SecurityUtils._check_xss_patterns(filename, "filename")
        
        return filename
    
    @staticmethod
    def _check_sql_injection(text: str, field_name: str = "input") -> None:
        """Check for SQL injection patterns"""
        text_lower = text.lower()
        
        for pattern in SecurityUtils.SQL_INJECTION_PATTERNS:
            if re.search(pattern, text_lower, re.IGNORECASE):
                raise ValidationException(
                    f"Potentially unsafe content detected in {field_name}",
                    field_name
                )
    
    @staticmethod
    def _check_xss_patterns(text: str, field_name: str = "input") -> None:
        """Check for XSS patterns"""
        text_lower = text.lower()
        
        for pattern in SecurityUtils.XSS_PATTERNS:
            if re.search(pattern, text_lower, re.IGNORECASE):
                raise ValidationException(
                    f"Potentially unsafe content detected in {field_name}",
                    field_name
                )
    
    @staticmethod
    def _sanitize_html_basic(text: str) -> str:
        """Basic HTML sanitization without external dependencies"""
        # Remove dangerous tags
        dangerous_tags = ['script', 'iframe', 'object', 'embed', 'form', 'input', 'textarea', 'select', 'button', 'link', 'meta', 'style']
        
        for tag in dangerous_tags:
            # Remove opening and closing tags
            text = re.sub(f'<{tag}[^>]*>', '', text, flags=re.IGNORECASE)
            text = re.sub(f'</{tag}>', '', text, flags=re.IGNORECASE)
        
        # Remove dangerous attributes
        dangerous_attrs = [r'on\w+', 'javascript:', 'vbscript:', 'data:', r'expression\s*\(']
        for attr in dangerous_attrs:
            text = re.sub(f'{attr}[^>]*', '', text, flags=re.IGNORECASE)
        
        return text

# Convenience functions for backward compatibility
def sanitize_input(text: str, max_length: int = 1000, allow_html: bool = False) -> str:
    """Enhanced input sanitization"""
    return SecurityUtils.sanitize_input(text, max_length, allow_html)

def validate_sql_safe(value: str, field_name: str = "input") -> str:
    """Validate SQL-safe input"""
    return SecurityUtils.validate_sql_safe(value, field_name)

def prevent_xss(text: str, field_name: str = "input") -> str:
    """Prevent XSS attacks"""
    return SecurityUtils.prevent_xss(text, field_name)

def sanitize_url(url: str, allowed_schemes: List[str] = None) -> str:
    """Sanitize and validate URLs"""
    return SecurityUtils.sanitize_url(url, allowed_schemes)

def validate_file_upload(filename: str, allowed_extensions: List[str] = None) -> str:
    """Validate file uploads"""
    return SecurityUtils.validate_file_upload(filename, allowed_extensions) 