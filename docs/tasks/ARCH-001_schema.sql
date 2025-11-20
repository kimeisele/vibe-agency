-- ============================================================================
-- VIBE AGENCY - PERSISTENCE SCHEMA v2.0
-- ============================================================================
-- Purpose: Normalized SQLite schema for agent operation persistence
-- Phase: 2.5 - Foundation Scalability
-- Created: 2025-11-20
-- Updated: 2025-11-20 (v2 - Post Reality Check)
-- Schema Version: 2
--
-- CHANGELOG v2:
-- - Expanded missions table with budget tracking (max_cost_usd, current_cost_usd, etc.)
-- - Added metadata extraction columns (owner, description, api_version)
-- - Added planning_sub_state and updated_at columns
-- - NEW: session_narrative table (ProjectMemory support)
-- - NEW: domain_concepts table (ProjectMemory support)
-- - NEW: domain_concerns table (ProjectMemory support)
-- - NEW: trajectory table (ProjectMemory support)
-- - NEW: artifacts table (SDLC artifact tracking)
-- - NEW: quality_gates table (GAD-004 compliance)
-- ============================================================================

-- Set schema version for migrations
PRAGMA user_version = 2;

-- Enable foreign key enforcement (required for referential integrity)
PRAGMA foreign_keys = ON;

-- ============================================================================
-- TABLE: missions
-- ============================================================================
-- Purpose: Core mission lifecycle tracking
-- Stores: Mission metadata, phase progression, completion status, budget
-- v2 Updates: Added budget tracking, metadata extraction, status fields
-- ============================================================================
CREATE TABLE missions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    mission_uuid TEXT UNIQUE NOT NULL,      -- External identifier for API/file references (from metadata.projectId)
    phase TEXT NOT NULL,                    -- PLANNING, CODING, TESTING, DEPLOYMENT, MAINTENANCE
    status TEXT NOT NULL,                   -- pending, in_progress, completed, failed
    created_at TEXT NOT NULL,               -- ISO 8601 timestamp (e.g., '2025-11-20T14:30:00Z')
    completed_at TEXT,                      -- ISO 8601 timestamp (NULL if still active)
    updated_at TEXT,                        -- ISO 8601 timestamp of last modification (from metadata.lastUpdatedAt)

    -- v2: Planning sub-state tracking
    planning_sub_state TEXT,                -- RESEARCH, BUSINESS_VALIDATION, FEATURE_SPECIFICATION (NULL if not in PLANNING)

    -- v2: Budget tracking (from budget object in project_manifest.json)
    max_cost_usd REAL,                      -- Maximum budget for this mission
    current_cost_usd REAL DEFAULT 0.0,      -- Current spend
    alert_threshold REAL DEFAULT 0.80,      -- Alert when current_cost / max_cost exceeds this (0.0-1.0)
    cost_breakdown JSON,                    -- Detailed cost breakdown by phase/agent (flexible JSON)

    -- v2: Metadata extraction (for queryability - from metadata object)
    owner TEXT,                             -- Mission owner (e.g., 'agent@vibe.agency')
    description TEXT,                       -- Human-readable description
    api_version TEXT DEFAULT 'agency.os/v1alpha1',  -- Manifest API version

    -- Flexible storage for remaining mission-specific data (spec, etc.)
    metadata JSON,

    -- Constraints
    CHECK (status IN ('pending', 'in_progress', 'completed', 'failed')),
    CHECK (phase IN ('PLANNING', 'CODING', 'TESTING', 'DEPLOYMENT', 'MAINTENANCE')),
    CHECK (planning_sub_state IS NULL OR planning_sub_state IN ('RESEARCH', 'BUSINESS_VALIDATION', 'FEATURE_SPECIFICATION')),
    CHECK (current_cost_usd >= 0),
    CHECK (alert_threshold >= 0.0 AND alert_threshold <= 1.0)
);

-- Performance index: Query active missions efficiently
CREATE INDEX idx_missions_status ON missions(status);

