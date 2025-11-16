#!/usr/bin/env bash
#
# show-context.sh
# ONE COMMAND to see full session context
#
# Usage: ./bin/show-context.sh
# Shows: session handoff + system status in readable format

set -euo pipefail

SESSION_HANDOFF=".session_handoff.json"
SYSTEM_STATUS=".system_status.json"

echo "════════════════════════════════════════════════════════════════"
echo "📋 SESSION CONTEXT"
echo "════════════════════════════════════════════════════════════════"
echo ""

# Show session handoff if exists
if [ -f "$SESSION_HANDOFF" ]; then
  echo "━━━ SESSION HANDOFF (from previous agent) ━━━"
  echo ""

  # Extract key fields using grep/sed (no jq dependency)
  FROM_SESSION=$(grep '"from_session"' "$SESSION_HANDOFF" | sed 's/.*: "\(.*\)".*/\1/')
  FROM_AGENT=$(grep '"from_agent"' "$SESSION_HANDOFF" | sed 's/.*: "\(.*\)".*/\1/')
  DATE=$(grep '"date"' "$SESSION_HANDOFF" | sed 's/.*: "\(.*\)".*/\1/')

  echo "From: $FROM_AGENT"
  echo "Session: $FROM_SESSION"
  echo "Date: $DATE"
  echo ""

  echo "Completed:"
  grep -A 10 '"completed":' "$SESSION_HANDOFF" | grep '    "' | sed 's/.*"\(.*\)".*/  ✅ \1/'
  echo ""

  echo "Next TODOs:"
  grep -A 20 '"next_session_todos":' "$SESSION_HANDOFF" | grep '    "' | sed 's/.*"\(.*\)".*/  🔲 \1/' | head -10
  echo ""

  echo "Critical files to understand:"
  grep -A 10 '"critical_files_to_understand":' "$SESSION_HANDOFF" | grep '    "' | sed 's/.*"\(.*\)".*/  📄 \1/'
  echo ""
else
  echo "⚠️  No session handoff found ($SESSION_HANDOFF)"
  echo ""
fi

# Show system status if exists
if [ -f "$SYSTEM_STATUS" ]; then
  echo "━━━ SYSTEM STATUS (auto-updated) ━━━"
  echo ""

  # Extract key fields
  TIMESTAMP=$(grep '"timestamp"' "$SYSTEM_STATUS" | sed 's/.*: "\(.*\)".*/\1/')
  BRANCH=$(grep '"branch"' "$SYSTEM_STATUS" | sed 's/.*: "\(.*\)".*/\1/')
  LAST_COMMIT_SHA=$(grep '"sha"' "$SYSTEM_STATUS" | sed 's/.*: "\(.*\)".*/\1/')
  LAST_COMMIT_MSG=$(grep '"message"' "$SYSTEM_STATUS" | sed 's/.*: "\(.*\)".*/\1/')
  CLEAN=$(grep '"working_directory_clean"' "$SYSTEM_STATUS" | sed 's/.*: \(.*\)/\1/' | tr -d ',')
  TESTS=$(grep '"planning_workflow"' "$SYSTEM_STATUS" | sed 's/.*: "\(.*\)".*/\1/')

  echo "Last updated: $TIMESTAMP"
  echo "Current branch: $BRANCH"
  echo "Last commit: $LAST_COMMIT_SHA - $LAST_COMMIT_MSG"
  echo "Working directory: $([ "$CLEAN" = "true" ] && echo "✅ Clean" || echo "⚠️  Modified")"
  echo "Tests (planning): $([ "$TESTS" = "passing" ] && echo "✅ Passing" || echo "❌ $TESTS")"
  echo ""
else
  echo "⚠️  No system status found ($SYSTEM_STATUS)"
  echo "   Run: ./bin/update-system-status.sh"
  echo ""
fi

echo "════════════════════════════════════════════════════════════════"
echo ""
echo "💡 Quick commands:"
echo "   View full session handoff:  cat .session_handoff.json"
echo "   View full system status:    cat .system_status.json"
echo "   Update system status:       ./bin/update-system-status.sh"
echo "   Verify system claims:       cat CLAUDE.md | grep 'Verify Command'"
echo ""
