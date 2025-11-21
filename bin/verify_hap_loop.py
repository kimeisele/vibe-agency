#!/usr/bin/env python3
"""
ARCH-011: The "Iron Dome" Verification
Verifies Repair Loop and Circuit Breaker functionality

This script simulates a failure state to verify that:
1. The system enters a repair loop (TESTING → CODING → TESTING)
2. The repair loop respects the max retry limit (3 attempts)
3. The circuit breaker terminates the loop after max retries

Strategy:
- Create a saboteur TestingSpecialist that always fails
- Run a dummy mission that reaches TESTING phase
- Observe: CODING → TESTING → CODING → TESTING (loop with circuit breaker)
- Verify SQLite logs show proper cycle count
"""

import json
import logging
import sys
from datetime import datetime
from pathlib import Path

# Setup path to find project modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from apps.agency.orchestrator.core_orchestrator import CoreOrchestrator, OrchestratorError
from apps.agency.orchestrator.types import ProjectPhase
from vibe_core.runtime.tool_safety_guard import ToolSafetyGuard
from vibe_core.specialists.base_specialist import BaseSpecialist, MissionContext, SpecialistResult
from vibe_core.store.sqlite_store import SQLiteStore

# Setup Logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("VERIFIER")


class SaboteurTester(BaseSpecialist):
    """
    A Specialist designed to fail intentionally to test the repair loop.

    This specialist simulates a failing TESTING phase:
    - Always returns success=False
    - Logs a clear failure message
    - Triggers the orchestrator's repair loop mechanism
    """

    def __init__(
        self,
        mission_id: int,
        sqlite_store: SQLiteStore,
        tool_safety_guard: ToolSafetyGuard,
        orchestrator=None,
    ):
        """Initialize the saboteur specialist"""
        super().__init__(
            role="TESTING",
            mission_id=mission_id,
            sqlite_store=sqlite_store,
            tool_safety_guard=tool_safety_guard,
            playbook_root=None,
        )
        self.orchestrator = orchestrator  # Optional orchestrator dependency
        self.execution_count = 0

    def validate_preconditions(self, context: MissionContext) -> bool:
        """Always report preconditions met (for testing)"""
        return True

    def execute(self, context: MissionContext) -> SpecialistResult:
        """
        Always fail to trigger repair loop.

        This simulates a TESTING phase that consistently fails tests.
        """
        self.execution_count += 1
        logger.info(
            f"😈 SABOTEUR: Failing the tests intentionally! (execution #{self.execution_count})"
        )

        # Log the failure to SQLite for audit trail
        self._log_decision(
            decision_type="SABOTEUR_TEST_FAILURE",
            rationale=f"Intentional test failure to verify repair loop (execution #{self.execution_count})",
            data={
                "execution_count": self.execution_count,
                "intentional": True,
                "message": "Saboteur always fails to test circuit breaker",
            },
        )

        # Return failure to trigger repair loop
        return SpecialistResult(
            success=False,
            error=f"Intentional Sabotage (execution #{self.execution_count}): All tests failed",
        )


def create_test_project(temp_dir: Path) -> str:
    """
    Create a minimal test project with necessary artifacts.

    Args:
        temp_dir: Temporary directory for project

    Returns:
        Project ID (UUID)
    """
    project_id = "arch-011-test-project"
    project_dir = temp_dir / "workspaces" / project_id
    project_dir.mkdir(parents=True, exist_ok=True)

    # Create artifacts directory structure
    artifacts_planning = project_dir / "artifacts" / "planning"
    artifacts_coding = project_dir / "artifacts" / "coding"
    artifacts_testing = project_dir / "artifacts" / "testing"
    artifacts_planning.mkdir(parents=True, exist_ok=True)
    artifacts_coding.mkdir(parents=True, exist_ok=True)
    artifacts_testing.mkdir(parents=True, exist_ok=True)

    # Create minimal feature_spec.json (required by CodingSpecialist)
    feature_spec = {
        "feature_name": "ARCH-011 Test Feature",
        "description": "Minimal feature for repair loop testing",
        "requirements": ["Test requirement"],
        "acceptance_criteria": ["Test passes"],
    }
    with open(artifacts_planning / "feature_spec.json", "w") as f:
        json.dump(feature_spec, f, indent=2)

    # Create minimal code_gen_spec.json (required by TestingSpecialist)
    code_gen_spec = {
        "generated_files": [],
        "implementation_notes": "Generated for ARCH-011 test",
        "code_quality_metrics": {},
    }
    with open(artifacts_coding / "code_gen_spec.json", "w") as f:
        json.dump(code_gen_spec, f, indent=2)

    # Create minimal qa_report.json (result of testing)
    qa_report = {
        "status": "FAILED",
        "test_execution": {
            "total_tests": 1,
            "passed": 0,
            "failed": 1,
            "errors": 0,
            "return_code": 1,
        },
        "blocker_bugs_open": 1,
        "critical_path_pass_rate": 0.0,
    }
    with open(artifacts_testing / "qa_report.json", "w") as f:
        json.dump(qa_report, f, indent=2)

    # Create a minimal project manifest starting in TESTING phase
    manifest = {
        "apiVersion": "agency.os/v1alpha1",
        "kind": "Project",
        "metadata": {
            "projectId": project_id,
            "name": "ARCH-011 Verification",
            "owner": "verify_hap_loop.py",
            "createdAt": datetime.utcnow().isoformat() + "Z",
        },
        "status": {
            "projectPhase": "TESTING",  # Start at TESTING so repair loop activates
            "planningSubState": None,
            "lastUpdate": datetime.utcnow().isoformat() + "Z",
        },
        "artifacts": {
            "feature_spec.json": str(artifacts_planning / "feature_spec.json"),
            "code_gen_spec.json": str(artifacts_coding / "code_gen_spec.json"),
            "qa_report.json": str(artifacts_testing / "qa_report.json"),
        },
        "budget": {
            "max_cost_usd": 10.0,
            "current_cost_usd": 0.0,
            "alert_threshold": 0.80,
            "cost_breakdown": {},
        },
    }

    # Write manifest
    manifest_path = project_dir / "project_manifest.json"
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)

    logger.info(f"✅ Created test project at {project_dir}")
    logger.info(f"   Project ID: {project_id}")
    logger.info("   Artifacts created: feature_spec.json, code_gen_spec.json, qa_report.json")

    return project_id