-- Performance index: Query missions by phase
CREATE INDEX idx_missions_phase ON missions(phase);

-- v2: Performance index: Query missions by owner (for multi-tenant scenarios)
CREATE INDEX idx_missions_owner ON missions(owner);

-- v2: Performance index: Query missions over budget
CREATE INDEX idx_missions_budget ON missions(max_cost_usd, current_cost_usd);

-- ============================================================================
-- TABLE: tool_calls
-- ============================================================================
-- Purpose: Audit trail of all agent tool executions
-- Supports: "What tools were used?", "Why did this fail?", "How long did X take?"
-- ============================================================================
CREATE TABLE tool_calls (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    mission_id INTEGER NOT NULL,            -- Links to parent mission
    tool_name TEXT NOT NULL,                -- e.g., 'WebFetch', 'Bash', 'Read'
    args JSON NOT NULL,                     -- Tool input parameters (as JSON object)
    result JSON,                            -- Tool output (NULL if error occurred)
    timestamp TEXT NOT NULL,                -- ISO 8601 timestamp of execution
    duration_ms INTEGER,                    -- Execution time in milliseconds
    success INTEGER NOT NULL,               -- 0 = failed, 1 = succeeded
    error_message TEXT,                     -- Error details (NULL if success=1)

    -- Referential integrity: Cascade delete when mission is deleted
    FOREIGN KEY (mission_id) REFERENCES missions(id) ON DELETE CASCADE,

    -- Constraints
    CHECK (success IN (0, 1))
);

-- Performance index: Query tool calls by mission and time (for audit queries)
CREATE INDEX idx_tool_calls_mission_time ON tool_calls(mission_id, timestamp);

-- Performance index: Query failed tool calls
CREATE INDEX idx_tool_calls_success ON tool_calls(success);

-- Performance index: Query tool usage statistics
CREATE INDEX idx_tool_calls_name ON tool_calls(tool_name);

-- ============================================================================
-- TABLE: decisions
-- ============================================================================
-- Purpose: Agent decision provenance (why did the agent choose X?)
-- Supports: "Why was approach Y chosen?", "What was the rationale?"
-- ============================================================================
CREATE TABLE decisions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    mission_id INTEGER NOT NULL,            -- Links to parent mission
    decision_type TEXT NOT NULL,            -- e.g., 'architecture_choice', 'tool_selection', 'approach'
    rationale TEXT,                         -- Human-readable explanation of decision
    timestamp TEXT NOT NULL,                -- ISO 8601 timestamp
    agent_name TEXT,                        -- Which agent made this decision (e.g., 'STEWARD', 'CODING')
    context JSON,                           -- Additional context data (alternatives considered, etc.)

    -- Referential integrity
    FOREIGN KEY (mission_id) REFERENCES missions(id) ON DELETE CASCADE
);

-- Performance index: Query decisions by mission and time
CREATE INDEX idx_decisions_mission_time ON decisions(mission_id, timestamp);

-- Performance index: Query decisions by type
CREATE INDEX idx_decisions_type ON decisions(decision_type);

-- Performance index: Query decisions by agent
CREATE INDEX idx_decisions_agent ON decisions(agent_name);

-- ============================================================================
-- TABLE: playbook_runs
-- ============================================================================
-- Purpose: Playbook execution metrics (performance tracking)
-- Supports: "How long do playbooks take?", "Which playbooks fail most?"
-- ============================================================================
CREATE TABLE playbook_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    mission_id INTEGER NOT NULL,            -- Links to parent mission (NULL for standalone runs)
    playbook_name TEXT NOT NULL,            -- e.g., 'restaurant.plan', 'research.analyze_topic'
    phase TEXT,                             -- SDLC phase (PLANNING, CODING, etc.)
    started_at TEXT NOT NULL,               -- ISO 8601 timestamp
    completed_at TEXT,                      -- ISO 8601 timestamp (NULL if still running)
    success INTEGER,                        -- 0 = failed, 1 = succeeded, NULL = in_progress
    metrics JSON,                           -- Execution metrics (tool_count, decision_count, etc.)
    error_message TEXT,                     -- Error details (NULL if success=1)

    -- Referential integrity (allow NULL mission_id for standalone playbook runs)
    FOREIGN KEY (mission_id) REFERENCES missions(id) ON DELETE CASCADE,

    -- Constraints
    CHECK (success IS NULL OR success IN (0, 1))
);

