#!/usr/bin/env python3
"""
Disable heavy middleware temporarily for performance
"""

# Read app.py
with open('app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Comment out heavy middleware
new_lines = []
for line in lines:
    # Temporarily disable these performance killers
    if any(x in line for x in [
        'setup_rate_limiting',
        'setup_user_activity', 
        'setup_audit_logging',
        'query_monitoring',
        'response_optimization'
    ]):
        new_lines.append(f"# TEMP_DISABLED: {line}")
    else:
        new_lines.append(line)

# Write back
with open('app.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("Disabled heavy middleware for performance")