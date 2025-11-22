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
# NOTE: These are OPTIONAL - only needed for integration tests that use the orchestrator
# Unit tests (like provider tests) should NOT require these dependencies
try:
    import apps.agency.orchestrator as orchestrator_module
    import vibe_core.playbook.executor as executor_module
    import vibe_core.playbook.loader as loader_module
    import vibe_core.playbook.router as router_module
    import vibe_core.runtime.prompt_registry as prompt_registry_module

    sys.modules["orchestrator"] = orchestrator_module
    sys.modules["executor"] = executor_module
    sys.modules["prompt_registry"] = prompt_registry_module
    sys.modules["router"] = router_module
    sys.modules["loader"] = loader_module
    sys.modules["agency_os_orchestrator"] = orchestrator_module
except ImportError:
    # These imports are optional - only needed for orchestrator integration tests
    # Unit tests (providers, utilities) can run without them
    pass

# Load legacy_config_loader dynamically (it's not in the main package)
# NOTE: This is also OPTIONAL - only needed for tests that use legacy config
repo_root = Path(__file__).parent.parent  # Define repo_root for fixtures to use
legacy_config_path = repo_root / "config" / "legacy_config_loader.py"
if legacy_config_path.exists():
    try:
        spec = spec_from_file_location("legacy_config_loader", legacy_config_path)
        if spec and spec.loader:
            legacy_config = module_from_spec(spec)
            sys.modules["legacy_config_loader"] = legacy_config
            spec.loader.exec_module(legacy_config)
    except ImportError:
        # Legacy config loader is optional
        pass

# Load handlers module with fallback
try:
    import apps.agency.orchestrator.handlers as handlers_module

    sys.modules["handlers"] = handlers_module
except ImportError:
    pass  # handlers module might not exist in all configs


@pytest.fixture(scope="function")
def vibe_root():
    """Provide the vibe-agency root directory for tests."""
    return Path(__file__).parent.parent


@pytest.fixture(scope="function", autouse=True)
def clean_test_data(vibe_root):
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
