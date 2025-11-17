#!/bin/bash
#
# show-status.sh - ONE COMMAND for full system context
#
# ZERO FRICTION: Everything you need to know in one command
#
# Displays:
# - Session handoff (what was done, what's next)
# - System status (git, linting, tests)
# - Test results (live smoke check)
# - TODO summary (code + docs)
# - Architecture completion (GAD/VAD/LAD)
# - Recent activity (last 3 commits)
# - Quick action commands
#
# Usage: ./bin/show-status.sh
#

set -e

# Just call the Python script - it does everything
./bin/show-context.py

# Optional: Show additional context if requested
if [ "$1" = "--verbose" ] || [ "$1" = "-v" ]; then
    echo ""
    echo "━━━ DETAILED STATS ━━━"
    echo ""
    
    # File counts
    echo "Repository stats:"
    echo "  Python files: $(find agency_os -name '*.py' | wc -l)"
    echo "  Test files: $(find tests -name '*.py' | wc -l)"
    echo "  Documentation: $(find docs -name '*.md' | wc -l)"
    echo "  Lines of code: $(find agency_os -name '*.py' -exec cat {} \; | wc -l)"
    echo ""
    
    # Recent test runs
    if [ -f ".pytest_cache/v/cache/lastfailed" ]; then
        echo "Last test failures:"
        cat .pytest_cache/v/cache/lastfailed | head -5
        echo ""
    fi
fi
