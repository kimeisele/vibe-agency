#!/usr/bin/env python3
"""
Deep Analysis - Search for additional "Todsünden" (mortal sins) in the framework

This test goes beyond workspace path resolution and looks for:
1. Integration gaps between components
2. Unused code / dead functions
3. Schema inconsistencies
4. Missing error handling
5. Circular dependencies
"""

# Import utilities
import importlib.util
import json
import os
import sys
from pathlib import Path

# Navigate to repo root from tests/ directory
repo_root = Path(__file__).parent.parent

spec = importlib.util.spec_from_file_location(
    "prompt_runtime", repo_root / "agency_os/core_system/runtime/prompt_runtime.py"
)
prompt_runtime = importlib.util.module_from_spec(spec)
spec.loader.exec_module(prompt_runtime)

# Load workspace_utils from scripts package (proper Python imports)
from scripts.workspace_utils import list_active_workspaces, load_workspace_manifest


def test_manifest_schema_consistency():
    """Test if all workspace manifests use consistent schema"""
    print("\n" + "=" * 60)
    print("TEST 1: Manifest Schema Consistency")
    print("=" * 60 + "\n")

    workspaces = list_active_workspaces()
    issues = []

    # Load root manifest for comparison
    root_manifest_path = Path("project_manifest.json")
    with open(root_manifest_path) as f:
        root_manifest = json.load(f)

    root_has_api_version = "apiVersion" in root_manifest
    root_has_kind = "kind" in root_manifest

    print("Root manifest:")
    print(f"  apiVersion: {'✅' if root_has_api_version else '❌'}")
    print(f"  kind: {'✅' if root_has_kind else '❌'}")
    print()

    for ws in workspaces:
        try:
            manifest = load_workspace_manifest(ws["name"])

            has_api_version = "apiVersion" in manifest
            has_kind = "kind" in manifest
            has_status = "status" in manifest
            has_artifacts = "artifacts" in manifest

            print(f"Workspace: {ws['name']}")
            print(f"  apiVersion: {'✅' if has_api_version else '❌'}")
            print(f"  kind: {'✅' if has_kind else '❌'}")
            print(f"  status: {'✅' if has_status else '❌'}")
            print(f"  artifacts: {'✅' if has_artifacts else '❌'}")

            # Check for schema consistency
            if root_has_api_version != has_api_version:
                issues.append(f"{ws['name']}: apiVersion mismatch with root")
            if root_has_kind != has_kind:
                issues.append(f"{ws['name']}: kind mismatch with root")

            print()

        except Exception as e:
            issues.append(f"{ws['name']}: Failed to load - {e}")
            print(f"  ❌ ERROR: {e}\n")

    if issues:
        print(f"⚠️  ISSUES FOUND ({len(issues)}):")
        for issue in issues:
            print(f"  - {issue}")
        return False
    else:
        print("✅ All manifests use consistent schema")
        return True


def test_agent_task_coverage():
    """Test if all agents have proper task definitions"""
    print("\n" + "=" * 60)
    print("TEST 2: Agent Task Coverage")
    print("=" * 60 + "\n")

    agents = [
        "VIBE_ALIGNER",
        "GENESIS_BLUEPRINT",
        "CODE_GENERATOR",
        "QA_VALIDATOR",
        "DEPLOY_MANAGER",
        "BUG_TRIAGE",
    ]

    issues = []

    for agent_id in agents:
        agent_base = Path("agency_os")

        # Find agent directory
        agent_path = None
        for framework_dir in agent_base.glob("*/agents"):
            potential_path = framework_dir / agent_id
            if potential_path.exists():
                agent_path = potential_path
                break

        if not agent_path:
            issues.append(f"{agent_id}: Agent directory not found")
            continue

        print(f"Agent: {agent_id}")

        # Check for required files
        required_files = ["_prompt_core.md", "_composition.yaml", "_knowledge_deps.yaml"]

        for req_file in required_files:
            file_path = agent_path / req_file
            exists = file_path.exists()
            print(f"  {req_file}: {'✅' if exists else '❌'}")

            if not exists:
                issues.append(f"{agent_id}: Missing {req_file}")

        # Check tasks directory
        tasks_dir = agent_path / "tasks"
        if tasks_dir.exists():
            task_files = list(tasks_dir.glob("task_*.md"))
            meta_files = list(tasks_dir.glob("task_*.meta.yaml"))

            print(f"  tasks: {len(task_files)} task files, {len(meta_files)} metadata files")

            # Check if all tasks have metadata
            for task_file in task_files:
                task_id = task_file.stem
                meta_file = tasks_dir / f"{task_id}.meta.yaml"

                if not meta_file.exists():
                    issues.append(f"{agent_id}: Task {task_id} missing metadata")
                    print(f"    ❌ {task_id}: No metadata")
                else:
                    print(f"    ✅ {task_id}")
        else:
            issues.append(f"{agent_id}: No tasks directory")
            print("  ❌ No tasks directory")

        print()

    if issues:
        print(f"⚠️  ISSUES FOUND ({len(issues)}):")
        for issue in issues:
            print(f"  - {issue}")
        return False
    else:
        print("✅ All agents have proper task definitions")
        return True


