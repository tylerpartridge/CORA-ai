#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/utils/async_file_utils.py
🎯 PURPOSE: Async file utilities for JSON operations
🔗 IMPORTS: aiofiles, json, pathlib
📤 EXPORTS: async_read_json, async_write_json, async_ensure_dir
"""

import json
import aiofiles
from pathlib import Path


async def async_ensure_dir(directory: Path) -> None:
    """Ensure directory exists"""
    directory.mkdir(parents=True, exist_ok=True)


async def async_read_json(filepath: Path) -> list:
    """Read JSON file asynchronously"""
    if not filepath.exists():
        return []
    
    async with aiofiles.open(filepath, 'r') as f:
        content = await f.read()
        return json.loads(content) if content else []


async def async_write_json(filepath: Path, data: list) -> None:
    """Write JSON file asynchronously"""
    async with aiofiles.open(filepath, 'w') as f:
        await f.write(json.dumps(data, indent=2))