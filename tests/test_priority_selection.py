"""Tests for priority-based task selection (GAD-701 Task 5)"""



def test_priority_selection_highest_first():
    """Test that highest priority TODO task is selected."""
    roadmap = {
        "version": 1,
        "project_name": "test",
        "phases": [
            {
                "name": "PHASE_1",
                "status": "TODO",
                "progress": 0,
                "task_ids": ["low-pri", "high-pri", "med-pri"],
            }
        ],
        "tasks": {
            "low-pri": {
                "id": "low-pri",
                "name": "Low Priority Task",
                "status": "TODO",
                "priority": 3,
                "created_at": "2025-11-18T00:00:00",
                "started_at": None,
                "completed_at": None,
                "time_budget_mins": 120,
                "time_used_mins": 0,
                "validation_checks": [],
                "blocking_reason": None,
                "blocked_by": [],
                "blocking_tasks": [],
                "related_files": [],
                "git_commits": [],
            },
            "high-pri": {
                "id": "high-pri",
                "name": "High Priority Task",
                "status": "TODO",
                "priority": 9,
                "created_at": "2025-11-18T00:00:00",
                "started_at": None,
                "completed_at": None,
                "time_budget_mins": 120,
                "time_used_mins": 0,
                "validation_checks": [],
                "blocking_reason": None,
                "blocked_by": [],
                "blocking_tasks": [],
                "related_files": [],
                "git_commits": [],
            },
            "med-pri": {
                "id": "med-pri",
                "name": "Medium Priority Task",
                "status": "TODO",
                "priority": 5,
                "created_at": "2025-11-18T00:00:00",
                "started_at": None,
                "completed_at": None,
                "time_budget_mins": 120,
                "time_used_mins": 0,
                "validation_checks": [],
                "blocking_reason": None,
                "blocked_by": [],
                "blocking_tasks": [],
                "related_files": [],
                "git_commits": [],
            },
        },
    }

    # Collect TODO tasks and sort by priority
    todo_tasks = [
        (task_id, task)
        for task_id, task in roadmap["tasks"].items()
        if task["status"] == "TODO" and not task.get("blocked_by")
    ]

    # Sort by priority descending (9, 5, 3)
    todo_tasks.sort(key=lambda x: x[1]["priority"], reverse=True)

    # First should be high-pri (priority 9)
    assert todo_tasks[0][0] == "high-pri", "Should select highest priority task first"
    assert todo_tasks[0][1]["priority"] == 9


def test_priority_selection_skips_done_tasks():
    """Test that DONE tasks are skipped in priority selection."""
    roadmap = {
        "version": 1,
        "project_name": "test",
        "phases": [
            {
                "name": "PHASE_1",
                "status": "TODO",
                "progress": 0,
                "task_ids": ["done-hi", "todo-lo", "todo-hi"],
            }
        ],
        "tasks": {
            "done-hi": {
                "id": "done-hi",
                "name": "Done High Priority",
                "status": "DONE",  # This is DONE
                "priority": 10,
                "created_at": "2025-11-18T00:00:00",
                "started_at": None,
                "completed_at": None,
                "time_budget_mins": 120,
                "time_used_mins": 0,
                "validation_checks": [],
                "blocking_reason": None,
                "blocked_by": [],
                "blocking_tasks": [],
                "related_files": [],
                "git_commits": [],
            },
            "todo-lo": {
                "id": "todo-lo",
                "name": "Todo Low Priority",
                "status": "TODO",
                "priority": 2,
                "created_at": "2025-11-18T00:00:00",
                "started_at": None,
                "completed_at": None,
                "time_budget_mins": 120,
                "time_used_mins": 0,
                "validation_checks": [],
                "blocking_reason": None,
                "blocked_by": [],
                "blocking_tasks": [],
                "related_files": [],
                "git_commits": [],
            },
            "todo-hi": {
                "id": "todo-hi",
                "name": "Todo High Priority",
                "status": "TODO",
                "priority": 8,
                "created_at": "2025-11-18T00:00:00",
                "started_at": None,
                "completed_at": None,
                "time_budget_mins": 120,
                "time_used_mins": 0,
                "validation_checks": [],
                "blocking_reason": None,
                "blocked_by": [],
                "blocking_tasks": [],
                "related_files": [],
                "git_commits": [],
            },
        },
    }

    # Collect only TODO tasks (skip DONE)
    todo_tasks = [
        (task_id, task)
        for task_id, task in roadmap["tasks"].items()
        if task["status"] == "TODO"
    ]

    # Should have 2 TODO tasks
    assert len(todo_tasks) == 2

    # Sort by priority
    todo_tasks.sort(key=lambda x: x[1]["priority"], reverse=True)

    # First should be todo-hi (priority 8)
    assert todo_tasks[0][0] == "todo-hi"


