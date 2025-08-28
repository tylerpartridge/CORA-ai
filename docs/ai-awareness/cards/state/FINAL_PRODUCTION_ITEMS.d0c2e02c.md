# Card: FINAL_PRODUCTION_ITEMS.md

> Source: `docs\ai-awareness\FINAL_PRODUCTION_ITEMS.md`

## Headers:
- # FINAL PRODUCTION ITEMS - GPT-5 AFTERCARE
- ## COMMIT & TAG:
- ## URGENT DATABASE MODEL NEEDED:
- ## SECURITY CLEANUP:
- ## WEBHOOK OPTIMIZATION:

## Content:
```bash git add routes/payment_coordinator.py git commit -m "feat: add webhook idempotency to prevent double-processing" git tag v0.1.0-webhook-fix git push origin main --tags ``` Add to models/database.py: ```python class WebhookEvent(Base):     __tablename__ = "webhook_events"...
