#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/app.py
🎯 PURPOSE: Main FastAPI application entry point (slimmed to <300 lines)
🔗 IMPORTS: FastAPI, middleware, routes, services
📤 EXPORTS: FastAPI app instance
"""

# Fix import path for production environment
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

# Load environment variables from .env file
import os
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware
from datetime import datetime
import json

# Import core dependencies
from models import get_db
from utils.redis_manager import redis_manager
from utils.logging_config import setup_logging as setup_legacy_logging, get_logger
from core.logging_json import setup_logging as setup_structured_logging
from utils.error_handler import ErrorHandler, CORAException

# Setup centralized logging (legacy first, optional JSON override)
setup_legacy_logging()
setup_structured_logging()
logger = get_logger(__name__)

# Import services needed for startup
from services.auth_service import (
    create_user, UserAlreadyExistsError, InvalidCredentialsError,
    create_email_verification_token, verify_email_token,
    authenticate_user, create_access_token,
    AuthenticationError, ValidationError
)
from services.email_service import send_email_verification, send_email
from tools.backup_manager import start_backup_scheduler_on_startup
from services.task_scheduler import start_task_scheduler, stop_task_scheduler

# Try to initialize Sentry for production
try:
    sentry_dsn = os.getenv("SENTRY_DSN") or os.getenv("CORA_SENTRY_DSN")
    sentry_env = os.getenv("SENTRY_ENV") or os.getenv("CORA_ENV") or os.getenv("ENVIRONMENT") or "development"
    if sentry_dsn and sentry_dsn.startswith("https://"):
        import sentry_sdk
        from sentry_sdk.integrations.fastapi import FastApiIntegration
        sentry_sdk.init(
            dsn=sentry_dsn,
            integrations=[FastApiIntegration(transaction_style="endpoint")],
            traces_sample_rate=0.1,
            environment=sentry_env,
            release="cora@4.0.0"
        )
        print(f"[CORA] Sentry initialized for environment: {sentry_env}")
    else:
        sentry_sdk = None
        print("[CORA] Sentry DSN not configured, skipping initialization")
except (ImportError, ValueError) as e:
    sentry_sdk = None
    print(f"[CORA] Failed to initialize Sentry: {e}")

from core.version import __version__

# Create FastAPI app
app = FastAPI(
    title="CORA AI - Contractor Business Intelligence",
    description="AI-powered expense tracking and profit intelligence for contractors",
    version=__version__,
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

from core.security import (
    build_cors_config_from_env,
    build_trusted_hosts_from_env,
    security_headers_middleware,
)
from core.request_id import install_request_id_middleware
from core.logging_ext import attach_request_id_filter
from core.access_log import install_access_log_middleware

# CORS (env-driven)
cors_conf = build_cors_config_from_env()
if cors_conf:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_conf["origins"],
        allow_methods=cors_conf["methods"],
        allow_headers=cors_conf["headers"],
        allow_credentials=cors_conf["credentials"],
    )

# Trusted hosts and HTTPS redirect (prod)
try:
    # Env-driven allowed hosts with test-friendly defaults
    env = (os.getenv("ENV") or os.getenv("CORA_ENV") or os.getenv("ENVIRONMENT") or "development").lower()
    hosts_env = (
        os.getenv("ALLOWED_HOSTS")
        or os.getenv("TRUSTED_HOSTS")
        or os.getenv("FASTAPI_ALLOWED_HOSTS")
        or os.getenv("STARLETTE_ALLOWED_HOSTS")
    )

    if hosts_env:
        allowed_hosts = [h.strip() for h in hosts_env.split(",") if h.strip()]
    else:
        if env in {"testing", "test"}:
            allowed_hosts = ["testserver", "localhost", "127.0.0.1", "[::1]"]
        else:
            allowed_hosts = ["localhost", "127.0.0.1", "[::1]"]

    app.add_middleware(TrustedHostMiddleware, allowed_hosts=allowed_hosts)
    logger.info(f"Trusted hosts configured: {allowed_hosts}")

    if env == "prod":
        from starlette.middleware.httpsredirect import HTTPSRedirectMiddleware

        app.add_middleware(HTTPSRedirectMiddleware)
except Exception as e:
    logger.warning(f"Security middleware setup issue: {e}")

# Rate limiting
try:
    # Prefer internal rate limiting middleware to avoid handler coupling issues
    from middleware.rate_limiting import setup_rate_limiting
    setup_rate_limiting(app)
except Exception as e:
    logger.warning(f"Rate limiting not enabled: {e}")

# Minimal security headers (last)
security_headers_middleware(app)

# Request-ID middleware and logging filter (after other middlewares)
install_request_id_middleware(app)
try:
    attach_request_id_filter()
except Exception as e:
    logger.warning(f"Request-ID logging filter not attached: {e}")

# Access log middleware (after request-id so rid is available)
try:
    install_access_log_middleware(app)
except Exception as e:
    logger.warning(f"Access log middleware not installed: {e}")

# Initialize error handler (no-arg constructor per production behavior)
error_handler = ErrorHandler()

# Exception handlers
@app.exception_handler(CORAException)
async def cora_exception_handler(request: Request, exc: CORAException):
    return ErrorHandler.handle_exception(exc, request)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    # Log with correct argument order (exception, request)
    ErrorHandler.log_error(exc, request)
    return ErrorHandler.handle_exception(exc, request)

# Removed custom host validation; relying on TrustedHostMiddleware and security headers middleware

# Static files and templates
static_dir = Path(__file__).parent / "web" / "static"
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
templates = Jinja2Templates(directory="web/templates")

# Module-level server start time
server_start_time = datetime.now()

# Register all routes from centralized module
from core.app_routes import register_routes
register_routes(app)

# Register core endpoints
from core.app_endpoints import register_core_endpoints
register_core_endpoints(app, server_start_time)

# Add WebSocket endpoint
from routes.websocket import websocket_endpoint
app.websocket("/ws")(lambda websocket: websocket_endpoint(websocket, app))

# Start backup scheduler on application startup
try:
    start_backup_scheduler_on_startup()
except (ImportError, RuntimeError, AttributeError) as e:
    logger.warning(f"Failed to start backup scheduler: {e}")

# Start business task scheduler on application startup
try:
    start_task_scheduler()
except (ImportError, RuntimeError, AttributeError) as e:
    logger.warning(f"Failed to start business task scheduler: {e}")

# Application startup event
@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("CORA AI starting up...")
    
    # Initialize Redis connection (no-op in dev)
    try:
        _ = redis_manager.ping()
    except Exception:
        pass
    
    # Log startup info
    logger.info(f"Server started at {server_start_time}")
    logger.info(f"Total routes registered: {len(app.routes)}")

# Application shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("CORA AI shutting down...")
    
    # Stop task scheduler
    try:
        stop_task_scheduler()
    except Exception as e:
        logger.warning(f"Error stopping task scheduler: {e}")
    
    # Close Redis connection (no-op in dev)
    try:
        await redis_manager.close()
    except Exception:
        pass
    
    logger.info("Shutdown complete")

# Main entry point
if __name__ == "__main__":
    import uvicorn
    
    # Get configuration from environment
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    reload = os.getenv("ENVIRONMENT", "development") == "development"
    
    # Run the application
    uvicorn.run(
        "app:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )
