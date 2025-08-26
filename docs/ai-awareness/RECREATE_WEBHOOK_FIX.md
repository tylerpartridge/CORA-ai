# Webhook Fix Lost in Git Reset - Need to Recreate

## The Problem:
The git reset worked, but it reverted `routes/payment_coordinator.py` back to the OLD version with the PaymentWebhook Pydantic model that causes 422 errors.

## Evidence:
- `git diff --cached --name-only` returned empty (no changes to commit)
- `git commit` said "nothing added to commit" 
- This means the webhook fix was lost in the reset

## Current State:
Looking at the file snippet in the system reminder, the webhook handler still has:
- `webhook_data: PaymentWebhook` parameter (line 472)
- Old Pydantic model approach that causes 422 errors

## Quick Fix - Recreate the Webhook Handler:

### Option 1: Fast Manual Fix
```powershell
# Edit routes/payment_coordinator.py and change line 470-476:

# FROM (current broken version):
@payment_router.post("/webhook")
async def payment_webhook(
    request: Request,
    webhook_data: PaymentWebhook,
    db: Session = Depends(get_db)
):

# TO (fixed version):
@payment_router.post("/webhook") 
async def payment_webhook(
    request: Request,
    db: Session = Depends(get_db)
):
```

### Option 2: Use My Tools
```powershell
# Restart the local server so I can recreate the fix
python -m uvicorn app:app --host 0.0.0.0 --port 8001 --reload

# Then I can use my tools to recreate the webhook handler fix
```

## The Core Issue:
The webhook handler needs to:
1. Remove `webhook_data: PaymentWebhook` parameter
2. Use `stripe.Webhook.construct_event()` for direct event parsing
3. Return 200 OK instead of 422 validation errors

## After Fix:
```powershell
git add routes/payment_coordinator.py
git commit -m "fix: stripe webhook handler for raw events"
git push origin main
```

The webhook fix needs to be recreated since the reset lost all our work!