-- Performance index: Query playbook runs by mission
CREATE INDEX idx_playbook_runs_mission ON playbook_runs(mission_id);

-- Performance index: Query playbook performance statistics
CREATE INDEX idx_playbook_runs_name ON playbook_runs(playbook_name);

-- Performance index: Query playbook failures
CREATE INDEX idx_playbook_runs_success ON playbook_runs(success);

-- ============================================================================
-- TABLE: agent_memory
-- ============================================================================
-- Purpose: Context persistence across agent invocations
-- Supports: Session state, user preferences, learned patterns
-- ============================================================================
CREATE TABLE agent_memory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    mission_id INTEGER NOT NULL,            -- Links to parent mission (NULL for global memory)
    key TEXT NOT NULL,                      -- Memory key (e.g., 'last_playbook', 'user_preference')
    value JSON,                             -- Memory value (flexible JSON storage)
    timestamp TEXT NOT NULL,                -- ISO 8601 timestamp of last update
    ttl INTEGER,                            -- Time-to-live in seconds (NULL = no expiration)
    expires_at TEXT,                        -- Computed expiration timestamp (NULL if ttl is NULL)

    -- Referential integrity
    FOREIGN KEY (mission_id) REFERENCES missions(id) ON DELETE CASCADE,

    -- Ensure unique keys per mission
    UNIQUE (mission_id, key)
);

-- Performance index: Query memory by mission and key (for fast context lookups)
CREATE INDEX idx_agent_memory_mission_key ON agent_memory(mission_id, key);

-- Performance index: Query expired memory for cleanup
CREATE INDEX idx_agent_memory_expires ON agent_memory(expires_at);

-- ============================================================================
-- v2: PROJECT MEMORY TABLES (Dedicated Tables for Queryability)
-- ============================================================================
-- Purpose: Replace JSON blob storage with structured tables for project_memory.json
-- Supports: Session narrative, domain tracking, trajectory, intent history
-- Decision: Option A (Dedicated Tables) - Full queryability over simplicity
-- ============================================================================

-- ============================================================================
-- TABLE: session_narrative
-- ============================================================================
-- Purpose: Session-by-session narrative of project evolution
-- Supports: "What happened in session X?", "Sessions in CODING phase"
-- Source: project_memory.json -> narrative array
-- ============================================================================
CREATE TABLE session_narrative (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    mission_id INTEGER NOT NULL,            -- Links to parent mission
    session_num INTEGER NOT NULL,           -- Session number (1, 2, 3, ...)
    summary TEXT NOT NULL,                  -- Human-readable session summary
    date TEXT NOT NULL,                     -- ISO 8601 timestamp of session
    phase TEXT NOT NULL,                    -- Phase during this session (PLANNING, CODING, etc.)

    -- Referential integrity
    FOREIGN KEY (mission_id) REFERENCES missions(id) ON DELETE CASCADE,

    -- Ensure unique session numbers per mission
    UNIQUE (mission_id, session_num)
);

-- Performance index: Query sessions by mission and time
CREATE INDEX idx_session_narrative_mission ON session_narrative(mission_id, session_num);

-- Performance index: Query sessions by phase
CREATE INDEX idx_session_narrative_phase ON session_narrative(phase);

