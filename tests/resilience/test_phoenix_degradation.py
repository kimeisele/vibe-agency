"""
GAD-100: Operation Phoenix - Resilience Verification.

Tests that the system degrades gracefully when the persistence layer fails.
"""

import os
import tempfile

import pytest

from vibe_core.ledger import VibeLedger
from vibe_core.scheduling import Task


class TestPhoenixDegradation:
    """Test suite for system resilience and graceful degradation."""

    def test_normal_boot(self):
        """Test that ledger initializes normally with valid path."""
        with tempfile.NamedTemporaryFile(suffix=".db") as tmp:
            ledger = VibeLedger(db_path=tmp.name)
            assert ledger.db_path == tmp.name
            assert ledger.conn is not None

            # Verify operations work
            task = Task(agent_id="test", payload={})
            ledger.record_start(task)
            record = ledger.get_task(task.id)
            assert record is not None
            assert record["status"] == "STARTED"
            ledger.close()

    def test_degraded_boot_on_failure(self):
        """Test that ledger falls back to memory when path is invalid."""
        # Create a directory where the DB file should be
        # This will cause sqlite3.connect to fail with IsADirectoryError (or similar)
        with tempfile.TemporaryDirectory() as tmp_dir:
            bad_path = os.path.join(tmp_dir, "bad_db_location")
            os.makedirs(bad_path)  # It's a directory!

            # Attempt to initialize ledger with directory path
            # Should log warning and fallback to :memory:
            ledger = VibeLedger(db_path=bad_path)

            # Assert fallback occurred
            assert ledger.db_path == ":memory:"

            # Assert system is still functional
            task = Task(agent_id="phoenix-test", payload={"data": "survival"})
            ledger.record_start(task)

            record = ledger.get_task(task.id)
            assert record is not None
            assert record["status"] == "STARTED"
            assert record["agent_id"] == "phoenix-test"

            ledger.close()

    def test_degraded_boot_on_permission_error(self):
        """Test fallback on permission error."""
        # Skip on Windows or root execution where chmod might not work as expected
        if os.name == "nt" or os.geteuid() == 0:
            pytest.skip("Skipping permission test on Windows/Root")

        with tempfile.NamedTemporaryFile(suffix=".db") as tmp:
            # Make file unreadable/unwritable
            os.chmod(tmp.name, 0o000)

            try:
                ledger = VibeLedger(db_path=tmp.name)

                # Assert fallback occurred
                assert ledger.db_path == ":memory:"

                # Assert functionality
                task = Task(agent_id="permission-test", payload={})
                ledger.record_start(task)
                assert ledger.get_task(task.id) is not None

                ledger.close()
            finally:
                # Restore permissions to allow cleanup
                os.chmod(tmp.name, 0o666)
