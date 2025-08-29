# Pricing Page + Payment CTA Implementation Plan

## Stack Analysis
- **Server**: FastAPI (Python 3.12+) with Jinja2 templates
- **Frontend**: Bootstrap 5 + vanilla JS, template-based rendering
- **Payment**: Stripe integration already exists in `routes/stripe_integration.py`
- **Templates**: Located in `web/templates/` with component system

## Implementation Steps

### 1. Navigation CTA Addition
**File**: `C:\CORA\web\templates\components\navigation.html`
- Add "Upgrade" or "Pay" button to authenticated navigation (line ~50)
- Insert after "Integrations" dropdown item
- Style with existing `.btn-primary` construction theme

### 2. Pricing Page Enhancement  
**File**: `C:\CORA\web\templates\pricing.html`
- Locate existing pricing cards/sections
- Add "Continue to Payment" CTA buttons
- Wire to Stripe Payment Link (primary) with fallback to Checkout Session
- Implement JavaScript handler for payment method selection

### 3. API Route Extension
**File**: `C:\CORA\routes\stripe_integration.py`
- Add new endpoint: `POST /api/checkout`
- Implement Stripe Checkout Session creation as fallback
- Handle success/cancel redirects to `/subscription?status=success|cancel`
- Integrate with existing StripeService class

### 4. Success/Cancel Page Updates
**File**: `C:\CORA\web\templates\subscription.html`
- Enhance existing subscription template
- Add status-based messaging for success/cancel scenarios
- Handle query parameters: `?status=success&session_id=xyz`
- Add appropriate CTAs for each status

### 5. Environment Configuration
**File**: `C:\CORA\app.py`
- Ensure Stripe environment variables are loaded
- Add validation for required payment configuration
- Wire new checkout route to main app router

### 6. Testing Implementation
**File**: `C:\CORA\tests\test_stripe_payment.py` (new)
- Unit tests for checkout API endpoint
- Integration tests for payment flow
- Mock Stripe API responses
- Test success/cancel redirect handling

## Route Integration
New route will be automatically included via existing:
```python
app.include_router(stripe_router)  # Line ~303 in app.py
```

## Template Inheritance
- Pricing page extends `base_public.html`
- Navigation component included via template inheritance
- Subscription page uses existing template structure

## JavaScript Requirements
- Payment method selection logic
- Stripe Payment Link redirection
- Checkout Session fallback handling
- Success/error state management
