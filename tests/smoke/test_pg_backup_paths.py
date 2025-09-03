import os
import re

def test_backup_filename_pattern():
    fname = "cora_pg_20250903_191240.dump"
    assert re.match(r"^cora_pg_\d{8}_\d{6}\.dump$", fname)

def test_default_backup_dir_env():
    backup_dir = os.environ.get("CORA_PG_BACKUP_DIR", "/var/backups/cora/pg")
    assert backup_dir.endswith("/pg")


