#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/tools/setup_env.py
🎯 PURPOSE: Generate secure keys and setup production environment
🔗 IMPORTS: secrets, os
📤 EXPORTS: Environment setup functions
"""

import secrets
import os
from pathlib import Path

def generate_secure_keys():
    """Generate secure keys for production"""
    secret_key = secrets.token_hex(32)
    jwt_secret = secrets.token_hex(32)
    return secret_key, jwt_secret

def setup_production_env():
    """Setup production environment file"""
    print("🔐 Setting up production environment...")
    
    # Generate secure keys
    secret_key, jwt_secret = generate_secure_keys()
    
    # Read template
    template_path = Path(__file__).parent.parent / "config" / "env.production.template"
    if not template_path.exists():
        print("❌ Template file not found")
        return False
    
    with open(template_path, 'r') as f:
        content = f.read()
    
    # Replace placeholders
    content = content.replace('REPLACE_WITH_SECURE_KEY', secret_key)
    content = content.replace('REPLACE_WITH_JWT_SECRET', jwt_secret)
    
    # Write to production
    prod_path = Path(__file__).parent.parent / ".env.production"
    with open(prod_path, 'w') as f:
        f.write(content)
    
    print("✅ Production environment file created")
    print(f"🔑 SECRET_KEY: {secret_key[:16]}...")
    print(f"🔑 JWT_SECRET_KEY: {jwt_secret[:16]}...")
    
    return True

if __name__ == "__main__":
    setup_production_env() 