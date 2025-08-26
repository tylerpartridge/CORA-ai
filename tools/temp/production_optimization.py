#!/usr/bin/env python3
"""
Production Optimization Script
Final optimizations for production deployment
"""
import os
import sys
sys.path.append('/mnt/host/c/CORA')

def optimize_for_production():
    """Apply production optimizations"""
    print("Production Optimization")
    print("=" * 30)
    
    optimizations = []
    issues = []
    
    # 1. Check Python cache files
    cache_files = []
    for root, dirs, files in os.walk('.'):
        if '__pycache__' in dirs:
            cache_files.append(os.path.join(root, '__pycache__'))
    
    if cache_files:
        optimizations.append(f"Found {len(cache_files)} Python cache directories (keep for performance)")
    
    # 2. Check for .pyc files in root
    pyc_files = [f for f in os.listdir('.') if f.endswith('.pyc')]
    if pyc_files:
        issues.append(f"Found {len(pyc_files)} .pyc files in root directory")
    else:
        optimizations.append("No .pyc files in root directory")
    
    # 3. Check environment configuration
    try:
        from config import config
        if config.DEBUG:
            issues.append("DEBUG mode is enabled - should be False for production")
        else:
            optimizations.append("DEBUG mode properly disabled")
    except Exception as e:
        issues.append(f"Could not check DEBUG setting: {e}")
    
    # 4. Check for test files that should be cleaned
    test_files = [
        'test_critical_endpoints.py',
        'security_review.py', 
        'production_optimization.py'
    ]
    
    cleanup_files = []
    for file in test_files:
        if os.path.exists(file):
            cleanup_files.append(file)
    
    if cleanup_files:
        optimizations.append(f"Production scripts can be archived: {len(cleanup_files)} files")
    
    # 5. Check static file optimization
    static_dirs = ['web/static/css', 'web/static/js']
    optimized_static = 0
    
    for static_dir in static_dirs:
        if os.path.exists(static_dir):
            files = os.listdir(static_dir)
            min_files = [f for f in files if '.min.' in f]
            optimized_static += len(min_files)
    
    if optimized_static > 0:
        optimizations.append(f"Found {optimized_static} minified static files")
    
    # 6. Database optimization check
    try:
        import sqlite3
        conn = sqlite3.connect('cora.db')
        
        # Check database size
        cursor = conn.cursor()
        cursor.execute("SELECT page_count * page_size as size FROM pragma_page_count(), pragma_page_size()")
        db_size = cursor.fetchone()[0]
        
        # Run VACUUM to optimize
        cursor.execute("VACUUM")
        conn.commit()
        conn.close()
        
        optimizations.append(f"Database optimized (size: {db_size // 1024}KB)")
    except Exception as e:
        issues.append(f"Could not optimize database: {e}")
    
    # Print results
    print(f"\nOptimizations Applied ({len(optimizations)}):")
    for item in optimizations:
        print(f"  + {item}")
    
    if issues:
        print(f"\nProduction Issues ({len(issues)}):")
        for item in issues:
            print(f"  ! {item}")
    
    print(f"\nProduction Readiness Summary:")
    print(f"Optimizations: {len(optimizations)}, Issues: {len(issues)}")
    
    if len(issues) == 0:
        print("System optimized and ready for production deployment!")
        return True
    else:
        print("Some production issues found - review before deployment")
        return False

if __name__ == "__main__":
    success = optimize_for_production()
    exit(0 if success else 1)