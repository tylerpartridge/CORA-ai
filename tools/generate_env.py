#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/tools/generate_env.py
🎯 PURPOSE: Generate secure environment variables for production
🔗 IMPORTS: secrets, os
📤 EXPORTS: Generated .env file
"""

import secrets
import os
import string

def generate_secure_key(length: int = 32) -> str:
    """Generate a secure random key"""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def generate_env_file():
    """Generate a secure .env file for production"""
    
    # Generate secure keys
    secret_key = generate_secure_key(64)
    
    env_content = f"""# CORA Production Environment Configuration
# Generated: {os.popen('date').read().strip()}
# WARNING: Keep this file secure and never commit it to version control

# Database Configuration
DATABASE_URL=sqlite:///./data/cora.db

# Security Keys (GENERATED - Keep these secure!)
SECRET_KEY={secret_key}
SENDGRID_API_KEY=your-sendgrid-api-key-here
STRIPE_WEBHOOK_SECRET=your-stripe-webhook-secret-here

# Email Configuration
FROM_EMAIL=noreply@coraai.tech
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587

# Rate Limiting
RATE_LIMIT_REQUESTS_PER_MINUTE=100

# CORS Configuration
ALLOWED_ORIGINS=https://coraai.tech,https://www.coraai.tech

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/cora.log

# Backup Configuration
BACKUP_RETENTION_DAYS=30
BACKUP_SCHEDULE=0 2 * * *

# Integration Keys (Optional - for future features)
PLAID_CLIENT_ID=your-plaid-client-id
PLAID_SECRET=your-plaid-secret
QUICKBOOKS_CLIENT_ID=your-quickbooks-client-id
QUICKBOOKS_CLIENT_SECRET=your-quickbooks-client-secret

# Monitoring
SENTRY_DSN=your-sentry-dsn-here
"""
    
    # Write to .env file
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("✅ Generated secure .env file")
    print("⚠️  IMPORTANT: Update the following values with your actual credentials:")
    print("   - SENDGRID_API_KEY")
    print("   - STRIPE_WEBHOOK_SECRET")
    print("   - Integration keys (when ready)")
    print("   - SENTRY_DSN (when monitoring is set up)")

if __name__ == "__main__":
    generate_env_file() 