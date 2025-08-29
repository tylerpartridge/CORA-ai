# GPT5_handoff.md

> One file to carry between threads.  
> **Part A (Stable Playbook)** stays stable.  
> **Part B (Session Capsule)** is the only section you update each thread.

---

## PART A — STABLE PLAYBOOK (ESSENTIALS)

### Hotkeys
- **save** → lightweight snapshot (append minimal awareness log)
- **checkpoint** → full milestone capture (NOW, NEXT, REGISTRY, LOST_AND_FOUND updated)
- **hydrate** → reload state when starting a fresh thread
- **TodoWrite** → required for any 2+ step task (forces a checklist doc)
- **handoff** → update Part B, then carry this file to the next thread

### Roles & Rules
- **Tyler**: intent, runs labeled commands, merges PRs.
- **GPT-5 (orchestrator)**: plan, delegate, prompts, scope guard.
- **Sonnet (READ-ONLY)**: audits, docs, JSON gap inventories, copy.
- **Opus (CODE-ONLY)**: FastAPI features, routes, tests, minimal diffs.

**Golden rules:**  
1) Delegate-first, concurrency OK if scopes don’t overlap.  
2) Money-path first: Payment → Upload → Generate → View → Outreach.  
3) Awareness is append-only; newest on top.  
4) Everything via PRs (even docs). No prod edits unless RED.

**Focus Rule — One Capsule at a Time:** pick ONE item from NOW/NEXT, finish it, `checkpoint`, then move on.

### Where things go
- **Audits:** `docs/ai-audits/YYYY-MM-DD/` (report.md, audit.json, now_next_patch.md)
- **Awareness:** `docs/awareness/NOW.md`, `NEXT.md`, `REGISTRY.yml`, `LOST_AND_FOUND.md`

### Modes
- **GREEN:** plan → delegate → PR → merge  
- **RED:** freeze deploys, capture logs, minimal fix, restore GREEN

### DoD
- **Audit (Sonnet):** `mvp_audit_report.md`, `mvp_audit.json`, `landing_status.md`, `now_next_patch.md`, plus REGISTRY/LOST_AND_FOUND snippets.  
- **Build (Opus):** P0 money-path files, tiny store, routers, tests.  
- **Awareness (Tyler):** append NOW/NEXT, REGISTRY, LOST_AND_FOUND; open & merge PR.

### Standard Prompts (abbrev references)
- **Sonnet Audit Prompt** → inventories implemented vs gaps and emits all artifacts.
- **Opus Implementation Prompt** → implements P0 items with routes/templates/tests.

---

## PART B — SESSION CAPSULE (UPDATE EACH THREAD; NEWEST FIRST)

### Session: 2025-08-29  (Timezone: America/St_Johns)
**North Star:** Finish MVP partials on money-path; keep CI GREEN.

**Repo / Branch**
- Repo: cora (main at 09efd3e)
- Branch: `chore/2025-08-29-archive-sonnet-handoff` (status: GREEN)
- CI: green; Notes: {…}

**Facts (quick)**
- Landing: {repo|external}; CTA → {PaymentLink|Missing}
- Stripe presence: payment_link {yes/no}, price_ids {yes/no}, webhook_secret {yes/no}
- Routes: billing {y/n}, webhook {y/n}, upload {y/n}, reports {y/n}, pricing {y/n}, healthz {y/n}

**P0 (must do)**
1) Archive Sonnet milestone handoff without breaking 300-line rule (SPLIT ✅).
2) Restore canonical `GPT5_handoff.md` at root (this file).
3) Proceed to close remaining MVP partials (money-path).

**P1/P2**
- P1: Final production end-to-end test sweep.
- P2: Beta onboarding helpers (calendly, tips page).

**Decisions Needed**
- None (today’s scope is housekeeping + unblock MVP).

**Awareness Updates**
- NOW.md (top-append): {yes/no}
- NEXT.md (top-append): {yes/no}
- REGISTRY.yml (append): {yes/no}
- LOST_AND_FOUND.md (append): {yes/no}

**Next Actions**
- SONNET: not needed
- OPUS: pending P0 items from audit (money-path only)
- TYLER: open PR with archive + baton restore; merge when CI green

**Handoff Note**
Carry this file forward next thread; update the Session Capsule only.
