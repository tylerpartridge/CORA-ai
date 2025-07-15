# CORA A/B Testing & Pricing Optimization Strategy

## Executive Summary

This document outlines a systematic approach to pricing optimization through A/B testing, designed to maximize revenue while maintaining healthy growth metrics. We'll run 12 tests over 6 months to optimize conversion, retention, and revenue.

## Testing Framework

### Statistical Requirements
- **Sample Size**: Minimum 1,000 users per variant
- **Confidence Level**: 95% (p < 0.05)
- **Power**: 80% minimum
- **Test Duration**: 2-4 weeks per test
- **Success Metric**: Revenue per visitor (primary), conversion rate (secondary)

### Testing Infrastructure
```python
# Core metrics to track per variant
{
    "variant_id": "control|test_a|test_b",
    "visitors": 1000,
    "signups": 150,
    "paid_conversions": 45,
    "revenue": 405.00,
    "churn_rate": 0.05,
    "ltv": 180.00
}
```

## Phase 1: Price Point Optimization (Months 1-2)

### Test 1.1: Starter Tier Pricing
**Hypothesis**: Lower starter price will increase overall revenue through volume

**Variants**:
- Control: $9/user/month
- Test A: $7/user/month (-22%)
- Test B: $5/user/month (-44%)
- Test C: $12/user/month (+33%)

**Metrics**:
- Primary: Revenue per visitor
- Secondary: Conversion rate, ARPU

**Expected Results**:
- $5 price: +40% conversions, -20% revenue
- $7 price: +20% conversions, -5% revenue
- $12 price: -25% conversions, +5% revenue

### Test 1.2: Professional Tier Pricing
**Hypothesis**: Pro tier has pricing power due to AI features

**Variants**:
- Control: $19/user/month
- Test A: $15/user/month
- Test B: $25/user/month
- Test C: $29/user/month

**Success Criteria**: Maximize tier mix revenue

### Test 1.3: Team Tier Entry Point
**Hypothesis**: Lower team tier attracts more growing businesses

**Variants**:
- Control: $39/user/month
- Test A: $29/user/month
- Test B: $49/user/month
- Test C: $35/user/month (5+ users)

## Phase 2: Free Tier Optimization (Months 2-3)

### Test 2.1: Free Tier Expense Limit
**Hypothesis**: Tighter limits drive faster conversion

**Variants**:
- Control: 50 expenses/month
- Test A: 25 expenses/month
- Test B: 100 expenses/month
- Test C: 30 expenses + 7-day trial of Pro

**Key Metrics**:
- Free→Paid conversion rate
- Time to conversion
- Activation rate

### Test 2.2: Free Tier Feature Gates
**Hypothesis**: Strategic feature limitations improve conversions

**Variants**:
- Control: Current feature set
- Test A: No QuickBooks sync
- Test B: Limited to 1 integration
- Test C: No CSV export

### Test 2.3: Free Trial vs Freemium
**Hypothesis**: Time-limited trials create urgency

**Variants**:
- Control: Freemium (current)
- Test A: 14-day trial of Pro tier
- Test B: 30-day trial of Starter
- Test C: Hybrid (free tier + trial upgrades)

**Implementation**:
```javascript
// Trial urgency messaging
if (daysLeft <= 3) {
  showBanner("Your trial ends in " + daysLeft + " days! Upgrade now for 20% off");
}
```

## Phase 3: Billing Cycle Optimization (Months 3-4)

### Test 3.1: Annual Discount Percentage
**Hypothesis**: Optimal discount balances cash flow and retention

**Variants**:
- Control: 17% annual discount
- Test A: 10% discount
- Test B: 20% discount
- Test C: 25% discount
- Test D: No discount, but add features

**Financial Impact Model**:
| Discount | Annual Adoption | Cash Flow Impact | LTV Impact |
|----------|----------------|------------------|------------|
| 10% | 25% | +3x baseline | -5% |
| 17% | 40% | +4.8x baseline | +12% |
| 20% | 45% | +5.4x baseline | +15% |
| 25% | 55% | +6.6x baseline | +18% |

### Test 3.2: Multi-Year Discounts
**Hypothesis**: 2-year commitments valuable for stability

**Variants**:
- Control: Annual only
- Test A: 2-year at 30% discount
- Test B: 3-year at 40% discount
- Test C: Tiered (1yr: 17%, 2yr: 27%, 3yr: 37%)

### Test 3.3: Billing Frequency Options
**Hypothesis**: Quarterly billing reduces churn

**Variants**:
- Control: Monthly/Annual only
- Test A: Add quarterly (5% discount)
- Test B: Add semi-annual (10% discount)
- Test C: All options available

## Phase 4: Upsell & Expansion (Months 4-5)

### Test 4.1: In-App Upgrade Prompts
**Hypothesis**: Contextual upsells improve conversion

**Variants**:
- Control: Settings page only
- Test A: Usage-triggered prompts
- Test B: Feature-gate prompts
- Test C: AI recommendations

**Trigger Examples**:
```python
# Usage triggers
if monthly_expenses > tier_limit * 0.8:
    show_upgrade_prompt("You're approaching your limit!")

# Feature triggers  
if user_clicked_locked_feature:
    show_upgrade_modal(feature_name)

# AI triggers
if ai_detected_growth_pattern:
    recommend_upgrade("Your business is growing!")
```

