#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/routes/pages_secured.py
🎯 PURPOSE: Secured page routes with debug endpoint protection
🔗 IMPORTS: FastAPI router, environment checks
📤 EXPORTS: router with secured page endpoints
"""

import os
from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent.parent))

# Security: Check if we're in production
IS_PRODUCTION = os.getenv("ENVIRONMENT", "development").lower() == "production"
DEBUG_ENABLED = os.getenv("DEBUG", "false").lower() == "true"

# Create router
router = APIRouter(
    tags=["Pages"],
    responses={404: {"description": "Not found"}},
)

# Security wrapper for debug endpoints
async def require_debug_access():
    """Ensure debug endpoints are only accessible in development or with DEBUG flag"""
    if IS_PRODUCTION and not DEBUG_ENABLED:
        raise HTTPException(
            status_code=404, 
            detail="Not found"  # Don't reveal it's a debug endpoint
        )
    return True

# SECURED DEBUG ENDPOINTS

@router.get("/test-routes")
async def test_routes_page(debug_access: bool = Depends(require_debug_access)):
    """Route testing page for debugging - SECURED"""
    template_path = Path(__file__).parent.parent / "web" / "templates" / "route_test.html"
    if template_path.exists():
        with open(template_path, 'r', encoding='utf-8') as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="<h1>Route Test - Page Not Found</h1>")

@router.get("/test-demo")
async def test_demo_page(debug_access: bool = Depends(require_debug_access)):
    """Serve test demo page for debugging - SECURED"""
    template_path = Path(__file__).parent.parent / "test_demo_page.html"
    if template_path.exists():
        with open(template_path, 'r', encoding='utf-8') as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="<h1>Test Demo - Page Not Found</h1>")

@router.get("/debug-demo")
async def debug_demo_page(debug_access: bool = Depends(require_debug_access)):
    """Serve debug demo page for troubleshooting - SECURED"""
    template_path = Path(__file__).parent.parent / "debug_demo.html"
    if template_path.exists():
        with open(template_path, 'r', encoding='utf-8') as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="<h1>Debug Demo - Page Not Found</h1>")

@router.get("/test-inheritance")
async def test_inheritance(request: Request, debug_access: bool = Depends(require_debug_access)):
    """Test template inheritance system - SECURED"""
    return request.app.state.templates.TemplateResponse("test_inheritance.html", {"request": request})

@router.get("/nav-test")
async def nav_test(request: Request, debug_access: bool = Depends(require_debug_access)):
    """Navigation test page - SECURED"""
    return request.app.state.templates.TemplateResponse("nav-test.html", {"request": request})

# PUBLIC ENDPOINTS (no changes needed)

@router.get("/")
async def root_page(request: Request):
    """Serve the main landing page"""
    return request.app.state.templates.TemplateResponse("index.html", {"request": request})

@router.get("/about")
async def about_page(request: Request):
    """Serve about page"""
    return request.app.state.templates.TemplateResponse("about.html", {"request": request})

# ... rest of public endpoints remain the same ...