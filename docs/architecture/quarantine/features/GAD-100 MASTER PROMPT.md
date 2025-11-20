# GAD-100 IMPLEMENTATION PACKAGE - MASTER PROMPT

**YOU ARE IMPLEMENTING:** GAD-100 Configuration & Environment Management
**REPOSITORY:** vibe-agency
**RISK LEVEL:** 🔴 CRITICAL (Open heart surgery on system core)
**EXECUTION MODE:** Autonomous phased rollout with checkpoints

-----

## EXECUTIVE SUMMARY

You are implementing a foundational architecture change that will become the bedrock (Pillar 1) for the entire system. This is NOT a simple refactoring - this is open heart surgery.

**What you’re building:**

- Central configuration layer (GAD-100) using vendored phoenix_config
- Unified API for all state/config access
- Schema validation for all state files
- Environment overlays (dev/staging/prod)
- Clear separation: repo-level vs workspace-level state

**Why this matters:**

- Eliminates the `.session_handoff.json` vs `project_manifest.json` confusion
- Makes MOTD implementation possible (GAD-500 Week 1 deliverable)
- Enables GAD-501 Layer 2 ambient context
- Foundation for GAD-5XX through GAD-8XX

-----

## CRITICAL CONSTRAINTS (GEMINI’S 1% - READ THIS!)

### 1. Schema Generation = AUDIT, not AUTO-CREATE

```python
# ❌ WRONG: Auto-generate schema from existing files
schema = auto_generate_from_files("workspaces/*/project_manifest.json")

# ✅ RIGHT: Generate AUDIT REPORT, human defines canonical schema
report = audit_all_manifests("workspaces/*/project_manifest.json")
# Returns: {
#   "found_keys": ["metadata", "status", "artifacts", ...],
#   "inconsistencies": [
#     "workspace_A has 'budget' key, workspace_B doesn't",
#     "workspace_C has status.projectPhase, workspace_D has status.phase"
#   ],
#   "type_mismatches": [...]
# }
# Human reviews report → defines canonical schema
```

**WHY:** Existing files may have drifted over time. Auto-generation would create a “Franken-schema” that validates bad data.

-----

### 2. Legacy Code Isolation = ADAPTER PATTERN

```python
# ❌ WRONG: Scattered if/else everywhere
if use_phoenix:
    manifest = load_from_phoenix()
else:
    # 20 lines of old code here

if use_phoenix:
    handoff = load_from_phoenix()
else:
    # 15 lines of old code there

# ✅ RIGHT: Isolate ALL legacy code in ONE adapter class
class LegacyConfigLoader:
    """Isolates all pre-GAD-100 config loading logic"""
    def get_project_manifest(self, project_id): ...
    def get_session_handoff(self): ...
    def get_system_integrity(self): ...

class VibeConfig:
    """GAD-100 phoenix_config wrapper"""
    def get_project_manifest(self, project_id): ...
    def get_session_handoff(self): ...
    def get_system_integrity(self): ...

# Orchestrator - clean adapter pattern
if use_phoenix:
    self.config = VibeConfig()
else:
    self.config = LegacyConfigLoader()

# Rest of system stays clean
manifest = self.config.get_project_manifest(project_id)
```

**WHY:** Makes switching trivial, keeps old code frozen, enables clean rollback.

-----

### 3. Migration Test = PROVE LOSSLESS

```python
# test_vad_100_migration.py (NEW - CRITICAL!)
def test_migration_is_lossless():
    """Verify state_migrator.py preserves all data"""

    # 1. Load with legacy system
    legacy_loader = LegacyConfigLoader()
    old_data = legacy_loader.get_project_manifest("test_workspace_golden")

    # 2. Run migration
    migrate_workspace("test_workspace_golden")

    # 3. Load with new system
    new_loader = VibeConfig()
    new_data = new_loader.get_project_manifest("test_workspace_golden")

    # 4. PROVE equivalence
    assert old_data == new_data, "Migration lost data!"
```

**WHY:** Without this test, you have NO PROOF that migration is safe.

-----

## EXECUTION PROTOCOL (6 PHASES)

### Phase 1: Vendor Phoenix Config (Week 1)

**Objective:** Copy phoenix_config into repo, verify it works in isolation

