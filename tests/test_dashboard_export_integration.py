#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/tests/test_dashboard_export_integration.py
🎯 PURPOSE: Integration checks for dashboard export start/end behavior (SKIPPED by default)
🔗 IMPORTS: os, urllib
📤 EXPORTS: Skipped tests unless RUN_EXPORTS_IT=1
"""

import os
import urllib.request
import urllib.parse
import pytest


RUN = os.getenv("RUN_EXPORTS_IT", "0") == "1"
BASE = os.getenv("BASE", "http://127.0.0.1:8000").rstrip("/")

pytestmark = pytest.mark.skipif(not RUN, reason="Skipped dashboard export integration tests (set RUN_EXPORTS_IT=1)")


def _get(path: str):
    url = urllib.parse.urljoin(BASE + "/", path.lstrip("/"))
    req = urllib.request.Request(url, method="GET")
    with urllib.request.urlopen(req, timeout=5) as resp:
        return resp.status, dict(resp.headers), resp.read()


def test_dashboard_export_none_params():
    code, headers, body = _get("/api/dashboard/export?format=csv")
    assert code == 200
    cd = headers.get("Content-Disposition", "")
    assert "attachment; filename=cora_dashboard_" in cd
    assert cd.endswith(".csv")


def test_dashboard_export_start_only():
    code, headers, body = _get("/api/dashboard/export?format=csv&start=2025-09-01")
    assert code == 200
    cd = headers.get("Content-Disposition", "")
    assert "_20250901.csv" in cd


def test_dashboard_export_end_only():
    code, headers, body = _get("/api/dashboard/export?format=csv&end=2025-09-30")
    assert code == 200
    cd = headers.get("Content-Disposition", "")
    assert "_20250930.csv" in cd


def test_dashboard_export_both():
    code, headers, body = _get("/api/dashboard/export?format=csv&start=2025-09-01&end=2025-09-30")
    assert code == 200
    cd = headers.get("Content-Disposition", "")
    assert "_20250901-20250930.csv" in cd


def test_dashboard_export_inverted_autocorrect():
    code, headers, body = _get("/api/dashboard/export?format=csv&start=2025-09-30&end=2025-09-01")
    assert code == 200
    cd = headers.get("Content-Disposition", "")
    assert "_20250901-20250930.csv" in cd


