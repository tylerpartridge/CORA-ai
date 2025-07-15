# 🔗 QuickBooks Integration Plan

## 🎯 Phase 1 Milestone: QuickBooks Integration

**Goal:** Enable CORA users to sync expenses with QuickBooks automatically
**Timeline:** 2-3 days (while waiting for deployment)
**Priority:** High - Last technical milestone for Phase 1

## 📊 QuickBooks API Research

### 1. QuickBooks Online API
**Endpoint:** https://developer.intuit.com/app/developer/qbo/docs/api/
**Authentication:** OAuth 2.0 with refresh tokens
**Rate Limits:** 100 requests per minute (sandbox), 500 requests per minute (production)

### 2. Required Scopes
```json
{
  "accounting": [
    "com.intuit.quickbooks.accounting",
    "com.intuit.quickbooks.payment"
  ],
  "expenses": [
    "com.intuit.quickbooks.accounting.transactions.read",
    "com.intuit.quickbooks.accounting.transactions.write"
  ]
}
```

### 3. Key Endpoints for CORA
- **POST /v3/company/{realmId}/purchase** - Create expense transactions
- **GET /v3/company/{realmId}/purchase** - Retrieve expenses
- **GET /v3/company/{realmId}/account** - Get chart of accounts
- **GET /v3/company/{realmId}/vendor** - Get vendor list

## 🔐 Authentication Flow

### OAuth 2.0 Implementation
```python
# 1. Authorization URL
auth_url = "https://appcenter.intuit.com/connect/oauth2"
params = {
    "client_id": QUICKBOOKS_CLIENT_ID,
    "response_type": "code",
    "scope": "com.intuit.quickbooks.accounting",
    "redirect_uri": "https://cora.ai/api/integrations/quickbooks/callback",
    "state": user_id  # CSRF protection
}

# 2. Exchange code for tokens
token_url = "https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer"
data = {
    "grant_type": "authorization_code",
    "code": auth_code,
    "redirect_uri": "https://cora.ai/api/integrations/quickbooks/callback"
}
```

### Token Storage
```python
class QuickBooksIntegration(Base):
    __tablename__ = "quickbooks_integrations"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    realm_id = Column(String(50))  # QuickBooks company ID
    access_token = Column(String(500))
    refresh_token = Column(String(500))
    token_expires_at = Column(DateTime)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

## 🔄 Sync Strategy

### 1. One-Way Sync (CORA → QuickBooks)
**Initial Approach:** Push CORA expenses to QuickBooks
- **Advantage:** CORA is the source of truth
- **Disadvantage:** No conflict resolution needed initially

### 2. Expense Mapping
```python
# CORA Expense → QuickBooks Purchase
cora_expense = {
    "amount": 45.67,
    "description": "Office supplies from Staples",
    "category": "Office Supplies",
    "vendor": "Staples",
    "date": "2025-01-15"
}

