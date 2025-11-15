#!/bin/bash
# ============================================================================
# LAYER 3: MANUAL DEPENDENCY SETUP (Fallback)
# ============================================================================
# Usage: ./setup.sh
#
# This is a manual fallback for environments where auto-install fails.
# Part of 4-layer dependency defense strategy.

set -e  # Exit on any error

echo "🔧 Vibe Agency - Environment Setup"
echo "=================================="

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | grep -oP '\d+\.\d+')
REQUIRED_VERSION="3.11"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo "⚠️  Warning: Python $PYTHON_VERSION detected (recommended: 3.11+)"
fi

# Install dependencies
echo ""
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Validate knowledge bases
echo ""
echo "🔍 Validating knowledge bases..."
if [ -f "validate_knowledge_index.py" ]; then
    python3 validate_knowledge_index.py
else
    echo "⚠️  validate_knowledge_index.py not found (skipping)"
fi

# Success
echo ""
echo "✅ Environment ready!"
echo ""
echo "Next steps:"
echo "  ./vibe-cli run <project-id>     # Run a project"
echo "  pytest tests/ -v                 # Run tests"
echo ""
