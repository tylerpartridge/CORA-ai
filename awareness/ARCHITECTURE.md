# CORA Technical Architecture
*Compressed technical reference - STABLE*

## DIRECTORY MAP
```
/CORA/
├── app.py                 # FastAPI main
├── routes/               # API endpoints
│   ├── auth_coordinator.py
│   ├── expense_routes.py
│   └── payment_coordinator.py
├── models/               # SQLAlchemy
│   ├── user.py
│   ├── expense.py
│   └── __init__.py
├── web/                  # Frontend
│   ├── templates/       # Jinja2
│   └── static/         # CSS/JS
├── tools/               # Utilities
│   ├── backup_cora.sh
│   └── cora.sh
└── awareness/          # AI context
```

## API STRUCTURE
```
/api/
├── /auth/
│   ├── POST /login      {email, password, remember_me}
│   ├── POST /signup     {email, password, name}
│   └── POST /logout
├── /expenses/
│   ├── GET /            List user expenses
│   ├── POST /           Create expense
│   ├── PUT /{id}        Update expense
│   └── DELETE /{id}
├── /payments/
│   └── POST /webhook    Stripe events
└── /dashboard/
    └── GET /stats       Analytics
```

## DATABASE SCHEMA
```sql
users: id, email, password_hash, created_at
expenses: id, user_id, amount, description, category_id
categories: id, name, icon
payments: id, user_email, stripe_payment_id, amount
subscriptions: id, user_email, stripe_sub_id, status
```

## KEY PATTERNS
- **Auth**: JWT tokens in httpOnly cookies
- **Validation**: Pydantic models
- **Database**: SQLAlchemy ORM
- **Templates**: Jinja2 with construction theme
- **Errors**: Try/except with logging
- **Testing**: pytest with fixtures

## INTEGRATIONS
- **Stripe**: Payment processing (sk_live_...)
- **Plaid**: Bank connections (ready)
- **QuickBooks**: Accounting sync (ready)
- **SendGrid**: Email service (configured)
- **DigitalOcean**: Hosting + Spaces

## ENVIRONMENT
```bash
PORT=8000
DATABASE_URL=sqlite:///cora.db
STRIPE_API_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...
JWT_SECRET_KEY=[generated]
```

## DEPLOY COMMANDS
```bash
ssh root@coraai.tech
cd /root/cora
git pull origin main
pm2 restart cora
```

---
*Reference only - see code for implementation*