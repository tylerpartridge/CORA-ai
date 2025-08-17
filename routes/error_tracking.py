#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/routes/error_tracking.py
🎯 PURPOSE: Client-side error tracking endpoints
🔗 IMPORTS: FastAPI, logging, datetime
📤 EXPORTS: Error tracking router
"""

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import logging
import json
from collections import defaultdict
from utils.notifier import send_email, send_slack

logger = logging.getLogger(__name__)

# Create router
error_router = APIRouter(
    prefix="/api/errors",
    tags=["Error Tracking"],
)

# In-memory error storage (in production, use database)
error_storage = defaultdict(list)
error_counts = defaultdict(int)
MAX_ERRORS_PER_TYPE = 100

class JavaScriptError(BaseModel):
    """JavaScript error model"""
    message: str
    source: Optional[str] = None
    lineno: Optional[int] = None
    colno: Optional[int] = None
    stack: Optional[str] = None
    userAgent: Optional[str] = None
    url: str
    timestamp: Optional[str] = None
    errorType: Optional[str] = "javascript"
    
class PerformanceMetric(BaseModel):
    """Performance metric model"""
    metric: str  # 'page_load', 'api_call', 'render_time'
    value: float  # milliseconds
    url: str
    metadata: Optional[Dict[str, Any]] = {}
    timestamp: Optional[str] = None

@error_router.post("/javascript")
async def log_javascript_error(error: JavaScriptError, request: Request):
    """Log JavaScript errors from client"""
    try:
        # Add server-side metadata
        error_data = error.dict()
        error_data['ip'] = request.client.host
        error_data['timestamp'] = error_data.get('timestamp') or datetime.now().isoformat()
        
        # Categorize error
        error_key = f"{error.source}:{error.lineno}" if error.source else error.message[:50]
        
        # Store error (with limits)
        if len(error_storage[error_key]) < MAX_ERRORS_PER_TYPE:
            error_storage[error_key].append(error_data)
        
        # Increment counter
        error_counts[error_key] += 1
        
        # Log for monitoring
        logger.error(f"JS Error: {error.message} at {error.source}:{error.lineno}")
        
        # Check for critical errors
        if is_critical_error(error):
            notify_critical_error(error_data)
        
        return JSONResponse(
            status_code=200,
            content={"status": "logged", "id": error_key}
        )
        
    except Exception as e:
        logger.error(f"Failed to log JS error: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": "Failed to log error"}
        )

@error_router.post("/performance")
async def log_performance_metric(metric: PerformanceMetric, request: Request):
    """Log performance metrics from client"""
    try:
        metric_data = metric.dict()
        metric_data['timestamp'] = metric_data.get('timestamp') or datetime.now().isoformat()
        metric_data['ip'] = request.client.host
        
        # Store metric
        metric_key = f"{metric.metric}:{metric.url}"
        if len(error_storage[metric_key]) < MAX_ERRORS_PER_TYPE:
            error_storage[metric_key].append(metric_data)
        
        # Check for performance issues
        if metric.metric == 'page_load' and metric.value > 3000:  # > 3 seconds
            logger.warning(f"Slow page load: {metric.url} took {metric.value}ms")
        
        return JSONResponse(
            status_code=200,
            content={"status": "logged"}
        )
        
    except Exception as e:
        logger.error(f"Failed to log performance metric: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": "Failed to log metric"}
        )

@error_router.get("/summary")
async def get_error_summary():
    """Get summary of recent errors"""
    try:
        # Calculate error rates
        now = datetime.now()
        recent_errors = []
        
        for error_key, errors in error_storage.items():
            recent = [e for e in errors 
                     if datetime.fromisoformat(e['timestamp']) > now - timedelta(hours=24)]
            if recent:
                recent_errors.append({
                    'key': error_key,
                    'count': len(recent),
                    'total_count': error_counts[error_key],
                    'last_seen': max(e['timestamp'] for e in recent),
                    'sample': recent[0]
                })
        
        # Sort by frequency
        recent_errors.sort(key=lambda x: x['count'], reverse=True)
        
        return {
            'total_error_types': len(error_storage),
            'total_errors_24h': sum(e['count'] for e in recent_errors),
            'top_errors': recent_errors[:10],
            'critical_errors': [e for e in recent_errors 
                               if is_critical_from_summary(e['sample'])]
        }
        
    except Exception as e:
        logger.error(f"Failed to get error summary: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": "Failed to get summary"}
        )

@error_router.delete("/clear")
async def clear_errors():
    """Clear error storage (admin only)"""
    try:
        error_storage.clear()
        error_counts.clear()
        return {"status": "cleared"}
    except Exception as e:
        logger.error(f"Failed to clear errors: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": "Failed to clear"}
        )

def is_critical_error(error: JavaScriptError) -> bool:
    """Determine if error is critical"""
    critical_keywords = [
        'SecurityError', 'TypeError: Cannot read', 
        'ReferenceError', 'Failed to fetch',
        'Network request failed', 'CORS'
    ]
    return any(keyword in error.message for keyword in critical_keywords)

def is_critical_from_summary(error_data: dict) -> bool:
    """Check if error from summary is critical"""
    critical_keywords = [
        'SecurityError', 'TypeError: Cannot read',
        'ReferenceError', 'Failed to fetch',
        'Network request failed', 'CORS'
    ]
    message = error_data.get('message', '')
    return any(keyword in message for keyword in critical_keywords)

def notify_critical_error(error_data: dict):
    """Notify about critical errors (implement based on notification system)"""
    logger.critical(f"CRITICAL JS ERROR: {error_data.get('message')} at {error_data.get('url')}")
    send_email("admin@example.com", "Critical JS Error", json.dumps(error_data))
    send_slack("#errors", f"Critical: {error_data.get('message')}")