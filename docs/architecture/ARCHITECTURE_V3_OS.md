# VIBE OS v3.0 - Operating System Architecture

**STATUS:** 🚧 PARTIALLY MIGRATED (Phase 3 & 4 Incomplete)
**LAST UPDATED:** 2025-11-20
**ASSESSMENT:** ⚠️ DOCUMENTATION DRIFT CONFIRMED
**NEXT ACTION:** Complete migration, deprecate `agency_os/`

---

## 🎯 EXECUTIVE SUMMARY

**The Vision:** Separate the domain-agnostic OS (Vibe OS) from the domain-specific application (Vibe Agency).

**The Reality:** Migration is ~60% complete. Both old (`agency_os/`) and new (`vibe_core/` + `apps/agency/`) structures coexist, causing boot failures and import confusion.

**Critical Blockers:**
1. ❌ **RouterBridge Missing** - The connector between PlaybookRouter and AgentRegistry doesn't exist
2. ⚠️ **Boot Script** - Still points to old `agency_os/core_system/orchestrator/core_orchestrator.py`
3. ⚠️ **Zombie Code** - 50 Python files still in deprecated `agency_os/`
4. ⚠️ **Import Confusion** - Code imports from both old and new locations

---

## 📊 CURRENT STATE (Code Census)

```
DIRECTORY STRUCTURE (2025-11-20):
├── vibe_core/          41 Python files  ✅ Kernel (OS Layer)
├── apps/agency/        25 Python files  ✅ Application (Agency Layer)
└── agency_os/          50 Python files  ⚠️ DEPRECATED (Zombie Code)

TOTAL: 116 Python files across 3 locations (should be 2)
```

### What EXISTS and WORKS:

**✅ vibe_core/ (Kernel - 41 files)**
```
vibe_core/
├── config/             # Phoenix config (consolidated)
├── playbook/           # PlaybookEngine, router, executor, loader
├── runtime/            # LLM client, safety, prompt system
├── specialists/        # BaseSpecialist, registry (abstract base)
├── store/              # SQLite persistence layer
└── task_management/    # Mission/roadmap/task management
```

**✅ apps/agency/ (Application - 25 files)**
```
apps/agency/
├── orchestrator/       # Core orchestrator (SDLC state machine)
├── personas/           # Architect, Coder, Researcher, Reviewer
└── specialists/        # Planning, Coding, Testing, Deployment, Maintenance
```

**⚠️ agency_os/ (DEPRECATED - 50 files - SHOULD BE REMOVED)**
- Mix of code that was moved and code that wasn't
- Some scripts still import from here
- Causing circular dependencies and boot failures

---

## 🏗️ THE 3-LAYER MODEL (v3.0 Architecture)

```
┌─────────────────────────────────────────────────────────┐
│  LAYER 3: INTERFACE (User-Facing)                      │
│  ├── vibe-cli          (CLI entry point)               │
│  ├── bin/              (Scripts and utilities)         │
│  └── Playbooks/        (Workflow definitions)          │
└─────────────────────────────────────────────────────────┘
                            ↕
┌─────────────────────────────────────────────────────────┐
│  LAYER 2: APPLICATION (Domain-Specific)                │
│  apps/agency/                                           │
│  ├── orchestrator/     (SDLC state machine)            │
│  ├── specialists/      (Planning, Coding, Testing...)  │
│  └── personas/         (Architect, Coder, Reviewer...) │
│                                                         │
│  Domain: Software Development Lifecycle (SDLC)         │
└─────────────────────────────────────────────────────────┘
                            ↕
┌─────────────────────────────────────────────────────────┐
│  LAYER 1: KERNEL (Domain-Agnostic OS)                  │
│  vibe_core/                                             │
│  ├── store/            (SQLite persistence)            │
│  ├── runtime/          (LLM, safety, prompts)          │
│  ├── playbook/         (Workflow engine)               │
│  ├── specialists/      (Base classes, registry)        │
│  ├── config/           (System configuration)          │
│  └── task_management/  (Missions, roadmaps, tasks)     │
│                                                         │
│  Reusable for ANY domain (healthcare, fintech, etc.)   │
└─────────────────────────────────────────────────────────┘
```

---

## 🔗 THE ROUTERBRIDGE GAP (P0 CRITICAL)

**Problem:** User intent → Specialist execution is broken.

**Current State:**
- ✅ `PlaybookRouter` exists (`vibe_core/playbook/router.py`)
- ✅ `AgentRegistry` exists (`vibe_core/specialists/registry.py`)
- ❌ **RouterBridge MISSING** - No integration between them!

**The Missing Flow:**
```python
# DESIRED (not implemented):
user_input = "build a restaurant app"
  ↓
PlaybookRouter.route(user_input)  # ✅ EXISTS
  ↓
RouterBridge.extract_requirements()  # ❌ MISSING!!!
  ↓
AgentRegistry.get_specialist(phase)  # ✅ EXISTS
  ↓
PlanningSpecialist.execute()  # ✅ EXISTS
```

