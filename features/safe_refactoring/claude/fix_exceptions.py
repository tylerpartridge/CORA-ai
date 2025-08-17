#!/usr/bin/env python3
"""Fix generic exception handlers"""

# Files to fix with line numbers:
FILES_TO_FIX = [
    ("routes\auth_coordinator.py", [268, 467]),
    ("routes\expenses.py", [179, 197]),
    ("routes\insights.py", [224]),
    ("routes\onboarding_routes.py", [376, 456]),
    ("routes\payment_coordinator.py", [386]),
    ("routes\performance_monitor.py", [345]),
    ("routes\voice_commands.py", [95, 128, 161]),
    ("routes\websocket.py", [68, 79, 93]),
    ("services\email_service.py", [47]),
    ("services\intelligence_orchestrator.py", [108]),
    ("services\predictive_intelligence.py", [420]),
    ("services\smart_receipts.py", [174, 176, 198]),
    ("utils\api_response_optimizer.py", [399, 427]),
    ("utils\db_optimizer.py", [53, 79, 86, 106]),
    ("utils\deployment_validator.py", [142, 321, 357]),
    ("utils\deployment_validator_simple.py", [95]),
    ("utils\materialized_views.py", [44, 70, 259]),
    ("utils\performance_monitor.py", [90]),
    ("utils\query_optimizer.py", [377, 387, 401]),
    ("utils\redis_manager.py", [56, 65, 74, 83]),
    ("middleware\csrf.py", [94]),
    ("middleware\file_upload_security.py", [246, 249]),
    ("middleware\rate_limiting.py", [106]),
    ("middleware\response_optimization.py", [73, 82]),
    ("middleware\security_headers_enhanced.py", [114]),
    ("middleware\user_activity.py", [55]),
    ("bulletproof_verification.py", [202]),
    ("check_db_schema.py", [62, 65]),
    ("code_quality_analysis.py", [106]),
    ("deploy_production.py", [136, 199, 211]),
    ("import_optimizer.py", [89]),
    ("production_optimization.py", [41, 88]),
    ("production_readiness_audit.py", [84, 93, 110, 120, 128, 157, 182, 207, 229, 236, 257, 263]),
    ("security_review.py", [31, 46, 69, 94]),
    ("test_complete_user_journey.py", [155, 400]),
    ("test_frontend_integration.py", [79]),
    ("test_integration_complete.py", [74, 97, 117, 173, 194, 231, 288, 320]),
    ("test_intelligence_route.py", [54]),
    ("test_onboarding_flow.py", [81, 153, 199, 209]),
    ("test_routes.py", [32]),
    ("test_which_cora.py", [29, 51]),
]

print("Files that need exception handler fixes:")
for filepath, lines in FILES_TO_FIX:
    print(f"{filepath}: lines {lines}")
