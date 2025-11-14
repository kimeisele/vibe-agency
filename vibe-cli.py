#!/usr/bin/env python3
"""
Vibe Agency CLI - Simple Prompt Generator

Usage:
    ./vibe-cli.py list                                    # List all agents
    ./vibe-cli.py tasks VIBE_ALIGNER                      # List tasks for agent
    ./vibe-cli.py generate VIBE_ALIGNER 02_feature_extraction  # Generate prompt

The generated prompt is saved to: COMPOSED_PROMPT.md
You can then copy/paste this into Claude Code.
"""

import sys
import os
import argparse
from pathlib import Path

# Import the runtime
import importlib.util
spec = importlib.util.spec_from_file_location(
    "prompt_runtime",
    Path(__file__).parent / "agency_os/00_system/runtime/prompt_runtime.py"
)
prompt_runtime = importlib.util.module_from_spec(spec)
spec.loader.exec_module(prompt_runtime)
PromptRuntime = prompt_runtime.PromptRuntime

# CRITICAL FIX #2: Import workspace utilities
sys.path.insert(0, str(Path(__file__).parent / 'scripts'))
from workspace_utils import (
    get_workspace_by_name,
    list_active_workspaces,
    get_active_workspace,
    set_active_workspace
)


# Agent descriptions for CLI
AGENT_DESCRIPTIONS = {
    "VIBE_ALIGNER": "Feature extraction & feasibility validation (Planning Phase 1)",
    "GENESIS_BLUEPRINT": "Architecture generation (Planning Phase 2)",
    "GENESIS_UPDATE": "Architecture updates (Planning Phase 2b)",
    "CODE_GENERATOR": "Code generation from architecture specs",
    "QA_VALIDATOR": "Quality assurance & testing",
    "DEPLOY_MANAGER": "Deployment orchestration",
    "BUG_TRIAGE": "Bug analysis & remediation planning",
}


def list_agents():
    """List all available agents"""
    print("\n" + "=" * 60)
    print("AVAILABLE AGENTS")
    print("=" * 60 + "\n")

    for agent_id, description in AGENT_DESCRIPTIONS.items():
        print(f"  {agent_id}")
        print(f"    → {description}\n")

    print("Use: ./vibe-cli.py tasks <AGENT_ID> to see tasks\n")


def list_tasks(agent_id: str):
    """List all tasks for an agent"""
    runtime = PromptRuntime()

    try:
        agent_path = runtime._get_agent_path(agent_id)
    except Exception as e:
        print(f"\n❌ Error: {e}\n")
        return

    tasks_dir = agent_path / "tasks"
    if not tasks_dir.exists():
        print(f"\n❌ No tasks found for {agent_id}\n")
        return

    print("\n" + "=" * 60)
    print(f"TASKS FOR: {agent_id}")
    print("=" * 60 + "\n")

    # Find all task files
    task_files = sorted(tasks_dir.glob("task_*.md"))

    for task_file in task_files:
        task_id = task_file.stem.replace("task_", "")

        # Try to load metadata
        meta_file = tasks_dir / f"task_{task_id}.meta.yaml"
        if meta_file.exists():
            import yaml
            with open(meta_file) as f:
                meta = yaml.safe_load(f)
                description = meta.get("description", "No description")
                phase = meta.get("phase", "?")
                print(f"  {task_id}")
                print(f"    Phase: {phase}")
                print(f"    → {description}\n")
        else:
            print(f"  {task_id}\n")

    print(f"Use: ./vibe-cli.py generate {agent_id} <TASK_ID>\n")


def generate_prompt(agent_id: str, task_id: str, output_file: str = "COMPOSED_PROMPT.md"):
    """Generate a composed prompt"""
    print("\n" + "=" * 60)
    print(f"GENERATING PROMPT: {agent_id}.{task_id}")
    print("=" * 60 + "\n")

    runtime = PromptRuntime()

    # Default context
    context = {
        "project_id": "user_project",
        "workspace": "workspaces/user_project",
        "phase": "PLANNING",
    }

    try:
        # Compose the prompt
        composed_prompt = runtime.execute_task(
            agent_id=agent_id,
            task_id=task_id,
            context=context
        )

        # Save to file
        output_path = Path(output_file)
        with open(output_path, "w") as f:
            f.write(composed_prompt)

        print("\n" + "=" * 60)
        print("✅ SUCCESS")
        print("=" * 60 + "\n")
        print(f"Prompt saved to: {output_path.absolute()}")
        print(f"Prompt size: {len(composed_prompt):,} characters\n")
        print("Next steps:")
        print("  1. Open the file in your editor")
        print("  2. Copy the entire content")
        print("  3. Paste into Claude Code")
        print("  4. Claude will execute the task\n")

    except Exception as e:
        print("\n" + "=" * 60)
        print("❌ ERROR")
        print("=" * 60 + "\n")
        print(str(e))
        print()


