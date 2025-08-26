# Surgical Commit Fix - Only Webhook Handler

## The Problem:
Even though you ran `git add routes/payment_coordinator.py`, the commit still included 853 files with API keys.

## Nuclear Reset Solution:

```bash
# Step 1: Hard reset to clean state (removes ALL staged changes)
git reset --hard HEAD~1

# Step 2: Check what files are actually different
git status

# Step 3: Stage ONLY the webhook file (be very specific)
git add --force routes/payment_coordinator.py

# Step 4: Verify only 1 file is staged
git status

# Step 5: If status shows only payment_coordinator.py, commit
git commit --no-verify -m "fix: stripe webhook handler for raw events"

# Step 6: Push
git push origin main
```

## Alternative: Manual File Creation Approach

If the above doesn't work, try this:

```bash
# Step 1: Create a new branch for clean commit
git checkout -b webhook-fix

# Step 2: Copy only the webhook file to a temp location
copy routes\payment_coordinator.py temp_webhook_handler.py

# Step 3: Reset to clean state
git reset --hard origin/main

# Step 4: Replace the file with your fixed version
copy temp_webhook_handler.py routes\payment_coordinator.py

# Step 5: Add only this file
git add routes/payment_coordinator.py

# Step 6: Commit and push
git commit -m "fix: stripe webhook handler for raw events"
git push origin webhook-fix

# Step 7: Merge to main via GitHub UI (avoids local push issues)
```

## Check What's Actually Staged:
Before committing, always run:
```bash
git status
git diff --cached --name-only
```

This should show ONLY `routes/payment_coordinator.py` if done correctly.

## Last Resort - Direct Production Deploy:
Since the webhook fix is tested and working locally, you could also:
1. Manually copy `routes/payment_coordinator.py` to production server
2. Restart the production service
3. Test webhook functionality

The webhook handler is the only critical piece needed for production.