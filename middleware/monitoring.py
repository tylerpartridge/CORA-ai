
import time
import logging
from fastapi import Request, Response
from prometheus_client import Counter, Histogram, generate_latest
import psutil
import os

# Prometheus metrics
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
REQUEST_LATENCY = Histogram('http_request_duration_seconds', 'HTTP request latency')
ACTIVE_CONNECTIONS = Counter('active_connections', 'Active database connections')
MEMORY_USAGE = Histogram('memory_usage_bytes', 'Memory usage in bytes')
CPU_USAGE = Histogram('cpu_usage_percent', 'CPU usage percentage')

# Business metrics
EXPENSES_CREATED = Counter('expenses_created_total', 'Total expenses created', ['source'])
VOICE_EXPENSES_SUCCESS = Counter('voice_expenses_success_total', 'Successful voice expenses')
VOICE_EXPENSES_FAILED = Counter('voice_expenses_failed_total', 'Failed voice expenses')
JOBS_CREATED = Counter('jobs_created_total', 'Total jobs created')
JOBS_COMPLETED = Counter('jobs_completed_total', 'Total jobs completed')
ALERTS_CREATED = Counter('alerts_created_total', 'Total alerts created', ['severity'])

logger = logging.getLogger(__name__)

async def monitoring_middleware(request: Request, call_next):
    """Monitoring middleware for metrics collection"""
    start_time = time.time()
    
    # Record request start
    method = request.method
    endpoint = request.url.path
    
    try:
        response = await call_next(request)
        
        # Record metrics
        duration = time.time() - start_time
        REQUEST_COUNT.labels(method=method, endpoint=endpoint, status=response.status_code).inc()
        REQUEST_LATENCY.observe(duration)
        
        # Record system metrics
        MEMORY_USAGE.observe(psutil.virtual_memory().used)
        CPU_USAGE.observe(psutil.cpu_percent())
        
        return response
        
    except Exception as e:
        # Record error metrics
        duration = time.time() - start_time
        REQUEST_COUNT.labels(method=method, endpoint=endpoint, status=500).inc()
        REQUEST_LATENCY.observe(duration)
        logger.error(f"Request failed: {str(e)}")
        raise

def get_metrics():
    """Get Prometheus metrics"""
    return generate_latest()

def get_system_health():
    """Get system health metrics"""
    return {
        'memory_usage': psutil.virtual_memory().percent,
        'cpu_usage': psutil.cpu_percent(),
        'disk_usage': psutil.disk_usage('/').percent,
        'load_average': os.getloadavg() if hasattr(os, 'getloadavg') else None
    }

# Export business metrics for use in routes
__all__ = [
    'monitoring_middleware',
    'get_metrics',
    'get_system_health',
    'EXPENSES_CREATED',
    'VOICE_EXPENSES_SUCCESS',
    'VOICE_EXPENSES_FAILED',
    'JOBS_CREATED',
    'JOBS_COMPLETED',
    'ALERTS_CREATED'
]