def set_workspace(workspace_name: str):
    """
    Set active workspace for this session (CRITICAL FIX #2)

    This sets the $ACTIVE_WORKSPACE environment variable which is used by
    workspace_utils.py to resolve artifact paths.
    """
    print("\n" + "=" * 60)
    print(f"SETTING ACTIVE WORKSPACE: {workspace_name}")
    print("=" * 60 + "\n")

    # Validate workspace exists
    ws = get_workspace_by_name(workspace_name)
    if not ws:
        print(f"❌ ERROR: Workspace '{workspace_name}' not found\n")
        print("Available workspaces:")
        for w in list_active_workspaces():
            print(f"  • {w['name']} ({w['type']})")
            print(f"    {w['description']}")
            print()
        return

    # Set workspace (persists to .active_workspace file)
    set_active_workspace(workspace_name)

    print(f"✅ Active workspace set to: {workspace_name}")
    print(f"   Type: {ws['type']}")
    print(f"   Manifest: {ws['manifestPath']}")
    print(f"   Artifacts: workspaces/{workspace_name}/artifacts/\n")
    print("✅ Workspace persisted to .active_workspace file")
    print("   All subsequent CLI commands will use this workspace.\n")


def list_workspaces():
    """List all active workspaces"""
    print("\n" + "=" * 60)
    print("ACTIVE WORKSPACES")
    print("=" * 60 + "\n")

    current_workspace = get_active_workspace()

    workspaces = list_active_workspaces()
    if not workspaces:
        print("No workspaces found.\n")
        return

    for ws in workspaces:
        prefix = "→" if ws['name'] == current_workspace else " "
        print(f"{prefix} {ws['name']} ({ws['type']})")
        print(f"    {ws['description']}")
        print(f"    Manifest: {ws['manifestPath']}")
        print()

    print(f"Current workspace: {current_workspace}")
    print("\nUse: ./vibe-cli.py workspace <NAME> to switch\n")


def main():
    parser = argparse.ArgumentParser(
        description="Vibe Agency CLI - Prompt Generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  ./vibe-cli.py list
  ./vibe-cli.py workspaces
  ./vibe-cli.py workspace prabhupad_os
  ./vibe-cli.py tasks VIBE_ALIGNER
  ./vibe-cli.py generate VIBE_ALIGNER 02_feature_extraction
  ./vibe-cli.py generate GENESIS_BLUEPRINT 01_select_core_modules
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # list command
    subparsers.add_parser("list", help="List all available agents")

    # workspaces command (CRITICAL FIX #2)
    subparsers.add_parser("workspaces", help="List all active workspaces")

    # workspace command (CRITICAL FIX #2)
    workspace_parser = subparsers.add_parser("workspace", help="Set active workspace")
    workspace_parser.add_argument("workspace_name", help="Workspace to activate (e.g., prabhupad_os)")

    # tasks command
    tasks_parser = subparsers.add_parser("tasks", help="List tasks for an agent")
    tasks_parser.add_argument("agent_id", help="Agent ID (e.g., VIBE_ALIGNER)")

    # generate command
    gen_parser = subparsers.add_parser("generate", help="Generate a composed prompt")
    gen_parser.add_argument("agent_id", help="Agent ID (e.g., VIBE_ALIGNER)")
    gen_parser.add_argument("task_id", help="Task ID (e.g., 02_feature_extraction)")
    gen_parser.add_argument("-o", "--output", default="COMPOSED_PROMPT.md",
                           help="Output file (default: COMPOSED_PROMPT.md)")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    if args.command == "list":
        list_agents()
    elif args.command == "workspaces":
        list_workspaces()
    elif args.command == "workspace":
        set_workspace(args.workspace_name)
    elif args.command == "tasks":
        list_tasks(args.agent_id)
    elif args.command == "generate":
        generate_prompt(args.agent_id, args.task_id, args.output)


if __name__ == "__main__":
    main()
