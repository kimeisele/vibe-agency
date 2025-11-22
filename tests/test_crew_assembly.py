#!/usr/bin/env python3
"""
Tests for ARCH-036: Crew Assembly

Verifies that Specialists are correctly registered in the kernel at boot time
via the SpecialistFactoryAgent pattern.
"""

import pytest
import tempfile
from pathlib import Path

from apps.agency.specialists import CodingSpecialist, PlanningSpecialist, TestingSpecialist
from vibe_core.agents.specialist_factory import SpecialistFactoryAgent
from vibe_core.kernel import VibeKernel
from vibe_core.runtime.tool_safety_guard import ToolSafetyGuard
from vibe_core.scheduling import Task


@pytest.fixture
def temp_ledger():
    """Create temporary ledger for testing"""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        ledger_path = f.name
    yield ledger_path
    Path(ledger_path).unlink(missing_ok=True)


@pytest.fixture
def kernel(temp_ledger):
    """Boot kernel with specialist factories"""
    kernel = VibeKernel(ledger_path=temp_ledger)
    kernel.boot()

    # Register specialist factories
    guard = ToolSafetyGuard()

    planning_factory = SpecialistFactoryAgent(
        specialist_class=PlanningSpecialist,
        role="planning",
        sqlite_store=kernel.ledger,
        tool_safety_guard=guard,
    )
    kernel.register_agent(planning_factory)

    coding_factory = SpecialistFactoryAgent(
        specialist_class=CodingSpecialist,
        role="coding",
        sqlite_store=kernel.ledger,
        tool_safety_guard=guard,
    )
    kernel.register_agent(coding_factory)

    testing_factory = SpecialistFactoryAgent(
        specialist_class=TestingSpecialist,
        role="testing",
        sqlite_store=kernel.ledger,
        tool_safety_guard=guard,
    )
    kernel.register_agent(testing_factory)

    return kernel


class TestCrewAssembly:
    """Tests for specialist registration (ARCH-036)"""

    def test_specialists_registered_at_boot(self, kernel):
        """Verify all specialists are registered in kernel"""
        # Check that factories are registered
        assert "specialist-planning" in kernel.agent_registry
        assert "specialist-coding" in kernel.agent_registry
        assert "specialist-testing" in kernel.agent_registry

    def test_specialist_factory_agent_ids(self, kernel):
        """Verify factory agent IDs follow naming convention"""
        planning_agent = kernel.agent_registry["specialist-planning"]
        assert planning_agent.agent_id == "specialist-planning"

        coding_agent = kernel.agent_registry["specialist-coding"]
        assert coding_agent.agent_id == "specialist-coding"

        testing_agent = kernel.agent_registry["specialist-testing"]
        assert testing_agent.agent_id == "specialist-testing"

    def test_specialist_factory_types(self, kernel):
        """Verify factories have correct specialist classes"""
        planning_agent = kernel.agent_registry["specialist-planning"]
        assert planning_agent.specialist_class == PlanningSpecialist

        coding_agent = kernel.agent_registry["specialist-coding"]
        assert coding_agent.specialist_class == CodingSpecialist

        testing_agent = kernel.agent_registry["specialist-testing"]
        assert testing_agent.specialist_class == TestingSpecialist

    def test_specialist_factory_roles(self, kernel):
        """Verify factories have correct roles"""
        planning_agent = kernel.agent_registry["specialist-planning"]
        assert planning_agent.role == "planning"

        coding_agent = kernel.agent_registry["specialist-coding"]
        assert coding_agent.role == "coding"

        testing_agent = kernel.agent_registry["specialist-testing"]
        assert testing_agent.role == "testing"

    def test_kernel_agent_count(self, kernel):
        """Verify kernel has exactly 3 specialists registered"""
        # Should have 3 specialist factories
        assert len(kernel.agent_registry) == 3

    def test_specialist_factory_repr(self, kernel):
        """Verify factory __repr__ for debugging"""
        planning_agent = kernel.agent_registry["specialist-planning"]
        repr_str = repr(planning_agent)

        assert "specialist-planning" in repr_str
        assert "PlanningSpecialist" in repr_str


