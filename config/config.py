# 🧭 LOCATION: /CORA/config.py
# 🎯 PURPOSE: Centralized configuration management for all environment variables
# 🔗 IMPORTS: os, secrets (for fallback generation)
# 📤 EXPORTS: All configuration variables with proper validation

import os
import secrets
from typing import Optional
from dotenv import load_dotenv

# Load environment variables - only load from .env file if it exists
import os
if os.path.exists('.env'):
    try:
        load_dotenv('.env')
    except Exception as e:
        print(f"Warning: Could not load .env file: {e}")
        print("Using default configuration values")
else:
    print("No .env file found, using default configuration values")

class Config:
    """Centralized configuration management with validation"""
    
    # Database Configuration - SQLite for demo reliability
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./cora.db")
    
    # Security Configuration - CRITICAL: No defaults for production secrets
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY")
    
    # JWT Configuration
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # Password Configuration
    PASSWORD_MIN_LENGTH: int = int(os.getenv("PASSWORD_MIN_LENGTH", "8"))
    PASSWORD_RESET_TOKEN_EXPIRE_HOURS: int = int(os.getenv("PASSWORD_RESET_TOKEN_EXPIRE_HOURS", "24"))
    
    # Plaid Configuration
    PLAID_CLIENT_ID: Optional[str] = os.getenv("PLAID_CLIENT_ID")
    PLAID_SECRET: Optional[str] = os.getenv("PLAID_SECRET")
    PLAID_ENV: str = os.getenv("PLAID_ENV", "sandbox")
    
    # Stripe Configuration
    STRIPE_API_KEY: Optional[str] = os.getenv("STRIPE_API_KEY")
    STRIPE_WEBHOOK_SECRET: Optional[str] = os.getenv("STRIPE_WEBHOOK_SECRET")
    
    # QuickBooks Configuration
    QUICKBOOKS_CLIENT_ID: Optional[str] = os.getenv("QUICKBOOKS_CLIENT_ID")
    QUICKBOOKS_CLIENT_SECRET: Optional[str] = os.getenv("QUICKBOOKS_CLIENT_SECRET")
    
    # Email Configuration
    EMAIL_API_KEY: Optional[str] = os.getenv("EMAIL_API_KEY")
    EMAIL_FROM: Optional[str] = os.getenv("EMAIL_FROM")
    
    # Redis Configuration
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    # Application Configuration
    BASE_URL: str = os.getenv("BASE_URL", "http://localhost:8000")
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))
    
    # AI Configuration
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    
    # Emotional Intelligence Configuration
    ENABLE_ENHANCED_ORCHESTRATOR: bool = os.getenv("ENABLE_ENHANCED_ORCHESTRATOR", "true").lower() == "true"
    EMOTIONAL_INTELLIGENCE_ENABLED: bool = os.getenv("EMOTIONAL_INTELLIGENCE_ENABLED", "true").lower() == "true"
    EMOTIONAL_RESPONSE_DELAY_MS: int = int(os.getenv("EMOTIONAL_RESPONSE_DELAY_MS", "2000"))
    
    @classmethod
    def validate_production_config(cls) -> None:
        """Validate that all required production secrets are set"""
        if not cls.DEBUG:  # Production mode
            required_secrets = [
                ("SECRET_KEY", cls.SECRET_KEY),
                ("JWT_SECRET_KEY", cls.JWT_SECRET_KEY),
            ]
            
            missing_secrets = []
            for name, value in required_secrets:
                if not value:
                    missing_secrets.append(name)
            
            if missing_secrets:
                raise ValueError(
                    f"CRITICAL: Missing required environment variables for production: {', '.join(missing_secrets)}"
                )
    
    @classmethod
    def get_secure_fallback(cls, key: str) -> str:
        """Generate secure fallback for development only"""
        if cls.DEBUG:
            return secrets.token_urlsafe(32)
        else:
            raise ValueError(f"CRITICAL: {key} not set in production environment")

# Global config instance
config = Config()

# Validate configuration on import
if __name__ == "__main__":
    config.validate_production_config()
    print("✅ Configuration validation passed") 