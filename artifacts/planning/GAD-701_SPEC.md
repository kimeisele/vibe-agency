# GAD-701: VIBE MISSION CONTROL (Task Tracking & Validation)

**Status:** APPROVED (2025-11-18)  
**Pillar:** GAD-7XX STEWARD Governance  
**Purpose:** Formal specification for the Operational Task Management Layer

---

## 1. Architectural Decrees (Immutable)

The following four decisions form the foundation of the Task Tracking System and are not subject to change without explicit amendment:

### 1.1 State Strategy: JSON + FileLock (No SQLite)

- All operational state is stored as JSON files (human-readable, version-controllable)
- Atomic writes are protected by `fcntl` file locking (POSIX-compliant)
- No database layer: simplifies deployment and debugging
- State hierarchy: `.vibe/config/roadmap.yaml` (Plan) → `.vibe/state/active_mission.json` (Hot State) → `.vibe/history/mission_logs/` (History)

### 1.2 Schema: Pydantic Models are Single Source of Truth

- All data structures are defined in `models.py` using Pydantic V1/V2 compatible syntax
- Validation occurs at deserialization (model instantiation)
- JSON encoding uses ISO 8601 for datetime fields
- Models are immutable once frozen (optional, can be overridden)

### 1.3 Validation: Registry Pattern (Simple Dict Mapping)

- Validators are registered in `validator_registry.py` as a dictionary mapping
- Each validator is a callable that accepts `(vibe_root: Path, **params)` and returns `bool`
- Custom validators can be added by extending `VALIDATOR_REGISTRY`
- Validation failures are tracked in `ValidationCheck.error` and `ValidationCheck.last_check`

### 1.4 Source of Truth Hierarchy

| Level | File | Purpose | Example |
|-------|------|---------|---------|
| **Strategic** | `.vibe/config/roadmap.yaml` | Master plan (phases, all tasks) | 100+ tasks across 5 phases |
| **Operational** | `.vibe/state/active_mission.json` | Current state (which task, progress) | Task 23, 47 mins elapsed |
| **Historical** | `.vibe/history/mission_logs/*.md` | Completed task records | Task 23 completed in 52 mins |

---

## 2. Core Components & Data Models

### 2.1 TaskStatus (Enum)

```python
class TaskStatus(str, Enum):
    TODO = "TODO"               # Not started
    IN_PROGRESS = "IN_PROGRESS" # Currently being worked on
    BLOCKED = "BLOCKED"         # Waiting on external input
    DONE = "DONE"              # Completed and validated
```

### 2.2 ValidationCheck (Model)

Represents a single validation rule attached to a task.

```python
class ValidationCheck(BaseModel):
    id: str                              # Unique identifier (e.g., "check_001")
    description: str                     # Human-readable description
    validator: str                       # Registry key (e.g., "tests_passing")
    params: Dict[str, Any]              # Parameters passed to validator function
    status: bool = False                # Current check result
    last_check: Optional[datetime]      # When was it last evaluated
    error: Optional[str]                # Error message if failed
```

### 2.3 Task (Model)

The core unit of work.

```python
class Task(BaseModel):
    version: int = 1                          # Schema version
    id: str                                   # Unique task ID
    name: str                                 # Human-readable name
    description: str                          # Detailed description
    status: TaskStatus                        # Current status
    priority: int = Field(default=5, ge=1, le=10)  # Priority 1-10
    created_at: datetime                      # When created
    started_at: Optional[datetime]            # When work started
    completed_at: Optional[datetime]          # When work completed
    time_budget_mins: int = 60               # Estimated time
    time_used_mins: int = 0                  # Actual time spent
    validation_checks: List[ValidationCheck]  # Associated validations
    blocking_reason: Optional[str]            # Why blocked (if BLOCKED)
    related_files: List[str]                  # Affected files
    git_commits: List[str]                    # Associated commits
    
    # Methods
    is_complete() -> bool                     # All checks passed?
    get_failed_checks() -> List[ValidationCheck]  # Which checks failed?
```

### 2.4 ActiveMission (Model)

Current operational state of the system.

```python
class ActiveMission(BaseModel):
    version: int = 1                          # Schema version
    current_task: Optional[Task]              # Task being worked on
    total_tasks_completed: int = 0            # Cumulative completed count
    total_time_spent_mins: int = 0            # Cumulative time
    current_phase: str = "PLANNING"           # Current SDLC phase
    last_updated: datetime                    # When state changed
```

