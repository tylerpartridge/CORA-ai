#!/bin/bash
# CSS Pre-commit Hook
# Prevents CSS conflicts before they reach the codebase

echo "🛡️ CSS Guardian Pre-commit Check..."

# Check for nav-link styles outside navbar.css
NAV_VIOLATIONS=$(grep -r "\.nav-link" --include="*.css" web/static/css/ | grep -v "navbar.css" | grep -v "DEPRECATED")

if [ ! -z "$NAV_VIOLATIONS" ]; then
    echo "❌ ERROR: nav-link styles found outside navbar.css!"
    echo "$NAV_VIOLATIONS"
    echo ""
    echo "Resolution: Move all .nav-link styles to web/static/css/navbar.css"
    exit 1
fi

# Check for navbar styles outside navbar.css
NAVBAR_VIOLATIONS=$(grep -r "\.navbar" --include="*.css" web/static/css/ | grep -v "navbar.css" | grep -v "DEPRECATED")

if [ ! -z "$NAVBAR_VIOLATIONS" ]; then
    echo "⚠️ WARNING: navbar styles found outside navbar.css"
    echo "$NAVBAR_VIOLATIONS"
    echo "Consider moving these to navbar.css for single source of truth"
fi

# Check for rem units in navbar.css
REM_IN_NAV=$(grep -E "\d+rem" web/static/css/navbar.css 2>/dev/null)

if [ ! -z "$REM_IN_NAV" ]; then
    echo "❌ ERROR: rem units found in navbar.css!"
    echo "$REM_IN_NAV"
    echo ""
    echo "Resolution: Use px units in navbar.css to avoid zoom interference"
    exit 1
fi

# Check for inline styles in templates (nav related)
INLINE_NAV=$(grep -r 'style="[^"]*font-size' web/templates/*.html 2>/dev/null | grep -E "nav|Nav")

if [ ! -z "$INLINE_NAV" ]; then
    echo "⚠️ WARNING: Inline font-size styles found in nav elements"
    echo "$INLINE_NAV"
    echo "Consider moving to CSS files"
fi

# Run Python conflict detector if available
if [ -f "features/css_guardian/claude/css_conflict_detector.py" ]; then
    echo "Running CSS conflict detector..."
    python features/css_guardian/claude/css_conflict_detector.py
    if [ $? -ne 0 ]; then
        echo "❌ CSS conflicts detected. Please resolve before committing."
        exit 1
    fi
fi

echo "✅ CSS Guardian checks passed!"
exit 0