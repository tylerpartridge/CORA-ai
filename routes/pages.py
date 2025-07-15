#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/routes/pages.py
🎯 PURPOSE: Page serving routes - minimal safe implementation
🔗 IMPORTS: FastAPI router, HTMLResponse
📤 EXPORTS: router with page endpoints
"""

from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
from dependencies.auth import get_current_user

# Create router
router = APIRouter(
    tags=["Pages"],
    responses={404: {"description": "Not found"}},
)

# Setup templates
templates_dir = Path(__file__).parent.parent / "web" / "templates"
templates = Jinja2Templates(directory=str(templates_dir))

@router.get("/")
async def root_page():
    """Serve the main landing page"""
    template_path = Path(__file__).parent.parent / "web" / "templates" / "index.html"
    if template_path.exists():
        with open(template_path, 'r', encoding='utf-8') as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="<h1>CORA AI - System Starting</h1>")

@router.get("/about")
async def about_page():
    """Serve about page"""
    return HTMLResponse(content="""
    <!DOCTYPE html>
    <html>
    <head>
        <title>About - CORA AI</title>
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                max-width: 800px;
                margin: 0 auto;
                padding: 40px 20px;
            }
            h1 { color: #7c3aed; }
        </style>
    </head>
    <body>
        <h1>About CORA</h1>
        <p>AI-powered bookkeeping for founders who'd rather be building.</p>
        <p><a href="/">← Back to Home</a></p>
    </body>
    </html>
    """)

@router.get("/contact")
async def contact_page():
    """Serve contact page"""
    return HTMLResponse(content="""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Contact - CORA AI</title>
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                max-width: 800px;
                margin: 0 auto;
                padding: 40px 20px;
            }
            h1 { color: #7c3aed; }
        </style>
    </head>
    <body>
        <h1>Contact Us</h1>
        <p>Email: contact.cora.ai@gmail.com</p>
        <p><a href="/">← Back to Home</a></p>
    </body>
    </html>
    """)

@router.get("/pricing")
async def pricing_page():
    """Serve pricing page"""
    return HTMLResponse(content="""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Pricing - CORA AI</title>
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                max-width: 800px;
                margin: 0 auto;
                padding: 40px 20px;
            }
            h1 { color: #7c3aed; }
            .price { font-size: 2em; font-weight: bold; color: #7c3aed; }
        </style>
    </head>
    <body>
        <h1>Simple, Transparent Pricing</h1>
        <div class="price">$47/month</div>
        <p>Everything you need to automate your bookkeeping.</p>
        <ul>
            <li>Unlimited expense tracking</li>
            <li>QuickBooks integration</li>
            <li>Real-time insights</li>
            <li>AI categorization</li>
        </ul>
        <p><a href="/">← Back to Home</a></p>
    </body>
    </html>
    """)

@router.get("/integrations/quickbooks")
async def quickbooks_integration_page():
    """Serve QuickBooks integration page"""
    template_path = Path(__file__).parent.parent / "web" / "templates" / "integrations" / "quickbooks.html"
    if template_path.exists():
        with open(template_path, 'r', encoding='utf-8') as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="<h1>QuickBooks Integration - Page Not Found</h1>")

@router.get("/integrations/stripe")
async def stripe_integration_page():
    """Serve Stripe integration page"""
    template_path = Path(__file__).parent.parent / "web" / "templates" / "integrations" / "stripe.html"
    if template_path.exists():
        with open(template_path, 'r', encoding='utf-8') as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="<h1>Stripe Integration - Page Not Found</h1>")

@router.get("/integrations/plaid")
async def plaid_integration_page():
    """Serve Plaid integration page"""
    template_path = Path(__file__).parent.parent / "web" / "templates" / "integrations" / "plaid.html"
    if template_path.exists():
        with open(template_path, 'r', encoding='utf-8') as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="<h1>Plaid Integration - Page Not Found</h1>")

@router.get("/dashboard")
async def dashboard(request: Request, current_user: str = Depends(get_current_user)):
    """Serve the dashboard page"""
    return templates.TemplateResponse("dashboard.html", {"request": request, "user": current_user})

@router.get("/admin")
async def admin_dashboard(request: Request):
    """Serve the admin dashboard page"""
    template_path = Path(__file__).parent.parent / "web" / "templates" / "admin.html"
    if template_path.exists():
        with open(template_path, 'r', encoding='utf-8') as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="<h1>Admin Dashboard - Page Not Found</h1>")

@router.get("/terms")
async def terms_page():
    """Serve Terms of Service page"""
    template_path = Path(__file__).parent.parent / "web" / "templates" / "terms.html"
    if template_path.exists():
        with open(template_path, 'r', encoding='utf-8') as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="<h1>Terms of Service - Page Not Found</h1>")

@router.get("/privacy")
async def privacy_page():
    """Serve Privacy Policy page"""
    template_path = Path(__file__).parent.parent / "web" / "templates" / "privacy.html"
    if template_path.exists():
        with open(template_path, 'r', encoding='utf-8') as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="<h1>Privacy Policy - Page Not Found</h1>")