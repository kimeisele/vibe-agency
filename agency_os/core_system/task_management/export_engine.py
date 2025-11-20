"""Multi-format Export Engine for task reports (GAD-701 Task 7)"""

import json
from io import StringIO
from typing import Any

from .models import Roadmap, TaskStatus


class ExportEngine:
    """Export roadmap and task data to various formats."""

    def __init__(self, roadmap: Roadmap):
        """Initialize export engine with roadmap."""
        self.roadmap = roadmap

    def to_json(self, pretty: bool = True) -> str:
        """Export roadmap to JSON format.

        Args:
            pretty: If True, use indentation for readability

        Returns:
            JSON string representation of roadmap
        """
        roadmap_dict = {
            "version": self.roadmap.version,
            "project_name": self.roadmap.project_name,
            "phases": [
                {
                    "name": p.name,
                    "status": p.status.value if hasattr(p.status, "value") else str(p.status),
                    "progress": p.progress,
                    "task_count": len(p.task_ids),
                }
                for p in self.roadmap.phases
            ],
            "tasks_summary": {
                "total": len(self.roadmap.tasks),
                "done": sum(1 for t in self.roadmap.tasks.values() if t.status == TaskStatus.DONE),
                "in_progress": sum(
                    1 for t in self.roadmap.tasks.values() if t.status == TaskStatus.IN_PROGRESS
                ),
                "todo": sum(1 for t in self.roadmap.tasks.values() if t.status == TaskStatus.TODO),
                "blocked": sum(
                    1 for t in self.roadmap.tasks.values() if t.status == TaskStatus.BLOCKED
                ),
            },
        }

        indent = 2 if pretty else None
        return json.dumps(roadmap_dict, indent=indent)

    def to_csv(self) -> str:
        """Export task summary to CSV format.

        Returns:
            CSV string with task data
        """
        output = StringIO()

        # CSV Header
        output.write("ID,Name,Status,Priority,Created,Progress\n")

        # Task rows
        for task in self.roadmap.tasks.values():
            task_id = task.id
            name = task.name.replace(",", ";")  # Escape commas
            status = task.status.value if hasattr(task.status, "value") else str(task.status)
            priority = str(task.priority)
            created = task.created_at.isoformat() if task.created_at else "N/A"

            # Calculate task progress from validation checks
            if task.validation_checks:
                passing = sum(1 for check in task.validation_checks if check.status)
                total = len(task.validation_checks)
                progress = int((passing / total) * 100) if total > 0 else 0
            else:
                progress = 0

            output.write(f"{task_id},{name},{status},{priority},{created},{progress}%\n")

        return output.getvalue()

    def to_markdown(self) -> str:
        """Export roadmap to Markdown format.

        Returns:
            Markdown formatted report
        """
        lines = []

        # Header
        lines.append(f"# {self.roadmap.project_name}")
        lines.append("")
        lines.append("## Project Overview")
        lines.append("")

        # Summary stats
        total_tasks = len(self.roadmap.tasks)
        done_tasks = sum(1 for t in self.roadmap.tasks.values() if t.status == TaskStatus.DONE)
        lines.append(
            f"**Progress:** {done_tasks}/{total_tasks} tasks complete "
            f"({int((done_tasks / total_tasks) * 100) if total_tasks > 0 else 0}%)"
        )
        lines.append("")

        # Phases
        lines.append("## Phases")
        lines.append("")

        for phase in self.roadmap.phases:
            phase_tasks = [
                self.roadmap.tasks[tid] for tid in phase.task_ids if tid in self.roadmap.tasks
            ]

            phase_status = (
                phase.status.value if hasattr(phase.status, "value") else str(phase.status)
            )
            lines.append(f"### {phase.name}")
            lines.append(f"**Status:** {phase_status} | **Progress:** {phase.progress}%")
            lines.append("")

            # Phase tasks
            for task in phase_tasks:
                status = task.status.value if hasattr(task.status, "value") else str(task.status)
                lines.append(f"- **{task.name}** [{status}] (Priority: {task.priority}/10)")

                if task.description:
                    lines.append(f"  - {task.description}")

                # Task progress
                if task.validation_checks:
                    passing = sum(1 for c in task.validation_checks if c.status)
                    total = len(task.validation_checks)
                    progress = int((passing / total) * 100) if total > 0 else 0
                    lines.append(f"  - Validation: {passing}/{total} checks ({progress}%)")

                lines.append("")

        return "\n".join(lines)

    def to_summary(self) -> dict[str, Any]:
        """Generate summary report as dict.

        Returns:
            Dictionary with comprehensive summary
        """
        tasks = self.roadmap.tasks
        total_tasks = len(tasks)

        done_tasks = [t for t in tasks.values() if t.status == TaskStatus.DONE]
        in_progress = [t for t in tasks.values() if t.status == TaskStatus.IN_PROGRESS]
        todo_tasks = [t for t in tasks.values() if t.status == TaskStatus.TODO]
        blocked_tasks = [t for t in tasks.values() if t.status == TaskStatus.BLOCKED]

        # Calculate metrics
        done_count = len(done_tasks)
        progress_percent = int((done_count / total_tasks) * 100) if total_tasks > 0 else 0

        avg_priority = (
            int(sum(t.priority for t in tasks.values()) / total_tasks) if total_tasks > 0 else 0
        )

        total_time_budgeted = sum(t.time_budget_mins for t in tasks.values())
        total_time_used = sum(t.time_used_mins for t in tasks.values())

        return {
            "project_name": self.roadmap.project_name,
            "total_tasks": total_tasks,
            "completed_tasks": done_count,
            "in_progress_tasks": len(in_progress),
            "todo_tasks": len(todo_tasks),
            "blocked_tasks": len(blocked_tasks),
            "progress_percent": progress_percent,
            "average_priority": avg_priority,
            "time_budgeted_mins": total_time_budgeted,
            "time_used_mins": total_time_used,
            "phases": [
                {
                    "name": p.name,
                    "status": p.status.value if hasattr(p.status, "value") else str(p.status),
                    "progress": p.progress,
                }
                for p in self.roadmap.phases
            ],
        }
