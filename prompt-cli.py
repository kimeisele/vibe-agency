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
import json
import getpass
from pathlib import Path
from datetime import datetime

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


def approve_qa(project_id: str):
    """
    Approve QA and proceed to deployment (HITL - Decision 8)

    This implements the durable wait mechanism from GAD-002.
    The orchestrator pauses at AWAITING_QA_APPROVAL state, and this
    command sets qa_approved=True to allow deployment to proceed.
    """
    print("\n" + "=" * 60)
    print(f"QA APPROVAL: {project_id}")
    print("=" * 60 + "\n")

    # Load project manifest
    manifest_path = Path(f"workspaces/{project_id}/project_manifest.json")

    if not manifest_path.exists():
        print(f"❌ ERROR: Project manifest not found at {manifest_path}\n")
        print("Make sure the project_id is correct and the orchestrator has run.\n")
        return

    with open(manifest_path, 'r') as f:
        manifest = json.load(f)

    # Validate state
    if manifest.get('current_phase') != 'AWAITING_QA_APPROVAL':
        print(f"❌ ERROR: Project is not awaiting QA approval")
        print(f"   Current phase: {manifest.get('current_phase')}\n")
        return

    # Load QA report to show user
    qa_report_path = Path(f"workspaces/{project_id}/artifacts/testing/qa_report.json")
    if qa_report_path.exists():
        with open(qa_report_path, 'r') as f:
            qa_report = json.load(f)

        print("QA Report Summary:")
        print(f"  Status: {qa_report.get('status', 'UNKNOWN')}")
        print(f"  Tests Passed: {qa_report.get('tests_passed', 'N/A')}")
        print(f"  Tests Failed: {qa_report.get('tests_failed', 'N/A')}")
        print()

    # Confirm approval
    print("Do you approve this deployment? (yes/no): ", end="")
    response = input().strip().lower()

    if response != "yes":
        print("\n❌ QA approval cancelled\n")
        return

    # Set approval flags
    manifest['artifacts']['qa_approved'] = True
    manifest['artifacts']['qa_approver'] = getpass.getuser()
    manifest['artifacts']['qa_approved_at'] = datetime.utcnow().isoformat() + "Z"

    # Save manifest
    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2)

    print("\n" + "=" * 60)
    print("✅ QA APPROVED")
    print("=" * 60 + "\n")
    print(f"Approver: {manifest['artifacts']['qa_approver']}")
    print(f"Approved at: {manifest['artifacts']['qa_approved_at']}")
    print("\nNext steps:")
    print(f"  1. Resume orchestrator: python -m agency_os.00_system.orchestrator.core_orchestrator resume {project_id}")
    print("  2. Orchestrator will proceed to DEPLOYMENT phase\n")


def reject_qa(project_id: str, reason: str = None):
    """
    Reject QA and return to CODING phase (HITL - Decision 8)

    This implements the error loop from ORCHESTRATION_workflow_design.yaml.
    The orchestrator will transition back to CODING to fix issues.
    """
    print("\n" + "=" * 60)
    print(f"QA REJECTION: {project_id}")
    print("=" * 60 + "\n")

    # Load project manifest
    manifest_path = Path(f"workspaces/{project_id}/project_manifest.json")

    if not manifest_path.exists():
        print(f"❌ ERROR: Project manifest not found at {manifest_path}\n")
        return

    with open(manifest_path, 'r') as f:
        manifest = json.load(f)

    # Validate state
    if manifest.get('current_phase') != 'AWAITING_QA_APPROVAL':
        print(f"❌ ERROR: Project is not awaiting QA approval")
        print(f"   Current phase: {manifest.get('current_phase')}\n")
        return

    # Confirm rejection
    if not reason:
        print("Reason for rejection: ", end="")
        reason = input().strip()

    print(f"\nRejecting QA with reason: {reason}")
    print("Do you want to proceed? (yes/no): ", end="")
    response = input().strip().lower()

    if response != "yes":
        print("\n❌ QA rejection cancelled\n")
        return

    # Set rejection flags and transition back to CODING
    manifest['artifacts']['qa_approved'] = False
    manifest['artifacts']['qa_rejected'] = True
    manifest['artifacts']['qa_rejection_reason'] = reason
    manifest['artifacts']['qa_rejector'] = getpass.getuser()
    manifest['artifacts']['qa_rejected_at'] = datetime.utcnow().isoformat() + "Z"
    manifest['current_phase'] = 'CODING'  # Error loop: back to CODING

    # Save manifest
    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2)

    print("\n" + "=" * 60)
    print("✅ QA REJECTED")
    print("=" * 60 + "\n")
    print(f"Rejector: {manifest['artifacts']['qa_rejector']}")
    print(f"Reason: {reason}")
    print(f"New phase: CODING (error loop)\n")
    print("\nNext steps:")
    print(f"  1. Resume orchestrator: python -m agency_os.00_system.orchestrator.core_orchestrator resume {project_id}")
    print("  2. Orchestrator will re-execute CODING phase to fix issues\n")


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
  ./vibe-cli.py approve-qa my_app
  ./vibe-cli.py reject-qa my_app --reason "Tests failing"
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

    # approve-qa command (HITL - GAD-002 Decision 8)
    approve_parser = subparsers.add_parser("approve-qa", help="Approve QA and proceed to deployment")
    approve_parser.add_argument("project_id", help="Project ID (e.g., my_app)")

    # reject-qa command (HITL - GAD-002 Decision 8)
    reject_parser = subparsers.add_parser("reject-qa", help="Reject QA and return to CODING")
    reject_parser.add_argument("project_id", help="Project ID (e.g., my_app)")
    reject_parser.add_argument("-r", "--reason", help="Rejection reason")

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
    elif args.command == "approve-qa":
        approve_qa(args.project_id)
    elif args.command == "reject-qa":
        reject_qa(args.project_id, args.reason)


if __name__ == "__main__":
    main()
