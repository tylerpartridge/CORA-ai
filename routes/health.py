
from fastapi import APIRouter, HTTPException, Response, Request
from fastapi.responses import JSONResponse
from middleware.monitoring import get_system_health, get_metrics
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from utils.redis_manager import redis_manager
from datetime import datetime, timezone
import time
from sqlalchemy import text  # lightweight ping query
from core.version import __version__
from services.email_service import EmailService
from core.request_id import get_request_id
from middleware.rate_limit import limiter
import sqlite3
import os

health_router = APIRouter()

@limiter.exempt
@health_router.get("/health")
async def health_check():
    """Basic health check"""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

@limiter.exempt
@health_router.get("/ping", operation_id="pingHealth", summary="Simple liveness check")
async def ping_health():
    """Simple liveness check"""
    return {"ok": True}

@limiter.exempt
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

@limiter.exempt
@health_router.get("/metrics", operation_id="getMetrics", summary="Prometheus metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    data = generate_latest()
    return Response(content=data, media_type=CONTENT_TYPE_LATEST)

@limiter.exempt
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


@limiter.exempt
@health_router.get("/smoke", operation_id="getSmoke", summary="Admin smoke check")
async def smoke(request: Request):
    """Lightweight admin diagnostics; protected via admin token or localhost-only."""
    import os
    from models import engine  # exported in models.__init__

    admin_token = os.getenv("ADMIN_TOKEN") or os.getenv("CORA_ADMIN_TOKEN")
    if admin_token:
        if request.headers.get("X-Admin-Token") != admin_token:
            raise HTTPException(status_code=403, detail="Forbidden")
    else:
        client_host = (request.client.host if request.client else "")
        if client_host not in {"127.0.0.1", "::1", "localhost"}:
            raise HTTPException(status_code=403, detail="Forbidden")

    # Checks
    time_utc = (
        datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    )

    # DB check (best-effort SELECT 1)
    t = time.perf_counter()
    db_ok = False
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        db_ok = True
    except Exception:
        db_ok = False
    db_ms = int(round((time.perf_counter() - t) / 0.001))
    db = {"ok": db_ok, "ms": db_ms}

    # Redis check via tolerant manager
    t = time.perf_counter()
    try:
        r_ok = bool(redis_manager.ping())
    except Exception:
        r_ok = False
    redis = {"ok": r_ok, "ms": int(round((time.perf_counter() - t) / 0.001))}

    # Email check via facade
    t = time.perf_counter()
    try:
        e_ok = bool(EmailService().health())
        email = {"ok": e_ok, "ms": int(round((time.perf_counter() - t) / 0.001))}
    except Exception:
        email = {"ok": False, "skipped": True, "ms": int(round((time.perf_counter() - t) / 0.001))}

    routes_count = len(request.app.routes)

    # Aggregate status
    if not db["ok"]:
        overall = "red"
    elif (not redis["ok"]) or (not email.get("ok", True) and not email.get("skipped")):
        overall = "yellow"
    else:
        overall = "green"

    payload = {
        "status": overall,
        "checks": {
            "time_utc": time_utc,
            "version": __version__,
            "request_id": get_request_id(),
            "db": db,
            "redis": redis,
            "email": email,
            "routes_count": routes_count,
        },
    }

    return JSONResponse(payload, headers={"Cache-Control": "no-store"})
