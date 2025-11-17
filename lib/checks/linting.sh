#!/usr/bin/env bash
#
# linting.sh - SSOT for linting checks
# Speed: <1s | Autofix: yes | Required: yes
#
# Usage:
#   check_linting check  # Check only, exit 1 on errors
#   check_linting fix    # Auto-fix, then check

check_linting() {
  local mode="${1:-check}"

  if ! command -v uv &>/dev/null; then
    echo "⚠️  uv not available - skipping linting check"
    return 0
  fi

  if [[ "$mode" == "fix" ]]; then
    # Auto-fix mode (pre-commit)
    if ! uv run ruff check . --fix 2>&1; then
      echo "❌ Linting errors remain after auto-fix"
      echo "   Fix manually: uv run ruff check ."
      return 1
    fi
  else
    # Check-only mode (pre-push, CI/CD)
    if ! uv run ruff check . --output-format=github 2>&1; then
      echo "❌ Linting failed"
      echo "   Fix with: uv run ruff check . --fix"
      return 1
    fi
  fi

  return 0
}
