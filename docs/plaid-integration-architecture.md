# Plaid Bank Integration Architecture

## 🏗️ Overview
This document outlines the architecture for integrating Plaid bank connections into CORA, completing our Phase 2 integration milestone.

## 🎯 Integration Goals
- Connect to 15,000+ financial institutions
- Sync transactions automatically with 90%+ categorization accuracy
- Provide real-time expense tracking from bank accounts
- Support both OAuth and username/password institutions
- Scale to 1,000+ users efficiently

## 📊 Data Flow Architecture

```
User → CORA Web UI → Plaid Link → Bank
         ↓               ↓          ↓
    Link Token      Public Token   Auth
         ↓               ↓          ↓
    CORA Backend → Access Token → Plaid API
         ↓               ↓          ↓
    Store Token     Fetch Txns   Categorize
         ↓               ↓          ↓
    PostgreSQL    Process/Map   AI Engine
         ↓               ↓          ↓
    Expense DB    Sync Status   Analytics
```

## 🗄️ Database Schema

### plaid_integrations
```sql
CREATE TABLE plaid_integrations (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    item_id VARCHAR(255) UNIQUE NOT NULL,
    access_token TEXT NOT NULL,  -- Encrypted
    institution_name VARCHAR(255),
    institution_id VARCHAR(255),
    accounts_data JSONB,  -- Account metadata
    cursor TEXT,  -- For transaction sync
    is_active BOOLEAN DEFAULT TRUE,
    last_sync_at TIMESTAMP,
    last_sync_error TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### plaid_accounts
```sql
CREATE TABLE plaid_accounts (
    id SERIAL PRIMARY KEY,
    integration_id INTEGER REFERENCES plaid_integrations(id),
    account_id VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255),
    official_name VARCHAR(255),
    type VARCHAR(50),  -- 'depository', 'credit', 'loan', etc.
    subtype VARCHAR(50),  -- 'checking', 'savings', 'credit card', etc.
    mask VARCHAR(10),  -- Last 4 digits
    current_balance DECIMAL(10, 2),
    available_balance DECIMAL(10, 2),
    currency_code VARCHAR(3) DEFAULT 'USD',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### plaid_transactions
```sql
CREATE TABLE plaid_transactions (
    id SERIAL PRIMARY KEY,
    account_id INTEGER REFERENCES plaid_accounts(id),
    transaction_id VARCHAR(255) UNIQUE NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    date DATE NOT NULL,
    name TEXT,
    merchant_name VARCHAR(255),
    category_id VARCHAR(50),
    category JSONB,  -- Full category hierarchy
    location JSONB,  -- Location data
    payment_channel VARCHAR(50),
    pending BOOLEAN DEFAULT FALSE,
    expense_id INTEGER REFERENCES expenses(id),  -- Linked CORA expense
    sync_status VARCHAR(50) DEFAULT 'synced',
    created_at TIMESTAMP DEFAULT NOW()
);
```

### plaid_sync_history
```sql
CREATE TABLE plaid_sync_history (
    id SERIAL PRIMARY KEY,
    integration_id INTEGER REFERENCES plaid_integrations(id),
    sync_type VARCHAR(50),  -- 'initial', 'historical', 'update'
    transactions_added INTEGER DEFAULT 0,
    transactions_modified INTEGER DEFAULT 0,
    transactions_removed INTEGER DEFAULT 0,
    sync_duration INTEGER,  -- milliseconds
    success BOOLEAN,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

## 🔐 Security Architecture

### Token Storage
```python
# Encrypt access tokens before storage
from cryptography.fernet import Fernet

def encrypt_token(token: str) -> str:
    cipher = Fernet(ENCRYPTION_KEY)
    return cipher.encrypt(token.encode()).decode()

def decrypt_token(encrypted_token: str) -> str:
    cipher = Fernet(ENCRYPTION_KEY)
    return cipher.decrypt(encrypted_token.encode()).decode()
```

### Environment Variables
```env
# Plaid Configuration
PLAID_CLIENT_ID=your_client_id
PLAID_SECRET=your_secret_key
PLAID_ENV=sandbox  # or development, production
PLAID_WEBHOOK_URL=https://your-app.com/api/plaid/webhook
PLAID_WEBHOOK_SECRET=your_webhook_secret

# Security
PLAID_ENCRYPTION_KEY=your_32_byte_encryption_key
```

## 🔄 Integration Flow

### 1. Link Token Creation
```python
@router.post("/api/plaid/create_link_token")
async def create_link_token(current_user: User):
    link_token = plaid_client.link_token_create({
        'user': {'client_user_id': str(current_user.id)},
        'client_name': 'CORA Expense Tracker',
        'products': ['transactions'],
        'country_codes': ['US'],
        'language': 'en',
        'webhook': PLAID_WEBHOOK_URL
    })
    return {"link_token": link_token['link_token']}
