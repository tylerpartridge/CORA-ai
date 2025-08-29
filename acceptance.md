# Acceptance Criteria: Pricing Page + Payment CTA Implementation

## ✅ Navigation Integration
- [ ] "Upgrade" or "Pay" CTA visible in authenticated navigation
- [ ] CTA styled consistently with existing construction theme
- [ ] CTA positioned logically in navigation flow (after Integrations)
- [ ] CTA links to pricing page (`/pricing`)
- [ ] CTA not visible for unauthenticated users (optional requirement)

## ✅ Pricing Page Enhancement
- [ ] Existing pricing page loads without errors
- [ ] "Continue to Payment" buttons added to pricing tiers/cards
- [ ] Payment buttons styled with construction theme (orange/blue)
- [ ] Payment buttons trigger correct payment flow
- [ ] Page maintains responsive design on mobile/tablet
- [ ] Page loads within 2 seconds on average connection

## ✅ Payment Flow - Primary (Stripe Payment Links)
- [ ] If `PAYMENT_LINK_URL` is configured, use as primary method
- [ ] Payment button redirects to Stripe Payment Link
- [ ] Payment Link opens in same tab (not popup)
- [ ] Payment Link configured for correct product/price
- [ ] Payment Link success redirects to `/subscription?status=success`
- [ ] Payment Link cancel redirects to `/subscription?status=cancel`

## ✅ Payment Flow - Fallback (Checkout Sessions)
- [ ] If Payment Link unavailable, create Checkout Session
- [ ] `POST /api/checkout` endpoint responds within 3 seconds
- [ ] Checkout Session includes correct line items
- [ ] Checkout Session respects `STRIPE_MODE` configuration
- [ ] Checkout Session redirects properly on success/cancel
- [ ] API returns proper error messages for invalid requests

## ✅ Success/Cancel Pages
- [ ] `/subscription?status=success` shows success message
- [ ] `/subscription?status=cancel` shows cancellation message  
- [ ] Success page includes next steps or account access info
- [ ] Cancel page includes retry option or contact information
- [ ] Both pages maintain site navigation and branding
- [ ] Session ID displayed on success page (if available)

## ✅ Environment Configuration
- [ ] Application validates required environment variables on startup
- [ ] Clear error messages for missing/invalid configuration
- [ ] `PAYMENT_LINK_URL` takes precedence over Checkout Sessions
- [ ] `STRIPE_MODE` defaults to "payment" if not specified
- [ ] Sensitive keys (STRIPE_SECRET_KEY) not logged or exposed

## ✅ Error Handling
- [ ] Payment failures show user-friendly error messages
- [ ] Network timeouts handled gracefully (10 second timeout)
- [ ] Invalid Stripe configuration shows admin-friendly errors
- [ ] Payment processing errors logged for debugging
- [ ] Users can retry failed payments without losing context

## ✅ Security Requirements
- [ ] STRIPE_SECRET_KEY never sent to frontend
- [ ] Payment endpoints require authentication (if applicable)
- [ ] CSRF protection enabled for payment forms
- [ ] HTTPS enforced for payment pages in production
- [ ] No sensitive payment data stored in application database

## ✅ Testing Coverage
- [ ] Unit tests for checkout API endpoint (happy path)
- [ ] Unit tests for checkout API endpoint (error cases)
- [ ] Integration tests for payment flow end-to-end
- [ ] Mock Stripe API responses in test environment
- [ ] Tests verify success/cancel redirect handling
- [ ] Tests cover environment variable validation

## ✅ Performance Requirements
- [ ] Pricing page loads in < 2 seconds
- [ ] Payment API responds in < 3 seconds
- [ ] No memory leaks in payment flow
- [ ] Payment buttons responsive to user clicks (< 500ms feedback)
- [ ] Images and assets optimized for payment pages

## ✅ User Experience
- [ ] Payment flow intuitive for non-technical users
- [ ] Clear pricing information before payment
- [ ] Payment status clearly communicated at each step
- [ ] Mobile-friendly payment experience
- [ ] Consistent branding throughout payment flow
- [ ] Accessible to users with disabilities (WCAG 2.1 AA)

## ✅ Documentation
- [ ] Environment variables documented with examples
- [ ] Payment flow documented for future developers
- [ ] Stripe webhook setup documented (if applicable)
- [ ] Troubleshooting guide for common payment issues
- [ ] API endpoints documented with request/response examples

## Definition of Done
All checklist items must be completed and verified through:
1. Manual testing in development environment
2. Automated test suite passing
3. Code review by team member
4. Stripe test mode validation
5. Performance testing under load
6. Accessibility audit with screen reader
7. Cross-browser testing (Chrome, Firefox, Safari, Edge)
8. Mobile device testing (iOS Safari, Android Chrome)
