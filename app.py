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

from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import json
from datetime import datetime, timedelta
import os
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from middleware.rate_limit import setup_rate_limiting
from middleware.security_headers import setup_security_headers
from middleware.logging_middleware import setup_request_logging
from middleware.error_handler import setup_error_handlers
from middleware.user_activity import setup_user_activity

# Initialize Sentry for error tracking
sentry_dsn = os.getenv('SENTRY_DSN')
if sentry_dsn:
    sentry_sdk.init(
        dsn=sentry_dsn,
        integrations=[FastApiIntegration()],
        traces_sample_rate=0.1,
        environment=os.getenv('ENVIRONMENT', 'production')
    )

# Import all existing route modules
from routes.auth_coordinator import auth_router
from routes.expenses import expense_router
from routes.payments import payment_router
from routes.dashboard_routes import dashboard_router
from routes.onboarding_routes import onboarding_router
from routes.admin_routes import admin_router
from routes.plaid_integration import plaid_router
from routes.quickbooks_integration import quickbooks_router
from routes.stripe_integration import stripe_router
from routes.pages import router as pages_router

# Debug logging for route registration
print(f"[CORA] Admin router imported: {admin_router}")
print(f"[CORA] Admin router routes: {len(admin_router.routes)}")
print(f"[CORA] Onboarding router imported: {onboarding_router}")
print(f"[CORA] Onboarding router routes: {len(onboarding_router.routes)}")

# Initialize FastAPI
app = FastAPI(
    title="Cora AI",
    description="AI Bookkeeping for Introverted Founders", 
    version="4.0.0"
)

# CORS settings
PROD_ORIGINS = [
    "https://coraai.tech",
    "https://www.coraai.tech"
]
DEV_ORIGINS = [
    "http://localhost",
    "http://localhost:8000",
    "http://127.0.0.1:8000"
]

origins = PROD_ORIGINS + DEV_ORIGINS

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# === SECURITY & LOGGING MIDDLEWARE ===
setup_rate_limiting(app)
setup_security_headers(app)
setup_request_logging(app)
setup_error_handlers(app)
setup_user_activity(app)

# Setup templates
templates_dir = Path(__file__).parent / "web" / "templates"
templates = Jinja2Templates(directory=str(templates_dir))

# Mount static files
static_dir = Path(__file__).parent / "web" / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Include all existing route modules
app.include_router(auth_router)
app.include_router(expense_router)
app.include_router(payment_router)
app.include_router(dashboard_router)
app.include_router(onboarding_router)
app.include_router(admin_router)
app.include_router(plaid_router)
app.include_router(quickbooks_router)
app.include_router(stripe_router)
app.include_router(pages_router)

# Debug logging after route registration
print(f"[CORA] Total routes registered: {len(app.routes)}")
print(f"[CORA] Admin routes: {[r.path for r in app.routes if hasattr(r, 'path') and 'admin' in str(r.path)]}")
print(f"[CORA] Onboarding routes: {[r.path for r in app.routes if hasattr(r, 'path') and 'onboarding' in str(r.path)]}")

# Module-level server start time
server_start_time = datetime.now()

# Basic route
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Serve the landing page"""
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "title": "Cora AI - AI Bookkeeping"}
    )

# Health check
@app.get("/health")
async def health_check():
    """Basic health check endpoint"""
    return {"status": "healthy", "version": "4.0.0"}

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
async def capture_email(email: str = Form(...)):
    """Capture email addresses from landing page"""
    # For now, just save to a JSON file (later: database)
    emails_file = Path(__file__).parent / "captured_emails.json"
    
    # Load existing emails or create new list
    if emails_file.exists():
        with open(emails_file, 'r') as f:
            emails = json.load(f)
    else:
        emails = []
    
    # Add new email
    emails.append({
        "email": email,
        "timestamp": datetime.now().isoformat(),
        "source": "landing_page_v4"
    })
    
    # Save back to file
    with open(emails_file, 'w') as f:
        json.dump(emails, f, indent=2)
    
    # Return success page (later: proper thank you page)
    return HTMLResponse("""
    <html>
        <head>
            <title>Thanks! - Cora AI</title>
            <style>
                body { font-family: sans-serif; text-align: center; padding: 50px; }
                .message { background: #8B00FF; color: white; padding: 20px; border-radius: 10px; display: inline-block; }
                a { color: #8B00FF; }
            </style>
        </head>
        <body>
            <div class="message">
                <h1>You're on the list!</h1>
                <p>We'll notify you when Cora AI launches.</p>
            </div>
            <p style="margin-top: 20px;">
                <a href="/">← Back to home</a>
            </p>
        </body>
    </html>
    """)

# Robots.txt for search engines
@app.get("/robots.txt")
async def robots():
    """Serve robots.txt for search engines"""
    return FileResponse("web/static/robots.txt", media_type="text/plain")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)