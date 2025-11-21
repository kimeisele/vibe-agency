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

# Check if session handoff exists
SESSION_HANDOFF_EXISTS="false"
if [ -f ".session_handoff.json" ]; then
  SESSION_HANDOFF_EXISTS="true"
fi

# Check linting status (if uv is available)
LINTING_STATUS="uv_not_available"
LINTING_ERRORS=0
if command -v uv &> /dev/null; then
  if uv run ruff check . --quiet 2>/dev/null; then
    LINTING_STATUS="passing"
    LINTING_ERRORS=0
  else
    LINTING_STATUS="failing"
    # Extract error count from ruff output, default to 1 if can't parse
    LINTING_ERRORS=$(uv run ruff check . 2>&1 | tail -3 | grep -oP "Found \K\d+" | tr -d '\n' | head -c 10)
    : "${LINTING_ERRORS:=1}"  # Default to 1 if empty
  fi
fi

# Check formatting status (if uv is available)
FORMATTING_STATUS="uv_not_available"
if command -v uv &> /dev/null; then
  if uv run ruff format --check . --quiet 2>/dev/null; then
    FORMATTING_STATUS="passing"
  else
    FORMATTING_STATUS="failing"
  fi
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
  "session_handoff_exists": $SESSION_HANDOFF_EXISTS,
  "linting": {
    "status": "$LINTING_STATUS",
    "errors_count": $LINTING_ERRORS
  },
  "formatting": {
    "status": "$FORMATTING_STATUS"
  },
  "steward": "manifest=truth | read>write | edit>create | test>claim | health>features",
  "note": "Quality checks cached here; full validation via pre-push hook",
  "generated_by": "bin/update-system-status.sh"
}
EOF

echo "✅ System status updated: $STATUS_FILE"
