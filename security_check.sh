#!/bin/bash
# Security check script for BVG Display

echo "🔒 BVG Display Security Check"
echo "=============================="
echo ""

ISSUES=0
WARNINGS=0

# Check 1: config.json permissions
echo "📋 Checking config.json permissions..."
if [ -f "./config/config.json" ]; then
    PERMS=$(stat -f "%Lp" "./config/config.json" 2>/dev/null || stat -c "%a" "./config/config.json" 2>/dev/null)
    if [ "$PERMS" = "600" ]; then
        echo "✅ config.json has secure permissions (600)"
    else
        echo "❌ config.json permissions: $PERMS (should be 600)"
        echo "   Fix: chmod 600 ./config/config.json"
        ISSUES=$((ISSUES + 1))
    fi
else
    echo "⚠️  config.json not found"
    WARNINGS=$((WARNINGS + 1))
fi

# Check 2: config directory permissions
echo ""
echo "📋 Checking config/ directory permissions..."
if [ -d "./config" ]; then
    DIR_PERMS=$(stat -f "%Lp" "./config" 2>/dev/null || stat -c "%a" "./config" 2>/dev/null)
    if [ "$DIR_PERMS" = "700" ]; then
        echo "✅ config/ directory has secure permissions (700)"
    else
        echo "⚠️  config/ directory permissions: $DIR_PERMS (recommended: 700)"
        echo "   Fix: chmod 700 ./config"
        WARNINGS=$((WARNINGS + 1))
    fi
fi

# Check 3: Git tracking
echo ""
echo "📋 Checking if config.json is git-ignored..."
if [ -d ".git" ]; then
    if git check-ignore -q config/config.json 2>/dev/null; then
        echo "✅ config.json is properly git-ignored"
    else
        echo "❌ config.json is NOT git-ignored!"
        echo "   This could expose your location if committed"
        echo "   Fix: Add 'config/config.json' to .gitignore"
        ISSUES=$((ISSUES + 1))
    fi
    
    # Check if already tracked
    if git ls-files --error-unmatch config/config.json 2>/dev/null; then
        echo "❌ config.json is TRACKED by git!"
        echo "   Your location data may already be in git history"
        echo "   See SECURITY.md for removal instructions"
        ISSUES=$((ISSUES + 1))
    fi
else
    echo "⚠️  Not a git repository (skip git checks)"
fi

# Check 4: Backup files
echo ""
echo "📋 Checking for sensitive backup files..."
BACKUPS=$(find . -name "config*.backup" -o -name "config*.bak" 2>/dev/null)
if [ -n "$BACKUPS" ]; then
    echo "⚠️  Found backup files that may contain sensitive data:"
    echo "$BACKUPS"
    echo "   Consider: chmod 600 on these files or delete them"
    WARNINGS=$((WARNINGS + 1))
else
    echo "✅ No sensitive backup files found"
fi

# Check 5: World-readable files
echo ""
echo "📋 Checking for world-readable config files..."
WORLD_READABLE=$(find ./config -type f -perm -004 2>/dev/null | grep -v "example")
if [ -n "$WORLD_READABLE" ]; then
    echo "⚠️  World-readable config files found:"
    echo "$WORLD_READABLE"
    echo "   Fix: chmod 600 <file>"
    WARNINGS=$((WARNINGS + 1))
else
    echo "✅ No world-readable config files"
fi

# Summary
echo ""
echo "=============================="
if [ $ISSUES -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo "✅ All security checks passed!"
    exit 0
elif [ $ISSUES -eq 0 ]; then
    echo "⚠️  Found $WARNINGS warning(s) - review recommended"
    exit 0
else
    echo "❌ Found $ISSUES critical issue(s) and $WARNINGS warning(s)"
    echo ""
    echo "Please fix critical issues to protect your location data."
    echo "See SECURITY.md for detailed guidance."
    exit 1
fi
