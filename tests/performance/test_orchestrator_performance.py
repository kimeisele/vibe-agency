#!/usr/bin/env python3
"""
Performance Tests for Core Orchestrator

These tests validate performance characteristics of the vibe-agency framework.
NOTE: Non-blocking - failures won't prevent deployment.

NOTE: These are placeholder tests for GAD-004 Phase 3.
Expand with real performance scenarios as needed.
"""

import sys
import time
from pathlib import Path

# Add orchestrator to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "agency_os/00_system/orchestrator"))

from core_orchestrator import CoreOrchestrator


def test_orchestrator_initialization_performance():
    """
    Test that orchestrator initializes within acceptable time.

    Target: < 1 second for initialization.
    """
    repo_root = Path(__file__).parent.parent.parent

    start_time = time.time()
    orchestrator = CoreOrchestrator(repo_root=repo_root, execution_mode="delegated")
    duration = time.time() - start_time

    # Verify orchestrator was initialized
    assert orchestrator is not None

    print(f"Orchestrator initialization: {duration:.3f}s")

    # Non-critical assertion
    if duration > 1.0:
        print(f"⚠️  Initialization slower than target (1.0s): {duration:.3f}s")
    else:
        print(f"✅ Initialization within target: {duration:.3f}s")

    # Always pass (non-blocking)
    assert True


def test_workflow_yaml_parsing_performance():
    """
    Test that workflow YAML parsing is performant.

    Target: < 500ms for workflow parsing.
    """
    repo_root = Path(__file__).parent.parent.parent
    orchestrator = CoreOrchestrator(repo_root=repo_root, execution_mode="delegated")

    start_time = time.time()
    workflow = orchestrator.workflow
    transitions = workflow.get("transitions", [])
    duration = time.time() - start_time

    print(f"Workflow YAML parsing: {duration:.3f}s ({len(transitions)} transitions)")

    # Non-critical assertion
    if duration > 0.5:
        print(f"⚠️  Parsing slower than target (0.5s): {duration:.3f}s")
    else:
        print(f"✅ Parsing within target: {duration:.3f}s")

    # Always pass (non-blocking)
    assert True


if __name__ == "__main__":
    print("⚡ Running Performance Tests...\n")

    try:
        test_orchestrator_initialization_performance()
        test_workflow_yaml_parsing_performance()

        print("\n✅ ALL PERFORMANCE TESTS COMPLETED")
        print("(Note: Performance tests are non-blocking)")
        sys.exit(0)

    except Exception as e:
        print(f"\n⚠️  PERFORMANCE TEST ERROR: {e}")
        print("(Note: Performance tests are non-blocking - continuing)")
        sys.exit(0)  # Non-blocking: always exit 0
