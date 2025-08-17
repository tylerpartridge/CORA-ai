#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/middleware/file_upload_security.py
🎯 PURPOSE: File upload security middleware to prevent malicious uploads
🔗 IMPORTS: FastAPI, magic, os, hashlib
📤 EXPORTS: validate_file_upload, secure_file_storage
"""

import os
import hashlib
import uuid
from typing import List, Optional, Tuple
from fastapi import UploadFile, HTTPException
import magic
from pathlib import Path

# Allowed file types and their MIME types
ALLOWED_FILE_TYPES = {
    # Images
    "image/jpeg": [".jpg", ".jpeg"],
    "image/png": [".png"],
    "image/gif": [".gif"],
    "image/webp": [".webp"],
    "image/svg+xml": [".svg"],
    
    # Documents
    "application/pdf": [".pdf"],
    "application/msword": [".doc"],
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": [".docx"],
    "application/vnd.ms-excel": [".xls"],
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": [".xlsx"],
    "text/csv": [".csv"],
    
    # Receipts and financial documents
    "image/tiff": [".tiff", ".tif"],
    "application/octet-stream": [".txt"],  # For plain text files
}

# File size limits (in bytes)
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB
MAX_DOCUMENT_SIZE = 10 * 1024 * 1024  # 10MB

# Dangerous file extensions to block
BLOCKED_EXTENSIONS = [
    ".exe", ".bat", ".cmd", ".com", ".pif", ".scr", ".vbs", ".js", ".jar",
    ".php", ".asp", ".aspx", ".jsp", ".py", ".pl", ".sh", ".cgi",
    ".dll", ".so", ".dylib", ".sys", ".drv", ".bin",
    ".lnk", ".url", ".hta", ".msi", ".msp", ".mst",
    ".reg", ".inf", ".ini", ".cfg", ".conf",
    ".ps1", ".psm1", ".psd1", ".ps1xml", ".psc1", ".pssc",
    ".app", ".applescript", ".scpt", ".command", ".terminal",
]

def validate_file_upload(file: UploadFile, max_size: Optional[int] = None) -> Tuple[bool, str]:
    """
    Validate file upload for security
    
    Args:
        file: UploadFile object
        max_size: Maximum file size in bytes (optional)
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        # Check file size
        if max_size is None:
            # Determine max size based on file type
            content_type = file.content_type or "application/octet-stream"
            if content_type.startswith("image/"):
                max_size = MAX_IMAGE_SIZE
            else:
                max_size = MAX_DOCUMENT_SIZE
        
        # Read file content for validation
        content = file.file.read()
        file.file.seek(0)  # Reset file pointer
        
        if len(content) > max_size:
            return False, f"File size exceeds maximum allowed size of {max_size // (1024*1024)}MB"
        
        # Check file extension
        file_extension = Path(file.filename).suffix.lower() if file.filename else ""
        
        if file_extension in BLOCKED_EXTENSIONS:
            return False, f"File type {file_extension} is not allowed"
        
        # Validate MIME type using python-magic
        try:
            mime_type = magic.from_buffer(content, mime=True)
        except Exception:
            # Fallback to content-type header
            mime_type = file.content_type or "application/octet-stream"
        
        # Check if MIME type is allowed
        if mime_type not in ALLOWED_FILE_TYPES:
            return False, f"MIME type {mime_type} is not allowed"
        
        # Check if file extension matches MIME type
        if file_extension and file_extension not in ALLOWED_FILE_TYPES.get(mime_type, []):
            return False, f"File extension {file_extension} does not match MIME type {mime_type}"
        
        # Additional security checks
        if not perform_deep_validation(content, mime_type):
            return False, "File failed security validation"
        
        return True, ""
        
    except Exception as e:
        return False, f"File validation error: {str(e)}"

def perform_deep_validation(content: bytes, mime_type: str) -> bool:
    """Perform deep validation of file content"""
    try:
        # Check for executable content in non-executable files
        if mime_type.startswith("image/") or mime_type.startswith("text/"):
            # Look for executable signatures
            executable_signatures = [
                b"MZ",  # Windows PE
                b"\x7fELF",  # Linux ELF
                b"\xfe\xed\xfa",  # Mach-O
                b"#!/",  # Shell script
            ]
            
            for sig in executable_signatures:
                if content.startswith(sig):
                    return False
        
        # Check for PHP code in text files
        if mime_type == "text/plain" or mime_type == "application/octet-stream":
            if b"<?php" in content or b"<?=" in content:
                return False
        
        # Check for HTML/script content in images
        if mime_type.startswith("image/"):
            if b"<script" in content or b"<html" in content:
                return False
        
        return True
        
    except Exception:
        return False