```bash
ACTIONS:
1. Copy python-packages/phoenix_config_/phoenix_config → lib/phoenix_config/
2. Copy tests → tests/lib/test_phoenix_config.py
3. Run tests: pytest tests/lib/test_phoenix_config.py
4. Document: docs/architecture/GAD-1XX/GAD-100.md (complete)

VERIFICATION:
✅ All phoenix_config tests pass
✅ No external dependency in requirements.txt
✅ GAD-100.md complete (40+ pages)
✅ Git commit: "feat(gad-100): Vendor phoenix_config (Phase 1)"

DELIVERABLES:
- lib/phoenix_config/ (vendored code)
- tests/lib/test_phoenix_config.py
- docs/architecture/GAD-1XX/GAD-100.md
- docs/architecture/GAD-1XX/GAD-101.md (Multi-source loading)
- docs/architecture/GAD-1XX/GAD-102.md (Environment overlays)
- docs/architecture/GAD-1XX/GAD-103.md (Schema validation)
```

**STOP POINT:** Wait for human approval before Phase 2

-----

### Phase 2: Schema Audit & Definition (Week 1-2)

**Objective:** Generate audit report, define canonical schemas

```bash
ACTIONS:
1. Implement: tools/schema_auditor.py (NOT auto-generator!)
2. Run audit on all state files:
   - workspaces/*/project_manifest.json
   - .session_handoff.json
   - .vibe/system_integrity_manifest.json
3. Generate: SCHEMA_AUDIT_REPORT.md
4. Human reviews report
5. Human defines canonical schemas in config/schemas/

VERIFICATION:
✅ Audit tool runs without errors
✅ SCHEMA_AUDIT_REPORT.md generated
✅ Report shows all inconsistencies
✅ Schemas defined (with human input!)
✅ Git commit: "feat(gad-100): Schema audit & canonical schemas (Phase 2)"

DELIVERABLES:
- tools/schema_auditor.py
- SCHEMA_AUDIT_REPORT.md
- config/schemas/project_manifest.schema.json (canonical!)
- config/schemas/session_handoff.schema.json
- config/schemas/system_integrity.schema.json
- config/schemas/knowledge_base.schema.json
```

**STOP POINT:** Wait for human to review audit report and approve schemas

-----

### Phase 3: Implement VibeConfig Wrapper (Week 2)

**Objective:** Create GAD-100 wrapper, isolate legacy code

```bash
ACTIONS:
1. Implement: LegacyConfigLoader (isolate ALL old code)
2. Implement: VibeConfig (phoenix_config wrapper)
3. Create: config/phoenix_config.yaml (defines all sources)
4. Create: config/base.yaml, config/dev.yaml, config/prod.yaml
5. Write tests: tests/test_vibe_config.py

VERIFICATION:
✅ LegacyConfigLoader passes existing tests
✅ VibeConfig passes new tests
✅ Both loaders return equivalent data (test_equivalence.py)
✅ No existing code broken
✅ Git commit: "feat(gad-100): VibeConfig wrapper + legacy isolation (Phase 3)"

DELIVERABLES:
- vibe_config.py (NEW - GAD-100 API)
- legacy_config_loader.py (NEW - isolated old code)
- config/phoenix_config.yaml
- config/base.yaml, config/dev.yaml, config/prod.yaml
- tests/test_vibe_config.py
- tests/test_legacy_loader.py
- tests/test_equivalence.py (critical!)
```

**STOP POINT:** Wait for tests to pass and human approval

-----

### Phase 4: Feature Flag Integration (Week 2-3)

**Objective:** Add feature flag to orchestrator, enable parallel operation

```bash
ACTIONS:
1. Modify: core_orchestrator.py
   - Add: __init__(use_phoenix_config=False)
   - Add adapter pattern for config loading
2. Update: All load_* methods to use config adapter
3. Add ENV var: VIBE_USE_PHOENIX_CONFIG=false (default)
4. Write tests: tests/test_feature_flag.py

VERIFICATION:
✅ Orchestrator works with use_phoenix_config=False (legacy)
✅ Orchestrator works with use_phoenix_config=True (new)
✅ All existing tests still pass
✅ Feature flag toggles correctly
✅ Git commit: "feat(gad-100): Feature flag for parallel operation (Phase 4)"

DELIVERABLES:
- core_orchestrator.py (modified with adapter pattern)
- tests/test_feature_flag.py
- .env.template (add VIBE_USE_PHOENIX_CONFIG)
```

**STOP POINT:** Test in dev environment, wait for human approval

-----

### Phase 5: Migration Tools & Testing (Week 3-4)

**Objective:** Build migration tools, prove lossless migration

```bash
ACTIONS:
1. Implement: tools/state_migrator.py
2. Implement: tools/validation_checker.py
3. Write CRITICAL test: tests/test_vad_100_migration.py
4. Run migration on test_workspace_golden/
5. Verify lossless migration

VERIFICATION:
✅ test_vad_100_migration.py passes (CRITICAL!)
✅ Migration preserves all data
✅ No data loss, no corruption
✅ Validation checker finds no issues
✅ Git commit: "feat(gad-100): Migration tools + lossless verification (Phase 5)"

DELIVERABLES:
- tools/state_migrator.py
- tools/validation_checker.py
- tests/test_vad_100_migration.py (THE CRITICAL TEST)
- MIGRATION_REPORT.md (audit trail)
```

