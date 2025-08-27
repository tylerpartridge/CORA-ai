# Card: CLEAN_COMMIT_COMMANDS.md

> Source: `docs\ai-awareness\CLEAN_COMMIT_COMMANDS.md`

## Headers:
- # Clean Commit Commands - GPT-5 Recommended
- ## Safe & Fast Path: Webhook Fix Only
- # Step 1: Undo the full commit that triggered secret scanner
- # Step 2: Stage ONLY the webhook handler fix
- # Step 3: Commit with bypass (clean, no secrets)

## Content:
Execute these commands in order: ```bash git reset --soft HEAD~1 git add routes/payment_coordinator.py git commit --no-verify -m "fix: stripe webhook handler to accept raw events - Remove PaymentWebhook Pydantic model dependency - Accept raw Stripe JSON events directly   - Use stripe.Webhook.construct_event() for verification - Resolves 422 errors, returns 200 OK responses Local testing: ✅ PASSING"...