**Required Implementation:**
```
Location: vibe_core/playbook/router_bridge.py (NEW FILE)
Purpose: Connect PlaybookRouter → AgentRegistry
Complexity: ~150 LOC (Medium)
Dependencies:
  - from vibe_core.playbook.router import PlaybookRouter
  - from vibe_core.specialists.registry import AgentRegistry
```

**Impact:** Without this, the playbook system and specialist system cannot communicate!

---

## 🚨 KNOWN ISSUES (Documentation Drift)

### 1. Boot Failure
**File:** `bin/system-boot.sh:197`
**Error:** `FileNotFoundError: /home/user/vibe-agency/agency_os/core_system/orchestrator/core_orchestrator.py`
**Root Cause:** vibe-cli still points to old `agency_os/` location
**Fix Required:** Update vibe-cli imports to use `apps.agency.orchestrator`

### 2. Banner Identity Crisis
**File:** `bin/system-boot.sh:56`
**Current:** ">>> AGENCY OPERATING SYSTEM <<<"
**Should Be:** ">>> VIBE OS v3.0 <<<"
**Impact:** Misleading branding, doesn't reflect "OS" nature

### 3. Zombie Code
**Location:** `agency_os/` (50 Python files)
**Status:** Some moved, some duplicated, some orphaned
**Risk:** Import confusion, maintenance nightmare
**Action:** Full deprecation analysis required

### 4. Import Confusion
**Problem:** Code imports from both:
- Old: `from agency_os.core_system.runtime...`
- New: `from vibe_core.runtime...`

**Evidence:** 37 architecture docs still reference `agency_os`

---

## 📋 COMPLETION CHECKLIST (Phase 3 & 4 Incomplete)

### ✅ Completed
- [x] Create `vibe_core/` directory structure
- [x] Create `apps/agency/` directory structure
- [x] Move core runtime components to `vibe_core/`
- [x] Move specialists to `apps/agency/`
- [x] Move orchestrator to `apps/agency/`
- [x] Consolidate Phoenix config

### ❌ Not Complete (Blocking Production)
- [ ] **Implement RouterBridge** (P0 - Critical)
- [ ] Update boot script to use new imports
- [ ] Update banner to "Vibe OS"
- [ ] Deprecate/archive `agency_os/`
- [ ] Update all imports (old → new paths)
- [ ] Update 37 architecture docs (remove `agency_os` references)
- [ ] Full test suite validation
- [ ] Update CLAUDE.md with new structure

---

## 🛠️ KERNEL COMPONENTS (Domain-Agnostic)

### vibe_core/store/ - Persistence Layer
```python
# SQLite-based persistence for:
- Missions (high-level project goals)
- Tasks (actionable work items)
- Decisions (specialist recommendations)
- Tool executions (audit trail)
```

### vibe_core/runtime/ - Execution Infrastructure
```python
# Core runtime services:
- llm_client.py          # Multi-provider LLM abstraction
- tool_safety_guard.py   # Iron Dome (GAD-509 circuit breaker)
- quota_manager.py       # Cost control (GAD-510)
- prompt_composer.py     # Dynamic prompt assembly
- context_loader.py      # Project context management
- providers/             # Anthropic, Google, OpenAI adapters
```

### vibe_core/playbook/ - Workflow Engine
```python
# Playbook orchestration system:
- executor.py            # Graph executor (GAD-902)
- loader.py              # Workflow loader (GAD-903)
- router.py              # Semantic routing (user intent → workflow)
- router_bridge.py       # ❌ MISSING - Playbook → Registry integration
- _registry.yaml         # Workflow definitions
```

### vibe_core/specialists/ - Agent Framework
```python
# Abstract specialist pattern:
- base_specialist.py     # Base class for all specialists
- registry.py            # AgentRegistry (phase → specialist mapping)
```

### vibe_core/task_management/ - Mission Control
```python
# Mission and task orchestration:
- mission_manager.py     # Mission lifecycle
- roadmap_manager.py     # Multi-phase roadmaps
- task_executor.py       # Task execution coordination
```

---

## 🎯 APPLICATION COMPONENTS (SDLC-Specific)

### apps/agency/orchestrator/ - State Machine
```python
# SDLC orchestration (5-phase workflow):
PLANNING → CODING → TESTING → DEPLOYMENT → MAINTENANCE

- core_orchestrator.py   # Main state machine
- orchestrator.py        # Orchestration logic
```

### apps/agency/specialists/ - SDLC Specialists
```python
# Domain specialists (inherit from BaseSpecialist):
- planning_specialist.py      # Requirements, architecture, tasks
- coding_specialist.py        # Implementation, file generation
- testing_specialist.py       # Test generation, validation
- deployment_specialist.py    # Deployment automation
- maintenance_specialist.py   # Monitoring, updates
```

### apps/agency/personas/ - Role-Based Agents
```python
# Specialized roles for different tasks:
- architect.py           # System design, architecture
- coder.py               # Implementation focus
- researcher.py          # Research and discovery
- reviewer.py            # Code review, validation
```

---

## 🔄 DATA FLOW (How It SHOULD Work)

