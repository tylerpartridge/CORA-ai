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

