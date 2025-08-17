#!/usr/bin/env python
"""Debug what template Flask is actually using"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app import app

# Check template directory
templates_dir = Path(__file__).parent / "web" / "templates"
login_path = templates_dir / "login.html"

print(f"Template directory: {templates_dir}")
print(f"Login template exists: {login_path.exists()}")
print(f"Login template path: {login_path}")

if login_path.exists():
    with open(login_path, 'r') as f:
        content = f.read()
        if "Stop Losing" in content:
            print("[OK] File contains 'Stop Losing' text")
        else:
            print("[FAIL] File missing 'Stop Losing' text")
        
        if "info-panel" in content:
            print("[OK] File contains 'info-panel'")
        else:
            print("[FAIL] File missing 'info-panel'")

# Check what Jinja2 sees
print(f"\nApp template folder: {app.state.templates.directory}")