class TestSpecialistFactoryAgent:
    """Tests for SpecialistFactoryAgent class"""

    def test_factory_creation(self):
        """Verify factory agent can be created"""
        guard = ToolSafetyGuard()
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            ledger_path = f.name

        try:
            kernel = VibeKernel(ledger_path=ledger_path)
            kernel.boot()

            factory = SpecialistFactoryAgent(
                specialist_class=PlanningSpecialist,
                role="planning",
                sqlite_store=kernel.ledger,
                tool_safety_guard=guard,
            )

            assert factory.agent_id == "specialist-planning"
            assert factory.specialist_class == PlanningSpecialist
            assert factory.role == "planning"

        finally:
            Path(ledger_path).unlink(missing_ok=True)

    def test_factory_requires_base_specialist_subclass(self):
        """Verify factory rejects non-BaseSpecialist classes"""
        guard = ToolSafetyGuard()
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            ledger_path = f.name

        try:
            kernel = VibeKernel(ledger_path=ledger_path)
            kernel.boot()

            class NotASpecialist:
                pass

            with pytest.raises(TypeError, match="must be a BaseSpecialist subclass"):
                SpecialistFactoryAgent(
                    specialist_class=NotASpecialist,
                    role="invalid",
                    sqlite_store=kernel.ledger,
                    tool_safety_guard=guard,
                )

        finally:
            Path(ledger_path).unlink(missing_ok=True)

    def test_factory_process_requires_mission_id(self, kernel):
        """Verify factory.process() fails if mission_id missing from payload"""
        planning_agent = kernel.agent_registry["specialist-planning"]

        # Create task without mission_id
        task = Task(agent_id="specialist-planning", payload={})

        # Should raise ValueError due to missing mission_id
        with pytest.raises(ValueError, match="missing required field 'mission_id'"):
            planning_agent.process(task)

    def test_factory_process_requires_dict_payload(self, kernel):
        """Verify factory.process() fails if payload is not a dict"""
        planning_agent = kernel.agent_registry["specialist-planning"]

        # Create task with non-dict payload
        task = Task(agent_id="specialist-planning", payload="not a dict")

        # Should raise TypeError
        with pytest.raises(TypeError, match="must be a dict"):
            planning_agent.process(task)


class TestStatusCommand:
    """Tests for --status command with specialist display"""

    def test_status_json_format(self, kernel):
        """Verify status output includes specialists in JSON format"""
        # This would be tested via CLI integration test
        # Here we verify that kernel.agent_registry has the expected structure
        agents = []
        for agent_id, agent in kernel.agent_registry.items():
            agent_info = {
                "agent_id": agent_id,
                "type": agent.__class__.__name__,
            }

            if hasattr(agent, "specialist_class"):
                agent_info["specialist_class"] = agent.specialist_class.__name__
                agent_info["role"] = agent.role

            agents.append(agent_info)

        # Verify structure
        assert len(agents) == 3

        planning_info = next(a for a in agents if a["agent_id"] == "specialist-planning")
        assert planning_info["type"] == "SpecialistFactoryAgent"
        assert planning_info["specialist_class"] == "PlanningSpecialist"
        assert planning_info["role"] == "planning"

        coding_info = next(a for a in agents if a["agent_id"] == "specialist-coding")
        assert coding_info["type"] == "SpecialistFactoryAgent"
        assert coding_info["specialist_class"] == "CodingSpecialist"
        assert coding_info["role"] == "coding"

        testing_info = next(a for a in agents if a["agent_id"] == "specialist-testing")
        assert testing_info["type"] == "SpecialistFactoryAgent"
        assert testing_info["specialist_class"] == "TestingSpecialist"
        assert testing_info["role"] == "testing"
