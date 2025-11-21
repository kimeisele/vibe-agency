# Specialist Agent Contract (ARCH-005)

**Status:** ✅ COMPLETE (Phase 2.5 - ARCH-005)
**Version:** 1.1
**Last Updated:** 2025-11-21 (imports fixed for post-split architecture)

---

## Table of Contents

1. [Overview](#overview)
2. [The HAP Pattern](#the-hap-pattern)
3. [Contract Requirements](#contract-requirements)
4. [Implementation Guide](#implementation-guide)
5. [Example: PlanningSpecialist](#example-planningspecialist)
6. [Testing Your Specialist](#testing-your-specialist)
7. [Best Practices](#best-practices)

---

## Overview

The **BaseSpecialist** is the abstract base class for all specialist agents in the **Hierarchical Agent Pattern (HAP)**. This document defines the contract that all specialists must implement.

### What is a Specialist?

A specialist is a phase-specific agent that handles ONE SDLC phase:

| Specialist            | Phase          | Responsibility                                |
|-----------------------|----------------|-----------------------------------------------|
| PlanningSpecialist    | PLANNING       | Requirements analysis, architecture design    |
| CodingSpecialist      | CODING         | Code generation, refactoring                  |
| TestingSpecialist     | TESTING        | Test creation, validation                     |
| DeploymentSpecialist  | DEPLOYMENT     | CI/CD, infrastructure provisioning            |
| MaintenanceSpecialist | MAINTENANCE    | Bug fixes, monitoring, updates                |

### Why Specialists?

**Before (Monolithic Orchestrator):**
```
Orchestrator (500+ LOC) → Handles all 5 phases inline
  ├─ PLANNING logic (100 LOC)
  ├─ CODING logic (150 LOC)
  ├─ TESTING logic (80 LOC)
  └─ ... (tight coupling, hard to test)
```

**After (HAP):**
```
Orchestrator (<200 LOC) → Pure routing logic
  ├─ PlanningSpecialist (autonomous, testable)
  ├─ CodingSpecialist (autonomous, testable)
  ├─ TestingSpecialist (autonomous, testable)
  └─ ... (loose coupling, easy to test)
```

---

## The HAP Pattern

**HAP (Hierarchical Agent Pattern)** aligns with the **4D Hypercube** architecture:

| Dimension   | HAP Integration                                              |
|-------------|--------------------------------------------------------------|
| **GAD**     | Specialists implement specific pillar capabilities          |
| **LAD**     | Specialists adapt behavior based on infrastructure layer     |
| **VAD**     | Specialists validate preconditions/postconditions            |
| **PAD**     | Specialists follow playbook-driven workflow choreography     |

### Lifecycle Flow

```
1. Orchestrator detects phase → selects specialist
2. Specialist.load_state() → crash recovery
3. Specialist.validate_preconditions() → fail fast
4. Specialist.on_start() → setup hook
5. Specialist.execute() → main workflow
6. Specialist.persist_state() → save decisions
7. Specialist.on_complete() → cleanup hook
   OR
   Specialist.on_error() → error recovery
```

---

## Contract Requirements

All specialists MUST implement the following interface:

### 1. Constructor Signature

```python
def __init__(
    self,
    role: str,
    mission_id: int,
    sqlite_store: SQLiteStore,
    tool_safety_guard: ToolSafetyGuard,
    playbook_root: Path | None = None,
)
```

**Parameters:**
- `role` (str): Specialist role (e.g., "PLANNING", "CODING") - REQUIRED
- `mission_id` (int): Database primary key for current mission - REQUIRED
- `sqlite_store` (SQLiteStore): Persistence layer - REQUIRED
- `tool_safety_guard` (ToolSafetyGuard): Tool safety enforcement - REQUIRED
- `playbook_root` (Path): Playbook directory (auto-detected if None)

**Why explicit dependencies?**
- **Testability**: Easy to mock SQLiteStore/ToolSafetyGuard in tests
- **Clarity**: No hidden global state or singletons
- **Fail Fast**: ValueError raised if dependencies missing

### 2. Abstract Methods (MUST IMPLEMENT)

#### `execute(context: MissionContext) -> SpecialistResult`

Main workflow logic. Called by orchestrator to execute the phase.

```python
@abstractmethod
def execute(self, context: MissionContext) -> SpecialistResult:
    """
    Execute the specialist's phase-specific workflow.

    Args:
        context: Mission context (mission_id, phase, metadata)

    Returns:
        SpecialistResult with success status and next phase
    """
    raise NotImplementedError
```

**Workflow:**
1. Load playbook for current phase
2. Execute workflow steps (call tools, make decisions)
3. Log decisions to SQLite via `_log_decision()`
4. Generate artifacts (code, docs, configs)
5. Return result with success status

#### `validate_preconditions(context: MissionContext) -> bool`

Validate that preconditions are met before execution.

```python
@abstractmethod
def validate_preconditions(self, context: MissionContext) -> bool:
    """
    Validate preconditions before execution.

    Returns:
        True if preconditions met, False otherwise
    """
    raise NotImplementedError
```

**Check:**
- Required files exist
- Dependencies are installed
- Previous phase completed successfully
- Budget constraints are satisfied

### 3. Lifecycle Hooks (OPTIONAL OVERRIDE)

#### `on_start(context: MissionContext) -> None`

Hook called before `execute()` begins. Use for:
- Logging start event
- Initializing resources
- Recording start timestamp

#### `on_complete(context: MissionContext, result: SpecialistResult) -> None`

Hook called after successful `execute()`. Use for:
- Logging completion event
- Cleaning up resources
- Persisting final state

#### `on_error(context: MissionContext, error: Exception) -> SpecialistResult`

Hook called when `execute()` raises exception. Use for:
- Logging error details
- Persisting partial state for recovery
- Returning error result

### 4. Persistence Methods (DEFAULT PROVIDED)

#### `persist_state() -> None`

Save specialist state to SQLite. Default implementation stores `self.state` dict.

#### `load_state() -> dict[str, Any]`

Load specialist state from SQLite (crash recovery). Default implementation loads most recent checkpoint.

---

## Implementation Guide

### Step 1: Create Specialist Class

```python
from vibe_core.specialists import BaseSpecialist, MissionContext, SpecialistResult

class PlanningSpecialist(BaseSpecialist):
    """
    Specialist for PLANNING phase.

    Responsibilities:
        - Requirement analysis
        - Architecture design
        - Task breakdown
    """

    def __init__(
        self,
        mission_id: int,
        sqlite_store: SQLiteStore,
        tool_safety_guard: ToolSafetyGuard,
    ):
        # Call parent constructor with role="PLANNING"
        super().__init__(
            role="PLANNING",
            mission_id=mission_id,
            sqlite_store=sqlite_store,
            tool_safety_guard=tool_safety_guard,
        )
```

### Step 2: Implement `validate_preconditions()`

```python
def validate_preconditions(self, context: MissionContext) -> bool:
    """Validate PLANNING phase preconditions"""

    # Check: project manifest exists
    manifest_path = context.project_root / "project_manifest.json"
    if not manifest_path.exists():
        logger.error(f"Precondition failed: project_manifest.json not found")
        return False

    # Check: not already in CODING phase
    mission = self.get_mission_data()
    if mission["phase"] != "PLANNING":
        logger.error(f"Precondition failed: already in {mission['phase']} phase")
        return False

    # All checks passed
    return True
```

### Step 3: Implement `execute()`

```python
def execute(self, context: MissionContext) -> SpecialistResult:
    """Execute PLANNING workflow"""

    # Step 1: Load playbook
    playbook = self._load_playbook("planning.yaml")

    # Step 2: Execute workflow steps
    self._log_decision(
        decision_type="PLANNING_STARTED",
        rationale="Beginning requirements analysis",
        data={"phase": "PLANNING"},
    )

    # Example: Generate architecture document
    architecture = self._generate_architecture(context)

    # Step 3: Generate artifacts
    artifact_path = context.project_root / "artifacts/planning/architecture.json"
    artifact_path.parent.mkdir(parents=True, exist_ok=True)

    with open(artifact_path, "w") as f:
        json.dump(architecture, f, indent=2)

    # Step 4: Log decision
    self._log_decision(
        decision_type="ARCHITECTURE_GENERATED",
        rationale="Created system architecture",
        data={"artifact": str(artifact_path)},
    )

    # Step 5: Return result
    return SpecialistResult(
        success=True,
        next_phase="CODING",
        artifacts=[str(artifact_path)],
        decisions=[{"type": "ARCHITECTURE_GENERATED"}],
    )
```

### Step 4: Add Helper Methods (Optional)

```python
def _generate_architecture(self, context: MissionContext) -> dict:
    """Generate system architecture"""

    # Load requirements from manifest
    manifest_path = context.project_root / "project_manifest.json"
    with open(manifest_path) as f:
        manifest = json.load(f)

    # Generate architecture based on requirements
    architecture = {
        "components": ["frontend", "backend", "database"],
        "tech_stack": {"frontend": "React", "backend": "FastAPI"},
        "generated_at": datetime.utcnow().isoformat() + "Z",
    }

    return architecture
```

---

## Example: PlanningSpecialist

Complete implementation example:

```python
#!/usr/bin/env python3
"""
PlanningSpecialist - ARCH-006
Handles PLANNING phase workflow
"""

import json
import logging
from datetime import datetime
from pathlib import Path

from vibe_core.specialists import BaseSpecialist, MissionContext, SpecialistResult
from vibe_core.runtime.tool_safety_guard import ToolSafetyGuard
from vibe_core.store.sqlite_store import SQLiteStore

logger = logging.getLogger(__name__)


class PlanningSpecialist(BaseSpecialist):
    """
    Specialist for PLANNING phase.

    Workflow:
        1. Validate preconditions (manifest exists, phase is PLANNING)
        2. Load planning playbook
        3. Analyze requirements
        4. Generate architecture
        5. Create task breakdown
        6. Return artifacts
    """

    def __init__(
        self,
        mission_id: int,
        sqlite_store: SQLiteStore,
        tool_safety_guard: ToolSafetyGuard,
    ):
        super().__init__(
            role="PLANNING",
            mission_id=mission_id,
            sqlite_store=sqlite_store,
            tool_safety_guard=tool_safety_guard,
        )

    def validate_preconditions(self, context: MissionContext) -> bool:
        """Validate PLANNING phase can execute"""

        # Check: project manifest exists
        manifest_path = context.project_root / "project_manifest.json"
        if not manifest_path.exists():
            logger.error("Precondition failed: project_manifest.json not found")
            return False

        # Check: phase is PLANNING
        mission = self.get_mission_data()
        if mission["phase"] != "PLANNING":
            logger.error(f"Precondition failed: current phase is {mission['phase']}")
            return False

        return True

    def execute(self, context: MissionContext) -> SpecialistResult:
        """Execute PLANNING workflow"""

        logger.info(f"PlanningSpecialist: Starting execution (mission_id={self.mission_id})")

        # Load playbook
        playbook = self._load_playbook("planning.yaml")

        # Generate architecture
        architecture = self._generate_architecture(context)

        # Save artifact
        artifact_path = context.project_root / "artifacts/planning/architecture.json"
        artifact_path.parent.mkdir(parents=True, exist_ok=True)

        with open(artifact_path, "w") as f:
            json.dump(architecture, f, indent=2)

        # Log decision
        self._log_decision(
            decision_type="ARCHITECTURE_GENERATED",
            rationale="Created system architecture based on requirements",
            data={"artifact": str(artifact_path), "components": len(architecture["components"])},
        )

        # Return success
        return SpecialistResult(
            success=True,
            next_phase="CODING",
            artifacts=[str(artifact_path)],
            decisions=[{"type": "ARCHITECTURE_GENERATED"}],
        )

    def _generate_architecture(self, context: MissionContext) -> dict:
        """Generate system architecture from requirements"""

        # Load manifest
        manifest_path = context.project_root / "project_manifest.json"
        with open(manifest_path) as f:
            manifest = json.load(f)

        # Extract requirements
        description = manifest.get("metadata", {}).get("description", "")

        # Generate architecture (simplified)
        architecture = {
            "name": manifest.get("metadata", {}).get("name", "unnamed-project"),
            "description": description,
            "components": ["frontend", "backend", "database"],
            "tech_stack": {
                "frontend": "React",
                "backend": "FastAPI",
                "database": "PostgreSQL",
            },
            "generated_at": datetime.utcnow().isoformat() + "Z",
        }

        return architecture
```

---

## Testing Your Specialist

### Unit Test Template

```python
import pytest
from pathlib import Path
from vibe_core.specialists import MissionContext
from vibe_core.runtime.tool_safety_guard import ToolSafetyGuard
from vibe_core.store.sqlite_store import SQLiteStore
from agency_os.agents.planning_specialist import PlanningSpecialist


def test_planning_specialist_validates_preconditions(tmp_path):
    """Test that PlanningSpecialist validates preconditions"""

    # Setup
    store = SQLiteStore(":memory:")
    guard = ToolSafetyGuard()

    # Create mission in PLANNING phase
    mission_id = store.create_mission(
        mission_uuid="test-001",
        phase="PLANNING",
        status="in_progress",
    )

    specialist = PlanningSpecialist(mission_id, store, guard)

    # Create context
    context = MissionContext(
        mission_id=mission_id,
        mission_uuid="test-001",
        phase="PLANNING",
        project_root=tmp_path,
        metadata={},
    )

    # Create manifest
    manifest_path = tmp_path / "project_manifest.json"
    manifest_path.write_text('{"metadata": {"name": "test-project"}}')

    # Test: preconditions should pass
    assert specialist.validate_preconditions(context) is True


def test_planning_specialist_executes_workflow(tmp_path):
    """Test that PlanningSpecialist executes successfully"""

    # Setup
    store = SQLiteStore(":memory:")
    guard = ToolSafetyGuard()

    mission_id = store.create_mission(
        mission_uuid="test-001",
        phase="PLANNING",
        status="in_progress",
    )

    specialist = PlanningSpecialist(mission_id, store, guard)

    context = MissionContext(
        mission_id=mission_id,
        mission_uuid="test-001",
        phase="PLANNING",
        project_root=tmp_path,
        metadata={},
    )

    # Create manifest
    manifest_path = tmp_path / "project_manifest.json"
    manifest_path.write_text('{"metadata": {"name": "test-project"}}')

    # Execute
    result = specialist.execute(context)

    # Assert
    assert result.success is True
    assert result.next_phase == "CODING"
    assert len(result.artifacts) > 0
```

---

## Best Practices

### 1. Fail Fast with Preconditions

Always validate preconditions BEFORE executing:

```python
if not specialist.validate_preconditions(context):
    return SpecialistResult(success=False, error="Preconditions not met")

result = specialist.execute(context)
```

### 2. Log ALL Decisions

Every significant decision should be logged:

```python
self._log_decision(
    decision_type="TOOL_SELECTED",
    rationale="Chose FastAPI for performance requirements",
    data={"tool": "FastAPI", "alternatives": ["Django", "Flask"]},
)
```

### 3. Use Tool Safety Guard

Always validate tool calls through the guard:

```python
# Before executing dangerous operation
allowed, violation = self.tool_safety_guard.check_action(
    "edit_file",
    {"path": "src/main.py"},
)

if not allowed:
    raise ToolSafetyGuardError(violation.message)
```

### 4. Make State Minimal and Serializable

Only store what's needed for crash recovery:

```python
self.state = {
    "current_step": "architecture_generation",
    "artifacts_created": ["architecture.json"],
    "last_checkpoint": datetime.utcnow().isoformat() + "Z",
}
```

### 5. Return Detailed Results

Provide rich results for orchestrator to act on:

```python
return SpecialistResult(
    success=True,
    next_phase="CODING",
    artifacts=["architecture.json", "tasks.json"],
    decisions=[
        {"type": "ARCHITECTURE_GENERATED", "components": 5},
        {"type": "TASKS_CREATED", "count": 12},
    ],
)
```

---

## FAQ

**Q: Can I call another specialist from my specialist?**
A: No. Specialists are independent. Use the orchestrator to coordinate phase transitions.

**Q: What if my specialist needs to run for hours?**
A: Use `persist_state()` periodically to checkpoint progress. Enable crash recovery via `load_state()`.

**Q: Can I use async/await in execute()?**
A: Yes, but ensure your playbook executor supports async workflows.

**Q: How do I test specialist in isolation?**
A: Use in-memory SQLite (`:memory:`) and mock ToolSafetyGuard.

---

**Next Steps:**
- Read the roadmap: `docs/roadmap/phase_2_5_foundation.json`
- See ARCH-006 for PlanningSpecialist implementation
- Check `tests/agents/` for test examples

---

**Version History:**
- v1.0 (2025-11-20): Initial release (ARCH-005)
