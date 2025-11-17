#!/usr/bin/env bash
#
# tests.sh - SSOT for test execution
# Speed: ~5-10s (unit), ~30s+ (e2e) | Autofix: no | Required: yes
#
# Usage:
#   check_tests unit         # Run unit tests only
#   check_tests integration  # Run integration tests
#   check_tests e2e          # Run E2E tests
#   check_tests all          # Run all tests

check_tests() {
  local scope="${1:-unit}"

  if ! command -v uv &>/dev/null; then
    echo "⚠️  uv not available - skipping tests"
    return 0
  fi

  case "$scope" in
    unit)
      echo "Running unit tests..."
      uv run pytest tests/ -v --ignore=tests/e2e --ignore=tests/performance
      ;;
    integration)
      echo "Running integration tests..."
      uv run pytest tests/ -v --ignore=tests/e2e --ignore=tests/performance -m integration
      ;;
    e2e)
      echo "Running E2E tests..."
      uv run pytest tests/e2e -v
      ;;
    all)
      echo "Running all tests..."
      uv run pytest tests/ -v
      ;;
    *)
      echo "❌ Unknown test scope: $scope"
      echo "   Valid: unit|integration|e2e|all"
      return 1
      ;;
  esac

  return $?
}
