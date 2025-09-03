#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/app.py
🎯 PURPOSE: FastAPI server - complete CORA AI system with auth, expenses, integrations
🔗 IMPORTS: FastAPI, Jinja2Templates, StaticFiles, all route modules
📤 EXPORTS: app (FastAPI instance) 
🔄 PATTERN: Connected monolith with existing route modules
📝 STATUS: Production ready with full CRUD API

💡 AI HINT: This connects all existing route modules for complete functionality.
⚠️ NEVER: Add business logic here. Just routing and basic validation.
"""

# Cora Version: 4.0
# Created: 2025-07-07
# Previous versions had 400+ files - keeping this one simple!

# Fix import path for production environment
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

# Load environment variables from .env file
import os
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, Request, Form, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from dependencies.database import get_db
from pydantic import BaseModel, EmailStr
from typing import Optional
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import json
from datetime import datetime, timedelta
import os
from models import get_db
from models import User
from utils.redis_manager import redis_manager
from sqlalchemy import text
from sqlalchemy.exc import DatabaseError, OperationalError, SQLAlchemyError
# TEMPORARILY DISABLED: Python 3.13 + eventlet incompatibility
# TODO: Re-enable when eventlet is updated or Python downgraded
# try:
#     import sentry_sdk
#     from sentry_sdk.integrations.fastapi import FastApiIntegration
# except ImportError as e:
#     print(f"[CORA] Sentry import failed: {e}")
#     sentry_sdk = None
#     FastApiIntegration = None
sentry_sdk = None
FastApiIntegration = None
# print("[CORA] Sentry temporarily disabled for Python 3.13 compatibility")
# TEMP_DISABLED: from middleware.rate_limit import setup_rate_limiting
from middleware.security_headers_enhanced import setup_security_headers
from middleware.logging_middleware import setup_request_logging
from middleware.error_handler import setup_error_handlers
# TEMP_DISABLED: from middleware.user_activity import setup_user_activity
from middleware.csrf import setup_csrf_protection
from middleware.account_lockout import setup_account_lockout
# TEMP_DISABLED: from middleware.audit_logging import setup_audit_logging
from middleware.monitoring import monitoring_middleware
# TEMP_DISABLED: from middleware.query_monitoring import QueryMonitoringMiddleware
# TEMP_DISABLED: from middleware.rate_limiting import setup_rate_limiting as setup_new_rate_limiting
from middleware.authorization import setup_authorization
# TEMP_DISABLED: from middleware.response_optimization import setup_response_optimization
# Import enhanced security modules
from middleware.api_security_config import setup_api_security
from middleware.auth_security_enhanced import AuthSecurityMiddleware
from utils.security_enhanced import SecurityUtils

# Initialize Sentry for error tracking
sentry_dsn = os.getenv('SENTRY_DSN', '').strip()
if sentry_dsn and sentry_dsn != 'your-sentry-dsn-here' and sentry_sdk:
    try:
        # In development, disable SSL verification if needed
        import urllib3
        if os.getenv('ENVIRONMENT', 'production') == 'development':
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
        sentry_sdk.init(
            dsn=sentry_dsn,
            integrations=[FastApiIntegration()] if FastApiIntegration else [],
            environment=os.getenv('ENVIRONMENT', 'production'),
            # Add SSL options for development
            https_proxy=os.getenv('HTTPS_PROXY', None),
            # Reduce sample rate in development
            traces_sample_rate=0.1 if os.getenv('ENVIRONMENT') == 'production' else 0.01
        )
#         print("[CORA] Sentry initialized successfully")
    except (ValueError, TypeError, AttributeError) as e:
        print(f"[CORA] Failed to initialize Sentry: {e}")
        # print("[CORA] Continuing without Sentry...")
else:
    # Ensure else block is not empty to avoid IndentationError
    print("[CORA] Sentry DSN not configured or not available, skipping Sentry initialization")

# Import all existing route modules
from routes.auth_coordinator import auth_router
from services.auth_service import create_user, UserAlreadyExistsError, InvalidCredentialsError, create_email_verification_token, verify_email_token, authenticate_user, create_access_token, AuthenticationError, ValidationError
from services.email_service import send_email_verification, send_email
# Import centralized logging and error handling
from utils.logging_config import setup_logging, get_logger
from utils.error_handler import ErrorHandler, CORAException

# Setup centralized logging
setup_logging()

logger = get_logger(__name__)
from routes.expense_routes import expense_router
from routes.payments import payment_router
from routes.payment_coordinator import payment_router as payment_coordinator_router
from routes.dashboard_routes import dashboard_router
from routes.onboarding_routes import onboarding_router
# Removed unused onboarding_v2 import
from routes.admin_routes import admin_router
from routes.plaid_integration import plaid_router
from routes.quickbooks_integration import quickbooks_router
from routes.stripe_integration import stripe_router
from routes.pages import router as pages_router
from routes.receipt_upload import router as receipt_router
from routes.cora_chat import cora_chat_router
from routes.cora_chat_enhanced import cora_chat_enhanced_router
from routes.jobs import job_router
from routes.chat import chat_router
from routes.alert_routes import alert_router
from routes.quick_wins import router as quick_wins_router
from routes.profit_analysis import router as profit_analysis_router
from routes.profit_intelligence import router as profit_intelligence_router
from routes.insights import router as insights_router
from routes.analytics import router as analytics_router
from routes.voice_commands import router as voice_router
from routes.receipts import router as receipts_router
from routes.predictions import router as predictions_router
from routes.pdf_export import router as pdf_export_router
from routes.cora_ai_routes import router as cora_ai_router
from routes.intelligence_orchestrator import router as intelligence_orchestrator_router
from routes.wellness import router as wellness_router
from routes.automation import router as automation_router
from routes.business_tasks import router as business_tasks_router
from routes.monitoring import monitoring_router
from routes.performance_monitor import router as performance_monitor_router
from routes.error_tracking import error_router
from routes.health import health_router
from routes.account_management import router as account_management_router
from routes.feature_flags_admin import router as feature_flags_router
from tools.backup_manager import backup_api_router, start_backup_scheduler_on_startup
from services.task_scheduler import start_task_scheduler, stop_task_scheduler

# Conversational onboarding removed - feature not implemented

# Debug logging for route registration
# print(f"[CORA] Admin router imported: {admin_router}")
# print(f"[CORA] Admin router routes: {len(admin_router.routes)}")
# print(f"[CORA] Onboarding router imported: {onboarding_router}")
# print(f"[CORA] Onboarding router routes: {len(onboarding_router.routes)}")
# print(f"[CORA] Onboarding V2 router imported: {onboarding_v2_router}")
# print(f"[CORA] Onboarding V2 router routes: {len(onboarding_v2_router.routes)}")

# Initialize FastAPI
app = FastAPI(
    title="Cora AI",
    description="AI Bookkeeping for Introverted Founders", 
    version="4.0.0"
)

# Global exception handler for CORA exceptions
@app.exception_handler(CORAException)
async def cora_exception_handler(request: Request, exc: CORAException):
    """Handle CORA exceptions with standardized error responses"""
    return ErrorHandler.handle_exception(exc, request)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle all other exceptions with standardized error responses"""
    return ErrorHandler.handle_exception(exc, request)

