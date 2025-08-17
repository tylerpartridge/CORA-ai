#!/usr/bin/env python3
"""Run import cleanup on all directories"""

from pathlib import Path
from import_cleaner import ImportCleaner

# Create cleaner
cleaner = ImportCleaner(backup_dir="features/safe_refactoring/claude/archived_imports")

# Run cleanup on models and services
project_root = Path(".")
print("Cleaning imports in models and services directories...\n")
cleaner.clean_project(project_root, dry_run=False, directories=['models', 'services'])

print("\nCleanup complete! All backups saved in archived_imports/")