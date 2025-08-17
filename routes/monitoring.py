#!/usr/bin/env python3
"""
Monitoring Routes for CORA
Provides performance metrics and system health endpoints
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
import psutil
import os
from datetime import datetime

from utils.performance_monitor import get_performance_metrics, PerformanceMonitor
from dependencies.auth import get_current_user

# Create router
monitoring_router = APIRouter(
    prefix="/api/monitoring",
    tags=["Monitoring"],
    responses={404: {"description": "Not found"}},
)

@monitoring_router.get("/health")
async def health_check():
    """Basic health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "CORA API"
    }

@monitoring_router.get("/performance")
async def get_performance_metrics(current_user: str = Depends(get_current_user)):
    """Get performance metrics (requires authentication)"""
    try:
        return get_performance_metrics()
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get performance metrics: {str(e)}"
        )

@monitoring_router.get("/system")
async def get_system_metrics(current_user: str = Depends(get_current_user)):
    """Get system performance metrics (requires authentication)"""
    try:
        process = psutil.Process(os.getpid())
        memory_info = process.memory_info()
        
        return {
            "cpu": {
                "percent": psutil.cpu_percent(interval=0.1),
                "count": psutil.cpu_count()
            },
            "memory": {
                "total_gb": psutil.virtual_memory().total / (1024**3),
                "available_gb": psutil.virtual_memory().available / (1024**3),
                "percent": psutil.virtual_memory().percent,
                "process_mb": memory_info.rss / (1024**2)
            },
            "disk": {
                "total_gb": psutil.disk_usage('/').total / (1024**3),
                "free_gb": psutil.disk_usage('/').free / (1024**3),
                "percent": psutil.disk_usage('/').percent
            },
            "process": {
                "threads": process.num_threads(),
                "connections": len(process.connections()),
                "open_files": len(process.open_files()),
                "cpu_percent": process.cpu_percent()
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get system metrics: {str(e)}"
        )

@monitoring_router.get("/performance/{metric_name}")
async def get_specific_metric(
    metric_name: str, 
    current_user: str = Depends(get_current_user)
):
    """Get statistics for a specific performance metric"""
    try:
        monitor = PerformanceMonitor()
        stats = monitor.get_system_health()
        if "error" in stats:
            raise HTTPException(status_code=404, detail=stats["error"])
        return stats
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get metric {metric_name}: {str(e)}"
        )

@monitoring_router.post("/performance/clear")
async def clear_performance_metrics(current_user: str = Depends(get_current_user)):
    """Clear all performance metrics (requires authentication)"""
    try:
        from utils.performance_monitor import clear_metrics
        clear_metrics()
        return {"message": "Performance metrics cleared successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to clear metrics: {str(e)}"
        )

@monitoring_router.post("/performance/enable")
async def enable_performance_monitoring(current_user: str = Depends(get_current_user)):
    """Enable performance monitoring"""
    try:
        from utils.performance_monitor import enable_monitoring
        enable_monitoring()
        return {"message": "Performance monitoring enabled"}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to enable monitoring: {str(e)}"
        )

@monitoring_router.post("/performance/disable")
async def disable_performance_monitoring(current_user: str = Depends(get_current_user)):
    """Disable performance monitoring"""
    try:
        from utils.performance_monitor import disable_monitoring
        disable_monitoring()
        return {"message": "Performance monitoring disabled"}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to disable monitoring: {str(e)}"
        )