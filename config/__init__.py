# Back-compat shim so old imports keep working after moving config.py -> config/config.py
from .config import *  # re-export anything defined in config/config.py

# Ensure DATABASE_URL is available at module level for legacy code
try:
    DATABASE_URL  # defined in .config?
except NameError:
    try:
        from .config import settings  # pydantic BaseSettings style
        DATABASE_URL = getattr(settings, "DATABASE_URL", None)
    except Exception:
        import os
        DATABASE_URL = os.getenv("DATABASE_URL")
