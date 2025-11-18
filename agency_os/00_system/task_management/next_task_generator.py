"""Next Task Generator (GAD-701)"""

from typing import Any

from .models import ActiveMission, Roadmap, TaskStatus


def generate_next_task(roadmap: Roadmap, mission: ActiveMission) -> dict[str, Any] | None:
    """
    PHASE 1 STUB: Finds the next TODO task in the roadmap.

    In later phases, this will contain complex logic (e.g., test-blocking checks).
    """

    # Simple linear search for the first task that is NOT DONE and NOT IN_PROGRESS
    for task_id, task in roadmap.tasks.items():
        if task.status == TaskStatus.TODO:
            # Return essential info for the TaskManager to start it
            return {'id': task_id, 'name': task.name}

    # If no TODO tasks found, check if the next phase has tasks
    # (Simplified for Phase 1 - assumes a continuous task list)

    return None  # Indicates project completion
