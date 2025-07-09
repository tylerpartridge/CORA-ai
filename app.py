#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/app.py
🎯 PURPOSE: FastAPI server - serves landing page and captures emails
🔗 IMPORTS: FastAPI, Jinja2Templates, StaticFiles
📤 EXPORTS: app (FastAPI instance) 
🔄 PATTERN: Simple monolith (no premature abstractions)
📝 TODOS: Deploy to DigitalOcean, add /health endpoint

💡 AI HINT: This is the ONLY server file. Keep all routes here until we have 10+ endpoints.
⚠️ NEVER: Add business logic here. Just routing and basic validation.
"""

# Cora Version: 4.0
# Created: 2025-07-07
# Previous versions had 400+ files - keeping this one simple!

from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path
import json
from datetime import datetime, timedelta
import os

# Initialize FastAPI
app = FastAPI(
    title="Cora AI",
    description="AI Bookkeeping for Introverted Founders", 
    version="4.0.0"
)

# Setup templates
templates_dir = Path(__file__).parent / "web" / "templates"
templates = Jinja2Templates(directory=str(templates_dir))

# Mount static files
static_dir = Path(__file__).parent / "web" / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

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

# Health check endpoint for monitoring
@app.get("/health")
async def health_check():
    """Simple health check endpoint for uptime monitoring"""
    return {
        "status": "healthy",
        "version": "4.0.0",
        "service": "CORA AI"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)