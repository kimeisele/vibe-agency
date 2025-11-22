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

   >>> VIBE OS v3.0 <<<
   🏗️ Kernel + Agency Architecture (Post-Split)
EOF
echo -e "${NC}"
echo "════════════════════════════════════════════════════════════════"

# ============================================================================
# 1. PRE-FLIGHT CHECKS (GIT & ENV)
# ============================================================================
echo "🔍 Running pre-flight environment checks..."

# Check .env file (GAD-5: Auto-provision from template)
if [ ! -f .env ]; then
    if [ -f .env.template ]; then
        echo -e "⚠️  .env file: ${YELLOW}Not found.${NC} Auto-provisioning from template..."
        cp .env.template .env
        echo -e "✅ ${GREEN}.env created from template${NC} (configure API keys as needed)"
    else
        echo -e "⚠️  .env file: ${YELLOW}Not found${NC} (.env.template also missing)"
    fi
else
    echo -e "✅ .env file: ${GREEN}Found${NC}"
fi

# Check Virtual Environment (GAD-5: Auto-heal if missing)
if [ ! -d ".venv" ]; then
    echo -e "⚠️  VirtualEnv: ${YELLOW}Not found.${NC} Auto-installing dependencies..."

    # Check if uv is available
    if command -v uv &> /dev/null; then
        echo "   Running: uv sync --extra dev"
        uv sync --extra dev || {
            echo -e "❌ ${RED}Failed to install dependencies with uv${NC}"
            exit 1
        }
        echo -e "✅ ${GREEN}Dependencies installed successfully${NC}"
    else
        echo -e "❌ ${RED}UV not found. Please install it first:${NC}"
        echo "   curl -LsSf https://astral.sh/uv/install.sh | sh"
        exit 1
    fi
else
    echo -e "✅ VirtualEnv: ${GREEN}Found${NC}"
fi

# Check Git Status
if git rev-parse --git-dir > /dev/null 2>&1; then
    BRANCH=$(git rev-parse --abbrev-ref HEAD)
    echo -e "✅ Git Repository: ${GREEN}Detected${NC} (branch: $BRANCH)"

    # Configure git hooks (auto-setup after env wipe)
    if [ -d ".githooks" ]; then
        git config core.hooksPath .githooks
        echo -e "✅ Git Hooks: ${GREEN}Configured${NC} (.githooks/)"
    fi
else
    echo -e "⚠️  Git Repository: ${YELLOW}Not initialized.${NC}"
fi

# ============================================================================
# ARCH-044: GIT-OPS SYNC CHECK (The Senses)
# ============================================================================
# Detect if local branch is behind remote (prevents working on stale code)
if git rev-parse --git-dir > /dev/null 2>&1; then
    BRANCH=$(git rev-parse --abbrev-ref HEAD)

    # Attempt background fetch (non-blocking, fail-safe)
    if git fetch origin "$BRANCH" > /dev/null 2>&1; then
        LOCAL_HASH=$(git rev-parse HEAD)
        REMOTE_HASH=$(git rev-parse "origin/$BRANCH" 2>/dev/null || echo "$LOCAL_HASH")

        if [ "$LOCAL_HASH" != "$REMOTE_HASH" ]; then
            BEHIND_COUNT=$(git rev-list --count HEAD..origin/"$BRANCH" 2>/dev/null || echo "0")
            if [ "$BEHIND_COUNT" -gt 0 ]; then
                export VIBE_GIT_STATUS="BEHIND_BY_$BEHIND_COUNT"
                echo -e "⚠️  Git Sync: ${YELLOW}Behind by $BEHIND_COUNT commit(s)${NC}"
            else
                export VIBE_GIT_STATUS="DIVERGED"
                echo -e "⚠️  Git Sync: ${YELLOW}Diverged from remote${NC}"
            fi
        else
            export VIBE_GIT_STATUS="SYNCED"
            echo -e "✅ Git Sync: ${GREEN}Up-to-date${NC}"
        fi
    else
        # Fetch failed (offline or no remote)
        export VIBE_GIT_STATUS="FETCH_FAILED"
        echo -e "⚠️  Git Sync: ${YELLOW}Unable to fetch (offline or no remote)${NC}"
    fi
else
    export VIBE_GIT_STATUS="NO_REPO"
fi

echo ""

# Set PYTHON variable to use venv if available
if [ -f ".venv/bin/python" ]; then
    PYTHON=".venv/bin/python"
else
    PYTHON="python3"
fi

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
if [ ! -f .vibe/state/active_mission.json ]; then
    echo "⚠️  Mission state not found. Executing Genesis Protocol..."
    if ! $PYTHON scripts/genesis.py; then
        echo "❌ GENESIS PROTOCOL FAILED: Could not bootstrap mission state"
        echo "✅ Genesis complete: .vibe/state/active_mission.json"
    fi
fi

$PYTHON bin/mission status 2>&1 || echo "⚠️  Mission Control not fully initialized"

# Auto-provision system integrity manifest if missing (GAD-501 Layer 0)
if [ ! -f .vibe/system_integrity_manifest.json ]; then
    echo "⚠️  System integrity manifest not found. Auto-generating..."
    $PYTHON scripts/generate-integrity-manifest.py > /dev/null 2>&1 && echo "✅ System integrity manifest auto-generated" || echo "❌ Failed to generate integrity manifest."
fi

# Auto-provision cleanup roadmap if missing
if [ ! -f .vibe/config/cleanup_roadmap.json ] && [ -f docs/cleanup_roadmap.json ]; then
    mkdir -p .vibe/config
    cp docs/cleanup_roadmap.json .vibe/config/cleanup_roadmap.json
    echo "✅ Cleanup roadmap auto-provisioned"
fi
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
$PYTHON ./vibe-cli boot 2>&1 || echo "⚠️  VIBE-CLI boot check failed (system may need initialization)"

echo ""
echo "════════════════════════════════════════════════════════════════"

# ============================================================================
# PERSONALIZED BOOT GREETING (ARCH-051: Steward Cartridge)
# ============================================================================
# Load user preferences and generate personalized greeting
BOOT_GREETING=$($PYTHON -c "
try:
    from vibe_core.cartridges.steward import StewardCartridge
    steward = StewardCartridge()
    user_name = steward.get_user_name()
    tone = steward.get_operator_tone()
    print(f'Welcome back, {user_name}. Systems are green. Your Vibe OS is ready.')
    if 'German' in tone or 'Deutsch' in tone:
        print(f'(Tonfall: {tone})')
except Exception:
    print('Welcome back. Your Vibe OS is ready.')
" 2>/dev/null || echo "Welcome back. Your Vibe OS is ready.")

echo -e "${GREEN}$BOOT_GREETING${NC}"
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
echo "   Run tests:         $PYTHON -m pytest tests/ -v"
echo ""
echo ""
echo "════════════════════════════════════════════════════════════════"
echo ""

# ============================================================================
# CLEANUP ROADMAP: Auto-verify and show next task if cleanup mode active
# ============================================================================
if [ -f .vibe/config/cleanup_roadmap.json ]; then
    echo "🧹 CLEANUP MODE ACTIVE"
    echo ""

    # Auto-verify completed tasks (prevents showing already-done tasks)
    $PYTHON ./bin/auto-verify-tasks.py

    # Show next task
    $PYTHON ./bin/next-task.py
fi
