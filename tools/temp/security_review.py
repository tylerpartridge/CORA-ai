#!/usr/bin/env python3
"""
Security Configuration Review for Production Deployment
Reviews critical security settings before production
"""
import os
import sys
sys.path.append('/mnt/host/c/CORA')

def review_security_config():
    """Review security configurations for production readiness"""
    print("Security Configuration Review")
    print("=" * 40)
    
    issues = []
    warnings = []
    passed = []
    
    # 1. Check environment variables
    try:
        from config import config
        if config.SECRET_KEY and len(config.SECRET_KEY) > 20:
            passed.append("Secret key configured properly")
        else:
            issues.append("SECRET_KEY too short or missing")
            
        if config.JWT_SECRET_KEY and len(config.JWT_SECRET_KEY) > 20:
            passed.append("JWT secret key configured properly")
        else:
            issues.append("JWT_SECRET_KEY too short or missing")
    except Exception as e:
        issues.append(f"Config import failed: {e}")
    
    # 2. Check database security
    try:
        if os.path.exists('cora.db'):
            import stat
            db_stat = os.stat('cora.db')
            # Check if database has proper permissions
            if oct(db_stat.st_mode)[-3:] == '644':
                passed.append("Database permissions appropriate")
            else:
                warnings.append("Database permissions may be too open")
        else:
            issues.append("Database file not found")
    except Exception as e:
        warnings.append(f"Could not check database permissions: {e}")
    
    # 3. Check for hardcoded secrets
    secret_patterns = [
        'password=',
        'secret=',
        'key=',
        'token=',
        'api_key='
    ]
    
    sensitive_files = ['app.py', 'config.py', 'routes/auth_routes.py']
    found_secrets = []
    
    for file_path in sensitive_files:
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r') as f:
                    content = f.read().lower()
                    for pattern in secret_patterns:
                        if pattern in content and 'env' not in content:
                            found_secrets.append(f"{file_path}: potential hardcoded {pattern}")
            except Exception:
                pass
    
    if found_secrets:
        issues.extend(found_secrets)
    else:
        passed.append("No obvious hardcoded secrets found")
    
    # 4. Check HTTPS configuration
    try:
        from middleware.security_headers import SecurityHeadersMiddleware
        passed.append("Security headers middleware present")
    except ImportError:
        warnings.append("Security headers middleware not found")
    
    # 5. Check CORS configuration
    try:
        import main
        # Look for CORS in the main app file
        with open('app.py', 'r') as f:
            app_content = f.read()
            if 'CORSMiddleware' in app_content:
                passed.append("CORS middleware configured")
            else:
                warnings.append("CORS middleware not found")
    except Exception:
        warnings.append("Could not verify CORS configuration")
    
    # Print results
    print(f"\nPassed Checks ({len(passed)}):")
    for item in passed:
        print(f"  + {item}")
    
    if warnings:
        print(f"\nWarnings ({len(warnings)}):")
        for item in warnings:
            print(f"  ! {item}")
    
    if issues:
        print(f"\nCritical Issues ({len(issues)}):")
        for item in issues:
            print(f"  - {item}")
    
    # Summary
    print(f"\nSecurity Review Summary:")
    print(f"Passed: {len(passed)}, Warnings: {len(warnings)}, Issues: {len(issues)}")
    
    if len(issues) == 0:
        print("Security configuration ready for production")
        return True
    else:
        print("Critical security issues found - fix before deployment")
        return False

if __name__ == "__main__":
    success = review_security_config()
    exit(0 if success else 1)