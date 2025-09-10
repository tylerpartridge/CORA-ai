# !/usr/bin/env python3
"""
🧭 LOCATION: /CORA/services/account_purge_service.py
🎯 PURPOSE: 30-day purge skeleton for soft-deleted accounts (service + CLI use)
🔗 IMPORTS: sqlite3, datetime, typing
📤 EXPORTS: AccountPurgeService
"""

import sqlite3
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple


@dataclass
class PurgeResult:
    dry_run: bool
    now: str
    to_purge_count: int
    skipped_active_count: int
    details: List[Dict[str, Any]]


class AccountPurgeService:
    """Minimal purge logic without schema edits.

    Contract:
    - Users with a column `deletion_scheduled` older than 30 days are purge candidates
    - Users still active (is_active truthy) are skipped
    - When dry_run=True, no deletes are executed; returns counts only
    - SQLite-compatible; uses column presence checks
    """

    def __init__(self, db_path: str = "cora.db") -> None:
        self.db_path = db_path

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    @staticmethod
    def _has_column(conn: sqlite3.Connection, table: str, column: str) -> bool:
        cur = conn.execute(f"PRAGMA table_info({table})")
        for row in cur.fetchall():
            if row[1] == column:
                return True
        return False

    @staticmethod
    def _is_truthy(val: Any) -> bool:
        if val is None:
            return False
        s = str(val).strip().lower()
        return s in {"1", "true", "yes", "on"}

    def find_candidates(self, now: Optional[datetime] = None) -> Tuple[List[sqlite3.Row], List[str]]:
        now = now or datetime.utcnow()
        issues: List[str] = []
        with self._connect() as conn:
            # Verify schema presence
            if not self._has_column(conn, "users", "deletion_scheduled"):
                issues.append("users.deletion_scheduled column not found; nothing to purge")
                return [], issues

            rows = conn.execute(
                """
                SELECT id, email, is_active, deletion_scheduled
                FROM users
                WHERE deletion_scheduled IS NOT NULL
                """
            ).fetchall()

            candidates: List[sqlite3.Row] = []
            for r in rows:
                try:
                    # Support multiple datetime storage formats
                    ds_raw = r["deletion_scheduled"]
                    # Accept ISO or naive; attempt parse
                    try:
                        ds = datetime.fromisoformat(str(ds_raw))
                    except Exception:
                        # fallback: common format
                        ds = datetime.strptime(str(ds_raw), "%Y-%m-%d %H:%M:%S")
                    if ds <= now - timedelta(days=30):
                        candidates.append(r)
                except Exception:
                    continue
        return candidates, issues

    def purge(self, dry_run: bool = True, now: Optional[datetime] = None) -> PurgeResult:
        now = now or datetime.utcnow()
        candidates, issues = self.find_candidates(now)
        details: List[Dict[str, Any]] = []
        skipped_active = 0
        purged = 0
        with self._connect() as conn:
            for r in candidates:
                uid = r["id"]
                email = r["email"]
                is_active = self._is_truthy(r["is_active"]) if "is_active" in r.keys() else False
                if is_active:
                    skipped_active += 1
                    details.append({"id": uid, "email": email, "status": "skipped_active"})
                    continue
                details.append({"id": uid, "email": email, "status": "purge_candidate"})
                if dry_run:
                    continue
                # Hard-delete user row (cascades depend on schema; this is minimal)
                conn.execute("DELETE FROM users WHERE id = ?", (uid,))
                purged += 1
            if not dry_run:
                conn.commit()
        return PurgeResult(
            dry_run=dry_run,
            now=now.isoformat(),
            to_purge_count=len(candidates),
            skipped_active_count=skipped_active,
            details=details,
        )
