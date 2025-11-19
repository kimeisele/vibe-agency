#!/usr/bin/env python3
"""
End-to-End Tests for Core Orchestrator

These tests validate the complete SDLC workflow execution,
simulating real-world usage of the vibe-agency framework.

NOTE: These are placeholder tests for GAD-004 Phase 3.
Expand with real E2E scenarios as the system matures.
"""

import sys
from pathlib import Path

# Add orchestrator to path
from agency_os_orchestrator import CoreOrchestrator


def test_orchestrator_initialization():
    """
    Test that orchestrator initializes correctly.

    This is a smoke test to ensure basic functionality works.
    """
    repo_root = Path(__file__).parent.parent.parent
    orchestrator = CoreOrchestrator(repo_root=repo_root, execution_mode="delegated")

    assert orchestrator is not None
    assert orchestrator.execution_mode == "delegated"
    assert orchestrator.workflow is not None

    print("✅ Orchestrator initialization test passed")


def test_workflow_yaml_loaded():
    """
    Test that workflow YAML is loaded correctly.

    Validates that all required transitions and states are present.
    """
    repo_root = Path(__file__).parent.parent.parent
    orchestrator = CoreOrchestrator(repo_root=repo_root, execution_mode="delegated")

    # Verify workflow structure
    assert "transitions" in orchestrator.workflow
    assert "states" in orchestrator.workflow

    transitions = orchestrator.workflow["transitions"]
    assert len(transitions) > 0

    states = orchestrator.workflow["states"]
    assert len(states) > 0

    # Verify critical transitions exist
    transition_names = [t["name"] for t in transitions]
    assert "T1_StartCoding" in transition_names

    # Verify critical states exist
    state_names = [s["name"] for s in states]
    assert "PLANNING" in state_names
    assert "CODING" in state_names

    print("✅ Workflow YAML loading test passed")


def test_prompt_registry_available():
    """
    Test that prompt registry is accessible.

    Validates that governance prompts can be loaded.
    """
    repo_root = Path(__file__).parent.parent.parent
    orchestrator = CoreOrchestrator(repo_root=repo_root, execution_mode="delegated")

    # Verify prompt registry exists
    assert hasattr(orchestrator, "prompt_registry")
    assert orchestrator.prompt_registry is not None

    print("✅ Prompt registry test passed")


if __name__ == "__main__":
    print("🧪 Running E2E Tests...\n")

    try:
        test_orchestrator_initialization()
        test_workflow_yaml_loaded()
        test_prompt_registry_available()

        print("\n✅ ALL E2E TESTS PASSED")
        sys.exit(0)

    except AssertionError as e:
        print(f"\n❌ E2E TEST FAILED: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)

    except Exception as e:
        print(f"\n❌ E2E TEST ERROR: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
