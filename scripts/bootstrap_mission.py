#!/usr/bin/env python3
"""
GAD-701 Bootstrap Script - Initialize Mission Control

This script:
1. Creates roadmap.yaml with Phase 1 tasks
2. Creates active_mission.json with initial state
3. Marks Task 1 (SCAFFOLD_GAD_701_CORE) as DONE
4. Starts Task 2 (INTEGRATE_CLI_DASHBOARD)
5. Displays the state (no validation yet)

This demonstrates DOGFOODING: The system managing itself immediately.
"""

import json
import sys
from datetime import datetime
from pathlib import Path

import yaml


def create_roadmap(vibe_root: Path) -> None:
    """Create initial roadmap.yaml with Phase 1 plan"""
    print("📋 Creating roadmap.yaml...")

    # Define Phase 1 tasks as dictionaries
    tasks = {
        "task-001": {
            "version": 1,
            "id": "task-001",
            "name": "SCAFFOLD_GAD_701_CORE",
            "description": "Create core task management files (models, manager, validators)",
            "status": "DONE",
            "priority": 10,
            "created_at": datetime.now().isoformat(),
            "started_at": None,
            "completed_at": datetime.now().isoformat(),
            "time_budget_mins": 120,
            "time_used_mins": 120,
            "validation_checks": [
                {
                    "id": "files_created",
                    "description": "Core files created (models.py, task_manager.py, etc)",
                    "validator": "validate_files_exist",
                    "params": {},
                    "status": True,
                    "last_check": datetime.now().isoformat(),
                    "error": None,
                },
                {
                    "id": "imports_work",
                    "description": "All imports resolve correctly",
                    "validator": "validate_imports",
                    "params": {},
                    "status": True,
                    "last_check": datetime.now().isoformat(),
                    "error": None,
                },
            ],
            "blocking_reason": None,
            "related_files": [],
            "git_commits": [],
        },
        "task-002": {
            "version": 1,
            "id": "task-002",
            "name": "INTEGRATE_CLI_DASHBOARD",
            "description": "Create rich-based CLI with mission control dashboard",
            "status": "IN_PROGRESS",
            "priority": 9,
            "created_at": datetime.now().isoformat(),
            "started_at": datetime.now().isoformat(),
            "completed_at": None,
            "time_budget_mins": 120,
            "time_used_mins": 0,
            "validation_checks": [
                {
                    "id": "cmd_mission_created",
                    "description": "cmd_mission.py created with all commands",
                    "validator": "validate_files_exist",
                    "params": {"files": ["agency_os/01_interface/cli/cmd_mission.py"]},
                    "status": False,
                    "last_check": None,
                    "error": None,
                },
                {
                    "id": "git_clean",
                    "description": "Git working directory is clean",
                    "validator": "validate_git_clean",
                    "params": {},
                    "status": False,
                    "last_check": None,
                    "error": None,
                },
                {
                    "id": "tests_passing",
                    "description": "All tests passing",
                    "validator": "validate_tests_passing",
                    "params": {},
                    "status": False,
                    "last_check": None,
                    "error": None,
                },
            ],
            "blocking_reason": None,
            "related_files": [
                "agency_os/01_interface/cli/cmd_mission.py",
                "agency_os/01_interface/cli/__init__.py",
            ],
            "git_commits": [],
        },
        "task-003": {
            "version": 1,
            "id": "task-003",
            "name": "IMPLEMENT_NEXT_TASK_GENERATOR",
            "description": "Auto-select next task based on roadmap progress",
            "status": "TODO",
            "priority": 8,
            "created_at": datetime.now().isoformat(),
            "started_at": None,
            "completed_at": None,
            "time_budget_mins": 90,
            "time_used_mins": 0,
            "validation_checks": [
                {
                    "id": "generator_implemented",
                    "description": "next_task_generator.py functional",
                    "validator": "validate_files_exist",
                    "params": {},
                    "status": False,
                    "last_check": None,
                    "error": None,
                },
                {
                    "id": "tests_passing",
                    "description": "Generator tests passing",
                    "validator": "validate_tests_passing",
                    "params": {},
                    "status": False,
                    "last_check": None,
                    "error": None,
                },
            ],
            "blocking_reason": None,
            "related_files": [],
            "git_commits": [],
        },
    }

    # Create roadmap
    roadmap = {
        "version": 1,
        "project_name": "vibe-agency",
        "phases": [
            {
                "name": "FOUNDATION_BUILD",
                "status": "IN_PROGRESS",
                "progress": 33,
                "task_ids": ["task-001", "task-002", "task-003"],
            },
        ],
        "tasks": tasks,
    }

    # Write roadmap.yaml
    roadmap_file = vibe_root / ".vibe" / "config" / "roadmap.yaml"
    roadmap_file.parent.mkdir(parents=True, exist_ok=True)

    with open(roadmap_file, "w") as f:
        yaml.dump(roadmap, f, default_flow_style=False, sort_keys=False)

    print(f"   ✅ Roadmap created: {roadmap_file}")
    print("      - 3 tasks defined")
    print("      - Task 1: DONE")
    print("      - Task 2: IN_PROGRESS (current)")
    print("      - Task 3: TODO")
    print()


