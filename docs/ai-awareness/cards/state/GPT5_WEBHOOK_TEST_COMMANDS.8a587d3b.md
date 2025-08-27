# Card: GPT5_WEBHOOK_TEST_COMMANDS.md

> Source: `docs\ai-awareness\GPT5_WEBHOOK_TEST_COMMANDS.md`

## Headers:
- # GPT-5 Webhook Test Commands - Execute These On Production Server
- ## PHASE 1: CLI Validation (Prove webhook handler works)
- ### Switch prod to CLI secret:
- # On prod server (root@159.203.183.48):
- # Confirm secret loaded:

## Content:
```bash cd /var/www/cora cp .env .env.bak.$(date +%Y%m%d-%H%M%S) sed -i 's/^STRIPE_WEBHOOK_SECRET=.*/STRIPE_WEBHOOK_SECRET=whsec_479a79d691712f2cc303dc72f3629939a8449b5e9011ba0183fc37f9c7ed1cde/' .env systemctl restart cora.service pid=$(pgrep -f "uvicorn"); tr '\0' '\n' </proc/$pid/environ | grep STRIPE_WEBHOOK_SECRET ``` ```bash stripe listen --forward-to https://coraai.tech/api/payments/webhook stripe trigger payment_intent.succeeded...
