# SCHEMA REALITY CHECK - Phase 0 Analysis

**Date:** 2025-11-20
**Migration Phase:** Shadow Mode - Phase 0 (Reality Check)
**Status:** 🔴 **CRITICAL GAPS IDENTIFIED - Schema Revision Required**

---

## Executive Summary

Analysis of current production JSON structures against the proposed SQL schema (ARCH-001_schema.sql) reveals **significant data loss risks** and **structural mismatches** that would prevent successful migration without schema modifications.

**Key Findings:**
- ✅ Core mission lifecycle mapping is viable
- 🔴 **CRITICAL:** ProjectManifest has rich metadata not captured in SQL
- 🔴 **CRITICAL:** ProjectMemory has no SQL representation
- 🔴 **CRITICAL:** Budget tracking absent from schema
- ⚠️  Nested artifact structures require serialization strategy
- ⚠️  Quality gate recording mechanism missing

**Recommendation:** **DO NOT PROCEED** with current schema. Revise ARCH-001 before implementing Adapter/Store.

---

## 1. Data Source Analysis

### 1.1 Current Production State Files

#### **project_manifest.json** (Primary State)
Location: `workspaces/{project_name}/project_manifest.json`

**Structure:**
```json
{
  "apiVersion": "agency.os/v1alpha1",
  "kind": "Project",
  "metadata": {
    "projectId": "f81d4fae-7dec-11d0-a765-00a0c91e6bf6",
    "name": "vibe-agency",
    "description": "The root project for the Vibe Agency OS.",
    "owner": "agent@vibe.agency",
    "createdAt": "2025-11-12T14:00:00Z",
    "lastUpdatedAt": "2025-11-12T14:00:00Z"
  },
  "spec": {
    "vibe": {},
    "genesis": {}
  },
  "status": {
    "projectPhase": "CODING",
    "planningSubState": "BUSINESS_VALIDATION",
    "lastUpdate": "2025-11-12T14:00:00Z",
    "message": "All specialist agent prompts designed."
  },
  "budget": {
    "max_cost_usd": 10.0,
    "current_cost_usd": 0.0,
    "alert_threshold": 0.80,
    "cost_breakdown": {}
  },
  "artifacts": {
    "planning": {
      "architecture": {
        "ref": "ef1c122a4a57d07036f70cb2b5460c199f25059f",
        "path": "/artifacts/planning/architecture.v1.json"
      }
    },
    "code": {
      "mainRepository": {
        "url": "https://github.com/kimeisele/vibe-agency.git",
        "branch": "main",
        "lastCommit": "ef1c122a4a57d07036f70cb2b5460c199f25059f"
      }
    }
  }
}
```

#### **project_memory.json** (Semantic Context)
Location: `.vibe/project_memory.json`

**Structure:**
```json
{
  "_schema_version": "1.0",
  "_created": "2025-11-20T00:00:00Z",
  "project_id": "vibe-agency",
  "narrative": [
    {
      "session": 1,
      "summary": "Implemented payment feature",
      "date": "2025-11-20T00:00:00Z",
      "phase": "CODING"
    }
  ],
  "domain": {
    "type": "general",
    "concepts": ["payment", "database", "authentication"],
    "concerns": ["PCI compliance", "performance"]
  },
  "trajectory": {
    "phase": "CODING",
    "completed": ["PLANNING"],
    "current_focus": "payment integration",
    "blockers": []
  },
  "intent_history": [
    {
      "session": 1,
      "intent": "payment integration",
      "confidence": "high"
    }
  ]
}
```

---

## 2. Detailed Field Mapping

### 2.1 ProjectManifest → missions Table

| JSON Field (project_manifest.json) | SQL Column (missions) | Type Match | Notes |
|-----------------------------------|----------------------|------------|-------|
| `metadata.projectId` | `mission_uuid` | ✅ TEXT | 1:1 mapping |
| `status.projectPhase` | `phase` | ✅ ENUM | Direct mapping |
| `status.projectPhase` | `status` | ⚠️  **MAPPING ISSUE** | JSON has phase, SQL expects status (pending/in_progress/completed) |
| `metadata.createdAt` | `created_at` | ✅ TEXT (ISO 8601) | 1:1 mapping |
| N/A | `completed_at` | ⚠️  **MISSING SOURCE** | No completion timestamp in JSON |
| **ENTIRE OBJECT** | `metadata` (JSON) | 🔴 **DATA LOSS RISK** | Storing entire manifest loses queryability |

