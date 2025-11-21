"""
Tests for SpecialistAgent adapter (ARCH-026)

Verifies that SpecialistAgent correctly wraps BaseSpecialist to work
with VibeKernel dispatch mechanism.
"""

from unittest.mock import Mock

import pytest

from vibe_core.agent_protocol import VibeAgent
from vibe_core.agents.specialist_agent import SpecialistAgent
from vibe_core.scheduling import Task
from vibe_core.specialists.base_specialist import BaseSpecialist, MissionContext, SpecialistResult

# ============================================================================
# MOCK SPECIALIST
# ============================================================================


class MockSpecialist(BaseSpecialist):
    """Mock specialist for testing SpecialistAgent adapter"""

    def __init__(self, role: str, mission_id: int, sqlite_store, tool_safety_guard):
        super().__init__(role, mission_id, sqlite_store, tool_safety_guard)
        self.execute_called = False
        self.validate_called = False
        self.on_start_called = False
        self.on_complete_called = False
        self.on_error_called = False
        self.should_fail_preconditions = False
        self.should_fail_execution = False

    def execute(self, context: MissionContext) -> SpecialistResult:
        """Execute mock workflow"""
        self.execute_called = True

        if self.should_fail_execution:
            raise RuntimeError("Mock execution failure")

        return SpecialistResult(
            success=True,
            next_phase="NEXT_PHASE",
            artifacts=["artifact1.txt", "artifact2.txt"],
            decisions=[
                {"type": "DECISION_1", "rationale": "Because reasons"},
                {"type": "DECISION_2", "rationale": "More reasons"},
            ],
        )

    def validate_preconditions(self, context: MissionContext) -> bool:
        """Validate mock preconditions"""
        self.validate_called = True
        return not self.should_fail_preconditions

    def on_start(self, context: MissionContext) -> None:
        """Hook called before execution"""
        self.on_start_called = True
        super().on_start(context)

    def on_complete(self, context: MissionContext, result: SpecialistResult) -> None:
        """Hook called after successful execution"""
        self.on_complete_called = True
        super().on_complete(context, result)

    def on_error(self, context: MissionContext, error: Exception) -> SpecialistResult:
        """Hook called on execution failure"""
        self.on_error_called = True
        return super().on_error(context, error)


# ============================================================================
# FIXTURES
# ============================================================================


@pytest.fixture
def mock_store():
    """Create mock SQLiteStore"""
    store = Mock()
    store.get_decisions_for_mission = Mock(return_value=[])
    store.record_decision = Mock()
    return store


@pytest.fixture
def mock_guard():
    """Create mock ToolSafetyGuard"""
    return Mock()


@pytest.fixture
def mock_specialist(mock_store, mock_guard):
    """Create MockSpecialist instance"""
    return MockSpecialist(
        role="PLANNING", mission_id=1, sqlite_store=mock_store, tool_safety_guard=mock_guard
    )


@pytest.fixture
def specialist_agent(mock_specialist):
    """Create SpecialistAgent wrapping MockSpecialist"""
    return SpecialistAgent(mock_specialist)


@pytest.fixture
def valid_task():
    """Create valid task payload for specialist"""
    return Task(
        agent_id="specialist-planning",
        payload={
            "mission_id": 1,
            "mission_uuid": "test-uuid-123",
            "phase": "PLANNING",
            "project_root": "/tmp/test-project",
            "metadata": {"key": "value"},
        },
    )


# ============================================================================
# TESTS: INITIALIZATION
# ============================================================================


def test_specialist_agent_implements_vibe_agent(specialist_agent):
    """SpecialistAgent should implement VibeAgent protocol"""
    assert isinstance(specialist_agent, VibeAgent)


def test_specialist_agent_wraps_specialist(mock_specialist):
    """SpecialistAgent should wrap BaseSpecialist instance"""
    agent = SpecialistAgent(mock_specialist)
    assert agent.specialist is mock_specialist


