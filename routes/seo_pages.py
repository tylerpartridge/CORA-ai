"""
SEO-Optimized Landing Pages for High-Value Keywords
Targets blue ocean opportunities and pain point keywords
"""
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
import os

router = APIRouter()
# Use centralized templates from app.state.templates set in app.py

# Real-Time Profit Tracking Landing Page
@router.get("/real-time-profit-tracking", response_class=HTMLResponse)
async def real_time_profit_tracking(request: Request):
    """Landing page for 'real time construction profit tracking' keyword"""
    return request.app.state.templates.TemplateResponse("seo/real-time-profit-tracking.html", {
        "request": request,
        "title": "Real-Time Construction Profit Tracking | CORA AI",
        "description": "Track construction job profits in real-time with instant alerts. Never lose money on a job again with CORA's AI-powered profit tracking.",
        "keywords": "real time construction profit tracking, live job costing, instant profit alerts"
    })

# Voice Input Construction Software
@router.get("/voice-input-construction", response_class=HTMLResponse)
async def voice_input_construction(request: Request):
    """Landing page for 'voice input construction software' keyword"""
    return request.app.state.templates.TemplateResponse("seo/voice-input-construction.html", {
        "request": request,
        "title": "Voice Input Construction Software | Track Expenses Hands-Free",
        "description": "Update job costs with voice commands. Perfect for construction sites when your hands are dirty. CORA's voice AI understands construction terminology.",
        "keywords": "voice input construction software, hands free job tracking, voice expense tracking"
    })

# Lost Money on Construction Job
@router.get("/why-construction-jobs-lose-money", response_class=HTMLResponse)
async def why_jobs_lose_money(request: Request):
    """Landing page for 'lost money on construction job' pain point"""
    return request.app.state.templates.TemplateResponse("seo/why-jobs-lose-money.html", {
        "request": request,
        "title": "Why 73% of Construction Jobs Lose Money | Stop Profit Leaks",
        "description": "Discover the 5 hidden reasons construction jobs go over budget and how CORA's AI alerts prevent profit loss before it happens.",
        "keywords": "lost money construction job, construction job over budget, construction profit loss"
    })

# Mobile Job Costing
@router.get("/mobile-job-costing", response_class=HTMLResponse)
async def mobile_job_costing(request: Request):
    """Landing page for 'mobile construction job costing' keyword"""
    return request.app.state.templates.TemplateResponse("seo/mobile-job-costing.html", {
        "request": request,
        "title": "Mobile Construction Job Costing App | Track Profits Anywhere",
        "description": "Track job costs from your phone on any construction site. Real-time profit updates, voice input, and instant budget alerts.",
        "keywords": "mobile construction job costing, construction app contractors, job costing app"
    })

# AI Budget Alerts
@router.get("/ai-budget-alerts", response_class=HTMLResponse)
async def ai_budget_alerts(request: Request):
    """Landing page for 'construction AI financial alerts' keyword"""
    return request.app.state.templates.TemplateResponse("seo/ai-budget-alerts.html", {
        "request": request,
        "title": "AI Construction Budget Alerts | Never Go Over Budget Again",
        "description": "CORA's AI predicts budget overruns before they happen. Get instant alerts when jobs are at risk of losing money.",
        "keywords": "AI construction budget alerts, construction financial alerts, budget overrun prevention"
    })

# Location-Specific Pages
@router.get("/texas-contractors", response_class=HTMLResponse)
async def texas_contractors(request: Request):
    """Local SEO page for Texas contractors"""
    return request.app.state.templates.TemplateResponse("seo/location/texas-contractors.html", {
        "request": request,
        "title": "Construction Profit Tracking for Texas Contractors | CORA",
        "description": "Built for Texas construction companies. Track job profits in real-time, get instant alerts, and never lose money on Houston, Dallas, or Austin projects.",
        "keywords": "Texas construction software, Houston contractor tools, Dallas job costing"
    })

@router.get("/florida-construction-software", response_class=HTMLResponse)
async def florida_construction(request: Request):
    """Local SEO page for Florida contractors"""
    return request.app.state.templates.TemplateResponse("seo/location/florida-construction.html", {
        "request": request,
        "title": "Florida Construction Job Costing Software | Miami to Orlando",
        "description": "Construction profit tracking designed for Florida's unique challenges. From Miami high-rises to Orlando commercial projects.",
        "keywords": "Florida construction software, Miami contractor tools, Orlando job tracking"
    })

@router.get("/california-contractor-tools", response_class=HTMLResponse)
async def california_contractors(request: Request):
    """Local SEO page for California contractors"""
    return request.app.state.templates.TemplateResponse("seo/location/california-contractors.html", {
        "request": request,
        "title": "California Construction Profit Tracking | LA to SF Bay Area",
        "description": "Built for California contractors dealing with high costs and tight margins. Track profits in real-time from Los Angeles to San Francisco.",
        "keywords": "California construction software, Los Angeles contractor tools, Bay Area job costing"
    })

@router.get("/new-york-construction-profit-tracking", response_class=HTMLResponse)
async def new_york_construction(request: Request):
    """Local SEO page for New York contractors"""
    return request.app.state.templates.TemplateResponse("seo/location/new-york-construction.html", {
        "request": request,
        "title": "NYC Construction Profit Tracking | Real-Time Job Costing",
        "description": "New York construction profit tracking that keeps up with the city's pace. From Manhattan renovations to Brooklyn developments.",
        "keywords": "NYC construction software, New York contractor tools, Manhattan job tracking"
    })