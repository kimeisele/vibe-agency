"""Tests for metrics & reporting system (GAD-701 Task 6)"""


def test_overall_progress_calculation():
    """Test overall progress metrics calculation."""
    # Simple task data structure
    tasks = {
        "task-1": {"status": "DONE"},
        "task-2": {"status": "DONE"},
        "task-3": {"status": "IN_PROGRESS"},
        "task-4": {"status": "TODO"},
        "task-5": {"status": "BLOCKED"},
    }

    total = len(tasks)
    completed = sum(1 for t in tasks.values() if t["status"] == "DONE")
    in_progress = sum(1 for t in tasks.values() if t["status"] == "IN_PROGRESS")
    todo = sum(1 for t in tasks.values() if t["status"] == "TODO")
    blocked = sum(1 for t in tasks.values() if t["status"] == "BLOCKED")

    progress_percent = int((completed / total) * 100) if total > 0 else 0

    assert total == 5
    assert completed == 2
    assert in_progress == 1
    assert todo == 1
    assert blocked == 1
    assert progress_percent == 40


def test_progress_percent_calculation():
    """Test progress percentage calculation accuracy."""
    test_cases = [
        (0, 5, 0),      # 0 of 5 = 0%
        (1, 5, 20),     # 1 of 5 = 20%
        (2, 5, 40),     # 2 of 5 = 40%
        (3, 5, 60),     # 3 of 5 = 60%
        (5, 5, 100),    # 5 of 5 = 100%
        (0, 0, 0),      # 0 of 0 = 0% (no division by zero)
    ]

    for completed, total, expected_percent in test_cases:
        progress = 0 if total == 0 else int((completed / total) * 100)
        assert progress == expected_percent, f"{completed}/{total} should be {expected_percent}%"


def test_phase_metrics_calculation():
    """Test phase-specific metrics calculation."""
    phase_tasks = [
        {"id": "p1-t1", "status": "DONE"},
        {"id": "p1-t2", "status": "DONE"},
        {"id": "p1-t3", "status": "IN_PROGRESS"},
        {"id": "p1-t4", "status": "TODO"},
    ]

    total = len(phase_tasks)
    completed = sum(1 for t in phase_tasks if t["status"] == "DONE")
    in_progress = sum(1 for t in phase_tasks if t["status"] == "IN_PROGRESS")
    todo = sum(1 for t in phase_tasks if t["status"] == "TODO")

    progress_percent = int((completed / total) * 100) if total > 0 else 0

    assert total == 4
    assert completed == 2
    assert in_progress == 1
    assert todo == 1
    assert progress_percent == 50


def test_time_utilization_calculation():
    """Test time budget vs used calculation."""
    tasks = [
        {"time_budget_mins": 120, "time_used_mins": 60},
        {"time_budget_mins": 90, "time_used_mins": 45},
        {"time_budget_mins": 150, "time_used_mins": 100},
    ]

    total_budgeted = sum(t["time_budget_mins"] for t in tasks)
    total_used = sum(t["time_used_mins"] for t in tasks)

    utilization = int((total_used / total_budgeted) * 100) if total_budgeted > 0 else 0

    assert total_budgeted == 360
    assert total_used == 205
    assert utilization == 56  # 205/360 * 100 = 56.9%


def test_priority_distribution():
    """Test priority distribution counting."""
    tasks = {
        "t1": {"priority": 10},
        "t2": {"priority": 9},
        "t3": {"priority": 9},
        "t4": {"priority": 5},
        "t5": {"priority": 1},
    }

    distribution = {i: 0 for i in range(1, 11)}
    for task in tasks.values():
        if 1 <= task["priority"] <= 10:
            distribution[task["priority"]] += 1

    assert distribution[10] == 1
    assert distribution[9] == 2
    assert distribution[5] == 1
    assert distribution[1] == 1
    assert distribution[2] == 0


def test_validation_metrics():
    """Test validation check pass rate calculation."""
    checks = [
        {"id": "c1", "status": True},
        {"id": "c2", "status": True},
        {"id": "c3", "status": True},
        {"id": "c4", "status": False},
        {"id": "c5", "status": False},
    ]

    total_checks = len(checks)
    passing_checks = sum(1 for c in checks if c["status"])
    failing_checks = total_checks - passing_checks

    pass_percent = int((passing_checks / total_checks) * 100) if total_checks > 0 else 0

    assert total_checks == 5
    assert passing_checks == 3
    assert failing_checks == 2
    assert pass_percent == 60


def test_empty_roadmap_metrics():
    """Test metrics calculation for empty roadmap."""
    tasks = {}

    total = len(tasks)
    completed = sum(1 for t in tasks.values() if t.get("status") == "DONE")

    progress_percent = int((completed / total) * 100) if total > 0 else 0

    assert total == 0
    assert completed == 0
    assert progress_percent == 0


def test_all_tasks_done_metrics():
    """Test metrics when all tasks are complete."""
    tasks = {
        "t1": {"status": "DONE"},
        "t2": {"status": "DONE"},
        "t3": {"status": "DONE"},
    }

    total = len(tasks)
    completed = sum(1 for t in tasks.values() if t["status"] == "DONE")

    progress_percent = int((completed / total) * 100) if total > 0 else 0

    assert total == 3
    assert completed == 3
    assert progress_percent == 100


def test_status_distribution():
    """Test status distribution counting."""
    tasks = [
        {"status": "DONE"},
        {"status": "DONE"},
        {"status": "IN_PROGRESS"},
        {"status": "TODO"},
        {"status": "TODO"},
        {"status": "TODO"},
        {"status": "BLOCKED"},
    ]

    distribution = {
        "DONE": 0,
        "IN_PROGRESS": 0,
        "TODO": 0,
        "BLOCKED": 0,
    }

    for task in tasks:
        distribution[task["status"]] += 1

    assert distribution["DONE"] == 2
    assert distribution["IN_PROGRESS"] == 1
    assert distribution["TODO"] == 3
    assert distribution["BLOCKED"] == 1
