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
# CHECK 0: PR Visibility (Process Gate - Warning Only)
# ============================================================================
echo "0️⃣  Checking PR visibility (informational)..."
echo "   Ensures your changes are tracked in a GitHub PR..."
echo ""

CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
if [ "$CURRENT_BRANCH" != "main" ]; then
  # Try to find a PR for this branch
  if command -v gh &>/dev/null; then
    PR_COUNT=$(gh pr list --head "$CURRENT_BRANCH" --state open 2>/dev/null | wc -l)
    if [ "$PR_COUNT" -eq 0 ]; then
      echo "   ⚠️  WARNING: No open PR found for branch '$CURRENT_BRANCH'"
      echo "       Your commits exist locally but are not tracked in GitHub."
      echo ""
      echo "   To create a PR:"
      echo "     gh pr create --title '...' --body '...'"
      echo ""
      echo "   (This is a WARNING only - push will proceed.)"
      echo ""
    else
      echo "   ✅ PR found for branch '$CURRENT_BRANCH'"
    fi
  fi
else
  echo "   ℹ️  On main branch (PR check skipped)"
fi

echo ""

# ============================================================================
# CHECK 1: Dependency Integrity (GAD-4 Upgrade)
# ============================================================================
echo "1️⃣  Checking dependency integrity (uv sync --extra dev --check)..."
echo "   Ensures pyproject.toml, uv.lock, and environment are in sync..."
echo ""

if ! command -v uv &>/dev/null; then
  echo "   ⚠️  uv not available - skipping dependency check"
else
  if ! uv sync --extra dev --check &>/dev/null; then
    echo "   ❌ DEPENDENCY INTEGRITY FAILED"
    echo ""
    echo "   Your local dependencies don't match pyproject.toml!"
    echo "   This is a systemic failure that MUST be fixed before push."
    echo ""
    echo "   How to fix:"
    echo "     uv sync --extra dev             # Sync environment to pyproject.toml"
    echo "     uv add <package>                # Add missing declared dependencies"
    echo "     # Then re-run this check"
    echo ""
    FAILED=1
  else
    echo "   ✅ Dependency integrity verified"
    echo "      (pyproject.toml, uv.lock, and environment are in sync)"
  fi
fi

echo ""

# ============================================================================
# CHECK 2: Linting (ruff check)
# ============================================================================
echo "2️⃣  Checking linting (ruff check)..."

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
# CHECK 3: Formatting (ruff format)
# ============================================================================
echo "3️⃣  Checking formatting (ruff format --check)..."

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
# CHECK 4: Tests (pytest)
# ============================================================================
echo "4️⃣  Running tests (pytest)..."

if ! command -v uv &>/dev/null; then
  echo "   ⚠️  uv not available - skipping test check"
else
  if ! uv run pytest tests/ -q --tb=short 2>&1 | tee /tmp/pytest.log; then
    FAILURES=$(grep -c "FAILED" /tmp/pytest.log 2>/dev/null || echo "0")
    echo ""
    echo "   ❌ TESTS FAILED: $FAILURES test(s) failed"
    echo ""
    echo "   How to fix:"
    echo "     uv run pytest tests/ -v         # Run with verbose output"
    echo "     uv run pytest tests/ -x         # Stop at first failure"
    echo ""
    FAILED=1
  else
    echo "   ✅ Tests passed"
  fi
fi

echo ""

# ============================================================================
# CHECK 5: Test Coverage
# ============================================================================
echo "5️⃣  Checking test coverage (minimum 60%)..."

if ! command -v uv &>/dev/null; then
  echo "   ⚠️  uv not available - skipping coverage check"
else
  if uv run pytest tests/ -q --cov=agency_os --cov-report=term 2>&1 | grep -q "TOTAL"; then
    COVERAGE=$(uv run pytest tests/ -q --cov=agency_os --cov-report=term 2>&1 | tail -1 | awk '{print $NF}' || echo "0%")
    COVERAGE_NUM=${COVERAGE%\%}

    if (( COVERAGE_NUM < 60 )); then
      echo "   ❌ COVERAGE TOO LOW: $COVERAGE (minimum 60% required)"
      echo ""
      echo "   How to improve:"
      echo "     uv run pytest tests/ --cov=agency_os --cov-report=html"
      echo "     open htmlcov/index.html                              # View detailed report"
      echo ""
      FAILED=1
    else
      echo "   ✅ Coverage acceptable: $COVERAGE (minimum 60% required)"
    fi
  else
    echo "   ⚠️  Could not calculate coverage (non-critical)"
  fi
fi

echo ""

# ============================================================================
# CHECK 6: Update system status
# ============================================================================
echo "6️⃣  Updating system status..."

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
