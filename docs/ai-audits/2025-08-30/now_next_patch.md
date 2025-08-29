# NOW/NEXT PATCH RECOMMENDATIONS
**Date:** 2025-08-30  
**Purpose:** Minimal updates to awareness files based on MVP audit findings  
**Append Method:** Newest entries on top  

## Proposed NOW.md Changes

**PREPEND to NOW.md:**
```markdown
### 2025-08-30T14:00:00 — Payment Links WIRED, Checkout Endpoint Optional
**Money-path: Direct Stripe Payment Links Implemented**

✅ COMPLETED:
- Payment Link routing: routes/pages.py passes env vars to template
- Template CTAs: Conditional logic for Payment Links vs /signup fallback  
- Tests: Comprehensive coverage of all payment link scenarios
- Documentation: Production links documented with 14-day trial info

Current Status:
- ✅ With PAYMENT_LINK_* env vars → Direct to Stripe (new tab)
- ✅ Without env vars → Fallback to /signup?plan=X (same tab)
- ✅ No JavaScript modal errors or "Unable to start checkout" popups
- ⏸️ /api/payments/checkout endpoint → OPTIONAL (nice-to-have)

Remaining:
1. Set production env vars (values documented)
2. Deploy and restart service
3. Add timezone selection to signup flow (1-2 hours)
```

## Proposed NEXT.md Changes  

**PREPEND to NEXT.md:**
```markdown
### 2025-08-30T12:00:00 — Revised MVP Completion Strategy
**Priority: Complete 12 MVP Partials (7-11 hours total)**

**[P0] Launch Blockers (1-2 hours):**
1. ✅ DONE: Payment links wired with /signup fallback
2. Configure PAYMENT_LINK_* env vars in production (15 min)
3. Timezone picker: Add to signup/settings UI (1-2 hours)
4. End-to-end payment flow smoke test (15 min)

**[P1] User Experience (4-6 hours):**  
5. Date range export filters (routes/account_management.py)
6. Email unsubscribe links (web/templates/emails/)
7. Onboarding save/resume/skip (routes/onboarding_routes.py)
8. Minimum data validation for weekly reports

**[P2] Polish (1-2 hours):**
9. Delete account UI integration 
10. Export filename standardization
11. Final payment success/cancel page testing

**COMPLETED P0 Discovery:**
- ✅ MVP audit: 12/12 partials mapped with effort estimates
- ✅ Payment infrastructure: Templates ready, endpoint missing
- ✅ Critical path: Payment integration (2-3 hours)
```

## Implementation Notes

### Critical Path Analysis
The audit revealed that payment functionality is 90% complete:
- ✅ Pricing page template with conditional PAYMENT_LINK logic
- ✅ JavaScript fallback to /api/payments/checkout  
- ✅ Stripe OAuth integration routes
- ❌ Missing /api/payments/checkout endpoint implementation

### Effort Distribution  
- **P0 Blockers:** 3-5 hours (payment + timezone)
- **P1 Experience:** 4-6 hours (export, email, onboarding)  
- **P2 Polish:** 1-2 hours (UI integration, standards)
- **Total:** 7-11 hours to complete all 12 MVP partials

### Risk Mitigation
- Payment implementation is low-risk (infrastructure exists)
- Timezone selection affects data accuracy (medium impact)
- Other items are user experience improvements (low risk)

**Recommendation:** Focus on P0 items first, P1 can be post-launch improvements if needed.