# GPT5_handoff.md

> One file to carry between threads.  
> **Part A (Stable Playbook)** stays stable.  
> **Part B (Session Capsule)** is the only section you update each thread.

---

## PART A — STABLE PLAYBOOK (ESSENTIALS)

### 🛑 FILES REQUIRED BEFORE BOOTUP

**MANDATORY: GPT-5 MUST HALT if these files are not provided at session start:**

□ BOOTUP.md  
□ docs/awareness/MISSION.md  
□ docs/ai-awareness/MVP_REQUIREMENTS.md  
□ docs/awareness/NOW.md  
□ docs/awareness/NEXT.md  
□ docs/awareness/STATUS.md  
□ docs/awareness/AI_WORK_LOG.md  
□ docs/awareness/AI_DISCUSSION_SPACE.md  
□ GPT5_handoff.md  

**Enforcement Rule:** If any of these 9 files are missing, GPT-5 must immediately request them from Tyler before proceeding with ANY other work. No exceptions.

### BOOTUP PROCEDURE

1. **File Verification Phase**
   - Confirm all 9 required files are provided
   - If any missing → HALT and request from Tyler
   
2. **Hydration Phase**
   - Read all provided awareness files
   - Parse current state from NOW.md, NEXT.md, STATUS.md
   - Review session capsule in GPT5_handoff.md Part B
   
3. **Discussion Phase (MANDATORY)**
   - **GPT-5 MUST summarize where we stand and propose what we *should* do next BEFORE generating any prompts**
   - Format: 
     - Current State: [1-2 sentences from NOW.md]
     - Last Completed: [what was finished]
     - Next Priority: [from NEXT.md]
     - Proposed Action: [what GPT-5 recommends doing]
     - Wait for Tyler's confirmation/adjustment
   - GPT-5 proposes ONE recommended next action. If the action produces edits, GPT-5 MUST also include the commit block. No "now or later" questions.
   
4. **Execution Phase**
   - Only after Tyler confirms the proposed action
   - Generate appropriate prompts for collaborators
   - Each prompt must specify target (Sonnet, Opus, Cursor, Tyler)

### Hotkeys
- **save** → lightweight snapshot (append minimal awareness log)
- **checkpoint** → full milestone capture (NOW, NEXT, REGISTRY, LOST_AND_FOUND updated)
- **hydrate** → reload state when starting a fresh thread
- **TodoWrite** → required for any 2+ step task (forces a checklist doc)
- **handoff** → update Part B, then carry this file to the next thread

### Prompt Labeling (Required)
All prompts must begin with a clear header identifying the target collaborator and be formatted as standalone code blocks for easy copy-paste:

```
SONNET — [task description]
[detailed prompt text with no extra commentary]
```

```  
OPUS — [task description]
[detailed prompt text with no extra commentary]
```

```
CURSOR — [task description] 
[detailed prompt text with no extra commentary]
```

```
TYLER — [task description]
[detailed prompt text with no extra commentary]
```

---

## PART B — SESSION CAPSULE

GPT-5 Handoff Capsule (to migrate threads)
Session: 2025-09-09T19:44:35Z

State: GREEN — monitoring baseline established; internal probe active; Windows scheduled tasks verified (daily 15:00 + 15:05 local); CI smoke JSON mode; uptime-sync workflow (interval param, default 300s) + docs; monitoring-postcheck (18:00Z) added.

What shipped:
- PR #81: monitoring minimal set reschedule + one-shot scripts (prod Sentry drop-in/test event; internal uptime probe cron; smokes).
- Windows Scheduled Tasks: “CORA Monitoring Minimal Set” (15:00 local) + “CORA Monitoring Verify” (15:05 local), both SYSTEM.
- Smoke: compact JSON summary (checks /ping and /version) and CI gate.
- External uptime: `.github/workflows/uptime-sync.yml` with `UPTIME_INTERVAL` (defaults 300s via repo/org var), docs updated (maintenance mode, interval policy).
- Postcheck: `.github/workflows/monitoring-postcheck.yml` to verify one-shot + probe log freshness at 18:00Z, artifacts uploaded.

Evidence:
- `C:\CORA\monitoring_minimal_set.log` contains “— scheduled-task verified” stamps.
- Task exports present: `C:\CORA\scheduled_task_query.txt`, `C:\CORA\scheduled_task_export.xml`.
- `docs/awareness/NOW.md`, `STATUS.md`, `AI_WORK_LOG.md`, `NEXT.md` updated with checkpoint.
- CI Smoke green; uptime-sync param set; maintenance mode block in OPERATIONS.md.

