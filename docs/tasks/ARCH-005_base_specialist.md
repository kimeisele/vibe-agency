# ARCH-005: Design BaseSpecialist Interface

**Phase:** 1 (Vertical Slice Extraction)
**Priority:** P0
**Estimated Time:** 120 minutes
**Dependencies:** ARCH-004

---

## Objective

Create the abstract base class for all specialist agents. This contract defines how specialists:
- Execute phase-specific work
- Persist state to SQLite
- Interact with tools safely
- Report progress and errors

---

## Acceptance Criteria

1. ✅ **Base Class Created**
   - `agency_os/agents/base_specialist.py` with abstract `BaseSpecialist` class

2. ✅ **Abstract Methods Defined**
   ```python
   class BaseSpecialist(ABC):
       @abstractmethod
       def execute(self, mission_context: MissionContext) -> SpecialistResult

       @abstractmethod
       def validate_preconditions(self, mission_context: MissionContext) -> bool

       @abstractmethod
       def get_required_tools(self) -> List[str]
   ```

3. ✅ **Concrete Shared Methods**
   - `persist_state()` - Save specialist state to SQLite
   - `load_state()` - Restore specialist state from SQLite
   - `log_decision()` - Record decision rationale to DB
   - `execute_tool()` - Safe tool execution with logging

4. ✅ **Lifecycle Hooks**
   ```python
   def on_start(self, mission_context: MissionContext) -> None
   def on_complete(self, result: SpecialistResult) -> None
   def on_error(self, error: Exception) -> None
   ```

5. ✅ **Integration with SQLite**
   - Uses `SQLiteStore` for all persistence
   - Automatically logs tool calls
   - Records decisions with rationale

6. ✅ **Documentation**
   - `docs/architecture/SPECIALIST_AGENT_CONTRACT.md` created
   - Explains: specialist responsibilities, lifecycle, state management
   - Examples of implementing a new specialist

---

## Design Principles

### 1. Separation of Concerns
- **Orchestrator:** Routes to correct specialist
- **Specialist:** Executes phase-specific logic
- **SQLiteStore:** Handles all persistence
- **ToolExecutor:** Handles tool safety/execution

### 2. Template Method Pattern
Base class provides structure, subclasses fill in details:

```python
def run(self, mission_context: MissionContext) -> SpecialistResult:
    """Template method - orchestrates specialist execution."""
    # 1. Validate preconditions
    if not self.validate_preconditions(mission_context):
        raise PreconditionError(f"{self.__class__.__name__} preconditions not met")

    # 2. Load previous state (if resuming)
    self.load_state(mission_context.mission_uuid)

    # 3. Execute lifecycle hook
    self.on_start(mission_context)

    try:
        # 4. Execute specialist logic (implemented by subclass)
        result = self.execute(mission_context)

        # 5. Persist final state
        self.persist_state(mission_context.mission_uuid)

        # 6. Completion hook
        self.on_complete(result)

        return result

    except Exception as e:
        # 7. Error handling hook
        self.on_error(e)
        raise
```

### 3. Dependency Injection
Specialists receive dependencies via constructor:

```python
class BaseSpecialist(ABC):
    def __init__(
        self,
        store: SQLiteStore,
        tool_executor: ToolExecutor,
        safety_guard: ToolSafetyGuard
    ):
        self.store = store
        self.tool_executor = tool_executor
        self.safety_guard = safety_guard
        self.state: Dict[str, Any] = {}
```

---

## Interface Design

### Data Structures

```python
from dataclasses import dataclass
from typing import Dict, Any, Optional, List
from enum import Enum

class SpecialistStatus(Enum):
    """Specialist execution status."""
    SUCCESS = "success"
    FAILURE = "failure"
    PARTIAL = "partial"  # Some work done, but not complete

@dataclass
class MissionContext:
    """Context provided to specialist by orchestrator."""
    mission_uuid: str
    phase: str
    playbook: Dict[str, Any]
    previous_phase_output: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = None

@dataclass
class SpecialistResult:
    """Result returned by specialist to orchestrator."""
    status: SpecialistStatus
    output: Dict[str, Any]
    next_phase: Optional[str] = None
    error_message: Optional[str] = None
    metrics: Dict[str, Any] = None  # Duration, tool calls, etc.
```

### Abstract Base Class