**STOP POINT:** Migration test MUST pass before proceeding to production

-----

### Phase 6: Production Rollout (Week 4-5)

**Objective:** Switch default to GAD-100, deprecate legacy

```bash
ACTIONS:
1. Change default: VIBE_USE_PHOENIX_CONFIG=true
2. Run full test suite
3. Update all docs
4. Deprecate LegacyConfigLoader (mark as deprecated)
5. Plan legacy removal (6 months)

VERIFICATION:
✅ All tests pass with phoenix_config
✅ No regressions
✅ Performance acceptable
✅ Documentation complete
✅ Git commit: "feat(gad-100): Switch to phoenix_config by default (Phase 6)"

DELIVERABLES:
- .env (VIBE_USE_PHOENIX_CONFIG=true by default)
- docs/MIGRATION_COMPLETE.md
- docs/guides/GAD-100_USAGE.md
- DEPRECATION_NOTICE.md (plan to remove legacy in 6 months)
```

**STOP POINT:** Monitor production for 2 weeks, then declare success

-----

## LAD/VAD INTEGRATION

### LAD-0: Configuration Layer (NEW)

```markdown
LAD-0 sits BELOW LAD-1 as the foundational configuration layer.

Responsibilities:
- Load all state files (manifests, handoffs, integrity)
- Validate against schemas
- Provide unified API to upper layers
- Handle environment overlays (dev/prod)

Used by:
- LAD-1: Manual config loading (fallback)
- LAD-2: Automatic config loading (tools)
- LAD-3: Hot reload config loading (runtime)
```

**Deliverable:** `docs/architecture/LAD/LAD-0.md`

-----

### VAD-000: Config Validation Tests (NEW)

```python
# tests/architecture/test_vad000_config.py

def test_vad000_phoenix_config_loads():
    """Verify GAD-100 config loads correctly"""
    config = VibeConfig(env="test")
    assert config.system_integrity is not None

def test_vad000_schema_validation():
    """Verify invalid state is caught"""
    invalid = {"bad": "data"}
    with pytest.raises(SchemaValidationError):
        config.validate_project_manifest(invalid)

def test_vad000_migration_lossless():
    """CRITICAL: Verify migration preserves data"""
    # See Phase 5 for full implementation
    ...
```

**Deliverable:** `docs/architecture/VAD/VAD-000.md`

-----

## ROLLBACK PROCEDURES

### Phase N Rollback

```bash
# If Phase N fails:
1. git revert <phase-n-commit>
2. Run: verification/phase_{N-1}_verify.py
3. Confirm: All Phase N-1 tests still pass
4. Report: "Phase N failed, rolled back to Phase N-1"
```

### Emergency Rollback

```bash
# Nuclear option - revert ALL GAD-100 changes:
1. git revert <gad-100-start-commit>^..<gad-100-current-commit>
2. Run: pytest (all tests)
3. Confirm: System back to pre-GAD-100 state
4. Report: "Emergency rollback complete"
```

-----

## REPORTING FORMAT

After each phase:

```
PHASE N: [TITLE]
Status: ✅ SUCCESS / ❌ FAILED
Duration: X hours
Changes:
  - Added: lib/phoenix_config/
  - Modified: core_orchestrator.py
  - Tests: 12 new, 156 existing (all pass)
Verification:
  ✅ Tests: 168/168 passed
  ✅ Linting: 0 errors
  ✅ Docs: GAD-100.md complete
Git:
  Commit: abc123def "feat(gad-100): Phase N complete"
  Branch: feature/gad-100-phase-n
Next: Awaiting human approval to proceed to Phase N+1
```

-----

## SUCCESS CRITERIA

GAD-100 is complete when:

- ✅ All 6 phases completed
- ✅ All tests passing
- ✅ Migration test proves lossless
- ✅ Documentation complete (GAD-100 through GAD-105, LAD-0, VAD-000)
- ✅ Production running with VIBE_USE_PHOENIX_CONFIG=true
- ✅ No regressions
- ✅ Legacy code marked deprecated

-----

## BEGIN EXECUTION

**START WITH:** Phase 1 - Vendor Phoenix Config

**READ FIRST:**

- This prompt (master instructions)
- docs/architecture/GAD-1XX/GAD-100.md (when created in Phase 1)
- Gemini’s 1% constraints (schema audit, adapter pattern, migration test)

**PROCEED ONLY AFTER:** Each phase verification passes + human approval

**GO!** 🚀​​​​​​​​​​​​​​​​
