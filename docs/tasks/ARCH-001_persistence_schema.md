# ARCH-001: Design SQLite Schema for Agent Operations

**Phase:** 0 (Persistence Foundation)
**Priority:** P0
**Estimated Time:** 90 minutes
**Dependencies:** None

---

## Objective

Design a normalized SQLite schema that supports:
- Mission lifecycle tracking
- Tool call audit trail
- Decision provenance
- Playbook execution metrics
- Agent memory/context persistence

---

## Acceptance Criteria

1. ✅ **Schema File Created**
   - `docs/tasks/ARCH-001_schema.sql` with 5 core tables

2. ✅ **Core Tables Defined**
   - `missions` - Mission lifecycle (id, phase, status, created_at, completed_at)
   - `tool_calls` - Tool execution audit (id, mission_id, tool_name, args, result, timestamp, duration_ms, success)
   - `decisions` - Agent decision provenance (id, mission_id, decision_type, rationale, timestamp, agent_name)
   - `playbook_runs` - Playbook execution metrics (id, mission_id, playbook_name, phase, started_at, completed_at, success)
   - `agent_memory` - Context persistence (id, mission_id, key, value, timestamp, ttl)

3. ✅ **Referential Integrity**
   - Foreign keys: `tool_calls.mission_id → missions.id`
   - Foreign keys: `decisions.mission_id → missions.id`
   - Foreign keys: `playbook_runs.mission_id → missions.id`
   - Foreign keys: `agent_memory.mission_id → missions.id`
   - Cascade deletes: Deleting mission removes all related records

4. ✅ **Performance Indexes**
   - Index on `missions.status` (for querying active missions)
   - Index on `tool_calls.mission_id, timestamp` (for audit queries)
   - Index on `decisions.mission_id, timestamp` (for decision history)
   - Index on `agent_memory.mission_id, key` (for context lookups)

5. ✅ **Migration Plan Documented**
   - `docs/tasks/ARCH-001_migration_plan.md` created
   - Strategy for JSON → SQLite transition
   - Backward compatibility approach
   - Schema versioning strategy (PRAGMA user_version)

---

## Schema Design Principles

### 1. Auditability
Every agent action must be traceable:
- **Who:** `agent_name` field in decisions/tool_calls
- **What:** `tool_name`, `decision_type`
- **When:** `timestamp` fields (ISO 8601 format)
- **Why:** `rationale` field in decisions
- **Outcome:** `result`, `success` fields

### 2. Queryability
Support debugging queries like:
```sql
-- "What tools did the planning phase use?"
SELECT tool_name, COUNT(*)
FROM tool_calls
JOIN missions ON tool_calls.mission_id = missions.id
WHERE missions.phase = 'PLANNING'
GROUP BY tool_name;

-- "Why did the agent make decision X?"
SELECT decision_type, rationale, timestamp
FROM decisions
WHERE mission_id = 'abc-123'
ORDER BY timestamp;

-- "Show me all failed tool calls in the last hour"
SELECT * FROM tool_calls
WHERE success = 0
  AND timestamp > datetime('now', '-1 hour');
```

### 3. Performance
- Keep table sizes manageable (archive old missions monthly)
- Use INTEGER primary keys (faster than UUID in SQLite)
- Index frequently queried columns
- VACUUM strategy for reclaiming space

### 4. Extensibility
- JSON columns for flexible data (args, result, metadata)
- Schema versioning for migrations
- Reserved columns for future use

---

## Example Schema Structure

```sql
-- missions: Core mission lifecycle
CREATE TABLE missions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    mission_uuid TEXT UNIQUE NOT NULL,  -- External identifier
    phase TEXT NOT NULL,                -- PLANNING, CODING, etc.
    status TEXT NOT NULL,               -- pending, in_progress, completed, failed
    created_at TEXT NOT NULL,           -- ISO 8601 timestamp
    completed_at TEXT,
    metadata JSON                       -- Flexible storage for mission-specific data
);

-- tool_calls: Audit trail of all tool executions
CREATE TABLE tool_calls (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    mission_id INTEGER NOT NULL,
    tool_name TEXT NOT NULL,
    args JSON NOT NULL,
    result JSON,
    timestamp TEXT NOT NULL,
    duration_ms INTEGER,
    success INTEGER NOT NULL,           -- 0 or 1
    error_message TEXT,
    FOREIGN KEY (mission_id) REFERENCES missions(id) ON DELETE CASCADE
);

CREATE INDEX idx_tool_calls_mission_time ON tool_calls(mission_id, timestamp);
CREATE INDEX idx_tool_calls_success ON tool_calls(success);

-- Additional tables follow same pattern...
```

---

## Deliverables

1. **docs/tasks/ARCH-001_schema.sql**
   - Complete DDL for all 5 tables
   - Indexes for performance
   - Comments explaining each field

2. **docs/tasks/ARCH-001_migration_plan.md**
   - JSON → SQLite transition strategy
   - Backward compatibility plan
   - Schema versioning approach

---

## Validation

```bash
# Test schema validity
sqlite3 :memory: < docs/tasks/ARCH-001_schema.sql

# Should create tables without errors
sqlite3 :memory: ".read docs/tasks/ARCH-001_schema.sql" ".tables"
# Expected output: agent_memory decisions missions playbook_runs tool_calls
```

---

## Next Steps

→ **ARCH-002:** Implement SQLiteStore class using this schema
→ **ARCH-003:** Integrate into boot_sequence.py and core_orchestrator.py