#### **CRITICAL GAPS:**

1. **Missing Status Distinction:**
   - JSON: Only `projectPhase` (PLANNING, CODING, etc.)
   - SQL: Requires both `phase` AND `status` (pending/in_progress/completed/failed)
   - **Risk:** Cannot distinguish between "PLANNING in_progress" vs "PLANNING completed"

2. **Budget Tracking Absent:**
   - JSON: `budget` (max_cost_usd, current_cost_usd, alert_threshold, cost_breakdown)
   - SQL: **NO BUDGET COLUMNS**
   - **Risk:** Budget tracking completely lost unless stored in JSON blob

3. **Rich Metadata Lost:**
   - JSON: `apiVersion`, `kind`, `description`, `owner`, `spec`
   - SQL: Must be serialized into generic `metadata` JSON column
   - **Risk:** Cannot query "all projects owned by agent@vibe.agency"

4. **Artifacts Structure:**
   - JSON: Nested structure with `planning`, `code`, `test`, `deployment`
   - SQL: No dedicated artifacts table or structured storage
   - **Risk:** Complex artifact relationships lost

---

### 2.2 ProjectMemory → agent_memory Table

| JSON Field (project_memory.json) | SQL Column (agent_memory) | Mapping Status |
|---------------------------------|---------------------------|----------------|
| `narrative` (array) | `value` (JSON) | 🔴 **FLATTENING REQUIRED** |
| `domain` (object) | `value` (JSON) | 🔴 **FLATTENING REQUIRED** |
| `trajectory` (object) | `value` (JSON) | 🔴 **FLATTENING REQUIRED** |
| `intent_history` (array) | `value` (JSON) | 🔴 **FLATTENING REQUIRED** |

#### **CRITICAL ISSUE:**

**ProjectMemory has no dedicated SQL representation.** The `agent_memory` table uses a key-value store pattern, but:

- **Narrative (session history):** Array of 50+ session objects
  - Current: Queryable as array in JSON
  - SQL: Must be one row per key (`narrative` → entire array as JSON blob)
  - **Risk:** Cannot query "sessions in CODING phase" without deserializing blob

- **Domain Concepts:** Dynamic array growing over time
  - Current: `["payment", "database", "authentication"]`
  - SQL: Single JSON blob or separate rows per concept?
  - **Risk:** No schema for concept tracking

- **Trajectory:** Rich object with phase, completed, focus, blockers
  - SQL: Single row with key="trajectory", value={entire object}
  - **Risk:** Cannot query "projects with blockers" efficiently

---

### 2.3 Tool Calls (Currently Not Persisted)

| Data Source | SQL Table | Status |
|------------|-----------|--------|
| **NONE** | `tool_calls` | ❌ **NO DATA SOURCE** |

**Finding:** Tool execution is not currently logged to any file. The `tool_calls` table assumes we will START tracking tool execution.

**Implication:** This is a NEW feature, not a migration concern.

---

### 2.4 Decisions (Currently Not Persisted)

| Data Source | SQL Table | Status |
|------------|-----------|--------|
| **NONE** | `decisions` | ❌ **NO DATA SOURCE** |

**Finding:** Agent decisions are not currently logged. The `decisions` table assumes we will START tracking decision provenance.

**Implication:** This is a NEW feature, not a migration concern.

---

### 2.5 Playbook Runs (Currently Not Persisted)

| Data Source | SQL Table | Status |
|------------|-----------|--------|
| **NONE** | `playbook_runs` | ❌ **NO DATA SOURCE** |

**Finding:** Playbook execution metrics are not currently logged. The `playbook_runs` table assumes we will START tracking playbook performance.

**Implication:** This is a NEW feature, not a migration concern.

---

## 3. Data Loss Risk Assessment

### 🔴 CRITICAL RISKS (Data Loss)