def test_specialist_agent_rejects_non_specialist():
    """SpecialistAgent should reject non-BaseSpecialist instances"""
    with pytest.raises(TypeError, match="must be a BaseSpecialist instance"):
        SpecialistAgent("not a specialist")


def test_agent_id_format(mock_specialist):
    """agent_id should follow format: specialist-{role}"""
    agent = SpecialistAgent(mock_specialist)
    assert agent.agent_id == "specialist-planning"


def test_agent_id_lowercase(mock_store, mock_guard):
    """agent_id should be lowercase even if role is uppercase"""
    specialist = MockSpecialist("CODING", 1, mock_store, mock_guard)
    agent = SpecialistAgent(specialist)
    assert agent.agent_id == "specialist-coding"


# ============================================================================
# TESTS: TASK PROCESSING (SUCCESS PATH)
# ============================================================================


def test_process_converts_task_to_context(specialist_agent, valid_task, mock_specialist):
    """process() should convert Task payload to MissionContext"""
    result = specialist_agent.process(valid_task)

    # Verify execute was called (context was valid)
    assert mock_specialist.execute_called
    assert result["success"] is True


def test_process_validates_preconditions(specialist_agent, valid_task, mock_specialist):
    """process() should validate preconditions before execution"""
    specialist_agent.process(valid_task)

    assert mock_specialist.validate_called


def test_process_calls_lifecycle_hooks(specialist_agent, valid_task, mock_specialist):
    """process() should call on_start, execute, on_complete"""
    _ = specialist_agent.process(valid_task)  # result not used, only hooks checked

    assert mock_specialist.on_start_called
    assert mock_specialist.execute_called
    assert mock_specialist.on_complete_called
    assert not mock_specialist.on_error_called  # No error occurred


def test_process_returns_specialist_result(specialist_agent, valid_task):
    """process() should return dict with SpecialistResult fields"""
    result = specialist_agent.process(valid_task)

    assert result["success"] is True
    assert result["next_phase"] == "NEXT_PHASE"
    assert result["artifacts"] == ["artifact1.txt", "artifact2.txt"]
    assert len(result["decisions"]) == 2
    assert result["error"] is None
    assert result["specialist"] == "MockSpecialist"
    assert result["role"] == "PLANNING"


def test_process_with_minimal_payload(specialist_agent, mock_specialist):
    """process() should handle minimal payload (optional fields)"""
    task = Task(
        agent_id="specialist-planning",
        payload={
            "mission_id": 1,
            "mission_uuid": "uuid-123",
            "phase": "PLANNING",
            # project_root and metadata are optional
        },
    )

    result = specialist_agent.process(task)

    assert result["success"] is True
    assert mock_specialist.execute_called


# ============================================================================
# TESTS: ERROR HANDLING
# ============================================================================


def test_process_fails_if_preconditions_not_met(specialist_agent, valid_task, mock_specialist):
    """process() should return error result if preconditions fail"""
    mock_specialist.should_fail_preconditions = True

    result = specialist_agent.process(valid_task)

    assert result["success"] is False
    assert result["error"] is not None
    assert "Preconditions not met" in result["error"]
    assert not mock_specialist.execute_called  # Should not execute
    assert not mock_specialist.on_complete_called
    # Result verified, no unused variables


def test_process_handles_execution_failure(specialist_agent, valid_task, mock_specialist):
    """process() should call on_error and re-raise exception if execution fails"""
    mock_specialist.should_fail_execution = True

    with pytest.raises(RuntimeError, match="Mock execution failure"):
        specialist_agent.process(valid_task)

    assert mock_specialist.on_error_called
    assert not mock_specialist.on_complete_called