# CORS settings
PROD_ORIGINS = [
    "https://coraai.tech",
    "https://www.coraai.tech"
]
DEV_ORIGINS = [
    "http://localhost",
    "http://localhost:8000",
    "http://localhost:8080",
    "http://127.0.0.1:8000",
    "http://127.0.0.1:8080"
]

origins = PROD_ORIGINS + DEV_ORIGINS

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# === ENHANCED SECURITY & LOGGING MIDDLEWARE ===
# Setup API security configuration (CORS, request limits, versioning)
setup_api_security(app)

# Add enhanced authentication security middleware
app.add_middleware(AuthSecurityMiddleware)

# Setup existing middleware
# TEMP_DISABLED: setup_rate_limiting(app)  # Rate limiting ENABLED for security
setup_security_headers(app)
setup_request_logging(app)
setup_error_handlers(app)
# TEMP_DISABLED: setup_user_activity(app)
setup_csrf_protection(app)
setup_account_lockout(app)
# TEMP_DISABLED: setup_audit_logging(app)
# setup_new_rate_limiting(app)  # Enhanced rate limiting - use basic for now
setup_authorization(app)  # Re-enabled - implementation complete
app.middleware('http')(monitoring_middleware)

# Legacy SecurityHeadersMiddleware removed to avoid overriding enhanced CSP