-- ============================================================================
-- TABLE: domain_concepts
-- ============================================================================
-- Purpose: Domain concepts extracted from user input (keywords)
-- Supports: "What concepts are associated with this project?"
-- Source: project_memory.json -> domain.concepts array
-- ============================================================================
CREATE TABLE domain_concepts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    mission_id INTEGER NOT NULL,            -- Links to parent mission
    concept TEXT NOT NULL,                  -- Concept keyword (e.g., 'payment', 'database', 'authentication')
    timestamp TEXT NOT NULL,                -- ISO 8601 timestamp when concept was extracted

    -- Referential integrity
    FOREIGN KEY (mission_id) REFERENCES missions(id) ON DELETE CASCADE,

    -- Ensure unique concepts per mission
    UNIQUE (mission_id, concept)
);

-- Performance index: Query concepts by mission
CREATE INDEX idx_domain_concepts_mission ON domain_concepts(mission_id);

-- Performance index: Query missions by concept (reverse lookup)
CREATE INDEX idx_domain_concepts_concept ON domain_concepts(concept);

-- ============================================================================
-- TABLE: domain_concerns
-- ============================================================================
-- Purpose: User concerns extracted from input (PCI, performance, etc.)
-- Supports: "What are the user's concerns for this project?"
-- Source: project_memory.json -> domain.concerns array
-- ============================================================================
CREATE TABLE domain_concerns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    mission_id INTEGER NOT NULL,            -- Links to parent mission
    concern TEXT NOT NULL,                  -- Concern description (e.g., 'PCI compliance', 'performance')
    timestamp TEXT NOT NULL,                -- ISO 8601 timestamp when concern was extracted

    -- Referential integrity
    FOREIGN KEY (mission_id) REFERENCES missions(id) ON DELETE CASCADE,

    -- Ensure unique concerns per mission
    UNIQUE (mission_id, concern)
);

-- Performance index: Query concerns by mission
CREATE INDEX idx_domain_concerns_mission ON domain_concerns(mission_id);

-- Performance index: Query missions by concern (reverse lookup)
CREATE INDEX idx_domain_concerns_concern ON domain_concerns(concern);

-- ============================================================================
-- TABLE: trajectory
-- ============================================================================
-- Purpose: Project trajectory tracking (phase progression, focus, blockers)
-- Supports: "What is the current focus?", "What are the blockers?"
-- Source: project_memory.json -> trajectory object
-- ============================================================================
CREATE TABLE trajectory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    mission_id INTEGER UNIQUE NOT NULL,     -- Links to parent mission (one trajectory per mission)
    current_phase TEXT NOT NULL,            -- Current phase (PLANNING, CODING, etc.)
    current_focus TEXT,                     -- Current focus area (e.g., 'payment integration')
    completed_phases JSON,                  -- Array of completed phase names (e.g., ["PLANNING", "CODING"])
    blockers JSON,                          -- Array of blocker descriptions (e.g., ["5 failing tests"])
    updated_at TEXT NOT NULL,               -- ISO 8601 timestamp of last update

    -- Referential integrity
    FOREIGN KEY (mission_id) REFERENCES missions(id) ON DELETE CASCADE
);

-- Performance index: Query trajectory by mission
CREATE INDEX idx_trajectory_mission ON trajectory(mission_id);

-- Performance index: Query missions by current phase
CREATE INDEX idx_trajectory_phase ON trajectory(current_phase);

-- ============================================================================
-- v2: ARTIFACTS TABLE (Structured SDLC Artifact Tracking)
-- ============================================================================
-- Purpose: Track artifacts produced during SDLC phases
-- Supports: "What artifacts were produced?", "Show all code artifacts"
-- Source: project_manifest.json -> artifacts object
-- Decision: Option A (Dedicated Table) - Artifact tracking is spine of SDLC
-- ============================================================================
CREATE TABLE artifacts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    mission_id INTEGER NOT NULL,            -- Links to parent mission
    artifact_type TEXT NOT NULL,            -- Artifact category: 'planning', 'code', 'test', 'deployment'
    artifact_name TEXT NOT NULL,            -- Artifact name (e.g., 'architecture', 'mainRepository')
    ref TEXT,                               -- Git commit ref (e.g., 'ef1c122a4a57d07036f70cb2b5460c199f25059f')
    path TEXT,                              -- File path (e.g., '/artifacts/planning/architecture.v1.json')
    url TEXT,                               -- Repository URL (e.g., 'https://github.com/kimeisele/vibe-agency.git')
    branch TEXT,                            -- Git branch (e.g., 'main')
    metadata JSON,                          -- Additional artifact-specific data
    created_at TEXT NOT NULL,               -- ISO 8601 timestamp of artifact creation

    -- Referential integrity
    FOREIGN KEY (mission_id) REFERENCES missions(id) ON DELETE CASCADE,

    -- Constraints
    CHECK (artifact_type IN ('planning', 'code', 'test', 'deployment'))
);

