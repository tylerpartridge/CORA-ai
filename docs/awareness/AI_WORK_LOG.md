# AI Work Log

> Living document for tracking AI contributions. Each AI that contributes should add entries here.
> Format: **Date — Model — Summary**
> Newest entries first.

## 2025-09-02 — Backup seatbelt installed (comprehensive nightly system)
- Created complete backup system: Linux/Windows scripts, restore guide, 14-day retention
- First successful run: backups/2025-09-02_123131 (21MB docs + 412KB DB + BI cache)
- Windows Task Scheduler setup ready (03:25 UTC daily); production systemd timer prepared

## 2025-09-02 — Export Manager modularized (945 lines → compliant)
- Split export_manager.js into modular tree: all modules <300 lines, largest 211 (modal-styles.js)
- Backward-compatible shim preserved for existing code
- CI guard alignment achieved; technical debt reduced

## 2025-09-02 — BI placeholders wired
BI snapshot hardened (tag `v0.1.0-bi-snapshot-hardened`) — QBO/Jobber using `manual_notes` **placeholders** only; human pricing confirmation pending. Final run: 5 OK / 2 ERR; IRS OK; cache + logs updated.

## 2025-09-01 — Unsubscribe link implemented (opt-in/opt-out)
- ✅ Merged PR #40: unsubscribe route + opt-in/opt-out for weekly insights emails
- ✅ Files: `models/user.py`, `migrations/add_weekly_insights_opt_in.py`, `routes/weekly_insights.py`, `routes/settings.py`, `dependencies/auth.py`, `app.py`, `tests/test_unsubscribe.py`
- 🚀 Deployed in batch window; smokes passed (`/health` 200, `/api/status` 200)
- 🟢 System health: GREEN

## 2025-09-01 — GPT-5/Opus — "Filename standardization shipped (timezone-aware); tests updated; deployed GREEN."

## 2025-09-01 — Weekly insights validation shipped (3/5/3)
- ✅ Merged PR #38: adds weekly validation service and route (`services/weekly_report_service.py`, `routes/weekly_insights.py`)
- ✅ Added tests: `tests/test_weekly_validation.py` (green)
- 🚀 Deployed in batch window; smokes passed (`/health` 200, `/api/status` 200)
- 🟢 System health: GREEN

## 2025-09-01 — GPT-5/Opus — "Weekly Insights 3/5/3 validation shipped; routes integrated; tests passing; deployed GREEN."

## 2025-09-01 — Filename standardization shipped
- ✅ Merged PR #36: standardize CSV export filenames to `cora_{type}_{email}_{YYYYMMDD}.csv` (timezone-aware)
- ✅ Updated `utils/filenames.py`, `web/static/js/export_manager.js`, and `tests/test_export_filenames.py`
- 🚀 Deployed in batch window; smokes passed (`/health` 200, `/api/status` 200)
- 🟢 System health: GREEN

## 2025-09-01 — Onboarding skip buttons shipped
- ✅ Created UserOnboardingStep model for skip state persistence
- ✅ Added /api/onboarding/skip-step endpoint with validation and warnings
- ✅ Enhanced checklist endpoint to show skipped steps and count toward progress
- ✅ Updated "I'll do this later" button to call skip API for relevant steps
- ✅ Created OnboardingService for feature availability checks (no blocking)
- ✅ Added comprehensive tests for skip functionality (test_onboarding_skip.py)
- 🎯 UX improvement: Users can now skip blocking onboarding steps while preserving progress state

## 2025-09-01 — Timezone selection verified
- Created throwaway user: test_landing3@example.com via signup UI
- DB shows timezone=America/New_York (auto-detected from browser)
- Confirms signup flow persists timezone and exports will respect user tz
- Test suite present but gated (requires CORA_DB_TESTS / CORA_E2E flags)
- Manual acceptance complete; feature marked DONE

## 2025-08-30 — EOD Checkpoint (21:09 UTC)
**Model:** Claude 3.5 Sonnet  
**Summary:** 
- ✅ PR #19 merged; awareness guards + checkpoint redirect live on `main`
- ✅ Handoff updated: prompt labeling standard + workflow clarified
- 🟢 System health: GREEN (baseline clean)
- 🧭 Next Action (tomorrow): create fresh branch from `main` for MVP money-path (pricing CTA → Stripe) per handoff

## 2025-08-30 — Repository Cleanup & Guards Deployed
**Model:** Claude 3.5 Sonnet  
**Summary:** 
- ✅ Rebase finished cleanly; PR #19 merged into main (squash)
- ✅ Branch + stale refs pruned; local on `main`
- ✅ Guards live: duplicate check, checkpoint logging guard, bootup files verifier
- ✅ Checkpoint logs redirected to CHECKPOINT_LOG.md (no more awareness corruption)
- 🟢 System health: GREEN
- 🎯 Next: open fresh work branch from `main` for today's focus

## 2025-08-30 — Critical Fixes Applied
**Model:** Claude 3.5 Sonnet (Opus Mode)
**Summary:** Fixed Git merge conflicts in CI workflow. Redirected checkpoint logging from AI_WORK_LOG.md to CHECKPOINT_LOG.md. Added bootup files verifier to CI. Updated pre-commit hooks to be more targeted (only check code files for backups, only check awareness files for line limits). System ready for actual work.

## 2025-08-30 — Pricing CTA Implementation Complete
**Model:** Claude 3.5 Sonnet (Opus Mode)
**Summary:** Implemented Stripe Payment Links for pricing CTAs. Routes pass PAYMENT_LINK environment variables to template. Template uses payment links when set, falls back to /signup?plan=X otherwise. Removed JavaScript checkout modal to prevent errors. Added comprehensive test coverage for all scenarios.## 2025-09-01 — Deploy wiring + scripted deploy
- Merged PR #32: repo deploy script + team runbook + BOOTUP/NOW/NEXT pointers
- First scripted deploy via Invoke-CoraDeploy.ps1 (batch window): /health 200 JSON, /api/status 200
- Notes: service restart clean; nginx unchanged; no errors in journalctl