# Add rate limiting middleware
from middleware.rate_limiter import RateLimitMiddleware
app.add_middleware(RateLimitMiddleware)

# Add query monitoring middleware (guard if import is missing)
try:
    query_monitor = QueryMonitoringMiddleware(app, slow_query_threshold=0.1)
    app.add_middleware(QueryMonitoringMiddleware, slow_query_threshold=0.1)
except NameError:
    print("[CORA] QueryMonitoringMiddleware not available; continuing without it")

# Add response optimization middleware
# TEMP_DISABLED: setup_response_optimization(app, enable_compression=True, enable_monitoring=True)

# Setup templates
templates_dir = Path(__file__).parent / "web" / "templates"
templates = Jinja2Templates(directory=str(templates_dir))

# Load bundle manifest for hashed JS files and expose to templates
try:
    bundles_manifest_path = Path(__file__).parent / "web" / "static" / "js" / "bundles" / "manifest.json"
    bundle_manifest = {}
    if bundles_manifest_path.exists():
        with open(bundles_manifest_path, "r", encoding="utf-8") as f:
            bundle_manifest = json.load(f)
    templates.env.globals["bundle_manifest"] = bundle_manifest
except (FileNotFoundError, json.JSONDecodeError, IOError) as e:
    print(f"[CORA] Failed to load bundle manifest: {e}")
    templates.env.globals["bundle_manifest"] = {}

# Expose a single templates instance via app state for all routers to use
app.state.templates = templates
# Temporarily disable perf/web-vitals bundles to reduce navigation "skips" during local dev
templates.env.globals["disable_perf_bundles"] = True

# Mount static files
static_dir = Path(__file__).parent / "web" / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Custom route for bundle files with long cache headers
@app.get("/static/js/bundles/{filename:path}")
async def serve_bundle_files(filename: str):
    """Serve bundle files with long cache headers for better performance"""
    bundle_path = static_dir / "js" / "bundles" / filename
    if not bundle_path.exists():
        raise HTTPException(status_code=404, detail="Bundle file not found")
    
    # Read file content
    with open(bundle_path, "rb") as f:
        content = f.read()
    
    # Determine content type
    content_type = "application/javascript"
    if filename.endswith(".map"):
        content_type = "application/json"
    
    # Return with long cache headers (1 year for hashed files)
    headers = {
        "Cache-Control": "public, max-age=31536000, immutable",  # 1 year
        "Content-Type": content_type,
    }
    
    return Response(content=content, headers=headers)

# Include all existing route modules
app.include_router(auth_router)
app.include_router(expense_router)
app.include_router(payment_router)
app.include_router(payment_coordinator_router)
app.include_router(dashboard_router)
app.include_router(onboarding_router)
# Removed unused onboarding_v2_router
app.include_router(admin_router)
app.include_router(plaid_router)
app.include_router(quickbooks_router)
app.include_router(stripe_router)
app.include_router(pages_router)
app.include_router(receipt_router)
app.include_router(backup_api_router)
app.include_router(job_router)
app.include_router(chat_router)
app.include_router(alert_router)
app.include_router(quick_wins_router)
app.include_router(profit_analysis_router)
app.include_router(profit_intelligence_router)
app.include_router(insights_router)
app.include_router(analytics_router)
app.include_router(voice_router)
app.include_router(receipts_router)
app.include_router(predictions_router)
app.include_router(cora_ai_router)
app.include_router(pdf_export_router)
app.include_router(intelligence_orchestrator_router, prefix="/api/intelligence", tags=["intelligence"])
app.include_router(wellness_router)
app.include_router(automation_router, prefix="/api/automation", tags=["automation"])
app.include_router(business_tasks_router)
app.include_router(monitoring_router)
app.include_router(performance_monitor_router)
app.include_router(error_router)
app.include_router(health_router)
app.include_router(account_management_router)
app.include_router(feature_flags_router)


