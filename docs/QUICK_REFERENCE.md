# 🎯 CORA QUICK REFERENCE CARD

## 🚀 Daily Commands
```bash
python start_cora.py          # ALWAYS start here
python health_check.py        # Check system health
python git_smart.py "msg"     # Commit with context
python restore_context.py     # Lost? Run this
python index_cora.py         # Update system maps
```

## 📁 Key Files
- **Main server**: `app.py`
- **What now?**: `.ai/CURRENT_FOCUS.md`
- **Don't build**: `.ai/FORBIDDEN.md`
- **File map**: `.ai/SYSTEM_MAP.md`
- **Progress**: `.ai/CHECKPOINT.md`

## ✅ Before Coding Checklist
- [ ] Run `python start_cora.py`
- [ ] Check `.ai/CURRENT_FOCUS.md`
- [ ] Verify not in `.ai/FORBIDDEN.md`
- [ ] Check file size (<300 lines)

## 🧭 Every New File Needs
```python
"""
🧭 LOCATION: /CORA/filename.py
🎯 PURPOSE: What it does (10 words max)
🔗 IMPORTS: What it needs
📤 EXPORTS: What it provides
🔄 PATTERN: Design pattern if any
📝 TODOS: What's next
"""
```

## 🚫 NEVER
- Create `utils.py` or `helpers.py`
- Exceed 300 lines per file
- Nest folders deep
- Use plain `git commit`
- Skip checkpoint updates
- Build without checking CURRENT_FOCUS

## 🤖 For AI Sessions
"Read these first:
1. `.entrypoint`
2. `.ai/CURRENT_FOCUS.md`
3. `.ai/SYSTEM_MAP.md`
Then [your request]"

## 🆘 Emergency
```bash
python health_check.py        # What's broken?
python restore_context.py     # Get full context
cat .ai/ACTIVE_FILES.md      # See all files
```

---
*Print this. Tape it to your monitor. Follow it.*