"""Pydantic Models for Task Management System (GAD-701)"""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class TaskStatus(str, Enum):
    TODO = "TODO"
    IN_PROGRESS = "IN_PROGRESS"
    BLOCKED = "BLOCKED"
    DONE = "DONE"


class ValidationCheck(BaseModel):
    id: str
    description: str
    validator: str  # Key in validator_registry
    params: dict[str, Any] = Field(default_factory=dict)
    status: bool = False
    last_check: datetime | None = None
    error: str | None = None


class Task(BaseModel):
    version: int = 1
    id: str
    name: str
    description: str
    status: TaskStatus
    priority: int = Field(default=5, ge=1, le=10)
    created_at: datetime = Field(default_factory=datetime.now)
    started_at: datetime | None = None
    completed_at: datetime | None = None
    time_budget_mins: int = 60
    time_used_mins: int = 0
    validation_checks: list[ValidationCheck] = Field(default_factory=list)
    blocking_reason: str | None = None
    blocked_by: list[str] = Field(default_factory=list)  # List of task IDs blocking this task
    blocking_tasks: list[str] = Field(default_factory=list)  # List of task IDs this task blocks
    related_files: list[str] = Field(default_factory=list)
    git_commits: list[str] = Field(default_factory=list)

    def is_complete(self) -> bool:
        return all(check.status for check in self.validation_checks)

    def get_failed_checks(self) -> list[ValidationCheck]:
        return [c for c in self.validation_checks if not c.status]

    def is_blocked(self) -> bool:
        """Check if this task is currently blocked by other tasks."""
        return len(self.blocked_by) > 0


class ActiveMission(BaseModel):
    version: int = 1
    current_task: Task | None = None
    total_tasks_completed: int = 0
    total_time_spent_mins: int = 0
    current_phase: str = "PLANNING"
    last_updated: datetime = Field(default_factory=datetime.now)

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class RoadmapPhase(BaseModel):
    name: str
    status: TaskStatus
    progress: int = 0
    task_ids: list[str] = Field(default_factory=list)


class Roadmap(BaseModel):
    version: int = 1
    project_name: str
    phases: list[RoadmapPhase]
    tasks: dict[str, Task] = Field(default_factory=dict)
