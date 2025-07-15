# 🔄 CORA User Flow Diagram

## Complete User Journey: Signup → Expense → Export

```
┌─────────────────┐
│   LANDING PAGE  │
│  (cora.com)     │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│   SIGN UP       │
│ • Email         │
│ • Password      │
│ • Business Name │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│  EMAIL VERIFY   │
│ • Click link    │
│ • Account active│
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│   DASHBOARD     │
│ • Welcome msg   │
│ • Quick actions │
│ • Empty state   │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│  ADD EXPENSE    │
│ • Upload photo  │
│ • Manual entry  │
│ • Auto-categorize│
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│  REVIEW/EDIT    │
│ • Check amount  │
│ • Verify category│
│ • Add notes     │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│   SAVE EXPENSE  │
│ • Store in DB   │
│ • Show success  │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│  EXPENSE LIST   │
│ • View all      │
│ • Filter/search │
│ • Bulk actions  │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│   EXPORT DATA   │
│ • Select format │
│ • Choose date   │
│ • Download file │
└─────────────────┘
```

## Key Decision Points

### 1. Signup Flow
- **Email validation:** Required before access
- **Business setup:** Optional but recommended
- **Onboarding:** Guided tour available

### 2. Expense Entry
- **Photo upload:** Primary method (AI extraction)
- **Manual entry:** Fallback option
- **Auto-categorization:** AI suggests category

### 3. Review Process
- **Amount verification:** User confirms extracted amount
- **Category selection:** User can override AI suggestion
- **Notes addition:** Optional context

### 4. Export Options
- **CSV format:** For accounting software
- **PDF report:** For records
- **Date range:** Customizable periods

## Success Metrics for Each Step

1. **Signup completion:** >80% of visitors
2. **First expense added:** >90% of signups within 24h
3. **Photo upload success:** >95% of attempts
4. **AI accuracy:** >90% correct categorization
5. **Export usage:** >60% of users export monthly

## Error Handling Points

- **Email verification:** Resend option available
- **Photo upload fails:** Manual entry fallback
- **AI categorization unclear:** Manual selection required
- **Export fails:** Retry with different format

## Mobile Responsiveness Checkpoints

- [ ] Signup form works on mobile
- [ ] Photo upload accessible on mobile
- [ ] Expense review readable on small screens
- [ ] Export options clear on mobile 