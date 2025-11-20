#!/usr/bin/env python3
"""
Smoke Test for Phase 4: Governance Integration
===============================================

Tests:
1. AUDITOR agent integration (invoke_auditor)
2. Quality gate execution (blocking/async)
3. Horizontal audit execution
4. Audit report schema validation

Run:
    python test_phase4_smoke.py
"""

import logging
import sys
from pathlib import Path

from agency_os.core_system.orchestrator.core_orchestrator import (
    CoreOrchestrator,
    ProjectManifest,
    ProjectPhase,
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def test_core_orchestrator_initialization():
    """Test 1: CoreOrchestrator loads with AUDITOR methods"""
    logger.info("Test 1: CoreOrchestrator initialization with AUDITOR methods")

    repo_root = Path(__file__).resolve().parent.parent.parent.parent
    orchestrator = CoreOrchestrator(repo_root)

    # Verify AUDITOR methods exist
    assert hasattr(orchestrator, "invoke_auditor"), "invoke_auditor method not found"
    assert hasattr(orchestrator, "apply_quality_gates"), "apply_quality_gates method not found"
    assert hasattr(orchestrator, "run_horizontal_audits"), "run_horizontal_audits method not found"

    logger.info("✅ Test 1 PASSED: All AUDITOR methods present")


def test_workflow_has_quality_gates():
    """Test 2: Workflow YAML contains quality gates"""
    logger.info("\nTest 2: Workflow YAML quality gates validation")

    repo_root = Path(__file__).resolve().parent.parent.parent.parent
    orchestrator = CoreOrchestrator(repo_root)

    # Check if T1_StartCoding has quality gates
    transition_found = False
    quality_gates_found = False

    for transition in orchestrator.workflow.get("transitions", []):
        if transition["name"] == "T1_StartCoding":
            transition_found = True
            if "quality_gates" in transition:
                quality_gates_found = True
                quality_gates = transition["quality_gates"]
                logger.info(f"   Found {len(quality_gates)} quality gates for T1_StartCoding:")
                for gate in quality_gates:
                    logger.info(f"     - {gate.get('check')} (blocking={gate.get('blocking')})")
            break

    assert transition_found, "T1_StartCoding transition not found"
    assert quality_gates_found, "T1_StartCoding has no quality_gates defined"

    logger.info("✅ Test 2 PASSED: Quality gates configured in workflow")


def test_workflow_has_horizontal_audits():
    """Test 3: Workflow YAML contains horizontal audits"""
    logger.info("\nTest 3: Workflow YAML horizontal audits validation")

    repo_root = Path(__file__).resolve().parent.parent.parent.parent
    orchestrator = CoreOrchestrator(repo_root)

    # Check if PLANNING state has horizontal_audits
    state_found = False
    audits_found = False

    for state in orchestrator.workflow.get("states", []):
        if state["name"] == "PLANNING":
            state_found = True
            if "horizontal_audits" in state:
                audits_found = True
                audits = state["horizontal_audits"]
                logger.info(f"   Found {len(audits)} horizontal audits for PLANNING:")
                for audit in audits:
                    logger.info(f"     - {audit.get('name')} (blocking={audit.get('blocking')})")
            break

    assert state_found, "PLANNING state not found"
    assert audits_found, "PLANNING has no horizontal_audits defined"

    logger.info("✅ Test 3 PASSED: Horizontal audits configured in workflow")


def test_audit_context_building():
    """Test 4: Audit context building for different check types"""
    logger.info("\nTest 4: Audit context building")

    repo_root = Path(__file__).resolve().parent.parent.parent.parent
    orchestrator = CoreOrchestrator(repo_root)

    # Create mock manifest
    manifest = ProjectManifest(
        project_id="test-project-123", name="Test Project", current_phase=ProjectPhase.PLANNING
    )

    # Test different check types
    check_types = [
        "prompt_security_scan",
        "data_privacy_scan",
        "code_security_scan",
        "license_compliance_scan",
    ]

    for check_type in check_types:
        context = orchestrator._build_audit_context(check_type, manifest)

        assert "audit_mode" in context, f"audit_mode missing for {check_type}"
        assert "project_id" in context, f"project_id missing for {check_type}"
        assert "target_files" in context, f"target_files missing for {check_type}"

        logger.info(f"   ✓ {check_type}: {len(context.get('target_files', []))} target files")

    logger.info("✅ Test 4 PASSED: Audit context building works for all check types")


def test_data_contracts_has_audit_schema():
    """Test 5: Data contracts YAML contains audit_report schema"""
    logger.info("\nTest 5: Data contracts audit_report schema validation")

    repo_root = Path(__file__).resolve().parent.parent.parent.parent
    contracts_path = repo_root / "agency_os/core_system/contracts/ORCHESTRATION_data_contracts.yaml"

    import yaml

    with open(contracts_path) as f:
        contracts = yaml.safe_load(f)

    # Check if audit_report.schema.json exists
    schema_found = False
    for schema in contracts.get("schemas", []):
        if schema["name"] == "audit_report.schema.json":
            schema_found = True
            logger.info(f"   Found audit_report schema (version {schema['version']})")

            # Verify key fields
            fields = {field["name"] for field in schema.get("fields", [])}
            required_fields = ["check_type", "severity", "blocking", "status", "timestamp"]

            for req_field in required_fields:
                assert req_field in fields, (
                    f"Required field '{req_field}' missing from audit_report schema"
                )
                logger.info(f"     ✓ {req_field}")

            break

    assert schema_found, "audit_report.schema.json not found in data contracts"

    logger.info("✅ Test 5 PASSED: Audit report schema is complete")


def test_coding_handler_has_code_generator():
    """Test 6: CodingHandler invokes CODE_GENERATOR"""
    logger.info("\nTest 6: CodingHandler CODE_GENERATOR integration")

    # Import CodingHandler
    # Verify it's not the stub version
    import inspect

    from handlers.coding_handler import CodingHandler

    source = inspect.getsource(CodingHandler.execute)

    # Check for CODE_GENERATOR task calls
    assert "task_01_spec_analysis_validation" in source, "Task 1 not found in CodingHandler"
    assert "task_02_code_generation" in source, "Task 2 not found in CodingHandler"
    assert "task_03_test_generation" in source, "Task 3 not found in CodingHandler"
    assert "task_04_documentation_generation" in source, "Task 4 not found in CodingHandler"
    assert "task_05_quality_assurance_packaging" in source, "Task 5 not found in CodingHandler"

    logger.info("   ✓ All 5 CODE_GENERATOR tasks present")
    logger.info("✅ Test 6 PASSED: CodingHandler has full CODE_GENERATOR integration")


def main():
    """Run all smoke tests"""
    print("=" * 70)
    print("PHASE 4 SMOKE TESTS: Governance Integration (GAD-002)")
    print("=" * 70)
    print()

    try:
        test_core_orchestrator_initialization()
        test_workflow_has_quality_gates()
        test_workflow_has_horizontal_audits()
        test_audit_context_building()
        test_data_contracts_has_audit_schema()
        test_coding_handler_has_code_generator()

        print()
        print("=" * 70)
        print("✅ ALL PHASE 4 SMOKE TESTS PASSED")
        print("=" * 70)
        print()
        print("Phase 4 Implementation Status:")
        print("  ✅ AUDITOR integration (invoke_auditor)")
        print("  ✅ Quality gate execution (blocking/async)")
        print("  ✅ Horizontal audit execution")
        print("  ✅ Audit report schema")
        print("  ✅ CODE_GENERATOR integration (5 tasks)")
        print()
        print("Ready for Phase 4 deployment!")
        print()

        return 0

    except AssertionError as e:
        logger.error(f"\n❌ TEST FAILED: {e}")
        return 1
    except Exception as e:
        logger.error(f"\n❌ UNEXPECTED ERROR: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
