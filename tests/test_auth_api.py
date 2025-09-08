#!/usr/bin/env python3

import pytest
from httpx import AsyncClient
from app import app


@pytest.mark.asyncio
async def test_login_bad_json_returns_400():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        resp = await ac.post("/api/auth/login", json={"email": "bad", "password": None})
        assert resp.status_code in (400, 422)


@pytest.mark.asyncio
async def test_login_wrong_password_returns_401(monkeypatch):
    # Stub authenticate_user to simulate invalid credentials
    from routes import auth_coordinator as ac_mod

    def fake_auth(db, email, password):
        return None

    monkeypatch.setattr(ac_mod, "authenticate_user", fake_auth)

    async with AsyncClient(app=app, base_url="http://test") as ac:
        resp = await ac.post("/api/auth/login", json={"email": "user@example.com", "password": "wrong"})
        assert resp.status_code == 401


@pytest.mark.asyncio
async def test_login_success_sets_cookie(monkeypatch):
    from routes import auth_coordinator as ac_mod
    class UserObj:
        email = "user@example.com"
        is_active = "true"
        email_verified = "true"

    def fake_auth(db, email, password):
        return UserObj()

    monkeypatch.setattr(ac_mod, "authenticate_user", fake_auth)

    async with AsyncClient(app=app, base_url="http://test") as ac:
        resp = await ac.post("/api/auth/login", json={"email": "user@example.com", "password": "ok"})
        assert resp.status_code == 200
        assert "access_token" in resp.cookies or any(c for c in resp.headers.get("set-cookie", "").split(";") if "access_token" in c.lower())


