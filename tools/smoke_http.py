#!/usr/bin/env python3
"""
Minimal HTTP smoke (no deps) for CORA.
Usage:
  BASE=http://127.0.0.1:8000 python tools/smoke_http.py
  BASE=https://coraai.tech ADMIN_TOKEN=... python tools/smoke_http.py
"""

from __future__ import annotations

import json
import os
import re
import sys
import time
import uuid
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError


BASE = os.getenv("BASE", "http://127.0.0.1:8000").rstrip("/") + "/"
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN")
SUMMARY_JSON = str(os.getenv("SUMMARY_JSON", "")).lower() in {"1", "true", "yes"}
UA = "cora-smoke/1.0"


def is_localhost(netloc: str) -> bool:
    host = netloc
    if ":" in netloc and not netloc.startswith("["):
        host = netloc.split(":", 1)[0]
    if netloc.startswith("[") and "]" in netloc:
        host = netloc.split("]", 1)[0].strip("[]")
    return host in {"127.0.0.1", "localhost", "::1"}


def semver(v: str) -> bool:
    return bool(re.match(r"^\d+\.\d+\.\d+$", v))


def do_get(path: str, rid: str) -> tuple[int | None, dict, bytes, str | None]:
    url = urljoin(BASE, path.lstrip("/"))
    req = Request(url, method="GET")
    req.add_header("User-Agent", UA)
    req.add_header("X-Request-ID", rid)
    if path.startswith("/smoke") and ADMIN_TOKEN:
        req.add_header("X-Admin-Token", ADMIN_TOKEN)
    try:
        with urlopen(req, timeout=3) as resp:
            headers = {k.lower(): v for k, v in resp.headers.items()}
            return resp.status, headers, resp.read(), None
    except HTTPError as e:
        try:
            body = e.read()
        except Exception:
            body = b""
        hdrs = getattr(e, "headers", {})
        try:
            hdrs = {k.lower(): v for k, v in hdrs.items()}
        except Exception:
            hdrs = {}
        return int(getattr(e, "code", 0) or 0), hdrs, body, None
    except URLError as e:
        return None, {}, b"", str(e)
    except Exception as e:
        return None, {}, b"", str(e)


def check_ping() -> bool:
    rid = str(uuid.uuid4())
    code, headers, body, err = do_get("/ping", rid)
    if err:
        print(f"FAIL: /ping error: {err}")
        return False
    if code != 200:
        print(f"FAIL: /ping status {code}")
        return False
    try:
        data = json.loads(body.decode("utf-8", "replace"))
    except Exception:
        print("FAIL: /ping non-JSON body")
        return False
    xr = headers.get("x-request-id")
    if not (isinstance(data, dict) and data.get("ok") is True and xr and xr == rid):
        print("FAIL: /ping body or X-Request-ID mismatch")
        return False
    # Security headers
    if (headers.get("x-frame-options", "") or "").upper() != "DENY":
        print("FAIL: /ping missing X-Frame-Options DENY")
        return False
    if (headers.get("x-content-type-options", "") or "").lower() != "nosniff":
        print("FAIL: /ping missing X-Content-Type-Options nosniff")
        return False
    if not headers.get("referrer-policy"):
        print("FAIL: /ping missing Referrer-Policy")
        return False
    # HSTS only required over https
    if urlparse(BASE).scheme == "https" and not headers.get("strict-transport-security"):
        print("FAIL: /ping missing HSTS on https")
        return False
    print("PASS")
    return True


def check_version() -> bool:
    rid = str(uuid.uuid4())
    code, headers, body, err = do_get("/version", rid)
    if err:
        print(f"FAIL: /version error: {err}")
        return False
    if code != 200:
        print(f"FAIL: /version status {code}")
        return False
    try:
        data = json.loads(body.decode("utf-8", "replace"))
        v = str(data.get("version", ""))
    except Exception:
        print("FAIL: /version non-JSON body")
        return False
    if not semver(v):
        print(f"FAIL: /version invalid semver '{v}'")
        return False
    print("PASS")
    return True


