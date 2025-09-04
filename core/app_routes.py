#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/core/app_routes.py
🎯 PURPOSE: Centralized router registration for FastAPI app
🔗 IMPORTS: All route modules and FastAPI app
📤 EXPORTS: register_routes function
"""

from fastapi import FastAPI
import logging

logger = logging.getLogger(__name__)


def register_routes(app: FastAPI) -> None:
    """
    Register all application routes with the FastAPI app.
    Centralized router registration to keep app.py under 300 lines.
    """
    
    # Import all routers
    from routes.auth_coordinator import auth_router
    from routes.expense_routes import expense_router
    from routes.payments import payment_router
    from routes.payment_coordinator import payment_router as payment_coordinator_router
    from routes.dashboard_routes import dashboard_router
    from routes.onboarding_routes import onboarding_router
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
    from tools.backup_manager import backup_api_router
    from routes.feedback_routes import feedback_router
    from routes.waitlist import waitlist_router
    from routes.sitemap import router as sitemap_router
    from routes.seo_pages import router as seo_pages_router
    from routes.blog import router as blog_router
    from routes.referral import router as referral_router
    from routes.weekly_insights import weekly_insights_router
    from routes.settings import settings_router
    from routes.unsubscribe_routes import unsubscribe_router
    from routes.user_settings import user_settings_router
    
    # Register all routers in the same order as original app.py
    app.include_router(auth_router)
    app.include_router(expense_router)
    app.include_router(payment_router)
    app.include_router(payment_coordinator_router)
    app.include_router(dashboard_router)
    app.include_router(onboarding_router)
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
    
    # Additional routers
    app.include_router(feedback_router)
    app.include_router(waitlist_router, prefix="/api/waitlist", tags=["waitlist"])
    
    # Chat routers
    app.include_router(cora_chat_router)
    app.include_router(cora_chat_enhanced_router)
    
    # SEO and content routers
    app.include_router(sitemap_router)
    app.include_router(seo_pages_router)
    app.include_router(blog_router)
    app.include_router(referral_router)
    
    # Settings and insights routers
    app.include_router(weekly_insights_router)
    app.include_router(settings_router)
    app.include_router(unsubscribe_router)
    app.include_router(user_settings_router)
    
    logger.info(f"Registered {len(app.routes)} routes")