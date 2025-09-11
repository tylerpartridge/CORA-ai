# 📁 MANDATORY FILE OPERATION WORKFLOW

Note: Rules SSOT is docs/SYSTEM_RULES.md. This file focuses only on the step-by-step workflow and visible checklist.

## The ONLY Acceptable Pattern:

### Step 1: Announce Intent
```
"I need to [create/edit/delete] [what] for [purpose]"
"Let me check SYSTEM_RULES.md first..."
```

### Step 2: Execute Checklist (VISIBLE)
```
"[ ] 1. Checking SYSTEM_RULES.md..." [ACTUALLY READ IT]
"[ ] 2. Searching for existing: [search query]..." [SHOW RESULTS]
"[ ] 3. Verifying directory..." [STATE WHICH ONE]
"[ ] 4. Edit vs Create Decision..." 
       "     - Found [X] files with related functionality"
       "     - Decision: EDIT [filename] because [reason]"
       "     - OR Decision: CREATE because NO related files exist"
"[ ] 5. Announcing: Creating/Editing [file] in [dir]"
"[ ] 6. Pre-flight complete. Proceeding."
```

### Step 3: Execute Operation
Only AFTER all checklist items are complete

## 🚨 AUTOMATIC FAILURE CONDITIONS:
- Creating file without checklist = STOP
- "Let me create..." without checking = STOP
- "I'll add this to..." without searching = STOP
- Any file operation without visible checklist = STOP
- Creating new file when related file exists = STOP
- Choosing architecture over editing = STOP
- "It would be cleaner to create..." = STOP

## ✅ EXAMPLE OF CORRECT WORKFLOW:
```
User: "Add a formatter function"

AI: "I need to create a formatting function.
Let me check SYSTEM_RULES.md first...

[ ] 1. Checking SYSTEM_RULES.md... ✓ (no utils.py, check existing files)
[ ] 2. Searching for existing format functions... ✓ 
      Found: routes/display.py handles display logic
[ ] 3. Verifying directory... ✓ (routes/ has the display code)
[ ] 4. Edit vs Create Decision... ✓
      - Found 1 file with related functionality
      - Decision: EDIT display.py because it handles display
[ ] 5. Announcing: Editing routes/display.py
[ ] 6. Pre-flight complete. Proceeding.

Now editing routes/display.py..."
```

## 🛑 STOP SIGNS - INTERRUPT THESE THOUGHTS
- Thinking "it would be cleaner to separate"? → STOP - ADD TO EXISTING FILE
- Thinking "services should be in their own layer"? → STOP - ADD TO EXISTING FILE  
- Thinking "this deserves its own module"? → STOP - ADD TO EXISTING FILE
- Thinking "better architecture would be..."? → STOP - ADD TO EXISTING FILE
- Thinking "following MVC/clean architecture"? → STOP - ADD TO EXISTING FILE

---
**NO SHORTCUTS. NO EXCEPTIONS. CHECKLIST EVERY TIME.**
