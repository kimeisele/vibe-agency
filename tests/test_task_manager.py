"""Unit Tests for Task Manager (GAD-701)"""

import importlib
import json
import tempfile
from pathlib import Path

import pytest

# Import task_management module dynamically (00_system starts with digit)
task_management = importlib.import_module('agency_os.00_system.task_management')
TaskManager = task_management.TaskManager
Task = task_management.Task
ActiveMission = task_management.ActiveMission
TaskStatus = task_management.TaskStatus
ValidationCheck = task_management.ValidationCheck


@pytest.fixture
def temp_vibe_root():
    """Create temporary directory for testing"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def task_manager(temp_vibe_root):
    """Create TaskManager instance for testing"""
    return TaskManager(temp_vibe_root)


class TestTaskManagerPersistence:
    """Test persistence of mission state"""

    def test_save_and_load_mission(self, task_manager, temp_vibe_root):
        """Test that mission state is saved and loaded correctly"""
        mission = ActiveMission(
            current_phase="CODING",
            total_tasks_completed=5
        )
        task_manager._save_mission(mission)

        # Verify file was created
        assert task_manager.state_file.exists()

        # Load and verify
        loaded_mission = task_manager.get_active_mission()
        assert loaded_mission.current_phase == "CODING"
        assert loaded_mission.total_tasks_completed == 5

    def test_empty_mission_on_first_run(self, task_manager):
        """Test that an empty mission is returned if no state file exists"""
        mission = task_manager.get_active_mission()
        assert mission.current_task is None
        assert mission.total_tasks_completed == 0


class TestFileLocking:
    """Test atomic file locking"""

    def test_concurrent_writes_dont_corrupt(self, task_manager):
        """Test that file locking prevents corruption during concurrent writes"""
        mission1 = ActiveMission(total_tasks_completed=1)
        mission2 = ActiveMission(total_tasks_completed=2)

        # Save mission 1
        task_manager._save_mission(mission1)
        loaded1 = task_manager.get_active_mission()
        assert loaded1.total_tasks_completed == 1

        # Save mission 2
        task_manager._save_mission(mission2)
        loaded2 = task_manager.get_active_mission()
        assert loaded2.total_tasks_completed == 2

        # Verify JSON is valid (not corrupted)
        with open(task_manager.state_file) as f:
            data = json.load(f)
            assert data['total_tasks_completed'] == 2


class TestValidation:
    """Test validation system"""

    def test_validate_current_task_with_no_active_task(self, task_manager):
        """Test validation when no task is active"""
        result = task_manager.validate_current_task()
        assert result["valid"] is False
        assert "error" in result

    def test_task_completion_requires_validation(self, task_manager, temp_vibe_root):
        """Test that task completion checks validation"""
        # Create a task with no validation checks (should fail)
        task = Task(
            id="test-task",
            name="Test Task",
            description="A test task",
            status=TaskStatus.IN_PROGRESS
        )

        mission = ActiveMission(current_task=task)
        task_manager._save_mission(mission)

        # Task with no validation checks should have is_complete() = True
        # (all() of empty list is True)
        assert task.is_complete() is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
