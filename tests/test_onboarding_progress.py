#!/usr/bin/env python3
"""
LOCATION: tests/test_onboarding_progress.py
PURPOSE: Integration tests for onboarding save/resume progress endpoints
NOTES:
- Skipped by default; enable by setting RUN_ONBOARDING_IT=1
- Requires auth cookie 'access_token' via IT_ACCESS_TOKEN
"""

import os
import pytest

RUN_IT = os.getenv("RUN_ONBOARDING_IT") == "1"
ACCESS_TOKEN = os.getenv("IT_ACCESS_TOKEN")


@pytest.fixture(scope="module")
def client():
    if not RUN_IT:
        pytest.skip("RUN_ONBOARDING_IT != 1")
    try:
        from fastapi.testclient import TestClient
        import app as app_module
    except Exception as e:
        pytest.skip(f"FastAPI TestClient unavailable: {e}")
    c = TestClient(app_module.app)
    if ACCESS_TOKEN:
        c.cookies.set("access_token", ACCESS_TOKEN)
    return c


@pytest.mark.skipif(not RUN_IT, reason="RUN_ONBOARDING_IT != 1")
def test_fetch_initial_progress(client):
    r = client.get("/api/onboarding/progress")
    if r.status_code == 401:
        pytest.skip("Auth required; set IT_ACCESS_TOKEN")
    assert r.status_code == 200
    data = r.json()
    assert "progress" in data and isinstance(data["progress"], dict)


@pytest.mark.skipif(not RUN_IT, reason="RUN_ONBOARDING_IT != 1")
def test_save_and_fetch_progress(client):
    payload = {"progress": {"step": "profile_setup", "percent": 33}}
    r = client.put("/api/onboarding/progress", json=payload)
    assert r.status_code != 401
    assert r.status_code == 200
    r2 = client.get("/api/onboarding/progress")
    assert r2.status_code == 200
    data = r2.json()
    assert data.get("progress", {}).get("step") == "profile_setup"


@pytest.mark.skipif(not RUN_IT, reason="RUN_ONBOARDING_IT != 1")
def test_overwrite_progress(client):
    payload = {"progress": {"step": "dashboard", "percent": 100}}
    r = client.put("/api/onboarding/progress", json=payload)
    assert r.status_code == 200
    r2 = client.get("/api/onboarding/progress")
    assert r2.status_code == 200
    assert r2.json().get("progress", {}).get("step") == "dashboard"


def test_unauth_progress_routes():
    if not RUN_IT:
        pytest.skip("RUN_ONBOARDING_IT != 1")
    from fastapi.testclient import TestClient
    import app as app_module
    c = TestClient(app_module.app)
    r = c.get("/api/onboarding/progress")
    assert r.status_code == 401
    r2 = c.put("/api/onboarding/progress", json={"progress": {}})
    assert r2.status_code == 401

