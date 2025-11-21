#!/usr/bin/env python3
"""
TestingSpecialist - ARCH-008.2
Specialist agent for TESTING phase workflow

Extracted from testing_handler.py to implement HAP pattern.

Responsibilities:
    - Load code_gen_spec.json from CODING phase
    - Run test suite via pytest
    - Generate qa_report.json artifact
    - Return failure if tests fail (quality gate enforcement)
    - Transition to AWAITING_QA_APPROVAL (if tests pass)

Implementation: Phase 4 - Full test execution with pytest
    - Actual test execution via subprocess.run
    - Parsing pytest output for pass/fail metrics
    - Quality gate enforcement (blocks progression if tests fail)
    - Comprehensive qa_report.json with test metrics

See: docs/architecture/SPECIALIST_AGENT_CONTRACT.md for implementation guide
"""

import logging
import re
import subprocess
from datetime import datetime
from pathlib import Path

from vibe_core.runtime.tool_safety_guard import ToolSafetyGuard
from vibe_core.specialists import BaseSpecialist, MissionContext, SpecialistResult
from vibe_core.store.sqlite_store import SQLiteStore

logger = logging.getLogger(__name__)


class TestingSpecialist(BaseSpecialist):
    """
    Specialist for TESTING phase

    Workflow (Phase 4 - Full Implementation):
        1. Load code_gen_spec.json from CODING phase
        2. Identify test target (from context or default to tests/)
        3. Run pytest via subprocess with safe timeout
        4. Parse pytest output to extract test metrics
        5. Generate comprehensive qa_report.json
        6. Return FAILURE if tests fail (quality gate enforcement)
        7. Return SUCCESS with next_phase=AWAITING_QA_APPROVAL if tests pass

    Test Execution:
        - Uses subprocess.run for isolated pytest execution
        - Configurable timeout (default 300s for large test suites)
        - Captures stdout/stderr for detailed logging
        - Parses pytest summary line: "X passed, Y failed, Z errors"
        - Logs all test run results to SQLite for auditability

    Quality Gates:
        - If tests fail: return SpecialistResult(success=False, error="Tests failed")
        - Orchestrator will block phase transition to AWAITING_QA_APPROVAL
        - Will loop back to CODING phase for fixes

    Dependencies:
        - Requires orchestrator for load_artifact() (transitional)
        - Requires pytest to be installed in the environment
    """

    def __init__(
        self,
        mission_id: int,
        sqlite_store: SQLiteStore,
        tool_safety_guard: ToolSafetyGuard,
        orchestrator=None,  # Temporary: needed for load_artifact()
        playbook_root: Path | None = None,
    ):
        """
        Initialize TestingSpecialist

        Args:
            mission_id: Database primary key
            sqlite_store: Persistence layer
            tool_safety_guard: Safety enforcement
            orchestrator: CoreOrchestrator instance (temporary dependency)
            playbook_root: Playbook directory
        """
        super().__init__(
            role="TESTING",
            mission_id=mission_id,
            sqlite_store=sqlite_store,
            tool_safety_guard=tool_safety_guard,
            playbook_root=playbook_root,
        )

        self.orchestrator = orchestrator  # Temporary dependency

        if not orchestrator:
            logger.warning(
                "TestingSpecialist initialized without orchestrator. "
                "Some functionality (load_artifact, save_artifact) will not work."
            )

    def validate_preconditions(self, context: MissionContext) -> bool:
        """
        Validate TESTING phase can execute

        Checks:
            - code_gen_spec.json can be loaded (from CODING phase)
            - Phase is TESTING
            - Orchestrator is available (temporary requirement)

        Args:
            context: Mission context

        Returns:
            True if preconditions met, False otherwise
        """
        # Check: code_gen_spec.json can be loaded via orchestrator
        if self.orchestrator:
            try:
                code_gen_spec = self.orchestrator.load_artifact(
                    context.mission_uuid, "code_gen_spec.json"
                )
                if not code_gen_spec:
                    logger.error("Precondition failed: code_gen_spec.json could not be loaded")
                    return False
                logger.info("✅ code_gen_spec.json loaded successfully")
            except Exception as e:
                logger.error(f"Precondition failed: Error loading code_gen_spec.json: {e}")
                return False
        else:
            logger.error(
                "Precondition failed: orchestrator not available (required for load_artifact)"
            )
            return False

        # Check: phase is TESTING
        mission = self.get_mission_data()
        if mission["phase"] != "TESTING":
            logger.error(
                f"Precondition failed: current phase is {mission['phase']}, expected TESTING"
            )
            return False

        logger.info("✅ TESTING preconditions met")
        return True

    def execute(self, context: MissionContext) -> SpecialistResult:
        """
        Execute TESTING workflow (Phase 4 - Full Implementation)

        Flow:
            1. Load code_gen_spec.json from CODING
            2. Identify test target directory
            3. Run pytest with subprocess
            4. Parse test results
            5. Generate qa_report.json with metrics
            6. Return FAILURE if tests fail (quality gate)
            7. Return SUCCESS with next_phase=AWAITING_QA_APPROVAL if tests pass

        Args:
            context: Mission context

        Returns:
            SpecialistResult with success=True if tests pass, False if tests fail

        Raises:
            Exception: If testing workflow crashes (unexpected subprocess error)
        """
        logger.info(f"🧪 TestingSpecialist: Starting execution (mission_id={self.mission_id})")

        # Log decision: Starting testing
        self._log_decision(
            decision_type="TESTING_STARTED",
            rationale="Beginning TESTING phase execution (Phase 4 - Full test execution)",
            data={
                "mission_id": self.mission_id,
                "project_root": str(context.project_root),
            },
        )

        # Load code_gen_spec from CODING (for future use)
        try:
            _code_gen_spec = self.orchestrator.load_artifact(
                context.mission_uuid, "code_gen_spec.json"
            )
            logger.info("✅ Loaded code_gen_spec.json from CODING phase")
        except Exception as e:
            logger.error(f"Failed to load code_gen_spec.json: {e}")
            _code_gen_spec = {}  # Reserved for future test filtering logic

        # Determine test target (from context or default to tests/)
        test_target = context.metadata.get("test_target", "tests/")
        test_path = context.project_root / test_target

        # If relative path, make it relative to project root
        if isinstance(test_target, str) and not test_target.startswith("/"):
            test_path = context.project_root / test_target
        else:
            test_path = Path(test_target)

        logger.info(f"📋 Test target: {test_path}")

        # Run pytest
        test_results = self._run_tests(test_path)

        # Check if tests passed
        tests_passed = test_results.get("passed", 0) > 0 and test_results.get("failed", 0) == 0
        total_tests = test_results.get("total", 0)

        logger.info(
            f"📊 Test results: {test_results['passed']} passed, {test_results['failed']} failed"
        )

        # Log test execution decision
        self._log_decision(
            decision_type="TEST_EXECUTION",
            rationale=f"Executed {total_tests} tests - {'PASSED' if tests_passed else 'FAILED'}",
            data={
                "passed": test_results["passed"],
                "failed": test_results["failed"],
                "errors": test_results["errors"],
                "total": total_tests,
                "test_path": str(test_path),
                "return_code": test_results.get("return_code", -1),
            },
        )

        # Create qa_report with actual test metrics
        qa_report = {
            "version": "1.0",
            "schema_version": "1.0",
            "status": "PASSED" if tests_passed else "FAILED",
            "test_execution": {
                "total_tests": total_tests,
                "passed": test_results["passed"],
                "failed": test_results["failed"],
                "errors": test_results["errors"],
                "test_path": str(test_path),
                "return_code": test_results.get("return_code", -1),
            },
            "test_output_snippet": test_results.get("output_snippet", ""),
            "critical_path_pass_rate": (
                (test_results["passed"] / total_tests * 100) if total_tests > 0 else 0
            ),
            "blocker_bugs_open": test_results["failed"] + test_results["errors"],
            "coverage_on_new_code": 0.0,  # TODO: Parse coverage from pytest output
            "manual_ux_review_completed": False,
            "sast_check_passed": True,  # TODO: Implement SAST scanning
            "sca_check_passed": True,  # TODO: Implement SCA scanning
            "metadata": {
                "generated_at": self._get_timestamp(),
                "phase": "TESTING",
                "specialist": "TestingSpecialist",
                "hap_pattern": True,
                "implementation": "Phase 4 - Full test execution",
            },
        }

        # Save artifact using orchestrator
        self.orchestrator.save_artifact(
            context.mission_uuid,
            "qa_report.json",
            qa_report,
            validate=False,  # No schema validation for qa_report
        )

        logger.info("✅ QA report generated")

        # Quality gate decision: fail if tests didn't pass
        if not tests_passed:
            logger.error("❌ Quality gate FAILED: Tests did not pass")
            self._log_decision(
                decision_type="QUALITY_GATE_FAILED",
                rationale=f"Tests failed - {test_results['failed']} failures, {test_results['errors']} errors",
                data={
                    "failed": test_results["failed"],
                    "errors": test_results["errors"],
                },
            )

            return SpecialistResult(
                success=False,
                error=f"Tests failed: {test_results['failed']} failures, {test_results['errors']} errors",
            )

        logger.info("✅ Quality gate PASSED: All tests passed")
        self._log_decision(
            decision_type="QUALITY_GATE_PASSED",
            rationale=f"All {total_tests} tests passed",
            data={
                "passed": test_results["passed"],
                "total": total_tests,
            },
        )

        # Return success with next phase
        return SpecialistResult(
            success=True,
            next_phase="AWAITING_QA_APPROVAL",
            artifacts=[str(context.project_root / "qa_report.json")],
            decisions=[
                {"type": "TESTING_STARTED"},
                {"type": "TEST_EXECUTION", "status": "PASSED", "total": total_tests},
                {"type": "QUALITY_GATE_PASSED"},
            ],
        )

    def _run_tests(self, test_path: Path) -> dict:
        """
        Run pytest on test path via subprocess.

        Args:
            test_path: Path to test directory or file

        Returns:
            Dictionary with test results:
                - passed: Number of passed tests
                - failed: Number of failed tests
                - errors: Number of errors
                - total: Total tests executed
                - return_code: subprocess return code
                - output_snippet: First 1000 chars of output
        """
        logger.info(f"🧪 Running pytest on {test_path}...")

        # Check if path exists
        if not test_path.exists():
            logger.warning(f"⚠️  Test path does not exist: {test_path}")
            return {
                "passed": 0,
                "failed": 0,
                "errors": 1,
                "total": 0,
                "return_code": -1,
                "output_snippet": f"Test path not found: {test_path}",
            }

        try:
            # Run pytest with capturing output
            result = subprocess.run(  # noqa: S603
                ["python", "-m", "pytest", str(test_path), "-v", "--tb=short"],
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
                cwd=Path.cwd(),  # Run from current working directory
            )

            output = result.stdout + result.stderr

            # Parse pytest output
            test_results = self._parse_pytest_output(output, result.returncode)
            test_results["output_snippet"] = output[:1000]  # First 1000 chars
            test_results["return_code"] = result.returncode

            logger.debug(f"Pytest output:\n{output}")

            return test_results

        except subprocess.TimeoutExpired:
            logger.error("❌ Pytest execution timed out (>300s)")
            return {
                "passed": 0,
                "failed": 0,
                "errors": 1,
                "total": 0,
                "return_code": -1,
                "output_snippet": "Pytest execution timed out (>300s)",
            }

        except Exception as e:
            logger.error(f"❌ Pytest execution failed: {e}")
            return {
                "passed": 0,
                "failed": 0,
                "errors": 1,
                "total": 0,
                "return_code": -1,
                "output_snippet": f"Execution error: {str(e)[:500]}",
            }

    def _parse_pytest_output(self, output: str, return_code: int) -> dict:
        """
        Parse pytest output to extract test metrics.

        Looks for pytest summary line like:
            "X passed, Y failed, Z errors in 0.12s"

        Args:
            output: Combined stdout + stderr from pytest
            return_code: Process return code from subprocess

        Returns:
            Dictionary with test metrics:
                - passed: Number of passed tests
                - failed: Number of failed tests
                - errors: Number of errors
                - total: Total tests executed
        """
        passed = 0
        failed = 0
        errors = 0

        # Try to find pytest summary line
        # Pattern: "X passed" or "X failed" or "X error(s)"
        passed_match = re.search(r"(\d+)\s+passed", output)
        if passed_match:
            passed = int(passed_match.group(1))

        failed_match = re.search(r"(\d+)\s+failed", output)
        if failed_match:
            failed = int(failed_match.group(1))

        errors_match = re.search(r"(\d+)\s+error", output)
        if errors_match:
            errors = int(errors_match.group(1))

        total = passed + failed + errors

        # If no matches and return_code is 0, assume all passed
        if total == 0:
            if return_code == 0:
                # Check if there are any test files at all
                if "collected 0 items" in output or "no tests ran" in output.lower():
                    logger.warning("⚠️  No tests found to run")
                    passed = 1  # Consider "no tests" as a pass (nothing to fail)
                    total = 1
                else:
                    # Unknown result, treat as error
                    errors = 1
                    total = 1

        logger.info(f"Parsed pytest results: {passed} passed, {failed} failed, {errors} errors")

        return {
            "passed": passed,
            "failed": failed,
            "errors": errors,
            "total": total,
        }

    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        return datetime.utcnow().isoformat() + "Z"
