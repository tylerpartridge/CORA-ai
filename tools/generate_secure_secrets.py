#!/usr/bin/env python3
"""
Generate Secure Secrets for Production
Creates cryptographically secure keys for JWT and session management
"""

import secrets
import string
import os
from datetime import datetime

def generate_secure_secret(length=32):
    """Generate a cryptographically secure secret key"""
    return secrets.token_urlsafe(length)

def generate_strong_password(length=20):
    """Generate a strong password for database"""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    # Avoid problematic characters in passwords
    alphabet = alphabet.replace('"', '').replace("'", '').replace('\\', '')
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def main():
    """Generate all required secrets for production"""
    print("🔐 Generating Secure Secrets for CORA Production")
    print("=" * 60)
    
    # Generate secrets
    secrets_dict = {
        'SECRET_KEY': generate_secure_secret(32),
        'JWT_SECRET_KEY': generate_secure_secret(32),
        'DATABASE_PASSWORD': generate_strong_password(20),
        'ADMIN_PASSWORD': generate_strong_password(16),
        'API_KEY': generate_secure_secret(24)
    }
    
    # Create production .env template
    env_content = f"""# CORA Production Environment Variables
# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
# ⚠️ KEEP THIS FILE SECURE - DO NOT COMMIT TO GIT

# Database Configuration (PostgreSQL)
DATABASE_URL=postgresql://cora_user:{secrets_dict['DATABASE_PASSWORD']}@localhost:5432/cora_db

# Security Keys (Generated cryptographically secure)
SECRET_KEY={secrets_dict['SECRET_KEY']}
JWT_SECRET_KEY={secrets_dict['JWT_SECRET_KEY']}

# JWT Configuration
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# API Keys (Replace with your actual keys)
OPENAI_API_KEY=your-openai-api-key-here
PLAID_CLIENT_ID=your-plaid-client-id-here
PLAID_SECRET=your-plaid-secret-here
STRIPE_API_KEY=your-stripe-api-key-here
STRIPE_WEBHOOK_SECRET=your-stripe-webhook-secret-here

# QuickBooks Configuration
QUICKBOOKS_CLIENT_ID=your-quickbooks-client-id-here
QUICKBOOKS_CLIENT_SECRET=your-quickbooks-client-secret-here

# Email Configuration
EMAIL_API_KEY=your-email-api-key-here
EMAIL_FROM=noreply@coraai.com

# Application Settings
DEBUG=False
BASE_URL=https://coraai.com
ENVIRONMENT=production

# Rate Limiting
RATE_LIMIT_REQUESTS_PER_MINUTE=100/minute

# Redis (for production caching)
REDIS_URL=redis://localhost:6379

# Monitoring
SENTRY_DSN=your-sentry-dsn-here

# Admin Access (for initial setup)
ADMIN_EMAIL=admin@coraai.com
ADMIN_PASSWORD={secrets_dict['ADMIN_PASSWORD']}

# Internal API Key (for service-to-service)
INTERNAL_API_KEY={secrets_dict['API_KEY']}
"""
    
    # Save to file
    output_path = "./config/.env.production.secure"
    os.makedirs("./config", exist_ok=True)
    
    with open(output_path, 'w') as f:
        f.write(env_content)
    
    print(f"\n✅ Secure environment file created: {output_path}")
    
    # Also create a secrets backup file
    backup_content = f"""# CORA Production Secrets Backup
# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
# ⚠️ STORE THIS SECURELY - DO NOT LOSE THESE KEYS

SECRET_KEY={secrets_dict['SECRET_KEY']}
JWT_SECRET_KEY={secrets_dict['JWT_SECRET_KEY']}
DATABASE_PASSWORD={secrets_dict['DATABASE_PASSWORD']}
ADMIN_PASSWORD={secrets_dict['ADMIN_PASSWORD']}
INTERNAL_API_KEY={secrets_dict['API_KEY']}

# PostgreSQL Setup Command:
sudo -u postgres psql -c "ALTER USER cora_user WITH PASSWORD '{secrets_dict['DATABASE_PASSWORD']}';"

# Initial Admin User:
Email: admin@coraai.com
Password: {secrets_dict['ADMIN_PASSWORD']}
"""
    
    backup_path = f"./config/secrets_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(backup_path, 'w') as f:
        f.write(backup_content)
    
    print(f"✅ Secrets backup created: {backup_path}")
    
    # Display important information
    print("\n" + "=" * 60)
    print("📋 IMPORTANT NEXT STEPS:")
    print("=" * 60)
    print("\n1. Copy the production env file:")
    print(f"   cp {output_path} .env")
    print("\n2. Update PostgreSQL password:")
    print(f"   sudo -u postgres psql -c \"ALTER USER cora_user WITH PASSWORD '{secrets_dict['DATABASE_PASSWORD']}'\"")
    print("\n3. Add your actual API keys to .env:")
    print("   - OpenAI API Key")
    print("   - Plaid credentials")
    print("   - Stripe keys")
    print("   - Email service key")
    print("\n4. Store the backup file securely:")
    print(f"   - Move {backup_path} to a secure location")
    print("   - Do NOT commit it to git")
    print("   - Consider using a password manager")
    print("\n5. Add .env to .gitignore:")
    print("   echo '.env' >> .gitignore")
    print("   echo '.env.production*' >> .gitignore")
    print("   echo 'config/secrets_backup*' >> .gitignore")
    
    print("\n🔒 Security Tips:")
    print("- Never commit .env files to git")
    print("- Rotate keys every 90 days")
    print("- Use environment variables in production")
    print("- Enable 2FA on all service accounts")
    print("- Monitor for exposed secrets on GitHub")
    
    print("\n✨ Secrets generation complete!")

if __name__ == "__main__":
    main()