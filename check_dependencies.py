#!/usr/bin/env python3
"""
Check Dependencies Script - Prevents NECK BREAKERS

This script validates that all required Python dependencies are installed
before code execution. Run this before committing or running the system.

Usage:
    python3 check_dependencies.py          # Check and report
    python3 check_dependencies.py --strict # Exit non-zero if missing
"""

import sys
import importlib
from typing import List, Tuple

# Define required dependencies
# Format: (import_name, package_name, is_critical)
DEPENDENCIES = [
    # Runtime dependencies (CRITICAL - code will crash without these)
    ("yaml", "pyyaml", True),
    ("anthropic", "anthropic", True),
    ("bs4", "beautifulsoup4", True),
    ("requests", "requests", True),

    # Dev dependencies (WARNING - tests/tools won't work)
    ("pytest", "pytest", False),
    ("black", "black", False),
    ("ruff", "ruff", False),
]

def check_dependency(module_name: str, package_name: str) -> bool:
    """Check if a Python module can be imported."""
    try:
        importlib.import_module(module_name)
        return True
    except ImportError:
        return False

def main() -> int:
    """Check all dependencies and report status."""
    strict_mode = "--strict" in sys.argv

    missing_critical: List[Tuple[str, str]] = []
    missing_optional: List[Tuple[str, str]] = []

    print("🔍 Checking Python dependencies...\n")

    # Check each dependency
    for module_name, package_name, is_critical in DEPENDENCIES:
        installed = check_dependency(module_name, package_name)

        if installed:
            print(f"✅ {package_name:20s} - installed")
        else:
            if is_critical:
                print(f"❌ {package_name:20s} - MISSING (CRITICAL)")
                missing_critical.append((module_name, package_name))
            else:
                print(f"⚠️  {package_name:20s} - missing (optional)")
                missing_optional.append((module_name, package_name))

    print()

    # Report critical missing dependencies
    if missing_critical:
        print("=" * 70)
        print("🚨 CRITICAL: Missing runtime dependencies!")
        print("   These are NECK BREAKERS - code will crash at runtime!")
        print()
        print("   Missing packages:")
        for _, package_name in missing_critical:
            print(f"   - {package_name}")
        print()
        print("   Fix with:")
        print("   pip install -r requirements.txt")
        print("   OR:")
        print(f"   pip install {' '.join(pkg for _, pkg in missing_critical)}")
        print("=" * 70)
        return 1

    # Report optional missing dependencies
    if missing_optional:
        print("⚠️  WARNING: Missing optional dependencies")
        print("   Tests and development tools may not work")
        print()
        print("   Missing packages:")
        for _, package_name in missing_optional:
            print(f"   - {package_name}")
        print()
        print("   Fix with:")
        print("   pip install -r requirements.txt")
        print()

        if strict_mode:
            return 1

    # All good!
    print("✅ All critical dependencies installed!")

    if not missing_optional:
        print("✅ All optional dependencies installed!")

    return 0

if __name__ == "__main__":
    sys.exit(main())
