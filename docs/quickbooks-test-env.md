# 🧪 QuickBooks Test Environment Setup

## 📋 Test Environment Variables

Create a `.env.local` file in the CORA root directory with these variables:

```env
# QuickBooks OAuth Configuration (Replace with actual values from QuickBooks Developer Portal)
QUICKBOOKS_CLIENT_ID=ABcDefGHijKLmnOPqrsTUVwxyz1234567890
QUICKBOOKS_CLIENT_SECRET=your_client_secret_here
QUICKBOOKS_BASIC_AUTH=QUJjRGVmR0hpakpMbm5PUHFyc1RVVnd4eXoxMjM0NTY3ODkwOnlvdXJfY2xpZW50X3NlY3JldF9oZXJl

# QuickBooks API URLs (Sandbox for testing)
QUICKBOOKS_AUTH_URL=https://appcenter.intuit.com/connect/oauth2
QUICKBOOKS_TOKEN_URL=https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer
QUICKBOOKS_API_URL=https://sandbox-quickbooks.api.intuit.com/v3/company
QUICKBOOKS_USERINFO_URL=https://sandbox-accounts.platform.intuit.com/v1/openid_connect/userinfo

# Redirect URI (Update with your local domain for testing)
QUICKBOOKS_REDIRECT_URI=http://localhost:8000/api/integrations/quickbooks/callback

# Other required environment variables
SECRET_KEY=test-secret-key-for-local-development
ENVIRONMENT=development
DATABASE_URL=sqlite:///./cora.db
```

## 🔧 Setup Instructions

### 1. Get QuickBooks Credentials
1. Follow the QuickBooks App Registration Guide
2. Create a sandbox app for testing
3. Copy the Client ID and Client Secret

### 2. Generate Basic Auth Header
```bash
# Replace with your actual credentials
echo -n "YOUR_CLIENT_ID:YOUR_CLIENT_SECRET" | base64
```

### 3. Update Environment File
1. Copy the template above to `.env.local`
2. Replace placeholder values with your actual credentials
3. Update redirect URI to match your local setup

### 4. Test OAuth Flow
```bash
# Load environment variables
source .env.local

# Start CORA server
python app.py

# Test auth endpoint
curl http://localhost:8000/api/integrations/quickbooks/auth
```

## 🚨 Important Notes

- **Never commit `.env.local` to git**
- **Use sandbox environment for testing**
- **Update redirect URI in QuickBooks app settings**
- **Test with real QuickBooks sandbox company**

## 📊 Test Checklist

- [ ] Environment variables loaded
- [ ] QuickBooks app configured
- [ ] Redirect URI matches
- [ ] OAuth flow works
- [ ] Token refresh works
- [ ] API calls succeed
- [ ] Error handling works 