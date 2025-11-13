# REFACTORING PLAN: AOS v0.1 → v0.2

**Goal**: Transform monolithic prompts into granular, addressable, modular prompt system.

**Status**: IN PROGRESS
**Started**: 2025-11-12
**Pilot Agent**: GENESIS_BLUEPRINT

---

## WHAT CHANGES

### BEFORE (v0.1):
```
agency_os/01_planning_framework/
└── prompts/
    └── GENESIS_BLUEPRINT_v5.md (951 lines - MONOLITH)
```

### AFTER (v0.2):
```
agency_os/01_planning_framework/agents/GENESIS_BLUEPRINT/
├── _composition.yaml              # How to combine prompts
├── _prompt_core.md                # Personality + Core identity
├── _knowledge_deps.yaml           # Required YAML knowledge files
│
├── tasks/
│   ├── task_01_select_core_modules.md
│   ├── task_01_select_core_modules.meta.yaml
│   ├── task_02_design_extensions.md
│   ├── task_02_design_extensions.meta.yaml
│   ├── task_03_generate_config_schema.md
│   ├── task_03_generate_config_schema.meta.yaml
│   ├── task_04_validate_architecture.md
│   ├── task_04_validate_architecture.meta.yaml
│   ├── task_05_handoff.md
│   └── task_05_handoff.meta.yaml
│
└── gates/
    ├── gate_no_extensions_in_core.md
    ├── gate_unidirectional_deps.md
    └── gate_stdlib_only_core.md
```

---

## FILE-BY-FILE BREAKDOWN

### 1. `_prompt_core.md`
**Source**: Lines 1-80 of GENESIS_BLUEPRINT_v5.md
**Contains**:
- Agent identity ("You are GENESIS BLUEPRINT...")
- Core responsibilities
- Genesis Core Pattern definition
- General constraints (no orchestration, artifact-centric)

**Example structure**:
```markdown
# GENESIS BLUEPRINT - Core Personality

You are **GENESIS BLUEPRINT**, the technical architecture generator for Agency OS.

## Core Responsibilities
1. Transform feature specs into Genesis-pattern architectures
2. Enforce Core-Extensions separation
3. Generate production-ready config schemas

## Genesis Core Pattern
- **Core**: Business logic only (stdlib only, no external libs)
- **Extensions**: Features (external libs allowed)
- **Unidirectional Dependencies**: Extensions → Core (NEVER Core → Extensions)
...
```

---

### 2. `task_01_select_core_modules.md`
**Source**: Lines 81-250 of GENESIS_BLUEPRINT_v5.md (Phase 1 section)
**Contains**:
- Detailed instructions for Core Module Selection
- stdlib catalog reference
- Selection algorithm
- Decision criteria

**Example structure**:
```markdown
# Task: Select Core Modules

## Objective
Analyze feature_spec.json and select stdlib-only modules for the Core layer.

## Input Artifact
- `feature_spec.json` (from VIBE_ALIGNER)

## Process
1. Load stdlib catalog from knowledge base
2. For each feature in feature_spec.json:
   - Identify required business logic
   - Map to stdlib modules (os, json, pathlib, etc.)
   - Flag if feature requires external libs (→ Extensions layer)

## Selection Algorithm
...

## Output
- `core_modules_selection.json`
```

---

### 3. `task_01_select_core_modules.meta.yaml`
**NEW FILE**
**Purpose**: Machine-readable metadata for runtime orchestration

```yaml
task_id: select_core_modules
phase: 1
dependencies: []  # No prerequisite tasks

inputs:
  - type: artifact
    ref: feature_spec.json
    required_fields: [features[].id, features[].name, features[].description]
  - type: knowledge
    ref: genesis_core_stdlib_catalog.yaml

outputs:
  - type: artifact
    ref: core_modules_selection.json
    schema_ref: ORCHESTRATION_data_contracts.yaml#core_modules

validation_gates:
  - gate_stdlib_only_core.md

estimated_complexity: medium
estimated_tokens: 1500
```

---

### 4. `_composition.yaml`
**NEW FILE**
**Purpose**: Defines how PromptRuntime combines prompt fragments

```yaml
composition_version: "2.0"
agent_id: GENESIS_BLUEPRINT
agent_version: "6.0"

composition_order:
  - source: _prompt_core.md
    type: base
    required: true

  - source: ${knowledge_files}
    type: knowledge
    required: true
    resolve_from: _knowledge_deps.yaml

  - source: ${task_prompt}
    type: task
    required: true
    path_pattern: tasks/${task_id}.md

  - source: ${gate_prompts}
    type: validation
    required: false
    resolve_from: tasks/${task_id}.meta.yaml#validation_gates

  - source: ${runtime_context}
    type: context
    required: true

variables:
  project_id: ${runtime_context.project_id}
  current_phase: ${runtime_context.current_phase}

conflict_resolution:
  strategy: last_wins
  exceptions:
    - section: CRITICAL_CONSTRAINTS
      strategy: merge_all
```

---

### 5. `_knowledge_deps.yaml`
**NEW FILE**
**Purpose**: Declare which YAML knowledge files this agent needs

