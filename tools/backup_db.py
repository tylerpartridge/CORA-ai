#!/usr/bin/env python3
"""
Database backup script for CORA
- Supports SQLite and PostgreSQL
- Stores backups in /data/archive/ with timestamped filenames
"""
import os
import shutil
import subprocess
from datetime import datetime
from urllib.parse import urlparse

BACKUP_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'archive')
os.makedirs(BACKUP_DIR, exist_ok=True)

DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///../data/cora.db')
parsed = urlparse(DATABASE_URL)
now = datetime.now().strftime('%Y%m%d_%H%M%S')

try:
    if parsed.scheme.startswith('sqlite'):
        db_path = parsed.path.lstrip('/')
        if not os.path.exists(db_path):
            print(f"[ERROR] SQLite DB not found: {db_path}")
            exit(1)
        backup_file = os.path.join(BACKUP_DIR, f'cora_sqlite_backup_{now}.db')
        shutil.copy2(db_path, backup_file)
        print(f"[OK] SQLite backup created: {backup_file}")
    elif parsed.scheme.startswith('postgres'):
        # Example: postgresql://user:pass@host:port/dbname
        user = parsed.username
        password = parsed.password
        host = parsed.hostname
        port = parsed.port or 5432
        dbname = parsed.path.lstrip('/')
        backup_file = os.path.join(BACKUP_DIR, f'cora_postgres_backup_{now}.sql')
        env = os.environ.copy()
        if password:
            env['PGPASSWORD'] = password
        cmd = [
            'pg_dump',
            '-h', host,
            '-p', str(port),
            '-U', user,
            '-F', 'c',
            '-b',
            '-v',
            '-f', backup_file,
            dbname
        ]
        print(f"[INFO] Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, env=env)
        if result.returncode == 0:
            print(f"[OK] PostgreSQL backup created: {backup_file}")
        else:
            print(f"[ERROR] pg_dump failed with code {result.returncode}")
    else:
        print(f"[ERROR] Unsupported DB scheme: {parsed.scheme}")
except Exception as e:
    print(f"[ERROR] Backup failed: {e}") 