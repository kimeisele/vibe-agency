#!/bin/bash
#
# system-boot.sh - THE ONE COMMAND (INSTANT)
#
# Purpose: Show session handoff + current branch (< 1 second)
# Usage: ./bin/system-boot.sh
#
# For full system status (tests, linting, etc): ./bin/show-status.sh
#

set -euo pipefail

VIBE_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$VIBE_ROOT"

# ============================================================================
# DEPENDENCY CHECK - Ensure venv is ready (fast when cached)
# ============================================================================
if [ ! -d ".venv" ] || ! python3 -c "import yaml" 2>/dev/null; then
    echo "📦 Installing dependencies..."
    uv sync --all-extras > /dev/null 2>&1
fi

echo "════════════════════════════════════════════════════════════════"
echo "🚀 VIBE-AGENCY SYSTEM BOOT"
echo "════════════════════════════════════════════════════════════════"
echo ""

# ============================================================================
# SESSION HANDOFF - Context + Backlog
# ============================================================================
echo "━━━ SESSION HANDOFF ━━━"
echo ""

if [ -f ".session_handoff.json" ]; then
    # Extract key information using Python (no jq dependency)
    python3 << 'PYEOF'
import json
import sys

try:
    with open('.session_handoff.json', 'r') as f:
        handoff = json.load(f)

    # Layer 0
    bedrock = handoff.get('layer0_bedrock', {})
    print(f"From: {bedrock.get('from', 'Unknown')}")
    print(f"Date: {bedrock.get('date', 'Unknown')}")
    print(f"State: {bedrock.get('state', 'Unknown')}")

    # Layer 1
    runtime = handoff.get('layer1_runtime', {})
    print(f"\nSummary: {runtime.get('completed_summary', 'No summary')}")

    # Backlog (TODOs)
    print("\n📋 BACKLOG:")
    todos = runtime.get('todos', [])
    for i, todo in enumerate(todos, 1):
        # Handle both string and dict formats
        if isinstance(todo, str):
            print(f"  {i}. {todo}")
        else:
            print(f"  {i}. {todo}")

    # Next steps
    detail = handoff.get('layer2_detail', {})
    next_steps = detail.get('next_steps_detail', [])

    if next_steps:
        print("\n🎯 NEXT ACTIONS:")
        for step in next_steps[:2]:  # Show top 2 priorities
            step_name = step.get('step', 'Unknown')
            priority = step.get('priority', '')
            if priority:
                print(f"  [{priority}] {step_name}")
            else:
                print(f"  • {step_name}")

except Exception as e:
    print(f"⚠️  Could not parse session handoff: {e}", file=sys.stderr)
    sys.exit(0)  # Non-fatal, continue boot

PYEOF

else
    echo "⚠️  No session handoff found (.session_handoff.json missing)"
    echo "   This is a fresh session."
fi

echo ""

# ============================================================================
# CURRENT BRANCH (instant, no git status)
# ============================================================================
if git rev-parse --git-dir > /dev/null 2>&1; then
    BRANCH=$(git rev-parse --abbrev-ref HEAD)
    echo "Branch: $BRANCH"
else
    echo "Git: Not a git repository"
fi

echo ""

# ============================================================================
# THE AGENT PROMPT - Ready to execute
# ============================================================================
echo "════════════════════════════════════════════════════════════════"
echo "📋 YOUR PROMPT (Execute this):"
echo "════════════════════════════════════════════════════════════════"
echo ""

# SYSTEM PROMPT (short, 67 tokens) + HANDOFF (has all context)
cat << 'SYSTEMPROMPT'
You are STEWARD, senior orchestration agent for vibe-agency.

PROTOCOL:
• Execute top priority from HANDOFF below
• Test-First Development (docs/policies/TEST_FIRST.md)
• Update .session_handoff.json when done
• Run ./bin/pre-push-check.sh before push

The HANDOFF contains your mission, context, and backlog.
Execute highest priority action NOW.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SYSTEMPROMPT

echo ""

# Output the full handoff (already has everything)
if [ -f ".session_handoff.json" ]; then
    cat .session_handoff.json
else
    echo "⚠️  No session handoff found (.session_handoff.json missing)"
    echo ""
    echo "BOOTSTRAP MISSION:"
    echo "1. Review recent commits: git log --oneline -5"
    echo "2. Check CLAUDE.md for system status"
    echo "3. Create .session_handoff.json with next steps"
fi

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "💡 Quick Commands:"
echo "   Full status:     ./bin/show-status.sh"
echo "   Pre-push check:  ./bin/pre-push-check.sh"
echo "   Run all tests:   uv run pytest tests/ -v"
echo "════════════════════════════════════════════════════════════════"
echo ""