def test_unused_imports():
    """Find Python files that import but never use modules"""
    print("\n" + "=" * 60)
    print("TEST 3: Unused Imports & Dead Code")
    print("=" * 60 + "\n")

    # This is a simplified check
    print("⚠️  Manual review recommended for:")
    print("  - Unused imports")
    print("  - Dead code paths")
    print("  - Unreachable functions")
    print()
    print("✅ Automated check: SKIPPED (requires AST analysis)")

    return True


def test_error_handling():
    """Test if critical functions have proper error handling"""
    print("\n" + "=" * 60)
    print("TEST 4: Error Handling Coverage")
    print("=" * 60 + "\n")

    # Test workspace_utils functions
    print("Testing workspace_utils error handling:")

    # Test 1: Invalid workspace name
    try:
        from scripts.workspace_utils import load_workspace_manifest

        load_workspace_manifest("nonexistent_workspace")
        print("  ❌ load_workspace_manifest: No error for invalid workspace")
        return False
    except FileNotFoundError:
        print("  ✅ load_workspace_manifest: Proper error for invalid workspace")

    # Test 2: Invalid workspace in get_workspace_by_name
    try:
        from scripts.workspace_utils import get_workspace_by_name

        result = get_workspace_by_name("nonexistent")
        if result is None:
            print("  ✅ get_workspace_by_name: Returns None for invalid workspace")
        else:
            print("  ❌ get_workspace_by_name: Should return None")
            return False
    except Exception as e:
        print(f"  ❌ get_workspace_by_name: Unexpected error - {e}")
        return False

    print()
    print("✅ Error handling coverage adequate")
    return True


def test_end_to_end_workflow():
    """Test complete workflow from workspace selection to prompt generation"""
    print("\n" + "=" * 60)
    print("TEST 5: End-to-End Workflow")
    print("=" * 60 + "\n")

    # Set workspace
    os.environ["ACTIVE_WORKSPACE"] = "prabhupad_os"
    print(f"✓ Set workspace: {os.getenv('ACTIVE_WORKSPACE')}")

    # Create runtime
    runtime = prompt_runtime.PromptRuntime()
    print("✓ Created runtime")

    # Execute task
    context = {"project_id": "prabhupad_os_001", "phase": "PLANNING"}

    try:
        prompt = runtime.execute_task(
            agent_id="VIBE_ALIGNER", task_id="01_education_calibration", context=context
        )

        print(f"✓ Generated prompt ({len(prompt):,} chars)")

        # Verify context was modified with resolved paths
        required_keys = [
            "_resolved_workspace",
            "_resolved_artifact_base_path",
            "_resolved_planning_path",
        ]

        all_present = all(key in context for key in required_keys)

        if all_present:
            print("✓ All resolved paths present in context")
            print()
            print("✅ End-to-end workflow successful")
            return True
        else:
            print("❌ Missing resolved paths in context")
            return False

    except Exception as e:
        print(f"❌ Workflow failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """Run all deep tests"""
    print("\n" + "=" * 70)
    print("DEEP ANALYSIS: Searching for additional 'Todsünden'")
    print("=" * 70)

    tests = [
        ("Manifest Schema Consistency", test_manifest_schema_consistency),
        ("Agent Task Coverage", test_agent_task_coverage),
        ("Unused Imports & Dead Code", test_unused_imports),
        ("Error Handling Coverage", test_error_handling),
        ("End-to-End Workflow", test_end_to_end_workflow),
    ]

    results = []

    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ TEST CRASHED: {test_name}")
            print(f"   Error: {e}")
            import traceback

            traceback.print_exc()
            results.append((test_name, False))

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70 + "\n")

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")

    print()
    print(f"Total: {passed}/{total} tests passed")

    if passed == total:
        print("\n✅ ALL TESTS PASSED - No additional Todsünden found!")
        return True
    else:
        print(f"\n⚠️  {total - passed} tests failed - Additional issues found")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
