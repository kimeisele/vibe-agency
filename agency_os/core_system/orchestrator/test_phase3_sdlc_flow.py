#!/usr/bin/env python3
"""
Phase 3 SDLC Flow Test
======================

Tests the complete SDLC flow through all phases:
PLANNING → CODING → TESTING → AWAITING_QA_APPROVAL → DEPLOYMENT → PRODUCTION

This is a smoke test for Phase 3 implementation (with stub handlers).
Full integration testing will come in Phase 4.

Usage:
    python test_phase3_sdlc_flow.py
"""

import shutil
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from orchestrator.core_orchestrator import CoreOrchestrator, ProjectPhase


def test_phase3_sdlc_flow():
    """Test complete SDLC flow (smoke test with stub handlers)"""

    print("\n" + "=" * 80)
    print("PHASE 3 SDLC FLOW TEST")
    print("=" * 80 + "\n")

    # Setup test project
    test_project_id = "phase3_test_project"
    test_workspace = Path(f"workspaces/{test_project_id}")

    # Clean up previous test if exists
    if test_workspace.exists():
        print(f"🧹 Cleaning up previous test workspace: {test_workspace}")
        shutil.rmtree(test_workspace)

    print(f"📁 Creating test workspace: {test_workspace}\n")

    # Initialize orchestrator
    print("🏗️  Initializing CoreOrchestrator...")
    orchestrator = CoreOrchestrator(repo_root=Path.cwd())

    # Create test project manifest
    print(f"📋 Creating project manifest for: {test_project_id}\n")
    manifest = orchestrator.create_project(
        project_id=test_project_id,
        description="Phase 3 SDLC Flow Test Project",
        user_prompt="Test the complete SDLC flow with stub handlers",
        max_budget_usd=5.0,
    )

    print(f"✅ Project created: {test_project_id}")
    print(f"   Phase: {manifest.current_phase.value}")
    print(f"   Budget: ${manifest.budget['max_cost_usd']}\n")

    # Test Phase 1: PLANNING
    print("=" * 80)
    print("PHASE 1: PLANNING")
    print("=" * 80 + "\n")

    try:
        print("🎯 Executing PLANNING phase...")
        orchestrator.execute_phase(manifest)
        print("✅ PLANNING complete")
        print(f"   New phase: {manifest.current_phase.value}")
        print(f"   Artifacts: {list(manifest.artifacts.keys())}\n")
    except Exception as e:
        print(f"❌ PLANNING failed: {e}\n")
        return False

    # Test Phase 2: CODING
    print("=" * 80)
    print("PHASE 2: CODING")
    print("=" * 80 + "\n")

    try:
        print("💻 Executing CODING phase (stub)...")
        orchestrator.execute_phase(manifest)
        print("✅ CODING complete (stub)")
        print(f"   New phase: {manifest.current_phase.value}")
        print(f"   Artifacts: {list(manifest.artifacts.keys())}\n")
    except Exception as e:
        print(f"❌ CODING failed: {e}\n")
        return False

    # Test Phase 3: TESTING
    print("=" * 80)
    print("PHASE 3: TESTING")
    print("=" * 80 + "\n")

    try:
        print("🧪 Executing TESTING phase (stub)...")
        orchestrator.execute_phase(manifest)
        print("✅ TESTING complete (stub)")
        print(f"   New phase: {manifest.current_phase.value}")
        print(f"   Artifacts: {list(manifest.artifacts.keys())}\n")
    except Exception as e:
        print(f"❌ TESTING failed: {e}\n")
        return False

    # Test Phase 4: AWAITING_QA_APPROVAL (HITL)
    print("=" * 80)
    print("PHASE 4: AWAITING_QA_APPROVAL (HITL)")
    print("=" * 80 + "\n")

    if manifest.current_phase != ProjectPhase.AWAITING_QA_APPROVAL:
        print(f"❌ Expected phase AWAITING_QA_APPROVAL, got {manifest.current_phase.value}\n")
        return False

    print("⏸️  Project is waiting for QA approval")
    print(f"   Current phase: {manifest.current_phase.value}")
    print("\n📝 In real usage, you would run:")
    print(f"   ./vibe-cli.py approve-qa {test_project_id}")
    print("\n🤖 For this test, simulating approval...\n")

    # Simulate QA approval
    manifest.artifacts["qa_approved"] = True
    manifest.artifacts["qa_approver"] = "test_script"
    orchestrator.save_project_manifest(manifest)

    # Test Phase 5: DEPLOYMENT
    print("=" * 80)
    print("PHASE 5: DEPLOYMENT")
    print("=" * 80 + "\n")

    # Manually transition to DEPLOYMENT (would normally be done by vibe-cli resume)
    manifest.current_phase = ProjectPhase.DEPLOYMENT

    try:
        print("🚀 Executing DEPLOYMENT phase (stub)...")
        orchestrator.execute_phase(manifest)
        print("✅ DEPLOYMENT complete (stub)")
        print(f"   New phase: {manifest.current_phase.value}")
        print(f"   Artifacts: {list(manifest.artifacts.keys())}\n")
    except Exception as e:
        print(f"❌ DEPLOYMENT failed: {e}\n")
        return False

    # Verify we reached PRODUCTION
    print("=" * 80)
    print("FINAL STATE: PRODUCTION")
    print("=" * 80 + "\n")

    if manifest.current_phase != ProjectPhase.PRODUCTION:
        print(f"❌ Expected phase PRODUCTION, got {manifest.current_phase.value}\n")
        return False

    print("🎉 Project successfully reached PRODUCTION phase!")
    print("\n📊 Final Report:")
    print(f"   Project ID: {manifest.project_id}")
    print(f"   Final Phase: {manifest.current_phase.value}")
    print(f"   Artifacts Created: {len(manifest.artifacts)}")
    print(
        f"   Budget Used: ${manifest.budget.get('current_cost_usd', 0):.2f} / ${manifest.budget['max_cost_usd']:.2f}"
    )
    print(f"   Workspace: {test_workspace}")

    # List all artifacts
    print("\n📦 Artifacts:")
    for artifact_name in sorted(manifest.artifacts.keys()):
        if (
            artifact_name.endswith("_spec")
            or artifact_name.endswith("_report")
            or artifact_name.endswith("_receipt")
        ):
            print(f"   ✓ {artifact_name}")

    print("\n" + "=" * 80)
    print("✅ PHASE 3 SDLC FLOW TEST PASSED")
    print("=" * 80 + "\n")

    return True


if __name__ == "__main__":
    try:
        success = test_phase3_sdlc_flow()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ TEST FAILED WITH ERROR: {e}\n")
        import traceback

        traceback.print_exc()
        sys.exit(1)