```yaml
version: "1.0"
agent_id: GENESIS_BLUEPRINT

required_knowledge:
  - path: agency_os/01_planning_framework/knowledge/FAE_constraints.yaml
    purpose: "v1.0 scope limits, feature feasibility rules"
    critical: true

  - path: agency_os/01_planning_framework/knowledge/FDG_dependencies.yaml
    purpose: "Feature prerequisites, dependency graph"
    critical: true

  - path: agency_os/01_planning_framework/knowledge/APCE_rules.yaml
    purpose: "Complexity scoring, effort estimation"
    critical: false  # Nice to have but not blocking

optional_knowledge:
  - path: agency_os/02_code_gen_framework/knowledge/CODE_GEN_dependencies.yaml
    purpose: "Library recommendations for Extensions layer"
    load_if: ${task_id} == "design_extensions"
```

---

### 6. `gate_stdlib_only_core.md`
**Source**: Lines 600-650 of GENESIS_BLUEPRINT_v5.md (Anti-Slop section)
**Contains**:
- Validation rules
- Rejection criteria
- Example violations

**Example structure**:
```markdown
# Validation Gate: stdlib-only Core

## Rule
The Core layer MUST use only Python stdlib modules. NO external libraries.

## Validation Process
1. Parse `core_modules_selection.json`
2. For each module in `core.modules[]`:
   - Check if module is in Python 3.11+ stdlib
   - If NOT in stdlib → REJECT with error

## Allowed stdlib modules
- os, sys, pathlib, json, datetime, logging, typing, ...

## Forbidden in Core
- requests, flask, sqlalchemy, pandas, numpy, ...

## Error Message Template
"REJECTED: Module '{module_name}' is not in Python stdlib. Move to Extensions layer."
```

---

## NEW RUNTIME COMPONENT

### `agency_os/00_system/runtime/prompt_runtime.py`
**NEW FILE**
**Purpose**: Prompt composition engine

**Key functions**:
```python
class PromptRuntime:
    def execute_task(agent_id: str, task_id: str, context: dict) -> dict:
        """Compose and execute an atomized task."""
        pass

    def _compose_prompt(composition_spec, task_id, knowledge_files, context) -> str:
        """Combine prompt fragments per composition spec."""
        pass

    def _resolve_knowledge_deps(agent_id, task_inputs) -> list[str]:
        """Resolve which YAML files to load."""
        pass

    def _run_validation_gates(result, gates) -> bool:
        """Execute validation gates against task output."""
        pass
```

---

## UPDATED FILES

### `.knowledge_index.yaml`
**Changes**: Add new `task_prompt` type entries

```yaml
categories:
  - id: "planning_architecture"
    intent:
      - "Genesis pattern"
      - "core module selection"
    files:
      # Existing knowledge YAMLs
      - path: "agency_os/01_planning_framework/knowledge/..."
        type: knowledge

      # NEW: Task prompts as "executable knowledge"
      - path: "agency_os/01_planning_framework/agents/GENESIS_BLUEPRINT/tasks/task_01_select_core_modules.md"
        type: task_prompt
        agent: GENESIS_BLUEPRINT
        task_id: select_core_modules
        semantic_tags: ["module_selection", "stdlib_only", "dependency_analysis"]
```

---

## TESTING PLAN

### Test Case: Compose task_01
```python
# test_composition.py
from prompt_runtime import PromptRuntime

runtime = PromptRuntime()

context = {
    "project_id": "test_project_001",
    "current_phase": "PLANNING",
    "artifacts": {
        "feature_spec": "workspaces/test/artifacts/planning/feature_spec.json"
    }
}

composed_prompt = runtime.execute_task(
    agent_id="GENESIS_BLUEPRINT",
    task_id="select_core_modules",
    context=context
)

print(composed_prompt)
# Expected: _prompt_core.md + knowledge YAMLs + task_01.md + runtime context
```

---

## MIGRATION STRATEGY

### Parallel Structure (No Breaking Changes)
1. Keep `prompts/GENESIS_BLUEPRINT_v5.md` (OLD - unchanged)
2. Create `agents/GENESIS_BLUEPRINT/` (NEW - parallel)
3. Test v0.2 structure
4. Once validated, deprecate v5.md

### Backward Compatibility
- Old orchestrator can still call v5.md monolith
- New PromptRuntime calls atomized structure
- Both can coexist during migration

---

## SUCCESS CRITERIA

### Phase 1 (GENESIS_BLUEPRINT Pilot)
- [x] Atomize GENESIS_BLUEPRINT into 5 tasks
- [x] Create composition.yaml
- [x] Build PromptRuntime prototype
- [ ] Successfully compose task_01 from fragments
- [ ] Validate composition matches original intent

### Phase 2 (Full Migration)
- [ ] Refactor VIBE_ALIGNER (786 lines → atomized)
- [ ] Refactor CODE_GENERATOR, QA_VALIDATOR, DEPLOY_MANAGER
- [ ] Update ORCHESTRATION_workflow_design.yaml to use task references
- [ ] Migrate all 8 agents

---

## EXECUTION ORDER

1. ✅ Write this plan
2. Create directory structure
3. Extract `_prompt_core.md`
4. Extract all 5 `task_*.md` files
5. Create all 5 `.meta.yaml` files
6. Extract validation gates
7. Create `_composition.yaml`
8. Create `_knowledge_deps.yaml`
9. Update `.knowledge_index.yaml`
10. Build `prompt_runtime.py`
11. Test composition
12. Commit & push

---

**NEXT STEP**: Create directory structure for GENESIS_BLUEPRINT atomization.
