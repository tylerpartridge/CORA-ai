#!/usr/bin/env python3
"""
Add currency field to users table

This migration adds a currency column to store user's preferred currency.
Default value is 'USD' to maintain backward compatibility.
"""

from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def upgrade(database_url: str = None):
    """Add currency column to users table"""
    if not database_url:
        database_url = os.getenv('DATABASE_URL', 'sqlite:///./cora.db')
    
    engine = create_engine(database_url)
    
    with engine.begin() as conn:
        try:
            # Check if column already exists (for idempotency)
            result = conn.execute(text("PRAGMA table_info(users)"))
            columns = [row[1] for row in result]
            
            if 'currency' not in columns:
                # Add currency column with default value
                conn.execute(text("""
                    ALTER TABLE users 
                    ADD COLUMN currency VARCHAR(8) DEFAULT 'USD'
                """))
                logger.info("Successfully added currency column to users table")
            else:
                logger.info("Currency column already exists in users table")
                
        except OperationalError as e:
            logger.error(f"Migration failed: {e}")
            raise


def downgrade(database_url: str = None):
    """Remove currency column from users table"""
    if not database_url:
        database_url = os.getenv('DATABASE_URL', 'sqlite:///./cora.db')
    
    engine = create_engine(database_url)
    
    with engine.begin() as conn:
        try:
            # SQLite doesn't support DROP COLUMN directly
            # Would need to recreate table without the column
            logger.warning("SQLite doesn't support DROP COLUMN. Manual intervention required for rollback.")
        except OperationalError as e:
            logger.error(f"Rollback failed: {e}")
            raise


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "downgrade":
        downgrade()
    else:
        upgrade()