"""Metrics & Reporting System for Task Management (GAD-701 Task 6)"""

from typing import Any

from .models import Roadmap, TaskStatus


class MetricsCalculator:
    """Calculate and report on task metrics and progress."""

    def __init__(self, roadmap: Roadmap):
        """Initialize metrics calculator with a roadmap."""
        self.roadmap = roadmap

    def get_overall_progress(self) -> dict[str, Any]:
        """Calculate overall project progress.

        Returns:
            dict with keys:
            - total_tasks: Total number of tasks
            - completed_tasks: Number of DONE tasks
            - in_progress_tasks: Number of IN_PROGRESS tasks
            - todo_tasks: Number of TODO tasks
            - blocked_tasks: Number of BLOCKED tasks
            - progress_percent: Overall completion percentage (0-100)
        """
        tasks = self.roadmap.tasks
        total = len(tasks)

        if total == 0:
            return {
                "total_tasks": 0,
                "completed_tasks": 0,
                "in_progress_tasks": 0,
                "todo_tasks": 0,
                "blocked_tasks": 0,
                "progress_percent": 0,
            }

        completed = sum(1 for t in tasks.values() if t.status == TaskStatus.DONE)
        in_progress = sum(1 for t in tasks.values() if t.status == TaskStatus.IN_PROGRESS)
        todo = sum(1 for t in tasks.values() if t.status == TaskStatus.TODO)
        blocked = sum(1 for t in tasks.values() if t.status == TaskStatus.BLOCKED)

        progress_percent = int((completed / total) * 100) if total > 0 else 0

        return {
            "total_tasks": total,
            "completed_tasks": completed,
            "in_progress_tasks": in_progress,
            "todo_tasks": todo,
            "blocked_tasks": blocked,
            "progress_percent": progress_percent,
        }

    def get_phase_metrics(self, phase_name: str) -> dict[str, Any] | None:
        """Get metrics for a specific phase.

        Args:
            phase_name: Name of the phase to analyze

        Returns:
            dict with phase metrics or None if phase not found
        """
        phase = None
        for p in self.roadmap.phases:
            if p.name == phase_name:
                phase = p
                break

        if not phase:
            return None

        task_ids = phase.task_ids
        phase_tasks = [self.roadmap.tasks[tid] for tid in task_ids if tid in self.roadmap.tasks]

        if not phase_tasks:
            return {
                "phase_name": phase_name,
                "phase_status": phase.status,
                "total_tasks": 0,
                "completed_tasks": 0,
                "in_progress_tasks": 0,
                "todo_tasks": 0,
                "blocked_tasks": 0,
                "progress_percent": 0,
            }

        total = len(phase_tasks)
        completed = sum(1 for t in phase_tasks if t.status == TaskStatus.DONE)
        in_progress = sum(1 for t in phase_tasks if t.status == TaskStatus.IN_PROGRESS)
        todo = sum(1 for t in phase_tasks if t.status == TaskStatus.TODO)
        blocked = sum(1 for t in phase_tasks if t.status == TaskStatus.BLOCKED)

        progress_percent = int((completed / total) * 100) if total > 0 else 0

        return {
            "phase_name": phase_name,
            "phase_status": phase.status,
            "total_tasks": total,
            "completed_tasks": completed,
            "in_progress_tasks": in_progress,
            "todo_tasks": todo,
            "blocked_tasks": blocked,
            "progress_percent": progress_percent,
        }

    def get_all_phase_metrics(self) -> list[dict[str, Any]]:
        """Get metrics for all phases.

        Returns:
            List of phase metrics dicts
        """
        metrics = []
        for phase in self.roadmap.phases:
            phase_metrics = self.get_phase_metrics(phase.name)
            if phase_metrics:
                metrics.append(phase_metrics)
        return metrics

    def get_time_metrics(self) -> dict[str, Any]:
        """Calculate time-based metrics.

        Returns:
            dict with keys:
            - total_time_budgeted_mins: Sum of all task time budgets
            - total_time_used_mins: Sum of all task time used
            - time_utilization_percent: Percentage of budget used
        """
        tasks = self.roadmap.tasks
        total_budgeted = sum(t.time_budget_mins for t in tasks.values())
        total_used = sum(t.time_used_mins for t in tasks.values())

        utilization = int((total_used / total_budgeted) * 100) if total_budgeted > 0 else 0

        return {
            "total_time_budgeted_mins": total_budgeted,
            "total_time_used_mins": total_used,
            "time_utilization_percent": utilization,
        }

    def get_priority_distribution(self) -> dict[int, int]:
        """Get distribution of tasks by priority.

        Returns:
            dict mapping priority level (1-10) to count of tasks at that level
        """
        distribution = {i: 0 for i in range(1, 11)}
        for task in self.roadmap.tasks.values():
            if 1 <= task.priority <= 10:
                distribution[task.priority] += 1
        return distribution

    def get_status_distribution(self) -> dict[str, int]:
        """Get distribution of tasks by status.

        Returns:
            dict mapping status to count of tasks with that status
        """
        distribution = {
            TaskStatus.TODO: 0,
            TaskStatus.IN_PROGRESS: 0,
            TaskStatus.BLOCKED: 0,
            TaskStatus.DONE: 0,
        }
        for task in self.roadmap.tasks.values():
            distribution[task.status] += 1
        return distribution

    def get_validation_metrics(self) -> dict[str, Any]:
        """Get metrics on validation check completion.

        Returns:
            dict with keys:
            - total_checks: Total number of validation checks
            - passing_checks: Number of passing checks
            - failing_checks: Number of failing checks
            - check_pass_percent: Percentage of passing checks
        """
        total_checks = 0
        passing_checks = 0

        for task in self.roadmap.tasks.values():
            for check in task.validation_checks:
                total_checks += 1
                if check.status:
                    passing_checks += 1

        if total_checks == 0:
            return {
                "total_checks": 0,
                "passing_checks": 0,
                "failing_checks": 0,
                "check_pass_percent": 0,
            }

        failing_checks = total_checks - passing_checks
        pass_percent = int((passing_checks / total_checks) * 100)

        return {
            "total_checks": total_checks,
            "passing_checks": passing_checks,
            "failing_checks": failing_checks,
            "check_pass_percent": pass_percent,
        }

    def generate_report(self) -> dict[str, Any]:
        """Generate comprehensive project metrics report.

        Returns:
            dict with all metrics combined
        """
        return {
            "overall_progress": self.get_overall_progress(),
            "phase_metrics": self.get_all_phase_metrics(),
            "time_metrics": self.get_time_metrics(),
            "validation_metrics": self.get_validation_metrics(),
            "priority_distribution": self.get_priority_distribution(),
            "status_distribution": self.get_status_distribution(),
        }