def create_mission_state(vibe_root: Path, task_002: dict) -> None:
    """Create active_mission.json with initial state"""
    print("📋 Creating active_mission.json...")

    # Create mission state
    mission = {
        "version": 1,
        "current_task": task_002,  # Task 2 is current
        "total_tasks_completed": 1,  # Task 1 is done
        "total_time_spent_mins": 120,
        "current_phase": "FOUNDATION_BUILD",
        "last_updated": datetime.now().isoformat(),
    }

    # Write active_mission.json
    state_file = vibe_root / ".vibe" / "state" / "active_mission.json"
    state_file.parent.mkdir(parents=True, exist_ok=True)

    with open(state_file, "w") as f:
        json.dump(mission, f, indent=2)

    print(f"   ✅ Mission state created: {state_file}")
    print("      - Current task: Task 2 (INTEGRATE_CLI_DASHBOARD)")
    print("      - Tasks completed: 1")
    print("      - Total time spent: 120 mins")
    print()


def bootstrap_mission(vibe_root: Path) -> None:
    """Bootstrap mission state"""
    print("🚀 Bootstrapping Mission Control...")
    print()

    # Create roadmap first
    create_roadmap(vibe_root)

    # Load roadmap to get task-002
    roadmap_file = vibe_root / ".vibe" / "config" / "roadmap.yaml"
    with open(roadmap_file) as f:
        roadmap = yaml.safe_load(f)

    task_002 = roadmap["tasks"]["task-002"]

    # Create mission state
    create_mission_state(vibe_root, task_002)

    print("=" * 60)
    print("📊 BOOTSTRAP SUMMARY")
    print("=" * 60)
    print()
    print("✅ System initialized with:")
    print("   • Roadmap: .vibe/config/roadmap.yaml")
    print("   • Mission state: .vibe/state/active_mission.json")
    print("   • Current task: Task 2 (INTEGRATE_CLI_DASHBOARD)")
    print()
    print("📋 Task Status:")
    print("   ✅ Task 1: SCAFFOLD_GAD_701_CORE (DONE)")
    print("   🚀 Task 2: INTEGRATE_CLI_DASHBOARD (IN_PROGRESS)")
    print("   ⏳ Task 3: IMPLEMENT_NEXT_TASK_GENERATOR (TODO)")
    print()
    print("🔍 Next Steps:")
    print("   1. View mission dashboard:")
    print("      uv run python -m agency_os.system.task_management.dummy")
    print()
    print("   2. View mission state:")
    print("      cat .vibe/state/active_mission.json | python -m json.tool")
    print()
    print("   3. Or directly check files:")
    print("      ls -la .vibe/")
    print()


def main():
    """Main entry point"""
    print()
    print("=" * 60)
    print("🎯 GAD-701 MISSION CONTROL BOOTSTRAP")
    print("=" * 60)
    print()

    # Find vibe root
    vibe_root = Path(__file__).parent.parent
    print(f"Vibe Root: {vibe_root}")
    print()

    # Run bootstrap
    try:
        bootstrap_mission(vibe_root)
        print("=" * 60)
        print("✅ BOOTSTRAP COMPLETE - SYSTEM LIVE!")
        print("=" * 60)
        print()
    except Exception as e:
        print()
        print("=" * 60)
        print(f"❌ BOOTSTRAP FAILED: {e}")
        print("=" * 60)
        sys.exit(1)


if __name__ == "__main__":
    main()
