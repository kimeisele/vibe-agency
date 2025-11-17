#!/usr/bin/env bash
#
# pre-push-check.sh - Medium Layer
# Runs: Linting + Formatting + System Status Update
# Time: 5-10s
#
# Usage: ./bin/pre-push-check.sh
# Git Hook: .githooks/pre-push calls this script

set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$REPO_ROOT"

# Source check functions (SSOT)
source "$REPO_ROOT/lib/checks/linting.sh"
source "$REPO_ROOT/lib/checks/formatting.sh"

echo "════════════════════════════════════════════════════════════════"
echo "🔍 PRE-PUSH QUALITY CHECKS"
echo "════════════════════════════════════════════════════════════════"
echo ""

FAILED=0

# CHECK 1: Linting
echo "1️⃣  Checking linting..."
if ! check_linting check; then
  FAILED=1
fi
echo ""

# CHECK 2: Formatting
echo "2️⃣  Checking formatting..."
if ! check_formatting check; then
  FAILED=1
fi
echo ""

# CHECK 3: Update system status (non-critical)
echo "3️⃣  Updating system status..."
if [ -f "$REPO_ROOT/bin/update-system-status.sh" ]; then
  if "$REPO_ROOT/bin/update-system-status.sh" &>/dev/null; then
    echo "   ✅ System status updated"
  else
    echo "   ⚠️  System status update failed (non-critical)"
  fi
else
  echo "   ⚠️  bin/update-system-status.sh not found (skipping)"
fi
echo ""

echo "════════════════════════════════════════════════════════════════"

# Final result
if [ $FAILED -eq 1 ]; then
  echo "❌ PRE-PUSH CHECKS FAILED"
  echo ""
  echo "   Push blocked. Fix the errors above and try again."
  echo ""
  exit 1
else
  echo "✅ ALL PRE-PUSH CHECKS PASSED"
  echo ""
  echo "   Safe to push!"
  echo ""
  exit 0
fi
