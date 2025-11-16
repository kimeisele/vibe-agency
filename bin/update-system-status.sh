#!/usr/bin/env bash
#
# update-system-status.sh
# Auto-updates .system_status.json with current git state
#
# Usage: ./bin/update-system-status.sh
# Called by: git hooks (post-commit, post-push) or manually

set -euo pipefail

STATUS_FILE=".system_status.json"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

# Get git information
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "unknown")
LAST_COMMIT=$(git log -1 --format="%h" 2>/dev/null || echo "none")
LAST_COMMIT_MSG=$(git log -1 --format="%s" 2>/dev/null || echo "none")
LAST_COMMIT_DATE=$(git log -1 --format="%ci" 2>/dev/null || echo "unknown")
GIT_STATUS=$(git status --porcelain 2>/dev/null || echo "")

# Determine if working directory is clean
if [ -z "$GIT_STATUS" ]; then
  WORKING_DIR_CLEAN="true"
else
  WORKING_DIR_CLEAN="false"
fi

# Run test suite status (quick check)
TESTS_STATUS="unknown"
if [ -f "tests/test_planning_workflow.py" ]; then
  if python3 tests/test_planning_workflow.py &>/dev/null; then
    TESTS_STATUS="passing"
  else
    TESTS_STATUS="failing"
  fi
fi

# Check linting status (ruff check)
LINTING_STATUS="unknown"
LINTING_ERROR_COUNT=0
if command -v uv &>/dev/null; then
  # Run ruff check and capture output (set +e to not exit on error)
  set +e
  LINTING_OUTPUT=$(uv run ruff check . 2>&1)
  RUFF_EXIT_CODE=$?
  set -e

  if [ $RUFF_EXIT_CODE -eq 0 ]; then
    LINTING_STATUS="passing"
  else
    LINTING_STATUS="failing"
    # Count errors (ruff outputs "Found X errors")
    LINTING_ERROR_COUNT=$(echo "$LINTING_OUTPUT" | grep -oP 'Found \K\d+' || echo "0")
  fi
else
  LINTING_STATUS="uv_not_available"
fi

# Check formatting status (ruff format)
FORMATTING_STATUS="unknown"
if command -v uv &>/dev/null; then
  if uv run ruff format --check . &>/dev/null; then
    FORMATTING_STATUS="passing"
  else
    FORMATTING_STATUS="failing"
  fi
else
  FORMATTING_STATUS="uv_not_available"
fi

# Check if session handoff exists
SESSION_HANDOFF_EXISTS="false"
if [ -f ".session_handoff.json" ]; then
  SESSION_HANDOFF_EXISTS="true"
fi

# Create system status JSON
cat > "$STATUS_FILE" <<EOF
{
  "timestamp": "$TIMESTAMP",
  "git": {
    "branch": "$CURRENT_BRANCH",
    "last_commit": {
      "sha": "$LAST_COMMIT",
      "message": "$LAST_COMMIT_MSG",
      "date": "$LAST_COMMIT_DATE"
    },
    "working_directory_clean": $WORKING_DIR_CLEAN
  },
  "tests": {
    "planning_workflow": "$TESTS_STATUS"
  },
  "linting": {
    "status": "$LINTING_STATUS",
    "errors_count": $LINTING_ERROR_COUNT
  },
  "formatting": {
    "status": "$FORMATTING_STATUS"
  },
  "session_handoff_exists": $SESSION_HANDOFF_EXISTS,
  "generated_by": "bin/update-system-status.sh"
}
EOF

echo "✅ System status updated: $STATUS_FILE"
