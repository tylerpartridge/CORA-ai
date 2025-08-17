#!/usr/bin/env python3
"""Run import cleanup on routes directory only"""

from pathlib import Path
from import_cleaner import ImportCleaner

# Create cleaner
cleaner = ImportCleaner(backup_dir="features/safe_refactoring/claude/archived_imports")

# Run cleanup on routes only
project_root = Path(".")
print("Cleaning imports in routes directory...\n")
cleaner.clean_project(project_root, dry_run=False, directories=['routes'])

print("\nCleanup complete! All backups saved in archived_imports/")