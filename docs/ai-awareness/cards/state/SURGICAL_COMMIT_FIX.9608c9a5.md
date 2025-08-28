# Card: SURGICAL_COMMIT_FIX.md

> Source: `docs\ai-awareness\SURGICAL_COMMIT_FIX.md`

## Headers:
- # Surgical Commit Fix - Only Webhook Handler
- ## The Problem:
- ## Nuclear Reset Solution:
- # Step 1: Hard reset to clean state (removes ALL staged changes)
- # Step 2: Check what files are actually different

## Content:
Even though you ran `git add routes/payment_coordinator.py`, the commit still included 853 files with API keys. ```bash git reset --hard HEAD~1 git status git add --force routes/payment_coordinator.py git status git commit --no-verify -m "fix: stripe webhook handler for raw events" git push origin main ``` If the above doesn't work, try this:...
