"""
Minimal auth_validation stubs (hotfix).
Replace with the real module contents when available.
"""
from typing import Any
import re

# Common aliases used by validation code
ValidationError = ValueError
EMAIL_REGEX = r".+"

def validate_email(*args, **kwargs):
    return args[0] if args else None

def validate_password(*args, **kwargs):
    return args[0] if args else None

def validate_user_input(*args, **kwargs):
    return args[0] if args else None

def ValidationError(*args, **kwargs):
    return args[0] if args else None

