# Database Seeding and Introspection Runbook

## Overview
This runbook covers the idempotent admin user seeding and database introspection utilities for CORA production operations.

## Prerequisites
- Python 3.8+ with SQLAlchemy installed
- Access to the CORA database (SQLite or PostgreSQL)
- Environment variables configured for admin seeding

## Tools

### 1. seed_users.py - Idempotent Admin User Creation

#### Purpose
Creates an admin user if it doesn't exist. Safe to run multiple times.

#### Required Environment Variables
```bash
export ADMIN_EMAIL="admin@coraai.tech"           # Required: Admin email address
export ADMIN_PASSWORD="secure-password-here"     # Required: Admin password (min 8 chars)
export ADMIN_TIMEZONE="America/St_Johns"         # Optional: Default is America/St_Johns
```

#### Usage
```bash
# Basic usage
cd /var/www/cora
python3 tools/seed_users.py

# With environment variables inline
ADMIN_EMAIL="admin@coraai.tech" ADMIN_PASSWORD="SecurePass123!" python3 tools/seed_users.py
```

#### Expected Output

**First run (user created):**
```json
{
  "status": "created",
  "message": "Admin user admin@coraai.tech created successfully",
  "user_id": 1,
  "timezone": "America/St_Johns"
}
```

**Subsequent runs (user exists):**
```json
{
  "status": "exists",
  "message": "Admin user admin@coraai.tech already exists",
  "user_id": 1,
  "is_admin": "true"
}
```

**Error case:**
```json
{
  "status": "error",
  "message": "ADMIN_EMAIL environment variable is required"
}
```

#### Exit Codes
- `0`: Success (user created or already exists)
- `1`: Error (missing env vars, database error, etc.)

### 2. db_introspect.py - Database Introspection

#### Purpose
Read-only utility to inspect database state, counts, and integrity.

#### Usage
```bash
# Basic usage - human readable output
cd /var/www/cora
python3 tools/db_introspect.py

# JSON output for automation
python3 tools/db_introspect.py --json

# Show 5 most recent records per table
python3 tools/db_introspect.py --recent 5

# Combined: JSON with recent records
python3 tools/db_introspect.py --json --recent 3
```

#### Expected Output

**Human-readable format:**
```
=== Database Introspection ===

Table Counts:
  users: 15
  jobs: 234
  expenses: 1052
  expense_categories: 8
  customers: 47
  payments: 89
  subscriptions: 12

Integrity Checks:
  orphaned_expenses: 0
  users_without_timezone: 2
  admin_users: 1
```

**JSON format:**
```json
{
  "table_counts": {
    "users": 15,
    "jobs": 234,
    "expenses": 1052,
    "expense_categories": 8,
    "customers": 47,
    "payments": 89,
    "subscriptions": 12
  },
  "integrity_checks": {
    "orphaned_expenses": 0,
    "users_without_timezone": 2,
    "admin_users": 1
  }
}
```

#### Exit Codes
- `0`: Success
- `1`: Database error or connection failure

## Common Workflows

### Initial Admin Setup
```bash
# 1. Set secure credentials
export ADMIN_EMAIL="admin@coraai.tech"
export ADMIN_PASSWORD="$(openssl rand -base64 32)"
export ADMIN_TIMEZONE="America/St_Johns"

# 2. Create admin user
python3 tools/seed_users.py

# 3. Verify creation
python3 tools/db_introspect.py --json | jq '.integrity_checks.admin_users'
```

### Pre-Migration Health Check
```bash
# 1. Get baseline counts
python3 tools/db_introspect.py --json > pre_migration_baseline.json

# 2. Check for data issues
python3 tools/db_introspect.py | grep orphaned

# 3. Archive recent records sample
python3 tools/db_introspect.py --json --recent 10 > pre_migration_sample.json
```

### Post-Migration Validation
```bash
# 1. Compare counts
python3 tools/db_introspect.py --json > post_migration.json

# 2. Diff the results
diff <(jq '.table_counts' pre_migration_baseline.json) \
     <(jq '.table_counts' post_migration.json)

# 3. Verify admin can still login (manual step)
# Visit /login with ADMIN_EMAIL and ADMIN_PASSWORD
```

## Troubleshooting

### Common Issues

#### 1. "No module named 'models'"
**Solution:** Ensure you're running from the CORA root directory:
```bash
cd /var/www/cora
python3 tools/seed_users.py
```

#### 2. "Access denied for user" (PostgreSQL)
**Solution:** Check DATABASE_URL environment variable:
```bash
echo $DATABASE_URL
# Should contain valid PostgreSQL credentials
```

#### 3. "database is locked" (SQLite)
**Solution:** Another process is using the database. Stop the service temporarily:
```bash
systemctl stop cora.service
python3 tools/db_introspect.py
systemctl start cora.service
```

#### 4. Password too weak error
**Solution:** Use a stronger password with mixed case, numbers, and symbols:
```bash
export ADMIN_PASSWORD="$(openssl rand -base64 32)"
```

## Security Considerations

1. **Never commit credentials** - Always use environment variables
2. **Rotate admin passwords** regularly in production
3. **Limit admin user creation** to authorized personnel only
4. **Audit admin actions** - Check logs after admin operations
5. **Use read-only introspection** for routine checks

## Monitoring Integration

For automated monitoring, schedule introspection:
```bash
# Add to crontab for daily checks
0 6 * * * cd /var/www/cora && python3 tools/db_introspect.py --json > /var/log/cora/db_daily_$(date +\%Y\%m\%d).json
```

## Related Documentation
- [Database Migration Plan](../plans/active/2025-09-03_db_migration_todowrite.md)
- [System Rules](../SYSTEM_RULES.md)
- [Deployment Guide](./DEPLOY.md)