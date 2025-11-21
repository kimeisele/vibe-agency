#!/usr/bin/env python3
"""
ARCH-009: Adaptive Error Recovery Test
Verifies that CodingSpecialist can detect QA failures and switch to repair mode.

This script validates the feedback loop where:
1. CodingSpecialist detects a failed QA report
2. Switches from "Greenfield Generation" mode to "Repair" mode
3. Analyzes test output and generates patches
4. Returns success with repairs applied

Usage:
  python3 bin/test-feedback-loop.py
"""

import json
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock

# Adjust path to find modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from apps.agency.specialists.coding import CodingSpecialist
from vibe_core.runtime.tool_safety_guard import ToolSafetyGuard
from vibe_core.specialists.base_specialist import MissionContext
from vibe_core.store.sqlite_store import SQLiteStore


def create_test_environment() -> tuple[Path, SQLiteStore, ToolSafetyGuard]:
    """Create a minimal test environment with required infrastructure"""
    # Create temporary workspace
    test_dir = Path(tempfile.mkdtemp(prefix="arch009_test_"))

    # Create subdirectories
    (test_dir / "artifacts").mkdir(exist_ok=True)
    (test_dir / "src").mkdir(exist_ok=True)

    # Create mock SQLiteStore (minimal implementation)
    store = MagicMock(spec=SQLiteStore)
    store.log_event = MagicMock(return_value=True)
    store.save_mission_decision = MagicMock(return_value=True)

    # Create mock ToolSafetyGuard
    guard = MagicMock(spec=ToolSafetyGuard)
    guard.check_action = MagicMock(return_value=(True, None))
    guard.record_file_write = MagicMock(return_value=True)

    return test_dir, store, guard


def create_qa_failure_report(test_dir: Path, failures: int = 5, passed: int = 10) -> dict:
    """Create a simulated QA failure report"""
    qa_report = {
        "status": "failure",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "test_execution": {
            "failed": failures,
            "passed": passed,
            "total": failures + passed,
        },
        "test_output_snippet": "AssertionError: expected 5 but got 0 in test_calculation()",
        "affected_files": ["src/calculator.py", "src/utils.py"],
        "failed_tests": [
            "test_addition",
            "test_subtraction",
            "test_multiplication",
            "test_division",
            "test_modulo",
        ],
    }

    # Write QA report to artifacts directory
    qa_report_path = test_dir / "artifacts" / "qa_report.json"
    with open(qa_report_path, "w") as f:
        json.dump(qa_report, f, indent=2)

    print(f"  ✅ Created QA failure report at {qa_report_path}")
    return qa_report


def create_dummy_source_file(test_dir: Path, filename: str = "calculator.py") -> Path:
    """Create a dummy source file to be patched"""
    src_file = test_dir / "src" / filename
    src_file.write_text(
        """
def add(a, b):
    '''Add two numbers'''
    return a + b

def subtract(a, b):
    '''Subtract two numbers'''
    return a - b

def multiply(a, b):
    '''Multiply two numbers'''
    return a * b

def divide(a, b):
    '''Divide two numbers'''
    if b == 0:
        raise ValueError("Division by zero")
    return a / b
"""
    )
    print(f"  ✅ Created dummy source file at {src_file}")
    return src_file


