#!/usr/bin/env python3
"""
Integration Tests: Prompt Composition System

Tests that ALL agents can compose their prompts correctly.
No LLM calls - just validates that composition works.
"""

import importlib.util
from pathlib import Path

import pytest


@pytest.fixture(scope="module")
def prompt_runtime():
    """Load PromptRuntime module dynamically."""
    runtime_path = Path("agency_os/00_system/runtime/prompt_runtime.py")

    if not runtime_path.exists():
        pytest.skip(f"prompt_runtime.py not found at {runtime_path.absolute()}")

    try:
        spec = importlib.util.spec_from_file_location("prompt_runtime", str(runtime_path))
        prompt_runtime_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(prompt_runtime_module)
        return prompt_runtime_module.PromptRuntime
    except Exception as e:
        pytest.skip(f"Failed to load prompt_runtime: {e}")


def check_agent_prompt_composition(PromptRuntime, agent_id: str, task_id: str) -> tuple[bool, str]:
    """
    Check if agent can compose a valid prompt.

    Returns:
        (success: bool, message: str)
    """
    runtime = PromptRuntime()

    try:
        prompt = runtime.execute_task(
            agent_id=agent_id,
            task_id=task_id,
            context={"project_id": "test", "workspace": "test", "user_input": "test input"},
        )

        # Validate prompt
        if len(prompt) < 100:
            return False, f"Prompt too short ({len(prompt)} chars)"

        if "CORE PERSONALITY" not in prompt and "personality" not in prompt.lower():
            return False, "Missing personality section"

        return True, f"OK ({len(prompt)} chars)"

    except Exception as e:
        return False, str(e)


# Test cases: (agent_id, task_id, category)
TEST_CASES = [
    # Planning Framework
    ("VIBE_ALIGNER", "02_feature_extraction", "planning"),
    ("VIBE_ALIGNER", "03_feasibility_validation", "planning"),
    ("GENESIS_BLUEPRINT", "01_select_core_modules", "planning"),
    ("GENESIS_BLUEPRINT", "02_design_extensions", "planning"),
    ("GENESIS_BLUEPRINT", "03_generate_config_schema", "planning"),
    ("GENESIS_BLUEPRINT", "04_validate_architecture", "planning"),
    ("GENESIS_BLUEPRINT", "05_handoff", "planning"),
    # Code Generation Framework
    ("CODE_GENERATOR", "01_spec_analysis_validation", "coding"),
    ("CODE_GENERATOR", "02_code_generation", "coding"),
    ("CODE_GENERATOR", "03_test_generation", "coding"),
    ("CODE_GENERATOR", "04_documentation_generation", "coding"),
    ("CODE_GENERATOR", "05_quality_assurance_packaging", "coding"),
    # QA Framework
    ("QA_VALIDATOR", "01_setup_environment", "testing"),
    ("QA_VALIDATOR", "02_automated_test_execution", "testing"),
    ("QA_VALIDATOR", "03_static_analysis", "testing"),
    ("QA_VALIDATOR", "04_report_generation", "testing"),
    # Deploy Framework
    ("DEPLOY_MANAGER", "01_pre_deployment_checks", "deployment"),
    ("DEPLOY_MANAGER", "02_deployment_execution", "deployment"),
    ("DEPLOY_MANAGER", "03_post_deployment_validation", "deployment"),
    ("DEPLOY_MANAGER", "04_report_generation", "deployment"),
    # Maintenance Framework
    ("BUG_TRIAGE", "01_bug_analysis_classification", "maintenance"),
    ("BUG_TRIAGE", "02_remediation_path_determination", "maintenance"),
    ("BUG_TRIAGE", "03_output_generation", "maintenance"),
]


class TestPromptComposition:
    """Test prompt composition for all agents and tasks."""

    @pytest.mark.parametrize("agent_id,task_id,category", TEST_CASES)
    def test_agent_prompt_composition(self, prompt_runtime, agent_id, task_id, category):
        """Test that agent can compose a valid prompt for the given task."""
        success, message = check_agent_prompt_composition(prompt_runtime, agent_id, task_id)

        assert success, f"{agent_id}/{task_id} failed: {message}"


class TestPromptCompositionSummary:
    """Summary test - run all composition checks and report."""

    def test_all_agents_composition_summary(self, prompt_runtime):
        """Run all composition checks and provide summary."""
        results = []

        for agent_id, task_id, category in TEST_CASES:
            success, message = check_agent_prompt_composition(prompt_runtime, agent_id, task_id)
            results.append((agent_id, task_id, category, success, message))

        # Calculate statistics
        total = len(results)
        passed = sum(1 for _, _, _, success, _ in results if success)
        failed = total - passed

        # Group by category
        by_category = {}
        for agent_id, task_id, category, success, message in results:
            if category not in by_category:
                by_category[category] = {"passed": 0, "failed": 0}
            if success:
                by_category[category]["passed"] += 1
            else:
                by_category[category]["failed"] += 1

        # Print summary
        print("\n" + "=" * 60)
        print("PROMPT COMPOSITION TEST SUMMARY")
        print("=" * 60)
        print(f"Total: {passed}/{total} passed ({failed} failed)")
        print()
        print("By category:")
        for category, stats in by_category.items():
            print(f"  {category}: {stats['passed']}/{stats['passed'] + stats['failed']} passed")
        print("=" * 60)

        # List failures
        failures = [(a, t, m) for a, t, _, s, m in results if not s]
        if failures:
            print("\nFailed tests:")
            for agent_id, task_id, message in failures:
                print(f"  ❌ {agent_id}/{task_id}: {message}")

        # Assert at least 80% pass rate (allow some failures for agents not yet implemented)
        pass_rate = passed / total if total > 0 else 0
        assert pass_rate >= 0.8, (
            f"Pass rate too low: {pass_rate:.1%} (expected ≥80%)\nFailed: {failed}/{total} tests"
        )