### Test 4.2: Add-On Features
**Hypothesis**: Modular pricing increases ARPU

**Test Add-Ons**:
- Advanced AI Insights: +$10/month
- Priority Support: +$5/month
- Extra Integrations: +$5/each
- White-label Reports: +$15/month

### Test 4.3: Seat Expansion Incentives
**Hypothesis**: Volume discounts encourage team growth

**Variants**:
- Control: Flat per-seat pricing
- Test A: 5+ seats get 20% off
- Test B: 10+ seats get 30% off
- Test C: Progressive (5-20% based on count)

## Phase 5: Onboarding & Activation (Month 5)

### Test 5.1: Pricing Page Design
**Hypothesis**: Design impacts conversion significantly

**Variants**:
- Control: Current design
- Test A: Highlight recommended tier
- Test B: Start with highest tier
- Test C: Interactive calculator
- Test D: Testimonials by tier

### Test 5.2: Trial Onboarding Flow
**Hypothesis**: Faster value realization improves conversion

**Variants**:
- Control: Standard onboarding
- Test A: Required QuickBooks connection
- Test B: Sample data pre-loaded
- Test C: Guided first expense entry
- Test D: Video walkthrough

### Test 5.3: Payment Method Timing
**Hypothesis**: Earlier card capture improves conversion

**Variants**:
- Control: Card required at upgrade
- Test A: Card optional at signup
- Test B: Card required for trial
- Test C: Progressive (ask after 3 days)

## Phase 6: Retention & Win-Back (Month 6)

### Test 6.1: Cancellation Flow
**Hypothesis**: Retention offers reduce churn

**Variants**:
- Control: Direct cancellation
- Test A: Offer 50% off for 2 months
- Test B: Downgrade option presented
- Test C: Pause account option
- Test D: Exit survey + personalized offer

### Test 6.2: Win-Back Campaigns
**Hypothesis**: Targeted offers re-activate churned users

**Test Campaigns**:
- 30 days: "We miss you" + 1 month free
- 60 days: 50% off for 3 months
- 90 days: New features announcement
- 180 days: "Start fresh" + onboarding help

### Test 6.3: Loyalty Rewards
**Hypothesis**: Rewards reduce churn and increase ARPU

**Test Programs**:
- Months 3-6: 10% loyalty discount
- Annual commitment: Free month
- Referral rewards: $50 credit per referral
- Usage achievements: Unlock features

## Implementation Guidelines

### Test Prioritization Matrix
| Test | Impact | Effort | Priority | Dependencies |
|------|--------|--------|----------|--------------|
| Starter Pricing | High | Low | 1 | None |
| Free Tier Limits | High | Low | 2 | None |
| Annual Discount | High | Medium | 3 | Billing system |
| Upgrade Prompts | Medium | Medium | 4 | Analytics |
| Trial Flow | High | High | 5 | Onboarding revamp |

### Success Metrics Dashboard
```python
# Key metrics to monitor
{
    "revenue_per_visitor": 3.45,
    "visitor_to_signup": 0.14,
    "signup_to_paid": 0.30,
    "monthly_churn": 0.05,
    "ltv_to_cac": 3.5,
    "annual_plan_adoption": 0.40,
    "expansion_revenue_ratio": 1.15
}
```

### Test Analysis Framework
1. **Pre-Test**:
   - Calculate required sample size
   - Set up tracking
   - Document hypothesis

2. **During Test**:
   - Monitor for errors
   - Check sample ratio
   - Watch for seasonality

3. **Post-Test**:
   - Statistical significance
   - Practical significance
   - Segment analysis
   - Long-term impact modeling

## Expected Outcomes

### Revenue Impact Projections
| Optimization Area | Expected Lift | Revenue Impact |
|-------------------|---------------|----------------|
| Price Points | +15% ARPU | +$138K ARR |
| Free Tier | +5% conversion | +$46K ARR |
| Annual Billing | +8% LTV | +$74K ARR |
| Upsells | +20% expansion | +$184K ARR |
| Retention | -2% churn | +$92K ARR |
| **Total** | **+58%** | **+$534K ARR** |

### Risk Mitigation
1. **Test Isolation**: Run one pricing test at a time
2. **Rollback Plan**: Can revert within 24 hours
3. **Communication**: Clear changelog for users
4. **Grandfathering**: Existing users keep their rates

## Long-Term Pricing Evolution

### Year 1: Foundation
- Establish optimal price points
- Build testing infrastructure
- Create pricing discipline

### Year 2: Sophistication
- Dynamic pricing by segment
- Geographic pricing
- Industry-specific packages

### Year 3: AI-Driven
- Personalized pricing
- Predictive churn pricing
- Real-time optimization

## Conclusion

This systematic approach to pricing optimization can increase revenue by 50-60% over 6 months while maintaining healthy unit economics. Key success factors:

1. **Disciplined Testing**: One variable at a time
2. **Statistical Rigor**: Proper sample sizes
3. **Customer Focus**: Balance revenue with experience
4. **Rapid Iteration**: 2-week test cycles
5. **Data-Driven Decisions**: Let metrics guide strategy

Start with Test 1.1 (Starter Tier Pricing) immediately upon reaching 1,000 monthly visitors.

---

*Document Version: 1.0*
*Last Updated: January 2025*
*Review Frequency: Bi-weekly during testing phases*