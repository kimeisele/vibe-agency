#!/usr/bin/env python3
"""
Vibe Agency Helper for Claude Code

This is what Claude actually needs - direct access to prompt composition!

Usage in Claude Code:
    from vibe_helper import compose_prompt

    prompt = compose_prompt("VIBE_ALIGNER", "02_feature_extraction")
    # Now Claude can work with the prompt directly!
"""

import importlib.util
import sys
from pathlib import Path

# Load prompt runtime
spec = importlib.util.spec_from_file_location(
    "prompt_runtime", Path(__file__).parent / "agency_os/00_system/runtime/prompt_runtime.py"
)
prompt_runtime = importlib.util.module_from_spec(spec)
spec.loader.exec_module(prompt_runtime)
PromptRuntime = prompt_runtime.PromptRuntime


def compose_prompt(agent_id: str, task_id: str, context: dict = None) -> str:
    """
    Compose a prompt that Claude can work with directly.

    Args:
        agent_id: Agent to use (e.g., "VIBE_ALIGNER")
        task_id: Task to execute (e.g., "02_feature_extraction")
        context: Optional context dict

    Returns:
        The composed prompt as a string

    Example:
        >>> prompt = compose_prompt("VIBE_ALIGNER", "02_feature_extraction")
        >>> # Now Claude reads the prompt and executes
    """
    runtime = PromptRuntime()

    if context is None:
        context = {
            "project_id": "user_project",
            "workspace": "workspaces/user_project",
            "phase": "PLANNING",
        }

    return runtime.execute_task(agent_id=agent_id, task_id=task_id, context=context)


def list_agents() -> dict:
    """List all available agents with descriptions"""
    return {
        "VIBE_ALIGNER": "Feature extraction & feasibility validation",
        "GENESIS_BLUEPRINT": "Architecture generation",
        "GENESIS_UPDATE": "Architecture updates",
        "CODE_GENERATOR": "Code generation from specs",
        "QA_VALIDATOR": "Quality assurance & testing",
        "DEPLOY_MANAGER": "Deployment orchestration",
        "BUG_TRIAGE": "Bug analysis & remediation",
    }


def list_tasks(agent_id: str) -> list:
    """List all tasks for an agent"""
    runtime = PromptRuntime()
    agent_path = runtime._get_agent_path(agent_id)
    tasks_dir = agent_path / "tasks"

    if not tasks_dir.exists():
        return []

    task_files = sorted(tasks_dir.glob("task_*.md"))
    return [f.stem.replace("task_", "") for f in task_files]


# For direct CLI usage (but Claude should use the functions above!)
if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 vibe_helper.py <agent_id> <task_id>")
        print("Example: python3 vibe_helper.py VIBE_ALIGNER 02_feature_extraction")
        sys.exit(1)

    agent_id = sys.argv[1]
    task_id = sys.argv[2]

    print(f"Composing prompt for {agent_id}.{task_id}...")
    prompt = compose_prompt(agent_id, task_id)
    print(f"\nPrompt composed ({len(prompt)} chars)")
    print("\n" + "=" * 60)
    print(prompt)