def check_metrics() -> bool:
    rid = str(uuid.uuid4())
    code, headers, body, err = do_get("/metrics", rid)
    if err:
        print(f"FAIL: /metrics error: {err}")
        return False
    if code != 200:
        print(f"FAIL: /metrics status {code}")
        return False
    ct = headers.get("content-type", "")
    text = body.decode("utf-8", "replace")
    if not ct.lower().startswith("text/plain"):
        print(f"FAIL: /metrics content-type '{ct}'")
        return False
    if ("python_info" not in text) and ("process_cpu_seconds_total" not in text):
        print("FAIL: /metrics missing expected metrics")
        return False
    print("PASS")
    return True


def check_smoke() -> bool:
    rid = str(uuid.uuid4())
    code, headers, body, err = do_get("/smoke", rid)
    if err:
        print(f"FAIL: /smoke error: {err}")
        return False
    netloc = urlparse(BASE).netloc
    expected_200 = bool(ADMIN_TOKEN) or is_localhost(netloc)
    if expected_200:
        if code != 200:
            print(f"FAIL: /smoke expected 200, got {code}")
            return False
        try:
            data = json.loads(body.decode("utf-8", "replace"))
        except Exception:
            print("FAIL: /smoke non-JSON body")
            return False
        status = (data.get("status") or "").lower()
        checks = data.get("checks") or {}
        cache = (headers.get("cache-control") or "").lower()
        xr = headers.get("x-request-id")
        if status not in {"green", "yellow", "red"}:
            print("FAIL: /smoke invalid status")
            return False
        for k in ("db", "redis", "email", "routes_count"):
            if k not in checks:
                print(f"FAIL: /smoke missing check '{k}'")
                return False
        if checks.get("request_id") != xr or not xr:
            print("FAIL: /smoke request_id mismatch")
            return False
        if "no-store" not in cache:
            print("FAIL: /smoke missing Cache-Control no-store")
            return False
        print("PASS")
        return True
    else:
        if code == 403:
            print("PASS")
            return True
        print(f"FAIL: /smoke expected 403 from non-localhost without token, got {code}")
        return False


def main() -> int:
    if SUMMARY_JSON:
        # Minimal JSON-only summary for CI: check /ping and /version silently
        # /ping
        rid_ping = str(uuid.uuid4())
        code_p, hdrs_p, body_p, err_p = do_get("/ping", rid_ping)
        ping_ok = (not err_p) and code_p == 200
        try:
            ping_ok = ping_ok and (json.loads(body_p.decode("utf-8", "replace")).get("ok") is True)
        except Exception:
            ping_ok = False
        # /version
        rid_v = str(uuid.uuid4())
        code_v, hdrs_v, body_v, err_v = do_get("/version", rid_v)
        ver = ""
        ver_ok = False
        if not err_v and code_v == 200:
            try:
                ver = str(json.loads(body_v.decode("utf-8", "replace")).get("version", ""))
                ver_ok = bool(ver) and semver(ver)
            except Exception:
                ver_ok = False
        ok = bool(ping_ok and ver_ok)
        summary = {"ok": ok, "ping": bool(ping_ok), "version": ver}
        print(json.dumps(summary))
        return 0 if ok else 1
    else:
        checks = [
            ("/ping", check_ping),
            ("/version", check_version),
            ("/metrics", check_metrics),
            ("/smoke", check_smoke),
        ]
        results = []
        for name, fn in checks:
            ok = False
            try:
                ok = fn()
            except Exception as e:
                print(f"FAIL: {name} exception: {e}")
                ok = False
            results.append(ok)
        overall = all(results)
        print(f"OVERALL: {'PASS' if overall else 'FAIL'}")
        return 0 if overall else 1


if __name__ == "__main__":
    sys.exit(main())
