"""Batch Operations for bulk task management (GAD-701 Task 8)"""

from typing import Any

from .models import TaskManager, TaskStatus


class BatchOperations:
    """Batch operations for managing multiple tasks at once."""

    def __init__(self, manager: TaskManager):
        """Initialize batch operations with task manager.

        Args:
            manager: TaskManager instance to use for operations
        """
        self.manager = manager

    def batch_start_tasks(self, task_ids: list[str]) -> dict[str, Any]:
        """Start multiple tasks.

        Args:
            task_ids: List of task IDs to start

        Returns:
            dict with results of each operation
        """
        results = {
            'requested': task_ids,
            'successful': [],
            'failed': [],
        }

        for task_id in task_ids:
            try:
                task = self.manager.start_task(task_id)
                results['successful'].append({
                    'id': task.id,
                    'name': task.name,
                    'status': task.status.value if hasattr(task.status, 'value') else str(task.status),
                })
            except Exception as e:
                results['failed'].append({
                    'id': task_id,
                    'error': str(e),
                })

        return results

    def batch_complete_tasks(self, task_ids: list[str], force: bool = False) -> dict[str, Any]:
        """Complete multiple tasks.

        Args:
            task_ids: List of task IDs to complete
            force: If True, skip validation

        Returns:
            dict with results of each operation
        """
        results = {
            'requested': task_ids,
            'successful': [],
            'failed': [],
        }

        for task_id in task_ids:
            try:
                if force:
                    # Direct completion without validation
                    task = self.manager.get_task(task_id)
                    task.status = TaskStatus.DONE
                    self.manager.save_current_mission()
                    results['successful'].append({
                        'id': task.id,
                        'name': task.name,
                        'method': 'forced',
                    })
                else:
                    # Validate before completing
                    task = self.manager.complete_current_task()
                    if task and task.id == task_id:
                        results['successful'].append({
                            'id': task.id,
                            'name': task.name,
                            'method': 'validated',
                        })
            except Exception as e:
                results['failed'].append({
                    'id': task_id,
                    'error': str(e),
                })

        return results

    def batch_update_priority(
        self,
        task_updates: dict[str, int]
    ) -> dict[str, Any]:
        """Update priority for multiple tasks.

        Args:
            task_updates: dict mapping task_id to new priority value

        Returns:
            dict with results of each operation
        """
        results = {
            'requested': list(task_updates.keys()),
            'successful': [],
            'failed': [],
        }

        for task_id, new_priority in task_updates.items():
            try:
                if not 1 <= new_priority <= 10:
                    raise ValueError(f"Priority must be 1-10, got {new_priority}")

                task = self.manager.get_task(task_id)
                task.priority = new_priority
                self.manager.save_current_mission()

                results['successful'].append({
                    'id': task.id,
                    'name': task.name,
                    'new_priority': new_priority,
                })
            except Exception as e:
                results['failed'].append({
                    'id': task_id,
                    'error': str(e),
                })

        return results

    def batch_block_tasks(self, blocking_pairs: list[tuple[str, str]]) -> dict[str, Any]:
        """Create blocking relationships between multiple tasks.

        Args:
            blocking_pairs: List of (blocker_id, blocked_id) tuples

        Returns:
            dict with results of each operation
        """
        results = {
            'requested': blocking_pairs,
            'successful': [],
            'failed': [],
        }

        for blocker_id, blocked_id in blocking_pairs:
            try:
                self.manager.block_task(blocker_id, blocked_id)
                results['successful'].append({
                    'blocker': blocker_id,
                    'blocked': blocked_id,
                })
            except Exception as e:
                results['failed'].append({
                    'blocker': blocker_id,
                    'blocked': blocked_id,
                    'error': str(e),
                })

        return results

    def batch_validate_tasks(self, task_ids: list[str]) -> dict[str, Any]:
        """Run validation checks on multiple tasks.

        Args:
            task_ids: List of task IDs to validate

        Returns:
            dict with validation results for each task
        """
        results = {
            'requested': task_ids,
            'results': {},
        }

        for task_id in task_ids:
            try:
                task = self.manager.get_task(task_id)

                # Count passing checks
                passing = sum(
                    1 for check in task.validation_checks if check.status
                )
                total = len(task.validation_checks)

                results['results'][task_id] = {
                    'name': task.name,
                    'passing_checks': passing,
                    'total_checks': total,
                    'pass_rate': int((passing / total) * 100) if total > 0 else 0,
                    'all_pass': passing == total,
                }
            except Exception as e:
                results['results'][task_id] = {
                    'error': str(e),
                }

        return results

    def get_batch_summary(self, task_ids: list[str]) -> dict[str, Any]:
        """Get summary of multiple tasks.

        Args:
            task_ids: List of task IDs to summarize

        Returns:
            dict with summary statistics
        """
        tasks = [
            self.manager.get_task(tid)
            for tid in task_ids
            if self.manager.get_task(tid)
        ]

        if not tasks:
            return {
                'total_tasks': 0,
                'by_status': {},
            }

        by_status = {}
        for status in TaskStatus:
            count = sum(1 for t in tasks if t.status == status)
            if count > 0:
                by_status[status.value if hasattr(status, 'value') else str(status)] = count

        avg_priority = int(sum(t.priority for t in tasks) / len(tasks))

        return {
            'total_tasks': len(tasks),
            'by_status': by_status,
            'average_priority': avg_priority,
            'total_time_budgeted': sum(t.time_budget_mins for t in tasks),
            'total_time_used': sum(t.time_used_mins for t in tasks),
        }
