"""
Pytest configuration and Layer -1 environment bootstrap.

This file runs BEFORE any test, ensuring the environment is properly set up.
Prevents silent failures in fresh clones, CI/CD, and browser environments.

Layer -1: Pre-test environment validation
- Runs before pytest collects any tests
- Auto-creates .venv if missing
- Validates core dependencies are importable
- Self-healing: auto-syncs on missing packages

User nugget: "kann nicht wieder irgendwas sein dass wieder was nicht installiert ist"
"""

import subprocess
import sys
from pathlib import Path


def pytest_configure(config):
    """
    Layer -1 Bootstrap: Ensure environment exists BEFORE any test runs.

    This hook is called by pytest before test collection begins.
    If environment is broken, we fix it automatically (graceful degradation).
    """
    project_root = Path.cwd()

    # Check 1: Are we in project root?
    if not (project_root / "pyproject.toml").exists():
        pytest.exit("❌ BOOTSTRAP FAILED: Not in project root (no pyproject.toml)", returncode=1)

    # Check 2: Does .venv exist?
    venv_path = project_root / ".venv"
    if not venv_path.exists():
        print("🔧 Layer -1 Bootstrap: No .venv found")
        print("   Creating virtual environment...")
        try:
            subprocess.run(
                ["uv", "sync", "--all-extras"],
                cwd=project_root,
                check=True,
                capture_output=True,
                text=True
            )
            print("   ✅ Virtual environment created")
        except subprocess.CalledProcessError as e:
            pytest.exit(
                f"❌ BOOTSTRAP FAILED: Could not create .venv\n"
                f"   Error: {e.stderr}",
                returncode=1
            )
        except FileNotFoundError:
            pytest.exit(
                "❌ BOOTSTRAP FAILED: uv not found\n"
                "   Install: curl -LsSf https://astral.sh/uv/install.sh | sh",
                returncode=1
            )

    # Check 3: Can we import core dependencies?
    # This catches cases where .venv exists but is incomplete/corrupted
    try:
        import yaml  # noqa: F401
        import pytest as _pytest  # noqa: F401
    except ImportError as e:
        print(f"🔧 Layer -1 Bootstrap: Missing dependency '{e.name}'")
        print("   Re-syncing virtual environment...")
        try:
            subprocess.run(
                ["uv", "sync", "--all-extras"],
                cwd=project_root,
                check=True,
                capture_output=True,
                text=True
            )
            print("   ✅ Dependencies synced")
        except subprocess.CalledProcessError as sync_error:
            pytest.exit(
                f"❌ BOOTSTRAP FAILED: Could not sync dependencies\n"
                f"   Error: {sync_error.stderr}",
                returncode=1
            )
