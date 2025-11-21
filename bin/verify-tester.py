#!/usr/bin/env python3
"""
Verification Script: TestingSpecialist Self-Test

This script verifies that the TestingSpecialist can:
1. Be instantiated with proper dependencies
2. Run pytest on a known passing test file
3. Parse pytest output correctly
4. Report success/failure appropriately

Run this after implementing TestingSpecialist to verify functionality.
"""

import logging
import sys
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from apps.agency.specialists.testing import TestingSpecialist  # noqa: E402
from vibe_core.runtime.tool_safety_guard import ToolSafetyGuard  # noqa: E402
from vibe_core.store.sqlite_store import SQLiteStore  # noqa: E402


def main():
    """Run verification tests"""
    logger.info("=" * 60)
    logger.info("TestingSpecialist Self-Verification")
    logger.info("=" * 60)

    # Initialize dependencies
    logger.info("\n1. Initializing dependencies...")
    try:
        db_path = PROJECT_ROOT / ".vibe" / "state" / "test_verify_tester.db"
        db_path.parent.mkdir(parents=True, exist_ok=True)

        store = SQLiteStore(str(db_path))
        guard = ToolSafetyGuard()
        logger.info("   ✅ Dependencies initialized")
    except Exception as e:
        logger.error(f"   ❌ Failed to initialize dependencies: {e}")
        return False

    # Create mock orchestrator (minimal for testing)
    logger.info("\n2. Creating mock orchestrator...")
    try:
        from unittest.mock import MagicMock

        orchestrator = MagicMock()
        orchestrator.load_artifact.return_value = {"version": "1.0", "status": "PASSED"}
        orchestrator.save_artifact.return_value = None
        logger.info("   ✅ Mock orchestrator created")
    except Exception as e:
        logger.error(f"   ❌ Failed to create mock orchestrator: {e}")
        return False

    # Initialize TestingSpecialist
    logger.info("\n3. Initializing TestingSpecialist...")
    try:
        specialist = TestingSpecialist(
            mission_id=1,
            sqlite_store=store,
            tool_safety_guard=guard,
            orchestrator=orchestrator,
        )
        logger.info("   ✅ TestingSpecialist initialized")
    except Exception as e:
        logger.error(f"   ❌ Failed to initialize TestingSpecialist: {e}")
        return False

    # Test _parse_pytest_output method
    logger.info("\n4. Testing pytest output parsing...")
    try:
        # Test case 1: Passing tests
        output1 = "tests/test_example.py::test_one PASSED\n"
        output1 += "tests/test_example.py::test_two PASSED\n"
        output1 += "======================== 2 passed in 0.12s ========================\n"
        result1 = specialist._parse_pytest_output(output1, return_code=0)
        assert result1["passed"] == 2, f"Expected 2 passed, got {result1['passed']}"
        assert result1["failed"] == 0, f"Expected 0 failed, got {result1['failed']}"
        logger.info("   ✅ Parse passing tests: 2 passed, 0 failed")

        # Test case 2: Failing tests
        output2 = "tests/test_example.py::test_one PASSED\n"
        output2 += "tests/test_example.py::test_two FAILED\n"
        output2 += "======================== 1 passed, 1 failed in 0.12s ========================\n"
        result2 = specialist._parse_pytest_output(output2, return_code=1)
        assert result2["passed"] == 1, f"Expected 1 passed, got {result2['passed']}"
        assert result2["failed"] == 1, f"Expected 1 failed, got {result2['failed']}"
        logger.info("   ✅ Parse failing tests: 1 passed, 1 failed")

        # Test case 3: No tests
        output3 = "collected 0 items\n"
        result3 = specialist._parse_pytest_output(output3, return_code=0)
        logger.info(f"   ✅ Parse no tests: {result3['passed']} passed, {result3['failed']} failed")

    except AssertionError as e:
        logger.error(f"   ❌ Parse test failed: {e}")
        return False
    except Exception as e:
        logger.error(f"   ❌ Unexpected error in parsing test: {e}")
        return False

    # Test actual pytest execution on real test files
    logger.info("\n5. Testing actual pytest execution...")
    try:
        # Run pytest on a small test file (use existing tests)
        test_file = PROJECT_ROOT / "tests" / "test_archive.py"
        if test_file.exists():
            logger.info(f"   Running pytest on {test_file.name}...")
            result = specialist._run_tests(test_file)
            logger.info(
                f"   ✅ Pytest execution completed: "
                f"{result['passed']} passed, {result['failed']} failed"
            )
        else:
            logger.warning(f"   ⚠️  Test file not found: {test_file}")

    except Exception as e:
        logger.error(f"   ❌ Pytest execution failed: {e}")
        return False

    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("✅ TestingSpecialist Verification PASSED")
    logger.info("=" * 60)
    logger.info("\nNext steps:")
    logger.info("  1. Run: uv run pytest tests/test_testing_workflow.py -v")
    logger.info("  2. Verify all tests pass")
    logger.info("  3. Check artifacts are created correctly")

    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
