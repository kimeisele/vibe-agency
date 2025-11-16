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
  "session_handoff_exists": $SESSION_HANDOFF_EXISTS,
  "generated_by": "bin/update-system-status.sh"
}
EOF

echo "✅ System status updated: $STATUS_FILE"
