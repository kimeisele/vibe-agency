#!/bin/bash
#
# VIBE OS BOOTLOADER (v1.0.1)
# ------------------------------------------------------------------
# Philosophy: The Shell prepares the stage. The Kernel plays the show.
# No business logic in Bash. All intelligence in Python.
# ------------------------------------------------------------------

set -euo pipefail

# 1. VISUAL INIT
# ------------------------------------------------------------------
# Clear only if interactive
if [ -t 1 ]; then clear; fi

CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${CYAN}"
cat << "EOF"
  _    _  _  _              ___   ___
 | |  | |(_)| |__   ___    / _ \ / __|
 | |  | || || '_ \ / _ \  | | | |\__ \
 \ \/\/ /| || |_) ||  __/ | |_| ||___/
  \_/\_/ |_||_.__/  \___|  \___/

  >> OPERATING SYSTEM v1.0.1-citizen <<
EOF
echo -e "${NC}"

# 2. ENVIRONMENT INTEGRITY (GAD-100)
# ------------------------------------------------------------------
# Ensure .env exists
if [ ! -f .env ]; then
    if [ -f .env.template ]; then
        cp .env.template .env
        echo -e "🔧 Bootloader: ${YELLOW}.env created from template.${NC}"
    else
        echo -e "🚨 Bootloader: ${RED}CRITICAL - .env.template missing.${NC}"
        exit 1
    fi
fi

# Ensure UV/Venv is healthy
if [ ! -d ".venv" ] || [ ! -f "uv.lock" ]; then
    echo -e "🔧 Bootloader: ${YELLOW}Initializing Python Environment...${NC}"
    if command -v uv &> /dev/null; then
        uv sync --extra dev > /dev/null 2>&1 || { echo -e "🚨 Bootloader: ${RED}Dependency install failed.${NC}"; exit 1; }
    else
        echo -e "🚨 Bootloader: ${RED}uv not installed. Run: curl -LsSf https://astral.sh/uv/install.sh | sh${NC}"
        exit 1
    fi
fi

# 3. THE SENSES: GIT AWARENESS (ARCH-044)
# ------------------------------------------------------------------
# Detect sync status quietly. Export to ENV for Kernel Consumption.
if git rev-parse --git-dir > /dev/null 2>&1; then
    # Non-blocking fetch in background
    git fetch origin "$(git rev-parse --abbrev-ref HEAD)" > /dev/null 2>&1 &
    FETCH_PID=$!

    # Give it 1 second, then move on (don't block boot)
    disown $FETCH_PID 2>/dev/null || true

    LOCAL=$(git rev-parse HEAD)
    REMOTE=$(git rev-parse "@{u}" 2>/dev/null || echo "$LOCAL")

    if [ "$LOCAL" != "$REMOTE" ]; then
        COUNT=$(git rev-list --count HEAD..@{u} 2>/dev/null || echo "0")
        export VIBE_GIT_STATUS="BEHIND_BY_$COUNT"
    else
        export VIBE_GIT_STATUS="SYNCED"
    fi
else
    export VIBE_GIT_STATUS="NO_REPO"
fi

# 4. HANDOVER TO KERNEL
# ------------------------------------------------------------------
# We use 'exec' to replace the shell process with Python.
# This saves memory and passes signals (Ctrl+C) correctly.

# Determine entry point
if [ -f "apps/agency/cli.py" ]; then
    ENTRYPOINT="apps/agency/cli.py"
else
    echo -e "🚨 Bootloader: ${RED}Kernel Entrypoint not found.${NC}"
    exit 1
fi

# LAUNCH VIBE OS
# Running without arguments enters interactive mode (ARCH-032)
exec uv run python "$ENTRYPOINT"