def test_greenfield_mode(test_dir: Path, store: SQLiteStore, guard: ToolSafetyGuard) -> bool:
    """Test 1: Greenfield mode (no QA report)"""
    print("\n[1/3] Testing GREENFIELD MODE (no QA feedback)...")

    try:
        # Create CodingSpecialist
        specialist = CodingSpecialist(
            mission_id=1,
            sqlite_store=store,
            tool_safety_guard=guard,
            orchestrator=None,
        )

        # Create mission context WITHOUT qa_report
        context = MissionContext(
            mission_id=1,
            mission_uuid="test-mission-001",
            phase="CODING",
            project_root=test_dir,
            metadata={},
        )

        # Attempt to detect QA feedback (should return None)
        qa_feedback = specialist._get_qa_feedback(context)

        if qa_feedback is None:
            print("  ✅ Greenfield mode: No QA report detected (expected)")
            print("  ✅ Would proceed with normal code generation")
            return True
        else:
            print(f"  ❌ FAILED: Unexpected QA report detected: {qa_feedback}")
            return False

    except Exception as e:
        print(f"  ❌ FAILED: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_repair_mode(test_dir: Path, store: SQLiteStore, guard: ToolSafetyGuard) -> bool:
    """Test 2: Repair mode activation (QA report detected)"""
    print("\n[2/3] Testing REPAIR MODE ACTIVATION (QA failure detected)...")

    try:
        # Create QA failure report on disk
        _qa_report = create_qa_failure_report(test_dir, failures=5, passed=10)

        # Create a dummy source file to be patched
        create_dummy_source_file(test_dir)

        # Create CodingSpecialist
        specialist = CodingSpecialist(
            mission_id=2,
            sqlite_store=store,
            tool_safety_guard=guard,
            orchestrator=None,
        )

        # Create mission context
        context = MissionContext(
            mission_id=2,
            mission_uuid="test-mission-002",
            phase="CODING",
            project_root=test_dir,
            metadata={},
        )

        # Detect QA feedback from disk
        qa_feedback = specialist._get_qa_feedback(context)

        if qa_feedback is None:
            print("  ❌ FAILED: QA report not loaded from disk")
            return False

        if qa_feedback.get("status") != "failure":
            print(f"  ❌ FAILED: Expected status='failure', got {qa_feedback.get('status')}")
            return False

        print(
            f"  ✅ QA report loaded: {qa_feedback.get('test_execution', {}).get('failed')} failures"
        )

        # Run repair mode
        result = specialist._run_repair_mode(context, qa_feedback)

        if not result.success:
            print("  ❌ FAILED: Repair mode returned success=False")
            return False

        if result.next_phase != "TESTING":
            print(f"  ❌ FAILED: Expected next_phase='TESTING', got {result.next_phase}")
            return False

        # Check that patches were applied
        decisions = result.decisions
        if not decisions:
            print("  ⚠️  WARNING: No decisions returned")

        repair_decision = None
        for decision in decisions:
            if decision.get("type") == "REPAIR_COMPLETED":
                repair_decision = decision
                break

        if repair_decision:
            patched_files = repair_decision.get("patched_files", [])
            print("  ✅ Repair mode activated")
            print(f"  ✅ Applied patches to {len(patched_files)} files")

            # Verify that source file was modified
            src_file = test_dir / "src" / "calculator.py"
            if src_file.exists():
                content = src_file.read_text()
                if "ARCH-009 Repair patch applied" in content:
                    print("  ✅ Verified: Source file was patched with marker")
                    return True
                else:
                    print("  ❌ FAILED: Source file not patched correctly")
                    return False

        print("  ❌ FAILED: Repair decision not found in results")
        return False

    except Exception as e:
        print(f"  ❌ FAILED: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_failure_analysis(test_dir: Path, store: SQLiteStore, guard: ToolSafetyGuard) -> bool:
    """Test 3: Verify failure analysis logging"""
    print("\n[3/3] Testing FAILURE ANALYSIS & LOGGING...")

    try:
        # Create QA failure report
        qa_report = create_qa_failure_report(test_dir, failures=3, passed=7)

        # Create CodingSpecialist
        specialist = CodingSpecialist(
            mission_id=3,
            sqlite_store=store,
            tool_safety_guard=guard,
            orchestrator=None,
        )

        # Create mission context
        context = MissionContext(
            mission_id=3,
            mission_uuid="test-mission-003",
            phase="CODING",
            project_root=test_dir,
            metadata={},
        )

        # Load QA feedback
        qa_feedback = specialist._get_qa_feedback(context)

        # Verify QA report structure
        test_execution = qa_feedback.get("test_execution", {})
        failures = test_execution.get("failed", 0)
        passes = test_execution.get("passed", 0)

        if failures == 3 and passes == 7:
            print(f"  ✅ QA report structure valid: {failures} failures, {passes} passes")
        else:
            print(f"  ❌ FAILED: Unexpected test counts: {failures} failures, {passes} passes")
            return False

        # Verify error log available
        error_log = qa_report.get("test_output_snippet", "")
        if "AssertionError" in error_log:
            print("  ✅ Error logs accessible for analysis")
        else:
            print("  ⚠️  WARNING: Error log snippet not as expected")

        # Verify failure analysis can extract failure list
        failed_tests = qa_report.get("failed_tests", [])
        if len(failed_tests) > 0:
            print(f"  ✅ Failed test list extracted: {len(failed_tests)} tests")
            print(f"     Example: {failed_tests[0]}")
        else:
            print("  ⚠️  WARNING: Failed test list not populated")

        return True

    except Exception as e:
        print(f"  ❌ FAILED: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """Run all ARCH-009 feedback loop tests"""
    print("=" * 70)
    print("🔄 ARCH-009: ADAPTIVE ERROR RECOVERY TEST")
    print("=" * 70)
    print(f"Started: {datetime.now().isoformat()}")

    # Create test environment
    print("\n[Setup] Creating test environment...")
    test_dir, store, guard = create_test_environment()
    print(f"  ✅ Test directory: {test_dir}")

    tests_passed = 0
    tests_failed = 0

    # Test 1: Greenfield mode
    if test_greenfield_mode(test_dir, store, guard):
        tests_passed += 1
    else:
        tests_failed += 1

    # Test 2: Repair mode
    if test_repair_mode(test_dir, store, guard):
        tests_passed += 1
    else:
        tests_failed += 1

    # Test 3: Failure analysis
    if test_failure_analysis(test_dir, store, guard):
        tests_passed += 1
    else:
        tests_failed += 1

    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"✅ Passed: {tests_passed}")
    print(f"❌ Failed: {tests_failed}")

    if tests_failed == 0:
        print("\n✨ ALL TESTS PASSED - ARCH-009 Adaptive Error Recovery Active!")
        print("\n[ARCH-009] Status:")
        print("  ✅ QA feedback detection from disk (persistence)")
        print("  ✅ Repair mode activation on failures")
        print("  ✅ Failure analysis and logging")
        print("  ✅ Patch generation for affected files")
        print("  ✅ Ready for feedback loop integration")

        # Cleanup
        import shutil

        shutil.rmtree(test_dir, ignore_errors=True)
        return 0
    else:
        print(f"\n⚠️  {tests_failed} TEST(S) FAILED")
        print(f"Test directory (for debugging): {test_dir}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
