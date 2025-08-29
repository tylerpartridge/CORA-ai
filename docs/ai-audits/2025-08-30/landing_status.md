# LANDING STATUS: CTA BEHAVIOR MATRIX
**Date:** 2025-08-30  
**Scope:** Payment CTA behavior with/without PAYMENT_LINK configuration  
**Template:** web/templates/pricing.html  

## Current Implementation Analysis

### Template Logic (Lines 368-580)
The pricing page implements a clean conditional pattern:

```html
{% if payment_link_solo %}
<a href="{{ payment_link_solo }}" class="btn-construction-secondary">Start Free Trial</a>
{% else %}
<button class="btn-construction-secondary" onclick="initiateCheckout('SOLO')">Start Free Trial</button>  
{% endif %}
```

### Payment Method Matrix

| Plan | PAYMENT_LINK Present | PAYMENT_LINK Absent | Template Lines | Status |
|------|---------------------|---------------------|----------------|---------|
| SOLO | Direct link to `payment_link_solo` | Link to `/signup?plan=SOLO` | 368-376 | ✅ WIRED |
| CREW | Direct link to `payment_link_crew` | Link to `/signup?plan=CREW` | 472-480 | ✅ WIRED |
| BUSINESS | Direct link to `payment_link_business` | Link to `/signup?plan=BUSINESS` | 572-580 | ✅ WIRED |

### JavaScript Fallback Behavior (Lines 1116-1151) - NO LONGER USED

**Status:** ✅ REMOVED - CTAs now use direct links or /signup fallback, no JavaScript checkout modal

**Previous Endpoint:** `/api/payments/checkout` (NOT IMPLEMENTED)
**New Behavior:** 
- With PAYMENT_LINK env vars → Direct Stripe Payment Links (opens in new tab)
- Without PAYMENT_LINK env vars → Direct link to `/signup?plan={PLAN}` (same tab)
- No modal errors, no "Unable to start checkout" popups

## Environment Variable Requirements

### Primary Method (Payment Links) - PRODUCTION READY
```bash
# Production values (14-day trial, card required)
PAYMENT_LINK_SOLO=https://buy.stripe.com/5kQfZh1yqarab9P8SXgw002
PAYMENT_LINK_CREW=https://buy.stripe.com/bJefZhdh8arafq57OTgw001
PAYMENT_LINK_BUSINESS=https://buy.stripe.com/8x2fZh1yq7eYcdT6KPgw000

# Alternative: Generic link for all plans
PAYMENT_LINK=https://buy.stripe.com/solo_link_id
PAYMENT_LINK_CREW=https://buy.stripe.com/crew_link_id  
PAYMENT_LINK_BUSINESS=https://buy.stripe.com/business_link_id
```

### Fallback Method (Checkout API)
```bash
STRIPE_API_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...
```

## Current Status Assessment

### ✅ READY COMPONENTS
- **Template Logic:** Conditional CTA blocks implemented
- **JavaScript Handler:** Complete error handling and redirects  
- **Plan Detection:** Proper plan type passing to backend
- **User Flow:** Signup redirect for unauthenticated users

### ❌ MISSING COMPONENTS  
- **Environment Variables:** No PAYMENT_LINK_* configured
- **Checkout Endpoint:** `/api/payments/checkout` not implemented
- **Success/Cancel Pages:** `/subscription?status=success` handling unclear

## Recommended Configuration Strategy

### Option 1: Payment Links (Preferred)
**Pros:** Simpler, direct to Stripe, no backend logic  
**Cons:** Less control over user flow  
**Setup:** Configure 3 environment variables  
**Effort:** 15 minutes  

### Option 2: Checkout API (Fallback)  
**Pros:** Full control, custom success/cancel handling  
**Cons:** More complex, requires endpoint implementation  
**Setup:** Implement `/api/payments/checkout` endpoint  
**Effort:** 2-3 hours  

## User Experience Impact

### With Payment Links
1. User clicks "Start Free Trial"  
2. Direct redirect to Stripe-hosted checkout
3. Stripe handles success/cancel redirects
4. Minimal CORA backend involvement

### With Checkout API
1. User clicks "Start Free Trial"
2. AJAX call to `/api/payments/checkout`
3. Redirect to Stripe Checkout Session  
4. CORA handles success/cancel flow with custom logic

## Security Considerations

- **Payment Links:** Stripe-validated, secure by default
- **Checkout API:** Requires proper authentication and webhook handling  
- **Environment Variables:** Both methods need secure credential storage

## Recommendation

**IMMEDIATE:** Configure Payment Links (Option 1) for fastest launch  
**FUTURE:** Implement Checkout API for enhanced user experience control  

The current template implementation cleanly supports both approaches without modification.