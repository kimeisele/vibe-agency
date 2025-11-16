#!/usr/bin/env bash
#
# pre-push-check.sh
# MANDATORY quality checks before git push
# Blocks push if critical checks fail
#
# Usage: ./bin/pre-push-check.sh
# Integration: ./bin/pre-push-check.sh && git push
# Git Hook: .githooks/pre-push (optional)
#
# Exit Codes:
#   0 = All checks passed (safe to push)
#   1 = Check failed (push blocked)

set -euo pipefail

echo "════════════════════════════════════════════════════════════════"
echo "🔍 PRE-PUSH QUALITY CHECKS"
echo "════════════════════════════════════════════════════════════════"
echo ""

FAILED=0

# ============================================================================
# CHECK 1: Linting (ruff check)
# ============================================================================
echo "1️⃣  Checking linting (ruff check)..."

if ! command -v uv &>/dev/null; then
  echo "   ⚠️  uv not available - skipping linting check"
else
  # Run ruff check and capture output
  if ! uv run ruff check . --output-format=github 2>&1 | tee /tmp/ruff-check.log; then
    ERRORS=$(grep -c "\.py:" /tmp/ruff-check.log 2>/dev/null || echo "0")
    echo ""
    echo "   ❌ LINTING FAILED: $ERRORS error(s) found"
    echo ""
    echo "   How to fix:"
    echo "     uv run ruff check . --fix      # Auto-fix most issues"
    echo "     uv run ruff check .            # Review remaining issues"
    echo ""
    FAILED=1
  else
    echo "   ✅ Linting passed (0 errors)"
  fi
fi

echo ""

# ============================================================================
# CHECK 2: Formatting (ruff format)
# ============================================================================
echo "2️⃣  Checking formatting (ruff format --check)..."

if ! command -v uv &>/dev/null; then
  echo "   ⚠️  uv not available - skipping formatting check"
else
  if ! uv run ruff format --check . &>/dev/null; then
    echo "   ❌ FORMATTING FAILED"
    echo ""
    echo "   How to fix:"
    echo "     uv run ruff format .           # Auto-format all files"
    echo ""
    FAILED=1
  else
    echo "   ✅ Formatting passed"
  fi
fi

echo ""

# ============================================================================
# CHECK 3: Update system status
# ============================================================================
echo "3️⃣  Updating system status..."

if [ -f "bin/update-system-status.sh" ]; then
  if ./bin/update-system-status.sh &>/dev/null; then
    echo "   ✅ System status updated"
  else
    echo "   ⚠️  System status update failed (non-critical)"
  fi
else
  echo "   ⚠️  bin/update-system-status.sh not found (skipping)"
fi

echo ""
echo "════════════════════════════════════════════════════════════════"

# ============================================================================
# FINAL RESULT
# ============================================================================
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
