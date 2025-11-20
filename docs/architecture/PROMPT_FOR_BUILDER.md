### 🚀 Finaler MASTERPROMPT (KORRIGIERT: GAD-701)

Bitte kopiere diesen Block **1:1**. Er enthält nun alle Spezifikationen und den Auftrag, die korrekte GAD-Dokumentation zu erstellen.

````markdown:finaler Masterprompt für den Builder Agent:PROMPT_FOR_BUILDER.md
ACT AS: SENIOR PYTHON ENGINEER (SYSTEMS ARCHITECT)

CONTEXT:
We are implementing **GAD-701 "VIBE MISSION CONTROL"** (Task Tracking & Validation). This is a component of the STEWARD Governance Pillar (GAD-7XX). The architecture has been reviewed and approved.
Your goal is PURE EXECUTION of the approved plan.

OBJECTIVE:
Implement the complete Task Tracking System and formalize its specification into the official GAD document.

CONSTRAINTS (NON-NEGOTIABLE):
1.  **Code Syntax:** Use PYDANTIC V1/V2 compatible Python syntax.
2.  **Concurrency:** Use 'fcntl' for atomic File Locking (assume Unix/Linux/MacOS environment).
3.  **No Bloat:** Do not add features or dependencies not explicitly listed in the spec.
4.  **Structure:** Directory structure and file names must be EXACT.
5.  **GAD-ID:** Use GAD-701 for all documentation and file naming.

DELIVERABLES (Total 8 Files):
**I. Code Files (7):**
1.  `agency_os/core_system/task_management/__init__.py` (Expose TaskManager)
2.  `agency_os/core_system/task_management/models.py` (The Pydantic Models)
3.  `agency_os/core_system/task_management/file_lock.py` (The Atomic Write Logic)
4.  `agency_os/core_system/task_management/validator_registry.py` (The Plugin System)
5.  `agency_os/core_system/task_management/task_manager.py` (The Core Logic)
6.  `agency_os/core_system/task_management/next_task_generator.py` (Simple stub logic)
7.  `tests/test_task_manager.py` (Create 3 basic unit tests: Persistence, Lock, Validation)

**II. Documentation File (1):**
8.  `artifacts/planning/GAD-701_SPEC.md` (Formal GAD Document)

---

### 📜 TASK: GENERATE GAD-701_SPEC.md

Generate the formal GAD Document with the following content and structure, using the detailed information provided in the "APPROVED SPECIFICATION" section below:

**Title:** GAD-701: VIBE MISSION CONTROL (Task Tracking & Validation)
**Status:** APPROVED (2025-11-XX)
**Purpose:** Formal specification for the Operational Task Management Layer within the GAD-7XX STEWARD Governance Pillar.
**Sections:**
1. **Architectural Decrees** (List the 4 immutable decisions).
2. **Core Components & Data Models** (Include the Pydantic models from the spec).
3. **File System Layout** (Include the exact file tree).
4. **Manager Interface** (Include the primary methods of the TaskManager class).

---

### 🏛️ ARCHITECTURE DECREES (IMMUTABLE)

1. **State Strategy:** JSON + FileLock (No SQLite).
2. **Schema:** Pydantic Models are Single Source of Truth.
3. **Validation:** Registry Pattern (Simple dict mapping).
4. **Source of Truth Hierarchy:** `.vibe/config/roadmap.yaml` (Plan), `.vibe/state/active_mission.json` (Hot State), `.vibe/history/mission_logs/` (History).

---

### 📋 APPROVED SPECIFICATION & CODE SKELETONS

#### 1. PYDANTIC MODELS (`models.py`)
```python
from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any
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
    params: Dict[str, Any] = Field(default_factory=dict)
    status: bool = False
    last_check: Optional[datetime] = None
    error: Optional[str] = None

class Task(BaseModel):
    version: int = 1
    id: str
    name: str
    description: str
    status: TaskStatus
    priority: int = Field(default=5, ge=1, le=10)
    created_at: datetime = Field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    time_budget_mins: int = 60
    time_used_mins: int = 0
    validation_checks: List[ValidationCheck] = Field(default_factory=list)
    blocking_reason: Optional[str] = None
    related_files: List[str] = Field(default_factory=list)
    git_commits: List[str] = Field(default_factory=list)
    
    def is_complete(self) -> bool:
        return all(check.status for check in self.validation_checks)
    
    def get_failed_checks(self) -> List[ValidationCheck]:
        return [c for c in self.validation_checks if not c.status]

class ActiveMission(BaseModel):
    version: int = 1
    current_task: Optional[Task] = None
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
    task_ids: List[str] = Field(default_factory=list)

class Roadmap(BaseModel):
    version: int = 1
    project_name: str
    phases: List[RoadmapPhase]
    tasks: Dict[str, Task] = Field(default_factory=dict)
````

#### 2\. FILE LOCK IMPLEMENTATION (`file_lock.py`)

```python
import json
import fcntl
from pathlib import Path
from typing import Any, Dict