quickbooks_purchase = {
    "Line": [
        {
            "Amount": 45.67,
            "DetailType": "AccountBasedExpenseLineDetail",
            "AccountBasedExpenseLineDetail": {
                "AccountRef": {
                    "value": "7",  # Office Supplies account ID
                    "name": "Office Supplies"
                }
            }
        }
    ],
    "VendorRef": {
        "value": "123",  # Staples vendor ID
        "name": "Staples"
    },
    "TxnDate": "2025-01-15",
    "PrivateNote": "Office supplies from Staples"
}
```

### 3. Category Mapping
```python
CORA_TO_QUICKBOOKS_CATEGORIES = {
    "Office Supplies": "Office Supplies",
    "Meals & Entertainment": "Meals and Entertainment",
    "Transportation": "Automobile",
    "Software & Subscriptions": "Computer and Internet Expenses",
    "Marketing & Advertising": "Advertising and Promotion",
    "Shipping & Postage": "Shipping and Delivery",
    "Professional Development": "Professional Development",
    "Travel": "Travel",
    "Utilities": "Utilities",
    "Insurance": "Insurance"
}
```

## 🏗️ Implementation Plan

### Phase 1: Authentication & Setup (Day 1)
**Claude's Tasks:**
- [ ] Create QuickBooks integration model
- [ ] Implement OAuth 2.0 flow
- [ ] Add integration endpoints (`/api/integrations/quickbooks/*`)

**Cursor's Tasks:**
- [ ] Research QuickBooks API documentation
- [ ] Create integration setup UI
- [ ] Document authentication flow

### Phase 2: Core Sync (Day 2)
**Claude's Tasks:**
- [ ] Implement expense → purchase mapping
- [ ] Add sync endpoint (`/api/integrations/quickbooks/sync`)
- [ ] Handle token refresh logic

**Cursor's Tasks:**
- [ ] Create sync status dashboard
- [ ] Add error handling and retry logic
- [ ] Test with sample data

### Phase 3: Advanced Features (Day 3)
**Claude's Tasks:**
- [ ] Add vendor auto-creation
- [ ] Implement account mapping
- [ ] Add sync history tracking

**Cursor's Tasks:**
- [ ] Create integration settings page
- [ ] Add sync scheduling
- [ ] Performance optimization

## 📁 File Structure

```
integrations/
├── __init__.py
├── quickbooks/
│   ├── __init__.py
│   ├── auth.py          # OAuth 2.0 authentication
│   ├── client.py        # QuickBooks API client
│   ├── mapper.py        # Data mapping logic
│   ├── sync.py          # Sync orchestration
│   └── models.py        # Integration models
├── routes/
│   └── quickbooks.py    # API endpoints
└── templates/
    └── integrations/
        └── quickbooks.html  # Setup UI
```

## 🔧 Technical Requirements

### Dependencies
```python
# requirements.txt additions
requests-oauthlib==1.3.1
python-quickbooks==0.9.0  # Optional: official SDK
```

### Environment Variables
```env
QUICKBOOKS_CLIENT_ID=your_client_id
QUICKBOOKS_CLIENT_SECRET=your_client_secret
QUICKBOOKS_REDIRECT_URI=https://cora.ai/api/integrations/quickbooks/callback
QUICKBOOKS_ENVIRONMENT=sandbox  # or production
```

## 🧪 Testing Strategy

### 1. Sandbox Testing
- Use QuickBooks sandbox environment
- Create test company with sample data
- Test all CRUD operations

### 2. Integration Tests
```python
def test_quickbooks_expense_sync():
    # Test expense creation in QuickBooks
    # Test category mapping
    # Test vendor creation
    # Test error handling
```

### 3. Performance Testing
- Test with 100+ expenses
- Monitor API rate limits
- Test token refresh scenarios

## 🚨 Risk Mitigation

### 1. API Rate Limits
- Implement request throttling
- Add retry logic with exponential backoff
- Monitor usage and alert on limits

### 2. Token Expiration
- Automatic token refresh
- Graceful error handling
- User notification for re-authentication

### 3. Data Conflicts
- Use CORA as source of truth initially
- Add conflict resolution later
- Maintain sync history for audit

## 📈 Success Metrics

### Phase 1 Goals
- [ ] 100% of CORA expenses sync to QuickBooks
- [ ] <5 second sync time per expense
- [ ] 0% data loss during sync
- [ ] User satisfaction >90%

### Future Enhancements
- [ ] Two-way sync (QuickBooks → CORA)
- [ ] Real-time sync with webhooks
- [ ] Bulk import from QuickBooks
- [ ] Advanced conflict resolution

## 🎯 Next Steps

1. **Claude:** Start with authentication model and OAuth flow
2. **Cursor:** Research API documentation and create setup UI
3. **Both:** Test sandbox integration together
4. **Both:** Deploy and test with real QuickBooks accounts

**Status:** 🟢 READY - Plan complete, ready for implementation
**Next:** Begin Phase 1 - Authentication & Setup 