-- Performance index: Query artifacts by mission and type
CREATE INDEX idx_artifacts_mission_type ON artifacts(mission_id, artifact_type);

-- Performance index: Query artifacts by type (all missions)
CREATE INDEX idx_artifacts_type ON artifacts(artifact_type);

-- Performance index: Query artifacts by ref (find artifact by commit)
CREATE INDEX idx_artifacts_ref ON artifacts(ref);

-- ============================================================================
-- v2: QUALITY GATES TABLE (GAD-004 Compliance)
-- ============================================================================
-- Purpose: Record quality gate results for auditability
-- Supports: "Did the mission pass quality gates?", "Which gates failed?"
-- Source: project_manifest.json -> quality_gates array (future)
-- ============================================================================
CREATE TABLE quality_gates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    mission_id INTEGER NOT NULL,            -- Links to parent mission
    gate_name TEXT NOT NULL,                -- Gate name (e.g., 'FACT_VALIDATOR', 'TEST_COVERAGE')
    status TEXT NOT NULL,                   -- Gate status: 'passed', 'failed', 'skipped'
    details JSON,                           -- Gate-specific details (scores, issues, etc.)
    timestamp TEXT NOT NULL,                -- ISO 8601 timestamp of gate execution

    -- Referential integrity
    FOREIGN KEY (mission_id) REFERENCES missions(id) ON DELETE CASCADE,

    -- Constraints
    CHECK (status IN ('passed', 'failed', 'skipped'))
);

-- Performance index: Query quality gates by mission
CREATE INDEX idx_quality_gates_mission ON quality_gates(mission_id);

-- Performance index: Query failed gates (for debugging)
CREATE INDEX idx_quality_gates_status ON quality_gates(status);

-- Performance index: Query gates by name (for statistics)
CREATE INDEX idx_quality_gates_name ON quality_gates(gate_name);

-- ============================================================================
-- VIEWS (Optional - for common queries)
-- ============================================================================

-- View: Active missions with latest activity
CREATE VIEW active_missions AS
SELECT
    m.id,
    m.mission_uuid,
    m.phase,
    m.status,
    m.created_at,
    COUNT(DISTINCT tc.id) AS tool_call_count,
    COUNT(DISTINCT d.id) AS decision_count,
    MAX(tc.timestamp) AS last_tool_call_at
FROM missions m
LEFT JOIN tool_calls tc ON tc.mission_id = m.id
LEFT JOIN decisions d ON d.mission_id = m.id
WHERE m.status IN ('pending', 'in_progress')
GROUP BY m.id;

-- View: Tool usage statistics
CREATE VIEW tool_usage_stats AS
SELECT
    tool_name,
    COUNT(*) AS total_calls,
    SUM(success) AS successful_calls,
    AVG(duration_ms) AS avg_duration_ms,
    MAX(duration_ms) AS max_duration_ms
FROM tool_calls
GROUP BY tool_name;

-- View: Playbook performance metrics
CREATE VIEW playbook_performance AS
SELECT
    playbook_name,
    COUNT(*) AS total_runs,
    SUM(success) AS successful_runs,
    AVG(CAST((julianday(completed_at) - julianday(started_at)) * 86400000 AS INTEGER)) AS avg_duration_ms
FROM playbook_runs
WHERE completed_at IS NOT NULL
GROUP BY playbook_name;

