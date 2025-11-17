#!/usr/bin/env bash
#
# commit-and-push.sh
# Canonical commit script with automatic linting enforcement
#
# Usage: ./bin/commit-and-push.sh "commit message"
# This script enforces linting BEFORE allowing commits (works like gravity)
#
# Why this exists:
# - Git hooks don't work in browser-based Claude Code
# - Git hooks require manual setup (git config core.hooksPath)
# - This script works EVERYWHERE (browser, desktop, one-time envs)
#
# Architecture:
# 1. Run linting with auto-fix
# 2. If linting fails → BLOCK commit (exit 1)
# 3. If linting passes → Allow commit + push
# 4. Update system status for next agent

set -euo pipefail

# Check if commit message provided
if [ $# -eq 0 ]; then
  echo "❌ Error: Commit message required"
  echo "Usage: ./bin/commit-and-push.sh \"your commit message\""
  exit 1
fi

COMMIT_MSG="$1"

echo "════════════════════════════════════════════════════════════════"
echo "🚀 COMMIT & PUSH (with linting enforcement)"
echo "════════════════════════════════════════════════════════════════"
echo ""

# Step 1: Check linting (with auto-fix)
echo "🔍 Step 1/4: Running linting check..."
if uv run ruff check . --fix; then
  echo "✅ Linting: Clean"
else
  echo ""
  echo "════════════════════════════════════════════════════════════════"
  echo "❌ COMMIT BLOCKED: Linting errors found"
  echo "════════════════════════════════════════════════════════════════"
  echo ""
  echo "Ruff found errors that could not be auto-fixed."
  echo ""
  echo "Fix manually, then try again:"
  echo "  1. Fix the errors shown above"
  echo "  2. Run: uv run ruff check ."
  echo "  3. When clean, run: ./bin/commit-and-push.sh \"$COMMIT_MSG\""
  echo ""
  exit 1
fi
echo ""

# Step 2: Format check
echo "🎨 Step 2/4: Checking code formatting..."
if ! uv run ruff format --check . &>/dev/null; then
  echo "⚠️  Auto-formatting code..."
  uv run ruff format .
  echo "✅ Formatting: Fixed"
else
  echo "✅ Formatting: Clean"
fi
echo ""

# Step 3: Git add, commit, push
echo "📦 Step 3/4: Committing and pushing..."
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)

git add .
git commit -m "$COMMIT_MSG"
git push -u origin "$CURRENT_BRANCH"

echo "✅ Pushed to: $CURRENT_BRANCH"
echo ""

# Step 4: Update system status
echo "📊 Step 4/4: Updating system status..."
./bin/update-system-status.sh

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "✅ COMMIT COMPLETE"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "💡 Full system status:"
echo ""
./bin/show-status.sh
echo ""
