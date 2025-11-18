"""Task Archival System - persist completed task snapshots (GAD-701 Task 9)"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from .models import Task


class TaskArchive:
    """Archive system for managing completed task snapshots."""

    def __init__(self, archive_dir: Path | None = None):
        """Initialize archive system.

        Args:
            archive_dir: Directory to store archived tasks. Defaults to .vibe/archive
        """
        if archive_dir is None:
            archive_dir = Path.cwd() / '.vibe' / 'archive'

        self.archive_dir = archive_dir
        self.archive_dir.mkdir(parents=True, exist_ok=True)

    def archive_task(self, task: Task) -> dict[str, Any]:
        """Archive a completed task.

        Args:
            task: Task to archive

        Returns:
            dict with archive metadata
        """
        # Create task snapshot
        snapshot = {
            'id': task.id,
            'name': task.name,
            'description': task.description,
            'status': task.status.value if hasattr(task.status, 'value') else str(task.status),
            'priority': task.priority,
            'created_at': task.created_at.isoformat() if task.created_at else None,
            'started_at': task.started_at.isoformat() if task.started_at else None,
            'completed_at': task.completed_at.isoformat() if task.completed_at else None,
            'time_budget_mins': task.time_budget_mins,
            'time_used_mins': task.time_used_mins,
            'validation_summary': {
                'total_checks': len(task.validation_checks),
                'passing_checks': sum(
                    1 for c in task.validation_checks if c.status
                ),
            },
            'archived_at': datetime.now().isoformat(),
        }

        # Save to archive file
        archive_file = self.archive_dir / f'{task.id}_archive.json'

        with open(archive_file, 'w') as f:
            json.dump(snapshot, f, indent=2)

        return {
            'task_id': task.id,
            'task_name': task.name,
            'archived_file': str(archive_file),
            'archived_at': snapshot['archived_at'],
        }

    def get_archived_task(self, task_id: str) -> dict[str, Any] | None:
        """Retrieve an archived task snapshot.

        Args:
            task_id: ID of archived task

        Returns:
            dict with archived task data or None if not found
        """
        archive_file = self.archive_dir / f'{task_id}_archive.json'

        if not archive_file.exists():
            return None

        with open(archive_file) as f:
            return json.load(f)

    def list_archived_tasks(self) -> list[dict[str, Any]]:
        """List all archived tasks.

        Returns:
            List of archived task summaries
        """
        archives = []

        for archive_file in sorted(self.archive_dir.glob('*_archive.json')):
            try:
                with open(archive_file) as f:
                    data = json.load(f)
                    archives.append({
                        'id': data['id'],
                        'name': data['name'],
                        'completed_at': data['completed_at'],
                        'archived_at': data['archived_at'],
                        'priority': data['priority'],
                    })
            except Exception:
                pass  # Skip malformed archives

        return archives

    def get_archive_stats(self) -> dict[str, Any]:
        """Get statistics about archived tasks.

        Returns:
            dict with archive statistics
        """
        archived_tasks = self.list_archived_tasks()

        if not archived_tasks:
            return {
                'total_archived': 0,
                'archive_size_bytes': 0,
                'oldest_archive': None,
                'newest_archive': None,
            }

        # Calculate total size
        total_size = sum(
            (self.archive_dir / f'{t["id"]}_archive.json').stat().st_size
            for t in archived_tasks
            if (self.archive_dir / f'{t["id"]}_archive.json').exists()
        )

        # Find oldest and newest
        completion_times = [
            t['completed_at'] for t in archived_tasks if t['completed_at']
        ]

        return {
            'total_archived': len(archived_tasks),
            'archive_size_bytes': total_size,
            'oldest_archive': min(completion_times) if completion_times else None,
            'newest_archive': max(completion_times) if completion_times else None,
        }

    def export_archive_as_json(self) -> str:
        """Export all archives as JSON.

        Returns:
            JSON string with all archived tasks
        """
        archived_tasks = []

        for archive_file in sorted(self.archive_dir.glob('*_archive.json')):
            try:
                with open(archive_file) as f:
                    archived_tasks.append(json.load(f))
            except Exception:
                pass

        return json.dumps(archived_tasks, indent=2)

    def export_archive_as_csv(self) -> str:
        """Export archives summary as CSV.

        Returns:
            CSV string with archived task summaries
        """
        lines = ['ID,Name,Priority,Status,Completed,Archived']
        archived_tasks = self.list_archived_tasks()

        for task in archived_tasks:
            lines.append(
                f'{task["id"]},{task["name"]},{task["priority"]},'
                f'DONE,{task["completed_at"]},{task["archived_at"]}'
            )

        return '\n'.join(lines)

    def cleanup_old_archives(self, days: int = 30) -> dict[str, Any]:
        """Remove archives older than specified days.

        Args:
            days: Age threshold in days

        Returns:
            dict with cleanup results
        """
        cutoff = datetime.now().timestamp() - (days * 86400)

        removed_count = 0
        freed_bytes = 0

        for archive_file in self.archive_dir.glob('*_archive.json'):
            if archive_file.stat().st_mtime < cutoff:
                freed_bytes += archive_file.stat().st_size
                archive_file.unlink()
                removed_count += 1

        return {
            'removed_count': removed_count,
            'freed_bytes': freed_bytes,
            'cutoff_days': days,
        }

    def get_archive_by_date_range(
        self,
        start_date: str,
        end_date: str
    ) -> list[dict[str, Any]]:
        """Get archived tasks completed in date range.

        Args:
            start_date: ISO format start date
            end_date: ISO format end date

        Returns:
            List of matching archived tasks
        """
        archived_tasks = self.list_archived_tasks()
        matching = []

        for task in archived_tasks:
            if task['completed_at']:
                if start_date <= task['completed_at'] <= end_date:
                    matching.append(task)

        return matching
