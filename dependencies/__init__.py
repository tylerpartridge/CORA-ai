"""
Dependencies package for CORA
Contains authentication and other dependencies
"""

from .auth import get_current_user, get_current_active_user

__all__ = ['get_current_user', 'get_current_active_user']