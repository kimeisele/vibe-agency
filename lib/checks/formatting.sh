#!/usr/bin/env bash
#
# formatting.sh - SSOT for formatting checks
# Speed: <1s | Autofix: yes | Required: yes
#
# Usage:
#   check_formatting check  # Check only, exit 1 on errors
#   check_formatting fix    # Auto-format, always succeeds

check_formatting() {
  local mode="${1:-check}"

  if ! command -v uv &>/dev/null; then
    echo "⚠️  uv not available - skipping formatting check"
    return 0
  fi

  if [[ "$mode" == "fix" ]]; then
    # Auto-format mode (pre-commit)
    uv run ruff format . &>/dev/null
    return 0  # Formatting always succeeds
  else
    # Check-only mode (pre-push, CI/CD)
    if ! uv run ruff format --check . &>/dev/null; then
      echo "❌ Formatting check failed"
      echo "   Fix with: uv run ruff format ."
      return 1
    fi
  fi

  return 0
}
