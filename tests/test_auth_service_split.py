#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/tests/test_auth_service_split.py
🎯 PURPOSE: Smoke test to verify auth_service split maintains backward compatibility
🔗 IMPORTS: services.auth_service
📤 EXPORTS: Test cases for auth service split
"""

import pytest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestAuthServiceSplit:
    """Verify that auth_service.py still exports all expected functions after split"""
    
    def test_user_functions_available(self):
        """Test that user management functions are available"""
        from services import auth_service
        
        # Check user management functions
        assert hasattr(auth_service, 'verify_password')
        assert hasattr(auth_service, 'get_password_hash')
        assert hasattr(auth_service, 'create_user')
        assert hasattr(auth_service, 'reset_password_with_token')
        
        # Verify they are callable
        assert callable(auth_service.verify_password)
        assert callable(auth_service.get_password_hash)
        assert callable(auth_service.create_user)
        assert callable(auth_service.reset_password_with_token)
    
    def test_token_functions_available(self):
        """Test that token management functions are available"""
        from services import auth_service
        
        # Check token functions
        assert hasattr(auth_service, 'create_access_token')
        assert hasattr(auth_service, 'verify_token')
        assert hasattr(auth_service, 'generate_password_reset_token')
        assert hasattr(auth_service, 'create_password_reset_token')
        assert hasattr(auth_service, 'create_email_verification_token')
        assert hasattr(auth_service, 'verify_email_token')
        
        # Verify they are callable
        assert callable(auth_service.create_access_token)
        assert callable(auth_service.verify_token)
        assert callable(auth_service.generate_password_reset_token)
        assert callable(auth_service.create_password_reset_token)
        assert callable(auth_service.create_email_verification_token)
        assert callable(auth_service.verify_email_token)
    
    def test_repository_functions_available(self):
        """Test that database functions are available"""
        from services import auth_service
        
        # Check repository functions
        assert hasattr(auth_service, 'get_user_by_email')
        assert hasattr(auth_service, 'authenticate_user')
        assert hasattr(auth_service, 'validate_password_reset_token')
        
        # Verify they are callable
        assert callable(auth_service.get_user_by_email)
        assert callable(auth_service.authenticate_user)
        assert callable(auth_service.validate_password_reset_token)
    
    def test_validation_functions_available(self):
        """Test that validation functions are available"""
        from services import auth_service
        
        # Check validation functions
        assert hasattr(auth_service, 'validate_email')
        assert hasattr(auth_service, 'validate_password')
        assert hasattr(auth_service, 'validate_user_input')
        
        # Verify they are callable
        assert callable(auth_service.validate_email)
        assert callable(auth_service.validate_password)
        assert callable(auth_service.validate_user_input)
    
    def test_exception_classes_available(self):
        """Test that exception classes are available"""
        from services import auth_service
        
        # Check exception classes
        assert hasattr(auth_service, 'AuthenticationError')
        assert hasattr(auth_service, 'UserAlreadyExistsError')
        assert hasattr(auth_service, 'InvalidCredentialsError')
        assert hasattr(auth_service, 'TokenValidationError')
        assert hasattr(auth_service, 'PasswordResetError')
        assert hasattr(auth_service, 'ValidationError')
        
        # Verify they are exception classes
        assert issubclass(auth_service.AuthenticationError, Exception)
        assert issubclass(auth_service.UserAlreadyExistsError, Exception)
        assert issubclass(auth_service.InvalidCredentialsError, Exception)
        assert issubclass(auth_service.TokenValidationError, Exception)
        assert issubclass(auth_service.PasswordResetError, Exception)
        assert issubclass(auth_service.ValidationError, Exception)
    
    def test_legacy_exports_available(self):
        """Test that legacy exports are still available"""
        from services import auth_service
        
        # Check legacy configuration exports
        assert hasattr(auth_service, 'SECRET_KEY')
        assert hasattr(auth_service, 'ALGORITHM')
        assert hasattr(auth_service, 'ACCESS_TOKEN_EXPIRE_MINUTES')
        assert hasattr(auth_service, 'PASSWORD_RESET_TOKEN_EXPIRE_HOURS')
        assert hasattr(auth_service, 'EMAIL_PATTERN')
        assert hasattr(auth_service, 'PASSWORD_MIN_LENGTH')
        assert hasattr(auth_service, 'pwd_context')
        
        # Verify types
        assert isinstance(auth_service.SECRET_KEY, str)
        assert isinstance(auth_service.ALGORITHM, str)
        assert isinstance(auth_service.ACCESS_TOKEN_EXPIRE_MINUTES, int)
        assert isinstance(auth_service.PASSWORD_RESET_TOKEN_EXPIRE_HOURS, int)
        assert isinstance(auth_service.PASSWORD_MIN_LENGTH, int)
    
    def test_module_imports_work(self):
        """Test that split modules can be imported directly if needed"""
        try:
            from services import auth_user
            from services import auth_tokens
            from services import auth_repository
            from services import auth_validation
            
            # Verify key functions exist in their respective modules
            assert hasattr(auth_user, 'create_user')
            assert hasattr(auth_tokens, 'create_access_token')
            assert hasattr(auth_repository, 'get_user_by_email')
            assert hasattr(auth_validation, 'validate_email')
            
        except ImportError as e:
            pytest.fail(f"Failed to import split module: {e}")
    
    def test_file_line_counts(self):
        """Verify that split modules are under 250 lines each"""
        import os
        
        modules = [
            'services/auth_user.py',
            'services/auth_tokens.py',
            'services/auth_repository.py',
            'services/auth_validation.py',
            'services/auth_service.py'
        ]
        
        for module_path in modules:
            if os.path.exists(module_path):
                with open(module_path, 'r') as f:
                    line_count = len(f.readlines())
                
                # All split modules should be under 250 lines
                if module_path != 'services/auth_service.py':
                    assert line_count <= 250, f"{module_path} has {line_count} lines (exceeds 250)"
                else:
                    # Facade should be minimal (under 150 lines)
                    assert line_count <= 150, f"Facade {module_path} has {line_count} lines (should be minimal)"


if __name__ == "__main__":
    print("\nTesting Auth Service Split\n")
    print("-" * 50)
    
    test = TestAuthServiceSplit()
    
    print("\n1. Testing user functions availability...")
    test.test_user_functions_available()
    print("   OK: All user functions available")
    
    print("\n2. Testing token functions availability...")
    test.test_token_functions_available()
    print("   OK: All token functions available")
    
    print("\n3. Testing repository functions availability...")
    test.test_repository_functions_available()
    print("   OK: All repository functions available")
    
    print("\n4. Testing validation functions availability...")
    test.test_validation_functions_available()
    print("   OK: All validation functions available")
    
    print("\n5. Testing exception classes availability...")
    test.test_exception_classes_available()
    print("   OK: All exception classes available")
    
    print("\n6. Testing legacy exports availability...")
    test.test_legacy_exports_available()
    print("   OK: All legacy exports available")
    
    print("\n7. Testing split module imports...")
    test.test_module_imports_work()
    print("   OK: Split modules can be imported directly")
    
    print("\n8. Testing file line counts...")
    test.test_file_line_counts()
    print("   OK: All modules within size limits")
    
    print("\n" + "=" * 50)
    print("SUCCESS: Auth service split completed successfully!")
    print("All functions remain available for backward compatibility")
    print("=" * 50)