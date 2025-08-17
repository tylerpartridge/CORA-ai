#!/usr/bin/env python3
"""
Account Management Endpoints
- Export my data (JSON download)
- Schedule account deletion with 30-day grace
"""

from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, Body, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from dependencies.database import get_db
from dependencies.auth import get_current_user
from models.user import User
from models.expense import Expense

router = APIRouter(prefix="/api", tags=["account"])


@router.get("/export-my-data")
async def export_user_data(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Export all user data as JSON for the current user."""
    try:
        user_data = {
            "profile": {
                "id": current_user.id,
                "email": current_user.email,
                "name": getattr(current_user, 'name', None),
                "created_at": str(getattr(current_user, 'created_at', '')),
            },
            "expenses": [],
            "settings": {},
            "audit_logs": []
        }

        expenses = db.query(Expense).filter(Expense.user_id == current_user.id).all()
        # Expect Expense model to have to_dict; fall back to minimal fields
        for e in expenses:
            if hasattr(e, 'to_dict'):
                user_data["expenses"].append(e.to_dict())
            else:
                user_data["expenses"].append({
                    "id": getattr(e, 'id', None),
                    "amount_cents": getattr(e, 'amount_cents', None),
                    "vendor": getattr(e, 'vendor', None),
                    "description": getattr(e, 'description', None),
                    "expense_date": str(getattr(e, 'expense_date', '')),
                })

        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"cora_data_export_{current_user.id}_{ts}.json"
        return JSONResponse(content=user_data, headers={"Content-Disposition": f"attachment; filename={filename}"})
    except Exception as e:
        return JSONResponse({"error": "Export failed"}, status_code=500)


@router.post("/delete-my-account")
async def delete_account(
    confirmation: str = Body(..., embed=True),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Soft delete: schedule account deletion in 30 days; deactivate immediately."""
    try:
        if confirmation != f"DELETE {current_user.email}":
            raise HTTPException(status_code=400, detail="Invalid confirmation")

        # Mark soft-deleted; fields may vary across schemas
        setattr(current_user, 'deleted_at', datetime.now())
        setattr(current_user, 'deletion_scheduled', datetime.now() + timedelta(days=30))
        try:
            setattr(current_user, 'is_active', False)
        except Exception:
            pass
        db.commit()

        return JSONResponse({
            "message": "Account scheduled for deletion in 30 days",
            "recovery_deadline": str(getattr(current_user, 'deletion_scheduled', ''))
        })
    except HTTPException:
        raise
    except Exception:
        db.rollback()
        return JSONResponse({"error": "Deletion failed"}, status_code=500)


