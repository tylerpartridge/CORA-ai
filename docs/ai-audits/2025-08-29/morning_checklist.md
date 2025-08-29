# 🌅 Morning Checklist - 2025-08-30

## 📋 Pre-Work Setup

### 1. Pull Latest Changes
```bash
git checkout main && git pull
```

### 2. Environment Configuration (Choose One)

**Option A: Payment Link (Primary)**
```bash
export PAYMENT_LINK_URL="https://buy.stripe.com/..."
# When set, Pricing page shows direct link to hosted Payment Link
```

**Option B: Checkout Fallback**
```bash
# Unset PAYMENT_LINK_URL to use Checkout fallback
unset PAYMENT_LINK_URL
export STRIPE_SECRET_KEY="sk_test_..."
export STRIPE_PRICE_ID="price_..."  
export STRIPE_MODE="payment"
# When PAYMENT_LINK_URL unset, button triggers /api/checkout redirect
```

### 3. Verification Steps

**Server Test:**
```bash
# Run server
python app.py

# Visit in browser:
# - /pricing - Verify CTA path works
#   - Link behavior when PAYMENT_LINK_URL set
#   - Button → /api/checkout redirect when unset (fallback)
```

**CI Guard Test (Optional):**
```bash
# Should PASS - awareness namespace compliance
bash ./ci_duplicate_guard.sh
```

### 4. Development Workflow

**Midday Batch Ritual:**
- Run Cursor Task: "Midday Batch (Draft PR)"
- Ensure all Stripe CTA tasks are progressing
- Check tests pass locally before commit

## 🎯 Today's Focus: Money-path Implementation

**Priority Tasks:**
1. ✅ Add nav "Pricing" link + CTA
2. ✅ Payment Link path (PAYMENT_LINK_URL)  
3. ✅ Checkout fallback (/api/checkout, STRIPE_* envs)
4. ✅ Success/Cancel page render
5. ✅ README quickstart + tests

**Success Criteria:**
- With PAYMENT_LINK_URL set → Pricing CTA opens hosted Payment Link
- With PAYMENT_LINK_URL unset + Stripe keys set → CTA triggers /api/checkout and redirects
- All tests green locally

**Expected Deliverable:**
Single PR: `feat(payments): add Pricing + Pay CTA; Payment Link first, Checkout fallback; config + tests`

---

**Awareness Status:** ✅ GREEN (namespace consolidated, CI guard active)