#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/utils/logging_config.py
🎯 PURPOSE: Centralized logging configuration for CORA application
🔗 IMPORTS: logging, os, sys
📤 EXPORTS: setup_logging, get_logger, LogConfig
"""

import logging
import logging.handlers
import os
import sys
from datetime import datetime
from typing import Optional, Dict, Any
from pathlib import Path

class LogConfig:
    """Centralized logging configuration"""
    
    # Log levels
    LEVELS = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL
    }
    
    # Default configuration
    DEFAULT_CONFIG = {
        "level": "INFO",
        "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        "date_format": "%Y-%m-%d %H:%M:%S",
        "log_dir": "logs",
        "max_file_size": 10 * 1024 * 1024,  # 10MB
        "backup_count": 5,
        "console_output": True,
        "file_output": True
    }
    
    # Module-specific log levels
    MODULE_LEVELS = {
        "cora.validation": "INFO",
        "cora.auth": "INFO",
        "cora.database": "INFO",
        "cora.api": "INFO",
        "cora.external": "WARNING",
        "uvicorn": "WARNING",
        "fastapi": "WARNING",
        "sqlalchemy": "WARNING"
    }

class StructuredFormatter(logging.Formatter):
    """Structured logging formatter with JSON-like output"""
    
    def format(self, record):
        # Add structured fields
        record.module = record.name
        record.timestamp = datetime.fromtimestamp(record.created).isoformat()
        
        # Format the message
        formatted = super().format(record)
        
        # Add extra fields if present
        if hasattr(record, 'extra_fields'):
            extra_str = " | ".join([f"{k}={v}" for k, v in record.extra_fields.items()])
            formatted += f" | {extra_str}"
        
        return formatted

def setup_logging(
    config: Optional[Dict[str, Any]] = None,
    log_dir: Optional[str] = None,
    level: Optional[str] = None
) -> None:
    """
    Setup centralized logging configuration
    
    Args:
        config: Custom configuration dictionary
        log_dir: Directory for log files
        level: Log level
    """
    
    # Merge configuration
    final_config = LogConfig.DEFAULT_CONFIG.copy()
    if config:
        final_config.update(config)
    
    # Override with parameters
    if log_dir:
        final_config["log_dir"] = log_dir
    if level:
        final_config["level"] = level
    
    # Create log directory
    log_path = Path(final_config["log_dir"])
    log_path.mkdir(exist_ok=True)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(LogConfig.LEVELS[final_config["level"]])
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Create formatters
    console_formatter = logging.Formatter(
        final_config["format"],
        datefmt=final_config["date_format"]
    )
    
    file_formatter = StructuredFormatter(
        final_config["format"],
        datefmt=final_config["date_format"]
    )
    
    # Console handler
    if final_config["console_output"]:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(LogConfig.LEVELS[final_config["level"]])
        console_handler.setFormatter(console_formatter)
        root_logger.addHandler(console_handler)
    
    # File handlers
    if final_config["file_output"]:
        # Main application log
        app_log_file = log_path / "cora.log"
        app_handler = logging.handlers.RotatingFileHandler(
            app_log_file,
            maxBytes=final_config["max_file_size"],
            backupCount=final_config["backup_count"]
        )
        app_handler.setLevel(LogConfig.LEVELS[final_config["level"]])
        app_handler.setFormatter(file_formatter)
        root_logger.addHandler(app_handler)
        
        # Error log
        error_log_file = log_path / "cora_errors.log"
        error_handler = logging.handlers.RotatingFileHandler(
            error_log_file,
            maxBytes=final_config["max_file_size"],
            backupCount=final_config["backup_count"]
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(file_formatter)
        root_logger.addHandler(error_handler)
        
        # Request log
        request_log_file = log_path / "cora_requests.log"
        request_handler = logging.handlers.RotatingFileHandler(
            request_log_file,
            maxBytes=final_config["max_file_size"],
            backupCount=final_config["backup_count"]
        )
        request_handler.setLevel(logging.INFO)
        request_handler.setFormatter(file_formatter)
        root_logger.addHandler(request_handler)
    
    # Configure module-specific log levels
    for module, module_level in LogConfig.MODULE_LEVELS.items():
        module_logger = logging.getLogger(module)
        module_logger.setLevel(LogConfig.LEVELS[module_level])
    
    # Log startup message
    startup_logger = logging.getLogger("cora.startup")
    startup_logger.info("Logging system initialized", extra={
        "extra_fields": {
            "log_level": final_config["level"],
            "log_dir": str(log_path),
            "console_output": final_config["console_output"],
            "file_output": final_config["file_output"]
        }
    })

def get_logger(name: str) -> logging.Logger:
    """
    Get a logger with the specified name
    
    Args:
        name: Logger name (usually __name__)
    
    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)

def log_with_context(logger: logging.Logger, level: str, message: str, 
                    context: Optional[Dict[str, Any]] = None, **kwargs):
    """
    Log message with structured context
    
    Args:
        logger: Logger instance
        level: Log level
        message: Log message
        context: Additional context dictionary
        **kwargs: Additional context fields
    """
    
    # Combine context and kwargs
    extra_fields = {}
    if context:
        extra_fields.update(context)
    if kwargs:
        extra_fields.update(kwargs)
    
    # Create log record with extra fields
    log_record = logging.LogRecord(
        name=logger.name,
        level=LogConfig.LEVELS.get(level, logging.INFO),
        pathname="",
        lineno=0,
        msg=message,
        args=(),
        exc_info=None
    )
    
    if extra_fields:
        log_record.extra_fields = extra_fields
    
    logger.handle(log_record)

# Convenience functions for common logging patterns
def log_request(logger: logging.Logger, method: str, path: str, status_code: int, 
                duration: float, user_id: Optional[str] = None, **kwargs):
    """Log HTTP request details"""
    log_with_context(
        logger, "INFO", "HTTP Request",
        context={
            "method": method,
            "path": path,
            "status_code": status_code,
            "duration_ms": round(duration * 1000, 2),
            "user_id": user_id
        },
        **kwargs
    )

def log_database_operation(logger: logging.Logger, operation: str, table: str, 
                          duration: float, rows_affected: Optional[int] = None, **kwargs):
    """Log database operation details"""
    log_with_context(
        logger, "INFO", "Database Operation",
        context={
            "operation": operation,
            "table": table,
            "duration_ms": round(duration * 1000, 2),
            "rows_affected": rows_affected
        },
        **kwargs
    )

def log_external_service(logger: logging.Logger, service: str, operation: str, 
                        duration: float, status: str, **kwargs):
    """Log external service calls"""
    log_with_context(
        logger, "INFO", "External Service Call",
        context={
            "service": service,
            "operation": operation,
            "duration_ms": round(duration * 1000, 2),
            "status": status
        },
        **kwargs
    )

def log_security_event(logger: logging.Logger, event_type: str, user_id: Optional[str] = None, 
                      ip_address: Optional[str] = None, **kwargs):
    """Log security-related events"""
    log_with_context(
        logger, "WARNING", "Security Event",
        context={
            "event_type": event_type,
            "user_id": user_id,
            "ip_address": ip_address
        },
        **kwargs
    )

# Initialize logging on module import
if not logging.getLogger().handlers:
    setup_logging() 