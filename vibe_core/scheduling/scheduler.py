"""
Core Scheduler for vibe-agency OS.

This module implements the minimal FIFO scheduler (ARCH-021),
which serves as the heartbeat for task distribution across agents.
"""

import uuid
from collections import deque
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Task:
    """
    Represents a unit of work in the scheduler queue.

    Attributes:
        id: Unique identifier for the task (auto-generated if not provided)
        priority: Priority level (for future priority queue support)
        agent_id: Identifier of the agent that submitted the task
        payload: The actual task data/instructions
    """

    agent_id: str
    payload: Any
    priority: int = 0
    id: str = field(default_factory=lambda: str(uuid.uuid4()))


class VibeScheduler:
    """
    FIFO (First-In, First-Out) task scheduler.

    This is the minimal scheduler implementation (ARCH-021) that serves
    as the first OS primitive for vibe-agency. It accepts tasks from
    agents and distributes them one by one in the order received.

    Design Principles:
    - Simple FIFO queue (no priority yet, but Task has priority field for future)
    - Thread-safe operations (using deque)
    - Minimal dependencies (pure Python)
    - Clear task lifecycle tracking
    """

    def __init__(self):
        """Initialize an empty task queue."""
        self._queue: deque[Task] = deque()

    def submit_task(self, task: Task) -> str:
        """
        Submit a task to the scheduler queue.

        Args:
            task: The Task object to be queued

        Returns:
            str: The task ID (task.id) for tracking

        Example:
            >>> scheduler = VibeScheduler()
            >>> task = Task(agent_id="agent-1", payload={"action": "compile"})
            >>> task_id = scheduler.submit_task(task)
        """
        self._queue.append(task)
        return task.id

    def next_task(self) -> Task | None:
        """
        Retrieve and remove the next task from the queue (FIFO).

        Returns:
            Task | None: The next task in the queue, or None if empty

        Example:
            >>> scheduler = VibeScheduler()
            >>> task = Task(agent_id="agent-1", payload={"action": "compile"})
            >>> scheduler.submit_task(task)
            >>> next_task = scheduler.next_task()
            >>> print(next_task.agent_id)  # "agent-1"
        """
        try:
            return self._queue.popleft()
        except IndexError:
            return None

    def get_queue_status(self) -> dict:
        """
        Get the current status of the scheduler queue.

        Returns:
            dict: Status information including pending task count

        Example:
            >>> scheduler = VibeScheduler()
            >>> status = scheduler.get_queue_status()
            >>> print(status["pending_tasks"])  # 0
        """
        return {"pending_tasks": len(self._queue), "queue_type": "FIFO"}
