#!/bin/bash
#
# system-boot.sh - THE ONE COMMAND
#
# Purpose: Boot sequence that gives agent FULL CONTEXT + NEXT ACTION
# Usage: ./bin/system-boot.sh
#
# Displays:
#   1. Layer 0 Kernel (system integrity)
#   2. Session Handoff (context + backlog)
#   3. Next Action (THE SINGLE THING TO DO)
#

set -euo pipefail

VIBE_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$VIBE_ROOT"

echo "════════════════════════════════════════════════════════════════"
echo "🚀 VIBE-AGENCY SYSTEM BOOT"
echo "════════════════════════════════════════════════════════════════"
echo ""

# ============================================================================
# LAYER 0: KERNEL - System Integrity Verification
# ============================================================================
echo "━━━ LAYER 0: KERNEL VERIFICATION ━━━"
echo ""

if [ -f "scripts/verify-system-integrity.py" ]; then
    # Run integrity check (fast mode)
    INTEGRITY_RESULT=$(python scripts/verify-system-integrity.py 2>&1 | tail -5 || echo "⚠️  Integrity check failed")

    if echo "$INTEGRITY_RESULT" | grep -q "✅"; then
        echo "✅ System Integrity: VERIFIED"
    else
        echo "⚠️  System Integrity: DEGRADED"
        echo "   Run: python scripts/verify-system-integrity.py"
    fi
else
    echo "✅ System Integrity: Scripts present (full check skipped)"
fi

echo ""

# ============================================================================
# LAYER 1: SESSION HANDOFF - Context + Backlog
# ============================================================================
echo "━━━ LAYER 1: SESSION HANDOFF ━━━"
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
# LAYER 2: SYSTEM STATUS - Quick Health Check
# ============================================================================
echo "━━━ LAYER 2: SYSTEM STATUS ━━━"
echo ""

# Git status
if git rev-parse --git-dir > /dev/null 2>&1; then
    BRANCH=$(git rev-parse --abbrev-ref HEAD)
    STATUS=$(git status --porcelain)

    echo "Branch: $BRANCH"

    if [ -z "$STATUS" ]; then
        echo "Working Directory: ✅ Clean"
    else
        echo "Working Directory: ⚠️  Modified files"
        echo "$STATUS" | head -5
    fi
else
    echo "Git: ⚠️  Not a git repository"
fi

echo ""

# Linting status (quick check)
if command -v ruff &> /dev/null; then
    LINT_ERRORS=$(uv run ruff check . --quiet 2>&1 | wc -l || echo "unknown")

    if [ "$LINT_ERRORS" -eq 0 ]; then
        echo "Linting: ✅ Clean"
    else
        echo "Linting: ⚠️  $LINT_ERRORS errors"
        echo "   Fix: uv run ruff check . --fix"
    fi
else
    echo "Linting: ⚠️  ruff not available"
fi

echo ""

# Test status (smoke test only)
if [ -d "tests" ]; then
    echo "Tests: Running quick smoke check..."
    TEST_RESULT=$(uv run pytest tests/test_layer0_integrity.py -q --tb=no 2>&1 | tail -1 || echo "failed")

    if echo "$TEST_RESULT" | grep -q "passed"; then
        echo "Tests: ✅ Smoke test passed"
    else
        echo "Tests: ⚠️  Smoke test failed"
        echo "   Run: uv run pytest tests/ -v"
    fi
else
    echo "Tests: ⚠️  No test directory found"
fi

echo ""

# ============================================================================
# THE AGENT PROMPT - Ready to execute
# ============================================================================
echo "════════════════════════════════════════════════════════════════"
echo "📋 YOUR PROMPT (Execute this):"
echo "════════════════════════════════════════════════════════════════"
echo ""

# SYSTEM PROMPT (short, <400 tokens) + HANDOFF (has all context)
cat << 'SYSTEMPROMPT'
You are STEWARD, the senior orchestration agent for vibe-agency.

YOUR ROLE:
- Execute strategic tasks with precision
- Follow Test-First Development (docs/policies/TEST_FIRST.md)
- Use existing 'patch cables' (modular synthesizer philosophy)
- Update .session_handoff.json when phase complete
- Run ./bin/pre-push-check.sh before pushing

THE HANDOFF BELOW contains your MISSION, CONTEXT, and BACKLOG.
Read it carefully and execute the highest priority action.

START NOW.

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
