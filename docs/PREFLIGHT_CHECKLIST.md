# ✈️ MANDATORY PRE-FLIGHT CHECKLIST

## STOP! Before ANY File Operation:

### 📋 THE CHECKLIST (Must Complete IN ORDER)
```
[ ] 1. TYPE: "Checking SYSTEM_RULES.md..." (and actually read it)
[ ] 2. SEARCH: Does this file/function already exist?
[ ] 3. VERIFY: Is this the correct directory?
[ ] 4. DECIDE: Edit vs Create
       - Can this functionality go in ANY existing file? → EDIT
       - Is there ANY file handling related features? → EDIT  
       - Would creating a new file be better architecture? → STILL EDIT
       - No related files exist anywhere? → ONLY THEN create
[ ] 5. ANNOUNCE: "Creating/Editing [filename] in [directory]"
[ ] 6. CONFIRM: "Pre-flight complete. Proceeding with [action]"
```

### 🚨 ENFORCEMENT PATTERN
```
User: "Create a utility function..."
AI: "Checking SYSTEM_RULES.md..." [READS IT]
AI: "Searching for existing currency functions..." [SEARCHES]
AI: "Verifying directory..." [CHECKS]
AI: "Found existing file: services/formatting.py"
AI: "Pre-flight complete. Editing services/formatting.py"
```

### ❌ VIOLATION EXAMPLE
```
User: "Create a utility function..."
AI: "Creating utils/helper.py..." [NO CHECKLIST = VIOLATION]
```

### ✅ SUCCESS EXAMPLE
```
User: "Create a utility function..."
AI: "Checking SYSTEM_RULES.md..."
AI: "Searching for existing utilities..."
AI: "Found routes/api.py has related functionality"
AI: "Pre-flight complete. Adding to api.py"
```

### 🎯 CONCRETE EXAMPLES
```
Task: "Add formatting function for display"
❌ WRONG: Create services/formatter.py
✅ RIGHT: Add to the file that displays the data

Task: "Add validation utility"
❌ WRONG: Create utils/validators.py
✅ RIGHT: Add to the file that needs validation

Task: "Add helper function"
❌ WRONG: Create helpers/utils.py
✅ RIGHT: Add to the file using that logic
```

---
**THIS CHECKLIST IS MANDATORY - NO EXCEPTIONS**