# 🧑 HUMAN TRAINING MANUAL - Don't Break CORA!

*For humans who want to work with AI assistants without causing chaos*

## 🚨 STOP! Before You Touch ANYTHING

### The 5-Second Startup Ritual
```bash
python start_cora.py
```
That's it. This runs health checks, updates indexes, shows current focus. ALWAYS start here.

## 🎯 The Golden Rules (Tattoo These On Your Brain)

### 1. **One File = One Job**
❌ WRONG: `utils.py`, `helpers.py`, `common.py`
✅ RIGHT: `email_send.py`, `stripe_checkout.py`, `user_login.py`

If you're about to create a file with a vague name, STOP. What does it ACTUALLY do?

### 2. **300 Lines = Time to Split**
Your file is getting fat. Split it before it becomes another Ghost disaster.
- See a file at 250 lines? Start planning the split
- Hit 300 lines? MANDATORY split
- "But it's all related!" - No. Split it.

### 3. **Every File Needs a Navigation Header**
```python
"""
🧭 LOCATION: /CORA/your_new_file.py
🎯 PURPOSE: What this file does in 10 words or less
🔗 IMPORTS: Main things it needs
📤 EXPORTS: Main things it provides
🔄 PATTERN: Design pattern if any
📝 TODOS: What's next for this file
"""
```
No header = AI confusion = wasted time = angry you

### 4. **Update Checkpoints or Die**
After EVERY coding session:
1. Edit `.ai/CHECKPOINT.md`
2. Update `.ai/CURRENT_FOCUS.md`
3. Run `python git_smart.py "what you did"`

Skip this and next session starts with confusion.

## 📁 Where Stuff Goes

### Need to add a new feature?
1. **First**: Check `.ai/FORBIDDEN.md` - Maybe we're NOT building it yet
2. **Second**: Check `.ai/NEXT_FEATURES.md` - Is it planned for later?
3. **Third**: Read `.ai/CURRENT_FOCUS.md` - Does it align with NOW?
4. **Only then**: Add to `app.py` if it's an endpoint, or create ONE new file

### Lost and confused?
```bash
# Option 1: Let the system tell you
python restore_context.py

# Option 2: Read in this order
cat .entrypoint
cat .ai/CURRENT_FOCUS.md
cat .ai/SYSTEM_MAP.md
```

### Want to commit?
```bash
# ALWAYS use smart commit
python git_smart.py "Added user authentication"

# NEVER use regular git
git commit -m "stuff"  # <- NO! BAD HUMAN!
```

## 🤖 Working with AI Assistants

### Starting a new session with Claude/ChatGPT/Cursor:

**DON'T DO THIS:**
"Hey, can you add a payment system to my app?"

**DO THIS:**
"I'm working on CORA v4. First, please read these files:
1. Check .entrypoint for the main server location
2. Read .ai/CURRENT_FOCUS.md
3. Look at .ai/SYSTEM_MAP.md
Then help me [specific task]"

### When AI seems confused:
1. Point it to `.cursorrules`
2. Tell it to check navigation headers
3. Remind it about the 300-line limit

## 🚫 The Seven Deadly Sins

1. **Creating `utils.py`** - Special place in hell for this
2. **Ignoring navigation headers** - AI can't help you
3. **Not updating checkpoints** - Future you will hate current you
4. **Deep nesting folders** - `src/core/utils/helpers/common/` = NO
5. **Skipping `start_cora.py`** - Miss health warnings
6. **Regular git commits** - Lose all context
7. **Building forbidden features** - Check `.ai/FORBIDDEN.md`!

## ✅ The Daily Workflow

### Morning Startup
```bash
# 1. Always start here
python start_cora.py

# 2. Check what you're supposed to be doing
cat .ai/CURRENT_FOCUS.md

# 3. See recent changes
python git_smart.py  # Just run it, shows git status
```

### Before Coding
1. Is this in CURRENT_FOCUS? If no, should you be doing it?
2. Will this require a new file? Check SYSTEM_MAP first
3. Is your target file approaching 300 lines? Plan to split

### After Coding
```bash
# 1. Update checkpoint
edit .ai/CHECKPOINT.md  # Add what you did

# 2. Commit smartly
python git_smart.py "Clear description of changes"

# 3. If focus changed
edit .ai/CURRENT_FOCUS.md
```

### Before Bed
```bash
# Check health one more time
python health_check.py

# Make sure everything's committed
python git_smart.py
```

## 🎓 Graduate Level Human Tips

### The "Oh Shit" Recovery
```bash
# When everything's broken
python health_check.py  # See what's wrong
python restore_context.py > recovery.md  # Save state
# Give recovery.md to fresh AI session
```

### The "Speed Run"
```bash
# When you need to code FAST but CLEAN
python start_cora.py  # 30 seconds
# Code your feature
python git_smart.py "Feature done"  # 30 seconds
# Total overhead: 1 minute, saves hours later
```

### The "New AI Session"
```bash
# Perfect prompt for new AI:
python restore_context.py | pbcopy  # Mac
python restore_context.py | clip     # Windows
# Paste into AI chat - instant context!
```

## 🏆 Signs You're Doing It Right

- ✅ Your files are under 300 lines
- ✅ Every file has a clear, specific name
- ✅ AI assistants understand your code immediately
- ✅ You can find any feature in 5 seconds
- ✅ New devs/AIs are productive in minutes
- ✅ You're shipping features, not organizing files

## 💀 Signs You're Becoming Ghost 2.0

- ❌ You have a `utils.py`
- ❌ Files are 500+ lines
- ❌ Nested folders everywhere
- ❌ AI keeps asking "where is X?"
- ❌ You spend more time organizing than coding
- ❌ 400+ files for a simple app

## 🎯 Remember: The Goal

You're building a BUSINESS, not engineering art. Every line of code should:
1. Help get customers
2. Make customers happy
3. Make money

If it doesn't do one of those three, it shouldn't exist.

---

**Final Words**: This system only works if you follow it. Skip steps and you'll end up with Ghost 2.0. Follow the rules and you'll ship faster than ever.

Now go build something people want to pay for!