def generate_secure_filename(original_filename: str, user_email: str) -> str:
    """
    Generate a secure filename to prevent path traversal and conflicts
    
    Args:
        original_filename: Original filename
        user_email: User's email for namespace
    
    Returns:
        Secure filename
    """
    # Get file extension
    file_extension = Path(original_filename).suffix.lower()
    
    # Generate unique identifier
    unique_id = str(uuid.uuid4())
    
    # Create hash of user email for namespace
    user_hash = hashlib.sha256(user_email.encode()).hexdigest()[:8]
    
    # Generate secure filename
    secure_filename = f"{user_hash}_{unique_id}{file_extension}"
    
    return secure_filename

def get_secure_upload_path(filename: str, user_email: str, upload_type: str = "general") -> str:
    """
    Get secure upload path for file storage
    
    Args:
        filename: Secure filename
        user_email: User's email
        upload_type: Type of upload (general, receipts, documents, etc.)
    
    Returns:
        Secure file path
    """
    # Create user-specific directory
    user_hash = hashlib.sha256(user_email.encode()).hexdigest()[:8]
    
    # Create upload directory structure
    upload_base = os.getenv("UPLOAD_DIR", "uploads")
    upload_path = os.path.join(upload_base, user_hash, upload_type)
    
    # Ensure directory exists
    os.makedirs(upload_path, exist_ok=True)
    
    # Return full path
    return os.path.join(upload_path, filename)

async def save_uploaded_file(file: UploadFile, user_email: str, upload_type: str = "general") -> str:
    """
    Save uploaded file securely
    
    Args:
        file: UploadFile object
        user_email: User's email
        upload_type: Type of upload
    
    Returns:
        File path where file was saved
    """
    # Generate secure filename
    secure_filename = generate_secure_filename(file.filename, user_email)
    
    # Get secure upload path
    file_path = get_secure_upload_path(secure_filename, user_email, upload_type)
    
    # Save file
    try:
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        return file_path
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")

def cleanup_old_files(upload_dir: str, max_age_days: int = 30):
    """
    Clean up old uploaded files
    
    Args:
        upload_dir: Upload directory
        max_age_days: Maximum age of files in days
    """
    try:
        import time
        current_time = time.time()
        max_age_seconds = max_age_days * 24 * 60 * 60
        
        for root, dirs, files in os.walk(upload_dir):
            for file in files:
                file_path = os.path.join(root, file)
                file_age = current_time - os.path.getmtime(file_path)
                
                if file_age > max_age_seconds:
                    try:
                        os.remove(file_path)
                        print(f"Removed old file: {file_path}")
                    except Exception as e:
                        print(f"Failed to remove old file {file_path}: {e}")
                        
    except Exception as e:
        print(f"Error during file cleanup: {e}")

def get_file_info(file_path: str) -> dict:
    """
    Get information about a file
    
    Args:
        file_path: Path to file
    
    Returns:
        Dictionary with file information
    """
    try:
        stat = os.stat(file_path)
        
        with open(file_path, "rb") as f:
            content = f.read(1024)  # Read first 1KB for MIME detection
            mime_type = magic.from_buffer(content, mime=True)
        
        return {
            "size": stat.st_size,
            "mime_type": mime_type,
            "created": stat.st_ctime,
            "modified": stat.st_mtime,
            "filename": os.path.basename(file_path)
        }
        
    except Exception as e:
        return {"error": str(e)}

# File upload decorator for route handlers
def secure_file_upload(max_size: Optional[int] = None, allowed_types: Optional[List[str]] = None):
    """
    Decorator for secure file upload handling
    
    Args:
        max_size: Maximum file size
        allowed_types: List of allowed MIME types
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Find UploadFile in arguments
            upload_file = None
            for arg in args:
                if isinstance(arg, UploadFile):
                    upload_file = arg
                    break
            
            if not upload_file:
                for value in kwargs.values():
                    if isinstance(value, UploadFile):
                        upload_file = value
                        break
            
            if upload_file:
                # Validate file
                is_valid, error_message = validate_file_upload(upload_file, max_size)
                if not is_valid:
                    raise HTTPException(status_code=400, detail=error_message)
                
                # Check allowed types if specified
                if allowed_types and upload_file.content_type not in allowed_types:
                    raise HTTPException(status_code=400, detail=f"File type {upload_file.content_type} not allowed")
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator 