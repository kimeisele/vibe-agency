#!/usr/bin/env python3
"""Bootstrap Phase 3 (ADVANCED_CAPABILITIES) into roadmap"""

import json
from datetime import datetime
from pathlib import Path

import yaml

vibe_root = Path(__file__).parent.parent
state_file = vibe_root / '.vibe' / 'state' / 'active_mission.json'
roadmap_file = vibe_root / '.vibe' / 'config' / 'roadmap.yaml'

# Load current state
with open(roadmap_file) as f:
    roadmap = yaml.safe_load(f)

with open(state_file) as f:
    mission = json.load(f)

# Add Phase 3
phase3 = {
    'name': 'ADVANCED_CAPABILITIES',
    'status': 'TODO',
    'progress': 0,
    'task_ids': ['task-007', 'task-008', 'task-009']
}

roadmap['phases'].append(phase3)

# Task 7: Reporting Engine
task7 = {
    'version': 1,
    'id': 'task-007',
    'name': 'REPORTING_ENGINE',
    'description': 'Multi-format export engine - JSON, CSV, Markdown reports',
    'status': 'TODO',
    'priority': 9,
    'created_at': datetime.now().isoformat(),
    'started_at': None,
    'completed_at': None,
    'time_budget_mins': 120,
    'time_used_mins': 0,
    'validation_checks': [
        {
            'id': 'export_logic',
            'description': 'Export engine supports JSON/CSV/Markdown formats',
            'validator': 'validate_files_exist',
            'params': {},
            'status': False,
            'last_check': None,
            'error': None
        },
        {
            'id': 'export_tests',
            'description': 'Export tests passing',
            'validator': 'validate_tests_passing',
            'params': {},
            'status': False,
            'last_check': None,
            'error': None
        }
    ],
    'blocking_reason': None,
    'blocked_by': [],
    'blocking_tasks': [],
    'related_files': [],
    'git_commits': []
}

# Task 8: Batch Operations
task8 = {
    'version': 1,
    'id': 'task-008',
    'name': 'BATCH_OPERATIONS',
    'description': 'Batch operations - start/update/complete multiple tasks',
    'status': 'TODO',
    'priority': 8,
    'created_at': datetime.now().isoformat(),
    'started_at': None,
    'completed_at': None,
    'time_budget_mins': 120,
    'time_used_mins': 0,
    'validation_checks': [
        {
            'id': 'batch_logic',
            'description': 'Batch operations implemented (start, update, complete)',
            'validator': 'validate_files_exist',
            'params': {},
            'status': False,
            'last_check': None,
            'error': None
        },
        {
            'id': 'batch_tests',
            'description': 'Batch operation tests passing',
            'validator': 'validate_tests_passing',
            'params': {},
            'status': False,
            'last_check': None,
            'error': None
        }
    ],
    'blocking_reason': None,
    'blocked_by': [],
    'blocking_tasks': [],
    'related_files': [],
    'git_commits': []
}

# Task 9: Archive & History
task9 = {
    'version': 1,
    'id': 'task-009',
    'name': 'ARCHIVE_AND_HISTORY',
    'description': 'Task archival system - persist completed task snapshots',
    'status': 'TODO',
    'priority': 7,
    'created_at': datetime.now().isoformat(),
    'started_at': None,
    'completed_at': None,
    'time_budget_mins': 120,
    'time_used_mins': 0,
    'validation_checks': [
        {
            'id': 'archive_logic',
            'description': 'Archive system for completed tasks',
            'validator': 'validate_files_exist',
            'params': {},
            'status': False,
            'last_check': None,
            'error': None
        },
        {
            'id': 'archive_tests',
            'description': 'Archive system tests passing',
            'validator': 'validate_tests_passing',
            'params': {},
            'status': False,
            'last_check': None,
            'error': None
        }
    ],
    'blocking_reason': None,
    'blocked_by': [],
    'blocking_tasks': [],
    'related_files': [],
    'git_commits': []
}

# Add tasks to roadmap
roadmap['tasks']['task-007'] = task7
roadmap['tasks']['task-008'] = task8
roadmap['tasks']['task-009'] = task9

# Update mission to have first Phase 3 task
mission['current_task'] = task7
mission['current_phase'] = 'ADVANCED_CAPABILITIES'
mission['last_updated'] = datetime.now().isoformat()

# Save
with open(roadmap_file, 'w') as f:
    yaml.dump(roadmap, f, default_flow_style=False, sort_keys=False)

with open(state_file, 'w') as f:
    json.dump(mission, f, indent=2)

print("=" * 70)
print("🚀 PHASE 3 BOOTSTRAP COMPLETE: ADVANCED_CAPABILITIES")
print("=" * 70)
print()
print("✅ Phase 3 Added to Roadmap (3 new tasks)")
print()
print("📋 New Tasks:")
print("  • Task 7: REPORTING_ENGINE - Multi-format export (JSON/CSV/MD)")
print("  • Task 8: BATCH_OPERATIONS - Start/complete multiple tasks")
print("  • Task 9: ARCHIVE_AND_HISTORY - Task persistence & snapshots")
print()
print("🎯 Next Task: Task 7 - REPORTING_ENGINE")
print("=" * 70)