### 2.5 RoadmapPhase & Roadmap (Models)

Strategic plan structure.

```python
class RoadmapPhase(BaseModel):
    name: str                                 # Phase name (e.g., "Sprint 1")
    status: TaskStatus                        # Phase status
    progress: int = 0                         # Completion percentage (0-100)
    task_ids: List[str]                       # IDs of tasks in this phase

class Roadmap(BaseModel):
    version: int = 1                          # Schema version
    project_name: str                         # Project identifier
    phases: List[RoadmapPhase]                # All phases
    tasks: Dict[str, Task]                    # All tasks by ID
```

---

## 3. File System Layout

```
agency_os/
└── 00_system/
    └── task_management/
        ├── __init__.py                    (Exports: TaskManager, models)
        ├── models.py                      (Pydantic models)
        ├── file_lock.py                   (Atomic read/write functions)
        ├── validator_registry.py          (Plugin system + validators)
        ├── task_manager.py                (Core TaskManager class)
        └── next_task_generator.py         (Task selection logic)

.vibe/
├── config/
│   └── roadmap.yaml                       (Strategic plan - user-managed)
├── state/
│   └── active_mission.json                (Hot state - atomic writes)
└── history/
    └── mission_logs/
        ├── task_001_completed.md          (Archive: completed tasks)
        ├── task_002_completed.md
        └── ...

tests/
└── test_task_manager.py                   (Unit tests: 3 basic tests)
```

---

## 4. Manager Interface (Primary Methods)

### 4.1 Constructor

```python
TaskManager(vibe_root: Path)
```

Initializes the manager and ensures directories exist.

### 4.2 Read Operations

```python
def get_active_mission() -> ActiveMission
    """Load current mission state (with FileLock)"""
    
def get_current_task() -> Optional[Task]
    """Get the task agent should work on right now"""
    
def get_roadmap() -> Roadmap
    """Load strategic plan"""
```

### 4.3 Write Operations (Atomic)

```python
def start_task(task_id: str) -> Task
    """Start a new task (sets it as current)"""
    
def update_task_progress(time_spent_mins: int = 0, 
                        blocking_reason: Optional[str] = None) -> Task
    """Update current task progress"""
```

### 4.4 Validation

```python
def validate_current_task() -> Dict[str, Any]
    """Run all validation checks for current task"""
    # Returns: {"valid": bool, "checks": {...}, "failed": [...]}
```

### 4.5 Completion

```python
def complete_current_task() -> Optional[Task]
    """
    Complete current task (HARD VALIDATION).
    Raises RuntimeError if validation fails.
    Returns next task or None if project complete.
    """
```

### 4.6 Internal Methods

```python
def _save_mission(mission: ActiveMission)
    """Atomic write to state file"""
    
def _archive_task(task: Task)
    """Save completed task to logs"""
```

---

## 5. Validator Registry

Built-in validators available for tasks:

### 5.1 `tests_passing`

Validates that all tests in a scope pass.

```python
def validate_tests_passing(vibe_root: Path, scope: str = "tests/") -> bool
    """Run pytest in scope (e.g., 'tests/')"""
```

**Usage in Task:**
```python
ValidationCheck(
    id="check_tests",
    description="All unit tests pass",
    validator="tests_passing",
    params={"scope": "tests/"}
)
```

### 5.2 `git_clean`

Validates that the working directory has no uncommitted changes.

```python
def validate_git_clean(vibe_root: Path) -> bool
    """Check for uncommitted changes (git status --porcelain)"""
```

**Usage in Task:**
```python
ValidationCheck(
    id="check_git",
    description="Git working directory is clean",
    validator="git_clean"
)
```

### 5.3 `docs_updated`

Validates that specific files were modified in the last commit.

```python
def validate_docs_updated(vibe_root: Path, required_files: list) -> bool
    """Check if all required_files were modified in the last commit"""
```

**Usage in Task:**
```python
ValidationCheck(
    id="check_docs",
    description="Documentation updated",
    validator="docs_updated",
    params={"required_files": ["docs/README.md", "docs/API.md"]}
)
```

---

## 6. State Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     OPERATIONAL FLOW                         │
└─────────────────────────────────────────────────────────────┘

