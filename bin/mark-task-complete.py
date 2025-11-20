#!/usr/bin/env python3
"""
Mark Task Complete - Update roadmap when task is done

Usage: ./bin/mark-task-complete.py TASK_ID
"""

import json
import sys
from datetime import datetime
from pathlib import Path


def load_roadmap():
    """Load the active roadmap (Phase 2.5 or cleanup)"""
    # Try Phase 2.5 roadmap first
    roadmap_path = Path(__file__).parent.parent / "docs/roadmap/phase_2_5_foundation.json"

    if roadmap_path.exists():
        with open(roadmap_path) as f:
            return json.load(f), roadmap_path

    # Fall back to legacy cleanup roadmap
    roadmap_path = Path(__file__).parent.parent / ".vibe/config/cleanup_roadmap.json"

    if not roadmap_path.exists():
        print("❌ No active roadmap found")
        sys.exit(1)

    with open(roadmap_path) as f:
        return json.load(f), roadmap_path


def mark_complete(roadmap, task_id):
    """Mark a task as complete"""
    progress = roadmap.get("progress_tracking", {})
    completed = progress.get("completed_tasks", [])

    if task_id in completed:
        print(f"⚠️  Task {task_id} already marked complete")
        return roadmap

    # Verify task exists
    task_found = False
    for phase in roadmap.get("phases", []):
        for task in phase.get("tasks", []):
            if task["task_id"] == task_id:
                task_found = True
                break

    if not task_found:
        print(f"❌ Task {task_id} not found in roadmap")
        sys.exit(1)

    # Add to completed list
    completed.append(task_id)
    progress["completed_tasks"] = completed
    progress["last_updated"] = datetime.utcnow().isoformat() + "Z"

    print(f"✅ Task {task_id} marked complete")
    return roadmap


def save_roadmap(roadmap_path, roadmap):
    """Save updated roadmap"""
    with open(roadmap_path, "w") as f:
        json.dump(roadmap, f, indent=2)
    print(f"💾 Roadmap updated: {roadmap_path}")


def show_progress(roadmap):
    """Show overall progress"""
    progress = roadmap.get("progress_tracking", {})
    completed = len(progress.get("completed_tasks", []))

    total_tasks = 0
    for phase in roadmap.get("phases", []):
        total_tasks += len(phase.get("tasks", []))

    pct = (completed / total_tasks * 100) if total_tasks > 0 else 0

    print(f"\n📊 Progress: {completed}/{total_tasks} tasks complete ({pct:.1f}%)")
    print(f"   Current Phase: {progress.get('current_phase', 'UNKNOWN')}")
    print("\n💡 Next: Run ./bin/next-task.py to see what's next")


def main():
    if len(sys.argv) < 2:
        print("Usage: ./bin/mark-task-complete.py TASK_ID")
        print("Example: ./bin/mark-task-complete.py Q001")
        sys.exit(1)

    task_id = sys.argv[1]

    roadmap, roadmap_path = load_roadmap()
    roadmap = mark_complete(roadmap, task_id)
    save_roadmap(roadmap_path, roadmap)
    show_progress(roadmap)


if __name__ == "__main__":
    main()
