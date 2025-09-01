#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/utils/filenames.py
🎯 PURPOSE: Standardized filename generation for CSV exports
🔗 IMPORTS: datetime, zoneinfo, re
📤 EXPORTS: generate_filename
"""

import re
from datetime import datetime
from typing import Optional
import logging

logger = logging.getLogger(__name__)


def generate_filename(
    export_type: str, 
    user_email: str, 
    user_timezone: Optional[str] = None,
    when: Optional[datetime] = None
) -> str:
    """
    Generate standardized CSV filename with timezone-aware date.
    
    Format: cora_{type}_{email}_{YYYYMMDD}.csv
    
    Args:
        export_type: Type of export (e.g., 'expenses', 'dashboard', 'report')
        user_email: User's email address (will be sanitized)
        user_timezone: User's timezone string (e.g., 'America/New_York')
        when: Optional datetime to use instead of now()
    
    Returns:
        Standardized filename string
    
    Examples:
        >>> generate_filename('expenses', 'user@example.com', 'America/New_York')
        'cora_expenses_user_at_example.com_20250831.csv'
    """
    # Sanitize export type (alphanumeric and underscores only)
    export_type = re.sub(r'[^a-zA-Z0-9_]', '', export_type).lower()
    if not export_type:
        export_type = 'export'
    
    # Sanitize email: lowercase, @ -> _at_, non-alphanumeric -> -
    sanitized_email = user_email.lower()
    sanitized_email = sanitized_email.replace('@', '_at_')
    # Replace any non [a-z0-9._-] with '-'
    sanitized_email = re.sub(r'[^a-z0-9._-]', '-', sanitized_email)
    # Remove multiple consecutive dashes
    sanitized_email = re.sub(r'-+', '-', sanitized_email)
    # Remove leading/trailing dashes
    sanitized_email = sanitized_email.strip('-')
    
    if not sanitized_email:
        # Fallback if email is completely invalid
        sanitized_email = 'user'
    
    # Get timezone-aware date
    date_str = get_timezone_aware_date(user_timezone, when)
    
    # Construct filename
    filename = f"cora_{export_type}_{sanitized_email}_{date_str}.csv"
    
    return filename


def get_timezone_aware_date(user_timezone: Optional[str] = None, when: Optional[datetime] = None) -> str:
    """
    Get date in YYYYMMDD format using user's timezone.
    
    Args:
        user_timezone: IANA timezone string (e.g., 'America/New_York')
        when: Optional datetime to use instead of now()
    
    Returns:
        Date string in YYYYMMDD format
    """
    try:
        if user_timezone:
            # Try to use the provided timezone
            import zoneinfo
            tz = zoneinfo.ZoneInfo(user_timezone)
            if when:
                # Convert the provided datetime to the user's timezone
                target_dt = when.astimezone(tz) if when.tzinfo else when.replace(tzinfo=tz)
            else:
                target_dt = datetime.now(tz)
        else:
            # Fallback to UTC
            from datetime import timezone
            if when:
                target_dt = when.astimezone(timezone.utc) if when.tzinfo else when.replace(tzinfo=timezone.utc)
            else:
                target_dt = datetime.now(timezone.utc)
    except Exception as e:
        # If timezone is invalid or zoneinfo fails, use UTC
        logger.warning(f"Invalid timezone '{user_timezone}', falling back to UTC: {e}")
        from datetime import timezone
        target_dt = when or datetime.now(timezone.utc)
        if not target_dt.tzinfo:
            target_dt = target_dt.replace(tzinfo=timezone.utc)
    
    # Format as YYYYMMDD
    return target_dt.strftime('%Y%m%d')


def sanitize_for_filename(text: str) -> str:
    """
    Sanitize any text for safe use in filenames.
    
    Args:
        text: Text to sanitize
    
    Returns:
        Sanitized text safe for filenames
    """
    # Replace any non-alphanumeric or allowed special chars
    sanitized = re.sub(r'[^a-zA-Z0-9._-]', '_', text)
    # Remove multiple consecutive underscores
    sanitized = re.sub(r'_+', '_', sanitized)
    # Remove leading/trailing underscores
    sanitized = sanitized.strip('_')
    
    return sanitized or 'file'