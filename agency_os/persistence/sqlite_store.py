"""
SQLite persistence layer for vibe-agency (Schema v2)

Implements ARCH-002: SQLiteStore class with CRUD operations for:
- Missions (lifecycle tracking + budget + metadata)
- Tool calls (audit trail)
- Decisions (provenance)
- Playbook runs (metrics)
- Agent memory (context persistence)
- TODO: Session narrative, artifacts, quality gates (Part 2)

Schema: docs/tasks/ARCH-001_schema.sql (v2)
"""

import json
import os
import sqlite3
import threading
from pathlib import Path
from typing import Any


class SQLiteStore:
    """
    SQLite persistence layer for agent operations

    Features:
    - Auto-creates database on first use (zero-config)
    - Loads schema from ARCH-001_schema.sql
    - Thread-safe (check_same_thread=False)
    - Context manager support (with statement)
    - Row factory for dict-like access

    Usage:
        with SQLiteStore(".vibe/state/vibe_agency.db") as store:
            mission_id = store.create_mission("uuid-001", "PLANNING", "pending")
            store.log_tool_call(mission_id, "WebFetch", {...}, {...}, timestamp, 100, True)
    """

    def __init__(self, db_path: str = ":memory:"):
        """
        Initialize SQLiteStore

        Args:
            db_path: Path to SQLite database file (default: in-memory)

        Note:
            - If db_path is a file path and doesn't exist, it will be created
            - Schema is loaded automatically on first creation
            - Existing databases are opened without schema reload
        """
        self.db_path = db_path
        self.conn: sqlite3.Connection | None = None
        self._lock = threading.RLock()  # Reentrant lock for thread-safe access

        # Create parent directory if needed (for file-based DBs)
        if db_path != ":memory:":
            os.makedirs(os.path.dirname(db_path) or ".", exist_ok=True)

        # Connect to database (creates file if not exists)
        self.conn = sqlite3.connect(
            db_path,
            check_same_thread=False,  # Thread-safe
            isolation_level="DEFERRED",  # Use transactions for thread-safety
        )

        # Enable dict-like row access (row['column_name'])
        self.conn.row_factory = sqlite3.Row

        # Enable foreign key constraints (required for CASCADE DELETE)
        self.conn.execute("PRAGMA foreign_keys = ON")

        # Check if database is empty (needs schema)
        cursor = self.conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='missions'"
        )
        tables_exist = cursor.fetchone() is not None

        if not tables_exist:
            self._load_schema()

    def _load_schema(self):
        """
        Load schema from ARCH-001_schema.sql

        Dynamically locates schema file relative to project root.
        Executes all DDL statements to create tables, indexes, views, triggers.
        """
        # Find project root (contains docs/tasks/ARCH-001_schema.sql)
        current_dir = Path(__file__).resolve()
        project_root = current_dir

        # Walk up directories to find project root (has docs/tasks/)
        while project_root != project_root.parent:
            schema_path = project_root / "docs" / "tasks" / "ARCH-001_schema.sql"
            if schema_path.exists():
                break
            project_root = project_root.parent
        else:
            raise FileNotFoundError("Could not find docs/tasks/ARCH-001_schema.sql in project tree")

        # Load and execute schema
        with open(schema_path) as f:
            schema_sql = f.read()
            self.conn.executescript(schema_sql)
            self.conn.commit()

    def _commit(self):
        """Commit transaction (for thread-safe writes)"""
        if self.conn:
            self.conn.commit()

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            self.conn = None

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit (auto-close connection)"""
        self.close()

    # ========================================================================
    # MISSION CRUD
    # ========================================================================

    def _map_manifest_to_missions_row(self, manifest: dict[str, Any]) -> dict[str, Any]:
        """
        Adapter: Convert project_manifest.json to missions table row (v2)

        This is the core adapter logic from SCHEMA_REALITY_CHECK.md Section 6.1.
        Extracts budget, metadata, and nested fields from project_manifest.json
        and flattens them into missions table columns.

        Args:
            manifest: project_manifest.json dict

        Returns:
            Dict with missions table columns (ready for create_mission(**kwargs))

        Example:
            manifest = json.load(open('workspaces/proj/project_manifest.json'))
            missions_row = store._map_manifest_to_missions_row(manifest)
            mission_id = store.create_mission(**missions_row)
        """
        metadata_section = manifest.get("metadata", {})
        status_section = manifest.get("status", {})
        budget_section = manifest.get("budget", {})

        # Extract metadata fields for queryability
        mission_uuid = metadata_section.get("projectId", "unknown")
        owner = metadata_section.get("owner")
        description = metadata_section.get("description")
        api_version = manifest.get("apiVersion", "agency.os/v1alpha1")

        # Extract status fields
        phase = status_section.get("projectPhase", "PLANNING")
        planning_sub_state = status_section.get("planningSubState")

        # Infer status from phase (Reality Check requirement)
        # If completed_at exists → completed, else in_progress
        completed_at = status_section.get("completedAt")
        if completed_at:
            status = "completed"
        elif phase == "PRODUCTION":
            status = "completed"
        else:
            status = "in_progress"

        # Timestamps
        created_at = metadata_section.get("createdAt")
        updated_at = metadata_section.get("lastUpdatedAt")

        # Budget tracking
        max_cost_usd = budget_section.get("max_cost_usd")
        current_cost_usd = budget_section.get("current_cost_usd", 0.0)
        alert_threshold = budget_section.get("alert_threshold", 0.80)
        cost_breakdown = budget_section.get("cost_breakdown")

        # Store remaining data in metadata JSON
        # (spec, artifacts will be handled by dedicated tables in Part 2)
        metadata_json = {
            "spec": manifest.get("spec"),
            "kind": manifest.get("kind"),
            # Store artifacts reference (Part 2 will extract to artifacts table)
            "artifacts": manifest.get("artifacts"),
        }

        return {
            "mission_uuid": mission_uuid,
            "phase": phase,
            "status": status,
            "created_at": created_at,
            "completed_at": completed_at,
            "updated_at": updated_at,
            "planning_sub_state": planning_sub_state,
            "max_cost_usd": max_cost_usd,
            "current_cost_usd": current_cost_usd,
            "alert_threshold": alert_threshold,
            "cost_breakdown": cost_breakdown,
            "owner": owner,
            "description": description,
            "api_version": api_version,
            "metadata": metadata_json,
        }

    def create_mission(
        self,
        mission_uuid: str,
        phase: str,
        status: str,
        created_at: str = None,
        completed_at: str | None = None,
        updated_at: str | None = None,
        planning_sub_state: str | None = None,
        max_cost_usd: float | None = None,
        current_cost_usd: float = 0.0,
        alert_threshold: float = 0.80,
        cost_breakdown: dict[str, Any] | None = None,
        owner: str | None = None,
        description: str | None = None,
        api_version: str = "agency.os/v1alpha1",
        metadata: dict[str, Any] | None = None,
    ) -> int:
        """
        Create a new mission (Schema v2)

        Args:
            mission_uuid: External UUID identifier
            phase: SDLC phase (PLANNING, CODING, TESTING, DEPLOYMENT, MAINTENANCE)
            status: Mission status (pending, in_progress, completed, failed)
            created_at: ISO 8601 timestamp (optional, defaults to now)
            completed_at: ISO 8601 completion timestamp (optional)
            updated_at: ISO 8601 last update timestamp (optional)
            planning_sub_state: Planning sub-state (RESEARCH, BUSINESS_VALIDATION, FEATURE_SPECIFICATION)
            max_cost_usd: Maximum budget for mission (optional)
            current_cost_usd: Current spend (default: 0.0)
            alert_threshold: Budget alert threshold 0.0-1.0 (default: 0.80)
            cost_breakdown: Cost breakdown by phase/agent as dict (optional)
            owner: Mission owner (e.g., 'agent@vibe.agency')
            description: Human-readable description
            api_version: Manifest API version (default: 'agency.os/v1alpha1')
            metadata: Additional mission data as dict (optional)

        Returns:
            mission_id: Auto-incremented integer ID
        """
        if created_at is None:
            from datetime import datetime

            created_at = datetime.utcnow().isoformat() + "Z"

        with self._lock:
            cursor = self.conn.execute(
                """
                INSERT INTO missions (
                    mission_uuid, phase, status, created_at, completed_at, updated_at,
                    planning_sub_state,
                    max_cost_usd, current_cost_usd, alert_threshold, cost_breakdown,
                    owner, description, api_version,
                    metadata
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    mission_uuid,
                    phase,
                    status,
                    created_at,
                    completed_at,
                    updated_at,
                    planning_sub_state,
                    max_cost_usd,
                    current_cost_usd,
                    alert_threshold,
                    json.dumps(cost_breakdown) if cost_breakdown else None,
                    owner,
                    description,
                    api_version,
                    json.dumps(metadata) if metadata else None,
                ),
            )
            self._commit()
            return cursor.lastrowid

    def _parse_mission_row(self, row: sqlite3.Row) -> dict[str, Any]:
        """
        Parse mission row and deserialize JSON fields

        Args:
            row: SQLite row

        Returns:
            Mission dict with parsed JSON fields
        """
        mission = dict(row)
        # Parse JSON fields (v2)
        if mission.get("metadata"):
            mission["metadata"] = json.loads(mission["metadata"])
        if mission.get("cost_breakdown"):
            mission["cost_breakdown"] = json.loads(mission["cost_breakdown"])
        return mission

    def get_mission(self, mission_id: int) -> dict[str, Any] | None:
        """
        Get mission by ID

        Args:
            mission_id: Integer ID

        Returns:
            Mission dict or None if not found
        """
        cursor = self.conn.execute("SELECT * FROM missions WHERE id = ?", (mission_id,))
        row = cursor.fetchone()
        if row is None:
            return None

        return self._parse_mission_row(row)

    def get_mission_by_uuid(self, mission_uuid: str) -> dict[str, Any] | None:
        """
        Get mission by UUID

        Args:
            mission_uuid: External UUID string

        Returns:
            Mission dict or None if not found
        """
        cursor = self.conn.execute("SELECT * FROM missions WHERE mission_uuid = ?", (mission_uuid,))
        row = cursor.fetchone()
        if row is None:
            return None

        return self._parse_mission_row(row)

    def update_mission_status(self, mission_id: int, status: str, completed_at: str | None = None):
        """
        Update mission status

        Args:
            mission_id: Integer ID
            status: New status (pending, in_progress, completed, failed)
            completed_at: ISO 8601 timestamp (optional)
        """
        self.conn.execute(
            "UPDATE missions SET status = ?, completed_at = ? WHERE id = ?",
            (status, completed_at, mission_id),
        )
        self._commit()

    def get_mission_history(self) -> list[dict[str, Any]]:
        """
        Get all missions (history)

        Returns:
            List of mission dicts, ordered by created_at DESC
        """
        cursor = self.conn.execute("SELECT * FROM missions ORDER BY created_at DESC")
        return [self._parse_mission_row(row) for row in cursor.fetchall()]

    def get_all_missions(self) -> list[dict[str, Any]]:
        """Alias for get_mission_history()"""
        return self.get_mission_history()

    def delete_mission(self, mission_id: int):
        """
        Delete mission (CASCADE DELETE removes related records)

        Args:
            mission_id: Integer ID
        """
        self.conn.execute("DELETE FROM missions WHERE id = ?", (mission_id,))
        self._commit()

    # ========================================================================
    # v2: MISSION BUDGET OPERATIONS
    # ========================================================================

    def update_mission_budget(
        self,
        mission_id: int,
        current_cost_usd: float | None = None,
        max_cost_usd: float | None = None,
        alert_threshold: float | None = None,
        cost_breakdown: dict[str, Any] | None = None,
    ):
        """
        Update mission budget fields (v2)

        Args:
            mission_id: Mission ID
            current_cost_usd: New current cost (optional)
            max_cost_usd: New max budget (optional)
            alert_threshold: New alert threshold (optional)
            cost_breakdown: New cost breakdown dict (optional)
        """
        updates = []
        params = []

        if current_cost_usd is not None:
            updates.append("current_cost_usd = ?")
            params.append(current_cost_usd)

        if max_cost_usd is not None:
            updates.append("max_cost_usd = ?")
            params.append(max_cost_usd)

        if alert_threshold is not None:
            updates.append("alert_threshold = ?")
            params.append(alert_threshold)

        if cost_breakdown is not None:
            updates.append("cost_breakdown = ?")
            params.append(json.dumps(cost_breakdown))

        if not updates:
            return  # Nothing to update

        params.append(mission_id)
        sql = f"UPDATE missions SET {', '.join(updates)} WHERE id = ?"
        self.conn.execute(sql, params)
        self._commit()

    def get_missions_over_budget(self) -> list[dict[str, Any]]:
        """
        Get missions that exceed their budget (v2)

        Returns:
            List of mission dicts where current_cost_usd > max_cost_usd
        """
        cursor = self.conn.execute(
            """
            SELECT * FROM missions
            WHERE max_cost_usd IS NOT NULL
              AND current_cost_usd > max_cost_usd
            ORDER BY created_at DESC
        """
        )
        return [self._parse_mission_row(row) for row in cursor.fetchall()]

    def get_missions_by_owner(self, owner: str) -> list[dict[str, Any]]:
        """
        Get missions by owner (v2)

        Args:
            owner: Owner identifier (e.g., 'agent@vibe.agency')

        Returns:
            List of mission dicts owned by specified owner
        """
        cursor = self.conn.execute(
            "SELECT * FROM missions WHERE owner = ? ORDER BY created_at DESC",
            (owner,),
        )
        return [self._parse_mission_row(row) for row in cursor.fetchall()]

    # ========================================================================
    # TOOL CALL LOGGING
    # ========================================================================

    def log_tool_call(
        self,
        mission_id: int,
        tool_name: str,
        args: dict[str, Any],
        result: dict[str, Any] | None,
        timestamp: str,
        duration_ms: int,
        success: bool,
        error_message: str | None = None,
    ) -> int:
        """
        Log tool execution

        Args:
            mission_id: Parent mission ID
            tool_name: Tool name (e.g., 'WebFetch', 'Bash')
            args: Tool arguments as dict
            result: Tool result as dict (None if error)
            timestamp: ISO 8601 timestamp
            duration_ms: Execution time in milliseconds
            success: True if successful, False if error
            error_message: Error details (optional)

        Returns:
            tool_call_id: Auto-incremented ID
        """
        cursor = self.conn.execute(
            """
            INSERT INTO tool_calls
            (mission_id, tool_name, args, result, timestamp, duration_ms, success, error_message)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                mission_id,
                tool_name,
                json.dumps(args),
                json.dumps(result) if result else None,
                timestamp,
                duration_ms,
                1 if success else 0,
                error_message,
            ),
        )
        self._commit()
        return cursor.lastrowid

    def get_tool_call(self, tool_call_id: int) -> dict[str, Any] | None:
        """Get tool call by ID"""
        cursor = self.conn.execute("SELECT * FROM tool_calls WHERE id = ?", (tool_call_id,))
        row = cursor.fetchone()
        if row is None:
            return None

        tool_call = dict(row)
        # Parse JSON fields
        if tool_call.get("args"):
            tool_call["args"] = json.loads(tool_call["args"])
        if tool_call.get("result"):
            tool_call["result"] = json.loads(tool_call["result"])
        return tool_call

    def get_tool_calls_for_mission(self, mission_id: int) -> list[dict[str, Any]]:
        """
        Get all tool calls for a mission

        Args:
            mission_id: Parent mission ID

        Returns:
            List of tool call dicts, ordered by timestamp
        """
        cursor = self.conn.execute(
            "SELECT * FROM tool_calls WHERE mission_id = ? ORDER BY timestamp",
            (mission_id,),
        )
        tool_calls = []
        for row in cursor.fetchall():
            tool_call = dict(row)
            if tool_call.get("args"):
                tool_call["args"] = json.loads(tool_call["args"])
            if tool_call.get("result"):
                tool_call["result"] = json.loads(tool_call["result"])
            tool_calls.append(tool_call)
        return tool_calls

    # ========================================================================
    # DECISION PROVENANCE
    # ========================================================================

    def record_decision(
        self,
        mission_id: int,
        decision_type: str,
        rationale: str,
        timestamp: str,
        agent_name: str,
        context: dict[str, Any] | None = None,
    ) -> int:
        """
        Record agent decision

        Args:
            mission_id: Parent mission ID
            decision_type: Type of decision (e.g., 'architecture_choice', 'tool_selection')
            rationale: Human-readable explanation
            timestamp: ISO 8601 timestamp
            agent_name: Agent that made decision (e.g., 'STEWARD')
            context: Additional context as dict (optional)

        Returns:
            decision_id: Auto-incremented ID
        """
        cursor = self.conn.execute(
            """
            INSERT INTO decisions
            (mission_id, decision_type, rationale, timestamp, agent_name, context)
            VALUES (?, ?, ?, ?, ?, ?)
        """,
            (
                mission_id,
                decision_type,
                rationale,
                timestamp,
                agent_name,
                json.dumps(context) if context else None,
            ),
        )
        self._commit()
        return cursor.lastrowid

    def get_decisions_for_mission(self, mission_id: int) -> list[dict[str, Any]]:
        """
        Get all decisions for a mission

        Args:
            mission_id: Parent mission ID

        Returns:
            List of decision dicts, ordered by timestamp
        """
        cursor = self.conn.execute(
            "SELECT * FROM decisions WHERE mission_id = ? ORDER BY timestamp",
            (mission_id,),
        )
        decisions = []
        for row in cursor.fetchall():
            decision = dict(row)
            if decision.get("context"):
                decision["context"] = json.loads(decision["context"])
            decisions.append(decision)
        return decisions

    # ========================================================================
    # AGENT MEMORY
    # ========================================================================

    def set_memory(
        self,
        mission_id: int,
        key: str,
        value: Any,
        timestamp: str,
        ttl: int | None = None,
    ):
        """
        Set agent memory (key-value storage)

        Args:
            mission_id: Parent mission ID
            key: Memory key
            value: Memory value (will be JSON-serialized)
            timestamp: ISO 8601 timestamp
            ttl: Time-to-live in seconds (optional)

        Note:
            If key already exists for mission, it will be updated (UPSERT)
        """
        # Check if key exists
        cursor = self.conn.execute(
            "SELECT id FROM agent_memory WHERE mission_id = ? AND key = ?",
            (mission_id, key),
        )
        existing = cursor.fetchone()

        if existing:
            # Update existing
            self.conn.execute(
                """
                UPDATE agent_memory
                SET value = ?, timestamp = ?, ttl = ?
                WHERE mission_id = ? AND key = ?
            """,
                (json.dumps(value), timestamp, ttl, mission_id, key),
            )
        else:
            # Insert new
            self.conn.execute(
                """
                INSERT INTO agent_memory (mission_id, key, value, timestamp, ttl)
                VALUES (?, ?, ?, ?, ?)
            """,
                (mission_id, key, json.dumps(value), timestamp, ttl),
            )
        self._commit()

    def get_memory(self, mission_id: int, key: str) -> dict[str, Any] | None:
        """
        Get agent memory by key

        Args:
            mission_id: Parent mission ID
            key: Memory key

        Returns:
            Memory dict or None if not found
        """
        cursor = self.conn.execute(
            "SELECT * FROM agent_memory WHERE mission_id = ? AND key = ?",
            (mission_id, key),
        )
        row = cursor.fetchone()
        if row is None:
            return None

        memory = dict(row)
        if memory.get("value"):
            memory["value"] = json.loads(memory["value"])
        return memory

    # ========================================================================
    # PLAYBOOK RUNS
    # ========================================================================

    def create_playbook_run(
        self,
        mission_id: int,
        playbook_name: str,
        phase: str,
        started_at: str,
    ) -> int:
        """
        Create playbook run record

        Args:
            mission_id: Parent mission ID
            playbook_name: Playbook identifier (e.g., 'research.analyze_topic')
            phase: SDLC phase (PLANNING, CODING, etc.)
            started_at: ISO 8601 timestamp

        Returns:
            run_id: Auto-incremented ID
        """
        cursor = self.conn.execute(
            """
            INSERT INTO playbook_runs (mission_id, playbook_name, phase, started_at)
            VALUES (?, ?, ?, ?)
        """,
            (mission_id, playbook_name, phase, started_at),
        )
        self._commit()
        return cursor.lastrowid

    def complete_playbook_run(
        self,
        run_id: int,
        completed_at: str,
        success: bool,
        metrics: dict[str, Any] | None = None,
    ):
        """
        Complete playbook run with metrics

        Args:
            run_id: Playbook run ID
            completed_at: ISO 8601 timestamp
            success: True if successful, False if failed
            metrics: Execution metrics as dict (optional)
        """
        self.conn.execute(
            """
            UPDATE playbook_runs
            SET completed_at = ?, success = ?, metrics = ?
            WHERE id = ?
        """,
            (completed_at, 1 if success else 0, json.dumps(metrics) if metrics else None, run_id),
        )
        self._commit()

    def get_playbook_run(self, run_id: int) -> dict[str, Any] | None:
        """Get playbook run by ID"""
        cursor = self.conn.execute("SELECT * FROM playbook_runs WHERE id = ?", (run_id,))
        row = cursor.fetchone()
        if row is None:
            return None

        run = dict(row)
        if run.get("metrics"):
            run["metrics"] = json.loads(run["metrics"])
        return run

    # ========================================================================
    # LEGACY MIGRATION (ARCH-003)
    # ========================================================================

    def import_legacy_mission(self, json_data: dict[str, Any]) -> int | None:
        """
        Import legacy mission from active_mission.json

        Args:
            json_data: Mission data from JSON file

        Returns:
            mission_id if imported, None if already exists

        This method provides backward compatibility for JSON-based missions.
        If the mission already exists in the database (by UUID), it will NOT
        be imported again (idempotent).
        """
        mission_uuid = json_data.get("mission_id", "unknown")

        # Check if mission already exists (idempotent)
        existing = self.get_mission_by_uuid(mission_uuid)
        if existing:
            return None  # Already imported

        # Extract mission data
        phase = json_data.get("context", {}).get("phase", "PLANNING")

        # Map legacy status to schema-compliant status
        legacy_status = json_data.get("status", "active")
        status_mapping = {
            "active": "in_progress",
            "pending": "pending",
            "in_progress": "in_progress",
            "completed": "completed",
            "failed": "failed",
        }
        status = status_mapping.get(legacy_status, "in_progress")

        created_at = json_data.get("created_at", json_data.get("genesis_time"))

        # Store full JSON as metadata (preserve everything)
        metadata = json_data

        # Create mission in database
        mission_id = self.create_mission(
            mission_uuid=mission_uuid,
            phase=phase,
            status=status,
            created_at=created_at,
            metadata=metadata,
        )

        return mission_id