```

### 2. Public Token Exchange
```python
@router.post("/api/plaid/exchange_public_token")
async def exchange_public_token(public_token: str, metadata: dict):
    # Exchange for access token
    exchange_response = plaid_client.item_public_token_exchange(public_token)
    access_token = exchange_response['access_token']
    item_id = exchange_response['item_id']
    
    # Store encrypted token
    integration = PlaidIntegration(
        user_id=current_user.id,
        item_id=item_id,
        access_token=encrypt_token(access_token),
        institution_name=metadata['institution']['name']
    )
    db.add(integration)
    
    # Fetch accounts
    await sync_accounts(integration)
    
    # Start initial transaction sync
    await sync_transactions(integration, initial=True)
```

### 3. Transaction Sync
```python
async def sync_transactions(integration: PlaidIntegration, cursor: str = None):
    access_token = decrypt_token(integration.access_token)
    
    # Use transactions_sync for efficient updates
    has_more = True
    added = modified = removed = 0
    
    while has_more:
        response = plaid_client.transactions_sync(
            access_token=access_token,
            cursor=cursor or integration.cursor
        )
        
        # Process transactions
        for txn in response['added']:
            await process_transaction(txn, 'added')
            added += 1
            
        for txn in response['modified']:
            await process_transaction(txn, 'modified')
            modified += 1
            
        for txn in response['removed']:
            await process_transaction(txn, 'removed')
            removed += 1
        
        # Update cursor
        cursor = response['next_cursor']
        has_more = response['has_more']
    
    # Update integration
    integration.cursor = cursor
    integration.last_sync_at = datetime.utcnow()
    
    # Log sync history
    await log_sync_history(integration, added, modified, removed)
```

### 4. Transaction Processing
```python
async def process_transaction(plaid_txn: dict, action: str):
    if action == 'removed':
        # Remove or mark as deleted
        db_txn = get_transaction_by_id(plaid_txn['transaction_id'])
        if db_txn:
            db_txn.sync_status = 'removed'
        return
    
    # Create or update transaction
    txn = PlaidTransaction(
        transaction_id=plaid_txn['transaction_id'],
        account_id=plaid_txn['account_id'],
        amount=plaid_txn['amount'],
        date=plaid_txn['date'],
        name=plaid_txn['name'],
        merchant_name=plaid_txn.get('merchant_name'),
        category_id=plaid_txn.get('category_id'),
        category=plaid_txn.get('category'),
        location=plaid_txn.get('location'),
        payment_channel=plaid_txn.get('payment_channel'),
        pending=plaid_txn.get('pending', False)
    )
    
    # Create corresponding CORA expense
    if not txn.pending:
        expense = await create_expense_from_transaction(txn)
        txn.expense_id = expense.id
    
    db.merge(txn)  # Upsert
```

## 🪝 Webhook Architecture

### Webhook Handler
```python
@router.post("/api/plaid/webhook")
async def plaid_webhook(request: Request):
    # Verify webhook
    if not verify_webhook_signature(request):
        raise HTTPException(401)
    
    webhook_type = request.json['webhook_type']
    item_id = request.json['item_id']
    
    # Get integration
    integration = get_integration_by_item_id(item_id)
    
    # Handle webhook types
    if webhook_type == 'SYNC_UPDATES_AVAILABLE':
        await sync_transactions(integration)
        
    elif webhook_type == 'INITIAL_UPDATE':
        # Initial 30 days complete
        await notify_user_initial_sync_complete(integration)
        
    elif webhook_type == 'HISTORICAL_UPDATE':
        # All historical data synced
        await notify_user_historical_sync_complete(integration)
        
    elif webhook_type == 'TRANSACTIONS_REMOVED':
        # Handle removed pending transactions
        await handle_removed_transactions(request.json['removed_transactions'])
        
    elif webhook_type == 'WEBHOOK_UPDATE_ACKNOWLEDGED':
        # Webhook verified
        pass
        
    elif webhook_type == 'ERROR':
        # Handle errors
        await handle_plaid_error(integration, request.json['error'])
```

## 🎨 UI Components

### Bank Connection Flow
```html
<!-- Link Initialization -->
<button id="link-bank-account">Connect Bank Account</button>

<script>
const handler = Plaid.create({
    token: linkToken,
    onSuccess: (public_token, metadata) => {
        // Send to backend
        fetch('/api/plaid/exchange_public_token', {
            method: 'POST',
            body: JSON.stringify({ public_token, metadata })
        });
    },
    onExit: (err, metadata) => {
        // Handle exit
    },
    onEvent: (eventName, metadata) => {
        // Track events
    }
});