Next Action (single):
After ~24h of internal probe stability, **set `UPTIME_API_KEY_ROBOT`** and trigger `uptime-sync.yml` (workflow_dispatch) to create external monitors. Keep `UPTIME_INTERVAL=300` on free tier; switch to `60` on paid plans by setting the repo/org variable (no code changes). Ensure postcheck SSH secrets present (PROD_HOST/PROD_SSH_USER/PROD_SSH_KEY).

Operator shortcuts:
- Windows run once (manual): `schtasks /Run /TN "CORA Monitoring Minimal Set"`
- View next runs: `Get-ScheduledTaskInfo -TaskName "CORA Monitoring Minimal Set"` and `"CORA Monitoring Verify"`
- CI Smoke logs: see README badge or `gh run view --web` for the latest “Smoke” run
- External maintenance mode (UptimeRobot): see OPERATIONS.md “External Uptime – Maintenance Mode”

New-thread bootstrap (paste as first message):
> Context loaded from GPT5_handoff.md. Goal: activate external uptime after stability window and wire Slack alerts. Please confirm secrets present (UPTIME_API_KEY_ROBOT, optional SLACK_WEBHOOK_URL; PROD_* for postcheck). Then: run `uptime-sync.yml` (workflow_dispatch). After first 17:30Z window, ensure `monitoring-postcheck` passes at 18:00Z.

### Commit Protocol (Non-Negotiable)
- Every change produced by Opus/Sonnet must be committed immediately.
- GPT-5 MUST output the exact `git add/commit/push` block whenever an edit is proposed.
- No asking whether to commit; commit is assumed unless Tyler explicitly says otherwise.
- All deploys are batched—no direct prod edits unless RED.

**Canonical commit block (template):**
```bash
# Stage & commit (template; adjust paths)
git add <files>
git commit -m "<conventional message>"
git push -u origin <branch>
```

> **Post-automation sanity:** After any automated commit/PR, run the **Verify PRs/Branches** checklist in `docs/SYSTEM_RULES.md`.

## Development Workflow (Required)

1) New work always starts from a clean `main`.
2) Create a feature branch:
   - Naming: `feature/YYYY-MM-DD-<brief-task>`
3) Make focused changes (one intent per PR).
4) Commit early/often; push the branch.
5) Open a PR to `main`, let CI/guards run.
6) Merge PR (squash). Do **not** commit directly to `main` unless RED.
7) Pull `main` locally (`git pull --prune`) after merges.

### Workflow Reflection — 2025-09-01 Learnings

This session showed the system at its best:
- **Pure role boundaries:** Opus code, Sonnet docs, Cursor git, GPT-5 orchestration
- **Strict single-path prompts:** No menus, no "now or later"  
- **Add-on layering:** Refinements before execution
- **Full awareness fidelity:** NOW/NEXT/STATUS + handoff updated at every milestone
- **Deploy rhythm:** 12:30/17:30 UTC held consistently, ensuring production stayed GREEN

Success factors to preserve:
1. Never break role purity
2. Never propose multiple paths  
3. Always checkpoint before session handoff
4. Awareness docs must lead, not lag
5. Deploy only at batch windows unless RED

