"""Pytest configuration for vibe-agency tests.

With proper package installation (uv pip install -e .), all imports work naturally.
No sys.path manipulation needed.
"""

import sqlite3
import sys
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

import pytest

# Legacy backward compatibility: Create module aliases for old test code
# These map old bare imports to new package imports
try:
    import agency_os.core_system.orchestrator as orchestrator_module
    import agency_os.core_system.playbook.executor as executor_module
    import agency_os.core_system.playbook.loader as loader_module
    import agency_os.core_system.playbook.router as router_module
    import agency_os.core_system.runtime.prompt_registry as prompt_registry_module

    sys.modules["orchestrator"] = orchestrator_module
    sys.modules["executor"] = executor_module
    sys.modules["prompt_registry"] = prompt_registry_module
    sys.modules["router"] = router_module
    sys.modules["loader"] = loader_module
    sys.modules["agency_os_orchestrator"] = orchestrator_module
except ImportError as e:
    # If package not installed, provide helpful error message
    print(
        f"\n❌ Import error: {e}\n"
        "Please install the package in editable mode:\n"
        "  uv pip install -e .\n"
        "Or:\n"
        "  make install\n"
    )
    raise

# Load legacy_config_loader dynamically (it's not in the main package)
repo_root = Path(__file__).parent.parent
legacy_config_path = repo_root / "config" / "legacy_config_loader.py"
if legacy_config_path.exists():
    spec = spec_from_file_location("legacy_config_loader", legacy_config_path)
    if spec and spec.loader:
        legacy_config = module_from_spec(spec)
        sys.modules["legacy_config_loader"] = legacy_config
        spec.loader.exec_module(legacy_config)

# Load handlers module with fallback
try:
    import agency_os.core_system.orchestrator.handlers as handlers_module

    sys.modules["handlers"] = handlers_module
except ImportError:
    pass  # handlers module might not exist in all configs


@pytest.fixture(scope="function", autouse=True)
def clean_test_data():
    """
    Clean up test data from SQLite before each test.

    This ensures tests start with a clean slate and don't have
    stale mission data from previous runs.
    """
    import time

    db_path = repo_root / ".vibe" / "state" / "vibe_agency.db"

    def cleanup_with_retry(max_retries=3):
        """Clean SQLite with retry on database lock"""
        for attempt in range(max_retries):
            try:
                conn = sqlite3.connect(db_path, timeout=5.0)
                cursor = conn.cursor()

                # Delete test missions and related data
                cursor.execute("DELETE FROM missions WHERE mission_uuid LIKE 'test_%'")
                cursor.execute(
                    "DELETE FROM decisions WHERE mission_id IN (SELECT id FROM missions WHERE mission_uuid LIKE 'test_%')"
                )
                cursor.execute(
                    "DELETE FROM artifacts WHERE mission_id IN (SELECT id FROM missions WHERE mission_uuid LIKE 'test_%')"
                )

                conn.commit()
                conn.close()
                return True
            except sqlite3.OperationalError as e:
                if "locked" in str(e) and attempt < max_retries - 1:
                    time.sleep(0.1 * (attempt + 1))  # Exponential backoff
                    continue
                # Ignore on last attempt or other errors
                return False
            except Exception:
                return False

    if db_path.exists():
        cleanup_with_retry()

    yield  # Run the test

    # Cleanup after test as well
    if db_path.exists():
        cleanup_with_retry()
