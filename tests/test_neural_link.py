#!/usr/bin/env python3
"""Tests for GAD-904: Agent Routing System (Neural Link)

Verifies capability-based agent selection without triggering real LLM calls.
"""

from pathlib import Path

import pytest

# Import SemanticAction definitions
runtime_dir = Path(__file__).parent.parent / "agency_os" / "core_system" / "runtime"
from agency_os.core_system.runtime.semantic_actions import SemanticAction, SemanticActionType

# Import personas and router
personas_dir = Path(__file__).parent.parent / "agency_os" / "03_agents" / "personas"


# Use simple dummy agents to avoid runtime infrastructure dependencies
class DummyAgent:
    def __init__(self, name: str, capabilities: list[str]):
        self.name = name
        self.capabilities = capabilities


# Real personas available but not used to keep tests $0 and infra-free
# from coder import CoderAgent
# from researcher import ResearcherAgent

router_dir = Path(__file__).parent.parent / "agency_os" / "core_system" / "playbook"
from executor import GraphExecutor, WorkflowGraph, WorkflowNode
from router import AgentRouter


class TestAgentRouter:
    def test_router_selects_coder_for_debugging(self):
        coder = DummyAgent(name="coder", capabilities=["coding", "debugging", "python"])
        researcher = DummyAgent(name="researcher", capabilities=["research", "search", "synthesis"])
        router = AgentRouter([coder, researcher])

        action = SemanticAction(
            action_type=SemanticActionType.DEBUG,
            name="debug_task",
            intent="Debug failing tests",
            description="Investigate and fix failures",
            required_skills=["debugging"],
        )
        best = router.find_best_agent(action)
        assert best is coder

    def test_router_returns_none_if_no_match(self):
        coder = DummyAgent(name="coder", capabilities=["coding", "debugging"])
        router = AgentRouter([coder])
        action = SemanticAction(
            action_type=SemanticActionType.RESEARCH,
            name="deep_research",
            intent="Investigate novel topic",
            description="",
            required_skills=["quantum_physics"],
        )
        assert router.find_best_agent(action) is None


class TestExecutorNeuralLink:
    def test_executor_uses_router_for_step(self):
        coder = DummyAgent(name="coder", capabilities=["coding", "debugging"])
        researcher = DummyAgent(name="researcher", capabilities=["research"])
        router = AgentRouter([coder, researcher])

        # Minimal workflow graph with one node needing debugging
        nodes = {
            "debug_step": WorkflowNode(
                id="debug_step",
                action="debug",
                required_skills=["debugging"],
            )
        }
        edges = []
        graph = WorkflowGraph(
            id="w1",
            name="Debug Workflow",
            intent="Test neural link",
            nodes=nodes,
            edges=edges,
            entry_point="debug_step",
            exit_points=["debug_step"],
        )

        executor = GraphExecutor()
        executor.set_router(router)
        result = executor.execute_step(graph, "debug_step")
        assert result.status.value == "success"
        assert result.output["agent"] == "coder"
        assert "debugging" in result.output["skills_used"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
