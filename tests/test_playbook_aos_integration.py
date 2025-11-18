"""
Test Playbook AOS Integration
Tests the lean MVP implementation of playbook integration into Agency OS.
"""

import subprocess
import sys
from pathlib import Path

import pytest

# Add agency_os to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "agency_os" / "00_system" / "runtime"))


def test_context_loader():
    """Test that ContextLoader can load context"""
    from context_loader import ContextLoader

    loader = ContextLoader()
    context = loader.load()

    # Verify all context sources are present
    assert "session" in context
    assert "git" in context
    assert "tests" in context
    assert "manifest" in context
    assert "environment" in context

    # Verify defaults are reasonable
    assert context["session"]["phase"] in [
        "PLANNING",
        "CODING",
        "TESTING",
        "DEPLOYMENT",
        "MAINTENANCE",
    ]
    assert "branch" in context["git"]
    assert "status" in context["tests"]


def test_playbook_engine_explicit_match():
    """Test explicit keyword matching"""
    from playbook_engine import PlaybookEngine

    engine = PlaybookEngine()
    context = {"session": {}, "git": {}, "tests": {}, "manifest": {}, "environment": {}}

    # Test explicit match
    route = engine.route("I want to build a restaurant app", context)

    assert route is not None
    assert route.confidence == "explicit"
    assert "restaurant" in route.source.lower() or route.task == "plan"


def test_playbook_engine_context_match():
    """Test context-based routing"""
    from playbook_engine import PlaybookEngine

    engine = PlaybookEngine()

    # Context with failing tests
    context = {
        "session": {"phase": "CODING", "backlog": []},
        "git": {"uncommitted": 0},
        "tests": {"failing_count": 3, "failing": ["test_a", "test_b", "test_c"]},
        "manifest": {},
        "environment": {},
    }

    route = engine.route("", context)

    assert route is not None
    assert route.task == "debug"
    assert route.confidence == "context"
    assert "failing" in route.source.lower()


def test_playbook_engine_suggestion_mode():
    """Test suggestion mode when no match"""
    from playbook_engine import PlaybookEngine

    engine = PlaybookEngine()

    # Empty context
    context = {
        "session": {"phase": "CODING", "backlog": []},
        "git": {"uncommitted": 0},
        "tests": {"failing_count": 0, "failing": []},
        "manifest": {},
        "environment": {},
    }

    route = engine.route("", context)

    assert route is not None
    assert route.confidence == "suggested"
    assert len(route.description) > 0


def test_prompt_composer():
    """Test prompt composition"""
    from prompt_composer import PromptComposer

    composer = PromptComposer()

    context = {
        "session": {"phase": "CODING", "last_task": "implement", "backlog": ["Feature A"]},
        "git": {
            "branch": "main",
            "uncommitted": 2,
            "last_commit": "abc123",
            "recent_commits": ["abc123 Fix bug"],
        },
        "tests": {"failing": [], "failing_count": 0, "status": "pytest_unavailable"},
        "manifest": {"project_type": "web_app", "test_framework": "pytest"},
        "environment": {"status": "ready"},
    }

    prompt = composer.compose("test", context)

    # Verify context injection
    assert "CODING" in prompt
    assert "main" in prompt
    assert "STEWARD" in prompt
    assert "TEST" in prompt.upper()


def test_boot_sequence():
    """Test complete boot sequence"""
    from boot_sequence import BootSequence

    boot = BootSequence()

    # Should not raise
    # Just verify it can be instantiated
    assert boot.context_loader is not None
    assert boot.playbook_engine is not None
    assert boot.prompt_composer is not None


def test_task_playbooks_exist():
    """Test that all task playbooks were created"""
    tasks_dir = Path("agency_os/00_system/playbook/tasks")

    required_tasks = ["debug.md", "implement.md", "test.md", "plan.md", "document.md", "analyze.md"]

    for task in required_tasks:
        task_file = tasks_dir / task
        assert task_file.exists(), f"Task playbook missing: {task}"

        # Verify it has content
        content = task_file.read_text()
        assert len(content) > 100, f"Task playbook too short: {task}"
        assert "## Mission" in content, f"Task playbook missing Mission section: {task}"
        assert "## Workflow" in content, f"Task playbook missing Workflow section: {task}"


def test_registry_moved_to_aos():
    """Test that registry was moved to agency_os"""
    registry_path = Path("agency_os/00_system/playbook/_registry.yaml")

    assert registry_path.exists(), "Registry not moved to agency_os"

    # Verify it's valid YAML
    import yaml

    with open(registry_path) as f:
        registry = yaml.safe_load(f)

    assert "routes" in registry
    assert len(registry["routes"]) > 0


def test_vibe_cli_boot_integration():
    """Test that vibe-cli boot mode works with new integration"""
    # This is a lightweight smoke test - just verify imports don't fail
    result = subprocess.run(
        ["python3", "./vibe-cli", "boot", "--help"], capture_output=True, text=True, timeout=5
    )

    # Should not crash
    assert result.returncode in [0, 2]  # 0 = success, 2 = argparse help


def test_health_check():
    """Test boot sequence health check"""
    from boot_sequence import BootSequence

    boot = BootSequence()
    health = boot.health_check()

    # Should return boolean
    assert isinstance(health, bool)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
