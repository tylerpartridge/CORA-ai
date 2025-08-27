# GPT5\_handoff.md

> One file to carry between threads.
> **Part A (Stable Playbook)** never changes.
> **Part B (Session Capsule)** is the only section you update each thread.

---

## PART A — STABLE PLAYBOOK (DON'T CHANGE)

### Tyler's Hotkeys (AI must respect)
- **save** → lightweight snapshot.
  *When:* minor progress worth persisting (e.g. Sonnet just finished an audit, or Opus produced a small PR).
  *Effect:* Append to awareness files, minimal log.

- **checkpoint** → full milestone capture.
  *When:* major progress (e.g. audit complete, PR merged, or trial model decision).
  *Effect:* Awareness spine fully updated (NOW, NEXT, REGISTRY, LOST_AND_FOUND), context re-synced, "truth-data" guaranteed.

- **hydrate** → reload state.
  *When:* new thread starts or after drift, to re-seed Sonnet/Opus with context.

- **TodoWrite** → mandatory if task spans 2+ steps.
  *When:* I give Sonnet/Opus a job that touches multiple files or subtasks.
  *Effect:* Forces them to write into a clear TodoWrite doc (ensures no step is skipped or lost).

- **handoff** → (implicit, not typed by them).
  *When:* end of a thread, or when passing baton between Sonnet/Opus.
  *Effect:* I ensure Part B of /GPT5_handoff.md is updated, then you copy it to the next thread.

---

### 1) Working Model (delegate-first)

* **Tyler**: sets intent, runs only clearly labeled "TYLER" blocks, pastes outputs, merges PRs.
* **GPT-5 (orchestrator)**: plans, writes prompts, routes work, produces paste-ready artifacts, guards scope.
* **Sonnet**: **READ-ONLY** audits & content (reports, docs, JSON gaps, copy).
* **Opus**: **CODE-ONLY** implementation (FastAPI routes, templates, tests) from Sonnet's P0 gaps.

**Golden rules**

1. **Concurrency allowed (GPT-5 orchestrated).** Default single-AI; GPT-5 may run Sonnet/Opus in parallel when scopes don't overlap. GPT-5 owns juggle/merge and prevents conflicting edits.
2. **Money-path first.** Payment → Upload → Generate → View → Outreach.
3. **Append-only awareness.** We never rewrite history; newest blocks go on top.
4. **PRs for everything.** Even docs. No direct prod edits unless RED mode.

**Concurrency guardrails**
- Separate scopes: Sonnet read-only vs Opus write-only, or different dirs/branches.
- No overlapping edits in the same files/PR; if needed, serialize.
- Clear file ownership & filenames (dated folders for artifacts).
- Rollback rule: audit truth wins; implementations rebase on audit if conflicts arise.

### Focus Rule — One Capsule at a Time
Every working AI (Sonnet, Opus, GPT-5) must operate in a closed loop:
- Pick exactly ONE item from NOW.md or NEXT.md capsule.
- Work only on that item until it is complete.
- Call for a `checkpoint` once complete.
- Do not drift or expand scope; park all other issues into NEXT.md or LOST_AND_FOUND.md.
- Resume only after the checkpoint is logged.

This ensures that work is finished, logged, and stable before moving on.

---

### 1a) User Flow v2 (Card-Upfront, 30-day Stripe trial)

1) /pricing → "Start 30-day free trial (no charge today)" → Stripe Payment Link (card required).
2) Stripe success redirect → Onboarding form (Typeform/Google Form/Notion).
3) We prepare the first report within 7–10 days.
4) Review call (retention-focused): ensure value, reduce cancellations before day 30. Stripe auto-bills on day 30 unless canceled.

Pilot fallback (no card) is allowed for special cases; if used, schedule review within 72h to convert.

**Trial Models (A/B) — Pros & Cons (1-liner each)**
- A) No-card trial → more signups, low paid conversion, heavy manual follow-up.
- B) Card-upfront trial → fewer signups, higher paid conversion, predictable billing.

---

### 2) Where things go

