#!/usr/bin/env python3
"""
Auto Task Verification - Detect completed tasks that weren't marked

This script checks if tasks in the cleanup roadmap are physically complete
(acceptance criteria met) but not marked as complete in the JSON.

It auto-fixes the roadmap if it finds discrepancies.
"""

import json
import sys
from datetime import UTC, datetime
from pathlib import Path


def load_roadmap():
    """Load the cleanup roadmap"""
    roadmap_path = Path(__file__).parent.parent / ".vibe/config/cleanup_roadmap.json"

    if not roadmap_path.exists():
        return None, None

    with open(roadmap_path) as f:
        return json.load(f), roadmap_path


def save_roadmap(roadmap, roadmap_path):
    """Save updated roadmap"""
    roadmap["progress_tracking"]["last_updated"] = datetime.now(UTC).isoformat()
    with open(roadmap_path, "w") as f:
        json.dump(roadmap, f, indent=2)


def check_q001_complete():
    """Check if Q001 acceptance criteria are met"""
    # Q001 acceptance criteria:
    # 1. docs/architecture/quarantine/ directory exists
    # 2. GAD-100, 101, 102, 103, 200, 300 moved to quarantine/features/
    # 3. README in quarantine explains why files are there

    quarantine = Path("docs/architecture/quarantine")
    if not quarantine.exists():
        return False

    features = quarantine / "features"
    if not features.exists():
        return False

    # Check for key feature files
    required_files = [
        "GAD-100.md",
        "GAD-101.md",
        "GAD-102.md",
        "GAD-103.md",
        "GAD-200.md",
        "GAD-300.md",
    ]

    for file in required_files:
        if not (features / file).exists():
            return False

    # Check for README
    if not (quarantine / "README.md").exists():
        return False

    return True


def check_q002_complete():
    """Check if Q002 acceptance criteria are met"""
    # Q002: docs/architecture/ARCHITECTURE_REGISTRY.md created
    registry = Path("docs/architecture/ARCHITECTURE_REGISTRY.md")
    return registry.exists()


def check_q003_complete():
    """Check if Q003 acceptance criteria are met"""
    # Q003: VADs and LADs documented in registry
    registry = Path("docs/architecture/ARCHITECTURE_REGISTRY.md")
    if not registry.exists():
        return False

    content = registry.read_text()
    # Check if VADs and LADs are documented
    return "VAD-001" in content and "LAD-1" in content


def check_q004_complete():
    """Check if Q004 acceptance criteria are met"""
    # Q004: GAD_IMPLEMENTATION_STATUS.md updated with honest metrics
    status_file = Path("docs/architecture/GAD_IMPLEMENTATION_STATUS.md")
    if not status_file.exists():
        return False

    content = status_file.read_text()
    # Check for key indicators of honest update
    return "15 architectural decisions" in content or "HONEST METRICS" in content.upper()


def check_b001_complete():
    """Check if B001 acceptance criteria are met"""
    # B001: Boot script auto-provisioning works
    # Check if genesis.py is called from system-boot.sh (Genesis Protocol)
    boot_script = Path("bin/system-boot.sh")
    if not boot_script.exists():
        return False

    content = boot_script.read_text()
    return "genesis.py" in content or "Genesis Protocol" in content


def check_b002_complete():
    """Check if B002 acceptance criteria are met"""
    # B002: CI/CD live fire mode disabled
    workflow = Path(".github/workflows/test.yml")
    if not workflow.exists():
        return False

    content = workflow.read_text()
    return "VIBE_LIVE_FIRE: false" in content or "VIBE_LIVE_FIRE: 'false'" in content


def check_b003_complete():
    """Check if B003 acceptance criteria are met"""
    # B003: GAD-511 marked as CRITICAL
    status_file = Path("docs/architecture/GAD_IMPLEMENTATION_STATUS.md")
    if not status_file.exists():
        return False

    content = status_file.read_text()
    return "GAD-511" in content and "CRITICAL" in content


def check_b004_complete():
    """Check if B004 acceptance criteria are met"""
    # B004: FREEZE banner in CLAUDE.md
    claude_md = Path("CLAUDE.md")
    if not claude_md.exists():
        return False

    content = claude_md.read_text()
    return "FREEZE" in content.upper()


# Map task IDs to verification functions
VERIFICATION_FUNCTIONS = {
    "Q001": check_q001_complete,
    "Q002": check_q002_complete,
    "Q003": check_q003_complete,
    "Q004": check_q004_complete,
    "B001": check_b001_complete,
    "B002": check_b002_complete,
    "B003": check_b003_complete,
    "B004": check_b004_complete,
}


def auto_verify_tasks(roadmap, roadmap_path):
    """Check all tasks and auto-mark completed ones"""
    progress = roadmap.get("progress_tracking", {})
    completed = set(progress.get("completed_tasks", []))

    fixed_count = 0

    for phase in roadmap.get("phases", []):
        for task in phase.get("tasks", []):
            task_id = task["task_id"]

            # Skip if already marked complete
            if task_id in completed:
                continue

            # Check if we have a verification function
            verify_func = VERIFICATION_FUNCTIONS.get(task_id)
            if not verify_func:
                continue  # Can't auto-verify this task

            # Run verification
            if verify_func():
                print(f"✅ Auto-detected: {task_id} is complete but not marked!")
                completed.add(task_id)
                fixed_count += 1

    # Update roadmap if changes were made
    if fixed_count > 0:
        progress["completed_tasks"] = sorted(list(completed))
        save_roadmap(roadmap, roadmap_path)
        print(f"\n💾 Roadmap updated: {fixed_count} task(s) auto-marked complete")
        return True

    return False


def main():
    roadmap, roadmap_path = load_roadmap()

    if not roadmap:
        print("No cleanup roadmap found.")
        sys.exit(0)

    print("🔍 Auto-verifying task completion status...")
    print("")

    had_fixes = auto_verify_tasks(roadmap, roadmap_path)

    if not had_fixes:
        print("✅ All completed tasks are properly marked.")

    print("")


if __name__ == "__main__":
    main()
