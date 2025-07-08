#!/bin/bash
# 🧭 LOCATION: /CORA/tools/start_session.sh
# 🎯 PURPOSE: Generate Claude bootup prompt for new sessions
# 📝 STAYS UNDER 50 LINES!

echo "=== CLAUDE SESSION BOOTUP PROMPT ==="
echo ""
echo "I'm starting a new work session on CORA. Please:"
echo ""
echo "1. Read these files in order:"
echo "   - NOW.md (current task)"
echo "   - STATUS.md (system health)"
echo "   - .mind/today/session.md (recent work)"
echo "   - NEXT.md (upcoming tasks)"
echo ""
echo "2. Give me a 3-line summary:"
echo "   - Where we left off"
echo "   - System status"
echo "   - Recommended next action"
echo ""
echo "3. If any files are approaching size limits, flag them"
echo ""
echo "Then wait for my direction."
echo ""
echo "=== COPY ABOVE TO CLAUDE ==="