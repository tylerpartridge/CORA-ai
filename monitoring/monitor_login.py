#!/usr/bin/env python3
"""Monitor login attempts in real-time"""

import time
import os
from datetime import datetime

print("=" * 70)
print("LOGIN MONITORING ACTIVE")
print("=" * 70)
print(f"Started at: {datetime.now()}")
print("Watching for login attempts...")
print("-" * 70)

# Monitor the log file
log_file = "app.log"
if os.path.exists(log_file):
    # Get initial file size
    initial_size = os.path.getsize(log_file)
    
    print(f"Monitoring {log_file}")
    print("Waiting for login attempts...\n")
    
    while True:
        current_size = os.path.getsize(log_file)
        if current_size > initial_size:
            with open(log_file, 'r') as f:
                f.seek(initial_size)
                new_lines = f.read()
                if new_lines:
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] New activity:")
                    print(new_lines)
                    initial_size = current_size
        time.sleep(0.5)
else:
    print("Log file not found. Monitoring console output instead...")
    print("\nPlease try logging in at http://localhost:8001/login")
    print("\nExpected flow:")
    print("1. Enter credentials")
    print("2. Click 'SIGN IN TO DASHBOARD'")
    print("3. Should redirect to /dashboard")
    print("\nI'll see the activity here when you login!")