1. LOAD STATE
   ├─ Read .vibe/state/active_mission.json (FileLock: LOCK_SH)
   ├─ Deserialize into ActiveMission model
   └─ Extract current_task

2. EXECUTE WORK
   ├─ Agent works on task
   └─ Calls update_task_progress() as needed (atomic writes)

3. VALIDATE COMPLETION
   ├─ Call validate_current_task()
   ├─ Run all ValidationCheck validators in parallel
   ├─ Collect results and update task.validation_checks
   └─ Return validation summary

4. COMPLETE TASK
   ├─ If validation fails: Raise RuntimeError (hard stop)
   ├─ If validation passes:
   │  ├─ Mark task.status = DONE
   │  ├─ Write task to .vibe/history/mission_logs/{id}_completed.md
   │  ├─ Update mission stats
   │  └─ Generate next task (stub: linear search for TODO)
   │
   ├─ If next task exists:
   │  └─ Load it from roadmap and set as current_task
   │
   └─ If no next task:
      └─ Set current_task = None (project complete)

5. PERSIST STATE
   └─ Call _save_mission(mission) (FileLock: LOCK_EX on temp file)
```

---

## 7. Concurrency & Thread Safety

### 7.1 File Locking Strategy

- **Reads:** Shared lock (`LOCK_SH`) allows multiple concurrent readers
- **Writes:** Exclusive lock (`LOCK_EX`) ensures only one writer at a time
- **Atomicity:** Write to `.tmp` file, then atomic rename (POSIX filesystems)

### 7.2 Race Condition Prevention

| Scenario | Handling |
|----------|----------|
| Two agents read mission simultaneously | Shared lock; both proceed |
| One agent writes while another reads | Read waits for write to complete |
| Two agents try to write | Second write waits for first to complete |
| Power failure during write | Temp file abandoned; original intact |

---

## 8. Example: Complete Task Lifecycle

```python
from pathlib import Path
from agency_os.system.task_management import TaskManager, Task, TaskStatus, ValidationCheck
from datetime import datetime

vibe_root = Path("/path/to/vibe-agency")
manager = TaskManager(vibe_root)

# 1. LOAD ROADMAP (read strategic plan)
roadmap = manager.get_roadmap()
print(f"Project: {roadmap.project_name}")
print(f"Tasks: {len(roadmap.tasks)}")

# 2. START A TASK
task_id = list(roadmap.tasks.keys())[0]
current_task = manager.start_task(task_id)
print(f"Started: {current_task.name}")

# 3. UPDATE PROGRESS (simulate work)
manager.update_task_progress(time_spent_mins=30)

# 4. CHECK VALIDATION (are we done?)
validation = manager.validate_current_task()
print(f"Valid: {validation['valid']}")
print(f"Failed checks: {validation['failed']}")

# 5. COMPLETE TASK (if valid)
if validation['valid']:
    next_task = manager.complete_current_task()
    print(f"Completed! Next task: {next_task.name if next_task else 'Project complete'}")
else:
    print("Cannot complete: fix validation failures first")

# 6. VERIFY STATE (read new mission)
mission = manager.get_active_mission()
print(f"Tasks completed: {mission.total_tasks_completed}")
print(f"Current task: {mission.current_task.name if mission.current_task else 'None'}")
```

---

## 9. Phase 1 Constraints & Future Enhancements

### 9.1 Current (Phase 1) Limitations

- Task generator is a simple linear search for TODO tasks
- No dependency resolution (tasks are independent)
- No parallel task execution
- Validator parameters are limited to simple types

### 9.2 Future Enhancements (Phase 2+)

- Task prioritization and intelligent task selection
- Dependency graphs (task A blocks task B)
- Async/parallel validator execution
- Performance metrics and analytics
- Integration with external CI/CD systems
- Custom validator development framework

---

## 10. Adoption Checklist

- [x] All 7 code files created and tested
- [x] Pydantic models compatible with V1 and V2
- [x] File locking implemented with `fcntl` (Unix/Linux/MacOS)
- [x] Validator registry populated with 3 built-in validators
- [x] 3 unit tests cover: Persistence, Locking, Validation
- [x] Documentation complete and published
- [x] Ready for integration into STEWARD Governance Pillar

---

**Document Status:** APPROVED  
**Last Updated:** 2025-11-18  
**Next Review:** Upon GAD-702 (Governance Integration)
