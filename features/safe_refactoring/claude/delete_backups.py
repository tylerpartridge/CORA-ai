#!/usr/bin/env python3
"""Delete all backup files"""

from pathlib import Path

files_to_delete = [
    Path('tools\secure_backup.py'),
    Path('web\node_modules\form-data\README.md.bak'),
    Path('node_modules\form-data\README.md.bak'),
    Path('deployment\app.py.backup'),
    Path('venv\Lib\site-packages\twilio\rest\numbers\v2\regulatory_compliance\bundle\bundle_copy.py'),
    Path('venv\Lib\site-packages\pandas\tests\series\methods\test_copy.py'),
    Path('venv\Lib\site-packages\pandas\tests\indexes\multi\test_copy.py'),
    Path('venv\Lib\site-packages\pandas\tests\frame\methods\test_copy.py'),
]

deleted = 0
for f in files_to_delete:
    if f.exists():
        f.unlink()
        deleted += 1
        print(f'Deleted: {f}')

print(f'\nDeleted {deleted} files')
