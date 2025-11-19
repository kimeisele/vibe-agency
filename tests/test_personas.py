#!/usr/bin/env python3
"""
Unit tests for Agent Personas (GAD-302)

Tests verify specialized personas inherit BaseAgent correctly and have
domain-specific capabilities.
"""

import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import pytest

# Add agency_os to path
import importlib.util
vibe_root = Path(__file__).parent.parent

# Dynamic import to handle numeric directory names
spec = importlib.util.spec_from_file_location(
    "personas",
    vibe_root / "agency_os" / "03_agents" / "personas" / "__init__.py"
)
personas_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(personas_module)

CoderAgent = personas_module.CoderAgent
ResearcherAgent = personas_module.ResearcherAgent
ReviewerAgent = personas_module.ReviewerAgent
ArchitectAgent = personas_module.ArchitectAgent


class TestCoderAgent:
    """Test Coder persona specialization."""

    def test_coder_init(self, tmp_path):
        """Test Coder agent initialization."""
        # Setup infrastructure
        (tmp_path / ".vibe" / "runtime").mkdir(parents=True)
        (tmp_path / ".vibe" / "config").mkdir(parents=True)
        (tmp_path / "bin").mkdir(parents=True)

        (tmp_path / ".vibe" / "runtime" / "context.json").write_text('{}')
        (tmp_path / ".vibe" / "config" / "roadmap.yaml").write_text("test")
        (tmp_path / "bin" / "vibe-shell").write_text("#!/bin/bash\necho test")
        (tmp_path / "bin" / "vibe-knowledge").write_text("#!/bin/bash\necho test")

        agent = CoderAgent(vibe_root=tmp_path)

        assert agent.name == "claude-coder"
        assert agent.role == "Code Developer"
        assert agent.execution_count == 0

    def test_coder_knowledge_domain(self, tmp_path):
        """Test Coder agent defaults to patterns domain."""
        (tmp_path / ".vibe" / "runtime").mkdir(parents=True)
        (tmp_path / ".vibe" / "config").mkdir(parents=True)
        (tmp_path / "bin").mkdir(parents=True)

        (tmp_path / ".vibe" / "runtime" / "context.json").write_text('{}')
        (tmp_path / ".vibe" / "config" / "roadmap.yaml").write_text("test")
        (tmp_path / "bin" / "vibe-shell").write_text("#!/bin/bash\necho test")
        (tmp_path / "bin" / "vibe-knowledge").write_text("#!/bin/bash\necho test")

        agent = CoderAgent(vibe_root=tmp_path)

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0,
                stdout="Path: patterns/python-context.md\nRelevance: 90.0%\n",
                stderr=""
            )

            result = agent.consult_knowledge("context manager")

            # Verify command was called with patterns domain
            assert result.found is True

    def test_coder_get_context_with_role(self, tmp_path):
        """Test Coder context includes role and capabilities."""
        (tmp_path / ".vibe" / "runtime").mkdir(parents=True)
        (tmp_path / ".vibe" / "config").mkdir(parents=True)
        (tmp_path / "bin").mkdir(parents=True)

        (tmp_path / ".vibe" / "runtime" / "context.json").write_text('{}')
        (tmp_path / ".vibe" / "config" / "roadmap.yaml").write_text("test")
        (tmp_path / "bin" / "vibe-shell").write_text("#!/bin/bash\necho test")
        (tmp_path / "bin" / "vibe-knowledge").write_text("#!/bin/bash\necho test")

        agent = CoderAgent(vibe_root=tmp_path)
        context = agent.get_context_with_role()

        assert context["persona"] == "Coder"
        assert "Write Python code" in context["capabilities"]
        assert "patterns" in context["knowledge_domains"]


