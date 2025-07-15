# Plaid Bank Integration Setup Guide

## 🚀 Overview
This guide walks you through setting up Plaid for bank account integration in CORA.

## 📋 Prerequisites
- Plaid developer account
- Python 3.8+
- PostgreSQL database
- HTTPS endpoint for webhooks (production)

## 🔧 Step 1: Create Plaid Account
1. Go to https://dashboard.plaid.com/signup
2. Sign up for a developer account
3. Verify your email address
4. Complete onboarding questionnaire

## 🎯 Step 2: Get API Credentials
1. Log in to Plaid Dashboard
2. Navigate to "Team Settings" → "Keys"
3. Copy your credentials:
   - **Client ID**: Your unique identifier
   - **Sandbox Secret**: For development/testing
   - **Development Secret**: For development environment (optional)
   - **Production Secret**: For live environment (requires approval)

## 🔐 Step 3: Environment Configuration
Create or update your `.env` file:

```env
# Plaid Configuration
PLAID_CLIENT_ID=your_client_id_here
PLAID_SECRET=your_sandbox_secret_here
PLAID_ENV=sandbox  # sandbox, development, or production
PLAID_PRODUCTS=transactions  # comma-separated: transactions,accounts,identity
PLAID_COUNTRY_CODES=US  # comma-separated: US,CA,GB,etc
PLAID_WEBHOOK_URL=https://your-app.com/api/plaid/webhook

# Security
PLAID_ENCRYPTION_KEY=your_32_byte_encryption_key_here
# Generate with: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# Optional Configuration
PLAID_REDIRECT_URI=https://your-app.com/oauth-return  # For OAuth institutions
PLAID_ANDROID_PACKAGE_NAME=com.yourcompany.cora  # For mobile app
PLAID_LOGO_URL=https://your-app.com/logo.png  # Custom logo in Link
```

## 🛠️ Step 4: Install Dependencies
```bash
# Install Plaid Python SDK
pip install plaid-python

# Install additional dependencies
pip install cryptography  # For token encryption
pip install python-dotenv  # For environment variables
```

## 🏗️ Step 5: Database Setup
Run the migration to create Plaid tables:

```sql
-- Create Plaid integration tables
CREATE TABLE plaid_integrations (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    item_id VARCHAR(255) UNIQUE NOT NULL,
    access_token TEXT NOT NULL,
    institution_name VARCHAR(255),
    institution_id VARCHAR(255),
    accounts_data JSONB,
    cursor TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    last_sync_at TIMESTAMP,
    last_sync_error TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE plaid_accounts (
    id SERIAL PRIMARY KEY,
    integration_id INTEGER REFERENCES plaid_integrations(id),
    account_id VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255),
    official_name VARCHAR(255),
    type VARCHAR(50),
    subtype VARCHAR(50),
    mask VARCHAR(10),
    current_balance DECIMAL(10, 2),
    available_balance DECIMAL(10, 2),
    currency_code VARCHAR(3) DEFAULT 'USD',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE plaid_transactions (
    id SERIAL PRIMARY KEY,
    account_id INTEGER REFERENCES plaid_accounts(id),
    transaction_id VARCHAR(255) UNIQUE NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    date DATE NOT NULL,
    name TEXT,
    merchant_name VARCHAR(255),
    category_id VARCHAR(50),
    category JSONB,
    location JSONB,
    payment_channel VARCHAR(50),
    pending BOOLEAN DEFAULT FALSE,
    expense_id INTEGER REFERENCES expenses(id),
    sync_status VARCHAR(50) DEFAULT 'synced',
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE plaid_sync_history (
    id SERIAL PRIMARY KEY,
    integration_id INTEGER REFERENCES plaid_integrations(id),
    sync_type VARCHAR(50),
    transactions_added INTEGER DEFAULT 0,
    transactions_modified INTEGER DEFAULT 0,
    transactions_removed INTEGER DEFAULT 0,
    sync_duration INTEGER,
    success BOOLEAN,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX idx_plaid_integrations_user_id ON plaid_integrations(user_id);
CREATE INDEX idx_plaid_accounts_integration_id ON plaid_accounts(integration_id);
CREATE INDEX idx_plaid_transactions_account_id ON plaid_transactions(account_id);
CREATE INDEX idx_plaid_transactions_date ON plaid_transactions(date);
CREATE INDEX idx_plaid_sync_history_integration_id ON plaid_sync_history(integration_id);
```

## 🧪 Step 6: Test Your Integration

### Sandbox Testing
1. Use test credentials:
   ```
   username: user_good
   password: pass_good
   ```
2. Select "First Platypus Bank" in Link
3. Transactions will be automatically generated

### Test Script
```python
from plaid import Client

# Initialize client
client = Client(
    client_id=PLAID_CLIENT_ID,
    secret=PLAID_SECRET,
    environment='sandbox'
)

# Create Link token
response = client.link_token_create({
    'user': {'client_user_id': 'test_user'},
    'client_name': 'CORA Test',
    'products': ['transactions'],
    'country_codes': ['US'],
    'language': 'en'
})

print(f"Link Token: {response['link_token']}")
```

## 🪝 Step 7: Configure Webhooks

### Development (ngrok)
```bash
# Install ngrok
npm install -g ngrok

# Start your local server
python app.py

# In another terminal, expose your webhook endpoint
ngrok http 8000

# Use the HTTPS URL for PLAID_WEBHOOK_URL
# Example: https://abc123.ngrok.io/api/plaid/webhook
```

