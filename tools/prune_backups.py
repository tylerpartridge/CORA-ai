#!/usr/bin/env python3
"""
🧭 LOCATION: tools/prune_backups.py
🎯 PURPOSE: Prune old backup checkpoints to keep disk under control
🔗 IMPORTS: pathlib, argparse, datetime, os, shutil, re, sys, json
📤 EXPORTS: CLI script (main)
"""
from __future__ import annotations
import argparse, os, re, sys, json, shutil
from pathlib import Path
import tempfile
from datetime import datetime
BASE = Path("/var/backups/cora").resolve()
TARGETS = ("system", "progress")
DATE_RE = re.compile(r"^\d{4}$")  # first-level YYYY; then MM; then DD

def _is_date_tree(p: Path) -> bool:
    # Expect BASE/sub/YYYY/MM/DD
    try:
        yyyy, mm, dd = p.parts[-3], p.parts[-2], p.parts[-1]
        return (
            re.fullmatch(r"\d{4}", yyyy) and
            re.fullmatch(r"\d{2}", mm) and 1 <= int(mm) <= 12 and
            re.fullmatch(r"\d{2}", dd) and 1 <= int(dd) <= 31
        )
    except Exception:
        return False

def _safe_under_base(path: Path) -> bool:
    try:
        return str(path.resolve()).startswith(str(BASE))
    except Exception:
        return False

def collect_days(root: Path) -> dict[str, list[Path]]:
    """Return map of YYYY-MM-DD -> list of leaf day directories."""
    days: dict[str, list[Path]] = {}
    if not root.exists():
        return days
    for yyyy in root.iterdir():
          if not yyyy.is_dir() or not re.fullmatch(r"\d{4}", yyyy.name): continue
          for mm in yyyy.iterdir():
              if not mm.is_dir() or not re.fullmatch(r"\d{2}", mm.name): continue
              for dd in mm.iterdir():
                  if not dd.is_dir() or not re.fullmatch(r"\d{2}", dd.name): continue
                  day = f"{yyyy.name}-{mm.name}-{dd.name}"
                  days.setdefault(day, []).append(dd)
    return days

def prune_target(sub: str, keep_days: int, dry_run: bool) -> dict:
    root = (BASE / sub).resolve()
    out = {"target": sub, "root": str(root), "kept_days": [], "removed_days": [], "errors": []}
    if not _safe_under_base(root):
        out["errors"].append(f"Unsafe path: {root}")
        return out
    days_map = collect_days(root)
    if not days_map:
        return out
    # sort by date ascending
    sorted_days = sorted(days_map.keys())
    keep = sorted_days[-keep_days:] if len(sorted_days) > keep_days else sorted_days
    remove = [d for d in sorted_days if d not in keep]
    out["kept_days"] = keep
    out["removed_days"] = remove
    # remove whole day directories
    for d in remove:
        for dd in days_map[d]:
            if not _safe_under_base(dd):
                out["errors"].append(f"Refused to remove unsafe {dd}")
                continue
            if dry_run:
                continue
            try:
                shutil.rmtree(dd)
                # attempt to clean empty parents
                for parent in [dd.parent, dd.parent.parent, dd.parent.parent.parent]:
                    if parent.exists() and parent.is_dir():
                        try:
                            next(parent.iterdir())
                        except StopIteration:
                            parent.rmdir()
            except Exception as e:
                out["errors"].append(f"Failed rm {dd}: {e}")
    return out

def main():
    parser = argparse.ArgumentParser(description="Prune old backups under /var/backups/cora")
    parser.add_argument("--keep-days", type=int, default=int(os.getenv("CORA_BACKUP_KEEP_DAYS", "3")))
    parser.add_argument("--only", choices=TARGETS, help="Prune only this subdir")
    parser.add_argument("--dry-run", action="store_true")
    # Hidden test-only override; allowed only under system temp folder
    parser.add_argument("--_test-base", dest="_test_base", default=None)
    args = parser.parse_args()
    if args._test_base:
        tb = Path(args._test_base).resolve()
        tmp_root = Path(tempfile.gettempdir()).resolve()
        if not str(tb).startswith(str(tmp_root)):
            print(json.dumps({"ok": False, "error": "_test-base must be under tmp"})); return 2
        globals()["BASE"] = tb
    if not BASE.exists():
        print(json.dumps({"ok": True, "note": f"{BASE} not present"})); return 0
    targets = [args.only] if args.only else list(TARGETS)
    results = []
    for t in targets:
        results.append(prune_target(t, max(1, args.keep_days), args.dry_run))
    print(json.dumps({"ok": True, "dry_run": args.dry_run, "results": results}, indent=2))
    return 0
if __name__ == "__main__":
    sys.exit(main())
