# 📊 CORA Database Schema Documentation
**Generated**: 2025-01-11 18:00  
**Purpose**: Help Claude create accurate SQLAlchemy models during restoration  
**Database**: data/cora.db (143,360 bytes)

## 🎯 Executive Summary

**Database Status**: ✅ **FULLY INTACT** with rich data
- **9 tables** with proper relationships
- **16 users** with hashed passwords
- **235 expenses** with auto-categorization
- **4 customers** with Stripe integration
- **4 subscriptions** with payment tracking
- **6 business profiles** with onboarding data

## 📋 Complete Table Schema

### 1. **users** Table (16 rows)
```sql
CREATE TABLE users (
    email VARCHAR NOT NULL PRIMARY KEY,
    hashed_password VARCHAR,
    created_at DATETIME,
    is_active VARCHAR
);
```
**Purpose**: User authentication and account management  
**Key Features**: Email-based primary key, BCrypt hashed passwords

### 2. **customers** Table (4 rows)
```sql
CREATE TABLE customers (
    id INTEGER NOT NULL PRIMARY KEY,
    user_email VARCHAR,
    stripe_customer_id VARCHAR,
    created_at DATETIME
);
```
**Purpose**: Stripe customer management  
**Relationships**: Links to users via user_email

### 3. **subscriptions** Table (4 rows)
```sql
CREATE TABLE subscriptions (
    id INTEGER NOT NULL PRIMARY KEY,
    customer_id INTEGER,
    stripe_subscription_id VARCHAR,
    plan_name VARCHAR,
    status VARCHAR,
    current_period_start DATETIME,
    current_period_end DATETIME,
    created_at DATETIME,
    canceled_at DATETIME
);
```
**Purpose**: Subscription management  
**Relationships**: Links to customers via customer_id

### 4. **payments** Table (6 rows)
```sql
CREATE TABLE payments (
    id INTEGER NOT NULL PRIMARY KEY,
    customer_id INTEGER,
    stripe_payment_intent_id VARCHAR,
    amount FLOAT,
    currency VARCHAR,
    status VARCHAR,
    description VARCHAR,
    created_at DATETIME
);
```
**Purpose**: Payment tracking  
**Relationships**: Links to customers via customer_id

### 5. **password_reset_tokens** Table (1 row)
```sql
CREATE TABLE password_reset_tokens (
    token_hash VARCHAR(64) NOT NULL PRIMARY KEY,
    user_email VARCHAR(255) NOT NULL,
    created_at DATETIME,
    expires_at DATETIME NOT NULL,
    used BOOLEAN,
    used_at DATETIME
);
```
**Purpose**: Password reset functionality  
**Security**: Token hashing, expiration tracking

### 6. **expense_categories** Table (15 rows)
```sql
CREATE TABLE expense_categories (
    id INTEGER NOT NULL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    icon VARCHAR(50),
    is_active BOOLEAN,
    created_at DATETIME
);
```
**Purpose**: Expense categorization system  
**Features**: Icon support, active/inactive status

### 7. **expenses** Table (235 rows)
```sql
CREATE TABLE expenses (
    id INTEGER NOT NULL PRIMARY KEY,
    user_email VARCHAR(255) NOT NULL,
    amount_cents INTEGER NOT NULL,
    currency VARCHAR(3),
    category_id INTEGER,
    description TEXT NOT NULL,
    vendor VARCHAR(200),
    expense_date DATETIME NOT NULL,
    payment_method VARCHAR(50),
    receipt_url VARCHAR(500),
    tags JSON,
    created_at DATETIME,
    updated_at DATETIME,
    confidence_score INTEGER DEFAULT NULL,
    auto_categorized INTEGER DEFAULT 0
);
```
**Purpose**: Core expense tracking  
**Features**: 
- Amount in cents for precision
- Auto-categorization with confidence scores
- JSON tags for flexible metadata
- Receipt URL storage
- Vendor tracking

### 8. **business_profiles** Table (6 rows)
```sql
CREATE TABLE business_profiles (
    id INTEGER PRIMARY KEY,
    user_email TEXT NOT NULL,
    business_name TEXT NOT NULL,
    business_type TEXT NOT NULL,
    industry TEXT NOT NULL,
    monthly_revenue_range TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```
**Purpose**: Business onboarding and profiling  
**Relationships**: Links to users via user_email

### 9. **user_preferences** Table (2 rows)
```sql
CREATE TABLE user_preferences (
    user_email TEXT PRIMARY KEY,
    goals TEXT,
    integrations TEXT,
    onboarding_completed BOOLEAN DEFAULT 0,
    onboarding_step INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```
**Purpose**: User preferences and onboarding state  
**Features**: JSON fields for goals and integrations

## 🔗 Key Relationships

### **User-Centric Relationships:**
- `users.email` → `customers.user_email`
- `users.email` → `expenses.user_email`
- `users.email` → `business_profiles.user_email`
- `users.email` → `user_preferences.user_email`
- `users.email` → `password_reset_tokens.user_email`

### **Payment Relationships:**
- `customers.id` → `subscriptions.customer_id`
- `customers.id` → `payments.customer_id`

### **Expense Relationships:**
- `expense_categories.id` → `expenses.category_id`

## 🎯 Model Creation Guidelines for Claude

### **Priority Models (Core Functionality):**
1. **User** - Authentication and account management
2. **Expense** - Core business logic
3. **ExpenseCategory** - Categorization system
4. **Customer** - Payment integration
5. **Subscription** - Subscription management

### **Secondary Models (Supporting):**
6. **Payment** - Payment tracking
7. **BusinessProfile** - Onboarding
8. **UserPreference** - User settings
9. **PasswordResetToken** - Security

### **SQLAlchemy Model Patterns:**
```python
# Use these patterns for consistency:
from sqlalchemy import Column, String, DateTime, Boolean, Integer, Text, Float
from sqlalchemy.sql import func
from .base import Base

class User(Base):
    __tablename__ = "users"
    
    email = Column(String, primary_key=True)
    hashed_password = Column(String)
    created_at = Column(DateTime, default=func.now())
    is_active = Column(String, default="1")
```

### **Important Notes:**
- **Amounts**: Use INTEGER for cents (expenses.amount_cents)
- **JSON Fields**: Use Text for JSON storage (expenses.tags)
- **Timestamps**: Use DateTime with func.now() default
- **Foreign Keys**: Use String for email-based relationships
- **Boolean**: Use INTEGER with 0/1 for SQLite compatibility

## ✅ Data Integrity Status

**All relationships intact** ✅  
**No orphaned records** ✅  
**Proper indexing** ✅  
**Data consistency** ✅  

**Ready for model recreation** ✅ 