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

### Roles & Rules
- **Tyler**: intent, runs labeled commands, merges PRs.
- **GPT-5 (orchestrator)**: plan, delegate, prompts, scope guard. **As orchestrator you must always be clear in prompts which collaborator (Sonnet, Opus, Cursor, Tyler) is intended to act. Each prompt must be a single copy-paste code block.**
  - When providing next actions, GPT-5 MUST give a single recommended path forward (no multiple-choice). Always choose one direction based on best judgment and evidence.
- **Sonnet (READ-ONLY)**: audits, docs, JSON gap inventories, copy.
- **Opus (CODE-ONLY)**: FastAPI features, routes, tests, minimal diffs.
- **Cursor**: Git operations (init, add, commit, push), can push to GitHub repo.

**Golden rules:**  
1) Delegate-first, concurrency OK if scopes don't overlap.  
2) Money-path first: Payment → Upload → Generate → View → Outreach.  
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

## PART B — SESSION CAPSULE (UPDATE EACH THREAD; NEWEST FIRST)

### Session: 2025-08-29  (Timezone: America/St_Johns)
**North Star:** Resume MVP partials completion; awareness ops locked.

**Repo / Branch**
- Repo: cora (main at b2d9478)
- Branch: main (merged chore/2025-08-29-archive-sonnet-handoff)
- CI: GREEN ✅ (all builds passing)

**Facts (quick)**
- Landing: repo; CTA → Stripe link/CTA (pending)
- Stripe presence: webhook_secret yes, payment_link needs implementation, price_ids need review
- Routes: billing y/n, webhook y, upload pending, reports y, pricing pending, healthz y

**P0 (must do)**
1) ✅ Archive Sonnet milestone handoff (COMPLETED - commit b2d9478).
2) ✅ Restore canonical `GPT5_handoff.md` at root (COMPLETED).
3) Resume MVP partials (money-path: Stripe link/CTA, upload/generate/view).

**P1/P2**
- P1: Final production end-to-end test sweep after MVP partials.
- P2: Beta onboarding helpers (calendly, tips page).

**Decisions Needed**
- Focus on 12 remaining MVP partial items from MVP_REQUIREMENTS.md

**Awareness Updates**
- NOW.md (checkpoint capsule): ✅ YES
- NEXT.md (checkpoint capsule): ✅ YES  
- AI_WORK_LOG.md (checkpoint capsule): ✅ YES
- AI_DISCUSSION_SPACE.md (checkpoint capsule): ✅ YES
- STATUS.md (checkpoint capsule): ✅ YES

**Next Actions**
- SONNET: awareness ops COMPLETE/LOCKED - do not reopen
- OPUS: resume MVP partials implementation (money-path focus)
- TYLER: merge confirmed complete, ready for next MVP sprint phase

**Handoff Note**
Carry this file forward next thread; update the Session Capsule only.
