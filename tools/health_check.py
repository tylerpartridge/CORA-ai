#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/health_check.py
🎯 PURPOSE: Check CORA system health before starting
🔗 IMPORTS: os, sys, json, importlib
📤 EXPORTS: check_health(), run_diagnostics()
🔄 PATTERN: Fail fast with clear errors
📝 TODOS: Add dependency version checking

🚀 Run this before starting development to catch issues early!
"""

import os
import sys
import json
import importlib.util

class HealthChecker:
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.info = []
        
    def check_required_files(self):
        """Ensure critical files exist"""
        required_files = [
            'app.py',
            '.cursorrules',
            '.ai/CURRENT_FOCUS.md',
            '.ai/SYSTEM_MAP.md',
            'templates/index.html'
        ]
        
        for file in required_files:
            if not os.path.exists(file):
                self.errors.append(f"❌ Missing required file: {file}")
            else:
                self.info.append(f"✅ Found: {file}")
    
    def check_file_sizes(self):
        """Warn about files approaching size limits"""
        for root, dirs, files in os.walk('.'):
            # Skip hidden directories except .ai
            dirs[:] = [d for d in dirs if not d.startswith('.') or d == '.ai']
            
            for file in files:
                if file.endswith('.py'):
                    path = os.path.join(root, file)
                    with open(path, 'r') as f:
                        lines = len(f.readlines())
                        
                    if lines > 300:
                        self.errors.append(f"❌ File too large: {path} ({lines} lines)")
                    elif lines > 250:
                        self.warnings.append(f"⚠️  Approaching limit: {path} ({lines} lines)")
    
    def check_navigation_headers(self):
        """Check if Python files have navigation headers"""
        missing_headers = []
        
        for root, dirs, files in os.walk('.'):
            dirs[:] = [d for d in dirs if not d.startswith('.') or d == '.ai']
            
            for file in files:
                if file.endswith('.py') and file != '__init__.py':
                    path = os.path.join(root, file)
                    with open(path, 'r') as f:
                        content = f.read()
                        
                    if '🧭 LOCATION:' not in content:
                        missing_headers.append(path)
        
        if missing_headers:
            self.warnings.append(f"⚠️  Files missing navigation headers: {', '.join(missing_headers)}")
    
    def check_imports(self):
        """Check for circular imports and forbidden patterns"""
        # This is a simple check - could be enhanced
        forbidden_patterns = ['from utils import', 'from helpers import', 'from common import']
        
        for root, dirs, files in os.walk('.'):
            dirs[:] = [d for d in dirs if not d.startswith('.') or d == '.ai']
            
            for file in files:
                if file.endswith('.py'):
                    path = os.path.join(root, file)
                    with open(path, 'r') as f:
                        content = f.read()
                        
                    for pattern in forbidden_patterns:
                        if pattern in content:
                            self.errors.append(f"❌ Forbidden import in {path}: {pattern}")
    
    def check_todos(self):
        """List all TODOs in the codebase"""
        todos = []
        
        for root, dirs, files in os.walk('.'):
            dirs[:] = [d for d in dirs if not d.startswith('.') or d == '.ai']
            
            for file in files:
                if file.endswith(('.py', '.md')):
                    path = os.path.join(root, file)
                    with open(path, 'r') as f:
                        for i, line in enumerate(f, 1):
                            if 'TODO' in line or '📝' in line:
                                todos.append(f"{path}:{i} - {line.strip()}")
        
        if todos:
            self.info.append(f"📝 Found {len(todos)} TODOs")
            for todo in todos[:5]:  # Show first 5
                self.info.append(f"   {todo}")
            if len(todos) > 5:
                self.info.append(f"   ... and {len(todos) - 5} more")
    
    def run_diagnostics(self):
        """Run all health checks"""
        print("🏥 CORA Health Check\n")
        
        self.check_required_files()
        self.check_file_sizes()
        self.check_navigation_headers()
        self.check_imports()
        self.check_todos()
        
        # Display results
        if self.errors:
            print("❌ ERRORS (must fix):")
            for error in self.errors:
                print(f"  {error}")
            print()
        
        if self.warnings:
            print("⚠️  WARNINGS (should fix):")
            for warning in self.warnings:
                print(f"  {warning}")
            print()
        
        if self.info:
            print("ℹ️  INFO:")
            for info in self.info:
                print(f"  {info}")
            print()
        
        # Summary
        if self.errors:
            print("❌ System is NOT healthy. Fix errors before proceeding.")
            return False
        elif self.warnings:
            print("⚠️  System is functional but has warnings.")
            return True
        else:
            print("✅ System is healthy!")
            return True

def check_health():
    """Quick health check - returns True if healthy"""
    checker = HealthChecker()
    return checker.run_diagnostics()

if __name__ == "__main__":
    healthy = check_health()
    sys.exit(0 if healthy else 1)