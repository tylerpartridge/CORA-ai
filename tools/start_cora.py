#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/start_cora.py
🎯 PURPOSE: Smart startup script - checks health and starts server
🔗 IMPORTS: subprocess, sys, health_check, index_cora
📤 EXPORTS: main entry point
🔄 PATTERN: Fail fast, start clean
📝 TODOS: Add automatic git status check

ALWAYS run this instead of python app.py!
"""

import subprocess
import sys
import os
import logging

logger = logging.getLogger(__name__)

# Add current directory to path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from health_check import check_health
from index_cora import update_indexes
from python_selector import PYTHON_CMD



def print_banner():
    """Show CORA startup banner"""
    print("""
    ╔═══════════════════════════════════════╗
    ║          CORA AI v4.0                 ║
    ║   AI Bookkeeping That Gets Smarter    ║
    ╚═══════════════════════════════════════╝
    """)

def check_git_status():
    """Check if there are uncommitted changes"""
    try:
        result = subprocess.run(['git', 'status', '--porcelain'], 
                              capture_output=True, text=True)
        if result.stdout:
            print("⚠️  Uncommitted changes detected:")
            changes = result.stdout.strip().split('\n')
            for change in changes[:5]:
                print(f"   {change}")
            if len(changes) > 5:
                print(f"   ... and {len(changes) - 5} more")
            print()
    except subprocess.SubprocessError as e:
        logger.warning(f"Git check failed - subprocess error: {str(e)}")
        pass  # Git not available
    except FileNotFoundError:
        logger.info("Git not found - skipping uncommitted changes check")
        pass  # Git not installed

def main():
    """Main startup sequence"""
    print_banner()
    
    # Step 1: Update indexes
    print("📊 Updating system indexes...")
    try:
        update_indexes()
        print()
    except Exception as e:
        print(f"❌ Failed to update indexes: {e}")
        return 1
    
    # Step 2: Run health check
    print("🏥 Running health check...")
    if not check_health():
        print("\n❌ Fix health issues before starting!")
        return 1
    print()
    

    
    # Step 3: Check git
    check_git_status()
    
    # Step 4: Show current focus
    if os.path.exists('.ai/CURRENT_FOCUS.md'):
        print("🎯 Current Focus:")
        with open('.ai/CURRENT_FOCUS.md', 'r') as f:
            lines = f.readlines()[2:6]  # Skip header, show key lines
            for line in lines:
                if line.strip():
                    print(f"   {line.strip()}")
        print()
    
    # Step 5: Start server
    print("🚀 Starting CORA server...")
    print("   URL: http://localhost:8000")
    print("   Docs: http://localhost:8000/docs")
    print("   Stop: Ctrl+C")
    print()
    
    try:
        # Use the correct Python interpreter
        subprocess.run([PYTHON_CMD, '-m', 'uvicorn', 'app:app', '--port', '8000', '--reload'])
    except KeyboardInterrupt:
        print("\n\n👋 CORA stopped gracefully")
        return 0
    except Exception as e:
        print(f"\n❌ Server error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())