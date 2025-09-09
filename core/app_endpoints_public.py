#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/core/app_endpoints_public.py
🎯 PURPOSE: Public/core endpoints split out from app.py to satisfy size guidelines
🔗 IMPORTS: FastAPI, SQLAlchemy, utilities
📤 EXPORTS: register_public_endpoints(app, server_start_time)
"""

from datetime import datetime
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, Request, Depends, HTTPException, Response
from fastapi.responses import JSONResponse, RedirectResponse
from sqlalchemy import text
from sqlalchemy.exc import DatabaseError, OperationalError, SQLAlchemyError
from sqlalchemy.orm import Session

from models import get_db as models_get_db, User
from utils.redis_manager import redis_manager
from core.version import __version__


def register_public_endpoints(app: FastAPI, server_start_time: datetime) -> None:
    """Register public/health/status and intelligence endpoints."""

    @app.get("/static/js/bundles/{filename:path}")
    async def serve_bundle_files(filename: str):
        static_dir = Path(__file__).parent.parent / "web" / "static"
        bundle_path = static_dir / "js" / "bundles" / filename
        if not bundle_path.exists():
            raise HTTPException(status_code=404, detail="Bundle file not found")

        with open(bundle_path, "rb") as f:
            content = f.read()

        content_type = "application/javascript"
        if filename.endswith(".map"):
            content_type = "application/json"

        headers = {
            "Cache-Control": "public, max-age=31536000, immutable",
            "Content-Type": content_type,
        }
        return Response(content=content, headers=headers)

    @app.get("/health")
    async def health_check():
        return {"status": "healthy", "version": __version__}

    @app.get("/api/health")
    async def api_health_check():
        return {"status": "healthy", "version": __version__}

    @app.get("/version", operation_id="getVersion", summary="Service version")
    async def get_version():
        # Source from FastAPI metadata to avoid any import/reload edge cases
        try:
            v = getattr(app, "version", None) or "0.0.0"
        except Exception:
            v = "0.0.0"
        return {"version": v}

    # /ping defined in routes/health.py via health_router

    @app.get("/api/health/detailed")
    async def detailed_health_check(db: Session = Depends(models_get_db)):
        health_status = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "checks": {},
            "metrics": {},
        }

        try:
            db.execute(text("SELECT 1"))
            health_status["checks"]["database"] = True
        except (DatabaseError, OperationalError, SQLAlchemyError):
            health_status["checks"]["database"] = False
            health_status["status"] = "degraded"

        try:
            redis_manager.client.ping()
            health_status["checks"]["redis"] = True
        except (ConnectionError, TimeoutError, AttributeError):
            health_status["checks"]["redis"] = False
            health_status["status"] = "degraded"

        try:
            import sentry_sdk  # type: ignore
            health_status["checks"]["sentry"] = (
                sentry_sdk is not None and sentry_sdk.Hub.current.client is not None
            )
        except Exception:
            health_status["checks"]["sentry"] = False

        uptime_seconds = int((datetime.now() - server_start_time).total_seconds())
        health_status["metrics"]["uptime_seconds"] = uptime_seconds
        health_status["metrics"]["uptime_human"] = f"{uptime_seconds // 3600}h {(uptime_seconds % 3600) // 60}m"

        return health_status

    @app.post("/api/cora-chat-v2/")
    async def redirect_chat_v2(request: Request):
        try:
            await request.body()
        except Exception:
            pass
        return RedirectResponse(url="/api/cora-ai/chat", status_code=307)

    @app.post("/api/signup")
    async def redirect_legacy_signup():
        return RedirectResponse(url="/api/auth/register", status_code=307)

    @app.get("/api/status")
    async def api_status():
        now = datetime.now()
        uptime_delta = now - server_start_time
        hours, remainder = divmod(int(uptime_delta.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        if hours > 0:
            uptime = f"{hours}h {minutes}m"
        elif minutes > 0:
            uptime = f"{minutes}m {seconds}s"
        else:
            uptime = f"{seconds}s"

        cora_dir = Path(__file__).parent.parent
        total_files = sum(1 for f in cora_dir.glob("*.py"))
        return {
            "status": "healthy",
            "version": "4.0",
            "uptime": uptime,
            "timestamp": now.isoformat(),
            "total_files": total_files,
        }

    @app.get("/api/predictive-intelligence/insights")
    async def predictive_intelligence_insights(request: Request, db: Session = Depends(models_get_db)):
        try:
            from dependencies.auth import get_current_user_optional  # local import
            current_user = await get_current_user_optional(request)
        except Exception:
            current_user = None

        try:
            from services.intelligence_orchestrator import IntelligenceOrchestrator
            orchestrator = IntelligenceOrchestrator(current_user, db)
            unified = await orchestrator.orchestrate_intelligence()
            payload = {
                "insights": unified.get("primary_signals", []),
                "predictions": unified.get("predictions", []),
                "recommendations": unified.get("growth_opportunities", []),
                "intelligence_score": unified.get("intelligence_score", 0),
            }
            return JSONResponse(payload)
        except Exception:
            return JSONResponse(
                {
                    "insights": [],
                    "predictions": [],
                    "recommendations": [],
                    "error": "Predictive intelligence unavailable",
                },
                status_code=200,
            )
