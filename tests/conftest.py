"""Pytest configuration for vibe-agency tests."""

import sys
from pathlib import Path

# Add project root to sys.path
repo_root = Path(__file__).parent.parent
sys.path.insert(0, str(repo_root))
