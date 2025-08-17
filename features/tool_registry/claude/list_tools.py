#!/usr/bin/env python3
"""
Quick Tool Discovery Script
Shows all available tools and their status
"""

import os
import sys
from pathlib import Path

def list_available_tools():
    """List all available tools with their status"""
    
    print("\n" + "="*60)
    print("CORA AVAILABLE TOOLS & COMMANDS")
    print("="*60)
    
    tools = [
        {
            "name": "System Health Dashboard",
            "command": "python features/system_health/claude/system_status.py",
            "description": "Complete system overview (87% = healthy)",
            "category": "Health"
        },
        {
            "name": "Database Health Check",
            "command": "python features/database_health/claude/check_db_health.py",
            "description": "Database integrity check (100% = perfect)",
            "category": "Health"
        },
        {
            "name": "Auth System Check",
            "command": "python features/auth_health/claude/test_auth_system.py",
            "description": "Authentication component tests",
            "category": "Health"
        },
        {
            "name": "Run All Tests",
            "command": "./run_tests.sh all",
            "description": "Execute test suite",
            "category": "Testing"
        },
        {
            "name": "Test Coverage Report",
            "command": "./run_tests.sh coverage",
            "description": "Tests with coverage analysis",
            "category": "Testing"
        },
        {
            "name": "Start Application",
            "command": "python app.py",
            "description": "Launch CORA web application",
            "category": "Core"
        },
        {
            "name": "List Features",
            "command": "ls features/*/STATUS",
            "description": "Show all feature STATUS files",
            "category": "Discovery"
        }
    ]
    
    # Group by category
    categories = {}
    for tool in tools:
        cat = tool["category"]
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(tool)
    
    # Display tools
    for category, cat_tools in categories.items():
        print(f"\n### {category} Tools")
        print("-" * 40)
        for tool in cat_tools:
            print(f"\n{tool['name']}:")
            print(f"  Command: {tool['command']}")
            print(f"  Purpose: {tool['description']}")
    
    # Quick check which tools are actually available
    print("\n" + "="*60)
    print("QUICK STATUS CHECK:")
    print("-" * 40)
    
    # Check if key files exist
    checks = [
        ("System Health", "features/system_health/claude/system_status.py"),
        ("Database Health", "features/database_health/claude/check_db_health.py"),
        ("Auth Health", "features/auth_health/claude/test_auth_system.py"),
        ("Test Runner", "run_tests.sh"),
        ("Main App", "app.py"),
        ("Database", "cora.db")
    ]
    
    for name, path in checks:
        exists = os.path.exists(path)
        status = "[OK]" if exists else "[MISSING]"
        print(f"  {status:10} {name}")
    
    print("\n" + "="*60)
    print("TIP: Run 'python features/system_health/claude/system_status.py'")
    print("     for a complete system health check!")
    print("="*60 + "\n")

if __name__ == "__main__":
    list_available_tools()