| Risk ID | Description | Impact | Mitigation Required |
|---------|-------------|--------|---------------------|
| **R-001** | **Budget data has no SQL columns** | Cannot track costs, alert thresholds | Add budget columns to missions table |
| **R-002** | **Status vs Phase conflation** | Cannot distinguish "PLANNING pending" from "PLANNING in_progress" | Add explicit status column logic or derive from completion |
| **R-003** | **Metadata queryability lost** | Cannot query by owner, apiVersion, description | Extract key metadata fields to columns |
| **R-004** | **ProjectMemory has no schema** | Session narrative, domain, trajectory flattened into JSON blobs | Create dedicated tables for narrative, domain, trajectory |
| **R-005** | **Artifact relationships lost** | Nested artifact structure (planning/code/test) becomes opaque JSON | Design artifact schema or accept JSON serialization |
| **R-006** | **Quality gate results missing** | GAD-004 requires gate recording in manifest | Add quality_gates table or manifest column |

### ⚠️  MODERATE RISKS (Reduced Functionality)

| Risk ID | Description | Impact | Workaround |
|---------|-------------|--------|-----------|
| **R-007** | planningSubState not in schema | Cannot query sub-state transitions | Store in metadata JSON or add column |
| **R-008** | lastUpdatedAt not in schema | Cannot track last modification time | Add updated_at column or use metadata |
| **R-009** | spec field has no representation | Project configuration lost | Store in metadata JSON |

---

## 4. Type Compatibility Matrix

| JSON Type | SQL Type | Compatible? | Notes |
|-----------|----------|-------------|-------|
| `string` (ISO 8601 timestamp) | `TEXT` | ✅ Yes | SQLite stores as TEXT, queryable with datetime() |
| `string` (UUID) | `TEXT UNIQUE` | ✅ Yes | Direct mapping |
| `enum` (projectPhase) | `TEXT` with CHECK constraint | ✅ Yes | ARCH-001 defines CHECK (phase IN (...)) |
| `number` (cost_usd) | **MISSING** | 🔴 **NO COLUMN** | Need REAL or INTEGER column |
| `object` (nested artifacts) | `JSON` | ⚠️  Loss of query | Must deserialize to query |
| `array` (narrative) | `JSON` | ⚠️  Loss of query | Must deserialize to query |
| `boolean` (N/A in current data) | `INTEGER` (0/1) | ✅ Yes | Standard SQLite pattern |

---

## 5. Schema Revision Requirements

### 5.1 Required Schema Changes

To avoid data loss, ARCH-001 must be revised to include:

#### **A. Expand missions table:**
```sql
ALTER TABLE missions ADD COLUMN:
  -- Budget tracking (GAD-XXX Budget Management)
  max_cost_usd REAL,
  current_cost_usd REAL DEFAULT 0.0,
  alert_threshold REAL DEFAULT 0.80,
  cost_breakdown JSON,

  -- Metadata extraction (for queryability)
  owner TEXT,
  description TEXT,
  api_version TEXT DEFAULT 'agency.os/v1alpha1',

  -- Status distinction
  planning_sub_state TEXT,  -- RESEARCH, BUSINESS_VALIDATION, FEATURE_SPECIFICATION

  -- Timestamps
  updated_at TEXT  -- Track last modification
```

#### **B. Create project_memory schema:**
```sql
-- Session narrative (50 sessions max)
CREATE TABLE session_narrative (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  mission_id INTEGER NOT NULL,
  session_num INTEGER NOT NULL,
  summary TEXT NOT NULL,
  date TEXT NOT NULL,
  phase TEXT NOT NULL,
  FOREIGN KEY (mission_id) REFERENCES missions(id) ON DELETE CASCADE,
  UNIQUE (mission_id, session_num)
);

-- Domain concepts (extracted keywords)
CREATE TABLE domain_concepts (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  mission_id INTEGER NOT NULL,
  concept TEXT NOT NULL,
  timestamp TEXT NOT NULL,
  FOREIGN KEY (mission_id) REFERENCES missions(id) ON DELETE CASCADE,
  UNIQUE (mission_id, concept)
);

-- Domain concerns (user concerns)
CREATE TABLE domain_concerns (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  mission_id INTEGER NOT NULL,
  concern TEXT NOT NULL,
  timestamp TEXT NOT NULL,
  FOREIGN KEY (mission_id) REFERENCES missions(id) ON DELETE CASCADE,
  UNIQUE (mission_id, concern)
);

-- Trajectory tracking
CREATE TABLE trajectory (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  mission_id INTEGER UNIQUE NOT NULL,
  current_phase TEXT NOT NULL,
  current_focus TEXT,
  completed_phases JSON,  -- Array of completed phase names
  blockers JSON,  -- Array of blocker descriptions
  updated_at TEXT NOT NULL,
  FOREIGN KEY (mission_id) REFERENCES missions(id) ON DELETE CASCADE
);
```

