#!/usr/bin/env python3
"""
Next Task Fetcher - Tell STEWARD what to work on

Reads cleanup_roadmap.json and returns the next pending task.
Used by system-boot.sh to show STEWARD what to do.
"""

import json
import sys
from pathlib import Path


def load_roadmap():
    """Load the cleanup roadmap"""
    roadmap_path = Path(__file__).parent.parent / ".vibe/config/cleanup_roadmap.json"

    if not roadmap_path.exists():
        return None

    with open(roadmap_path) as f:
        return json.load(f)


def find_next_task(roadmap, roadmap_path):
    """Find the first pending task in current phase"""
    if not roadmap:
        return None

    progress = roadmap.get("progress_tracking", {})
    current_phase_id = progress.get("current_phase", "PHASE_0")
    completed_task_ids = set(progress.get("completed_tasks", []))

    # Find current phase
    current_phase = None
    for phase in roadmap.get("phases", []):
        if phase["phase_id"] == current_phase_id:
            current_phase = phase
            break

    if not current_phase:
        return None

    # Find first pending task in current phase
    for task in current_phase.get("tasks", []):
        task_id = task["task_id"]
        if task_id not in completed_task_ids:
            # Check dependencies
            deps = task.get("dependencies", [])
            deps_met = all(dep in completed_task_ids for dep in deps)

            if deps_met:
                return {
                    "phase_id": current_phase_id,
                    "phase_name": current_phase["phase_name"],
                    "task": task
                }

    # No pending tasks in current phase - move to next phase
    phases = roadmap.get("phases", [])
    current_idx = next((i for i, p in enumerate(phases) if p["phase_id"] == current_phase_id), -1)

    if current_idx >= 0 and current_idx + 1 < len(phases):
        next_phase = phases[current_idx + 1]
        # Update progress to next phase
        progress["current_phase"] = next_phase["phase_id"]
        save_progress(roadmap_path, roadmap)

        # Return first task of next phase
        if next_phase.get("tasks"):
            first_task = next_phase["tasks"][0]
            return {
                "phase_id": next_phase["phase_id"],
                "phase_name": next_phase["phase_name"],
                "task": first_task
            }

    return None  # All tasks complete


def save_progress(roadmap_path, roadmap):
    """Save updated roadmap"""
    with open(roadmap_path, 'w') as f:
        json.dump(roadmap, f, indent=2)


def format_task_display(next_task):
    """Format task for display to STEWARD"""
    if not next_task:
        return """
🎉 ALL CLEANUP TASKS COMPLETE!

The foundation cleanup roadmap is finished.
Run: ./bin/cleanup-report.sh for completion summary.
"""

    task = next_task["task"]
    phase = next_task["phase_name"]

    output = f"""
╔════════════════════════════════════════════════════════════════════════════╗
║                      🎯 NEXT TASK FOR STEWARD                             ║
╚════════════════════════════════════════════════════════════════════════════╝

Phase: {phase}
Task ID: {task['task_id']}
Priority: {task['priority']}
Estimated Time: {task['estimated_time_mins']} minutes

📋 TASK: {task['name']}

{task['description']}

✅ ACCEPTANCE CRITERIA:
"""

    for i, criteria in enumerate(task.get('acceptance_criteria', []), 1):
        output += f"   {i}. {criteria}\n"

    deps = task.get('dependencies', [])
    if deps:
        output += f"\n⚠️  Dependencies: {', '.join(deps)} (must be complete first)\n"

    output += f"""
💡 When complete:
   Run: ./bin/mark-task-complete.py {task['task_id']}
   This will update the roadmap and queue the next task.

📖 Full Roadmap: .vibe/config/cleanup_roadmap.json
"""

    return output


def main():
    roadmap_path = Path(__file__).parent.parent / ".vibe/config/cleanup_roadmap.json"

    if not roadmap_path.exists():
        print("No cleanup roadmap found.")
        print("The system is either not in cleanup mode or the roadmap hasn't been created.")
        sys.exit(0)

    with open(roadmap_path) as f:
        roadmap = json.load(f)

    next_task = find_next_task(roadmap, roadmap_path)
    print(format_task_display(next_task))


if __name__ == "__main__":
    main()
