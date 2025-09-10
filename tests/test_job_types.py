#!/usr/bin/env python3
"""
LOCATION: tests/test_job_types.py
PURPOSE: Integration tests for typical job types (list/custom/select)
NOTES:
- Skipped by default; enable RUN_ONBOARDING_IT=1 and provide IT_ACCESS_TOKEN
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
def test_list_job_types(client):
    r = client.get("/api/onboarding/job-types")
    if r.status_code == 401:
        pytest.skip("Auth required; set IT_ACCESS_TOKEN")
    assert r.status_code == 200
    items = r.json().get("items", [])
    assert isinstance(items, list)
    assert any(i.get("name") for i in items)


@pytest.mark.skipif(not RUN_IT, reason="RUN_ONBOARDING_IT != 1")
def test_create_custom_job_type(client):
    r = client.post("/api/onboarding/job-types/custom", json={"name": "Tile"})
    assert r.status_code in (200, 409, 201)
    data = r.json()
    assert data.get("name") == "Tile"
    assert data.get("custom") is True


@pytest.mark.skipif(not RUN_IT, reason="RUN_ONBOARDING_IT != 1")
def test_select_job_types(client):
    r = client.put("/api/onboarding/job-types/select", json={"selected": ["Plumbing", "Tile"]})
    assert r.status_code == 200
    sel = r.json().get("selected", [])
    assert "Plumbing" in sel or "Tile" in sel

