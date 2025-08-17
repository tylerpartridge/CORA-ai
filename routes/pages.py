#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/routes/pages.py
🎯 PURPOSE: Page serving routes - minimal safe implementation
🔗 IMPORTS: FastAPI router, HTMLResponse
📤 EXPORTS: router with page endpoints
"""

from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from dependencies.auth import get_current_user
from dependencies.auth_hybrid import get_current_user_hybrid
from models import get_db
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent.parent))

# Create router
router = APIRouter(
    tags=["Pages"],
    responses={404: {"description": "Not found"}},
)

# Templates now provided centrally by app.py via request.app.state.templates

# Test routes removed - use /dashboard for testing

@router.get("/")
async def root_page(request: Request):
    """Serve the main landing page"""
    return request.app.state.templates.TemplateResponse("index.html", {"request": request})

@router.get("/admin/feature-flags", response_class=HTMLResponse)
async def feature_flags_admin(request: Request):
    """Admin UI for managing feature flags"""
    return request.app.state.templates.TemplateResponse("admin/feature-flags.html", {"request": request})

@router.get("/about")
async def about_page(request: Request):
    """Serve about page"""
    return request.app.state.templates.TemplateResponse("about.html", {"request": request})

@router.get("/intelligence-demo")
async def intelligence_demo_redirect():
    """Redirect to intelligence orchestration demo"""
    return RedirectResponse(url="/api/intelligence/demo")

@router.get("/demo")
async def demo_redirect():
    """Redirect to intelligence orchestration demo (short link)"""
    return RedirectResponse(url="/api/intelligence/demo")

@router.get("/test-routes")
async def test_routes_page():
    """Route testing page for debugging"""
    template_path = Path(__file__).parent.parent / "web" / "templates" / "route_test.html"
    if template_path.exists():
        with open(template_path, 'r', encoding='utf-8') as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="<h1>Route Test - Page Not Found</h1>")

@router.get("/profit-intelligence")
async def profit_intelligence_page():
    """Serve profit intelligence page"""
    template_path = Path(__file__).parent.parent / "web" / "templates" / "profit_intelligence.html"
    if template_path.exists():
        with open(template_path, 'r', encoding='utf-8') as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="<h1>Profit Intelligence - Page Not Found</h1>")

@router.get("/insights")
async def insights_dashboard_page():
    """Serve AI insights dashboard page"""
    template_path = Path(__file__).parent.parent / "web" / "templates" / "insights_dashboard.html"
    if template_path.exists():
        with open(template_path, 'r', encoding='utf-8') as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="<h1>AI Insights Dashboard - Page Not Found</h1>")

@router.get("/analytics")
async def user_analytics_page():
    """Serve user analytics dashboard page"""
    template_path = Path(__file__).parent.parent / "web" / "templates" / "user_analytics.html"
    if template_path.exists():
        with open(template_path, 'r', encoding='utf-8') as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="<h1>User Analytics Dashboard - Page Not Found</h1>")

@router.get("/cora-personality-demo")
async def cora_personality_demo():
    """Serve CORA personality demo page"""
    template_path = Path(__file__).parent.parent / "web" / "templates" / "cora_personality_demo.html"
    if template_path.exists():
        with open(template_path, 'r', encoding='utf-8') as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="<h1>CORA Personality Demo - Page Not Found</h1>")

@router.get("/unified-ai-demo")
async def unified_ai_demo():
    """Serve unified AI intelligence demo page"""
    template_path = Path(__file__).parent.parent / "web" / "templates" / "unified_ai_demo.html"
    if template_path.exists():
        with open(template_path, 'r', encoding='utf-8') as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="<h1>Unified AI Demo - Page Not Found</h1>")

@router.get("/test-demo")
async def test_demo_page():
    """Serve test demo page for debugging"""
    template_path = Path(__file__).parent.parent / "test_demo_page.html"
    if template_path.exists():
        with open(template_path, 'r', encoding='utf-8') as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="<h1>Test Demo - Page Not Found</h1>")

@router.get("/debug-demo")
async def debug_demo_page():
    """Serve debug demo page for troubleshooting"""
    template_path = Path(__file__).parent.parent / "debug_demo.html"
    if template_path.exists():
        with open(template_path, 'r', encoding='utf-8') as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="<h1>Debug Demo - Page Not Found</h1>")

@router.get("/contact")
async def contact_page(request: Request):
    """Serve contact page"""
    return request.app.state.templates.TemplateResponse("contact.html", {"request": request})

@router.get("/pricing")
async def pricing_page(request: Request):
    """Serve pricing page"""
    return request.app.state.templates.TemplateResponse("pricing.html", {"request": request})

@router.get("/select-plan")
async def select_plan_page(request: Request):
    """Plan selection page - shown after signup, before onboarding"""
    return request.app.state.templates.TemplateResponse("select-plan.html", {"request": request})

@router.get("/help/knowledge-base", response_class=HTMLResponse)
async def knowledge_base_page(request: Request):
    return request.app.state.templates.TemplateResponse("help/knowledge-base.html", {"request": request})

@router.get("/subscription")
async def subscription_page(request: Request, status: str = "", session_id: str = ""):
    """Subscription status/landing page for checkout redirects"""
    return request.app.state.templates.TemplateResponse(
        "subscription.html",
        {"request": request, "status": status, "session_id": session_id}
    )

@router.get("/features")
async def features_page(request: Request):
    """Serve features page"""
    return request.app.state.templates.TemplateResponse("features.html", {"request": request})

@router.get("/referral", response_class=HTMLResponse)
async def referral_dashboard(request: Request):
    return request.app.state.templates.TemplateResponse("referral.html", {"request": request})

@router.get("/signup-clean")
async def signup_clean():
    """Clean signup page for testing"""
    template_path = Path(__file__).parent.parent / "web" / "templates" / "signup_clean.html"
    if template_path.exists():
        with open(template_path, 'r', encoding='utf-8') as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="<h1>Signup Clean - Page Not Found</h1>")

@router.get("/nav-test")
async def nav_test(request: Request):
    """Navigation test page"""
    return request.app.state.templates.TemplateResponse("nav-test.html", {"request": request})

@router.get("/test-inheritance")
async def test_inheritance(request: Request):
    """Test template inheritance system"""
    return request.app.state.templates.TemplateResponse("test_inheritance.html", {"request": request})

@router.get("/how-it-works")
async def how_it_works_page(request: Request):
    """Serve how it works page"""
    return request.app.state.templates.TemplateResponse("how-it-works.html", {"request": request})

@router.get("/reviews")
async def reviews_page(request: Request):
    """Serve reviews page"""
    return request.app.state.templates.TemplateResponse("reviews.html", {"request": request})

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

@router.get("/integrations")
async def integrations_page():
    """Serve integrations overview page"""
    return HTMLResponse(content="""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Integrations - CORA AI</title>
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                max-width: 800px;
                margin: 0 auto;
                padding: 40px 20px;
                background: #0a0a0a;
                color: #ffffff;
            }
            h1 { color: #FF9800; }
            .integration-card {
                background: #1a1a1a;
                border: 1px solid #FF9800;
                border-radius: 8px;
                padding: 20px;
                margin: 20px 0;
                transition: all 0.3s ease;
            }
            .integration-card:hover {
                box-shadow: 0 4px 20px rgba(255,152,0,0.3);
            }
            a { color: #4db8ff; text-decoration: none; }
            a:hover { text-decoration: underline; }
        </style>
    </head>
    <body>
        <h1>Integrations</h1>
        <p>Connect CORA with your favorite tools.</p>
        
        <div class="integration-card">
            <h3>QuickBooks</h3>
            <p>Sync your expenses and invoices automatically.</p>
            <a href="/integrations/quickbooks">Learn More →</a>
        </div>
        
        <div class="integration-card">
            <h3>Plaid</h3>
            <p>Connect your bank accounts securely.</p>
            <a href="/integrations/plaid">Learn More →</a>
        </div>
        
        <div class="integration-card">
            <h3>Stripe</h3>
            <p>Accept payments and track revenue.</p>
            <a href="/integrations/stripe">Learn More →</a>
        </div>
        
        <p><a href="/">← Back to Home</a></p>
    </body>
    </html>
    """)

@router.get("/integrations/plaid", response_class=HTMLResponse)
async def integrations_plaid_page(request: Request):
    """Serve the Plaid integration page"""
    return request.app.state.templates.TemplateResponse("integrations/plaid.html", {"request": request})

# Redirect old dashboard URLs to unified dashboard
@router.get("/plaid-dashboard")
async def plaid_dashboard_redirect():
    """Redirect to unified dashboard"""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/dashboard", status_code=301)

@router.get("/jobs")
async def jobs_redirect():
    """Redirect to unified dashboard"""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/dashboard", status_code=301)

@router.get("/waitlist", response_class=HTMLResponse)
async def waitlist_page(request: Request):
    """Serve the contractor waitlist signup page"""
    return request.app.state.templates.TemplateResponse("waitlist.html", {"request": request})

@router.get("/dashboard")
async def dashboard(request: Request):
    """Serve the mobile-first dashboard (authenticated users only)"""
    try:
        # Try to get user with hybrid auth (cookie or header)
        from dependencies.auth_hybrid import get_current_user_hybrid
        current_user = await get_current_user_hybrid(request, None, next(get_db()))
        # Use the actual dashboard template that exists
        return request.app.state.templates.TemplateResponse("core_protected/dashboard.html", {
            "request": request,
            "user": current_user
        })
    except (HTTPException, AttributeError) as e:

        # Log the actual error for debugging

        import logging

        logging.error(f"Dashboard access error: {e}")

        return RedirectResponse(url="/login", status_code=302)

# Legacy dashboard routes removed - using single dashboard_mobile_first.html


@router.get("/admin")
async def admin_dashboard(request: Request):
    """Serve the admin dashboard page"""
    template_path = Path(__file__).parent.parent / "web" / "templates" / "admin.html"
    if template_path.exists():
        with open(template_path, 'r', encoding='utf-8') as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="<h1>Admin Dashboard - Page Not Found</h1>")

@router.get("/terms")
async def terms_page(request: Request):
    """Serve Terms of Service page"""
    return request.app.state.templates.TemplateResponse("terms.html", {"request": request})

@router.get("/privacy")
async def privacy_page(request: Request):
    """Serve Privacy Policy page"""
    return request.app.state.templates.TemplateResponse("privacy.html", {"request": request})

@router.get("/receipt-upload")
async def receipt_upload_page(request: Request):
    """Serve the receipt upload page"""
    template_path = Path(__file__).parent.parent / "web" / "templates" / "receipt_upload.html"
    if template_path.exists():
        with open(template_path, 'r', encoding='utf-8') as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="<h1>Receipt Upload - Page Not Found</h1>")

@router.get("/receipts")
async def receipts_page(request: Request):
    """Serve the smart receipts page"""
    try:
        # Try to get user with hybrid auth (cookie or header)
        from dependencies.auth_hybrid import get_current_user_hybrid
        current_user = await get_current_user_hybrid(request, None, next(get_db()))
        
        template_path = Path(__file__).parent.parent / "web" / "templates" / "receipt_upload.html"
        if template_path.exists():
            with open(template_path, 'r', encoding='utf-8') as f:
                return HTMLResponse(content=f.read())
        return HTMLResponse(content="<h1>Smart Receipts - Page Not Found</h1>")
    except (HTTPException, AttributeError) as e:

        # Log the actual error for debugging

        import logging

        logging.error(f"Dashboard access error: {e}")

        return RedirectResponse(url="/login", status_code=302)

@router.get("/signup")
async def signup_page(request: Request):
    """Serve the signup page"""
    return request.app.state.templates.TemplateResponse("signup.html", {"request": request})

@router.get("/login")
async def login_page(request: Request):
    """Serve the login page"""
    return request.app.state.templates.TemplateResponse("login.html", {"request": request})

@router.get("/onboarding", response_class=HTMLResponse)
async def onboarding_page(request: Request):
    """Serve the AI-powered onboarding page (recommended entry point)"""
    return request.app.state.templates.TemplateResponse("onboarding-ai-wizard.html", {"request": request})





# Removed duplicate/broken onboarding routes - only /onboarding is needed

# Removed unused onboarding/connect-bank and onboarding/success routes

@router.get("/expenses")
async def expenses_page(request: Request):
    """Serve the expenses page with swipeable cards"""
    # Template doesn't exist, return a basic HTML page
    return HTMLResponse(content="""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Expenses - CORA AI</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link rel="stylesheet" href="/static/css/construction-theme.css">
    </head>
    <body>
        <div style="padding: 20px; text-align: center;">
            <h1 style="color: #FF9800;">Expenses</h1>
            <p>Expense tracking coming soon!</p>
            <a href="/dashboard" style="color: #FF9800;">Back to Dashboard</a>
        </div>
    </body>
    </html>
    """)

@router.get("/reports")
async def reports_page(request: Request):
    """Serve the reports page"""
    # Template doesn't exist, return a basic HTML page
    return HTMLResponse(content="""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Reports - CORA AI</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link rel="stylesheet" href="/static/css/construction-theme.css">
    </head>
    <body>
        <div style="padding: 20px; text-align: center;">
            <h1 style="color: #FF9800;">Reports</h1>
            <p>Report generation coming soon!</p>
            <a href="/dashboard" style="color: #FF9800;">Back to Dashboard</a>
        </div>
    </body>
    </html>
    """)

@router.get("/help")
async def help_page(request: Request):
    """Serve help page"""
    return request.app.state.templates.TemplateResponse("help.html", {"request": request})

# Blog route removed - handled by routes/blog.py with actual blog posts

@router.get("/demo")
async def demo_page():
    """Serve demo page"""
    return HTMLResponse(content="""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Demo - CORA AI</title>
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                max-width: 800px;
                margin: 0 auto;
                padding: 40px 20px;
                background: #0a0a0a;
                color: #ffffff;
            }
            h1 { color: #FF9800; }
            a { color: #4db8ff; text-decoration: none; }
            a:hover { text-decoration: underline; }
        </style>
    </head>
    <body>
        <h1>Request a Demo</h1>
        <p>See CORA in action with a personalized demo.</p>
        <p><a href="/contact">Contact Us for Demo</a></p>
        <p><a href="/">← Back to Home</a></p>
    </body>
    </html>
    """)

@router.get("/careers")
async def careers_page():
    """Serve careers page"""
    return HTMLResponse(content="""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Careers - CORA AI</title>
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                max-width: 800px;
                margin: 0 auto;
                padding: 40px 20px;
                background: #0a0a0a;
                color: #ffffff;
            }
            h1 { color: #FF9800; }
            a { color: #4db8ff; text-decoration: none; }
            a:hover { text-decoration: underline; }
        </style>
    </head>
    <body>
        <h1>Join Our Team</h1>
        <p>Build the future of construction technology with us.</p>
        <p><a href="/contact">Contact Us</a></p>
        <p><a href="/">← Back to Home</a></p>
    </body>
    </html>
    """)

@router.get("/press")
async def press_page():
    """Serve press page"""
    return HTMLResponse(content="""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Press - CORA AI</title>
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                max-width: 800px;
                margin: 0 auto;
                padding: 40px 20px;
                background: #0a0a0a;
                color: #ffffff;
            }
            h1 { color: #FF9800; }
            a { color: #4db8ff; text-decoration: none; }
            a:hover { text-decoration: underline; }
        </style>
    </head>
    <body>
        <h1>Press & Media</h1>
        <p>Latest news and press releases about CORA.</p>
        <p><a href="/contact">Media Inquiries</a></p>
        <p><a href="/">← Back to Home</a></p>
    </body>
    </html>
    """)

@router.get("/security")
async def security_page():
    """Serve security page"""
    return HTMLResponse(content="""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Security - CORA AI</title>
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                max-width: 800px;
                margin: 0 auto;
                padding: 40px 20px;
                background: #0a0a0a;
                color: #ffffff;
            }
            h1 { color: #FF9800; }
            a { color: #4db8ff; text-decoration: none; }
            a:hover { text-decoration: underline; }
        </style>
    </head>
    <body>
        <h1>Security & Privacy</h1>
        <p>Your data security is our top priority.</p>
        <p><a href="/privacy">Privacy Policy</a></p>
        <p><a href="/">← Back to Home</a></p>
    </body>
    </html>
    """)

@router.get("/forgot-password")
async def forgot_password_page():
    """Serve forgot password page"""
    return HTMLResponse(content="""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Forgot Password - CORA AI</title>
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                max-width: 800px;
                margin: 0 auto;
                padding: 40px 20px;
                background: #0a0a0a;
                color: #ffffff;
            }
            h1 { color: #FF9800; }
            a { color: #4db8ff; text-decoration: none; }
            a:hover { text-decoration: underline; }
        </style>
    </head>
    <body>
        <h1>Reset Your Password</h1>
        <p>Enter your email address and we'll send you a link to reset your password.</p>
        <p><a href="/login">← Back to Login</a></p>
    </body>
    </html>
    """)