class TestResearcherAgent:
    """Test Researcher persona specialization."""

    def test_researcher_init(self, tmp_path):
        """Test Researcher agent initialization."""
        (tmp_path / ".vibe" / "runtime").mkdir(parents=True)
        (tmp_path / ".vibe" / "config").mkdir(parents=True)
        (tmp_path / "bin").mkdir(parents=True)

        (tmp_path / ".vibe" / "runtime" / "context.json").write_text('{}')
        (tmp_path / ".vibe" / "config" / "roadmap.yaml").write_text("test")
        (tmp_path / "bin" / "vibe-shell").write_text("#!/bin/bash\necho test")
        (tmp_path / "bin" / "vibe-knowledge").write_text("#!/bin/bash\necho test")

        agent = ResearcherAgent(vibe_root=tmp_path)

        assert agent.name == "claude-researcher"
        assert agent.role == "Researcher"
        assert agent.execution_count == 0

    def test_researcher_knowledge_domain(self, tmp_path):
        """Test Researcher agent defaults to research domain."""
        (tmp_path / ".vibe" / "runtime").mkdir(parents=True)
        (tmp_path / ".vibe" / "config").mkdir(parents=True)
        (tmp_path / "bin").mkdir(parents=True)

        (tmp_path / ".vibe" / "runtime" / "context.json").write_text('{}')
        (tmp_path / ".vibe" / "config" / "roadmap.yaml").write_text("test")
        (tmp_path / "bin" / "vibe-shell").write_text("#!/bin/bash\necho test")
        (tmp_path / "bin" / "vibe-knowledge").write_text("#!/bin/bash\necho test")

        agent = ResearcherAgent(vibe_root=tmp_path)

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0,
                stdout="Path: research/ai-trends.md\nRelevance: 85.0%\n",
                stderr=""
            )

            result = agent.consult_knowledge("vector embeddings")

            assert result.found is True

    def test_researcher_research_topic(self, tmp_path):
        """Test Researcher can conduct topic research."""
        (tmp_path / ".vibe" / "runtime").mkdir(parents=True)
        (tmp_path / ".vibe" / "config").mkdir(parents=True)
        (tmp_path / "bin").mkdir(parents=True)

        (tmp_path / ".vibe" / "runtime" / "context.json").write_text('{}')
        (tmp_path / ".vibe" / "config" / "roadmap.yaml").write_text("test")
        (tmp_path / "bin" / "vibe-shell").write_text("#!/bin/bash\necho test")
        (tmp_path / "bin" / "vibe-knowledge").write_text("#!/bin/bash\necho test")

        agent = ResearcherAgent(vibe_root=tmp_path)

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0,
                stdout="Path: research/topic.md\nRelevance: 80.0%\n",
                stderr=""
            )

            result = agent.research_topic("machine learning")

            assert result["topic"] == "machine learning"
            assert result["found"] is True

    def test_researcher_compare_approaches(self, tmp_path):
        """Test Researcher can compare two approaches."""
        (tmp_path / ".vibe" / "runtime").mkdir(parents=True)
        (tmp_path / ".vibe" / "config").mkdir(parents=True)
        (tmp_path / "bin").mkdir(parents=True)

        (tmp_path / ".vibe" / "runtime" / "context.json").write_text('{}')
        (tmp_path / ".vibe" / "config" / "roadmap.yaml").write_text("test")
        (tmp_path / "bin" / "vibe-shell").write_text("#!/bin/bash\necho test")
        (tmp_path / "bin" / "vibe-knowledge").write_text("#!/bin/bash\necho test")

        agent = ResearcherAgent(vibe_root=tmp_path)

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0,
                stdout="Path: research/approach.md\nRelevance: 75.0%\n",
                stderr=""
            )

            result = agent.compare_approaches(
                "databases",
                "sql databases",
                "nosql databases"
            )

            assert result["topic"] == "databases"
            assert result["approach_a"] == "sql databases"
            assert result["approach_b"] == "nosql databases"

    def test_researcher_get_context_with_role(self, tmp_path):
        """Test Researcher context includes role and capabilities."""
        (tmp_path / ".vibe" / "runtime").mkdir(parents=True)
        (tmp_path / ".vibe" / "config").mkdir(parents=True)
        (tmp_path / "bin").mkdir(parents=True)

        (tmp_path / ".vibe" / "runtime" / "context.json").write_text('{}')
        (tmp_path / ".vibe" / "config" / "roadmap.yaml").write_text("test")
        (tmp_path / "bin" / "vibe-shell").write_text("#!/bin/bash\necho test")
        (tmp_path / "bin" / "vibe-knowledge").write_text("#!/bin/bash\necho test")

        agent = ResearcherAgent(vibe_root=tmp_path)
        context = agent.get_context_with_role()

        assert context["persona"] == "Researcher"
        assert "Deep research on topics" in context["capabilities"]
        assert "research" in context["knowledge_domains"]


