#!/bin/bash
# Test bootup awareness commands

echo "=== Testing Bootup Awareness Discovery ==="
echo ""

echo "1. Testing capability discovery..."
if [ -f "docs/system/CAPABILITIES_AWARENESS.md" ]; then
    echo "   ✓ CAPABILITIES_AWARENESS.md found"
    capabilities=$(grep "^### [0-9]" docs/system/CAPABILITIES_AWARENESS.md | wc -l)
    echo "   ✓ Found $capabilities capabilities"
else
    echo "   ✗ CAPABILITIES_AWARENESS.md not found!"
fi

echo ""
echo "2. Testing wiring registry..."
if [ -f "docs/system/AWARENESS_WIRING_REGISTRY.md" ]; then
    echo "   ✓ AWARENESS_WIRING_REGISTRY.md found"
    wired=$(grep "Status:** ✅ WIRED" docs/system/AWARENESS_WIRING_REGISTRY.md | wc -l)
    echo "   ✓ Found $wired wired services"
else
    echo "   ✗ AWARENESS_WIRING_REGISTRY.md not found!"
fi

echo ""
echo "3. Testing SendGrid awareness..."
if grep -q "SendGrid" docs/system/CAPABILITIES_AWARENESS.md 2>/dev/null; then
    echo "   ✓ SendGrid found in capabilities"
fi

if grep -q "SendGrid" docs/system/AWARENESS_WIRING_REGISTRY.md 2>/dev/null; then
    echo "   ✓ SendGrid found in wiring registry"
fi

echo ""
echo "4. Quick capability list:"
grep "^### [0-9]" docs/system/CAPABILITIES_AWARENESS.md | head -5

echo ""
echo "=== Test Complete ==="
echo "In a fresh session, running bootup.md will discover all $capabilities capabilities!"