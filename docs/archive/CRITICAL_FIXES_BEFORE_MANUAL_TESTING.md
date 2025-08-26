# 🚨 CRITICAL FIXES NEEDED BEFORE MANUAL TESTING

*Created for: Tyler*  
*Purpose: Minimize friction during manual testing*  
*Priority: Only the most critical issues that will block or frustrate testing*

## 🔴 SHOWSTOPPERS (Fix These First)

### 1. **Email Service Not Working**
**Problem**: Users can't reset passwords or receive any emails  
**Testing Impact**: You'll get stuck if you forget a password  
**Quick Fix**: 
```python
# Add to services/email_service.py
import requests

def send_email(to_email: str, subject: str, body: str):
    """Simple SendGrid email implementation"""
    SENDGRID_API_KEY = "ALxDBEHhSR2DWekJ_Bf-qw"  # Move to env later
    
    response = requests.post(
        "https://api.sendgrid.com/v3/mail/send",
        headers={
            "Authorization": f"Bearer {SENDGRID_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "personalizations": [{"to": [{"email": to_email}]}],
            "from": {"email": "noreply@coraai.tech"},
            "subject": subject,
            "content": [{"type": "text/plain", "value": body}]
        }
    )
    return response.status_code == 202
```

### 2. **Can't Export Any Data**
**Problem**: No way to get expense data out of the system  
**Testing Impact**: Can't verify data or use it elsewhere  
**Quick Fix**: Add simple CSV export endpoint
```python
# Add to routes/expenses.py
@expense_router.get("/export/csv")
async def export_expenses_csv(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    expenses = db.query(Expense).filter(Expense.user_email == current_user.email).all()
    output = "Date,Description,Amount,Category\n"
    for expense in expenses:
        output += f"{expense.date},{expense.description},{expense.amount},{expense.category}\n"
    return Response(content=output, media_type="text/csv", headers={"Content-Disposition": "attachment; filename=expenses.csv"})
```

### 3. **No Legal Pages**
**Problem**: No Terms of Service or Privacy Policy  
**Testing Impact**: Can't legally onboard real users  
**Quick Fix**: Create minimal pages
```html
<!-- Add to web/templates/terms.html -->
<h1>Terms of Service</h1>
<p>This is a beta service. Use at your own risk. We're not responsible for anything.</p>
<p>Last updated: July 2025</p>

<!-- Add to web/templates/privacy.html -->
<h1>Privacy Policy</h1>
<p>We collect expense data you provide. We don't sell it. We use cookies.</p>
<p>Contact: privacy@coraai.tech</p>
```

### 4. **Hardcoded Secret Keys**
**Problem**: Major security risk with exposed keys  
**Testing Impact**: Could compromise your test data  
**Quick Fix**: At minimum, change these NOW:
- In `auth_service.py`: Change `SECRET_KEY = "your-secret-key-here"` to something random
- In `.env.production`: Generate new keys for production

## 🟡 ANNOYING ISSUES (Fix If Time)

### 5. **Can't Upload Receipts**
**Problem**: Have to type everything manually  
**Testing Impact**: Tedious to test real expense entry  
**Note**: This is a bigger feature - skip for initial testing

### 6. **No Recurring Expenses**
**Problem**: Have to re-enter subscriptions monthly  
**Testing Impact**: Annoying but not blocking  
**Note**: Can add manually for now

### 7. **No Mobile Optimization**
**Problem**: Hard to use on phone  
**Testing Impact**: Desktop testing is fine  
**Note**: Beta users can use desktop

## 🟢 ALREADY WORKING (Don't Worry About)

✅ User registration and login  
✅ Basic expense CRUD  
✅ Categories (15 pre-loaded)  
✅ Admin dashboard  
✅ Security middleware  
✅ Database backups  
✅ Production deployment  

## 📋 Testing Checklist

When you start manual testing, try this flow:

1. **Sign Up**
   - Create account with your email
   - ⚠️ You won't get confirmation email (unless you fix #1)

2. **Add Expenses**
   - Try different categories
   - Test different amounts
   - Check date handling

3. **View Dashboard**
   - Check totals are correct
   - Verify category breakdowns
   - Test time filters

4. **Admin Features**
   - Access `/admin` dashboard
   - View user stats
   - Check feedback system

5. **Export Data**
   - ⚠️ Won't work unless you fix #2
   - Alternative: Check database directly

6. **Error Cases**
   - Try invalid data
   - Test auth failures
   - Check rate limiting

## 🚀 Quick Start Commands

```bash
# Local testing
cd C:\CORA
python -m uvicorn app:app --reload

# Check database
python
>>> from models import SessionLocal, Expense
>>> db = SessionLocal()
>>> expenses = db.query(Expense).all()
>>> for e in expenses: print(e.description, e.amount)

# Production logs
ssh root@coraai.tech
pm2 logs cora --lines 100
```

## 💡 Pro Tips

1. **Use the API docs**: Visit `http://localhost:8000/docs` for interactive API testing
2. **Check logs**: Most issues will show up in console or PM2 logs
3. **Test with 2 accounts**: Create admin and regular user to test permissions
4. **Use real data**: Enter actual expenses to see if categorization makes sense
5. **Note everything**: Keep a list of issues as you find them

## 🎯 Success Criteria

You can consider the system "ready for beta users" when:

1. ✅ You can complete a full user journey (signup → add expense → view dashboard)
2. ✅ Email notifications work (at least password reset)
3. ✅ You can export your data somehow
4. ✅ Legal pages exist (even if basic)
5. ✅ No hardcoded secrets in code

Everything else can be iteratively improved based on user feedback!

---

**Remember**: This is a beta. It doesn't need to be perfect, just functional and secure enough for early users to provide feedback. Focus on the showstoppers first!