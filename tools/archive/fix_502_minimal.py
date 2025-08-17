#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/tools/fix_502_minimal.py
🎯 PURPOSE: Minimal fix for 502 error - focus on most likely issues
🔗 IMPORTS: subprocess
📤 EXPORTS: Fix status
"""

import subprocess

PRODUCTION_IP = "159.203.183.48"

def apply_minimal_fix():
    """Apply minimal fixes for 502 error"""
    print("🔧 Applying minimal 502 fixes...")
    print(f"Server: {PRODUCTION_IP}")
    print("-" * 50)
    
    fixes = [
        # 1. Create missing __init__.py files
        (
            "touch /var/www/cora/middleware/__init__.py /var/www/cora/models/__init__.py /var/www/cora/routes/__init__.py /var/www/cora/services/__init__.py /var/www/cora/dependencies/__init__.py",
            "Creating __init__.py files"
        ),
        
        # 2. Check Python syntax of security headers
        (
            "cd /var/www/cora && python -m py_compile middleware/security_headers.py",
            "Checking Python syntax"
        ),
        
        # 3. Test import directly
        (
            "cd /var/www/cora && python -c 'import middleware.security_headers'",
            "Testing import"
        ),
        
        # 4. Check PM2 error output
        (
            "pm2 logs cora --err --lines 30 --nostream",
            "Getting error logs"
        ),
        
        # 5. Restart with verbose output
        (
            "cd /var/www/cora && pm2 delete cora; pm2 start app.py --name cora --interpreter python",
            "Restarting PM2 process"
        ),
        
        # 6. Final status check
        (
            "pm2 status",
            "Final PM2 status"
        )
    ]
    
    for command, description in fixes:
        print(f"\n📌 {description}...")
        try:
            result = subprocess.run(
                ['ssh', f'root@{PRODUCTION_IP}', command],
                capture_output=True,
                text=True
            )
            if result.stdout:
                print(result.stdout)
            if result.stderr and "Warning" not in result.stderr:
                print(f"Error: {result.stderr}")
        except Exception as e:
            print(f"Failed: {e}")
    
    print("\n" + "=" * 50)
    print("✅ Minimal fixes applied")
    print("\nNext steps if still 502:")
    print("1. Check logs: ssh root@{} 'pm2 logs cora --lines 50'".format(PRODUCTION_IP))
    print("2. Test manually: ssh root@{} 'cd /var/www/cora && python app.py'".format(PRODUCTION_IP))

if __name__ == "__main__":
    apply_minimal_fix()