# Include feedback router for beta users
from routes.feedback_routes import feedback_router
app.include_router(feedback_router)

# Include waitlist router for contractor signups
from routes.waitlist import waitlist_router
app.include_router(waitlist_router, prefix="/api/waitlist", tags=["waitlist"])

# Include CORA chat routers for landing page conversations
app.include_router(cora_chat_router)
app.include_router(cora_chat_enhanced_router)

# Include sitemap router for SEO
from routes.sitemap import router as sitemap_router
app.include_router(sitemap_router)

# Include SEO landing pages router
from routes.seo_pages import router as seo_pages_router
app.include_router(seo_pages_router)

# Include blog router for content marketing
from routes.blog import router as blog_router
app.include_router(blog_router)
from routes.referral import router as referral_router
app.include_router(referral_router)

# Conversational onboarding registration removed - feature not implemented

# Test panel removed - no longer needed

# Add additional routes
from routes.weekly_insights import weekly_insights_router
from routes.settings import settings_router, unsubscribe_router
app.include_router(weekly_insights_router)
app.include_router(settings_router)
app.include_router(unsubscribe_router)

# Add WebSocket endpoint
from routes.websocket import websocket_endpoint
app.websocket("/ws")(lambda websocket: websocket_endpoint(websocket, app))

# Debug logging after route registration
# print(f"[CORA] Total routes registered: {len(app.routes)}")
# print(f"[CORA] Admin routes: {[r.path for r in app.routes if hasattr(r, 'path') and 'admin' in str(r.path)]}")
# print(f"[CORA] Onboarding routes: {[r.path for r in app.routes if hasattr(r, 'path') and 'onboarding' in str(r.path)]}")

# Module-level server start time
server_start_time = datetime.now()

# Start backup scheduler on application startup
try:
    start_backup_scheduler_on_startup()
#     print("[CORA] Backup scheduler started successfully")
except (ImportError, RuntimeError, AttributeError) as e:
    print(f"[CORA] Failed to start backup scheduler: {e}")

# Start business task scheduler on application startup
try:
    from services.task_scheduler import start_task_scheduler
    start_task_scheduler()
#     print("[CORA] Business task scheduler started successfully")
except (ImportError, RuntimeError, AttributeError) as e:
    print(f"[CORA] Failed to start business task scheduler: {e}")

# Landing page is handled by routes/pages.py

# Health check
@app.get("/health")
async def health_check():
    """Basic health check endpoint"""
    return {"status": "healthy", "version": "4.0.0"}

@app.get("/api/health")
async def api_health_check():
    """API health check endpoint"""
    return {"status": "healthy", "version": "4.0.0"}

@app.get("/api/health/detailed")
async def detailed_health_check(db: Session = Depends(get_db)):
    """Detailed health check with component status"""
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "checks": {},
        "metrics": {}
    }
    
    # Check database connection
    try:
        db.execute(text("SELECT 1"))
        health_status["checks"]["database"] = True
    except (DatabaseError, OperationalError, SQLAlchemyError) as e:
        health_status["checks"]["database"] = False
        health_status["status"] = "degraded"
#         print(f"Database health check failed: {str(e)}")
    
    # Check Redis connection
    try:
        redis_manager.client.ping()
        health_status["checks"]["redis"] = True
    except (ConnectionError, TimeoutError, AttributeError) as e:
        health_status["checks"]["redis"] = False
        health_status["status"] = "degraded"
#         print(f"Redis health check failed: {str(e)}")
    
    # Check Sentry status
    try:
        health_status["checks"]["sentry"] = sentry_sdk is not None and sentry_sdk.Hub.current.client is not None
    except (AttributeError, RuntimeError) as e:
        health_status["checks"]["sentry"] = False