```
1. User Input (vibe-cli)
   ↓
2. PlaybookRouter (vibe_core/playbook/router.py)
   → Parses user intent
   → Loads workflow YAML
   ↓
3. RouterBridge (❌ MISSING!)
   → Extracts phase/requirements
   → Maps to specialist
   ↓
4. AgentRegistry (vibe_core/specialists/registry.py)
   → Returns specialist instance
   ↓
5. Specialist Execute (apps/agency/specialists/*.py)
   → Calls LLM (vibe_core/runtime/llm_client.py)
   → Protected by Safety Guard (vibe_core/runtime/tool_safety_guard.py)
   → Persists decisions (vibe_core/store/sqlite_store.py)
   ↓
6. Results → User
```

**BROKEN AT STEP 3:** No RouterBridge = disconnected system!

---

## 🎓 KEY ARCHITECTURAL PRINCIPLES

### 1. **Separation of Concerns**
- **Kernel (vibe_core):** Domain-agnostic infrastructure
- **App (apps/agency):** Software development domain logic
- **Interface (vibe-cli):** User interaction layer

### 2. **Hierarchical Agent Pattern (HAP)**
- Specialists inherit from `BaseSpecialist`
- Registry manages specialist lifecycle
- Orchestrator delegates to specialists (not inline execution)

### 3. **Persistence First**
- SQLite as source of truth (not JSON)
- All decisions persisted for audit trail
- Mission state queryable and recoverable

### 4. **Safety by Design**
- Circuit breaker (Iron Dome) prevents cascading failures
- Quota manager enforces cost limits
- Tool safety guard validates all operations

---

## 📖 RELATED DOCUMENTATION

| Document | Purpose | Status |
|----------|---------|--------|
| `KERNEL_AGENCY_SPLIT_PLAN.md` | Original migration plan | ✅ Plan Complete |
| `ARCHITECTURE_MAP.md` | GAD-based architecture (older) | ⚠️ Outdated |
| `ARCHITECTURE_V2.md` | Previous architecture | ⚠️ Pre-split |
| `SSOT.md` | Implementation decisions | ⚠️ Needs update |
| `ARCHITECTURE_V3_OS.md` | **This document** | ✅ Current Reality |

---

## 🚀 NEXT STEPS (Post-Audit Actions)

### Immediate (P0 - Week 1)
1. **Implement RouterBridge** (`vibe_core/playbook/router_bridge.py`)
2. **Fix Boot Script** (update imports to new locations)
3. **Update Banner** ("Vibe OS v3.0" branding)

### Short-Term (P1 - Week 2)
4. **Deprecate `agency_os/`** (move to `archive/` or delete)
5. **Update Import Paths** (old → new across codebase)
6. **Validate Tests** (ensure 100% pass rate with new structure)

### Medium-Term (P2 - Week 3-4)
7. **Update Documentation** (37 files with `agency_os` references)
8. **Update CLAUDE.md** (reflect new structure)
9. **Update SSOT.md** (new implementation decisions)

---

## ✅ VERIFICATION COMMANDS

```bash
# 1. Check directory structure
ls -la vibe_core/ apps/agency/ agency_os/

# 2. Count files (should see: 41, 25, 0)
find vibe_core -name "*.py" | wc -l
find apps/agency -name "*.py" | wc -l
find agency_os -name "*.py" | wc -l  # Should be 0 when complete

# 3. Test boot sequence
./bin/system-boot.sh  # Should succeed without errors

# 4. Verify imports (should return 0 results)
grep -r "from agency_os" vibe_core/ apps/agency/

# 5. Run full test suite
uv run pytest tests/ -v  # Should be 100% pass
```

---

## 📊 SUCCESS METRICS

| Metric | Current | Target |
|--------|---------|--------|
| Boot Success Rate | 0% ❌ | 100% ✅ |
| Legacy Files (`agency_os/`) | 50 files | 0 files |
| RouterBridge Exists | No ❌ | Yes ✅ |
| Import Consistency | Mixed | 100% new paths |
| Test Pass Rate | Unknown | 100% |
| Docs Updated | 0/37 | 37/37 |

---

## 🏁 DEFINITION OF DONE

The v3.0 OS architecture will be considered **COMPLETE** when:

- [ ] ✅ `./bin/system-boot.sh` succeeds without errors
- [ ] ✅ Banner displays "Vibe OS v3.0"
- [ ] ✅ RouterBridge implemented and tested
- [ ] ✅ `agency_os/` directory deleted/archived
- [ ] ✅ All imports use `vibe_core.*` or `apps.agency.*`
- [ ] ✅ Full test suite passes (100%)
- [ ] ✅ All architecture docs updated
- [ ] ✅ CLAUDE.md reflects new structure
- [ ] ✅ Junior agent can onboard using docs (safe for reading)

---

**END OF ARCHITECTURE_V3_OS.md**

*This document reflects the ACTUAL state as of 2025-11-20, not the aspirational state.*
*Use this as the map. Use git log for the history. Use tests to verify claims.*