* **Audits:** `docs/ai-audits/YYYY-MM-DD/` (report.md, audit.json, landing\_status.md, now\_next\_patch.md).
* **Awareness spine:**

  * `docs/awareness/NOW.md` (today's north star + 3 actions, newest on top)
  * `docs/awareness/NEXT.md` (5–7 tasks, P0/P1/P2, newest on top)
  * `docs/awareness/REGISTRY.yml` (presence flags, masked tails only)
  * `docs/awareness/LOST_AND_FOUND.md` (facts with no home)

---

### 3) Modes

* **GREEN** (normal): plan → delegate → paste → PR → merge.
* **RED** (incident): freeze deploys, capture logs, minimal diffs, restore GREEN, then resume plan.

---

### 4) Definition of Done (DoD)

* **Audit DoD (Sonnet):**

  * `mvp_audit_report.md`, `mvp_audit.json` (with P0/P1/P2), `landing_status.md`,
    `now_next_patch.md`, and snippets for `REGISTRY.yml` & `LOST_AND_FOUND.md`.
  * All internally consistent and tied to money-path.
* **Build DoD (Opus):**

  * P0 items implemented with minimal code: routes, tiny store, templates, test (gated).
  * `include_router` notes included. No secrets in code.
* **Awareness DoD (Tyler):**

  * NOW/NEXT updated (top-append), REGISTRY/LOST\_AND\_FOUND appended, PR opened and merged.

---

### 5) Command & PR etiquette

* Branch names: `audit/YYYY-MM-DD-truth-pass`, `feature/YYYY-MM-DD-money-path`.
* Commit messages: `feat: money-path P0 routes` / `docs: Sonnet audit + awareness`.
* Never run unlabelled commands. GPT-5 will **always** give copy-paste blocks labeled **TYLER**.

---

### 5a) Terminal targets & navigation (always labeled)
- **LOCAL (Cursor PowerShell venv):** `(venv) PS C:\CORA>` — use for git add/commit/push, editing files, running pytest.
- **PROD (DigitalOcean web console):** use the Droplet's **Console** or `ssh root@coraai.tech` — use for editing `.env`, `systemctl restart`, `curl` health checks.
- **GITHUB (web):** go to `https://github.com/tylerpartridge/CORA-ai` → **Pull requests** → **New pull request** → base: `main`, compare: `<your-branch>` → **Create pull request**.
- **STRIPE (web):** dashboard.stripe.com → **Payment links** (or **Products → Price**) → copy your Payment Link.
**Instruction blocks convention:** I (GPT-5) will prefix steps like **TYLER — LOCAL**, **TYLER — PROD**, **TYLER — GITHUB**, **TYLER — STRIPE** so location is always obvious.

---

### 6) Standard Prompts (paste verbatim when asked)

#### 6.1 Sonnet — Audit Prompt (READ-ONLY)

```
Role: Senior Product & QA Auditor (READ-ONLY) for CORA "Profit Pulse"
Goal: Inventory what exists vs the money path and return paste-ready docs & awareness updates.

Focus: Payment (Stripe), Upload CSVs, Generate report (HTML+JSON), View latest.

Deliverables (write full contents):
1) docs/ai-audits/{DATE}/mvp_audit_report.md
   Sections: Exec Summary; Implemented (by file/route); Gaps; Risks; 1-Week Priority; DoD checklist.
2) docs/ai-audits/{DATE}/mvp_audit.json
   [{ id, title, required_by: ["payment"|"upload"|"generate"|"view"], implemented_in: [paths], gap, risk, recommendation, priority: "P0"|"P1"|"P2" }]
3) docs/ai-audits/{DATE}/landing_status.md
   Where landing lives (repo vs external). CTA wired to Stripe? If missing, include minimal templates/pricing.html using env var PAYMENT_LINK.
4) docs/ai-audits/{DATE}/now_next_patch.md
   ### NOW ({DATE}) -> 1-sentence north star + 3 actions (≤90 min total)
   ### NEXT ({DATE}) -> 5–7 tasks (15–60 min), label P0/P1/P2
5) Awareness snippets (append-only):
   - REGISTRY.yml: presence flags (stripe.payment_link_present, price_ids_present, webhook_secret_present), routes_present {billing, webhook, upload, reports, pricing, healthz}, landing {kind, path_or_url}
   - LOST_AND_FOUND.md: bullets of orphan facts

Redaction: no secrets; only presence or masked tails (last 6 + sha8). Be concrete with paths/routes.
Acceptance: All artifacts complete and consistent with the repo you can read.
```

#### 6.2 Opus — Implementation Prompt (CODE-ONLY)

```
Role: Senior FastAPI Engineer
Inputs: P0 items from docs/ai-audits/{DATE}/mvp_audit.json

Deliverables (full file contents):
1) app/routes/billing.py  (checkout session if used; webhook handler marks user "paid")
2) app/routes/upload.py   (POST /onboarding/upload, saves CSVs under uploads/{user_id}/)
3) app/routes/reports.py  (POST /reports/generate calls reports/generate.py; GET /reports/latest serves HTML)
4) app/routes/pages.py    (GET /pricing, GET /reports)
5) app/core/settings.py   (Pydantic env: STRIPE_* , UPLOADS_DIR, REPORTS_DIR)
6) app/models/state_store.py (tiny JSON store)
7) templates/pricing.html + templates/reports_latest.html (minimal HTML)
8) tools/run_report.py    (CLI for local generate)
9) tests/test_reports_flow.py (gated by env; temp dirs; stub generator)

Include: where to `include_router` in app, and TODOs if decisions are needed.
Constraints: No secrets in code. Keep concise. Dependencies: fastapi, pydantic, stripe, pandas, jinja2.
Acceptance: Files compile in principle; satisfy P0 money path.
```

---

### 7) Session Ritual (always the same)

**Start a thread**

1. Paste **Part B** from last thread.
2. If auditing: dispatch **Sonnet** with the standard prompt (date filled).
3. Update awareness using Sonnet's `now_next_patch.md` and snippets.
4. If building: dispatch **Opus** with **only** Sonnet's **P0** list.

**End a thread**

* Append a fresh **Part B** (updated), copy file to new thread, and continue.

---

## PART B — SESSION CAPSULE (UPDATE THIS SECTION EACH THREAD)

> Fill the placeholders; keep old capsules below this one (append-only, newest first).

### Session: 2025-08-27  (Timezone: America/St\_Johns)

**North Star:** Lock card-upfront trial; ensure /pricing CTA goes to Stripe; redirect to onboarding.

**Repo / Branch**

* Repo: cora (main at {short\_commit})
* Working branch: `{branch_name}`  (status: GREEN)
* CI: {green/yellow/red}; Notes: {…}

**Facts (quick)**

* Landing: repo — `web/templates/index.html`; CTA → Missing link (per audit)
* Stripe presence: payment\_link no, price\_ids yes, webhook\_secret no, trial_model = "card_upfront_30d"
* Routes present: billing y, webhook y, upload y, reports y, pricing y, healthz y
* Generator assets: reports/generate.py y, templates/report.html y

**P0 (must do)**

1. Stripe Payment Link with 30-day trial + success redirect URL set.
2. /pricing Solo CTA points to that Stripe link.
3. Onboarding form captures company, CSV/Drive link, goals; confirmation shows "Book review" (Calendly).

**P1/P2 (later)**

* P1: {…}
* P2: {…}

**Decisions Needed**

* Keep $149 setup as separate later step? (default: later).

**Awareness Updates (applied?)**

* NOW\.md (top-appended): applied: yes
* NEXT.md (top-appended): applied: yes
* REGISTRY.yml (appended): applied: yes
* LOST\_AND\_FOUND.md (appended): applied: yes

**Next Actions**

* SONNET: done
* OPUS: COMPLETE ✅ (all 8 P0 deliverables implemented)
* TYLER: copy implementation files, set Stripe env vars, deploy

**Handoff Note for Next Thread**

* Carry this Part B forward. Keep Part A unchanged.

---

### Session: {DATE}  (Timezone: America/St\_Johns)

**North Star:** {one sentence — e.g., "Ship the money path for 3 paid pilots."}

**Repo / Branch**

* Repo: cora (main at {short\_commit})
* Working branch: `{branch_name}`  (status: {GREEN|RED})
* CI: {green/yellow/red}; Notes: {…}

**Facts (quick)**

* Landing: {repo|external} — {path\_or\_url}; CTA → {PaymentLink|PriceID|Missing}
* Stripe presence: payment\_link {yes/no}, price\_ids {yes/no}, webhook\_secret {yes/no}
* Routes present: billing {y/n}, webhook {y/n}, upload {y/n}, reports {y/n}, pricing {y/n}, healthz {y/n}
* Generator assets: reports/generate.py {y/n}, templates/report.html {y/n}

**P0 (must do)**

1. {P0 item 1}
2. {P0 item 2}
3. {P0 item 3}

**P1/P2 (later)**

* P1: {…}
* P2: {…}

**Decisions Needed**

* {short list of open decisions, or "None"}

**Awareness Updates (applied?)**

* NOW\.md (top-appended): {yes/no}
* NEXT.md (top-appended): {yes/no}
* REGISTRY.yml (appended): {yes/no}
* LOST\_AND\_FOUND.md (appended): {yes/no}

**Next Actions**

* SONNET: {run/not needed} — if run, link to audit files.
* OPUS: {pending/underway} — scope = P0 list above.
* TYLER: {copy-paste tasks only — e.g., open PR, paste templates, run CI}

**Handoff Note for Next Thread**

* Carry this Part B forward. Keep Part A unchanged.