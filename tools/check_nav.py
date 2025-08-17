#!/usr/bin/env python3
"""
Nav CSS Diagnostics

Compares CSS loaded by key pages and scans for nav-related overrides so we can
pinpoint why nav fonts differ across pages.

Usage: python tools/check_nav.py
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import List, Tuple

from app import app  # FastAPI instance
from fastapi.testclient import TestClient


PAGE_PATHS: List[str] = ["/", "/contact", "/login", "/signup"]


def extract_css_hrefs(html: str) -> List[str]:
    return re.findall(r"<link[^>]+rel=\"stylesheet\"[^>]+href=\"([^\"]+)\"", html, flags=re.I)


def find_inline_nav_styles(html: str) -> List[str]:
    # Capture style attributes on nav and its descendants
    return re.findall(r"<(?:nav|a|button|div)[^>]*class=\"[^\"]*navbar[^\"]*\"[^>]*style=\"([^\"]+)\"", html, flags=re.I)


def list_navlink_rules_from_css() -> List[Tuple[str, str]]:
    rules: List[Tuple[str, str]] = []
    css_dir = Path("web/static/css")
    for path in css_dir.rglob("*.css"):
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        # find .nav-link blocks with font-size
        for m in re.finditer(r"\.nav-link[^{]*\{[^}]*\}", text, flags=re.I | re.S):
            block = m.group(0)
            if re.search(r"font-size\s*:\s*[^;]+;", block):
                rules.append((str(path), re.sub(r"\s+", " ", block.strip())))
    return rules


def main() -> None:
    client = TestClient(app)
    print("\n=== NAV CSS DIAGNOSTICS ===\n")
    for path in PAGE_PATHS:
        r = client.get(path)
        print(f"-- {path} -- status={r.status_code}")
        html = r.text
        hrefs = extract_css_hrefs(html)
        print("CSS hrefs (order):")
        for href in hrefs:
            print(f"  - {href}")
        inlines = find_inline_nav_styles(html)
        if inlines:
            print("Inline nav-related style attributes:")
            for s in inlines:
                print(f"  * {s}")
        else:
            print("Inline nav-related style attributes: NONE")
        # Quick check for multiple navbars (duplicate markup)
        nav_count = len(re.findall(r"<nav[^>]+navbar", html, flags=re.I))
        print(f"Navbar elements in DOM: {nav_count}")
        print()

    print("Nav-link font-size rules found in CSS files:")
    for fpath, block in list_navlink_rules_from_css():
        print(f"- {fpath}: {block}")


if __name__ == "__main__":
    main()


