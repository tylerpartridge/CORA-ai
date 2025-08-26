# GPT-5 Webhook Test Commands - Execute These On Production Server

## PHASE 1: CLI Validation (Prove webhook handler works)

### Switch prod to CLI secret:
```bash
# On prod server (root@159.203.183.48):
cd /var/www/cora
cp .env .env.bak.$(date +%Y%m%d-%H%M%S)
sed -i 's/^STRIPE_WEBHOOK_SECRET=.*/STRIPE_WEBHOOK_SECRET=whsec_479a79d691712f2cc303dc72f3629939a8449b5e9011ba0183fc37f9c7ed1cde/' .env
systemctl restart cora.service

# Confirm secret loaded:
pid=$(pgrep -f "uvicorn"); tr '\0' '\n' </proc/$pid/environ | grep STRIPE_WEBHOOK_SECRET
```

### Test with Stripe CLI:
```bash
# On Windows (local):
stripe listen --forward-to https://coraai.tech/api/payments/webhook
stripe trigger payment_intent.succeeded

# Expected: [200] POST https://coraai.tech/api/payments/webhook
```

## PHASE 2: Production Validation (Real events)

### Switch back to live destination secret:
```bash
# On prod server:
sed -i 's/^STRIPE_WEBHOOK_SECRET=.*/STRIPE_WEBHOOK_SECRET=whsec_jXC5MOJ4Sy5irlZaS3SW8vSveyjpGely/' .env
systemctl restart cora.service
```

### Test with real Stripe event:
- Go to Stripe Dashboard (Live mode)
- Create $1 Payment Link charge
- Check Event deliveries for 200 OK

## VERIFICATION COMMANDS:

```bash
# Check service logs:
journalctl -u cora.service -n 50 --no-pager

# Check webhook response:
curl -X POST https://coraai.tech/api/payments/webhook \
  -H "Content-Type: application/json" \
  -d '{"test":"data"}'
# Should return: 400 Missing Stripe signature (GOOD)
```

## EXPECTED RESULTS:
- ✅ CLI test: 200 OK in CLI console + journalctl
- ✅ Live test: 200 OK in Stripe Dashboard Event deliveries
- ✅ Webhook handler working correctly

**NO CODE CHANGES NEEDED. JUST SECRET SWAPPING AND TESTING.**