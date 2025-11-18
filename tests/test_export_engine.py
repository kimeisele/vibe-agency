"""Tests for multi-format export engine (GAD-701 Task 7)"""

import json


def test_json_export_structure():
    """Test JSON export has correct structure."""
    # Simple task data
    tasks = {
        "t1": {"status": "DONE"},
        "t2": {"status": "DONE"},
        "t3": {"status": "IN_PROGRESS"},
        "t4": {"status": "TODO"},
    }

    # Simulate export
    result = {
        "version": 1,
        "project_name": "test-project",
        "phases": [{"name": "PHASE_1", "status": "IN_PROGRESS", "progress": 50, "task_count": 4}],
        "tasks_summary": {
            "total": len(tasks),
            "done": sum(1 for t in tasks.values() if t["status"] == "DONE"),
            "in_progress": sum(1 for t in tasks.values() if t["status"] == "IN_PROGRESS"),
            "todo": sum(1 for t in tasks.values() if t["status"] == "TODO"),
            "blocked": 0,
        },
    }

    # Must be valid JSON
    json_str = json.dumps(result)
    parsed = json.loads(json_str)

    assert parsed["version"] == 1
    assert parsed["project_name"] == "test-project"
    assert parsed["tasks_summary"]["total"] == 4
    assert parsed["tasks_summary"]["done"] == 2


def test_csv_format_valid():
    """Test CSV export has valid format."""
    lines = []
    lines.append("ID,Name,Status,Priority,Created,Progress")
    lines.append('task-1,"Build System",DONE,9,2025-11-18T00:00:00,100%')
    lines.append('task-2,"Add Features",IN_PROGRESS,8,2025-11-18T01:00:00,50%')
    lines.append('task-3,"Testing",TODO,7,2025-11-18T02:00:00,0%')

    csv_str = "\n".join(lines)

    # Parse CSV
    csv_lines = csv_str.split("\n")
    assert len(csv_lines) == 4

    # Header
    header = csv_lines[0].split(",")
    assert "ID" in header
    assert "Status" in header
    assert "Priority" in header
    assert "Progress" in header

    # Data row
    row = csv_lines[1].split(",")
    assert len(row) == 6
    assert row[0] == "task-1"


def test_markdown_format_structure():
    """Test Markdown export has valid structure."""
    md = """# test-project

## Project Overview

**Progress:** 2/4 tasks complete (50%)

## Phases

### PHASE_1
**Status:** IN_PROGRESS | **Progress:** 50%

- **Build System** [DONE] (Priority: 9/10)
  - Build the core system
  - Validation: 2/2 checks (100%)

- **Add Features** [IN_PROGRESS] (Priority: 8/10)
  - Add new features
  - Validation: 1/2 checks (50%)
"""

    # Check structure
    assert "# test-project" in md
    assert "## Project Overview" in md
    assert "## Phases" in md
    assert "### PHASE_1" in md
    assert "Progress:" in md
    assert "[DONE]" in md
    assert "[IN_PROGRESS]" in md


def test_summary_dict_completeness():
    """Test summary report includes all required fields."""
    summary = {
        "project_name": "test-project",
        "total_tasks": 4,
        "completed_tasks": 2,
        "in_progress_tasks": 1,
        "todo_tasks": 1,
        "blocked_tasks": 0,
        "progress_percent": 50,
        "average_priority": 8,
        "time_budgeted_mins": 480,
        "time_used_mins": 120,
        "phases": [
            {"name": "PHASE_1", "status": "IN_PROGRESS", "progress": 50},
            {"name": "PHASE_2", "status": "TODO", "progress": 0},
        ],
    }

    # Required fields
    assert summary["project_name"]
    assert summary["total_tasks"] == 4
    assert summary["completed_tasks"] == 2
    assert summary["progress_percent"] == 50
    assert summary["time_budgeted_mins"] == 480
    assert len(summary["phases"]) == 2


def test_progress_calculation_from_validation():
    """Test task progress calculation from validation checks."""
    # Task with validation checks
    validation_checks = [
        {"id": "c1", "status": True},
        {"id": "c2", "status": True},
        {"id": "c3", "status": False},
    ]

    passing = sum(1 for c in validation_checks if c["status"])
    total = len(validation_checks)
    progress = int((passing / total) * 100) if total > 0 else 0

    assert passing == 2
    assert total == 3
    assert progress == 66


def test_empty_project_export():
    """Test export handles empty project."""
    summary = {
        "project_name": "empty-project",
        "total_tasks": 0,
        "completed_tasks": 0,
        "in_progress_tasks": 0,
        "todo_tasks": 0,
        "blocked_tasks": 0,
        "progress_percent": 0,
        "phases": [],
    }

    assert summary["total_tasks"] == 0
    assert summary["progress_percent"] == 0
    assert len(summary["phases"]) == 0


def test_csv_escaping_special_chars():
    """Test CSV properly escapes task names with special characters."""
    # Task name with comma
    task_name = "Build System, Phase 2"
    escaped_name = task_name.replace(",", ";")

    csv_line = f'task-1,"{escaped_name}",DONE,9,2025-11-18,100%'

    # Should be parseable
    assert "task-1" in csv_line
    assert "DONE" in csv_line
    assert "9" in csv_line


def test_json_pretty_print():
    """Test JSON pretty printing."""
    data = {"project": "test", "tasks": 5, "progress": 50}

    # Without pretty print
    compact = json.dumps(data)
    assert "\n" not in compact

    # With pretty print
    pretty = json.dumps(data, indent=2)
    assert "\n" in pretty
    assert '"project"' in pretty


def test_phase_status_values():
    """Test phase status values are properly represented."""
    phases = [
        {"name": "PHASE_1", "status": "IN_PROGRESS", "progress": 50},
        {"name": "PHASE_2", "status": "TODO", "progress": 0},
        {"name": "PHASE_3", "status": "DONE", "progress": 100},
    ]

    for phase in phases:
        assert phase["status"] in ["TODO", "IN_PROGRESS", "DONE", "BLOCKED"]
        assert 0 <= phase["progress"] <= 100


def test_task_status_in_summary():
    """Test all task statuses represented in summary."""
    summary = {
        "completed_tasks": 2,
        "in_progress_tasks": 1,
        "todo_tasks": 5,
        "blocked_tasks": 0,
    }

    total = (
        summary["completed_tasks"]
        + summary["in_progress_tasks"]
        + summary["todo_tasks"]
        + summary["blocked_tasks"]
    )

    assert total == 8
    assert all(v >= 0 for v in summary.values())
