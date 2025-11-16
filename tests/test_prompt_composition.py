#!/usr/bin/env python3
"""
Integration Tests: Prompt Composition System

Tests that ALL agents can compose their prompts correctly.
No LLM calls - just validates that composition works.
"""

import importlib.util
import os
import sys
from pathlib import Path

# Debug: Print working directory
print(f"Working directory: {os.getcwd()}")
print(f"Python path: {sys.path}")

# Check if prompt_runtime file exists
runtime_path = Path("agency_os/00_system/runtime/prompt_runtime.py")
if not runtime_path.exists():
    print(f"❌ ERROR: prompt_runtime.py not found at {runtime_path.absolute()}")
    print(f"   Current dir contents: {list(Path('.').iterdir())[:10]}")
    sys.exit(1)

print(f"✓ Found prompt_runtime at {runtime_path.absolute()}")

# Load prompt runtime
try:
    spec = importlib.util.spec_from_file_location("prompt_runtime", str(runtime_path))
    prompt_runtime = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(prompt_runtime)
    PromptRuntime = prompt_runtime.PromptRuntime
    print("✓ Successfully loaded PromptRuntime")
except Exception as e:
    print(f"❌ ERROR loading prompt_runtime: {e}")
    import traceback

    traceback.print_exc()
    sys.exit(1)


def check_agent_prompt_composition(agent_id: str, task_id: str) -> bool:
    """Check if agent can compose a valid prompt (not a pytest test)"""
    runtime = PromptRuntime()

    try:
        prompt = runtime.execute_task(
            agent_id=agent_id,
            task_id=task_id,
            context={"project_id": "test", "workspace": "test", "user_input": "test input"},
        )

        # Validate prompt
        assert len(prompt) > 100, "Prompt too short"
        assert "CORE PERSONALITY" in prompt or "personality" in prompt.lower(), (
            "Missing personality section"
        )

        print(f"✅ {agent_id}/{task_id}: OK ({len(prompt)} chars)")
        return True

    except Exception as e:
        print(f"❌ {agent_id}/{task_id}: FAILED - {e}")
        return False


def main():
    print("=" * 60)
    print("INTEGRATION TEST: Prompt Composition")
    print("=" * 60)
    print()

    # Test cases: (agent_id, task_id)
    test_cases = [
        # Planning Framework
        ("VIBE_ALIGNER", "02_feature_extraction"),
        ("VIBE_ALIGNER", "03_feasibility_validation"),
        ("GENESIS_BLUEPRINT", "01_select_core_modules"),
        ("GENESIS_BLUEPRINT", "02_design_extensions"),
        ("GENESIS_BLUEPRINT", "03_generate_config_schema"),
        ("GENESIS_BLUEPRINT", "04_validate_architecture"),
        ("GENESIS_BLUEPRINT", "05_handoff"),
        # Code Generation Framework
        ("CODE_GENERATOR", "01_spec_analysis_validation"),
        ("CODE_GENERATOR", "02_code_generation"),
        ("CODE_GENERATOR", "03_test_generation"),
        ("CODE_GENERATOR", "04_documentation_generation"),
        ("CODE_GENERATOR", "05_quality_assurance_packaging"),
        # QA Framework
        ("QA_VALIDATOR", "01_setup_environment"),
        ("QA_VALIDATOR", "02_automated_test_execution"),
        ("QA_VALIDATOR", "03_static_analysis"),
        ("QA_VALIDATOR", "04_report_generation"),
        # Deploy Framework
        ("DEPLOY_MANAGER", "01_pre_deployment_checks"),
        ("DEPLOY_MANAGER", "02_deployment_execution"),
        ("DEPLOY_MANAGER", "03_post_deployment_validation"),
        ("DEPLOY_MANAGER", "04_report_generation"),
        # Maintenance Framework
        ("BUG_TRIAGE", "01_bug_analysis_classification"),
        ("BUG_TRIAGE", "02_remediation_path_determination"),
        ("BUG_TRIAGE", "03_output_generation"),
    ]

    results = []
    for agent_id, task_id in test_cases:
        success = check_agent_prompt_composition(agent_id, task_id)
        results.append((agent_id, task_id, success))

    print()
    print("=" * 60)
    print("RESULTS")
    print("=" * 60)

    passed = sum(1 for _, _, success in results if success)
    failed = len(results) - passed

    print(f"Passed: {passed}/{len(results)}")
    print(f"Failed: {failed}/{len(results)}")

    if failed > 0:
        print("\nFailed tests:")
        for agent_id, task_id, success in results:
            if not success:
                print(f"  - {agent_id}/{task_id}")
        sys.exit(1)

    print("\n✅ All tests passed!")
    sys.exit(0)


if __name__ == "__main__":
    main()
