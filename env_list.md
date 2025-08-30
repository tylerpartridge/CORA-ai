# Required Environment Variables for Stripe Payment Integration

## Primary Payment Method (Stripe Payment Links)
```bash
# Optional: Direct Payment Link URL (recommended for simplicity)
PAYMENT_LINK_URL="https://buy.stripe.com/your-payment-link-id"
```

## Fallback Payment Method (Stripe Checkout Sessions)
```bash
# Required for Checkout Session creation
STRIPE_SECRET_KEY="sk_test_..." # or sk_live_... for production
STRIPE_PUBLIC_KEY="pk_test_..." # or pk_live_... for production

# Optional: Specific price ID for Checkout Sessions
STRIPE_PRICE_ID="price_1234567890abcdef"
```

## Payment Configuration
```bash
# Payment mode: "payment" for one-time, "subscription" for recurring
STRIPE_MODE="payment"  # Default: "payment"

# Success/Cancel redirect URLs (optional, defaults to /subscription)
STRIPE_SUCCESS_URL="https://yourdomain.com/subscription?status=success&session_id={CHECKOUT_SESSION_ID}"
STRIPE_CANCEL_URL="https://yourdomain.com/subscription?status=cancel"
```

## Environment Variable Descriptions

### PAYMENT_LINK_URL
- **Purpose**: Direct Stripe Payment Link for immediate checkout
- **Required**: No (but recommended for simplicity)
- **Example**: `https://buy.stripe.com/test_abc123def456`
- **Notes**: If provided, this will be the primary payment method. Users click and go directly to Stripe's hosted checkout.

### STRIPE_SECRET_KEY
- **Purpose**: Server-side Stripe API authentication
- **Required**: Yes (for Checkout Session fallback)
- **Format**: `sk_test_...` (test) or `sk_live_...` (production)
- **Security**: Never expose in frontend code

### STRIPE_PUBLIC_KEY
- **Purpose**: Client-side Stripe.js initialization
- **Required**: No (only needed for advanced Stripe.js features)
- **Format**: `pk_test_...` (test) or `pk_live_...` (production)
- **Notes**: Safe to expose in frontend code

### STRIPE_PRICE_ID
- **Purpose**: Specific price/product for Checkout Sessions
- **Required**: No (can be hardcoded in route)
- **Format**: `price_1234567890abcdef`
- **Notes**: Links to your Stripe product/price configuration

### STRIPE_MODE
- **Purpose**: Payment type configuration
- **Required**: No (defaults to "payment")
- **Options**: 
  - `"payment"` - One-time payment
  - `"subscription"` - Recurring subscription
- **Default**: `"payment"`

### STRIPE_SUCCESS_URL / STRIPE_CANCEL_URL
- **Purpose**: Post-payment redirect destinations
- **Required**: No (defaults to `/subscription` with status params)
- **Notes**: Must be absolute URLs for Stripe Checkout Sessions

## Validation Requirements
The application will validate:
1. At least one payment method is configured (PAYMENT_LINK_URL OR STRIPE_SECRET_KEY)
2. STRIPE_SECRET_KEY format is valid if provided
3. STRIPE_MODE is either "payment" or "subscription"
4. URLs are properly formatted if provided

## Development vs Production
- **Development**: Use `sk_test_` and `pk_test_` keys
- **Production**: Use `sk_live_` and `pk_live_` keys
- **Payment Links**: Create separate links for test/live modes in Stripe Dashboard