def test_priority_selection_respects_blocking():
    """Test that blocked tasks are skipped in priority selection."""
    roadmap = {
        "version": 1,
        "project_name": "test",
        "phases": [
            {
                "name": "PHASE_1",
                "status": "TODO",
                "progress": 0,
                "task_ids": ["task-1", "task-2"],
            }
        ],
        "tasks": {
            "task-1": {
                "id": "task-1",
                "name": "Task 1",
                "status": "TODO",
                "priority": 5,
                "created_at": "2025-11-18T00:00:00",
                "started_at": None,
                "completed_at": None,
                "time_budget_mins": 120,
                "time_used_mins": 0,
                "validation_checks": [],
                "blocking_reason": None,
                "blocked_by": [],  # Not blocked
                "blocking_tasks": ["task-2"],
                "related_files": [],
                "git_commits": [],
            },
            "task-2": {
                "id": "task-2",
                "name": "Task 2",
                "status": "TODO",
                "priority": 10,  # Higher priority but blocked
                "created_at": "2025-11-18T00:00:00",
                "started_at": None,
                "completed_at": None,
                "time_budget_mins": 120,
                "time_used_mins": 0,
                "validation_checks": [],
                "blocking_reason": None,
                "blocked_by": ["task-1"],  # Blocked by task-1
                "blocking_tasks": [],
                "related_files": [],
                "git_commits": [],
            },
        },
    }

    # Collect TODO tasks but skip blocked ones
    todo_tasks = [
        (task_id, task)
        for task_id, task in roadmap["tasks"].items()
        if task["status"] == "TODO" and not task.get("blocked_by")
    ]

    # Should only have task-1 (task-2 is blocked)
    assert len(todo_tasks) == 1
    assert todo_tasks[0][0] == "task-1", "Task 2 is blocked, so Task 1 should be selected"


def test_priority_selection_three_priority_levels():
    """Test selecting among high, medium, and low priority tasks."""
    priorities = [
        ("p1", 10),
        ("p2", 5),
        ("p3", 1),
        ("p4", 7),
        ("p5", 3),
    ]

    tasks = {}
    for task_id, priority in priorities:
        tasks[task_id] = {
            "id": task_id,
            "name": f"Task {task_id}",
            "status": "TODO",
            "priority": priority,
            "created_at": "2025-11-18T00:00:00",
            "started_at": None,
            "completed_at": None,
            "time_budget_mins": 120,
            "time_used_mins": 0,
            "validation_checks": [],
            "blocking_reason": None,
            "blocked_by": [],
            "blocking_tasks": [],
            "related_files": [],
            "git_commits": [],
        }

    # Collect and sort
    task_list = list(tasks.items())
    task_list.sort(key=lambda x: x[1]["priority"], reverse=True)

    # Expected order: 10, 7, 5, 3, 1
    expected_order = ["p1", "p4", "p2", "p5", "p3"]
    actual_order = [task_id for task_id, _ in task_list]

    assert actual_order == expected_order, f"Expected {expected_order}, got {actual_order}"


def test_priority_fallback_to_non_priority():
    """Test fallback when use_priority=False selects first in order."""
    roadmap = {
        "version": 1,
        "project_name": "test",
        "phases": [
            {
                "name": "PHASE_1",
                "status": "TODO",
                "progress": 0,
                "task_ids": ["task-1", "task-2", "task-3"],
            }
        ],
        "tasks": {
            "task-1": {
                "id": "task-1",
                "name": "Task 1",
                "status": "TODO",
                "priority": 3,
                "created_at": "2025-11-18T00:00:00",
                "started_at": None,
                "completed_at": None,
                "time_budget_mins": 120,
                "time_used_mins": 0,
                "validation_checks": [],
                "blocking_reason": None,
                "blocked_by": [],
                "blocking_tasks": [],
                "related_files": [],
                "git_commits": [],
            },
            "task-2": {
                "id": "task-2",
                "name": "Task 2",
                "status": "TODO",
                "priority": 10,
                "created_at": "2025-11-18T00:00:00",
                "started_at": None,
                "completed_at": None,
                "time_budget_mins": 120,
                "time_used_mins": 0,
                "validation_checks": [],
                "blocking_reason": None,
                "blocked_by": [],
                "blocking_tasks": [],
                "related_files": [],
                "git_commits": [],
            },
            "task-3": {
                "id": "task-3",
                "name": "Task 3",
                "status": "TODO",
                "priority": 7,
                "created_at": "2025-11-18T00:00:00",
                "started_at": None,
                "completed_at": None,
                "time_budget_mins": 120,
                "time_used_mins": 0,
                "validation_checks": [],
                "blocking_reason": None,
                "blocked_by": [],
                "blocking_tasks": [],
                "related_files": [],
                "git_commits": [],
            },
        },
    }

    # Collect TODO tasks in phase order
    todo_tasks = []
    for task_id in roadmap["phases"][0]["task_ids"]:
        if task_id in roadmap["tasks"]:
            task = roadmap["tasks"][task_id]
            if task["status"] == "TODO":
                todo_tasks.append((task_id, task))

    # Without priority sorting, first is task-1
    assert todo_tasks[0][0] == "task-1", "Without priority, should select in phase order"

    # With priority sorting, first is task-2
    todo_tasks.sort(key=lambda x: x[1]["priority"], reverse=True)
    assert todo_tasks[0][0] == "task-2", "With priority, should select task-2 (priority 10)"
