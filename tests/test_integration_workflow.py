#!/usr/bin/env python3
"""
Integration Tests: End-to-End Workflow Validation

Tests the complete planning workflow:
LEAN_CANVAS_VALIDATOR → VIBE_ALIGNER → GENESIS_BLUEPRINT

This validates that the hardened planning framework works end-to-end.
"""

import importlib.util
import sys
from pathlib import Path

# Load prompt runtime
spec = importlib.util.spec_from_file_location(
    "prompt_runtime", "agency_os/00_system/runtime/prompt_runtime.py"
)
prompt_runtime = importlib.util.module_from_spec(spec)
spec.loader.exec_module(prompt_runtime)
PromptRuntime = prompt_runtime.PromptRuntime


def test_lean_canvas_to_vibe_aligner():
    """Test integration: LEAN_CANVAS_VALIDATOR → VIBE_ALIGNER"""
    print("\n" + "=" * 60)
    print("TEST: LEAN_CANVAS_VALIDATOR → VIBE_ALIGNER Integration")
    print("=" * 60)

    runtime = PromptRuntime()

    # Simulate LEAN_CANVAS_VALIDATOR output
    lean_canvas_context = {
        "project_id": "test_integration_001",
        "workspace": "test",
        "lean_canvas_summary": {
            "problem": "Freelance designers waste 5hrs/week on invoicing",
            "customer_segments": "Solo freelance designers earning $50-150k/year",
            "unique_value_proposition": "One-click invoice generation from tracked time",
            "solution_mvp": "Time tracker + invoice template generator",
            "riskiest_assumptions": [
                "Designers will pay $20/month for time tracking",
                "Time tracking data is sufficient for accurate invoicing",
            ],
        },
    }

    try:
        # Test VIBE_ALIGNER can consume lean_canvas output
        prompt = runtime.execute_task(
            agent_id="VIBE_ALIGNER", task_id="02_feature_extraction", context=lean_canvas_context
        )

        assert len(prompt) > 10000, "Prompt too short"
        assert "lean_canvas" in prompt.lower() or "riskiest" in prompt.lower(), (
            "Prompt should reference lean canvas context"
        )

        print("✅ PASS: VIBE_ALIGNER can consume LEAN_CANVAS output")
        return True

    except Exception as e:
        print(f"❌ FAIL: {e}")
        return False


def test_vibe_aligner_to_genesis():
    """Test integration: VIBE_ALIGNER → GENESIS_BLUEPRINT"""
    print("\n" + "=" * 60)
    print("TEST: VIBE_ALIGNER → GENESIS_BLUEPRINT Integration")
    print("=" * 60)

    runtime = PromptRuntime()

    # Simulate VIBE_ALIGNER output
    vibe_aligner_context = {
        "project_id": "test_integration_001",
        "workspace": "test",
        "feature_spec": {
            "project": {"name": "InvoiceQuick", "category": "Web App", "scale": "Solo User"},
            "features": [
                {"id": "F001", "name": "Time Tracking", "priority": "must_have"},
                {"id": "F002", "name": "Invoice Generation", "priority": "must_have"},
            ],
            "nfr_requirements": [
                {"category_id": "NFR-SEC", "response": "Basic auth, no PII storage"}
            ],
        },
    }

    try:
        # Test GENESIS_BLUEPRINT can consume VIBE_ALIGNER output
        prompt = runtime.execute_task(
            agent_id="GENESIS_BLUEPRINT",
            task_id="01_select_core_modules",
            context=vibe_aligner_context,
        )

        assert len(prompt) > 5000, "Prompt too short"
        assert "feature_spec" in prompt.lower() or "nfr" in prompt.lower(), (
            "Prompt should reference feature_spec context"
        )

        print("✅ PASS: GENESIS_BLUEPRINT can consume VIBE_ALIGNER output")
        return True

    except Exception as e:
        print(f"❌ FAIL: {e}")
        return False


def test_lean_canvas_validator_structure():
    """Test that LEAN_CANVAS_VALIDATOR agent structure is complete"""
    print("\n" + "=" * 60)
    print("TEST: LEAN_CANVAS_VALIDATOR Agent Structure")
    print("=" * 60)

    agent_dir = Path("agency_os/01_planning_framework/agents/LEAN_CANVAS_VALIDATOR")

    required_files = [
        "_composition.yaml",
        "_knowledge_deps.yaml",
        "_prompt_core.md",
        "tasks/task_01_canvas_interview.md",
        "tasks/task_01_canvas_interview.meta.yaml",
        "tasks/task_02_risk_analysis.md",
        "tasks/task_02_risk_analysis.meta.yaml",
        "tasks/task_03_handoff.md",
        "tasks/task_03_handoff.meta.yaml",
        "gates/gate_lean_canvas_complete.md",
    ]

    missing = []
    for file_path in required_files:
        full_path = agent_dir / file_path
        if not full_path.exists():
            missing.append(file_path)

    if missing:
        print(f"❌ FAIL: Missing files: {missing}")
        return False

    print("✅ PASS: All required agent files exist")
    return True


def test_new_knowledge_bases_exist():
    """Test that new knowledge bases from hardening implementation exist"""
    print("\n" + "=" * 60)
    print("TEST: New Knowledge Bases Exist")
    print("=" * 60)

    required_kb = [
        "system_steward_framework/knowledge/PRODUCT_QUALITY_METRICS.yaml",
        "system_steward_framework/knowledge/NFR_CATALOG.yaml",
        "system_steward_framework/knowledge/architecture/PROMPT_SECURITY_GUIDELINES.md",
    ]

    missing = []
    for kb_path in required_kb:
        if not Path(kb_path).exists():
            missing.append(kb_path)

    if missing:
        print(f"❌ FAIL: Missing knowledge bases: {missing}")
        return False

    print("✅ PASS: All new knowledge bases exist")
    return True


def main():
    print("=" * 60)
    print("INTEGRATION TEST SUITE")
    print("Testing Hardened Planning Framework")
    print("=" * 60)

    tests = [
        ("LEAN_CANVAS_VALIDATOR Structure", test_lean_canvas_validator_structure),
        ("New Knowledge Bases", test_new_knowledge_bases_exist),
        ("LEAN_CANVAS → VIBE_ALIGNER", test_lean_canvas_to_vibe_aligner),
        ("VIBE_ALIGNER → GENESIS", test_vibe_aligner_to_genesis),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"\n❌ {test_name}: EXCEPTION - {e}")
            import traceback

            traceback.print_exc()
            results.append((test_name, False))

    print("\n" + "=" * 60)
    print("INTEGRATION TEST RESULTS")
    print("=" * 60)

    passed = sum(1 for _, success in results if success)
    failed = len(results) - passed

    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")

    print(f"\nPassed: {passed}/{len(results)}")
    print(f"Failed: {failed}/{len(results)}")

    if failed > 0:
        sys.exit(1)

    print("\n✅ All integration tests passed!")
    sys.exit(0)


if __name__ == "__main__":
    main()
