"""
Task Execution Ledger for vibe-agency OS.

This module implements the VibeLedger (ARCH-024), which provides
persistent storage of task execution history using SQLite.

The Ledger is the "Black Box" - it records every task execution
for observability, debugging, and crash recovery.
"""

import json
import logging
import sqlite3
from datetime import datetime
from typing import Any

from vibe_core.scheduling import Task

logger = logging.getLogger(__name__)


class VibeLedger:
    """
    SQLite-based task execution history ledger.

    The ledger records every task execution with full input/output
    data, timestamps, and status. This enables:
    - Observability: "What did the system do?"
    - Debugging: "Why did task X fail?"
    - Resumption: "Where were we before the crash?"
    - Auditing: "Which agent processed what?"

    Design Principles:
    - Write-ahead logging (every execution recorded)
    - Structured data (JSON serialization for complex payloads)
    - Failure-safe (recording errors never crashes kernel)
    - Queryable (SQL interface for analysis)

    Schema:
        task_history table:
        - task_id: Unique task identifier (TEXT PRIMARY KEY)
        - agent_id: Agent that processed the task (TEXT)
        - input_payload: Task payload as JSON (TEXT)
        - output_result: Agent result as JSON (TEXT, nullable)
        - status: COMPLETED, FAILED, or STARTED (TEXT)
        - error_message: Error details if FAILED (TEXT, nullable)
        - timestamp: Execution timestamp (TEXT, ISO format)
    """

    def __init__(self, db_path: str = "vibe_ledger.db"):
        """
        Initialize the ledger with SQLite database.

        Args:
            db_path: Path to SQLite database file. Use ":memory:"
                     for in-memory database (testing).

        Example:
            >>> ledger = VibeLedger("vibe_ledger.db")
            >>> # For testing:
            >>> test_ledger = VibeLedger(":memory:")
        """
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row  # Enable dict-like access
        self._initialize_schema()
        logger.info(f"LEDGER: Initialized (db_path={db_path})")

    def _initialize_schema(self) -> None:
        """Create task_history table if it doesn't exist."""
        cursor = self.conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS task_history (
                task_id TEXT PRIMARY KEY,
                agent_id TEXT NOT NULL,
                input_payload TEXT NOT NULL,
                output_result TEXT,
                status TEXT NOT NULL,
                error_message TEXT,
                timestamp TEXT NOT NULL
            )
        """
        )
        self.conn.commit()
        logger.debug("LEDGER: Schema initialized")

    def record_start(self, task: Task) -> None:
        """
        Record that a task has started execution.

        This creates an initial record with status STARTED.
        Use record_completion or record_failure to update the final state.

        Args:
            task: The Task that is starting

        Example:
            >>> ledger.record_start(task)
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                """
                INSERT OR REPLACE INTO task_history
                (task_id, agent_id, input_payload, status, timestamp)
                VALUES (?, ?, ?, ?, ?)
            """,
                (
                    task.id,
                    task.agent_id,
                    json.dumps(task.payload),
                    "STARTED",
                    datetime.utcnow().isoformat(),
                ),
            )
            self.conn.commit()
            logger.debug(f"LEDGER: Recorded START for task {task.id}")
        except Exception as e:
            logger.error(f"LEDGER: Failed to record start for task {task.id}: {e}")

    def record_completion(self, task: Task, result: Any) -> None:
        """
        Record successful task completion with result.

        Args:
            task: The Task that completed
            result: The result returned by agent.process()

        Example:
            >>> result = agent.process(task)
            >>> ledger.record_completion(task, result)

        Notes:
            - Result is JSON-serialized; non-serializable results are converted to str
            - Recording failures are logged but don't raise exceptions
        """
        try:
            # Serialize result (handle non-JSON-serializable types)
            try:
                result_json = json.dumps(result)
            except (TypeError, ValueError):
                result_json = json.dumps(str(result))

            cursor = self.conn.cursor()
            cursor.execute(
                """
                INSERT OR REPLACE INTO task_history
                (task_id, agent_id, input_payload, output_result, status, timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
                (
                    task.id,
                    task.agent_id,
                    json.dumps(task.payload),
                    result_json,
                    "COMPLETED",
                    datetime.utcnow().isoformat(),
                ),
            )
            self.conn.commit()
            logger.debug(f"LEDGER: Recorded COMPLETED for task {task.id}")
        except Exception as e:
            logger.error(f"LEDGER: Failed to record completion for task {task.id}: {e}")

    def record_failure(self, task: Task, error: str) -> None:
        """
        Record task failure with error message.

        Args:
            task: The Task that failed
            error: Error message or exception string

        Example:
            >>> try:
            ...     result = agent.process(task)
            ... except Exception as e:
            ...     ledger.record_failure(task, str(e))
            ...     raise

        Notes:
            - Recording failures are logged but don't raise exceptions
            - This ensures the ledger never causes a double-fault
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                """
                INSERT OR REPLACE INTO task_history
                (task_id, agent_id, input_payload, status, error_message, timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
                (
                    task.id,
                    task.agent_id,
                    json.dumps(task.payload),
                    "FAILED",
                    error,
                    datetime.utcnow().isoformat(),
                ),
            )
            self.conn.commit()
            logger.debug(f"LEDGER: Recorded FAILED for task {task.id}")
        except Exception as e:
            logger.error(f"LEDGER: Failed to record failure for task {task.id}: {e}")

    def get_history(
        self, limit: int = 10, status: str | None = None, agent_id: str | None = None
    ) -> list[dict[str, Any]]:
        """
        Retrieve recent task execution history.

        Args:
            limit: Maximum number of records to return (default: 10)
            status: Filter by status (COMPLETED, FAILED, STARTED), or None for all
            agent_id: Filter by agent_id, or None for all agents

        Returns:
            List of task history records as dictionaries

        Example:
            >>> # Get last 10 tasks
            >>> history = ledger.get_history(limit=10)
            >>>
            >>> # Get failed tasks only
            >>> failures = ledger.get_history(status="FAILED")
            >>>
            >>> # Get tasks for specific agent
            >>> agent_history = ledger.get_history(agent_id="echo-agent")
        """
        try:
            cursor = self.conn.cursor()

            # Build query with optional filters
            query = "SELECT * FROM task_history WHERE 1=1"
            params = []

            if status:
                query += " AND status = ?"
                params.append(status)

            if agent_id:
                query += " AND agent_id = ?"
                params.append(agent_id)

            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)

            cursor.execute(query, params)
            rows = cursor.fetchall()

            # Convert to list of dicts
            history = []
            for row in rows:
                record = dict(row)
                # Deserialize JSON fields
                if record["input_payload"]:
                    try:
                        record["input_payload"] = json.loads(record["input_payload"])
                    except json.JSONDecodeError:
                        pass  # Keep as string if invalid JSON

                if record["output_result"]:
                    try:
                        record["output_result"] = json.loads(record["output_result"])
                    except json.JSONDecodeError:
                        pass  # Keep as string if invalid JSON

                history.append(record)

            return history

        except Exception as e:
            logger.error(f"LEDGER: Failed to retrieve history: {e}")
            return []

    def get_task(self, task_id: str) -> dict[str, Any] | None:
        """
        Retrieve a specific task record by ID.

        Args:
            task_id: The task ID to look up

        Returns:
            Task record as dictionary, or None if not found

        Example:
            >>> record = ledger.get_task("task-123")
            >>> if record:
            ...     print(record["status"])  # "COMPLETED"
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM task_history WHERE task_id = ?", (task_id,))
            row = cursor.fetchone()

            if row:
                record = dict(row)
                # Deserialize JSON fields
                if record["input_payload"]:
                    try:
                        record["input_payload"] = json.loads(record["input_payload"])
                    except json.JSONDecodeError:
                        pass

                if record["output_result"]:
                    try:
                        record["output_result"] = json.loads(record["output_result"])
                    except json.JSONDecodeError:
                        pass

                return record

            return None

        except Exception as e:
            logger.error(f"LEDGER: Failed to retrieve task {task_id}: {e}")
            return None

    def get_statistics(self) -> dict[str, Any]:
        """
        Get aggregate statistics about task execution.

        Returns:
            Dictionary with statistics:
            - total_tasks: Total number of tasks recorded
            - completed: Number of completed tasks
            - failed: Number of failed tasks
            - started: Number of tasks still in STARTED state
            - agents: List of unique agent IDs

        Example:
            >>> stats = ledger.get_statistics()
            >>> print(f"Success rate: {stats['completed'] / stats['total_tasks']:.2%}")
        """
        try:
            cursor = self.conn.cursor()

            # Total tasks
            cursor.execute("SELECT COUNT(*) as count FROM task_history")
            total_tasks = cursor.fetchone()["count"]

            # By status
            cursor.execute("SELECT status, COUNT(*) as count FROM task_history GROUP BY status")
            status_counts = {row["status"]: row["count"] for row in cursor.fetchall()}

            # Unique agents
            cursor.execute("SELECT DISTINCT agent_id FROM task_history")
            agents = [row["agent_id"] for row in cursor.fetchall()]

            return {
                "total_tasks": total_tasks,
                "completed": status_counts.get("COMPLETED", 0),
                "failed": status_counts.get("FAILED", 0),
                "started": status_counts.get("STARTED", 0),
                "agents": agents,
            }

        except Exception as e:
            logger.error(f"LEDGER: Failed to retrieve statistics: {e}")
            return {
                "total_tasks": 0,
                "completed": 0,
                "failed": 0,
                "started": 0,
                "agents": [],
            }

    def close(self) -> None:
        """Close the database connection."""
        if self.conn:
            self.conn.close()
            logger.info("LEDGER: Database connection closed")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - ensures connection is closed."""
        self.close()
