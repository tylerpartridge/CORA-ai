## 2025-09-09T15:25Z — Monitoring Minimal Set rescheduled
- Missed 15:00Z batch; rescheduled Monitoring Minimal Set to 17:30Z UTC today. Prep one‑shot scripts to execute at window; no manual testing.
**2025-09-09T13:30Z — Cursor — Secrets/ops milestone checkpoint:**
- PRs merged/open: #75 routes hygiene, #76 secrets audit + untrack .env, #77 secretless scripts, #78 SYSTEM_RULES secrets policy, #79 CI secrets scanning
- Root backup hooks cleaned; pre-push guard installed
- Service GREEN; ops hardened; monitoring minimal set queued for 15:00 UTC

**2025-09-09T00:00Z — Cursor — Section 2 (API-only) probe**
- Unauth GET /api/user/profile → expected 401
- Local smokes: ran (see server logs)
- Auth/login not executed by policy (API-only today) → Section 2 marked **YELLOW**
- Follow-up: seed a test user via scripted path next GREEN session, then re-run Section 2
## 2025-09-08 — Cursor — Ops Hardening complete: disk retention policy enforced, journald capped at 200M, smoke.sh executable. TLS renewal pending (certbot not installed).

## 2025-09-08 — GPT-5 + Cursor — PROD recovery (disk full). Freed ~19G under /var/backups/cora/system; service healthy; smokes green (health 200, status 200, protected 401). No code changes.

## 2025-09-04 (UTC) — Policy Update
- Collaboration roles updated: **Cursor = primary executor (code/git/deploy)**; **Sonnet = audits/intel/codebase search only**; **Opus removed**.
- Prompt Labeling enforced; explicit Tyler-required steps will be called out.

## 2025-09-04 (UTC) — RED (prod 502)

- Manual Walkthrough S1 progress: Steps 1–7 executed; evidence captured in `docs/ai-audits/2025-09-04/manual_walkthrough_auth.md`.
- Defects logged: **A-RESET-500** (`POST /api/auth/forgot-password` → 500), **A-LOGIN-TIMEOUT** (CLI `POST /api/auth/login` stalls), **A-LOGIN-SLOW-60S** (first two bad-login attempts ~60s), **A-LOGIN-RATELIMIT-OK** (429 with retry hint), **A-LOGIN-RETRY-MISMATCH** (message “483s” vs `retry_after=60`).
- Shipped: **PR #70** (prefs: `/api/user/settings` GET/PATCH, currency field, tz-aware exports). CI green; merged (squash). Deploy attempted.
- Incident: PROD startup failed (TypeError `ErrorHandler()` ctor; then ImportError `PDFExporter`). On-box mitigations applied (`ErrorHandler()` no-arg; `PDFExporter` alias), still 502. Disk `/` at ~98%.
- Next: **Morning 3-step recover** (vacuum logs, reproduce traceback, minimal import fix), then run Step 8 smokes (unauth 401, auth GET/PATCH, re-GET).

## 2025-09-04 (UTC) — RED (prod 502)

- Manual Walkthrough S1 progress: Steps 1–7 executed; evidence captured in `docs/ai-audits/2025-09-04/manual_walkthrough_auth.md`.
- Defects logged: **A-RESET-500** (`POST /api/auth/forgot-password` → 500), **A-LOGIN-TIMEOUT** (CLI `POST /api/auth/login` stalls), **A-LOGIN-SLOW-60S** (first two bad-login attempts ~60s), **A-LOGIN-RATELIMIT-OK** (429 with retry hint), **A-LOGIN-RETRY-MISMATCH** (message “483s” vs `retry_after=60`).
- Shipped: **PR #70** (prefs: `/api/user/settings` GET/PATCH, currency field, tz-aware exports). CI green; merged (squash). Deploy attempted.
- Incident: PROD startup failed (TypeError `ErrorHandler()` ctor; then ImportError `PDFExporter`). On-box mitigations applied (`ErrorHandler()` no-arg; `PDFExporter` alias), still 502. Disk `/` at ~98%.
- Next: **Morning 3-step recover** (vacuum logs, reproduce traceback, minimal import fix), then run Step 8 smokes (unauth 401, auth GET/PATCH, re-GET).


### 2025-09-03 EOD (UTC) — Prod cutover to Postgres + smokes + backups (GREEN)
**Action:** Completed SQLite→Postgres production cutover using transactional migrator with auto-rollback guard (unused). Patched validator to cast FK-like columns; added canonical smoke harness (bash+python) and runbook; scaffolded manual walkthrough doc.
**Evidence:** /api/status → 200; smokes GREEN (200/200/401); DSN stored at `/root/CORA_PROD_PG_DSN.env`; migration artifacts in `/var/log/cora_migration/` (SRC/TGT/JSONL); nightly pg_dump timer installed; first dump + restore verify passed.
**Shipped:** `tools/migrate_sqlite_to_postgres.py`, `tools/db_introspect.py` (cast fix), `tools/smoke.sh`, `tools/smoke.py`, `docs/runbooks/SMOKES.md`, manual walkthrough scaffold.
**State:** GREEN on Postgres.
**Next:** Manual Walkthrough Section 1 (Auth & Session) tomorrow; capture notes/evidence, then proceed to Section 2 (Profile & Timezone).

### 2025-09-03 23:13:51 UTC — Decision — Defer off-site backups
**Reason:** Launch focus; local nightly dumps + verified restore are sufficient pre-revenue.
**Trigger to revisit:** After first paying customer **or** immediately post-launch.
**Owner:** Tyler (approve when ready to enable S3 runbook).

## 2025-09-03 — GPT-5 — Prod cutover to Postgres
Cut over CORA prod from SQLite → **PostgreSQL** with full backups, transactional migrate, health-gated DSN switch, and auto-rollback safety.
**Probes:** initial 000 then 200.
**Artifacts (prod):** /var/log/cora_migration/prod_src_counts_*.json, prod_tgt_counts_*.json, prod_migration_*.jsonl.
**Notes:** Validator cast warning persists (benign); follow-up patch scheduled.
# AI Work Log

> Living document for tracking AI contributions. Each AI that contributes should add entries here.
> Format: **Date — Model — Summary**
> Newest entries first.

## 2025-09-03 — Opus — Codified durable workflow rules
Codified three durable workflow rules into `docs/SYSTEM_RULES.md` (CI router guard, stub-first rescue, journalctl-first) from production debugging session. These rules emerged from resolving router import issues causing service restart loops. Updated file: `docs/SYSTEM_RULES.md` with new section "DURABLE WORKFLOW RULES (2025-09-03)".

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

## 2025-09-03 — Backup automation + restore drill
- Windows Task Scheduler @ 00:55 local with transcript logging
- Interactive + scheduled backups verified with checksums
- Restore drill succeeded to C:\CORA\restore_sandbox_20250903_092313