def atomic_read_json(path: Path) -> Dict[str, Any]:
    """
    Read JSON with file lock (prevents race conditions)
    """
    with open(path, 'r') as f:
        # NOTE: Using a shared lock for reading to allow multiple readers
        fcntl.flock(f.fileno(), fcntl.LOCK_SH)
        try:
            # Must seek(0) to ensure read is from the start after the lock is acquired
            f.seek(0)
            return json.load(f)
        finally:
            fcntl.flock(f.fileno(), fcntl.LOCK_UN)

def atomic_write_json(path: Path, data: Dict[str, Any]):
    """
    Atomic JSON write (lock -> temp file -> replace)
    
    This prevents:
    - Race conditions (via exclusive lock on the temporary file)
    - Corrupted JSON (via temp file)
    """
    temp_path = path.with_suffix('.tmp')
    
    # Write to temp file
    with open(temp_path, 'w') as f:
        # NOTE: Exclusive lock on the temporary file
        fcntl.flock(f.fileno(), fcntl.LOCK_EX)
        try:
            json.dump(data, f, indent=2, default=str)
            f.flush()
        finally:
            fcntl.flock(f.fileno(), fcntl.LOCK_UN)
    
    # Atomic replace (renaming is atomic on POSIX filesystems)
    temp_path.replace(path)
```

#### 3\. VALIDATOR REGISTRY (`validator_registry.py`)

```python
# FILE: agency_os/core_system/task_management/validator_registry.py

from pathlib import Path
from typing import Dict, Callable, Any
import subprocess


# ============================================================================
# VALIDATOR FUNCTIONS
# ============================================================================

def validate_tests_passing(vibe_root: Path, scope: str = "tests/") -> bool:
    """Run pytest in scope (e.g., 'tests/')"""
    result = subprocess.run(
        ["pytest", scope, "-v"],
        cwd=vibe_root,
        capture_output=True,
        timeout=60
    )
    # Return code 0 means success
    return result.returncode == 0


def validate_git_clean(vibe_root: Path) -> bool:
    """Check for uncommitted changes (git status --porcelain)"""
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=vibe_root,
        capture_output=True
    )
    # If stdout is empty, the working directory is clean
    return len(result.stdout.strip()) == 0


def validate_docs_updated(vibe_root: Path, required_files: list) -> bool:
    """Check if all required_files were modified in the last commit (HEAD~1)"""
    result = subprocess.run(
        ["git", "diff", "--name-only", "HEAD~1"],
        cwd=vibe_root,
        capture_output=True,
        text=True
    )
    
    modified_files = set(result.stdout.strip().split('\n'))
    
    # Check if all required files are in the list of modified files
    return all(req in modified_files for req in required_files)


# ============================================================================
# REGISTRY
# ============================================================================

# The registry maps the string ID (from the Task model) to the actual function
VALIDATOR_REGISTRY: Dict[str, Callable] = {
    "tests_passing": validate_tests_passing,
    "git_clean": validate_git_clean,
    "docs_updated": validate_docs_updated,
}


def run_validators(task: Any, vibe_root: Path) -> Dict[str, Any]:
    """
    Run all validators for a given task.
    
    Returns dict: {check_id: bool, check_id_error: str}
    """
    results = {}
    
    for check in task.validation_checks:
        validator_func = VALIDATOR_REGISTRY.get(check.validator)
        
        if not validator_func:
            results[check.id] = False
            results[f"{check.id}_error"] = f"Unknown validator: {check.validator}"
            continue
        
        try:
            # Call the function, passing vibe_root and any parameters from the Task model
            passed = validator_func(vibe_root, **check.params)
            results[check.id] = passed
        except Exception as e:
            results[check.id] = False
            results[f"{check.id}_error"] = str(e)
    
    return results
