# FINAL PRODUCTION ITEMS - GPT-5 AFTERCARE

## COMMIT & TAG:
```bash
git add routes/payment_coordinator.py
git commit -m "feat: add webhook idempotency to prevent double-processing"
git tag v0.1.0-webhook-fix
git push origin main --tags
```

## URGENT DATABASE MODEL NEEDED:
Add to models/database.py:
```python
class WebhookEvent(Base):
    __tablename__ = "webhook_events"
    id = Column(Integer, primary_key=True)
    stripe_event_id = Column(String(255), unique=True, index=True)
    event_type = Column(String(100))
    processed_at = Column(DateTime)
```

## SECURITY CLEANUP:
- Rotate CLI secret: whsec_479a79d691712f2cc303dc72f3629939a8449b5e9011ba0183fc37f9c7ed1cde
- Ensure prod uses live secret (not CLI)
- Delete sensitive .md files

## WEBHOOK OPTIMIZATION:
- Limit Stripe webhook to needed events only
- Add monitoring/alerting for error rates

WEBHOOK CORE: ✅ WORKING
PRODUCTION POLISH: ⏳ THESE ITEMS