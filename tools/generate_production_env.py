#!/usr/bin/env python3
"""
CORA Production Environment Generator
Generates secure production environment variables for deployment
"""

import secrets
import string
import os
import sys
from pathlib import Path

def generate_secure_password(length=32):
    """Generate a secure random password"""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    while True:
        password = ''.join(secrets.choice(alphabet) for _ in range(length))
        if (any(c.islower() for c in password)
                and any(c.isupper() for c in password)
                and any(c.isdigit() for c in password)
                and any(c in "!@#$%^&*" for c in password)):
            return password

def generate_secret_key(length=64):
    """Generate a secure secret key"""
    return secrets.token_urlsafe(length)

def generate_production_env():
    """Generate production environment file with secure values"""
    
    print("🔐 Generating CORA Production Environment Configuration...")
    
    # Read template
    template_path = Path("config/env.production.template")
    if not template_path.exists():
        print("❌ Template file not found: config/env.production.template")
        sys.exit(1)
    
    with open(template_path, 'r') as f:
        template_content = f.read()
    
    # Generate secure values
    print("🔑 Generating secure secrets...")
    
    # Database password
    db_password = generate_secure_password(24)
    
    # Secret keys
    secret_key = generate_secret_key(64)
    jwt_secret_key = generate_secret_key(64)
    
    # Redis password
    redis_password = generate_secure_password(20)
    
    # Backup encryption key
    backup_key = generate_secret_key(32)
    
    # Admin password
    admin_password = generate_secure_password(16)
    
    # Replace placeholders
    replacements = {
        'YOUR_SECURE_PASSWORD': db_password,
        'YOUR_64_CHAR_SECRET_KEY_HERE': secret_key,
        'YOUR_64_CHAR_JWT_SECRET_KEY_HERE': jwt_secret_key,
        'YOUR_REDIS_PASSWORD': redis_password,
        'YOUR_BACKUP_ENCRYPTION_KEY': backup_key,
        'YOUR_SECURE_ADMIN_PASSWORD': admin_password,
    }
    
    production_content = template_content
    for placeholder, value in replacements.items():
        production_content = production_content.replace(placeholder, value)
    
    # Write production environment file
    output_path = Path(".env.production")
    
    if output_path.exists():
        backup_path = Path(f".env.production.backup.{int(os.time.time())}")
        print(f"📦 Backing up existing .env.production to {backup_path}")
        output_path.rename(backup_path)
    
    with open(output_path, 'w') as f:
        f.write(production_content)
    
    # Set secure permissions
    os.chmod(output_path, 0o600)
    
    print("✅ Production environment file generated successfully!")
    print(f"📁 File: {output_path.absolute()}")
    print(f"🔒 Permissions: {oct(output_path.stat().st_mode)[-3:]}")
    
    # Generate summary
    print("\n" + "="*60)
    print("🔐 PRODUCTION ENVIRONMENT SUMMARY")
    print("="*60)
    print(f"Database Password: {db_password}")
    print(f"Redis Password: {redis_password}")
    print(f"Admin Password: {admin_password}")
    print(f"Secret Key: {secret_key[:20]}...")
    print(f"JWT Secret: {jwt_secret_key[:20]}...")
    print(f"Backup Key: {backup_key[:20]}...")
    print("="*60)
    
    print("\n⚠️  IMPORTANT NEXT STEPS:")
    print("1. Update API keys (OpenAI, Plaid, Stripe, SendGrid)")
    print("2. Configure domain settings (coraai.tech)")
    print("3. Set up SSL certificates")
    print("4. Configure monitoring (Sentry DSN)")
    print("5. Test all integrations")
    
    print("\n🚀 Ready for deployment!")
    return output_path

def verify_environment():
    """Verify the production environment is properly configured"""
    
    print("\n🔍 Verifying production environment...")
    
    env_path = Path(".env.production")
    if not env_path.exists():
        print("❌ .env.production file not found")
        return False
    
    # Read and check for required variables
    with open(env_path, 'r') as f:
        content = f.read()
    
    required_vars = [
        'DATABASE_URL',
        'SECRET_KEY',
        'JWT_SECRET_KEY',
        'REDIS_URL',
        'OPENAI_API_KEY',
        'STRIPE_API_KEY',
        'SENDGRID_API_KEY'
    ]
    
    missing_vars = []
    for var in required_vars:
        if f'{var}=' not in content or f'{var}=YOUR_' in content:
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing or incomplete variables: {', '.join(missing_vars)}")
        return False
    
    print("✅ Production environment verified!")
    return True

if __name__ == "__main__":
    try:
        # Generate production environment
        env_file = generate_production_env()
        
        # Verify configuration
        if verify_environment():
            print("\n🎉 Production environment ready for deployment!")
        else:
            print("\n⚠️  Please complete the configuration before deployment")
            
    except Exception as e:
        print(f"❌ Error generating production environment: {e}")
        sys.exit(1) 