#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/app.py
🎯 PURPOSE: FastAPI server - main application entry point (MINIMAL WORKING VERSION)
🔗 IMPORTS: FastAPI, StaticFiles, basic routes only
📤 EXPORTS: app (FastAPI instance)
"""

from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import json
from datetime import datetime
import logging

# Import our minimal async utilities
from utils.async_file_utils import async_read_json, async_write_json, async_ensure_dir

# Import routes
from routes import health_router, pages_router, auth_router, expense_router, payment_router
from routes.quickbooks_integration import quickbooks_router
from routes.stripe_integration import stripe_router
from routes.plaid_integration import plaid_router

# Import middleware
from middleware import setup_rate_limiting, setup_security_headers, setup_request_logging, setup_error_handlers

# Initialize FastAPI
app = FastAPI(
    title="CORA AI",
    description="AI Bookkeeping for Introverted Founders",
    version="4.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup middleware
setup_security_headers(app)
setup_error_handlers(app)
# setup_rate_limiting(app)  # Commented out until slowapi installed
# setup_request_logging(app)  # Commented out until logs directory exists

# Mount static files
static_dir = Path(__file__).parent / "web" / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
    logging.info(f"Mounted static files from {static_dir}")

# Include routers
app.include_router(health_router)
app.include_router(pages_router)
app.include_router(auth_router)
app.include_router(expense_router)
app.include_router(payment_router)
app.include_router(quickbooks_router)
app.include_router(stripe_router)
app.include_router(plaid_router)

# The health check is now handled by the health_router

# The root page is now handled by the pages_router

# Email Capture Route (existing functionality)
@app.post("/api/v1/capture-email")
async def capture_email(request: Request, email: str = Form(...)):
    """Capture email from landing page form"""
    try:
        # Create data directory if it doesn't exist
        data_dir = Path(__file__).parent / "data"
        await async_ensure_dir(data_dir)
        
        # Read existing emails or create new list
        email_file = data_dir / "captured_emails.json"
        emails = await async_read_json(email_file)
        
        # Add new email with timestamp
        emails.append({
            "email": email,
            "timestamp": datetime.now().isoformat(),
            "source": "landing_page"
        })
        
        # Save updated list
        await async_write_json(email_file, emails)
        
        # Return success as JSON for AJAX requests
        if request.headers.get("accept") == "application/json":
            return JSONResponse({
                "status": "success",
                "message": "Thank you! We'll notify you when CORA launches."
            })
        
        # Return HTML for form submissions
        return HTMLResponse(f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Thank You - CORA</title>
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    min-height: 100vh;
                    margin: 0;
                    background-color: #f8f9fa;
                }}
                .message {{
                    text-align: center;
                    padding: 40px;
                    background: white;
                    border-radius: 8px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }}
                h1 {{ color: #7c3aed; }}
                a {{
                    color: #7c3aed;
                    text-decoration: none;
                }}
            </style>
        </head>
        <body>
            <div class="message">
                <h1>✅ Thank You!</h1>
                <p>We've captured your email: <strong>{email}</strong></p>
                <p>We'll notify you as soon as CORA is ready!</p>
                <p><a href="/">← Back to Home</a></p>
            </div>
        </body>
        </html>
        """)
        
    except Exception as e:
        logging.error(f"Failed to capture email: {e}")
        return JSONResponse({
            "status": "error",
            "message": "Failed to capture email"
        }, status_code=500)

# Startup event
@app.on_event("startup")
async def startup_event():
    """Simple startup tasks"""
    logging.basicConfig(level=logging.INFO)
    logging.info("CORA AI starting up - minimal working version")
    logging.info("Run 'python app.py' to start the server")

# Run server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)