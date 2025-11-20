"""Tests for Project Memory - Semantic layer for STEWARD intelligence"""

import json
import tempfile
from pathlib import Path

import pytest

# Direct import from file (module naming issue with 00_ prefix)
PROJECT_ROOT = Path(__file__).parent.parent
runtime_path = PROJECT_ROOT / "agency_os" / "core_system" / "runtime"

from agency_os.core_system.runtime.project_memory import ProjectMemoryManager


class TestProjectMemoryManager:
    """Test project memory management"""

    @pytest.fixture
    def temp_project(self):
        """Create temporary project directory"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            yield project_root

    @pytest.fixture
    def memory_manager(self, temp_project):
        """Create memory manager instance"""
        return ProjectMemoryManager(temp_project)

    def test_creates_default_memory(self, memory_manager):
        """Test that default memory structure is created"""
        memory = memory_manager.load()

        assert memory["_schema_version"] == "1.0"
        assert "narrative" in memory
        assert "domain" in memory
        assert "trajectory" in memory
        assert "intent_history" in memory
        assert memory["narrative"] == []

    def test_saves_and_loads_memory(self, memory_manager, temp_project):
        """Test memory persistence"""
        memory = memory_manager.load()
        memory["narrative"].append({"session": 1, "summary": "Test session", "phase": "TESTING"})

        memory_manager.save(memory)

        # Load again and verify
        loaded = memory_manager.load()
        assert len(loaded["narrative"]) == 1
        assert loaded["narrative"][0]["summary"] == "Test session"

    def test_update_after_session(self, memory_manager):
        """Test session update logic"""
        context = {
            "session": {"phase": "CODING"},
            "tests": {"failing": [], "failing_count": 0},
        }

        memory_manager.update_after_session(
            session_summary="Implemented payment feature",
            context=context,
            user_input="Add Stripe payment integration",
        )

        memory = memory_manager.load()

        # Check narrative updated
        assert len(memory["narrative"]) == 1
        assert memory["narrative"][0]["summary"] == "Implemented payment feature"
        assert memory["narrative"][0]["phase"] == "CODING"

        # Check intent extraction
        assert len(memory["intent_history"]) == 1
        assert memory["intent_history"][0]["intent"] == "payment integration"

    def test_intent_extraction(self, memory_manager):
        """Test intent extraction from user input"""
        intents = memory_manager._extract_intents("Fix failing pytest tests", session_num=1)

        assert len(intents) == 2  # "test" and "fix" keywords
        assert any(i["intent"] == "fix failing tests" for i in intents)

    def test_semantic_summary_generation(self, memory_manager):
        """Test semantic summary generation"""
        # Add some memory
        context = {
            "session": {"phase": "CODING"},
            "tests": {"failing": [], "failing_count": 0},
        }

        memory_manager.update_after_session(
            session_summary="Setup project structure",
            context=context,
            user_input="Create restaurant booking app",
        )

        summary = memory_manager.get_semantic_summary()

        assert "PROJECT MEMORY SUMMARY" in summary
        assert "Session 1" in summary
        assert "Setup project structure" in summary

    def test_trajectory_phase_tracking(self, memory_manager):
        """Test that phase changes are tracked in trajectory"""
        # Session 1: PLANNING
        memory_manager.update_after_session(
            "Initial planning",
            {"session": {"phase": "PLANNING"}},
        )

        memory = memory_manager.load()
        assert memory["trajectory"]["phase"] == "PLANNING"
        assert memory["trajectory"]["completed"] == []

        # Session 2: CODING (phase changed)
        memory_manager.update_after_session(
            "Started coding",
            {"session": {"phase": "CODING"}},
        )

        memory = memory_manager.load()
        assert memory["trajectory"]["phase"] == "CODING"
        assert "PLANNING" in memory["trajectory"]["completed"]

    def test_blocker_tracking_from_failing_tests(self, memory_manager):
        """Test that failing tests create blockers"""
        context = {
            "session": {"phase": "CODING"},
            "tests": {"failing": ["test_1", "test_2"], "failing_count": 2, "framework": "pytest"},
        }

        memory_manager.update_after_session("Working on features", context)

        memory = memory_manager.load()
        assert len(memory["trajectory"]["blockers"]) > 0
        assert "2 failing tests" in memory["trajectory"]["blockers"][0]

    def test_domain_concept_extraction(self, memory_manager):
        """Test domain concept extraction from user input"""
        memory_manager.update_after_session(
            "Setup database",
            {"session": {"phase": "PLANNING"}},
            user_input="Add PostgreSQL database with user authentication and API endpoints",
        )

        memory = memory_manager.load()
        domain = memory["domain"]

        # Should extract: database, authentication, api
        assert "database" in domain["concepts"]
        assert "authentication" in domain["concepts"]
        assert "api" in domain["concepts"]

    def test_concern_extraction(self, memory_manager):
        """Test user concern extraction"""
        memory_manager.update_after_session(
            "Planning payment",
            {"session": {"phase": "PLANNING"}},
            user_input="Need PCI compliant payment processing with good performance",
        )

        memory = memory_manager.load()
        concerns = memory["domain"]["concerns"]

        assert "PCI compliance" in concerns
        assert "performance" in concerns

    def test_history_trimming(self, memory_manager):
        """Test that history is trimmed to prevent bloat"""
        context = {"session": {"phase": "TESTING"}}

        # Add 60 sessions (should trim to 50)
        for i in range(60):
            memory_manager.update_after_session(f"Session {i}", context, user_input=f"test {i}")

        memory = memory_manager.load()

        # Should only keep last 50 sessions
        assert len(memory["narrative"]) == 50
        assert memory["narrative"][-1]["summary"] == "Session 59"
        assert memory["narrative"][0]["summary"] == "Session 10"  # First 10 trimmed

    def test_corrupted_file_fallback(self, memory_manager, temp_project):
        """Test graceful fallback if memory file is corrupted"""
        # Create corrupted JSON file
        memory_file = temp_project / ".vibe" / "project_memory.json"
        memory_file.parent.mkdir(exist_ok=True)
        memory_file.write_text("{ invalid json }")

        # Should fallback to default without crashing
        memory = memory_manager.load()
        assert memory["_schema_version"] == "1.0"
        assert memory["narrative"] == []

    def test_project_id_inference(self, memory_manager, temp_project):
        """Test project ID inference from manifest or directory name"""
        # No manifest - should use directory name
        memory = memory_manager.load()
        assert memory["project_id"] == temp_project.name

        # With manifest
        manifest = {"project_id": "test-project-123"}
        manifest_file = temp_project / "project_manifest.json"
        manifest_file.write_text(json.dumps(manifest))

        # Create new manager to re-infer
        new_manager = ProjectMemoryManager(temp_project)
        memory = new_manager.load()
        assert memory["project_id"] == "test-project-123"