BI Engine established (docs/bi/*); sweeps produce evidence cards + pulse summaries; findings promoted to NEXT after human review.

### End-of-Day Close
- Append newest-on-top entry in `docs/awareness/AI_WORK_LOG.md` summarizing what landed and system health.
- Update GPT5_handoff.md "Session Capsule" with:
  - State (GREEN/YELLOW/RED)
  - What shipped today
  - **Next Action** for tomorrow (one line)
- If a branch is mid-flight, ensure it's pushed and PR is open.

### Morning Boot (Next Day)
- `git checkout main && git pull --prune`
- Create a fresh feature branch from `main` for the **one** top priority.
- Proceed with the Development Workflow steps above.

## PART B — SESSION CAPSULE
### Session: 2025-09-09T13:30Z
**State:** GREEN — service healthy, ops hardened, secrets audit complete; monitoring minimal set queued.
**What shipped:** PRs #75–79 (routes hygiene, secrets audit + untrack .env, secretless scripts, SYSTEM_RULES secrets policy, CI secrets scanning).
**Evidence:** Awareness updated; AI_WORK_LOG, STATUS, NOW, NEXT synchronized; handoff capsule logged.
**Next Action (single):** Run monitoring minimal set at 2025-09-09T15:00Z.


**Timestamp Standard (Part B):** Use **UTC ISO-8601** for all session headers, checkpoints, and capsules, e.g. `2025-09-08T12:30Z`.  
If you need to reference local time in prose, append in parentheses (America/St_Johns), but capsule keys stay UTC.

### RED Incident Mini-Template
For any **RED** capsule, append this 5-line block:

- **Root cause:**  
- **Impact:**  
- **Mitigation:**  
- **Evidence:**  
- **Next Action (single):**  

(Keep it to one screen; link to logs/PRs in Evidence.)

### Session: 2025-09-09T00:00Z
**State:** YELLOW — Section 2 auth not executed (API-only policy today).
**What simulated:** Unauth probe + local smokes; no login/PATCH.
**Evidence:** AI_WORK_LOG.md entry (probe result + smokes note).
**Next Action (single):** Seed a test user via scripted path in next GREEN session, then re-run Section 2.

### Session: 2025-09-08T12:30Z
**State:** GREEN — prod healthy; smokes pass
**What shipped:** No app code; ops cleanup restored service (freed ~19G under /var/backups/cora/system)
**Evidence:** /health 200, /api/status 200, /api/feature-flags 401
**Next Action (single):** Renew TLS (install certbot or run manual renew) before 2025-09-19

### Session: 2025-09-06T00:00Z
**State:** GREEN — prod healthy; status/health 200
**What shipped:** Hotfixes applied: `ErrorHandler()` no-arg init; corrected `ErrorHandler.log_error(request, exception)` call; auth guard after `authenticate_user`; compatibility alias `PDFExporter = ProfitIntelligencePDFExporter`; added `users.currency` (idempotent) migration; removed large old `/var/backups/cora/system` tars to resolve disk-full
**Evidence:** Front-door `/api/status` 200 and `/health` 200; unauth `/api/user/settings` → 401; login sets cookie and allows settings GET/PATCH (values persist)
**Next Action (single):** Merge and deploy PR #73 (hotfix), then confirm no repo/server drift

### Session: 2025-09-04T00:00Z
**State:** RED — prod returning 502 (service not starting); ErrorHandler ctor + PDF exporter import issues; disk ~98% full.
**What shipped:** PR #70 merged (prefs: `/api/user/settings` GET/PATCH, currency field, tz-aware exports) + router refactor passes guards; CI green.
**Evidence:** Walkthrough S1 Steps 1–7 captured; defects A-RESET-500, A-LOGIN-TIMEOUT, A-LOGIN-SLOW-60S, A-LOGIN-RATELIMIT-OK, A-LOGIN-RETRY-MISMATCH logged in audit doc.
**Next Action (single):** Morning 3-step recover (vacuum logs; print traceback via `journalctl` or direct `import app`; apply minimal import fix), then run Step 8 smokes (401, auth GET/PATCH, re-GET).

### Session: 2025-09-03T00:00Z
**State:** GREEN (Postgres)
**Shipped Today:**
- Prod DB cutover SQLite→Postgres (transactional), parity verified
- Validator cast hardening (orphan checks clean)
- Canonical smoke harness + runbook
- Manual walkthrough scaffold
- Nightly Postgres backups + restore verify
**Acceptance:** `/api/status` 200; smokes GREEN; DSN in `/root/CORA_PROD_PG_DSN.env`; artifacts in `/var/log/cora_migration/`
**Next Action (single):** Manual Walkthrough — Section 1 (Auth & Session): run steps, capture evidence; then queue Section 2.

### Prompt Labeling (Reminder)
All prompts MUST start with a header naming the actor (SONNET / OPUS / TYLER / CURSOR) and be in their own code block. No mixed-actor blocks.

### Command Cheatsheet (keep here for Tyler)
- Create branch: `git checkout -b feature/YYYY-MM-DD-<task>`
- Stage+commit: `git add -A && git commit -m "<type>(scope): <message>"`
- Push: `git push -u origin $(git rev-parse --abbrev-ref HEAD)`
- Open PR: `gh pr create --fill --base main --head $(git rev-parse --abbrev-ref HEAD)`
- Merge PR: `gh pr merge <#> --squash --delete-branch` (or `--admin` if policy allows)
- Sync main: `git checkout main && git pull --prune`

---
**Runbooks:** See `docs/runbooks/DEPLOY.md` for deploy steps and `docs/runbooks/SMOKES.md` for canonical smokes.
---

### Roles & Rules
- **Tyler**: intent, runs labeled commands, merges PRs.
- **GPT-5 (orchestrator)**: plan, delegate, prompts, scope guard. Prompts clearly labeled per standard. One path only.
- **Sonnet (AUDITS/INTEL-ONLY)**: audits, docs, JSON gap inventories, codebase search & file finding. No code changes.
- **Cursor (PRIMARY EXECUTOR)**: code changes, refactors, tests, migrations, git/PR/deploy orchestration.

**Golden rules:**
1) Delegate-first, concurrency OK if scopes don't overlap.
2) Money-path first.
3) Awareness is append-only; newest on top.
4) Everything via PRs (even docs). No prod edits unless RED.
5) No decision trees for routine ops. If protocol defines a path, follow it without asking.

**Focus Rule — One Capsule at a Time:** pick ONE item from NOW/NEXT, finish it, `checkpoint`, then move on.

### Where things go
- **Audits:** `docs/ai-audits/YYYY-MM-DD/` (report.md, audit.json, now_next_patch.md)
- **Awareness:** `docs/awareness/NOW.md`, `NEXT.md`, `REGISTRY.yml`, `LOST_AND_FOUND.md`

### Modes
- **GREEN:** plan → delegate → PR → merge  
- **RED:** freeze deploys, capture logs, minimal fix, restore GREEN

### Batch Deploy Policy
Deploys are batched at 12:30 and 17:30 UTC. Commits land continuously; production pulls happen in these windows unless RED.

### DoD
- **Audit (Sonnet):** `mvp_audit_report.md`, `mvp_audit.json`, `landing_status.md`, `now_next_patch.md`, plus REGISTRY/LOST_AND_FOUND snippets.  
- **Build (Opus):** P0 money-path files, tiny store, routers, tests.  
- **Awareness (Tyler):** append NOW/NEXT, REGISTRY, LOST_AND_FOUND; open & merge PR.

### Standard Prompts (abbrev references)
- **Sonnet Audit Prompt** → inventories implemented vs gaps and emits all artifacts.
- **Opus Implementation Prompt** → implements P0 items with routes/templates/tests.

### Workflow and Collaboration — Capabilities

### Workflow Reflection — 2025-09-01 Session Learnings

This session demonstrated an exemplary workflow cadence. The following principles are now considered best practice:

1. **Role purity** — Opus = code, Sonnet = docs, Cursor = git/deploy, GPT-5 = orchestrator.  
2. **One-path discipline** — GPT-5 proposes a single next action, not a menu.  
3. **Add-on layering** — clarifications and strategic notes appear before execution prompts.  
4. **Awareness fidelity** — every shipped change logged across AI_WORK_LOG, STATUS, NEXT, GPT5_handoff.  
5. **Batch deploy rhythm** — deploys only at 12:30 / 17:30 UTC, maintaining cadence.  
6. **Deferred manual checks allowed** if explicitly documented in awareness files.  
7. **Shared North Star** — finish MVP list first, then audit, then refresh NEXT priorities.

This reflection is permanent. Future sessions should emulate this pattern unless explicitly overridden. This workflow is evidence that the long effort to tune awareness and sync has succeeded.

I spoke to Opus like you should have and this was our conversation:

> quick question, if you cannot actually push code to my git repo, how much can you do on your end? and can cursor push it to my git repo?

● Great question! Here's what I can and cannot do:

**What I CAN do:**
- Modify all files locally — Complete implementation ready to deploy
- Run and verify tests — Confirmed all scenarios work
- Document everything — Full PR description with test matrix ready

**What I CANNOT do:**
- Git operations — No git init, add, commit, or push
- Create actual GitHub PR — Can't interact with GitHub
- Deploy to production — Can't SSH or restart services

**What Cursor CAN do for you:**
Yes, Cursor can handle all the git operations! Here's the workflow:

```bash
# Initialize git if needed
git init
git add routes/pages.py web/templates/pricing.html tests/test_pricing_cta.py
git add docs/ai-audits/2025-08-30/*.md docs/awareness/LOST_AND_FOUND.md

# Commit with conventional message
git commit -m "feat(pricing): CTAs use Stripe Payment Links with /signup fallback

- Pass PAYMENT_LINK env vars from route to template
- Template uses payment links when set, /signup?plan=X fallback otherwise
- Remove JavaScript checkout modal to prevent errors
- Add comprehensive test coverage for all scenarios
- Document production Stripe Payment Link URLs

Test matrix verified:
- No env vars → /signup fallback ✓
- Specific links → Stripe URLs ✓
- Generic link → applies to all ✓
- Mixed config → correct behavior ✓"

# Push to GitHub
git push origin main  # or create feature branch first

# Create PR via GitHub CLI
gh pr create --title "feat(pricing): CTAs use Stripe Payment Links with /signup fallback" --body "..."
```

TL;DR: Opus does 100% of the code work. You (through Cursor or another git client) must commit and push the changed files. The implementation is complete and tested — ready to ship.

---


### Session: 2025-09-03 (UTC)
**State:** GREEN — prod running on **Postgres**; health 200; admin seeded; migration artifacts saved on prod.
**What shipped:** Phase 3 cutover + Phase 4 validation; awareness updated.
**Next Action (single):** Patch validator to cast types in orphan checks and re-run db_introspect.py against Postgres.

### GPT-5 Handoff → Opus

#### Context
- Current work: stabilizing CORA prod FastAPI app (`cora.service` on Ubuntu 24.10).  
- Location: `/var/www/cora/` on `root@cora-ai-prod`.  
- Service is stuck in restart loops due to missing router imports.  
- Recent blockers:  
  - `weekly_insights_router` not defined → stub added at `routes/weekly_insights.py`.  
  - `settings_router` not defined → stub added at `routes/settings.py`.  
  - Even with stubs, `app.py` still references these routers before they're defined.  
- Result: health probes return `000` (service down).  

#### Goal
Ensure `app.py` reliably imports **all routers** before calling `app.include_router(...)`, so that:
- `cora.service` starts cleanly.
- Health check (`curl 127.0.0.1:8000/`) returns **200** (OK) or **401** (unauthorized).  
- Ready state achieved for next step: user seeding + DB migration.

#### Tasks for Opus
1. Inspect `app.py`:  
   - Find all `app.include_router(...)` calls.  
   - Confirm corresponding imports (`from routes.<file> import <router>`) exist *above*.  
   - Add or reorder imports as needed.  
   - Keep stub fallback imports at top if necessary.  
2. Backup before editing:  
   ```bash
   cp app.py app.py.bak.$(date +%Y%m%d_%H%M%S)
   ```
3. Patch app.py incrementally (don't overwrite file wholesale).
4. Restart and probe:
   ```bash
   systemctl restart cora.service
   sleep 2
   curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:8000/
   ```
5. Confirm service is active (no restart loop).

#### Acceptance
- cora.service stays running.
- No NameError for settings_router or weekly_insights_router.
- Health probe shows 200 or 401.
- System ready to move to auth seeding + DB migration.

### Session: 2025-09-02 (UTC)
**North Star:** Lock BI intelligence loop; keep awareness current.
**State:** BI snapshot tool hardened + tagged (v0.1.0-bi-snapshot-hardened); first run captured 5 OK / 2 ERR (QBO timeouts, Jobber 403); error artifacts cached; awareness docs updated.
**System Health:** GREEN
**Next Action (single):** AM — Comprehensive Manual Walkthrough; then add QBO/Jobber manual_notes placeholders and schedule weekly snapshot.

### Session: 2025-09-01 15:30 UTC
**Shipped:**
- Weekly Insights 3/5/3 validation (PR #38)
- Unsubscribe link + opt-in/opt-out for weekly insights emails (PR #40)
- Deploy: GREEN; smokes 200/200
**System Health:** GREEN
**Notes:** Manual checklist walkthroughs skipped by intent; full review will happen once core MVP tasks are done.
**Next Action (single):** Split `export_manager.js` (<300 lines) to satisfy pre-commit guard.

### Session: 2025-09-01 (America/St_Johns)
**North Star:** MVP quick wins, flow unblocked.

**Shipped**
- PR #36 merged: standardize CSV export filenames to `cora_{type}_{email}_{YYYYMMDD}.csv` (timezone-aware)
- Files: `utils/filenames.py`, `web/static/js/export_manager.js`, `tests/test_export_filenames.py`
- Deployed via batch window; smokes passed (health 200, api/status 200)

**State**
- Timezone selection fully implemented and verified (tests/test_filenames_tz.py)
- Deploy procedure is one-command (.\deploy)
- Awareness log updated

**System Health:** GREEN

**Next Action (single):**
Data validation quick win:
- Add weekly checks service and minimal thresholds
- Surface validation in UI; add minimal tests

### Session: 2025-08-30 (America/St_Johns)
**North Star:** Ship money-path features from a clean, protected awareness baseline.

**State**
- Main is clean; PR #19 merged (squash). Guards active and passing.
- Checkpoint logs redirected → `docs/awareness/CHECKPOINT_LOG.md`.
- Awareness corpus stable; `AI_WORK_LOG.md` carries human work entries only.

**System Health:** GREEN

**Next Action:** Create fresh branch from `main` for today's focus per MVP priorities.

**Handoff Note**
Carry this file forward next thread; update the Session Capsule only.

