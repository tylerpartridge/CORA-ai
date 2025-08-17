#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/models/base.py
🎯 PURPOSE: Database configuration and base model
🔗 IMPORTS: SQLAlchemy
📤 EXPORTS: Base, engine, SessionLocal
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import centralized config
from config import config

# Database URL from centralized config
DATABASE_URL = config.DATABASE_URL

# Create engine with PostgreSQL-specific configuration
if "postgresql" in DATABASE_URL:
    engine = create_engine(
        DATABASE_URL,
        pool_size=20,
        max_overflow=30,
        pool_timeout=30,
        pool_recycle=3600,
        pool_pre_ping=True
    )
else:
    # SQLite configuration with connection pooling for concurrent users
    from sqlalchemy import event
    import sqlite3
    
    engine = create_engine(
        DATABASE_URL,
        connect_args={
            "check_same_thread": False,
            "timeout": 30,  # 30 second timeout for lock contention
        },
        pool_size=10,           # Max concurrent connections
        max_overflow=20,        # Additional connections during peak
        pool_timeout=30,        # Wait time for connection
        pool_recycle=3600,      # Recycle connections every hour
        pool_pre_ping=True      # Verify connection before use
    )
    
    # Enable WAL mode for better concurrent access
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        if isinstance(dbapi_connection, sqlite3.Connection):
            cursor = dbapi_connection.cursor()
            # Enable WAL mode for better concurrent access
            cursor.execute("PRAGMA journal_mode=WAL")
            # Optimize for performance
            cursor.execute("PRAGMA synchronous=NORMAL")
            cursor.execute("PRAGMA cache_size=1000")
            cursor.execute("PRAGMA temp_store=MEMORY")
            cursor.close()

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()