#!/bin/bash
#
# system-boot.sh - STEWARD Boot Sequence
#
# Purpose: Initialize STEWARD with session context (< 1 second)
# Usage: ./bin/system-boot.sh
#
# Full system diagnostics: ./bin/show-status.sh
#

set -euo pipefail

VIBE_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$VIBE_ROOT"

# ============================================================================
# DEPENDENCY CHECK
# ============================================================================
if [ ! -d ".venv" ] || ! python3 -c "import yaml" 2>/dev/null; then
    echo "📦 Installing dependencies..."
    uv sync --all-extras > /dev/null 2>&1
fi

# ============================================================================
# BOOT HEADER
# ============================================================================
echo "════════════════════════════════════════════════════════════════"
echo "⚡ STEWARD BOOT SEQUENCE"
echo "════════════════════════════════════════════════════════════════"
echo ""

# ============================================================================
# SESSION CONTEXT
# ============================================================================
echo "━━━ SESSION CONTEXT ━━━"
echo ""

if [ -f ".session_handoff.json" ]; then
    python3 << 'PYEOF'
import json
import sys

try:
    with open('.session_handoff.json', 'r') as f:
        handoff = json.load(f)

    # Session metadata
    bedrock = handoff.get('layer0_bedrock', {})
    print(f"From: {bedrock.get('from', 'Unknown')}")
    print(f"Date: {bedrock.get('date', 'Unknown')}")
    print(f"State: {bedrock.get('state', 'Unknown')}")

    # Current status
    runtime = handoff.get('layer1_runtime', {})
    summary = runtime.get('completed_summary', 'No summary available')
    print(f"\nCurrent Status:\n  {summary}")

    # Backlog
    todos = runtime.get('todos', [])
    if todos:
        print("\n📋 BACKLOG:")
        for i, todo in enumerate(todos, 1):
            print(f"  {i}. {todo}")

    # Priority actions
    detail = handoff.get('layer2_detail', {})
    next_steps = detail.get('next_steps_detail', [])
    if next_steps:
        print("\n🎯 PRIORITY ACTIONS:")
        for step in next_steps[:2]:
            step_name = step.get('step', 'Unknown')
            priority = step.get('priority', '')
            print(f"  [{priority}] {step_name}" if priority else f"  • {step_name}")

except Exception as e:
    print(f"⚠️  Could not parse handoff: {e}", file=sys.stderr)
    sys.exit(0)

PYEOF

else
    echo "⚠️  No session handoff found"
    echo ""
    echo "BOOTSTRAP MODE:"
    echo "  1. Review recent commits: git log --oneline -5"
    echo "  2. Check system status: CLAUDE.md"
    echo "  3. Initialize handoff: .session_handoff.json"
fi

echo ""

# ============================================================================
# ENVIRONMENT
# ============================================================================
if git rev-parse --git-dir > /dev/null 2>&1; then
    BRANCH=$(git rev-parse --abbrev-ref HEAD)
    echo "Current Branch: $BRANCH"
else
    echo "Git: Not a repository"
fi

echo ""

# ============================================================================
# STEWARD OPERATIONAL PROTOCOL
# ============================================================================
echo "════════════════════════════════════════════════════════════════"
echo "📋 OPERATIONAL PROTOCOL"
echo "════════════════════════════════════════════════════════════════"
echo ""

cat << 'SYSTEMPROMPT'
STEWARD OPERATIONAL PROTOCOL

Your role: Execute strategic tasks with precision for a non-technical client.

Core Protocol:
• Read complete HANDOFF below before acting
• Execute top priority from backlog
• Test-First Development (docs/policies/TEST_FIRST.md)
• Update .session_handoff.json when phase complete
• Run ./bin/pre-push-check.sh before push

Entry Point Awareness:
• If user request is vague, suggest optimal entry point
• Reference: docs/playbook/ENTRY_POINTS.md (9 specialized modes)
• Route to correct GAD pillar automatically
• Proactively suggest 2-3 relevant options when unclear

Output Standard (Client is strategic operator):
• Status: 2-3 sentences, business terms
• Actions: 2-3 concrete next steps, prioritized with time estimates
• Questions: Specific decisions only (propose options proactively)

Tone: Senior consultant. Clarity over explanation. Action over analysis.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
HANDOFF DATA (Complete session context):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

SYSTEMPROMPT

# Output handoff JSON
if [ -f ".session_handoff.json" ]; then
    cat .session_handoff.json
else
    echo '{"status": "bootstrap", "message": "No handoff found - initialize session"}'
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# ============================================================================
# QUICK REFERENCE
# ============================================================================
echo "💡 Quick Commands:"
echo "   Full diagnostics:  ./bin/show-status.sh"
echo "   Pre-push check:    ./bin/pre-push-check.sh"
echo "   Run tests:         uv run pytest tests/ -v"
echo ""
echo "📚 Entry Points:     docs/playbook/USER_PLAYBOOK.md"
echo ""
echo "════════════════════════════════════════════════════════════════"