class TestReviewerAgent:
    """Test Reviewer persona specialization."""

    def test_reviewer_init(self, tmp_path):
        """Test Reviewer agent initialization."""
        (tmp_path / ".vibe" / "runtime").mkdir(parents=True)
        (tmp_path / ".vibe" / "config").mkdir(parents=True)
        (tmp_path / "bin").mkdir(parents=True)

        (tmp_path / ".vibe" / "runtime" / "context.json").write_text('{}')
        (tmp_path / ".vibe" / "config" / "roadmap.yaml").write_text("test")
        (tmp_path / "bin" / "vibe-shell").write_text("#!/bin/bash\necho test")
        (tmp_path / "bin" / "vibe-knowledge").write_text("#!/bin/bash\necho test")

        agent = ReviewerAgent(vibe_root=tmp_path)

        assert agent.name == "claude-reviewer"
        assert agent.role == "Code Reviewer"

    def test_reviewer_review_code(self, tmp_path):
        """Test Reviewer can review code."""
        (tmp_path / ".vibe" / "runtime").mkdir(parents=True)
        (tmp_path / ".vibe" / "config").mkdir(parents=True)
        (tmp_path / "bin").mkdir(parents=True)

        (tmp_path / ".vibe" / "runtime" / "context.json").write_text('{}')
        (tmp_path / ".vibe" / "config" / "roadmap.yaml").write_text("test")
        (tmp_path / "bin" / "vibe-shell").write_text("#!/bin/bash\necho test")
        (tmp_path / "bin" / "vibe-knowledge").write_text("#!/bin/bash\necho test")

        agent = ReviewerAgent(vibe_root=tmp_path)

        review = agent.review_code("src/main.py")

        assert review["file"] == "src/main.py"
        assert "error_handling" in review["review_checklist"]
        assert "test_coverage" in review["review_checklist"]

    def test_reviewer_compare_architectures(self, tmp_path):
        """Test Reviewer can compare architectures."""
        (tmp_path / ".vibe" / "runtime").mkdir(parents=True)
        (tmp_path / ".vibe" / "config").mkdir(parents=True)
        (tmp_path / "bin").mkdir(parents=True)

        (tmp_path / ".vibe" / "runtime" / "context.json").write_text('{}')
        (tmp_path / ".vibe" / "config" / "roadmap.yaml").write_text("test")
        (tmp_path / "bin" / "vibe-shell").write_text("#!/bin/bash\necho test")
        (tmp_path / "bin" / "vibe-knowledge").write_text("#!/bin/bash\necho test")

        agent = ReviewerAgent(vibe_root=tmp_path)

        comparison = agent.compare_architectures(
            "monolith",
            "microservices"
        )

        assert comparison["approach_a"] == "monolith"
        assert comparison["approach_b"] == "microservices"
        assert "scalability" in comparison["evaluation_criteria"]

    def test_reviewer_get_context_with_role(self, tmp_path):
        """Test Reviewer context includes role and capabilities."""
        (tmp_path / ".vibe" / "runtime").mkdir(parents=True)
        (tmp_path / ".vibe" / "config").mkdir(parents=True)
        (tmp_path / "bin").mkdir(parents=True)

        (tmp_path / ".vibe" / "runtime" / "context.json").write_text('{}')
        (tmp_path / ".vibe" / "config" / "roadmap.yaml").write_text("test")
        (tmp_path / "bin" / "vibe-shell").write_text("#!/bin/bash\necho test")
        (tmp_path / "bin" / "vibe-knowledge").write_text("#!/bin/bash\necho test")

        agent = ReviewerAgent(vibe_root=tmp_path)
        context = agent.get_context_with_role()

        assert context["persona"] == "Reviewer"
        assert "Code quality analysis" in context["capabilities"]
        assert "patterns" in context["knowledge_domains"]


