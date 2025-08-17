#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/dependencies/database.py
🎯 PURPOSE: Database connection dependency for FastAPI
🔗 IMPORTS: sqlite3, pathlib
📤 EXPORTS: get_db
"""

import sqlite3
from pathlib import Path
from typing import Generator

def get_db() -> Generator[sqlite3.Connection, None, None]:
    """Get database connection - Updated to use main cora.db file"""
    # Use the same database as config.py for consistency
    db_path = Path("cora.db")
    
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    
    try:
        yield conn
    finally:
        conn.close() 