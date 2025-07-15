# Routes package initialization
# Safe restoration - created by Cursor following Claude's plan

from .health import health_router
from .pages import router as pages_router
from .auth_coordinator import auth_router
from .expenses import expense_router
from .payments import payment_router

__all__ = ['health_router', 'pages_router', 'auth_router', 'expense_router', 'payment_router'] 