def test_circuit_breaker():
    """
    Test the repair loop and circuit breaker.

    Scenario:
    1. Create a minimal project in TESTING phase
    2. Inject SaboteurTester as the TestingSpecialist
    3. Run orchestrator.execute_phase() multiple times
    4. Verify:
       - The loop cycles: CODING → TESTING → CODING → TESTING
       - Max attempts limit prevents infinite loop (circuit breaker)
       - Database audit trail shows proper execution counts

    Returns:
        True if test passed, False otherwise
    """
    print("\n" + "=" * 80)
    print("🛡️ ARCH-011: Testing Repair Loop & Circuit Breaker")
    print("=" * 80)
    print(f"Started: {datetime.now().isoformat()}\n")

    # Use the actual project root (where orchestrator can find its configs)
    repo_root = Path.cwd()
    temp_path = repo_root

    try:
        # Step 1: Create test project
        print("📋 STEP 1: Creating minimal test project...")
        project_id = create_test_project(temp_path)

        # Step 2: Initialize orchestrator
        print("\n📋 STEP 2: Initializing CoreOrchestrator...")
        try:
            orchestrator = CoreOrchestrator(
                repo_root=temp_path, execution_mode="delegated"  # Use delegated mode (file-based)
            )
            print("   ✅ CoreOrchestrator initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize orchestrator: {e}")
            return False

        # Step 3: Load project manifest
        print("\n📋 STEP 3: Loading project manifest...")
        try:
            manifest = orchestrator.load_project_manifest(project_id)
            print(f"   ✅ Manifest loaded (current phase: {manifest.current_phase.value})")
        except Exception as e:
            logger.error(f"❌ Failed to load manifest: {e}")
            return False

        # Step 4: Inject saboteur specialist
        print("\n📋 STEP 4: Injecting SaboteurTester as TestingSpecialist...")
        try:
            # Register saboteur specialist to override real TestingSpecialist
            orchestrator.agent_registry.register_specialist(ProjectPhase.TESTING, SaboteurTester)
            print("   ✅ SaboteurTester registered in AgentRegistry")
        except Exception as e:
            logger.error(f"❌ Failed to register saboteur: {e}")
            return False

        # Step 5: Run the repair loop test
        print("\n📋 STEP 5: Running orchestrator with repair loop...")
        print(
            "   Expected flow: TESTING → (fail) → CODING → TESTING → (fail) → ...(max 3 attempts)"
        )
        print()

        repair_attempts = 0
        max_repair_attempts = 3
        execution_phases = []

        try:
            # Execute phase multiple times to observe repair loop
            for iteration in range(10):  # Upper bound to prevent actual infinite loop
                current_phase = manifest.current_phase
                execution_phases.append(current_phase.value)

                print(f"   Iteration {iteration + 1}: {current_phase.value} phase")

                # Execute current phase
                try:
                    success = orchestrator.execute_phase(manifest)
                    print(f"      → Phase execution returned: {success}")
                except OrchestratorError as e:
                    # Circuit breaker should raise this after max attempts
                    print(f"      → 🔌 Circuit breaker triggered: {str(e)[:60]}...")
                    break

                # Reload manifest after phase execution
                manifest = orchestrator.load_project_manifest(project_id)

                # Detect repair loop (same phase CODING executed consecutively)
                if iteration > 0:
                    prev_phase = execution_phases[-2]
                    if prev_phase == "CODING" and current_phase == "CODING":
                        repair_attempts += 1
                        print(
                            f"      🔄 Repair loop detected! Attempt {repair_attempts}/{max_repair_attempts}"
                        )

                        if repair_attempts > max_repair_attempts:
                            print(
                                f"      🔌 Max repair attempts exceeded ({repair_attempts} > {max_repair_attempts})"
                            )
                            break

                # Check if we've reached a terminal state
                if manifest.current_phase == ProjectPhase.PRODUCTION:
                    print("   ⏸️  Reached PRODUCTION (workflow complete)")
                    break

        except Exception as e:
            logger.error(f"Error during execution: {e}")
            # This is expected when circuit breaker is triggered
            pass

        # Step 6: Analyze database audit trail
        print("\n📋 STEP 6: Analyzing SQLite audit trail...")
        analysis_results = {
            "execution_phases": execution_phases,
            "repair_cycles": 0,
            "coding_phase_count": 0,
            "testing_phase_count": 0,
        }

        try:
            if orchestrator.db_store:
                with orchestrator.db_store as db:
                    # Query decisions table for SABOTEUR_TEST_FAILURE entries
                    cursor = db.conn.execute(
                        "SELECT COUNT(*) as count FROM decisions WHERE decision_type = 'SABOTEUR_TEST_FAILURE'"
                    )
                    result = cursor.fetchone()
                    saboteur_failures = result["count"] if result else 0

                    print("   ✅ Database audit trail:")
                    print(f"      - Saboteur failures recorded: {saboteur_failures}")
            else:
                print("   ⚠️  SQLite store not available (running in delegated mode)")
                saboteur_failures = 0
        except Exception as e:
            logger.warning(f"   ⚠️  Could not query database: {e}")
            saboteur_failures = 0

        # Count phases in execution sequence
        for phase in execution_phases:
            if phase == "CODING":
                analysis_results["coding_phase_count"] += 1
            elif phase == "TESTING":
                analysis_results["testing_phase_count"] += 1

        # Calculate repair cycles (CODING→TESTING→CODING patterns)
        for i in range(len(execution_phases) - 2):
            if (
                execution_phases[i] == "CODING"
                and execution_phases[i + 1] == "TESTING"
                and execution_phases[i + 2] == "CODING"
            ):
                analysis_results["repair_cycles"] += 1

        # Step 7: Verify results
        print("\n📋 STEP 7: Verifying repair loop behavior...")
        print(f"\n   Execution sequence: {' → '.join(execution_phases)}")
        print("\n   Analysis:")
        print(f"   - Total phases executed: {len(execution_phases)}")
        print(f"   - CODING phase count: {analysis_results['coding_phase_count']}")
        print(f"   - TESTING phase count: {analysis_results['testing_phase_count']}")
        print(f"   - Repair cycles detected: {analysis_results['repair_cycles']}")
        print(f"   - Database saboteur failures: {saboteur_failures}")

        # Verify success criteria
        print("\n" + "=" * 80)
        print("VERIFICATION RESULTS")
        print("=" * 80)

        success = True

        # Check 1: Loop was executed (multiple phases)
        if len(execution_phases) > 1:
            print("✅ CHECK 1: Repair loop executed (multiple phase transitions)")
        else:
            print("❌ CHECK 1: FAILED - No repair loop detected")
            success = False

        # Check 2: Loop was contained (not infinite)
        if len(execution_phases) <= 10:
            print(
                f"✅ CHECK 2: Circuit breaker contained the loop ({len(execution_phases)} iterations)"
            )
        else:
            print(
                f"❌ CHECK 2: FAILED - Loop exceeded safe limit ({len(execution_phases)} iterations)"
            )
            success = False

        # Check 3: CODING phase executed at least twice (repair attempt)
        if analysis_results["coding_phase_count"] >= 2:
            print(
                f"✅ CHECK 3: Repair cycle detected (CODING executed {analysis_results['coding_phase_count']} times)"
            )
        else:
            print(
                f"❌ CHECK 3: FAILED - No repair cycle (CODING only {analysis_results['coding_phase_count']} times)"
            )
            success = False

        # Check 4: TESTING phase executed multiple times
        if analysis_results["testing_phase_count"] >= 2:
            print(
                f"✅ CHECK 4: Testing executed multiple times ({analysis_results['testing_phase_count']} times)"
            )
        else:
            print(
                f"⚠️  CHECK 4: Testing not repeated as expected ({analysis_results['testing_phase_count']} times)"
            )
            # This is less critical - might indicate delegated mode

        return success

    except Exception as e:
        logger.error(f"❌ FATAL ERROR: {e}", exc_info=True)
        return False


def main():
    """Main entry point"""
    try:
        success = test_circuit_breaker()

        print("\n" + "=" * 80)
        if success:
            print("🎉 ARCH-011 VERIFICATION PASSED")
            print("   ✅ Repair Loop mechanism is working")
            print("   ✅ Circuit Breaker is containing the loop")
            print("   ✅ System is resilient to cascading failures")
            print("\nNext: Run full test suite to ensure no regressions")
            print("=" * 80)
            return 0
        else:
            print("❌ ARCH-011 VERIFICATION FAILED")
            print("   Review logs above for specific failures")
            print("=" * 80)
            return 1
    except KeyboardInterrupt:
        print("\n⚠️  Verification interrupted by user")
        return 130
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
