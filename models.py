"""
Compatibility module for legacy imports
All models are now organized in the /models/ package
This file ensures compatibility with health checks and legacy code
"""

# Import everything from the models package
from models import *

# Ensure all models are accessible at the root level
__all__ = [
    'Base', 'engine', 'SessionLocal', 'get_db',
    'User', 'Expense', 'ExpenseCategory', 
    'Customer', 'Subscription', 'Payment',
    'BusinessProfile', 'UserPreference', 'PasswordResetToken', 'EmailVerificationToken',
    'PlaidIntegration', 'PlaidAccount', 'PlaidTransaction', 'PlaidSyncHistory',
    'QuickBooksIntegration', 'StripeIntegration', 'Feedback', 'UserActivity',
    'Job', 'JobNote', 'ContractorWaitlist', 'JobAlert', 'AnalyticsLog', 'PredictionFeedback'
]