-- ============================================================================
-- MAINTENANCE TRIGGERS (Auto-cleanup)
-- ============================================================================

-- Trigger: Auto-compute expires_at when TTL is set
CREATE TRIGGER compute_memory_expiration
AFTER INSERT ON agent_memory
FOR EACH ROW
WHEN NEW.ttl IS NOT NULL
BEGIN
    UPDATE agent_memory
    SET expires_at = datetime(NEW.timestamp, '+' || NEW.ttl || ' seconds')
    WHERE id = NEW.id;
END;

-- ============================================================================
-- SCHEMA VALIDATION QUERIES (v2)
-- ============================================================================
-- Run these to verify schema integrity after creation:
--
-- 1. List all tables:
--    .tables
--    Expected (v2): agent_memory artifacts decisions domain_concepts domain_concerns
--                   missions playbook_runs quality_gates session_narrative tool_calls trajectory
--
-- 2. Verify foreign keys are enabled:
--    PRAGMA foreign_keys;
--    Expected: 1
--
-- 3. Check schema version:
--    PRAGMA user_version;
--    Expected: 2
--
-- 4. Test referential integrity (cascade deletes work):
--    INSERT INTO missions (mission_uuid, phase, status, created_at, max_cost_usd, owner)
--        VALUES ('test-001', 'PLANNING', 'pending', '2025-11-20T00:00:00Z', 100.0, 'test@vibe.agency');
--    INSERT INTO tool_calls (mission_id, tool_name, args, timestamp, success)
--        VALUES (1, 'test_tool', '{}', '2025-11-20T00:01:00Z', 1);
--    INSERT INTO session_narrative (mission_id, session_num, summary, date, phase)
--        VALUES (1, 1, 'Test session', '2025-11-20T00:00:00Z', 'PLANNING');
--    INSERT INTO artifacts (mission_id, artifact_type, artifact_name, created_at)
--        VALUES (1, 'planning', 'test_artifact', '2025-11-20T00:00:00Z');
--    DELETE FROM missions WHERE mission_uuid = 'test-001';
--    SELECT COUNT(*) FROM tool_calls;  -- Expected: 0 (cascade delete worked)
--    SELECT COUNT(*) FROM session_narrative;  -- Expected: 0 (cascade delete worked)
--    SELECT COUNT(*) FROM artifacts;  -- Expected: 0 (cascade delete worked)
--
-- 5. Test budget constraints:
--    INSERT INTO missions (mission_uuid, phase, status, created_at, current_cost_usd)
--        VALUES ('test-002', 'CODING', 'in_progress', '2025-11-20T00:00:00Z', -10.0);
--    -- Expected: CHECK constraint failed (current_cost_usd >= 0)
--
-- 6. Test queryability (ProjectMemory):
--    -- "Find all sessions in CODING phase"
--    SELECT * FROM session_narrative WHERE phase = 'CODING';
--
--    -- "Find all missions with blockers"
--    SELECT m.mission_uuid, t.blockers
--    FROM missions m
--    JOIN trajectory t ON t.mission_id = m.id
--    WHERE json_array_length(t.blockers) > 0;
--
--    -- "Find all projects with 'payment' concept"
--    SELECT m.mission_uuid, m.description
--    FROM missions m
--    JOIN domain_concepts dc ON dc.mission_id = m.id
--    WHERE dc.concept = 'payment';
--
-- 7. Test budget queries (v2):
--    -- "Find missions over budget"
--    SELECT mission_uuid, owner, current_cost_usd, max_cost_usd
--    FROM missions
--    WHERE current_cost_usd > max_cost_usd;
--
--    -- "Find missions approaching alert threshold"
--    SELECT mission_uuid, owner,
--           ROUND(current_cost_usd / max_cost_usd, 2) AS budget_utilization
--    FROM missions
--    WHERE max_cost_usd IS NOT NULL
--      AND (current_cost_usd / max_cost_usd) >= alert_threshold;
-- ============================================================================