```python
from abc import ABC, abstractmethod
from typing import List, Dict, Any
from agency_os.persistence import SQLiteStore
from agency_os.tools import ToolExecutor, ToolSafetyGuard

class BaseSpecialist(ABC):
    """
    Abstract base class for all specialist agents.

    Specialists are phase-specific agents that execute a single SDLC phase
    (PLANNING, CODING, TESTING, DEPLOYMENT, MAINTENANCE). They:

    - Receive mission context from orchestrator
    - Execute phase-specific logic
    - Persist decisions to SQLite
    - Return results to orchestrator

    Subclasses must implement:
    - execute(): Phase-specific work
    - validate_preconditions(): Check if phase can run
    - get_required_tools(): Declare tool dependencies
    """

    def __init__(
        self,
        store: SQLiteStore,
        tool_executor: ToolExecutor,
        safety_guard: ToolSafetyGuard
    ):
        self.store = store
        self.tool_executor = tool_executor
        self.safety_guard = safety_guard
        self.state: Dict[str, Any] = {}

    # ========== TEMPLATE METHOD (public interface) ==========

    def run(self, mission_context: MissionContext) -> SpecialistResult:
        """
        Execute specialist work (template method).

        This method orchestrates the specialist lifecycle:
        1. Validate preconditions
        2. Load previous state
        3. Execute specialist logic (abstract method)
        4. Persist state
        5. Return result
        """
        # Implementation shown above

    # ========== ABSTRACT METHODS (must implement) ==========

    @abstractmethod
    def execute(self, mission_context: MissionContext) -> SpecialistResult:
        """
        Execute phase-specific work.

        This is the core logic of the specialist. Subclasses implement
        their phase-specific workflow here.

        Returns:
            SpecialistResult with status, output, and next phase
        """
        pass

    @abstractmethod
    def validate_preconditions(self, mission_context: MissionContext) -> bool:
        """
        Check if specialist can execute in current context.

        Example preconditions:
        - CodingSpecialist: Planning phase must be complete
        - DeploymentSpecialist: Testing phase must pass

        Returns:
            True if preconditions met, False otherwise
        """
        pass

    @abstractmethod
    def get_required_tools(self) -> List[str]:
        """
        Declare which tools this specialist needs.

        Used for:
        - Capability checking (can this specialist run here?)
        - Security (validate tool access against playbook)

        Returns:
            List of tool names (e.g., ["research", "code_generator"])
        """
        pass

    # ========== CONCRETE METHODS (provided by base class) ==========

    def persist_state(self, mission_uuid: str) -> None:
        """Save specialist state to SQLite."""
        # Implementation: Store self.state as JSON in agent_memory table
        pass

    def load_state(self, mission_uuid: str) -> None:
        """Restore specialist state from SQLite."""
        # Implementation: Load from agent_memory table into self.state
        pass

    def log_decision(
        self,
        mission_uuid: str,
        decision_type: str,
        rationale: str
    ) -> None:
        """Record a decision to the database."""
        self.store.record_decision(
            mission_uuid,
            decision_type,
            rationale,
            agent_name=self.__class__.__name__
        )

    def execute_tool(
        self,
        mission_uuid: str,
        tool_name: str,
        args: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute tool with safety checks and logging.

        1. Validates tool against safety guard
        2. Executes tool via tool_executor
        3. Logs result to SQLite
        4. Returns result
        """
        # Validate tool is allowed
        if not self.safety_guard.is_tool_allowed(tool_name, self.get_required_tools()):
            raise ToolNotAllowedError(f"{tool_name} not in allowed tools")

        # Execute tool
        start_time = time.time()
        try:
            result = self.tool_executor.execute(tool_name, args)
            duration_ms = int((time.time() - start_time) * 1000)

            # Log success
            self.store.log_tool_call(
                mission_uuid,
                tool_name,
                args,
                result,
                success=True,
                duration_ms=duration_ms
            )

            return result

        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)

            # Log failure
            self.store.log_tool_call(
                mission_uuid,
                tool_name,
                args,
                result=None,
                success=False,
                duration_ms=duration_ms,
                error_message=str(e)
            )

            raise

    # ========== LIFECYCLE HOOKS (optional override) ==========

    def on_start(self, mission_context: MissionContext) -> None:
        """Called before execute(). Override for setup logic."""
        pass

    def on_complete(self, result: SpecialistResult) -> None:
        """Called after successful execute(). Override for cleanup."""
        pass

    def on_error(self, error: Exception) -> None:
        """Called on execution failure. Override for error handling."""
        pass
```

---

## Example Subclass (Reference Implementation)

```python
class PlanningSpecialist(BaseSpecialist):
    """Specialist for PLANNING phase."""

    def validate_preconditions(self, mission_context: MissionContext) -> bool:
        """Planning has no preconditions (first phase)."""
        return True

    def get_required_tools(self) -> List[str]:
        """Planning needs research and analysis tools."""
        return ["research", "analyze_requirements", "generate_architecture"]

    def execute(self, mission_context: MissionContext) -> SpecialistResult:
        """Execute planning workflow."""
        # 1. Analyze requirements
        requirements = self.execute_tool(
            mission_context.mission_uuid,
            "analyze_requirements",
            {"input": mission_context.playbook.get("user_input")}
        )

        self.log_decision(
            mission_context.mission_uuid,
            "requirements_analysis",
            f"Identified {len(requirements['features'])} features"
        )

        # 2. Generate architecture
        architecture = self.execute_tool(
            mission_context.mission_uuid,
            "generate_architecture",
            {"requirements": requirements}
        )

        # 3. Return result
        return SpecialistResult(
            status=SpecialistStatus.SUCCESS,
            output={
                "requirements": requirements,
                "architecture": architecture
            },
            next_phase="CODING"
        )
```

---

## Deliverables

1. **agency_os/agents/__init__.py**
   ```python
   from .base_specialist import BaseSpecialist, MissionContext, SpecialistResult, SpecialistStatus

   __all__ = ["BaseSpecialist", "MissionContext", "SpecialistResult", "SpecialistStatus"]
   ```

2. **agency_os/agents/base_specialist.py**
   - Complete implementation (250-300 LOC)
   - Full docstrings
   - Type hints

3. **docs/architecture/SPECIALIST_AGENT_CONTRACT.md**
   - Explains specialist pattern
   - Lifecycle diagram
   - How to implement new specialists
   - Best practices

---

## Validation

```bash
# Verify abstract class structure
python3 -c "
from agency_os.agents import BaseSpecialist
import inspect
print('Abstract methods:', [m for m in dir(BaseSpecialist) if getattr(getattr(BaseSpecialist, m), '__isabstractmethod__', False)])
"

# Expected output: ['execute', 'get_required_tools', 'validate_preconditions']
```

---

## Next Steps

→ **ARCH-006:** Implement PlanningSpecialist using this contract
→ **ARCH-007:** Prove specialist pattern with end-to-end test
