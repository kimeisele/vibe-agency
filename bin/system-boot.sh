#!/bin/bash
#
# system-boot.sh - STEWARD Boot Sequence
#
# Purpose: Initialize STEWARD with session context + playbook routing
# Usage: ./bin/system-boot.sh
#
# Flow:
#   1. Pre-flight checks (dependencies, environment)
#   2. Call vibe-cli boot (displays MOTD, session context, playbook routes)
#   3. Ready for STEWARD to receive user intent
#
# Full system diagnostics: ./bin/show-status.sh
#

set -euo pipefail

VIBE_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$VIBE_ROOT"

# ============================================================================
# PRE-FLIGHT CHECKS
# ============================================================================
echo "🔍 Running pre-flight checks..."
echo ""

# Check dependencies
if [ ! -d ".venv" ]; then
    echo "📦 Dependencies not found. Please run:"
    echo "   make install"
    echo "   or"
    echo "   uv sync --all-extras"
    echo ""
    exit 1
fi

# Check environment
if git rev-parse --git-dir > /dev/null 2>&1; then
    BRANCH=$(git rev-parse --abbrev-ref HEAD)
    echo "✅ Git repository detected (branch: $BRANCH)"
else
    echo "⚠️  Not a git repository"
fi

echo ""

# ============================================================================
# SYSTEM HEALTH CHECK (Anti-Decay Mechanism)
# ============================================================================
echo "🏥 Running system health check (Anti-Decay mechanism)..."
echo ""

if ./bin/vibe-shell --health 2>&1; then
    echo "✅ System health check PASSED - proceeding to boot"
else
    echo ""
    echo "⚠️  System health check FAILED"
    echo "⚠️  Attempting to proceed anyway, but system may be unstable"
    echo ""
fi

echo ""

# ============================================================================
# BOOT WITH VIBE-CLI
# ============================================================================
echo "🚀 Starting STEWARD with playbook routing..."
echo ""

# Call vibe-cli in boot mode
# This will:
# - Display MOTD (system status)
# - Load session handoff
# - Show available playbook routes
# - Output ready state
python3 ./vibe-cli boot

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "📋 STEWARD OPERATIONAL PROTOCOL"
echo "════════════════════════════════════════════════════════════════"
echo ""

cat << 'SYSTEMPROMPT'
⚡ You are STEWARD, senior orchestration agent at vibe-agency.

Your role: Execute strategic tasks with precision for a non-technical client.

Core Protocol:
• Read complete HANDOFF above before acting
• Execute top priority from backlog
• Test-First Development (docs/policies/TEST_FIRST.md)
• Update .session_handoff.json when phase complete
• Run ./bin/pre-push-check.sh before push

Playbook System:
• Use playbook routes when user intent is clear (see available routes above)
• If user says "restaurant app", load restaurant playbook context
• If user says "continue work", use session_resume playbook
• If unclear, suggest 2-3 relevant playbook options

Output Standard (Client is strategic operator):
• Status: 2-3 sentences, business terms
• Actions: 2-3 concrete next steps, prioritized with time estimates
• Questions: Specific decisions only (propose options proactively)

Tone: Senior consultant. Clarity over explanation. Action over analysis.

SYSTEMPROMPT

echo ""
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "💡 Quick Commands:"
echo "   Full diagnostics:  ./bin/show-status.sh"
echo "   Pre-push check:    ./bin/pre-push-check.sh"
echo "   Run tests:         python3 -m pytest tests/ -v"
echo ""
echo "📚 Playbook Registry: docs/playbook/_registry.yaml"
echo ""
echo "════════════════════════════════════════════════════════════════"
