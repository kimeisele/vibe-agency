#!/usr/bin/env bash
#
# create-session-handoff.sh
# Interactive helper to create .session_handoff.json
#
# Usage: ./bin/create-session-handoff.sh
# Prompts for key information and generates handoff file

set -euo pipefail

HANDOFF_FILE=".session_handoff.json"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "unknown")

echo "════════════════════════════════════════════════════════════════"
echo "📝 CREATE SESSION HANDOFF"
echo "════════════════════════════════════════════════════════════════"
echo ""

# Check if handoff already exists
if [ -f "$HANDOFF_FILE" ]; then
  echo "⚠️  $HANDOFF_FILE already exists!"
  echo ""
  read -p "Overwrite? (y/N): " -n 1 -r
  echo ""
  if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Aborted."
    exit 1
  fi
  echo ""
fi

# Gather information
echo "Current branch: $CURRENT_BRANCH"
echo ""

read -p "From session (branch name): " FROM_SESSION
FROM_SESSION=${FROM_SESSION:-$CURRENT_BRANCH}

read -p "From agent (who is handing off): " FROM_AGENT
FROM_AGENT=${FROM_AGENT:-"Claude Code"}

read -p "Date (YYYY-MM-DD): " DATE
DATE=${DATE:-$(date -u +"%Y-%m-%d")}

echo ""
echo "What was completed? (comma-separated, press Enter when done)"
read -p "> " COMPLETED_INPUT
IFS=',' read -ra COMPLETED_ARRAY <<< "$COMPLETED_INPUT"

echo ""
echo "What artifacts were created? (comma-separated, press Enter when done)"
read -p "> " ARTIFACTS_INPUT
IFS=',' read -ra ARTIFACTS_ARRAY <<< "$ARTIFACTS_INPUT"

echo ""
echo "Next session TODOs (one per line, empty line to finish):"
TODOS_JSON="["
FIRST_TODO=true
while true; do
  read -p "> " TODO
  if [ -z "$TODO" ]; then
    break
  fi
  if [ "$FIRST_TODO" = true ]; then
    TODOS_JSON="$TODOS_JSON\n    \"$TODO\""
    FIRST_TODO=false
  else
    TODOS_JSON="$TODOS_JSON,\n    \"$TODO\""
  fi
done
TODOS_JSON="$TODOS_JSON\n  ]"

# Build completed array JSON
COMPLETED_JSON="["
FIRST=true
for item in "${COMPLETED_ARRAY[@]}"; do
  # Trim whitespace
  item=$(echo "$item" | xargs)
  if [ "$FIRST" = true ]; then
    COMPLETED_JSON="$COMPLETED_JSON\n    \"$item\""
    FIRST=false
  else
    COMPLETED_JSON="$COMPLETED_JSON,\n    \"$item\""
  fi
done
COMPLETED_JSON="$COMPLETED_JSON\n  ]"

# Build artifacts array JSON
ARTIFACTS_JSON="["
FIRST=true
for item in "${ARTIFACTS_ARRAY[@]}"; do
  # Trim whitespace
  item=$(echo "$item" | xargs)
  if [ "$FIRST" = true ]; then
    ARTIFACTS_JSON="$ARTIFACTS_JSON\n    \"$item\""
    FIRST=false
  else
    ARTIFACTS_JSON="$ARTIFACTS_JSON,\n    \"$item\""
  fi
done
ARTIFACTS_JSON="$ARTIFACTS_JSON\n  ]"

# Create handoff file
cat > "$HANDOFF_FILE" <<EOF
{
  "from_session": "$FROM_SESSION",
  "from_agent": "$FROM_AGENT",
  "date": "$DATE",
  "branch": "$CURRENT_BRANCH",

  "completed": $(echo -e "$COMPLETED_JSON"),

  "artifacts_created": $(echo -e "$ARTIFACTS_JSON"),

  "next_session_todos": $(echo -e "$TODOS_JSON"),

  "context_for_next_session": {
    "system_state": "TODO: Describe system state",
    "critical_insight": "TODO: Key insight for next agent",
    "known_issues": [],
    "key_decisions": []
  },

  "critical_files_to_understand": [],

  "anti_patterns_to_avoid": [],

  "meta": {
    "handoff_type": "session_handoff",
    "scope": "project_development",
    "created": "$TIMESTAMP",
    "format_version": "1.0"
  }
}
EOF

echo ""
echo "✅ Session handoff created: $HANDOFF_FILE"
echo ""
echo "⚠️  IMPORTANT: Edit the file to add:"
echo "   - context_for_next_session details"
echo "   - critical_files_to_understand"
echo "   - anti_patterns_to_avoid"
echo ""
echo "Preview:"
./bin/show-context.sh
