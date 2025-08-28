# CORA Landing Page & CTA Status Analysis
**Date:** 2025-08-27  
**Focus:** Landing page location, CTA functionality, payment integration

## Landing Page Location & Status

### ✅ **Landing Page: Repository-Based**
- **Location:** `/web/templates/index.html` (repo-hosted)
- **Route:** `GET /` via `routes/pages.py`
- **Status:** Professional construction-themed design implemented
- **Domain:** Live at `https://coraai.tech/`

### ✅ **Supporting Pages Present**
- **Pricing Page:** `/web/templates/pricing.html` via `GET /pricing`
- **About Page:** Route exists for `/about`
- **Features Page:** Route exists for `/features`  
- **How It Works:** Route exists for `/how-it-works`

## CTA Analysis

### ✅ **Landing Page CTAs**
- **Primary CTA:** Email capture form for lead generation
- **Secondary CTAs:** Multiple buttons directing to signup/pricing
- **Design:** Professional construction-themed with hover effects
- **Status:** Functional for lead capture, not connected to payment

### 🚨 **Pricing Page CTA Status - BROKEN**
- **Current State:** Pricing tiers displayed (SOLO, CREW, BUSINESS)
- **CTA Buttons:** Present but **NOT connected** to payment processing
- **Gap:** No functional "Get Started" or "Buy Now" buttons
- **Impact:** Users cannot complete purchases despite viewing pricing

## Payment Integration Status

### ⚠️ **Missing Environment Variables**
```bash
# Required but missing in production:
STRIPE_PUBLISHABLE_KEY=[NEEDED]
STRIPE_SECRET_KEY=[NEEDED]
STRIPE_STARTER_PRICE_ID=[NEEDED]     # For SOLO plan
STRIPE_PROFESSIONAL_PRICE_ID=[NEEDED] # For CREW plan  
STRIPE_ENTERPRISE_PRICE_ID=[NEEDED]  # For BUSINESS plan
STRIPE_WEBHOOK_SECRET=[NEEDED]
```

### ✅ **Payment Infrastructure Ready**
- **Checkout Endpoint:** `POST /api/payments/checkout` implemented
- **Price ID Mapping:** Code references STRIPE_*_PRICE_ID variables (routes/payment_coordinator.py:360-362)
- **Webhook Handler:** `POST /api/payments/webhook` ready for Stripe events

## Missing Pricing Page Template (Minimal CTA Version)

**File:** `web/templates/pricing.html` (needs CTA buttons added)

**Required Addition - Payment Buttons:**
```html
<!-- Add to each pricing card -->
<div class="card-body d-flex flex-column">
    <!-- existing pricing content -->
    
    <div class="mt-auto">
        <button class="btn btn-construction w-100" onclick="startCheckout('SOLO')">
            Get Started - $29/month
        </button>
    </div>
</div>

<script>
async function startCheckout(planType) {
    try {
        const response = await fetch('/api/payments/checkout', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + localStorage.getItem('token')
            },
            body: JSON.stringify({
                plan_type: planType,
                success_url: window.location.origin + '/dashboard',
                cancel_url: window.location.origin + '/pricing'
            })
        });
        
        const data = await response.json();
        if (data.checkout_url) {
            window.location.href = data.checkout_url;
        } else {
            alert('Please log in first to purchase a plan');
            window.location.href = '/login';
        }
    } catch (error) {
        console.error('Checkout error:', error);
        alert('Error starting checkout. Please try again.');
    }
}
</script>
```

## Payment Link Alternative (Using PAYMENT_LINK env var)

**If direct checkout fails, implement payment links:**

```html
<!-- Alternative: Direct Stripe Payment Links -->
<div class="mt-auto">
    <a href="{{ PAYMENT_LINK_SOLO }}" class="btn btn-construction w-100">
        Get Started - $29/month
    </a>
</div>
```

**Required Environment Variables:**
```bash
PAYMENT_LINK_SOLO=https://buy.stripe.com/[payment_link_id]
PAYMENT_LINK_CREW=https://buy.stripe.com/[payment_link_id]  
PAYMENT_LINK_BUSINESS=https://buy.stripe.com/[payment_link_id]
```

## Recommendations

### Immediate (P0 - Revenue Blocking)
1. **Configure Stripe environment variables** in production
2. **Add payment buttons** to pricing.html using checkout endpoint
3. **Test payment flow** end-to-end with test cards

### Short-term (P1 - Conversion Optimization)
1. **Implement Stripe Payment Links** as backup payment method
2. **Add loading states** and error handling to checkout buttons
3. **Track conversion analytics** for pricing page visits → purchases

### Long-term (P2 - Growth)
1. **A/B test pricing page layouts** for higher conversion
2. **Add plan comparison features** to highlight value differences
3. **Implement free trial signup** before payment required

## Current Revenue Impact

**Status:** 🚨 **REVENUE BLOCKED**
- Professional landing page attracts users ✅
- Pricing page displays plans clearly ✅  
- **Payment buttons non-functional** ❌
- **Cannot collect money** despite having payment infrastructure ❌

**Fix Time:** ~60 minutes (Stripe config + button implementation)
**Revenue Impact:** Immediate - can start collecting payments same day