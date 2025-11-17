#!/usr/bin/env bash
#
# create-session-handoff.sh
# Automated session handoff creation (4-layer format v2.0)
#
# Usage: ./bin/create-session-handoff.sh [--auto]
#
# Options:
#   --auto    Non-interactive mode (extract from git + receipts)
#
# Related: GAD-100 Phase 3, config/schemas/session_handoff.schema.json

set -euo pipefail

HANDOFF_FILE=".session_handoff.json"
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "unknown")
DATE=$(date -u +"%Y-%m-%d")
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

# Parse arguments
AUTO_MODE=false
if [[ "${1:-}" == "--auto" ]]; then
  AUTO_MODE=true
fi

echo "════════════════════════════════════════════════════════════════"
echo "📝 CREATE SESSION HANDOFF (v2.0 - 4-layer format)"
echo "════════════════════════════════════════════════════════════════"
echo ""

# Check if handoff already exists
if [ -f "$HANDOFF_FILE" ]; then
  echo "⚠️  $HANDOFF_FILE already exists!"
  echo ""
  if [ "$AUTO_MODE" = true ]; then
    echo "Auto-mode: Overwriting existing handoff..."
  else
    read -p "Overwrite? (y/N): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
      echo "Aborted."
      exit 1
    fi
  fi
  echo ""
fi

# Gather information
if [ "$AUTO_MODE" = true ]; then
  # AUTO MODE: Extract from git + .vibe/
  echo "[Auto Mode] Extracting session info..."

  FROM_AGENT="Claude Code - ${CURRENT_BRANCH}"

  # Extract completed work from recent commits
  COMPLETED_SUMMARY=$(git log -1 --pretty=format:"%s" 2>/dev/null || echo "Session work completed")

  # Extract TODOs from git grep (look for TODO comments in changed files)
  TODOS=$(git diff --name-only HEAD~1..HEAD 2>/dev/null | xargs grep -h "TODO:" 2>/dev/null | head -n 3 || echo "")

  # Get state from git status
  if git diff-index --quiet HEAD -- 2>/dev/null; then
    STATE="complete"
    BLOCKER="null"
  else
    STATE="in-progress"
    BLOCKER="null"
  fi

  # Get critical files from recent commits
  CRITICAL_FILES=$(git diff --name-only HEAD~1..HEAD 2>/dev/null | head -n 5 || echo "")

else
  # INTERACTIVE MODE
  echo "Current branch: $CURRENT_BRANCH"
  echo ""

  read -p "From agent (e.g., 'Claude Code - Feature Work'): " FROM_AGENT
  FROM_AGENT=${FROM_AGENT:-"Claude Code - ${CURRENT_BRANCH}"}

  read -p "State (complete/blocked/in-progress): " STATE
  STATE=${STATE:-"complete"}

  read -p "Blocker (or press Enter if none): " BLOCKER
  BLOCKER=${BLOCKER:-"null"}

  echo ""
  echo "What was completed? (one-line summary)"
  read -p "> " COMPLETED_SUMMARY
  COMPLETED_SUMMARY=${COMPLETED_SUMMARY:-"Work completed in this session"}

  echo ""
  echo "Next session TODOs (one per line, empty line to finish):"
  TODOS=""
  while true; do
    read -p "> " TODO
    if [ -z "$TODO" ]; then
      break
    fi
    if [ -z "$TODOS" ]; then
      TODOS="$TODO"
    else
      TODOS="$TODOS
$TODO"
    fi
  done

  echo ""
  echo "Critical files (one per line, empty line to finish):"
  CRITICAL_FILES=""
  while true; do
    read -p "> " FILE
    if [ -z "$FILE" ]; then
      break
    fi
    if [ -z "$CRITICAL_FILES" ]; then
      CRITICAL_FILES="$FILE"
    else
      CRITICAL_FILES="$CRITICAL_FILES
$FILE"
    fi
  done
fi

# Convert to JSON arrays
TODOS_JSON="[]"
if [ -n "$TODOS" ]; then
  TODOS_JSON=$(echo "$TODOS" | python3 -c "import sys, json; print(json.dumps([line.strip() for line in sys.stdin if line.strip()]))")
fi

CRITICAL_FILES_JSON="[]"
if [ -n "$CRITICAL_FILES" ]; then
  CRITICAL_FILES_JSON=$(echo "$CRITICAL_FILES" | python3 -c "import sys, json; print(json.dumps([line.strip() for line in sys.stdin if line.strip()]))")
fi

# Convert blocker to JSON null if needed
if [ "$BLOCKER" = "null" ]; then
  BLOCKER_JSON="null"
else
  BLOCKER_JSON="\"$BLOCKER\""
fi

# Create handoff file (4-layer format)
cat > "$HANDOFF_FILE" <<EOF
{
  "_schema_version": "2.0_4layer",
  "_token_budget": 450,
  "_optimization": "Automated handoff creation",

  "layer0_bedrock": {
    "from": "$FROM_AGENT",
    "date": "$DATE",
    "state": "$STATE",
    "blocker": $BLOCKER_JSON
  },

  "layer1_runtime": {
    "completed_summary": "$COMPLETED_SUMMARY",
    "todos": $TODOS_JSON,
    "critical_files": $CRITICAL_FILES_JSON
  },

  "layer2_detail": {
    "completed": [],
    "key_decisions": [],
    "warnings": [],
    "next_steps_detail": []
  }
}
EOF

echo ""
echo "✅ Session handoff created: $HANDOFF_FILE"
echo ""

if [ "$AUTO_MODE" = false ]; then
  echo "⚠️  IMPORTANT: Edit the file to add layer2_detail:"
  echo "   - completed (detailed work items)"
  echo "   - key_decisions (architectural choices)"
  echo "   - warnings (gotchas for next agent)"
  echo "   - next_steps_detail (expanded TODOs)"
  echo ""
fi

# Validate against schema
if command -v python3 &> /dev/null; then
  echo "Validating against schema..."
  python3 -c "
import json, sys
from pathlib import Path

# Load handoff
with open('$HANDOFF_FILE') as f:
    handoff = json.load(f)

# Load schema
schema_file = Path('config/schemas/session_handoff.schema.json')
if schema_file.exists():
    with open(schema_file) as f:
        schema = json.load(f)

    # Basic validation (check required fields)
    required = schema.get('required', [])
    missing = [r for r in required if r not in handoff]

    if missing:
        print(f'❌ Validation failed: Missing required fields: {missing}')
        sys.exit(1)

    print('✅ Schema validation passed')
else:
    print('⚠️  Schema file not found, skipping validation')
" || echo "⚠️  Validation skipped (Python error)"
fi

echo ""
echo "Preview:"
echo "────────────────────────────────────────────────────────────────"
cat "$HANDOFF_FILE"
echo "────────────────────────────────────────────────────────────────"
