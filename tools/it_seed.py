"""
Seed a local SQLite DB for onboarding IT and emit a JWT access token.
Windows-safe; no shell heredocs needed.

Usage:
  # Optional: override the DB file
  set DATABASE_URL=sqlite:///./it_onboarding.db
  python tools/it_seed.py

Prints the token to STDOUT on success.
"""
from __future__ import annotations
import os
import sys
from pathlib import Path

# Ensure project root is on sys.path when running from tools/
ROOT = str(Path(__file__).resolve().parents[1])
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
from sqlalchemy import create_engine
from sqlalchemy.engine.url import make_url
from models.base import Base
from fastapi.testclient import TestClient


def ensure_schema(url: str) -> None:
    u = make_url(url)
    kwargs = {}
    if u.get_backend_name() == "sqlite":
        kwargs["connect_args"] = {"check_same_thread": False}
    engine = create_engine(url, **kwargs)
    Base.metadata.create_all(bind=engine)


def seed_and_token(url: str) -> str:
    # Ensure env hints are set before importing app
    os.environ["DATABASE_URL"] = url
    os.environ.setdefault("ENV", "testing")
    os.environ.setdefault("ENVIRONMENT", "testing")
    os.environ.setdefault("CORA_ENV", "testing")
    os.environ.setdefault("ALLOW_JWT_NO_AUD", "1")
    # Lazy import to bind app to the target DATABASE_URL
    import app as appmod  # noqa: WPS433  (runtime import by design for test binding)
    c = TestClient(appmod.app)
    email = "admin@coraai.tech"
    password = "ChangeMe123!"
    try:
        c.post(
            "/api/auth/register",
            json={"email": email, "password": password, "confirm_password": password},
        )
    except Exception:
        # Ignore if route enforces uniqueness and user exists
        pass
    r = c.post("/api/auth/login", json={"email": email, "password": password})
    # Prefer cookie (our JSON login sets HttpOnly cookie)
    tok = r.cookies.get("access_token") or ""
    if not tok:
        # Fallback to form endpoint which returns token in JSON
        r = c.post(
            "/api/auth/login-form",
            data={"username": email, "password": password},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        j = r.json() if r.headers.get("content-type", "").startswith("application/json") else {}
        tok = j.get("access_token", "")
    if not tok:
        raise SystemExit("ERROR: login returned no access_token")
    return tok


def main() -> None:
    url = os.getenv("DATABASE_URL", "sqlite:///./it_onboarding.db")
    # Bind env and import app before ensuring schema so metadata includes all models
    os.environ["DATABASE_URL"] = url
    # Import app now to load models with the correct engine binding
    import app as _  # noqa: F401
    ensure_schema(url)
    tok = seed_and_token(url)
    print(tok)


if __name__ == "__main__":
    main()


""" 
Seed a local SQLite DB for onboarding IT and emit a JWT access token.
Windows-safe; no shell heredocs needed.

Usage:
  # Optional: override the DB file
  set DATABASE_URL=sqlite:///./it_onboarding.db
  python tools/it_seed.py

Prints the token to STDOUT on success.
"""
from __future__ import annotations
import os
from sqlalchemy import create_engine
from sqlalchemy.engine.url import make_url
from models.base import Base
from fastapi.testclient import TestClient
import app as appmod

def ensure_schema(url: str) -> None:
    u = make_url(url)
    kwargs = {}
    if u.get_backend_name() == "sqlite":
        kwargs["connect_args"] = {"check_same_thread": False}
    engine = create_engine(url, **kwargs)
    Base.metadata.create_all(bind=engine)

def seed_and_token(url: str) -> str:
    os.environ["DATABASE_URL"] = url
    c = TestClient(appmod.app)
    email = "admin@coraai.tech"
    password = "ChangeMe123!"
    try:
        c.post("/api/auth/register", json={"email": email, "password": password, "confirm_password": password})
    except Exception:
        pass
    r = c.post("/api/auth/login", json={"email": email, "password": password})
    j = r.json() if r.headers.get("content-type","" ).startswith("application/json") else {}
    tok = j.get("access_token","")
    if not tok:
        raise SystemExit("ERROR: login returned no access_token")
    return tok

def main() -> None:
    url = os.getenv("DATABASE_URL", "sqlite:///./it_onboarding.db")
    ensure_schema(url)
    tok = seed_and_token(url)
    print(tok)

if __name__ == "__main__":
    main()
