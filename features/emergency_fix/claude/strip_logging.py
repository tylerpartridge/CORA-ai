#!/usr/bin/env python3
"""
Remove excessive logging from app.py
"""

import re

# Read app.py
with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Comment out all print statements except critical ones
lines = content.split('\n')
new_lines = []

for line in lines:
    # Keep critical startup messages, comment out the spam
    if 'print(' in line:
        if any(x in line for x in ['running on', 'ERROR', 'CRITICAL', 'Failed']):
            new_lines.append(line)  # Keep these
        else:
            new_lines.append(f"# {line}" if not line.strip().startswith('#') else line)
    else:
        new_lines.append(line)

# Write back
with open('app.py', 'w', encoding='utf-8') as f:
    f.write('\n'.join(new_lines))

print("✓ Commented out spam logging in app.py")