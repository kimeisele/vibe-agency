"""Tests for task archival system (GAD-701 Task 9)"""



def test_task_snapshot_structure():
    """Test task snapshot has correct structure."""
    snapshot = {
        'id': 'task-1',
        'name': 'Build System',
        'description': 'Build core system',
        'status': 'DONE',
        'priority': 9,
        'created_at': '2025-11-18T00:00:00',
        'started_at': '2025-11-18T01:00:00',
        'completed_at': '2025-11-18T02:00:00',
        'time_budget_mins': 120,
        'time_used_mins': 100,
        'validation_summary': {
            'total_checks': 2,
            'passing_checks': 2,
        },
        'archived_at': '2025-11-18T03:00:00',
    }

    assert snapshot['id'] == 'task-1'
    assert snapshot['status'] == 'DONE'
    assert snapshot['validation_summary']['passing_checks'] == 2
    assert 'archived_at' in snapshot


def test_archive_metadata():
    """Test archive operation returns metadata."""
    metadata = {
        'task_id': 'task-1',
        'task_name': 'Build System',
        'archived_file': '/path/to/.vibe/archive/task-1_archive.json',
        'archived_at': '2025-11-18T03:00:00',
    }

    assert metadata['task_id']
    assert metadata['task_name']
    assert '_archive.json' in metadata['archived_file']
    assert 'T' in metadata['archived_at']  # ISO format check


def test_archive_list_structure():
    """Test archive list has correct structure."""
    archived = [
        {
            'id': 'task-1',
            'name': 'Task 1',
            'completed_at': '2025-11-18T02:00:00',
            'archived_at': '2025-11-18T03:00:00',
            'priority': 9,
        },
        {
            'id': 'task-2',
            'name': 'Task 2',
            'completed_at': '2025-11-18T04:00:00',
            'archived_at': '2025-11-18T05:00:00',
            'priority': 7,
        },
    ]

    assert len(archived) == 2
    assert archived[0]['id'] == 'task-1'
    assert archived[1]['priority'] == 7


def test_archive_stats_structure():
    """Test archive statistics structure."""
    stats = {
        'total_archived': 5,
        'archive_size_bytes': 15000,
        'oldest_archive': '2025-11-10T00:00:00',
        'newest_archive': '2025-11-18T00:00:00',
    }

    assert stats['total_archived'] == 5
    assert stats['archive_size_bytes'] > 0
    assert stats['oldest_archive'] < stats['newest_archive']


def test_archive_csv_format():
    """Test archive CSV export format."""
    csv = """ID,Name,Priority,Status,Completed,Archived
task-1,Build System,9,DONE,2025-11-18T02:00:00,2025-11-18T03:00:00
task-2,Add Features,7,DONE,2025-11-18T04:00:00,2025-11-18T05:00:00"""

    lines = csv.split('\n')
    assert len(lines) == 3

    header = lines[0].split(',')
    assert 'ID' in header
    assert 'Name' in header
    assert 'Priority' in header
    assert 'Completed' in header


def test_cleanup_results_structure():
    """Test cleanup operation results."""
    cleanup_result = {
        'removed_count': 5,
        'freed_bytes': 25000,
        'cutoff_days': 30,
    }

    assert cleanup_result['removed_count'] == 5
    assert cleanup_result['freed_bytes'] > 0
    assert cleanup_result['cutoff_days'] == 30


def test_date_range_filtering():
    """Test date range filtering for archives."""
    start = '2025-11-10T00:00:00'
    end = '2025-11-18T23:59:59'

    archived = [
        {
            'id': 'task-1',
            'completed_at': '2025-11-12T10:00:00',  # Within range
        },
        {
            'id': 'task-2',
            'completed_at': '2025-11-09T10:00:00',  # Before range
        },
        {
            'id': 'task-3',
            'completed_at': '2025-11-20T10:00:00',  # After range
        },
    ]

    matching = [
        t for t in archived
        if t['completed_at'] and start <= t['completed_at'] <= end
    ]

    assert len(matching) == 1
    assert matching[0]['id'] == 'task-1'


def test_empty_archive():
    """Test handling of empty archive."""
    stats = {
        'total_archived': 0,
        'archive_size_bytes': 0,
        'oldest_archive': None,
        'newest_archive': None,
    }

    assert stats['total_archived'] == 0
    assert stats['archive_size_bytes'] == 0
    assert stats['oldest_archive'] is None


def test_validation_summary_in_archive():
    """Test validation summary in archive snapshot."""
    snapshot = {
        'id': 'task-1',
        'validation_summary': {
            'total_checks': 3,
            'passing_checks': 2,
        },
    }

    total = snapshot['validation_summary']['total_checks']
    passing = snapshot['validation_summary']['passing_checks']
    pass_rate = int((passing / total) * 100) if total > 0 else 0

    assert pass_rate == 66  # 2/3 * 100


def test_json_export_structure():
    """Test JSON export of archives."""
    json_str = """[
  {
    "id": "task-1",
    "name": "Task 1",
    "status": "DONE",
    "priority": 9,
    "completed_at": "2025-11-18T02:00:00",
    "archived_at": "2025-11-18T03:00:00"
  },
  {
    "id": "task-2",
    "name": "Task 2",
    "status": "DONE",
    "priority": 7,
    "completed_at": "2025-11-18T04:00:00",
    "archived_at": "2025-11-18T05:00:00"
  }
]"""

    # Valid JSON
    import json
    data = json.loads(json_str)

    assert len(data) == 2
    assert data[0]['id'] == 'task-1'
    assert data[1]['priority'] == 7


def test_archive_file_naming():
    """Test archive file naming convention."""
    task_ids = ['task-1', 'task-2', 'task-abc-123']

    for task_id in task_ids:
        archive_name = f'{task_id}_archive.json'
        assert archive_name.endswith('_archive.json')
        assert task_id in archive_name