#### **C. Create artifacts schema:**
```sql
CREATE TABLE artifacts (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  mission_id INTEGER NOT NULL,
  artifact_type TEXT NOT NULL,  -- 'planning', 'code', 'test', 'deployment'
  artifact_name TEXT NOT NULL,  -- 'architecture', 'mainRepository'
  ref TEXT,  -- Git commit ref
  path TEXT,  -- File path
  url TEXT,  -- Repository URL
  metadata JSON,  -- Additional artifact-specific data
  created_at TEXT NOT NULL,
  FOREIGN KEY (mission_id) REFERENCES missions(id) ON DELETE CASCADE
);

CREATE INDEX idx_artifacts_mission_type ON artifacts(mission_id, artifact_type);
```

#### **D. Create quality_gates table (GAD-004):**
```sql
CREATE TABLE quality_gates (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  mission_id INTEGER NOT NULL,
  gate_name TEXT NOT NULL,
  status TEXT NOT NULL,  -- 'passed', 'failed', 'skipped'
  details JSON,
  timestamp TEXT NOT NULL,
  FOREIGN KEY (mission_id) REFERENCES missions(id) ON DELETE CASCADE
);

CREATE INDEX idx_quality_gates_mission ON quality_gates(mission_id);
```

---

### 5.2 Migration Strategy Impact

**Current Strategy:** Adapter Pattern with Shadow Mode (Dual Write)

**Revised Strategy Required:**
1. **Phase 0.5: Schema Revision** (INSERT BEFORE current Phase 0)
   - Update ARCH-001_schema.sql with changes above
   - Validate schema with test data
   - Document migration mapping (revised)

2. **Phase 1: Shadow Mode**
   - Implement Adapter with revised schema
   - Dual write to JSON + SQLite
   - No data loss during transition

3. **Phase 2: Cutover**
   - Switch read source to SQLite
   - Deprecate JSON writes

---

## 6. Adapter Pattern Implications

### 6.1 Required Adapter Logic

The Adapter must handle:

**A. ProjectManifest Serialization:**
```python
def manifest_to_sql(manifest: dict) -> dict:
    """
    Convert project_manifest.json to SQL row(s).

    Returns:
        {
            'missions': {...},  # Single row
            'artifacts': [...],  # Multiple rows
            'quality_gates': [...]  # Multiple rows (if present)
        }
    """
    return {
        'missions': {
            'mission_uuid': manifest['metadata']['projectId'],
            'phase': manifest['status']['projectPhase'],
            'status': infer_status(manifest),  # INFER from phase
            'created_at': manifest['metadata']['createdAt'],
            'updated_at': manifest['metadata']['lastUpdatedAt'],
            'planning_sub_state': manifest['status'].get('planningSubState'),
            'owner': manifest['metadata']['owner'],
            'description': manifest['metadata']['description'],
            'max_cost_usd': manifest['budget']['max_cost_usd'],
            'current_cost_usd': manifest['budget']['current_cost_usd'],
            'metadata': json.dumps(manifest['spec'])  # Store spec as JSON
        },
        'artifacts': flatten_artifacts(manifest['artifacts']),
        ...
    }
```

