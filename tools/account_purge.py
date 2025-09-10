#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/tools/account_purge.py
🎯 PURPOSE: CLI entrypoint to run 30-day purge (dry-run by default)
🔗 IMPORTS: argparse, json
📤 EXPORTS: __main__
"""

import argparse
import json
from datetime import datetime

from services.account_purge_service import AccountPurgeService


def main():
    parser = argparse.ArgumentParser(description="Run 30-day account purge (dry-run by default)")
    parser.add_argument("--db", default="cora.db", help="Path to SQLite DB (default: cora.db)")
    parser.add_argument("--dry-run", action="store_true", help="Do not delete; only report")
    parser.add_argument("--now", default=None, help="Override current time (ISO-8601)")
    args = parser.parse_args()

    now = None
    if args.now:
        now = datetime.fromisoformat(args.now)

    svc = AccountPurgeService(db_path=args.db)
    result = svc.purge(dry_run=args.dry_run or True, now=now)
    print(json.dumps({
        "dry_run": result.dry_run,
        "now": result.now,
        "to_purge_count": result.to_purge_count,
        "skipped_active_count": result.skipped_active_count,
        "details": result.details,
    }, indent=2))


if __name__ == "__main__":
    main()


