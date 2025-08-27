# Payment Implementation Notes

## Implementation Summary (2025-08-27)

### Files Modified
1. **web/templates/pricing.html** - Added Jinja2 conditionals to use payment links when available, fallback to checkout API
2. **routes/pages.py** - Updated `/pricing` route to pass payment link environment variables to template
3. **config/config.py** - Added centralized environment bindings for Stripe configuration and payment links
4. **tests/test_pricing_cta.py** - Created comprehensive test suite for pricing CTA behavior

### Environment Variables Added
```bash
# Direct Stripe Payment Links (optional - highest priority)
PAYMENT_LINK_SOLO=https://buy.stripe.com/your_solo_link
PAYMENT_LINK_CREW=https://buy.stripe.com/your_crew_link
PAYMENT_LINK_BUSINESS=https://buy.stripe.com/your_business_link

# Alternative: Single payment link for all plans
PAYMENT_LINK=https://buy.stripe.com/your_general_link

# Stripe API Configuration (for checkout session creation)
STRIPE_SECRET_KEY=sk_live_...
STRIPE_PUBLISHABLE_KEY=pk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Price IDs (for checkout session creation)
STRIPE_STARTER_PRICE_ID=price_...
STRIPE_PROFESSIONAL_PRICE_ID=price_...
STRIPE_ENTERPRISE_PRICE_ID=price_...
```

### How It Works
1. **If PAYMENT_LINK_* is set**: CTA buttons become direct links to Stripe Payment Links
2. **Otherwise**: CTA buttons call JavaScript `initiateCheckout()` function which POSTs to `/api/payments/checkout`

### Configuration Priority
1. Plan-specific payment links (`PAYMENT_LINK_SOLO`, `PAYMENT_LINK_CREW`, `PAYMENT_LINK_BUSINESS`)
2. General payment link (`PAYMENT_LINK`)
3. Checkout API fallback (requires Stripe API keys and price IDs)

### Testing
Run tests with: `RUN_PRICING_TESTS=1 pytest tests/test_pricing_cta.py -v`

### Production Deployment
1. Set environment variables in production
2. No code changes needed - behavior is entirely env-driven
3. Test with: `curl https://coraai.tech/pricing | grep -E "(buy.stripe.com|initiateCheckout)"`

### Security Notes
- Never commit actual Stripe keys to repository
- Use environment variables or secrets management service
- Payment links are safe to expose in HTML (they're public URLs)
- Stripe API keys must remain server-side only