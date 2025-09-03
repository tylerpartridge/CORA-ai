# Market Pulse — 2025-09-02

> **Placeholder Notes (QBO & Jobber):** Scraping is currently blocked (timeouts/403). We enabled `manual_notes` *placeholders* in the BI registry to wire the fallback path **without** fabricating prices. No pricing values are recorded until human confirmation.

## Snapshot
**Market Overview:** First hardened BI snapshot completed. 5 of 7 sources succeeded. QuickBooks Online timed out across multiple URLs; Jobber returned 403 (error HTML cached). Others were captured with pricing snippets.

**Key Metrics (run-level):**
- Sources processed: 7
- URLs fetched: 7
- Successful: 5
- Failed: 2
- Cache dir: docs/bi/cache/2025-09-02

## Notable Moves
- Zoho Expense pricing page consistently accessible (5 snippets captured).
- Buildertrend pricing captured reliably (20 snippets).
- Procore pricing page reachable (11 snippets, largely "contact/sales" language).
- QBO: persistent timeouts; added alt URLs + HTTP overrides, still failing this run.
- Jobber: 403 blocking; error page captured for analysis.

## Vendor Status Table
| Vendor               | Status       | Best URL                                                | Snippets | Notes                          |
|----------------------|--------------|---------------------------------------------------------|----------|---------------------------------|
| Contractor Foreman   | OK           | https://contractorforeman.com/                          | 18       | Pricing snippets captured       |
| QuickBooks Online    | manual_fallback (placeholders) | https://quickbooks.intuit.com/pricing/                 | 0        | Timeouts across primary/alt URLs; awaiting human pricing confirmation |
| Zoho Expense         | OK           | https://www.zoho.com/us/expense/pricing/               | 5        | Pricing snippets captured       |
| Jobber               | manual_fallback (placeholders) | https://www.getjobber.com/pricing/                      | 0        | 403; error HTML/JSON cached; awaiting human pricing confirmation |
| Buildertrend         | OK           | https://buildertrend.com/pricing/                       | 20       | Pricing snippets captured       |
| Procore              | OK           | https://www.procore.com/pricing                         | 11       | Generic pricing page captured (no list prices; lead-gen CTA) |
| IRS 1099-K (reg)     | OK           | https://www.irs.gov/newsroom/irs-provides-transition-relief-for-third-party-settlement-organizations-form-1099-k-threshold-is-5000-for-calendar-year-2024 | 4 | Transition-relief page captured; 2024 threshold 5000 messaging opportunity |

## Risks & Watchlist
- **QBO access instability**: timeouts despite retries and alt URLs.
- **Jobber bot-blocking (403)**: requires manual fallback or different endpoints.
- **Evidence volatility**: sites change markup; selectors may require periodic refresh.

## Implications
- Pricing pressure at low-end (Zoho free tier), QBO reliability issues for scraping.
- Continue considering Solo $29 / Crew $69 / Business $149 experiment.
- Messaging: emphasize hands-free voice capture over "AI bookkeeping."

## Next BI Actions
- Add/confirm `manual_notes` for QBO (bullets + date) for guaranteed fallback on future runs.
- Explore alternate public sources for QBO pricing (support articles, reseller PDFs) and add to `alt_urls`.
- Consider lightweight headless-browser fallback for 403/anti-bot pages (deferred; not MVP).