# Roadmap Directory

**Active Roadmap:** Phase 2.5 - Foundation Scalability

---

## 🎯 CURRENT: Phase 2.5 - Foundation Scalability

**File:** `phase_2_5_foundation.json`
**Status:** Active (0/13 tasks complete)
**Objective:** Architect for scale - SQLite persistence + Hierarchical Agent Pattern (HAP)

### Strategic Alignment

This roadmap addresses the **Gemini-identified bottlenecks**:
1. ✅ **Monolithic Orchestrator** → HAP (specialists per SDLC phase)
2. ✅ **Lack of Persistence** → SQLite layer (queryable state)
3. ✅ **Tool Security** → Capability-based security (playbook-driven)

### Phases

#### Phase 0: Persistence Foundation (SQLite)
**Estimated:** 3 sessions, ~480 minutes

| Task | Name | Priority | Time |
|------|------|----------|------|
| ARCH-001 | Design SQLite schema | P0 | 90m |
| ARCH-002 | Implement SQLite store | P0 | 180m |
| ARCH-003 | Migrate mission state to DB | P0 | 120m |
| ARCH-004 | Add tool call logging | P0 | 90m |

**Deliverables:**
- `agency_os/persistence/sqlite_store.py`
- `.vibe/state/vibe_agency.db` (auto-created on boot)
- Full audit trail: tool calls, decisions, playbook runs

#### Phase 1: Vertical Slice Extraction
**Estimated:** 3 sessions, ~420 minutes

| Task | Name | Priority | Time |
|------|------|----------|------|
| ARCH-005 | Design BaseSpecialist interface | P0 | 120m |
| ARCH-006 | Extract PlanningSpecialist | P0 | 180m |
| ARCH-007 | Prove specialist pattern | P0 | 120m |

**Deliverables:**
- `agency_os/agents/base_specialist.py` (abstract base)
- `agency_os/agents/planning_specialist.py` (first specialist)
- Orchestrator delegates to specialist (no inline execution)

#### Phase 2: HAP Pattern Generalization
**Estimated:** 4 sessions, ~630 minutes

| Task | Name | Priority | Time |
|------|------|----------|------|
| ARCH-008 | Implement 4 remaining specialists | P1 | 300m |
| ARCH-009 | Refactor orchestrator to routing | P1 | 180m |
| ARCH-010 | Playbook capability declaration | P1 | 150m |

**Deliverables:**
- 5 specialists: Planning, Coding, Testing, Deployment, Maintenance
- `core_orchestrator.py` < 200 LOC (pure routing)
- Capability-based tool security

#### Phase 3: Verification & Documentation
**Estimated:** 2 sessions, ~300 minutes

| Task | Name | Priority | Time |
|------|------|----------|------|
| ARCH-011 | Run HAP verification suite | P0 | 90m |
| ARCH-012 | Update architecture docs | P1 | 120m |
| ARCH-013 | Create completion report | P1 | 90m |

**Deliverables:**
- `docs/PHASE_2_5_COMPLETION_REPORT.md`
- Updated `ARCHITECTURE_V2.md` with HAP design
- All tests passing (>= 95% coverage)

---

## 📊 Before → After Metrics (Target)

| Metric | Before | After Target | Impact |
|--------|--------|--------------|--------|
| **Orchestrator LOC** | ~500+ | < 200 | ✅ Pure routing |
| **Specialist Count** | 0 | 5 | ✅ Phase isolation |
| **Persistence** | JSON files | SQLite | ✅ Queryable |
| **Tool Logging** | Text logs | DB audit trail | ✅ Debuggable |
| **Delegation** | Monolithic | HAP | ✅ Scalable |
| **Security** | Ad-hoc | Capability-based | ✅ Controlled |

---

## 🔄 Execution Strategy

### Mode: STEWARD Sessions

1. User spawns STEWARD session
2. STEWARD reads `phase_2_5_foundation.json`
3. Finds next pending task (dependency-aware)
4. Executes task following acceptance criteria
5. Marks complete, updates roadmap JSON
6. Session ends or continues to next task

### Safety Rails

- **Strict Dependencies:** ARCH-N cannot start until ARCH-(N-1) complete
- **Test-First:** All new code requires >= 80% test coverage
- **Rollback Plan:** Each phase in separate git branch
- **Session State:** `.session_handoff.json` preserves context

---

## 📚 Task Specifications

Detailed specs for each task:
- `docs/tasks/ARCH-001_persistence_schema.md`
- `docs/tasks/ARCH-002_sqlite_store.md`
- `docs/tasks/ARCH-005_base_specialist.md`
- *(Additional specs to be created as tasks progress)*

---

## 🗂️ Completed Roadmaps

### Cleanup Roadmap (2025-11-20) ✅

**File:** `docs/archive/cleanup_roadmap_completed_2025-11-20.json`
**Status:** COMPLETE (16/16 tasks)
**Duration:** 2 weeks, 12 sessions

**Key Achievements:**
- Boot reliability: Fail → 100% success
- Test suite: 369 → 631 tests (+71%)
- Import system fixed (40+ sys.path hacks removed)
- Provider system tested (0% → 70% coverage)

**See:** `CLEANUP_COMPLETION_REPORT.md` for full details

---

## 🎯 Future Roadmaps (Potential)

### Phase 3: Product Features
- Feature-driven development (user-facing capabilities)
- Builds on HAP + SQLite foundation
- TBD after Phase 2.5 complete

### Phase 4: Sandboxing (Optional)
- Container-based execution isolation
- Only needed if autonomous agent spawning added
- Deferred until use case validated

---

## 📖 References

- **CLAUDE.md:** Current system status and quick start
- **ARCHITECTURE_V2.md:** Conceptual model and design
- **ARCHITECTURE_REGISTRY.md:** All architectural decisions (ADRs, GADs, VADs, LADs)
- **INDEX.md:** Documentation navigation hub

---

*Last Updated: 2025-11-20*
