"""Next Task Generator - Auto-selects next task based on roadmap progress (GAD-701)"""

from typing import Any

from .models import ActiveMission, Roadmap, TaskStatus


def generate_next_task(roadmap: Roadmap, mission: ActiveMission, use_priority: bool = True) -> dict[str, Any] | None:
    """
    Auto-select the next task based on roadmap state.

    Strategy (in priority order):
    1. Find next TODO task in current phase (optionally sorted by priority)
    2. If all tasks in current phase are done, move to next phase
    3. If all phases complete, return None (project done)

    Args:
        roadmap: The project roadmap
        mission: Current mission state
        use_priority: If True, select highest priority TODO task (default: True)
                     If False, select first TODO task in phase order

    Returns:
        dict with 'id' and 'name' keys, or None if no more tasks

    Example:
        >>> # Auto-select highest priority TODO task
        >>> result = generate_next_task(roadmap, mission)
        >>> if result:
        ...     print(f"Next task: {result['name']}")
        ...
        >>> # Or select first TODO in order
        >>> result = generate_next_task(roadmap, mission, use_priority=False)
    """
    # Strategy 1: Find next TODO task in any phase
    candidate_tasks = []

    for phase in roadmap.phases:
        # Process tasks in phase order
        for task_id in phase.task_ids:
            if task_id not in roadmap.tasks:
                continue  # Skip if task doesn't exist

            task = roadmap.tasks[task_id]

            # Skip already done or in-progress tasks
            if task.status in (TaskStatus.DONE, TaskStatus.IN_PROGRESS):
                continue

            # Check if task is blocked by incomplete dependencies
            if hasattr(task, "blocked_by") and task.blocked_by:
                # Task is blocked, skip it
                continue

            # Found a TODO task - add to candidates
            candidate_tasks.append((task_id, task))

    # If use_priority, sort by priority (highest first) and return top task
    if use_priority and candidate_tasks:
        # Sort by priority descending (higher priority = lower number semantically, but stored as 1-10)
        # In this model, priority 10 is highest, priority 1 is lowest
        candidate_tasks.sort(key=lambda x: x[1].priority, reverse=True)
        task_id, task = candidate_tasks[0]
        return {"id": task_id, "name": task.name}

    # If not using priority, return first candidate
    if candidate_tasks:
        task_id, task = candidate_tasks[0]
        return {"id": task_id, "name": task.name}

    # Strategy 2: Check if current phase is complete, move to next
    if roadmap.phases:
        current_phase_idx = _find_current_phase_index(roadmap, mission)

        if current_phase_idx is not None and current_phase_idx < len(roadmap.phases) - 1:
            next_phase_idx = current_phase_idx + 1
            next_phase = roadmap.phases[next_phase_idx]

            # Try to find first task in next phase (with same selection strategy)
            next_phase_tasks = []
            for task_id in next_phase.task_ids:
                if task_id in roadmap.tasks:
                    task = roadmap.tasks[task_id]
                    if task.status == TaskStatus.TODO:
                        next_phase_tasks.append((task_id, task))

            if next_phase_tasks:
                if use_priority:
                    next_phase_tasks.sort(key=lambda x: x[1].priority, reverse=True)
                task_id, task = next_phase_tasks[0]
                return {"id": task_id, "name": task.name}

    # No more tasks found - project complete
    return None


def _find_current_phase_index(roadmap: Roadmap, mission: ActiveMission) -> int | None:
    """Find the index of the current phase based on mission state."""
    for idx, phase in enumerate(roadmap.phases):
        if phase.name == mission.current_phase:
            return idx

    # If current phase not found, default to first phase
    return 0 if roadmap.phases else None