class TestArchitectAgent:
    """Test Architect persona specialization."""

    def test_architect_init(self, tmp_path):
        """Test Architect agent initialization."""
        (tmp_path / ".vibe" / "runtime").mkdir(parents=True)
        (tmp_path / ".vibe" / "config").mkdir(parents=True)
        (tmp_path / "bin").mkdir(parents=True)

        (tmp_path / ".vibe" / "runtime" / "context.json").write_text('{}')
        (tmp_path / ".vibe" / "config" / "roadmap.yaml").write_text("test")
        (tmp_path / "bin" / "vibe-shell").write_text("#!/bin/bash\necho test")
        (tmp_path / "bin" / "vibe-knowledge").write_text("#!/bin/bash\necho test")

        agent = ArchitectAgent(vibe_root=tmp_path)

        assert agent.name == "claude-architect"
        assert agent.role == "System Architect"

    def test_architect_design_system(self, tmp_path):
        """Test Architect can design a system."""
        (tmp_path / ".vibe" / "runtime").mkdir(parents=True)
        (tmp_path / ".vibe" / "config").mkdir(parents=True)
        (tmp_path / "bin").mkdir(parents=True)

        (tmp_path / ".vibe" / "runtime" / "context.json").write_text('{}')
        (tmp_path / ".vibe" / "config" / "roadmap.yaml").write_text("test")
        (tmp_path / "bin" / "vibe-shell").write_text("#!/bin/bash\necho test")
        (tmp_path / "bin" / "vibe-knowledge").write_text("#!/bin/bash\necho test")

        agent = ArchitectAgent(vibe_root=tmp_path)

        design = agent.design_system(
            "user-service",
            ["user authentication", "user profiles"],
            ["100k users", "single region"]
        )

        assert design["system"] == "user-service"
        assert len(design["requirements"]) == 2
        assert "scalability" in design["design_considerations"]

    def test_architect_evaluate_tradeoff(self, tmp_path):
        """Test Architect can evaluate tradeoffs."""
        (tmp_path / ".vibe" / "runtime").mkdir(parents=True)
        (tmp_path / ".vibe" / "config").mkdir(parents=True)
        (tmp_path / "bin").mkdir(parents=True)

        (tmp_path / ".vibe" / "runtime" / "context.json").write_text('{}')
        (tmp_path / ".vibe" / "config" / "roadmap.yaml").write_text("test")
        (tmp_path / "bin" / "vibe-shell").write_text("#!/bin/bash\necho test")
        (tmp_path / "bin" / "vibe-knowledge").write_text("#!/bin/bash\necho test")

        agent = ArchitectAgent(vibe_root=tmp_path)

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0,
                stdout="Path: decisions/api-design.md\nRelevance: 80.0%\n",
                stderr=""
            )

            tradeoff = agent.evaluate_tradeoff(
                "api design",
                "rest",
                "graphql"
            )

            assert tradeoff["decision"] == "api design"
            assert tradeoff["option_a"] == "rest"
            assert tradeoff["option_b"] == "graphql"

    def test_architect_document_adr(self, tmp_path):
        """Test Architect can document ADRs."""
        (tmp_path / ".vibe" / "runtime").mkdir(parents=True)
        (tmp_path / ".vibe" / "config").mkdir(parents=True)
        (tmp_path / "bin").mkdir(parents=True)

        (tmp_path / ".vibe" / "runtime" / "context.json").write_text('{}')
        (tmp_path / ".vibe" / "config" / "roadmap.yaml").write_text("test")
        (tmp_path / "bin" / "vibe-shell").write_text("#!/bin/bash\necho test")
        (tmp_path / "bin" / "vibe-knowledge").write_text("#!/bin/bash\necho test")

        agent = ArchitectAgent(vibe_root=tmp_path)

        adr = agent.document_adr(
            "Use REST API for service communication",
            status="ACCEPTED",
            context="Need to define service communication strategy",
            decision="Use REST API",
            consequences=["Standard HTTP semantics", "Wide tooling support"]
        )

        assert adr["title"] == "Use REST API for service communication"
        assert adr["status"] == "ACCEPTED"
        assert len(adr["consequences"]) == 2

    def test_architect_get_context_with_role(self, tmp_path):
        """Test Architect context includes role and capabilities."""
        (tmp_path / ".vibe" / "runtime").mkdir(parents=True)
        (tmp_path / ".vibe" / "config").mkdir(parents=True)
        (tmp_path / "bin").mkdir(parents=True)

        (tmp_path / ".vibe" / "runtime" / "context.json").write_text('{}')
        (tmp_path / ".vibe" / "config" / "roadmap.yaml").write_text("test")
        (tmp_path / "bin" / "vibe-shell").write_text("#!/bin/bash\necho test")
        (tmp_path / "bin" / "vibe-knowledge").write_text("#!/bin/bash\necho test")

        agent = ArchitectAgent(vibe_root=tmp_path)
        context = agent.get_context_with_role()

        assert context["persona"] == "Architect"
        assert "System design" in context["capabilities"]
        assert "decisions" in context["knowledge_domains"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