#         print(f"Sentry health check error: {str(e)}")
    
    # Calculate uptime
    uptime_seconds = int((datetime.now() - server_start_time).total_seconds())
    health_status["metrics"]["uptime_seconds"] = uptime_seconds
    health_status["metrics"]["uptime_human"] = f"{uptime_seconds // 3600}h {(uptime_seconds % 3600) // 60}m"
    
    return health_status

# Legacy endpoint compatibility and API shims
# Redirect old endpoints to current ones to eliminate 404s without touching frontend immediately
@app.post("/api/cora-chat-v2/")
async def redirect_chat_v2(request: Request):
    """Redirect legacy chat v2 endpoint to the active CORA AI chat endpoint.
    Uses 307 to preserve method and body.
    """
    try:
        # Read body to avoid client issues with some proxies dropping body on redirect
        # Body is not used here but reading ensures compatibility
        await request.body()
    except Exception:
        pass
    return RedirectResponse(url="/api/cora-ai/chat", status_code=307)

@app.post("/api/signup")
async def redirect_legacy_signup():
    """Redirect legacy signup endpoint to the current auth register endpoint."""
    return RedirectResponse(url="/api/auth/register", status_code=307)

# Predictive intelligence insights (frontend expects this convenience endpoint)
@app.get("/api/predictive-intelligence/insights")
async def predictive_intelligence_insights(
    request: Request,
    db: Session = Depends(get_db)
):
    """Return predictive intelligence insights unified for dashboard consumption.
    Auth handled inside orchestrator via current session/cookie if present.
    """
    try:
        # Attempt to get current user; fall back to anonymous-safe orchestration
        from dependencies.auth import get_current_user_optional
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
            "intelligence_score": unified.get("intelligence_score", 0)
        }
        return JSONResponse(payload)
    except Exception as e:
        # Graceful fallback
        return JSONResponse({
            "insights": [],
            "predictions": [],
            "recommendations": [],
            "error": "Predictive intelligence unavailable"
        }, status_code=200)