```

#### 4\. TASK MANAGER (`task_manager.py`)

```python
# FILE: agency_os/core_system/task_management/task_manager.py

from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime
import yaml # Import for roadmap.yaml
import json # Import for internal use

from .models import ActiveMission, Task, Roadmap, TaskStatus
from .file_lock import atomic_read_json, atomic_write_json
from .validator_registry import run_validators
from .next_task_generator import generate_next_task


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
    
    def get_current_task(self) -> Optional[Task]:
        """Get the task agent should work on right now"""
        mission = self.get_active_mission()
        return mission.current_task
    
    def get_roadmap(self) -> Roadmap:
        """Load strategic plan"""
        if not self.roadmap_file.exists():
            # In a real system, this should generate a template
            raise FileNotFoundError(f"Roadmap not found: {self.roadmap_file}")
        
        # NOTE: Using a simple file read for YAML config, assuming the Agent/User handles the lock
        # The main state (.json) is what requires the atomic lock.
        with open(self.roadmap_file, 'r') as f:
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
    
    def update_task_progress(self, time_spent_mins: int = 0, 
                             blocking_reason: Optional[str] = None) -> Task:
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
    
    def validate_current_task(self) -> Dict[str, Any]:
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
                check.error = None # Clear previous error if passed
        
        self._save_mission(mission)
        
        return {
            "valid": task.is_complete(),
            "checks": {c.id: c.status for c in task.validation_checks},
            "failed": [c.description for c in task.get_failed_checks()]
        }
    
    # ========================================================================
    # COMPLETION
    # ========================================================================
    
    def complete_current_task(self) -> Optional[Task]:
        """
        Complete current task (HARD VALIDATION)
        
        Returns next task or None if validation failed
        """
        # Validate first
        validation = self.validate_current_task()
        
        if not validation["valid"]:
            raise RuntimeError(
                f"Task validation failed. Fix required: {validation['failed']}"
            )
        
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
        
        if next_task_info and 'id' in next_task_info:
            next_task_id = next_task_info['id']
            # Load task from roadmap (since tasks are stored there)
            next_task = roadmap.tasks.get(next_task_id) 
            
            if next_task:
                mission.current_task = next_task
                mission.current_task.status = TaskStatus.IN_PROGRESS
                mission.current_task.started_at = datetime.now()
            else:
                mission.current_task = None
        else:
            mission.current_task = None # Project complete or generator failed
        
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
        self.log_dir.mkdir(parents=True, exist_ok=True) # Ensure dir exists before writing
        log_file = self.log_dir / f"{task.id}_completed.md"
        
        content = f"""# {task.name}

**Status:** {task.status.value}
**Completed:** {task.completed_at.isoformat() if task.completed_at else 'N/A'}
**Time Spent:** {task.time_used_mins} mins

## Validation Checks
{"".join(f"- [{('✅' if c.status else '❌')}] {c.description}\n" for c in task.validation_checks)}

## Related Files
{"".join(f"- {f}\n" for f in task.related_files)}

## Git Commits
{"".join(f"- {c}\n" for c in task.git_commits)}
"""
        
        with open(log_file, 'w') as f:
            f.write(content)
```

#### 5\. NEXT TASK GENERATOR (`next_task_generator.py`)

```python
# FILE: agency_os/core_system/task_management/next_task_generator.py

from typing import Optional, Dict, Any
from .models import Roadmap, ActiveMission

def generate_next_task(roadmap: Roadmap, mission: ActiveMission) -> Optional[Dict[str, Any]]:
    """
    PHASE 1 STUB: Finds the next TODO task in the roadmap.
    
    In later phases, this will contain complex logic (e.g., test-blocking checks).
    """
    
    # Simple linear search for the first task that is NOT DONE and NOT IN_PROGRESS
    for task_id, task in roadmap.tasks.items():
        if task.status == "TODO":
            # Return essential info for the TaskManager to start it
            return {'id': task_id, 'name': task.name}

    # If no TODO tasks found, check if the next phase has tasks
    # (Simplified for Phase 1 - assumes a continuous task list)
    
    return None # Indicates project completion
```
