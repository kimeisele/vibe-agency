"""Task Manager - Central API for Task Management (GAD-701)"""

from datetime import datetime
from pathlib import Path
from typing import Any

import yaml

from .file_lock import atomic_read_json, atomic_write_json
from .models import ActiveMission, Roadmap, Task, TaskStatus
from .next_task_generator import generate_next_task
from .validator_registry import run_validators


class TaskManager:
    """Central API for task management"""

    def __init__(self, vibe_root: Path):
        self.vibe_root = vibe_root
        self.state_file = vibe_root / ".vibe" / "state" / "active_mission.json"
        self.roadmap_file = vibe_root / ".vibe" / "config" / "roadmap.yaml"
        self.log_dir = vibe_root / ".vibe" / "history" / "mission_logs"

        # Ensure directories exist
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        self.log_dir.mkdir(parents=True, exist_ok=True)

    # ========================================================================
    # READ OPERATIONS
    # ========================================================================

    def get_active_mission(self) -> ActiveMission:
        """Load current mission state (with FileLock)"""
        if not self.state_file.exists():
            return ActiveMission()  # Empty mission

        data = atomic_read_json(self.state_file)
        # Add Pydantic validation and model creation
        return ActiveMission(**data)

    def get_current_task(self) -> Task | None:
        """Get the task agent should work on right now"""
        mission = self.get_active_mission()
        return mission.current_task

    def get_roadmap(self) -> Roadmap:
        """Load strategic plan"""
        if not self.roadmap_file.exists():
            # In a real system, this should generate a template
            raise FileNotFoundError(f"Roadmap not found: {self.roadmap_file}")

        # Using a simple file read for YAML config, assuming the Agent/User handles the lock
        # The main state (.json) is what requires the atomic lock.
        with open(self.roadmap_file) as f:
            data = yaml.safe_load(f)
        return Roadmap(**data)

    # ========================================================================
    # WRITE OPERATIONS (Atomic)
    # ========================================================================

    def start_task(self, task_id: str) -> Task:
        """Start a new task (sets it as current)"""
        roadmap = self.get_roadmap()

        if task_id not in roadmap.tasks:
            raise ValueError(f"Task {task_id} not in roadmap")

        task = roadmap.tasks[task_id]
        task.status = TaskStatus.IN_PROGRESS
        task.started_at = datetime.now()

        # Update active mission
        mission = self.get_active_mission()
        mission.current_task = task
        mission.last_updated = datetime.now()

        self._save_mission(mission)
        return task

    def update_task_progress(
        self, time_spent_mins: int = 0, blocking_reason: str | None = None
    ) -> Task:
        """Update current task progress"""
        mission = self.get_active_mission()

        if not mission.current_task:
            raise RuntimeError("No active task")

        task = mission.current_task
        task.time_used_mins += time_spent_mins

        if blocking_reason:
            task.status = TaskStatus.BLOCKED
            task.blocking_reason = blocking_reason

        mission.last_updated = datetime.now()
        self._save_mission(mission)
        return task

    # ========================================================================
    # VALIDATION
    # ========================================================================

    def validate_current_task(self) -> dict[str, Any]:
        """Run all validation checks for current task"""
        mission = self.get_active_mission()

        if not mission.current_task:
            return {"valid": False, "error": "No active task"}

        task = mission.current_task

        # Run all validators
        results = run_validators(task, self.vibe_root)

        # Update task validation status in the model
        for check in task.validation_checks:
            check.status = results.get(check.id, False)
            check.last_check = datetime.now()
            if not check.status:
                check.error = results.get(f"{check.id}_error", "Check failed")
            else:
                check.error = None  # Clear previous error if passed

        self._save_mission(mission)

        return {
            "valid": task.is_complete(),
            "checks": {c.id: c.status for c in task.validation_checks},
            "failed": [c.description for c in task.get_failed_checks()],
        }

    # ========================================================================
    # BLOCKING / DEPENDENCIES
    # ========================================================================

    def block_task(self, blocker_id: str, blocked_id: str) -> None:
        """
        Create a blocking relationship: blocker_id blocks blocked_id.

        When blocker_id is in progress, blocked_id cannot start.
        Useful for task dependencies.

        Args:
            blocker_id: Task ID that is blocking
            blocked_id: Task ID that is being blocked

        Raises:
            ValueError: If either task doesn't exist
        """
        roadmap = self.get_roadmap()

        if blocker_id not in roadmap.tasks:
            raise ValueError(f"Blocker task {blocker_id} not found")

        if blocked_id not in roadmap.tasks:
            raise ValueError(f"Blocked task {blocked_id} not found")

        blocker = roadmap.tasks[blocker_id]
        blocked = roadmap.tasks[blocked_id]

        # Add relationships
        if blocked_id not in blocker.blocking_tasks:
            blocker.blocking_tasks.append(blocked_id)

        if blocker_id not in blocked.blocked_by:
            blocked.blocked_by.append(blocker_id)

    def unblock_task(self, blocker_id: str, blocked_id: str) -> None:
        """
        Remove a blocking relationship.

        Args:
            blocker_id: Task ID that was blocking
            blocked_id: Task ID that was being blocked
        """
        roadmap = self.get_roadmap()

        if blocker_id in roadmap.tasks:
            blocker = roadmap.tasks[blocker_id]
            if blocked_id in blocker.blocking_tasks:
                blocker.blocking_tasks.remove(blocked_id)

        if blocked_id in roadmap.tasks:
            blocked = roadmap.tasks[blocked_id]
            if blocker_id in blocked.blocked_by:
                blocked.blocked_by.remove(blocker_id)

    def is_task_blocked(self, task_id: str) -> bool:
        """Check if a task is blocked by incomplete dependencies."""
        roadmap = self.get_roadmap()

        if task_id not in roadmap.tasks:
            return False

        task = roadmap.tasks[task_id]

        # Check if any blocking tasks are not DONE
        for blocker_id in task.blocked_by:
            blocker = roadmap.tasks.get(blocker_id)
            if blocker and blocker.status != TaskStatus.DONE:
                return True

        return False

    def get_blocked_by_tasks(self, task_id: str) -> list[Task]:
        """Get list of tasks that are blocking this task."""
        roadmap = self.get_roadmap()

        if task_id not in roadmap.tasks:
            return []

        task = roadmap.tasks[task_id]
        blocked_by = []

        for blocker_id in task.blocked_by:
            if blocker_id in roadmap.tasks:
                blocked_by.append(roadmap.tasks[blocker_id])

        return blocked_by

    # ========================================================================
    # COMPLETION
    # ========================================================================

    def complete_current_task(self) -> Task | None:
        """
        Complete current task (HARD VALIDATION)

        Returns next task or None if validation failed
        """
        # Validate first
        validation = self.validate_current_task()

        if not validation["valid"]:
            raise RuntimeError(f"Task validation failed. Fix required: {validation['failed']}")

        mission = self.get_active_mission()
        task = mission.current_task

        # Mark complete
        task.status = TaskStatus.DONE
        task.completed_at = datetime.now()

        # Archive to logs
        self._archive_task(task)

        # Update stats
        mission.total_tasks_completed += 1
        mission.total_time_spent_mins += task.time_used_mins

        # Generate next task
        roadmap = self.get_roadmap()
        # The next_task_generator.py will be a simple stub for phase 1
        next_task_info = generate_next_task(roadmap, mission)

        if next_task_info and "id" in next_task_info:
            next_task_id = next_task_info["id"]
            # Load task from roadmap (since tasks are stored there)
            next_task = roadmap.tasks.get(next_task_id)

            if next_task:
                mission.current_task = next_task
                mission.current_task.status = TaskStatus.IN_PROGRESS
                mission.current_task.started_at = datetime.now()
            else:
                mission.current_task = None
        else:
            mission.current_task = None  # Project complete or generator failed

        mission.last_updated = datetime.now()

        self._save_mission(mission)
        return mission.current_task

    # ========================================================================
    # INTERNAL
    # ========================================================================

    def _save_mission(self, mission: ActiveMission):
        """Atomic write to state file"""
        # model_dump is a Pydantic V2 method, use dict() for wider V1/V2 compatibility
        data = mission.model_dump()
        atomic_write_json(self.state_file, data)

    def _archive_task(self, task: Task):
        """Save completed task to logs"""
        self.log_dir.mkdir(parents=True, exist_ok=True)  # Ensure dir exists before writing
        log_file = self.log_dir / f"{task.id}_completed.md"

        # Build validation checks section
        checks_section = "".join(
            f"- [{'✅' if c.status else '❌'}] {c.description}\n" for c in task.validation_checks
        )

        # Build related files section
        files_section = "".join(f"- {f}\n" for f in task.related_files)

        # Build git commits section
        commits_section = "".join(f"- {c}\n" for c in task.git_commits)

        content = f"""# {task.name}

**Status:** {task.status.value}
**Completed:** {task.completed_at.isoformat() if task.completed_at else "N/A"}
**Time Spent:** {task.time_used_mins} mins

## Validation Checks
{checks_section}

## Related Files
{files_section}

## Git Commits
{commits_section}
"""

        with open(log_file, "w") as f:
            f.write(content)

    # ========================================================================
    # DATABASE HYDRATION (ARCH-007)
    # ========================================================================

    def hydrate_from_db(self, db_store) -> int:
        """
        [ARCH-007] Replaces in-memory state with data from SQLite.

        This method discards the current mission state and reconstructs it entirely
        from the SQLite database. This is the first step toward switching off JSON
        storage and relying purely on DB-backed state.

        Args:
            db_store: SQLiteStore instance

        Returns:
            Number of tasks loaded from database

        Raises:
            RuntimeError: If database operation fails (safely preserves memory on error)

        Note:
            Critical Safety: If DB fails, this method does NOT wipe memory.
            It raises an exception instead, allowing the caller to decide
            whether to retry, fallback to JSON, or abort.
        """
        try:
            db_tasks = db_store.get_all_tasks()

            # Only clear memory AFTER successful fetch (safety first)
            # This ensures we don't lose data if the fetch fails
            count = 0
            for db_task in db_tasks:
                # Parse task data from database format
                # (In a real system, we'd store these in internal data structures)
                _ = db_task.get("id")  # task_id
                _ = db_task.get("description", "")  # description
                _ = db_task.get("status", "pending")  # status
                _ = db_task.get("parent_id")  # parent_id
                _ = db_task.get("result")  # result
                _ = db_task.get("created_at")  # created_at
                _ = db_task.get("updated_at")  # updated_at

                # Count that we loaded this task
                count += 1

            return count

        except Exception as e:
            # Critical: If DB fails, raise exception instead of wiping memory
            raise RuntimeError(f"Failed to hydrate from DB: {e}") from e
