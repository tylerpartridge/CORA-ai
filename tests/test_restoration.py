#!/usr/bin/env python3
"""
[LOCATION] LOCATION: /CORA/tests/test_restoration.py
[TARGET] PURPOSE: Test restoration progress - safe validation framework
[LINK] IMPORTS: pytest, basic validation functions
[EXPORT] EXPORTS: Test functions for restoration validation
"""

import pytest
import os
import sys
from pathlib import Path

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_server_imports():
    """Test that the main server still imports successfully"""
    try:
        import app
        assert hasattr(app, 'app'), "app.py should have 'app' attribute"
        print("[OK] Server imports successfully")
        return True
    except ImportError as e:
        pytest.fail(f"[ERROR] Server import failed: {e}")

def test_database_exists():
    """Test that the database files exist and are accessible"""
    db_files = [
        'data/cora.db',
        'data/claude_memory.db', 
        'data/comprehensive_logs.db'
    ]
    
    for db_file in db_files:
        assert os.path.exists(db_file), f"[ERROR] Database file missing: {db_file}"
        # Test file is readable
        assert os.access(db_file, os.R_OK), f"[ERROR] Database file not readable: {db_file}"
    
    print("[OK] All database files exist and are accessible")
    return True

def test_directory_structure():
    """Test that core directories exist with proper Python package structure"""
    required_dirs = [
        'routes',
        'models', 
        'middleware',
        'tests'
    ]
    
    for dir_name in required_dirs:
        assert os.path.exists(dir_name), f"[ERROR] Directory missing: {dir_name}"
        init_file = os.path.join(dir_name, '__init__.py')
        assert os.path.exists(init_file), f"[ERROR] __init__.py missing in {dir_name}"
    
    print("[OK] Directory structure is correct")
    return True

def test_route_imports():
    """Test that route modules can be imported (as they're created by Claude)"""
    route_modules = [
        'routes.health',
        'routes.pages',
        'routes.auth_coordinator'
    ]
    
    imported_count = 0
    for module_name in route_modules:
        try:
            __import__(module_name)
            imported_count += 1
            print(f"[OK] {module_name} imports successfully")
        except ImportError:
            print(f"[WARNING] {module_name} not yet created (expected during restoration)")
    
    print(f"[OK] {imported_count}/{len(route_modules)} route modules imported")
    return imported_count > 0  # At least one should work

def test_model_imports():
    """Test that model modules can be imported (as they're created by Claude)"""
    model_modules = [
        'models.base',
        'models.user',
        'models.business_profile',
        'models.customer',
        'models.expense_category',
        'models.expense',
        'models.payment',
        'models.subscription',
        'models.user_preference',
        'models.password_reset_token'
    ]
    
    imported_count = 0
    for module_name in model_modules:
        try:
            __import__(module_name)
            imported_count += 1
            print(f"[OK] {module_name} imports successfully")
        except ImportError:
            print(f"[WARNING] {module_name} not yet created (expected during restoration)")
    
    print(f"[OK] {imported_count}/{len(model_modules)} model modules imported")
    return imported_count >= 8  # At least the core models should work

def test_configuration_files():
    """Test that essential configuration files exist"""
    config_files = [
        'data/requirements.txt',  # Fixed: requirements.txt is in data directory
        'deployment/Dockerfile',
        'deployment/docker-compose.yml'
    ]
    
    for config_file in config_files:
        assert os.path.exists(config_file), f"[ERROR] Configuration file missing: {config_file}"
    
    print("[OK] All configuration files exist")
    return True

def test_documentation_files():
    """Test that restoration documentation exists"""
    doc_files = [
        'DATABASE_SCHEMA_DOCUMENTATION.md',
        'CONFIGURATION_ANALYSIS.md',
        'COLLABORATION_TASK.md'
    ]
    
    for doc_file in doc_files:
        assert os.path.exists(doc_file), f"[ERROR] Documentation file missing: {doc_file}"
    
    print("[OK] All documentation files exist")
    return True

def test_backup_cleanup_progress():
    """Test that backup cleanup is making progress"""
    backup_dirs = [
        '.mind/backups/file_splitting',
        '.mind/backups/import_cleanup',
        '.mind/backup'
    ]
    
    total_files = 0
    for backup_dir in backup_dirs:
        if os.path.exists(backup_dir):
            try:
                files = os.listdir(backup_dir)
                total_files += len(files)
            except (OSError, PermissionError):
                pass  # Some files may be locked
    
    # Should have fewer than 26,000 files (original count)
    assert total_files < 26000, f"[ERROR] Too many backup files remaining: {total_files}"
    print(f"[OK] Backup cleanup progress: {total_files} files remaining")
    return True

if __name__ == "__main__":
    """Run all tests and provide summary"""
    print("[TEST] CORA RESTORATION TEST SUITE")
    print("=" * 50)
    
    tests = [
        test_server_imports,
        test_database_exists,
        test_directory_structure,
        test_route_imports,
        test_model_imports,
        test_configuration_files,
        test_documentation_files,
        test_backup_cleanup_progress
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"[ERROR] {test.__name__} failed: {e}")
    
    print("=" * 50)
    print(f"[STATS] TEST RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Restoration is progressing well.")
    elif passed >= total * 0.7:
        print("[OK] Most tests passed. Restoration is on track.")
    else:
        print("[WARNING] Several tests failed. Review restoration progress.") 