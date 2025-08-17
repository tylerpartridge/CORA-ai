#!/usr/bin/env python3
import random, string
from typing import List
from fastapi import APIRouter, Depends, Body, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from dependencies.database import get_db
from dependencies.auth import get_current_user

router = APIRouter(prefix="/api/referral", tags=["referral"])


def generate_referral_code(user_id: int) -> str:
    prefix = f"CORA{user_id}"
    suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"{prefix}{suffix}"


@router.get("/my-code")
async def get_referral_code(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    row = db.execute("SELECT referral_code FROM referrals WHERE referrer_id=:u", {"u": current_user.id}).fetchone()
    if not row:
        # Create code with collision detection
        for _ in range(5):
            code = generate_referral_code(current_user.id)
            exists = db.execute("SELECT 1 FROM referrals WHERE referral_code=:c", {"c": code}).fetchone()
            if not exists:
                db.execute("INSERT INTO referrals(referrer_id, referral_code) VALUES(:u, :c)", {"u": current_user.id, "c": code})
                db.commit()
                row = (code,)
                break
        if not row:
            raise HTTPException(status_code=500, detail="Failed to generate referral code")
    code = row[0]
    converted = db.execute("SELECT COUNT(1) FROM referral_conversions WHERE referral_code=:c AND converted=1", {"c": code}).fetchone()[0]
    return {"code": code, "link": f"https://coraai.com/signup?ref={code}", "successful_referrals": converted}


@router.post("/send-invite")
async def send_invite(emails: List[str] = Body(...), db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    code_row = db.execute("SELECT referral_code FROM referrals WHERE referrer_id=:u", {"u": current_user.id}).fetchone()
    if not code_row:
        raise HTTPException(status_code=400, detail="Referral code not found")
    code = code_row[0]
    # Record invitations (email delivery can be wired later)
    for email in emails[:10]:
        db.execute("INSERT INTO referral_invites(referrer_id, invited_email, referral_code) VALUES(:u, :e, :c)", {"u": current_user.id, "e": email, "c": code})
    db.commit()
    return {"sent": len(emails)}


