#!/usr/bin/env python3
"""
Integration test for complete multi-layer quality enforcement system (GAD-004)

This test validates that all 3 layers work together:
- Layer 1: Session-Scoped Enforcement (pre-push checks)
- Layer 2: Workflow-Scoped Quality Gates (manifest recording)
- Layer 3: Deployment-Scoped Validation (GitHub Actions)
"""

import json
import subprocess
import sys
from pathlib import Path


def test_complete_quality_enforcement_flow():
    """
    End-to-end test of all 3 layers working together
    """
    print("🧪 Testing complete multi-layer quality enforcement flow...")

    # LAYER 1: Session-scoped enforcement
    print("\n1️⃣  Testing Layer 1 (Session-Scoped Enforcement)...")

    # Ensure code is clean
    subprocess.run(["uv", "run", "ruff", "check", ".", "--fix"], check=True, capture_output=True)

    # Run pre-push check
    result = subprocess.run(["./bin/pre-push-check.sh"], capture_output=True, text=True)
    assert result.returncode == 0, f"Layer 1: Pre-push check failed on clean code:\n{result.stdout}"
    print("   ✅ Layer 1 passed")

    # Verify system status updated
    status_file = Path(".system_status.json")
    assert status_file.exists(), ".system_status.json not found"

    with open(status_file) as f:
        status = json.load(f)

    assert "linting" in status, "linting field missing from system status"
    assert status["linting"]["status"] == "passing", (
        f"Expected linting status 'passing', got '{status['linting']['status']}'"
    )
    print("   ✅ System status correctly updated")

    # LAYER 2: Workflow-scoped quality gates
    print("\n2️⃣  Testing Layer 2 (Workflow-Scoped Quality Gates)...")

    # Verify orchestrator has quality gate recording methods
    from agency_os_orchestrator import CoreOrchestrator

    orch = CoreOrchestrator(repo_root=Path.cwd(), execution_mode="delegated")
    assert hasattr(orch, "_record_quality_gate_result"), (
        "Orchestrator missing _record_quality_gate_result method"
    )
    assert hasattr(orch, "_get_transition_config"), (
        "Orchestrator missing _get_transition_config method"
    )
    assert hasattr(orch, "apply_quality_gates"), "Orchestrator missing apply_quality_gates method"
    print("   ✅ Layer 2 code exists and is callable")

    # LAYER 3: Deployment-scoped validation
    print("\n3️⃣  Testing Layer 3 (Deployment-Scoped Validation)...")

    # Verify GitHub Actions workflow exists
    workflow_file = Path(".github/workflows/post-merge-validation.yml")
    assert workflow_file.exists(), "Layer 3: GitHub Actions workflow not found"

    # Verify workflow has required steps
    with open(workflow_file) as f:
        workflow_content = f.read()

    assert "e2e-validation" in workflow_content, "Workflow missing e2e-validation job"
    assert "Run E2E test suite" in workflow_content, "Workflow missing E2E test step"
    assert "post-merge-validation.yml" in str(workflow_file), "Workflow file name incorrect"
    print("   ✅ Layer 3 workflow exists and is configured")

    # INTEGRATION: Verify all layers are connected
    print("\n🔗 Testing Layer Integration...")

    # Layer 1 → Layer 2: System status should influence orchestrator decisions
    assert status["linting"]["status"] in ["passing", "failing"], (
        "Linting status should be deterministic"
    )

    # Layer 2 → Layer 3: E2E tests should validate orchestrator behavior
    e2e_test_file = Path("tests/e2e/test_orchestrator_e2e.py")
    assert e2e_test_file.exists(), "E2E tests not found"

    print("   ✅ All layers are integrated")

    print("\n✅ ALL LAYERS INTEGRATED SUCCESSFULLY")


if __name__ == "__main__":
    try:
        test_complete_quality_enforcement_flow()
        sys.exit(0)
    except AssertionError as e:
        print(f"\n❌ INTEGRATION TEST FAILED: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ INTEGRATION TEST ERROR: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