def test_process_rejects_missing_mission_id(specialist_agent):
    """process() should raise ValueError if mission_id missing"""
    task = Task(
        agent_id="specialist-planning",
        payload={
            # mission_id missing
            "mission_uuid": "uuid-123",
            "phase": "PLANNING",
        },
    )

    with pytest.raises(ValueError, match="missing required field"):
        specialist_agent.process(task)


def test_process_rejects_missing_phase(specialist_agent):
    """process() should raise ValueError if phase missing"""
    task = Task(
        agent_id="specialist-planning",
        payload={
            "mission_id": 1,
            "mission_uuid": "uuid-123",
            # phase missing
        },
    )

    with pytest.raises(ValueError, match="missing required field"):
        specialist_agent.process(task)


def test_process_rejects_non_dict_payload(specialist_agent):
    """process() should raise TypeError if payload is not a dict"""
    task = Task(agent_id="specialist-planning", payload="not a dict")

    with pytest.raises(TypeError, match="Task payload must be a dict"):
        specialist_agent.process(task)


# ============================================================================
# TESTS: INTEGRATION WITH KERNEL
# ============================================================================


def test_specialist_agent_registers_with_kernel(specialist_agent):
    """SpecialistAgent should register with kernel successfully"""
    from vibe_core.kernel import VibeKernel

    kernel = VibeKernel(ledger_path=":memory:")
    kernel.register_agent(specialist_agent)

    status = kernel.get_status()
    assert "specialist-planning" in status["agent_ids"]


def test_specialist_agent_dispatch_via_kernel(specialist_agent, valid_task, mock_specialist):
    """Kernel should successfully dispatch task to SpecialistAgent"""
    from vibe_core.kernel import VibeKernel

    kernel = VibeKernel(ledger_path=":memory:")
    kernel.boot()
    kernel.register_agent(specialist_agent)

    # Submit task
    _ = kernel.submit(valid_task)  # task_id not used in assertions

    # Execute via kernel tick
    busy = kernel.tick()

    assert busy is True  # Work was done
    assert mock_specialist.execute_called  # Specialist executed
    assert mock_specialist.on_start_called
    assert mock_specialist.on_complete_called


def test_kernel_records_specialist_execution_in_ledger(specialist_agent, valid_task):
    """Kernel should record specialist execution in ledger"""
    from vibe_core.kernel import VibeKernel

    kernel = VibeKernel(ledger_path=":memory:")
    kernel.boot()
    kernel.register_agent(specialist_agent)

    # Submit and execute
    _ = kernel.submit(valid_task)  # task_id not used in assertions
    kernel.tick()

    # Query ledger
    executions = kernel.ledger.get_history(limit=10)

    assert len(executions) == 1
    execution = executions[0]
    assert execution["status"] == "COMPLETED"
    assert execution["agent_id"] == "specialist-planning"
    assert execution["output_result"]["success"] is True


def test_kernel_records_specialist_failure_in_ledger(specialist_agent, valid_task, mock_specialist):
    """Kernel should record specialist failure in ledger"""
    from vibe_core.kernel import VibeKernel

    kernel = VibeKernel(ledger_path=":memory:")
    kernel.boot()
    kernel.register_agent(specialist_agent)

    # Configure specialist to fail
    mock_specialist.should_fail_execution = True

    # Submit and execute
    _ = kernel.submit(valid_task)  # task_id not used in assertions

    try:
        kernel.tick()
    except RuntimeError:
        pass  # Expected

    # Query ledger
    executions = kernel.ledger.get_history(limit=10)

    assert len(executions) == 1
    execution = executions[0]
    assert execution["status"] == "FAILED"
    assert "Mock execution failure" in execution["error_message"]


# ============================================================================
# TESTS: REPR
# ============================================================================


def test_specialist_agent_repr(specialist_agent):
    """__repr__ should include agent_id and specialist class"""
    repr_str = repr(specialist_agent)
    assert "SpecialistAgent" in repr_str
    assert "specialist-planning" in repr_str
    assert "MockSpecialist" in repr_str
