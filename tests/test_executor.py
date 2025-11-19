#!/usr/bin/env python3
"""
Test suite for GAD-902: Graph Executor

Tests the graph-based orchestration logic in isolation.
Ensures the executor correctly:
  1. Validates workflow graphs
  2. Performs topological sort
  3. Detects circular dependencies
  4. Generates execution plans
  5. Handles dry-run mode
"""

import sys
from pathlib import Path

import pytest

# Add runtime directory to path
runtime_dir = Path(__file__).parent.parent / "agency_os" / "00_system" / "playbook"
sys.path.insert(0, str(runtime_dir))

from executor import (
    ExecutionStatus,
    GraphExecutor,
    MockAgent,
    WorkflowEdge,
    WorkflowGraph,
    WorkflowNode,
)


class TestGraphExecutor:
    """Tests for graph executor logic"""

    def test_executor_initializes_with_mock_agent(self):
        """Executor initializes with mock agent by default"""
        executor = GraphExecutor()
        assert executor.agent is not None
        assert isinstance(executor.agent, MockAgent)

    def test_topological_sort_simple_chain(self):
        """Topological sort handles simple linear workflow"""
        nodes = {
            "step1": WorkflowNode(id="step1", action="analyze"),
            "step2": WorkflowNode(id="step2", action="design"),
            "step3": WorkflowNode(id="step3", action="implement"),
        }

        edges = [
            WorkflowEdge("step1", "step2"),
            WorkflowEdge("step2", "step3"),
        ]

        workflow = WorkflowGraph(
            id="test",
            name="Test",
            intent="Test",
            nodes=nodes,
            edges=edges,
            entry_point="step1",
            exit_points=["step3"],
        )

        executor = GraphExecutor()
        plan = executor._topological_sort(workflow)

        assert plan.is_valid
        assert plan.execution_order == ["step1", "step2", "step3"]
        assert plan.dependencies == {
            "step1": [],
            "step2": ["step1"],
            "step3": ["step2"],
        }

    def test_topological_sort_parallel_steps(self):
        """Topological sort handles parallel steps correctly"""
        nodes = {
            "start": WorkflowNode(id="start", action="start"),
            "parallel_a": WorkflowNode(id="parallel_a", action="task_a"),
            "parallel_b": WorkflowNode(id="parallel_b", action="task_b"),
            "end": WorkflowNode(id="end", action="end"),
        }

        edges = [
            WorkflowEdge("start", "parallel_a"),
            WorkflowEdge("start", "parallel_b"),
            WorkflowEdge("parallel_a", "end"),
            WorkflowEdge("parallel_b", "end"),
        ]

        workflow = WorkflowGraph(
            id="test",
            name="Test",
            intent="Test",
            nodes=nodes,
            edges=edges,
            entry_point="start",
            exit_points=["end"],
        )

        executor = GraphExecutor()
        plan = executor._topological_sort(workflow)

        assert plan.is_valid
        assert plan.execution_order[0] == "start"
        assert plan.execution_order[-1] == "end"
        # parallel_a and parallel_b can be in any order as long as after start, before end
        assert set(plan.execution_order[1:3]) == {"parallel_a", "parallel_b"}

    def test_circular_dependency_detection(self):
        """Executor detects circular dependencies"""
        nodes = {
            "step1": WorkflowNode(id="step1", action="step1"),
            "step2": WorkflowNode(id="step2", action="step2"),
            "step3": WorkflowNode(id="step3", action="step3"),
        }

        edges = [
            WorkflowEdge("step1", "step2"),
            WorkflowEdge("step2", "step3"),
            WorkflowEdge("step3", "step1"),  # Creates cycle
        ]

        workflow = WorkflowGraph(
            id="test",
            name="Test",
            intent="Test",
            nodes=nodes,
            edges=edges,
            entry_point="step1",
            exit_points=["step3"],
        )

        executor = GraphExecutor()
        plan = executor._topological_sort(workflow)

        assert not plan.is_valid
        assert "circular" in plan.errors[0].lower()

    def test_missing_node_detection(self):
        """Executor detects edges pointing to non-existent nodes"""
        nodes = {
            "step1": WorkflowNode(id="step1", action="step1"),
            "step2": WorkflowNode(id="step2", action="step2"),
        }

        edges = [
            WorkflowEdge("step1", "nonexistent"),  # Points to non-existent node
        ]

        workflow = WorkflowGraph(
            id="test",
            name="Test",
            intent="Test",
            nodes=nodes,
            edges=edges,
            entry_point="step1",
            exit_points=["step2"],
        )

        executor = GraphExecutor()
        plan = executor._topological_sort(workflow)

        assert not plan.is_valid
        assert "non-existent" in plan.errors[0].lower()

    def test_missing_entry_point_detection(self):
        """Executor detects missing entry point"""
        nodes = {
            "step1": WorkflowNode(id="step1", action="step1"),
        }

        edges = []

        workflow = WorkflowGraph(
            id="test",
            name="Test",
            intent="Test",
            nodes=nodes,
            edges=edges,
            entry_point="nonexistent",  # Entry point doesn't exist
            exit_points=["step1"],
        )

        executor = GraphExecutor()
        plan = executor._topological_sort(workflow)

        assert not plan.is_valid
        assert "entry point" in plan.errors[0].lower()

    def test_validate_workflow_valid(self):
        """Validate workflow returns true for valid graph"""
        nodes = {
            "step1": WorkflowNode(id="step1", action="step1"),
            "step2": WorkflowNode(id="step2", action="step2"),
        }

        edges = [WorkflowEdge("step1", "step2")]

        workflow = WorkflowGraph(
            id="test",
            name="Test",
            intent="Test",
            nodes=nodes,
            edges=edges,
            entry_point="step1",
            exit_points=["step2"],
        )

        executor = GraphExecutor()
        is_valid, message = executor.validate_workflow(workflow)

        assert is_valid
        assert "valid" in message.lower()

    def test_validate_workflow_invalid(self):
        """Validate workflow returns false for invalid graph"""
        nodes = {
            "step1": WorkflowNode(id="step1", action="step1"),
        }

        edges = [WorkflowEdge("step1", "nonexistent")]

        workflow = WorkflowGraph(
            id="test",
            name="Test",
            intent="Test",
            nodes=nodes,
            edges=edges,
            entry_point="step1",
            exit_points=["nonexistent"],
        )

        executor = GraphExecutor()
        is_valid, message = executor.validate_workflow(workflow)

        assert not is_valid

    def test_dry_run_simple_workflow(self):
        """Dry-run generates execution plan without executing"""
        nodes = {
            "step1": WorkflowNode(id="step1", action="analyze"),
            "step2": WorkflowNode(id="step2", action="implement"),
        }

        edges = [WorkflowEdge("step1", "step2")]

        workflow = WorkflowGraph(
            id="test",
            name="Test Workflow",
            intent="Test intent",
            nodes=nodes,
            edges=edges,
            entry_point="step1",
            exit_points=["step2"],
        )

        executor = GraphExecutor()
        result = executor.dry_run(workflow)

        assert result["is_valid"]
        assert result["workflow_id"] == "test"
        assert result["execution_plan"]["execution_order"] == ["step1", "step2"]
        assert "step1" in result["nodes"]
        assert "step2" in result["nodes"]

    def test_dry_run_includes_node_details(self):
        """Dry-run includes all node details in output"""
        nodes = {
            "step1": WorkflowNode(
                id="step1",
                action="analyze",
                description="Analyze problem",
                required_skills=["analysis"],
                timeout_seconds=600,
            ),
        }

        edges = []

        workflow = WorkflowGraph(
            id="test",
            name="Test",
            intent="Test",
            nodes=nodes,
            edges=edges,
            entry_point="step1",
            exit_points=["step1"],
        )

        executor = GraphExecutor()
        result = executor.dry_run(workflow)

        node_details = result["nodes"]["step1"]
        assert node_details["action"] == "analyze"
        assert node_details["description"] == "Analyze problem"
        assert node_details["required_skills"] == ["analysis"]
        assert node_details["timeout_seconds"] == 600

    def test_execute_workflow(self):
        """Execute workflow generates results"""
        nodes = {
            "step1": WorkflowNode(id="step1", action="step1"),
            "step2": WorkflowNode(id="step2", action="step2"),
        }

        edges = [WorkflowEdge("step1", "step2")]

        workflow = WorkflowGraph(
            id="test",
            name="Test",
            intent="Test",
            nodes=nodes,
            edges=edges,
            entry_point="step1",
            exit_points=["step2"],
        )

        executor = GraphExecutor()
        result = executor.execute(workflow)

        assert result["status"] == "success"
        assert result["execution_order"] == ["step1", "step2"]
        assert len(result["results"]) == 2

    def test_execution_history_tracking(self):
        """Executor tracks execution history"""
        nodes = {
            "step1": WorkflowNode(id="step1", action="step1"),
        }

        edges = []

        workflow = WorkflowGraph(
            id="test",
            name="Test",
            intent="Test",
            nodes=nodes,
            edges=edges,
            entry_point="step1",
            exit_points=["step1"],
        )

        executor = GraphExecutor()
        executor.execute(workflow)

        history = executor.get_execution_history()
        assert len(history) > 0
        assert history[0].node_id == "step1"
        assert history[0].status == ExecutionStatus.SUCCESS

    def test_cost_estimation(self):
        """Executor returns estimated workflow cost"""
        nodes = {
            "step1": WorkflowNode(id="step1", action="step1"),
        }

        edges = []

        workflow = WorkflowGraph(
            id="test",
            name="Test",
            intent="Test",
            nodes=nodes,
            edges=edges,
            entry_point="step1",
            exit_points=["step1"],
            estimated_cost_usd=1.50,
        )

        executor = GraphExecutor()
        cost = executor.get_execution_cost(workflow)

        assert cost == 1.50

    def test_mock_agent_capabilities(self):
        """Mock agent reports its capabilities"""
        agent = MockAgent(skills=["coding", "testing"])

        assert agent.can_execute(["coding"])
        assert agent.can_execute(["coding", "testing"])
        assert not agent.can_execute(["unknown_skill"])

    def test_complex_workflow_with_branching(self):
        """Executor handles complex workflows with branching"""
        nodes = {
            "start": WorkflowNode(id="start", action="start"),
            "branch_a": WorkflowNode(id="branch_a", action="branch_a"),
            "branch_b": WorkflowNode(id="branch_b", action="branch_b"),
            "join": WorkflowNode(id="join", action="join"),
            "end": WorkflowNode(id="end", action="end"),
        }

        edges = [
            WorkflowEdge("start", "branch_a"),
            WorkflowEdge("start", "branch_b"),
            WorkflowEdge("branch_a", "join"),
            WorkflowEdge("branch_b", "join"),
            WorkflowEdge("join", "end"),
        ]

        workflow = WorkflowGraph(
            id="complex",
            name="Complex Workflow",
            intent="Test complex workflow",
            nodes=nodes,
            edges=edges,
            entry_point="start",
            exit_points=["end"],
            estimated_cost_usd=2.00,
        )

        executor = GraphExecutor()
        is_valid, message = executor.validate_workflow(workflow)

        assert is_valid
        plan = executor._topological_sort(workflow)
        assert plan.is_valid
        assert plan.execution_order[0] == "start"
        assert plan.execution_order[-1] == "end"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
