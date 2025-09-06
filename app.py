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
from datetime import datetime
import json

# Import core dependencies
from models import get_db
from utils.redis_manager import redis_manager
from utils.logging_config import setup_logging, get_logger
from utils.error_handler import ErrorHandler, CORAException

# Setup centralized logging
setup_logging()
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

# Create FastAPI app
app = FastAPI(
    title="CORA AI - Contractor Business Intelligence",
    description="AI-powered expense tracking and profit intelligence for contractors",
    version="4.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize error handler (no-arg constructor per production behavior)
error_handler = ErrorHandler()

# Exception handlers
@app.exception_handler(CORAException)
async def cora_exception_handler(request: Request, exc: CORAException):
    return ErrorHandler.handle_exception(exc, request)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    # Note: calling with (request, exception) to match production behavior
    ErrorHandler.log_error(request, exc)
    return ErrorHandler.handle_exception(exc, request)

# Middleware for trusted host and security headers
@app.middleware("http")
async def trusted_host_middleware(request: Request, call_next):
    """Enforce trusted host header for security"""
    allowed_hosts = {
        "localhost",
        "127.0.0.1",
        "0.0.0.0",
        "coraai.tech",
        "www.coraai.tech",
        "cora-ai.com",
        "www.cora-ai.com"
    }
    
    host = request.headers.get("host", "").split(":")[0].lower()
    if host and host not in allowed_hosts:
        logger.warning(f"Rejected request from untrusted host: {host}")
        return JSONResponse(
            status_code=400,
            content={"detail": "Invalid host header"}
        )
    
    response = await call_next(request)
    
    # Add security headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    
    return response

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
    
    # Initialize Redis connection
    try:
        if redis_manager.ping():
            logger.info("Redis connection established")
    except Exception as e:
        logger.warning(f"Redis not available: {e}")
    
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
    
    # Close Redis connection
    try:
        await redis_manager.close()
    except Exception as e:
        logger.warning(f"Error closing Redis: {e}")
    
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