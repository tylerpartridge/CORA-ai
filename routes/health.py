
from fastapi import APIRouter, HTTPException, Response
from middleware.monitoring import get_system_health, get_metrics
from utils.redis_manager import redis_manager
from datetime import datetime
import sqlite3
import os

health_router = APIRouter()

@health_router.get("/health")
async def health_check():
    """Basic health check"""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

@health_router.get("/health/detailed")
async def detailed_health_check():
    """Detailed health check with all components"""
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "components": {}
    }
    
    # Database health
    try:
        db_path = "cora.db"
        if os.path.exists(db_path):
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            conn.close()
            health_status["components"]["database"] = "healthy"
        else:
            health_status["components"]["database"] = "missing"
    except Exception as e:
        health_status["components"]["database"] = f"error: {str(e)}"
        health_status["status"] = "unhealthy"
    
    # Redis health
    try:
        if redis_manager.redis_client and redis_manager.redis_client.ping():
            health_status["components"]["redis"] = "healthy"
        else:
            health_status["components"]["redis"] = "unavailable"
    except Exception as e:
        health_status["components"]["redis"] = f"error: {str(e)}"
    
    # System health
    try:
        system_health = get_system_health()
        health_status["components"]["system"] = system_health
    except Exception as e:
        health_status["components"]["system"] = f"error: {str(e)}"
    
    return health_status

@health_router.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return Response(content=get_metrics(), media_type="text/plain")

@health_router.get("/health/ready")
async def readiness_check():
    """Readiness check for load balancers"""
    # Check if all critical services are ready
    try:
        # Database check
        db_path = "cora.db"
        if not os.path.exists(db_path):
            raise HTTPException(status_code=503, detail="Database not ready")
        
        # Redis check (optional)
        if redis_manager.redis_client:
            redis_manager.redis_client.ping()
        
        return {"status": "ready"}
        
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Service not ready: {str(e)}")
