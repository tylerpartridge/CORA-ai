#!/usr/bin/env python3
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from dependencies.database import get_db
from dependencies.auth import require_admin, get_current_user

router = APIRouter(prefix="/api", tags=["feature_flags"])


@router.get("/feature-flags")
async def get_flags(db: Session = Depends(get_db), user=Depends(get_current_user)):
    rows = db.execute("SELECT name, enabled, rollout_percentage FROM feature_flags").fetchall()
    return {name: bool(enabled) for (name, enabled, _rollout) in rows}


@router.post("/admin/feature-flags/{flag_name}/toggle")
async def toggle_flag(flag_name: str, db: Session = Depends(get_db), _: str = Depends(require_admin)):
    row = db.execute("SELECT enabled FROM feature_flags WHERE name=:n", {"n": flag_name}).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Flag not found")
    new_val = 0 if bool(row[0]) else 1
    db.execute("UPDATE feature_flags SET enabled=:v, updated_at=CURRENT_TIMESTAMP WHERE name=:n", {"v": new_val, "n": flag_name})
    db.commit()
    return {"name": flag_name, "enabled": bool(new_val)}


@router.post("/admin/feature-flags/{flag_name}/rollout")
async def set_rollout(flag_name: str, payload: dict, db: Session = Depends(get_db), _: str = Depends(require_admin)):
    pct = int(payload.get("percentage", 0))
    pct = max(0, min(100, pct))
    updated = db.execute("UPDATE feature_flags SET rollout_percentage=:p, updated_at=CURRENT_TIMESTAMP WHERE name=:n", {"p": pct, "n": flag_name})
    if updated.rowcount == 0:
        raise HTTPException(status_code=404, detail="Flag not found")
    db.commit()
    return {"name": flag_name, "rollout_percentage": pct}


