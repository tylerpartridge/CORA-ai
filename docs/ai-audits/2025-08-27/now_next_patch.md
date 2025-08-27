# NOW/NEXT Patch - MVP Payment Flow Completion
**Date:** 2025-08-27  
**Context:** CORA is 90% MVP-ready, blocked only by payment configuration and CTA connection

## Paste-Ready Updates

### NOW (2025-08-27)
**North Star:** Enable payment processing to start collecting revenue from existing traffic

**Actions (≤ 90 minutes total):**
- Configure Stripe production environment variables (STRIPE_SECRET_KEY, price IDs, webhook secret) - 30min
- Add functional payment buttons to pricing.html that call /api/payments/checkout endpoint - 45min  
- Test complete purchase flow with Stripe test cards and verify webhook delivery - 15min

### NEXT (2025-08-27)
**Sprint Tasks (15-60 min each):**

1. **[P0] Stripe Environment Configuration** (30min)
   - Set STRIPE_SECRET_KEY, STRIPE_PUBLISHABLE_KEY, STRIPE_WEBHOOK_SECRET in production
   - Configure STRIPE_STARTER_PRICE_ID, STRIPE_PROFESSIONAL_PRICE_ID, STRIPE_ENTERPRISE_PRICE_ID
   - Verify webhook endpoint receives events properly

2. **[P0] Pricing Page Payment Integration** (45min)
   - Add JavaScript checkout buttons to web/templates/pricing.html
   - Wire buttons to call /api/payments/checkout with correct plan_type
   - Implement loading states and basic error handling

3. **[P0] Payment Flow Testing** (30min) 
   - Test end-to-end purchase with Stripe test cards (4242 4242 4242 4242)
   - Verify webhook processing creates user subscriptions
   - Confirm successful payments redirect to dashboard

4. **[P1] Payment Link Backup System** (45min)
   - Create Stripe Payment Links for each plan tier
   - Add PAYMENT_LINK_* environment variables as backup
   - Implement fallback buttons if checkout session creation fails

5. **[P1] Production Webhook Verification** (30min)
   - Add signature verification to webhook endpoint using STRIPE_WEBHOOK_SECRET
   - Test webhook delivery in production environment
   - Monitor webhook events for payment confirmation

6. **[P1] CSV Upload Production Validation** (45min)
   - Test file upload limits (10MB) with large CSV files
   - Verify OCR processing works with production image uploads
   - Check user-specific storage permissions and access

7. **[P2] Report Generation Load Testing** (60min)
   - Test PDF generation under concurrent user load
   - Verify report download performance with large files
   - Monitor memory usage during batch report generation

## Implementation Notes

**Payment Button JavaScript Template:**
```javascript
async function startCheckout(planType) {
    const response = await fetch('/api/payments/checkout', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ plan_type: planType })
    });
    const data = await response.json();
    if (data.checkout_url) window.location.href = data.checkout_url;
}
```

**Required Environment Variables:**
- STRIPE_SECRET_KEY (from Stripe Dashboard > Developers > API Keys)
- STRIPE_PUBLISHABLE_KEY (from Stripe Dashboard > Developers > API Keys)  
- STRIPE_WEBHOOK_SECRET (from Stripe Dashboard > Developers > Webhooks)
- STRIPE_STARTER_PRICE_ID, STRIPE_PROFESSIONAL_PRICE_ID, STRIPE_ENTERPRISE_PRICE_ID (from Stripe Products)

**Validation Checklist:**
- [ ] Test card 4242424242424242 completes purchase successfully
- [ ] Webhook receives payment_intent.succeeded events
- [ ] User gains access to dashboard after successful payment
- [ ] Failed payments show appropriate error messages
- [ ] All three pricing tiers (SOLO/CREW/BUSINESS) work correctly