### Production
1. Ensure your webhook endpoint is HTTPS
2. Set up webhook URL in environment variables
3. Implement webhook signature verification
4. Monitor webhook delivery in Plaid Dashboard

## 🔄 Step 8: Implement Link Flow

### Frontend Integration
```html
<!-- Include Plaid Link -->
<script src="https://cdn.plaid.com/link/v2/stable/link-initialize.js"></script>

<!-- Link Button -->
<button id="link-account-button">Connect Bank Account</button>

<script>
// Create Link token first (call your backend)
fetch('/api/plaid/create_link_token', {
    method: 'POST',
    headers: {
        'Authorization': 'Bearer ' + userToken
    }
})
.then(response => response.json())
.then(data => {
    // Initialize Link
    const handler = Plaid.create({
        token: data.link_token,
        onSuccess: (public_token, metadata) => {
            // Send public token to your backend
            fetch('/api/plaid/exchange_public_token', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': 'Bearer ' + userToken
                },
                body: JSON.stringify({
                    public_token: public_token,
                    metadata: metadata
                })
            });
        },
        onExit: (err, metadata) => {
            // Handle exit
            console.log('User exited Link', err, metadata);
        },
        onEvent: (eventName, metadata) => {
            // Track events
            console.log('Link event:', eventName, metadata);
        }
    });

    // Open Link
    document.getElementById('link-account-button').onclick = () => {
        handler.open();
    };
});
</script>
```

## 📊 Step 9: Monitor Your Integration

### Plaid Dashboard Monitoring
1. **API Calls**: Monitor usage and errors
2. **Items**: View connected accounts
3. **Webhooks**: Check delivery status
4. **Logs**: Debug API calls

### Application Monitoring
```python
# Health check endpoint
@app.route('/api/plaid/health', methods=['GET'])
def plaid_health():
    try:
        # Test API connection
        client.categories_get()
        
        # Check active connections
        active_count = PlaidIntegration.query.filter_by(is_active=True).count()
        
        # Check recent errors
        recent_errors = PlaidIntegration.query.filter(
            PlaidIntegration.last_sync_error.isnot(None),
            PlaidIntegration.updated_at > datetime.now() - timedelta(hours=1)
        ).count()
        
        return {
            'status': 'healthy',
            'active_connections': active_count,
            'recent_errors': recent_errors
        }
    except Exception as e:
        return {'status': 'unhealthy', 'error': str(e)}, 500
```

## 🚨 Common Issues & Solutions

### Issue: "INVALID_API_KEYS"
**Solution**: Verify your Client ID and Secret match the environment

### Issue: "PRODUCT_NOT_READY"
**Solution**: Wait a moment and retry - initial sync may take time

### Issue: "ITEM_LOGIN_REQUIRED"
**Solution**: User needs to re-authenticate through Link

### Issue: Rate Limiting
**Solution**: Implement exponential backoff and respect rate limits

### Issue: Webhook Delivery Failures
**Solution**: 
- Ensure endpoint returns 200 status
- Implement idempotency
- Log all webhook receipts
- Set up webhook retry logic

## 🔒 Security Best Practices

1. **Encrypt Access Tokens**
   ```python
   from cryptography.fernet import Fernet
   
   def encrypt_token(token: str) -> str:
       cipher = Fernet(ENCRYPTION_KEY)
       return cipher.encrypt(token.encode()).decode()
   ```

2. **Verify Webhook Signatures**
   ```python
   import hmac
   import hashlib
   
   def verify_webhook(request):
       signature = request.headers.get('Plaid-Verification')
       body = request.get_data()
       
       computed = hmac.new(
           PLAID_WEBHOOK_SECRET.encode(),
           body,
           hashlib.sha256
       ).hexdigest()
       
       return hmac.compare_digest(signature, computed)
   ```

3. **Implement Proper Error Handling**
   - Never expose access tokens in logs
   - Sanitize error messages for users
   - Log full errors server-side only

4. **Regular Security Audits**
   - Review connected accounts monthly
   - Monitor for suspicious activity
   - Implement anomaly detection

## 📱 Mobile App Integration

If building a mobile app:
1. Use Link token flow (not public key)
2. Set Android package name in config
3. Configure iOS redirect URI
4. Handle app-to-app redirects

## 🚀 Go Live Checklist

### Development Complete
- [ ] Sandbox testing successful
- [ ] Error handling implemented
- [ ] Webhook processing tested
- [ ] Security measures in place

### Production Preparation
- [ ] Production API keys obtained
- [ ] SSL certificate configured
- [ ] Webhook URL accessible
- [ ] Rate limiting implemented
- [ ] Monitoring set up

### Compliance
- [ ] Privacy policy updated
- [ ] Terms of service updated
- [ ] User consent flow implemented
- [ ] Data retention policy defined

### Launch
- [ ] Switch to production environment
- [ ] Test with real bank account
- [ ] Monitor initial connections
- [ ] Gather user feedback

## 📚 Resources
- [Plaid Quickstart](https://plaid.com/docs/quickstart/)
- [API Reference](https://plaid.com/docs/api/)
- [Link Documentation](https://plaid.com/docs/link/)
- [Webhook Reference](https://plaid.com/docs/api/webhooks/)
- [Error Handling](https://plaid.com/docs/errors/)
- [Going Live](https://plaid.com/docs/link/production/)

## 🆘 Support
- Plaid Support: https://dashboard.plaid.com/support
- Community: https://plaid.com/community/
- Status Page: https://status.plaid.com/

---

**Note**: This guide covers the essential steps. For advanced features like Identity verification, Asset reports, or Payment Initiation, refer to Plaid's specific product documentation.