**B. ProjectMemory Serialization:**
```python
def memory_to_sql(memory: dict, mission_id: int) -> dict:
    """
    Convert project_memory.json to SQL rows.

    Returns:
        {
            'session_narrative': [...],
            'domain_concepts': [...],
            'domain_concerns': [...],
            'trajectory': {...}
        }
    """
```

### 6.2 Complexity Estimate

| Component | Complexity | Reason |
|-----------|-----------|--------|
| Missions table mapping | **Medium** | Need to infer status, flatten budget |
| Artifacts flattening | **High** | Nested structure requires recursive traversal |
| ProjectMemory split | **High** | 4 separate tables, array flattening |
| Quality gates | **Low** | New feature, no backward compat |

**Estimated Adapter LOC:** 300-500 lines (vs original estimate of 150 lines)

---

## 7. Recommendations

### 7.1 Immediate Actions (BLOCKING)

1. **DO NOT implement Adapter/Store with current schema** ❌
2. **Revise ARCH-001_schema.sql** with Section 5.1 changes ✅
3. **Create test dataset** for validation (use existing workspaces) ✅
4. **Run schema validation** with SQLite:
   ```bash
   sqlite3 test.db < docs/tasks/ARCH-001_schema_v2.sql
   # Verify tables created without errors
   ```

### 7.2 Decision Points

**DECISION REQUIRED:** How to represent ProjectMemory?

**Option A: Dedicated Tables (Recommended)**
- ✅ Pro: Full queryability ("sessions in CODING phase")
- ✅ Pro: Respects Phase 2.5 "queryable state" goal
- ❌ Con: More complex schema (4 new tables)
- ❌ Con: Adapter complexity increases

**Option B: JSON Blob in agent_memory**
- ✅ Pro: Simpler schema (use existing agent_memory table)
- ✅ Pro: Faster initial implementation
- ❌ Con: Loses queryability (defeats SQLite purpose)
- ❌ Con: Trajectory/blocker queries require deserialization

**RECOMMENDATION:** **Option A (Dedicated Tables)** - Queryability is the PRIMARY goal of Phase 2.5.

---

**DECISION REQUIRED:** How to represent Artifacts?

**Option A: Dedicated artifacts table (Recommended)**
- ✅ Pro: Can query "all code artifacts" efficiently
- ✅ Pro: Maintains artifact relationships
- ❌ Con: Schema more complex

**Option B: JSON blob in missions.metadata**
- ✅ Pro: Simpler schema
- ❌ Con: Cannot query artifact-specific fields

**RECOMMENDATION:** **Option A (Dedicated Table)** - Artifact tracking is critical for SDLC workflows.

---

### 7.3 Success Criteria for Phase 0

Before proceeding to Phase 1 (Adapter implementation):

- [ ] ARCH-001_schema_v2.sql created with all Section 5.1 additions
- [ ] Test data migration successful (use workspaces/vibe_internal/project_manifest.json)
- [ ] No data loss verified (round-trip JSON → SQL → JSON matches)
- [ ] Queryability proven:
  - [ ] "Find all missions with blockers" works
  - [ ] "Find all CODING phase sessions" works
  - [ ] "Find all projects over budget" works
- [ ] Adapter complexity re-estimated and approved

---

## 8. Conclusion

**Can we proceed with current schema?** ❌ **NO**

**Why?**
1. Budget tracking would be completely lost
2. ProjectMemory semantic context would be flattened into opaque JSON blobs
3. Status distinction (pending vs in_progress) is ambiguous
4. Artifact relationships would be lost
5. Quality gate recording (GAD-004) has no schema

**Next Steps:**
1. **Lead Architect approves schema revision** (Section 5.1)
2. **Update ARCH-001_schema.sql → v2**
3. **Re-run Reality Check** with revised schema
4. **Then and only then:** Proceed to Adapter implementation

**Estimated Delay:** +2-3 days for schema revision and validation

**Risk if we proceed anyway:** Migration will succeed technically but lose 40-60% of queryability goals, defeating the purpose of SQLite persistence.

---

**Report Author:** STEWARD (Senior Orchestration Agent)
**Verification:** Manual analysis of 3 data sources (project_manifest.json, project_memory.json, core_orchestrator.py)
**Next Review:** After ARCH-001 revision approved
