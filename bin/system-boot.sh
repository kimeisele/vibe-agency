#!/bin/bash
#
# VIBE AGENCY OS - Atomic System Boot Sequence
#
# PURPOSE: Runs integrity checks and securely hands over control to the STEWARD (Mission Control).
# USAGE: ./bin/system-boot.sh
#
# Note: The STEWARD system prompt is now managed dynamically via GAD-7 mission state,
#       not hardcoded in this script.

set -euo pipefail

# --- TERM CHECK (GAD-501: CI/CD Compatibility) ---
# If TERM is not set (e.g., in CI), set it to dumb and disable color output
if [ -z "${TERM:-}" ] || [ "${TERM:-}" = "" ]; then
    export TERM=dumb
    USE_COLOR=false
elif [ "${TERM}" = "dumb" ]; then
    USE_COLOR=false
else
    USE_COLOR=true
fi

# --- VIBE COLORS ---
if [ "$USE_COLOR" = true ]; then
    CYAN='\033[0;36m'
    GREEN='\033[0;32m'
    RED='\033[0;31m'
    YELLOW='\033[1;33m'
    NC='\033[0m'
else
    CYAN=''
    GREEN=''
    RED=''
    YELLOW=''
    NC=''
fi

# --- INITIALIZATION ---
VIBE_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$VIBE_ROOT"

# --- AUTO-PROVISIONING (GAD-5: Zero-Config Boot) ---
# If no .env exists, create it from template silently
if [ ! -f .env ]; then
    if [ -f .env.template ]; then
        cp .env.template .env
        # Note: .env will have placeholder values, but phoenix.py handles missing keys gracefully
    fi
fi

# Only clear if we have a real terminal
if [ "$USE_COLOR" = true ]; then
    clear
fi

echo -e "${CYAN}"
cat << "EOF"
__     __  _   _               _
\ \   / / (_) | |__     ___   | |
 \ \ / /  | | | '_ \   / _ \  | |
  \ V /   | | | |_) | |  __/  |_|
   \_/    |_| |_.__/   \___|  (_)

   >>> AGENCY OPERATING SYSTEM <<<
   >>> GAD-2/3/4/5/6/7 COMPLETE <<<
EOF
echo -e "${NC}"
echo "════════════════════════════════════════════════════════════════"

# ============================================================================
# 1. PRE-FLIGHT CHECKS (GIT & ENV)
# ============================================================================
echo "🔍 Running pre-flight environment checks..."

# Check Virtual Environment
if [ ! -d ".venv" ]; then
    echo -e "⚠️  VirtualEnv: ${YELLOW}Not active.${NC} Dependencies may be unstable."
fi

# Check Git Status
if git rev-parse --git-dir > /dev/null 2>&1; then
    BRANCH=$(git rev-parse --abbrev-ref HEAD)
    echo -e "✅ Git Repository: ${GREEN}Detected${NC} (branch: $BRANCH)"
else
    echo -e "⚠️  Git Repository: ${YELLOW}Not initialized.${NC}"
fi

echo ""

# ============================================================================
# 2. SYSTEM HEALTH CHECK (The Anti-Decay Mechanism)
# ============================================================================
echo "🏥 Running system health check (GAD-5 Anti-Decay)..."
echo ""

# Use the vibe-shell health check
if ./bin/vibe-shell --health 2>&1 | grep -q "SYSTEM HEALTHY"; then
    echo -e "✅ System health check: ${GREEN}PASSED${NC} (All critical checks green)"
else
    echo ""
    echo -e "❌ System health check: ${RED}FAILED${NC}"
    echo -e "⚠️  Proceeding anyway, but system may be unstable. Fix dependencies!"
fi

echo ""

# ============================================================================
# 3. HANDOVER TO STEWARD (Mission Control)
# ============================================================================
echo "🚀 Transferring control to STEWARD (Mission Control)..."
echo "════════════════════════════════════════════════════════════════"
echo ""

# The primary system prompt is displayed via the Mission Control Dashboard
# This replaces the old hardcoded SYSTEMPROMPT block.
python3 bin/mission status 2>&1 || echo "⚠️  Mission Control not initialized (run scripts/bootstrap_mission.py)"
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
python3 ./vibe-cli boot 2>&1 || echo "⚠️  VIBE-CLI boot check failed (system may need initialization)"

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
echo ""
echo "════════════════════════════════════════════════════════════════"
echo ""

# ============================================================================
# CLEANUP ROADMAP: Show next task if cleanup mode active
# ============================================================================
if [ -f .vibe/config/cleanup_roadmap.json ]; then
    echo "🧹 CLEANUP MODE ACTIVE"
    echo ""
    python3 ./bin/next-task.py
fi