document.getElementById('link-bank-account').onclick = () => {
    handler.open();
};
</script>
```

### Account Management UI
```javascript
// Display connected accounts
function displayAccounts(accounts) {
    return accounts.map(account => `
        <div class="account-card">
            <h3>${account.name}</h3>
            <p>${account.institution_name}</p>
            <p>****${account.mask}</p>
            <p>Balance: $${account.current_balance}</p>
            <button onclick="syncAccount(${account.id})">Sync Now</button>
            <button onclick="disconnectAccount(${account.id})">Disconnect</button>
        </div>
    `).join('');
}
```

## 🔄 Sync Strategy

### Initial Sync
1. Exchange public token for access token
2. Fetch and store account information
3. Sync last 30 days of transactions
4. Queue historical sync job

### Historical Sync
1. After initial sync completes
2. Fetch remaining transactions (up to 24 months)
3. Process in batches to avoid timeouts
4. Update UI with progress

### Ongoing Sync
1. Listen for webhooks
2. Use cursor-based sync for efficiency
3. Handle additions, modifications, and removals
4. Update CORA expenses accordingly

### Manual Refresh
1. User-triggered sync
2. Call transactions_refresh endpoint
3. Force webhook trigger
4. Update last sync timestamp

## 📈 Performance Optimization

### Batch Processing
```python
async def batch_process_transactions(transactions: List[dict], batch_size: int = 100):
    for i in range(0, len(transactions), batch_size):
        batch = transactions[i:i + batch_size]
        await asyncio.gather(*[
            process_transaction(txn, 'added') 
            for txn in batch
        ])
        await asyncio.sleep(0.1)  # Rate limiting
```

### Caching Strategy
```python
# Cache institution data
@lru_cache(maxsize=1000)
def get_institution_info(institution_id: str):
    return plaid_client.institutions_get_by_id(institution_id)

# Cache category mappings
CATEGORY_CACHE = {}
def map_plaid_to_cora_category(plaid_category: list):
    cache_key = tuple(plaid_category)
    if cache_key not in CATEGORY_CACHE:
        CATEGORY_CACHE[cache_key] = calculate_mapping(plaid_category)
    return CATEGORY_CACHE[cache_key]
```

## 🧪 Testing Strategy

### Sandbox Testing
```python
# Test credentials for sandbox
TEST_CREDENTIALS = {
    'username': 'user_good',
    'password': 'pass_good'
}

# Simulate transactions
def simulate_sandbox_transactions():
    # Sandbox automatically generates transactions
    # Use fire_webhook to trigger updates
    plaid_client.sandbox_item_fire_webhook(
        access_token,
        webhook_code='SYNC_UPDATES_AVAILABLE'
    )
```

### Integration Tests
```python
@pytest.mark.asyncio
async def test_plaid_sync_flow():
    # Create link token
    link_token = await create_link_token(test_user)
    assert link_token is not None
    
    # Exchange public token
    integration = await exchange_public_token(
        'public-sandbox-xxx', 
        test_metadata
    )
    assert integration.access_token is not None
    
    # Sync transactions
    await sync_transactions(integration)
    
    # Verify expenses created
    expenses = get_user_expenses(test_user)
    assert len(expenses) > 0
```

## 🚨 Error Handling

### Common Errors
```python
ERROR_HANDLERS = {
    'ITEM_LOGIN_REQUIRED': handle_reauth_required,
    'INVALID_ACCESS_TOKEN': handle_token_invalid,
    'RATE_LIMIT_EXCEEDED': handle_rate_limit,
    'INSTITUTION_ERROR': handle_institution_error,
    'PRODUCT_NOT_READY': handle_product_not_ready
}

async def handle_plaid_error(error_code: str, integration: PlaidIntegration):
    handler = ERROR_HANDLERS.get(error_code, handle_generic_error)
    await handler(integration)
    
    # Log error
    integration.last_sync_error = error_code
    await notify_user_of_error(integration, error_code)
```

## 📊 Monitoring & Analytics

### Key Metrics
- Connection success rate
- Sync latency (webhook → expense created)
- Transaction categorization accuracy
- Error rates by institution
- API usage vs limits

### Health Checks
```python
async def plaid_health_check():
    metrics = {
        'active_connections': count_active_integrations(),
        'pending_syncs': count_pending_syncs(),
        'error_rate': calculate_error_rate(),
        'avg_sync_time': calculate_avg_sync_time(),
        'api_usage': get_api_usage_metrics()
    }
    return metrics
```

## 🎯 Success Criteria

1. **Connection Rate**: >90% success rate for bank connections
2. **Sync Performance**: <5 second average sync time
3. **Data Accuracy**: >95% transaction categorization accuracy
4. **Uptime**: 99.9% webhook processing uptime
5. **Scale**: Support 1,000+ concurrent users
6. **Security**: Zero security incidents
7. **User Satisfaction**: >4.5/5 rating for bank sync feature

This architecture provides CORA with a robust, scalable, and secure bank integration that completes our Phase 2 integration milestone!