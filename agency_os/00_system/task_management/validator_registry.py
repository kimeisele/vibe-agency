"""Validator Registry Plugin System (GAD-701)"""

import subprocess
from collections.abc import Callable
from pathlib import Path
from typing import Any

# ============================================================================
# VALIDATOR FUNCTIONS
# ============================================================================


def validate_tests_passing(vibe_root: Path, scope: str = "tests/") -> bool:
    """Run pytest in scope (e.g., 'tests/')"""
    result = subprocess.run(  # noqa: S603
        ["pytest", scope, "-v"],
        cwd=vibe_root,
        capture_output=True,
        timeout=60
    )
    # Return code 0 means success
    return result.returncode == 0


def validate_git_clean(vibe_root: Path) -> bool:
    """Check for uncommitted changes (git status --porcelain)"""
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=vibe_root,
        capture_output=True
    )
    # If stdout is empty, the working directory is clean
    return len(result.stdout.strip()) == 0


def validate_docs_updated(vibe_root: Path, required_files: list) -> bool:
    """Check if all required_files were modified in the last commit (HEAD~1)"""
    result = subprocess.run(
        ["git", "diff", "--name-only", "HEAD~1"],
        cwd=vibe_root,
        capture_output=True,
        text=True
    )

    modified_files = set(result.stdout.strip().split('\n'))

    # Check if all required files are in the list of modified files
    return all(req in modified_files for req in required_files)


# ============================================================================
# REGISTRY
# ============================================================================

# The registry maps the string ID (from the Task model) to the actual function
VALIDATOR_REGISTRY: dict[str, Callable] = {
    "tests_passing": validate_tests_passing,
    "git_clean": validate_git_clean,
    "docs_updated": validate_docs_updated,
}


def run_validators(task: Any, vibe_root: Path) -> dict[str, Any]:
    """
    Run all validators for a given task.

    Returns dict: {check_id: bool, check_id_error: str}
    """
    results = {}

    for check in task.validation_checks:
        validator_func = VALIDATOR_REGISTRY.get(check.validator)

        if not validator_func:
            results[check.id] = False
            results[f"{check.id}_error"] = f"Unknown validator: {check.validator}"
            continue

        try:
            # Call the function, passing vibe_root and any parameters from the Task model
            passed = validator_func(vibe_root, **check.params)
            results[check.id] = passed
        except Exception as e:
            results[check.id] = False
            results[f"{check.id}_error"] = str(e)

    return results