# --- NEW ENDPOINT ---
@app.get("/api/status")
async def api_status():
    """Return server status and basic stats"""
    now = datetime.now()
    uptime_delta = now - server_start_time
    # Format uptime as human-readable string
    hours, remainder = divmod(int(uptime_delta.total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)
    if hours > 0:
        uptime = f"{hours}h {minutes}m"
    elif minutes > 0:
        uptime = f"{minutes}m {seconds}s"
    else:
        uptime = f"{seconds}s"
    # Count .py files in CORA directory
    cora_dir = Path(__file__).parent
    total_files = sum(1 for f in cora_dir.glob('*.py'))
    return {
        "status": "healthy",
        "version": "4.0",
        "uptime": uptime,
        "timestamp": now.isoformat(),
        "total_files": total_files
    }

# Email capture endpoint
@app.post("/api/v1/capture-email")
async def capture_email(email: str = Form(...), db: Session = Depends(get_db)):
    """Capture email addresses from landing page - saves to database"""
    from models.waitlist import ContractorWaitlist
    
    try:
        # Check if email already exists
        existing = db.query(ContractorWaitlist).filter(
            ContractorWaitlist.email == email.lower().strip()
        ).first()
        
        if existing:
            # Update the timestamp if they're signing up again
            existing.updated_at = datetime.now()
            db.commit()
            message = "Welcome back! We've updated your spot on the list."
        else:
            # Create new waitlist entry
            new_entry = ContractorWaitlist(
                name="",  # We'll get this during onboarding
                email=email.lower().strip(),
                source="landing_page_hero",
                source_details="Hero section email capture",
                status="pending"
            )
            db.add(new_entry)
            db.commit()
            message = "Email captured successfully!"
        
        # Return JSON response for JavaScript handler
        return JSONResponse({
            "success": True,
            "message": message
        })
        
    except (DatabaseError, SQLAlchemyError, ValueError) as e:
        # Log the error but don't expose details to frontend
#         print(f"Error capturing email: {str(e)}")
        db.rollback()
        return JSONResponse({
            "success": False,
            "message": "Sorry, there was an error. Please try again."
        }, status_code=500)

@app.post("/api/v1/lead-capture")
async def lead_capture(
    email: str = Form(...),
    business_name: str = Form(...),
    platform_type: str = Form(...),
    monthly_transactions: str = Form(...),
    db: Session = Depends(get_db)
):
    """Capture detailed lead information from landing page form"""
    try:
        from models.waitlist import ContractorWaitlist
        
        # Check if email already exists
        existing = db.query(ContractorWaitlist).filter(
            ContractorWaitlist.email == email.lower().strip()
        ).first()
        
        if existing:
            # Update existing entry with new details
            existing.company_name = business_name
            existing.business_type = platform_type
            existing.team_size = monthly_transactions  # Using team_size field for volume
            existing.source = "landing_page_form"
            existing.source_details = "Detailed lead form submission"
            existing.updated_at = datetime.now()
            message = "Lead information updated successfully!"
        else:
            # Create new detailed lead entry
            new_lead = ContractorWaitlist(
                name="",  # Will be filled during onboarding
                email=email.lower().strip(),
                company_name=business_name,
                business_type=platform_type,
                team_size=monthly_transactions,  # Jobs per month maps to team_size field
                source="landing_page_form",
                source_details="Detailed lead form submission",
                status="pending"
            )
            db.add(new_lead)
            message = "Lead captured successfully!"
        
        db.commit()
        
        # Return success response with redirect info
        return JSONResponse({
            "success": True,
            "message": message,
            "redirect": f"/signup?email={email}&company={business_name}"
        })
        
    except (DatabaseError, SQLAlchemyError, ValueError) as e:
        db.rollback()
#         print(f"Error capturing lead: {str(e)}")
        return JSONResponse({
            "success": False,
            "message": "Sorry, there was an error. Please try again."
        }, status_code=500)

# Robots.txt for search engines
@app.get("/robots.txt")
async def robots():
    """Serve robots.txt"""
    return FileResponse("web/static/robots.txt")

# === CSP FIX ENDPOINT REMOVED FOR SECURITY ===
# The /fix-csp endpoint has been removed as it allowed runtime modification
# of security headers, which is a security vulnerability.
# CSP headers should be configured properly in middleware/security_headers.py

# Pydantic models for signup
class SignupRequest(BaseModel):
    email: EmailStr
    password: str
    password_confirm: str
    signup_source: str = "web"
    referral_code: Optional[str] = None

class SignupResponse(BaseModel):
    success: bool
    message: str
    user_id: int = None

## Deprecated endpoint removed: /api/signup (use /api/auth/register)

# Login endpoint removed - now handled by auth_coordinator.py

# Contact form endpoint
class ContactRequest(BaseModel):
    name: str
    company_name: str
    email: EmailStr
    phone: Optional[str] = None
    topic: str
    message: str

@app.post("/api/contact")
async def contact_form(request: ContactRequest, db: Session = Depends(get_db)):
    """Handle contact form submissions with enhanced security validation"""
    try:
        # Enhanced security validation
        try:
            # Sanitize all input fields
            sanitized_name = SecurityUtils.sanitize_input(request.name, max_length=100)
            sanitized_company = SecurityUtils.sanitize_input(request.company_name, max_length=100)
            sanitized_email = SecurityUtils.sanitize_input(request.email, max_length=255)
            sanitized_phone = SecurityUtils.sanitize_input(request.phone or "", max_length=20)
            sanitized_topic = SecurityUtils.sanitize_input(request.topic, max_length=100)
            sanitized_message = SecurityUtils.sanitize_input(request.message, max_length=2000)
            
            # Validate SQL safety
            SecurityUtils.validate_sql_safe(sanitized_name, "name")
            SecurityUtils.validate_sql_safe(sanitized_company, "company_name")
            SecurityUtils.validate_sql_safe(sanitized_email, "email")
            SecurityUtils.validate_sql_safe(sanitized_phone, "phone")
            SecurityUtils.validate_sql_safe(sanitized_topic, "topic")
            SecurityUtils.validate_sql_safe(sanitized_message, "message")
            
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
        
        # Log contact attempt (privacy-conscious)
        logger.info(f"Contact form submission from: {sanitized_email[:20]}...")
        
        # For now, just log and return success (email service can be configured later)
        logger.info(f"Contact form data received: {request.dict()}")
        
        # TODO: Add email service integration when SendGrid is configured
        # TODO: Add database storage for contact form submissions
        
        return {"success": True, "message": "Thank you for your message! We'll get back to you within 2 hours."}
            
    except (ValueError, TypeError, RuntimeError) as e:
        logger.error(f"Contact form error: {str(e)}")
        import traceback
        logger.error(f"Contact form traceback: {traceback.format_exc()}")
        return {"success": False, "message": "An error occurred. Please try again or contact us directly."}

# Email verification endpoint
@app.get("/verify-email")
async def verify_email_endpoint(token: str, db: Session = Depends(get_db)):
    """Verify user email address"""
    try:
        # Verify the token
        verification_successful = verify_email_token(db=db, token=token)
        
        if verification_successful:
            # Always redirect to onboarding after successful verification
            return RedirectResponse(url="/onboarding", status_code=302)
        else:
            raise HTTPException(status_code=400, detail="Verification failed")
            
    except InvalidCredentialsError as e:
        return HTMLResponse(f"""
        <html>
            <head>
                <title>Verification Failed - CORA</title>
                <style>
                    body {{ 
                        font-family: Inter, sans-serif; 
                        text-align: center; 
                        padding: 50px; 
                        background: #1a1a1a; 
                        color: #e2e8f0; 
                        margin: 0; 
                    }}
                    .container {{ 
                        max-width: 600px; 
                        margin: 0 auto; 
                        background: rgba(26, 26, 26, 0.95); 
                        padding: 3rem; 
                        border-radius: 8px; 
                        border: 1px solid rgba(255,82,82,0.3); 
                    }}
                    .error {{ 
                        background: linear-gradient(135deg, #FF5252, #F44336); 
                        color: white; 
                        padding: 2rem; 
                        border-radius: 8px; 
                        margin-bottom: 2rem; 
                    }}
                    .btn {{ 
                        background: #FF9800; 
                        color: #1a1a1a; 
                        padding: 1rem 2rem; 
                        text-decoration: none; 
                        border-radius: 4px; 
                        font-weight: 700; 
                        text-transform: uppercase; 
                        letter-spacing: 1px; 
                        display: inline-block; 
                        margin-top: 1rem; 
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="error">
                        <h1>✗ Verification Failed</h1>
                        <p>{str(e)}</p>
                    </div>
                    <p>The verification link may have expired or already been used.</p>
                    <a href="/signup" class="btn">Try Signing Up Again →</a>
                </div>
            </body>
        </html>
        """, status_code=400)
    except (DatabaseError, SQLAlchemyError, RuntimeError) as e:
        logger.error(f"Email verification error: {str(e)}")
        return HTMLResponse("""
        <html>
            <head><title>Error - CORA</title></head>
            <body style="font-family: sans-serif; text-align: center; padding: 50px;">
                <h1>Something went wrong</h1>
                <p>Please try again or contact support.</p>
                <a href="/">← Back to home</a>
            </body>
        </html>
        """, status_code=500)

# Resend verification email endpoint
@app.get("/resend-verification")
async def resend_verification_endpoint(email: str, db: Session = Depends(get_db)):
    """Resend verification email"""
    try:
        # Check if user exists and is not verified
        user = db.query(User).filter(User.email == email).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        if user.email_verified == "true":
            raise HTTPException(status_code=400, detail="Email already verified")
        
        # Create new verification token
        verification_token = create_email_verification_token(db=db, email=email)
        
        # Send verification email
        email_sent = send_email_verification(
            to_email=email,
            verification_token=verification_token,
            user_name=user.email.split('@')[0]  # Use email prefix as name
        )
        
        if email_sent:
            return {"success": True, "message": "Verification email sent successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to send verification email")
            
    except HTTPException:
        raise
    except (DatabaseError, SQLAlchemyError, RuntimeError) as e:
        logger.error(f"Resend verification error: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to resend verification email")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8001))
    # Single worker for easier debugging and Ctrl+C handling
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=False, workers=1)