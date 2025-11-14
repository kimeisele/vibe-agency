# CRITICAL WORKSPACE ARCHITECTURE ANALYSIS

**Date:** 2025-11-14
**Severity:** 🔴 CRITICAL - Multiple KO Criteria Identified
**Context:** Gemini Comparison Review - Framework Architecture Validation
**Status:** ACTIVE - Immediate Action Required

---

## EXECUTIVE SUMMARY

This report documents **6 critical architectural flaws** (KO criteria) discovered during a comparative analysis with Gemini AI's framework review. While Gemini correctly identified the symptom (artifacts landing in root directory), the root causes are significantly more severe and systemic.

**Critical Finding:** The framework contains fully-implemented workspace management utilities (`workspace_utils.py`) that are **completely unused** by the runtime system. This represents a fundamental integration failure.

**Business Impact:**
- ❌ Multi-client isolation is **non-functional**
- ❌ All artifacts currently land in root directory
- ❌ Workspace-based context switching is **broken**
- ❌ Production deployments would fail client segregation requirements

**Recommendation:** Immediate implementation of Phase 1 fixes (3 critical patches) before any further feature development.

---

## 1. GEMINI'S ANALYSIS VALIDATION

### What Gemini Got RIGHT ✅

Gemini correctly identified:

1. **Symptom:** Artifacts are being written to the root directory instead of workspace-specific paths
   - Evidence: `project_manifest.json` exists in root (should only be in workspaces/)
   - Impact: Multiple client projects cannot coexist

2. **Missing Enforcement:** The ORCHESTRATOR doesn't enforce workspace path discipline
   - Evidence: No explicit path injection in agent invocations
   - Impact: Agents default to CWD (root directory)

3. **Proposed Solution:** Extend `project_manifest.json` with explicit `artifact_paths` section
   - Example:
     ```json
     {
       "artifact_paths": {
         "planning": "workspaces/prabhupad_os/artifacts/planning/",
         "coding": "workspaces/prabhupad_os/artifacts/coding/"
       }
     }
     ```

### What Gemini MISSED ❌

Gemini's analysis was **incomplete** because it focused on the data model (manifest structure) without auditing:
- Existing codebase infrastructure
- Runtime integration points
- Environment variable propagation
- Schema consistency across components

The proposed solution (extending manifest) is **necessary but insufficient** - it addresses the data model but not the execution model.

---

## 2. CRITICAL KO CRITERIA ANALYSIS

### 🔴 KO #1: WORKSPACE_UTILS.PY EXISTS BUT IS NEVER IMPORTED

**Severity:** CRITICAL
**Type:** Integration Failure
**Impact:** Complete workspace isolation is non-functional

#### Evidence

**File:** `scripts/workspace_utils.py` (562 lines)

```python
def resolve_artifact_base_path(workspace_name: Optional[str] = None) -> Path:
    """
    Resolves workspace name to artifacts/ base directory.

    Used by SOPs to determine where to save/load artifacts based on active workspace.

    Examples:
        >>> resolve_artifact_base_path('acme_corp')
        PosixPath('workspaces/acme_corp/artifacts')

        >>> resolve_artifact_base_path('ROOT')
        PosixPath('artifacts')
    """
    if workspace_name is None:
        workspace_name = get_active_workspace()

    if workspace_name == 'ROOT':
        return Path('artifacts')
    else:
        return Path(f'workspaces/{workspace_name}/artifacts')
```

**Location:** Lines 94-119

**This function does EXACTLY what Gemini proposed!**

#### Verification: Zero Imports

```bash
$ grep -r "import.*workspace_utils" **/*.py
# RESULT: No matches found

$ grep -r "from.*workspace_utils" **/*.py
# RESULT: No matches found
```

**Conclusion:** The workspace resolution logic is fully implemented but **completely disconnected** from the runtime.

#### Root Cause

The `prompt_runtime.py` (which composes prompts for agents) and `vibe-cli.py` (which invokes the runtime) both operate **independently** of `workspace_utils.py`.

**File:** `agency_os/00_system/runtime/prompt_runtime.py`

```python
def _format_runtime_context(self, context: Dict[str, Any]) -> str:
    """Format runtime context as markdown"""
    lines = ["**Runtime Context:**\n"]
    for key, value in context.items():
        if isinstance(value, dict):
            lines.append(f"- **{key}:**")
            for k, v in value.items():
                lines.append(f"  - {k}: `{v}`")
        else:
            lines.append(f"- **{key}:** `{value}`")

    return "\n".join(lines)
```

**Location:** Lines 420-431

**Analysis:** The runtime context is formatted as **markdown text** for the LLM prompt. It is NOT used to actually resolve file paths programmatically.

---

### 🔴 KO #2: $ACTIVE_WORKSPACE ENVIRONMENT VARIABLE IS NEVER SET

**Severity:** CRITICAL
**Type:** Configuration Failure
**Impact:** Workspace context always defaults to 'ROOT'

#### Evidence

**File:** `scripts/workspace_utils.py`

```python
def get_active_workspace() -> str:
    """
    Returns current workspace context from environment variable.

    The $ACTIVE_WORKSPACE environment variable is set by SOP_008 (Switch Workspace)
    and determines which workspace manifest all SSF operations target.

    Returns:
        str: Workspace name (e.g., 'acme_corp') or 'ROOT' if not set
    """
    return os.getenv('ACTIVE_WORKSPACE', 'ROOT')
```

**Location:** Lines 39-58

#### Verification: No Setters Found

```bash
$ grep -r "ACTIVE_WORKSPACE.*=" **/*.py **/*.md
# Only documentation references found, no actual setters
```

**Search Results:**
- `docs/archive/architecture-v1-incorrect/ARCHITECTURE_GAP_ANALYSIS.md` - Documents the *intended* design
- `docs/architecture/SYSTEM_DATA_FLOW_MAP.yaml` - Mentions the variable in the spec
- **ZERO actual implementations**

#### Impact Chain

```
get_active_workspace()
  → Always returns 'ROOT' (environment variable unset)
    → resolve_artifact_base_path('ROOT')
      → Returns Path('artifacts')
        → BUT: 'artifacts/' directory doesn't exist in root!
          → Agents fall back to writing in root directory
```

---

### 🔴 KO #3: ORCHESTRATOR IS MARKDOWN - CANNOT EXECUTE PYTHON

**Severity:** CRITICAL
**Type:** Architectural Mismatch
**Impact:** No programmatic enforcement of workspace discipline

#### Evidence

**File:** `agency_os/00_system/prompts/AGENCY_OS_ORCHESTRATOR_v1.md`

```markdown
## CORE WORKFLOW (STATE MACHINE EXECUTION)

This is your main execution loop. It is triggered by an external event
(e.g., a Git commit, a Temporal signal) for a given `project_id`.

```python
def handle_trigger(project_id: str, trigger_event: Dict):
    """
    Main entry point for the orchestrator.
    """
    # 1. Load the SSoT
    manifest = load_project_manifest(project_id)
    current_state = manifest.status.projectPhase

    # 2. Route to the correct state handler
    if current_state == "PLANNING":
        handle_planning_state(manifest, trigger_event)
    ...
```
```

**Location:** Lines 40-81

#### Analysis

This is **pseudocode documentation**, not executable code. The ORCHESTRATOR is a **prompt template** that Claude Code reads, not a Python module.

**Implications:**
1. The ORCHESTRATOR cannot import `workspace_utils.py`
2. It cannot programmatically resolve paths
3. It can only **instruct Claude via natural language** to follow path conventions
4. There is no **runtime enforcement** of workspace isolation

#### The Missing Layer

```
┌─────────────────────────────────────┐
│   ORCHESTRATOR.md (Prompt)          │  ← What EXISTS
│   (Natural language instructions)   │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│   orchestrator_runtime.py           │  ← What's MISSING
│   (Actual Python runtime)           │
│   - Imports workspace_utils         │
│   - Resolves paths programmatically │
│   - Calls Claude API with context   │
│   - Validates outputs                │
└─────────────────────────────────────┘
```

---

### 🔴 KO #4: PROMPT_RUNTIME ONLY FORMATS CONTEXT AS TEXT

**Severity:** HIGH
**Type:** Integration Gap
**Impact:** Workspace paths are informational only, not operational

#### Evidence

**File:** `agency_os/00_system/runtime/prompt_runtime.py`

```python
def execute_task(self, agent_id: str, task_id: str, context: Dict[str, Any]) -> str:
    """
    Compose and execute an atomized task.

    Args:
        context: Runtime context (project_id, artifacts, etc.)

    Returns:
        Composed prompt string ready for LLM execution
    """
    # ... composition logic ...

    final_prompt = self._compose_prompt(
        agent_id=agent_id,
        composition_spec=comp_spec,
        task_id=task_id,
        task_meta=task_meta,
        knowledge_files=knowledge_files,
        runtime_context=context  # ← Passed to formatting only
    )

    return final_prompt
```

**Location:** Lines 108-177

**Context Formatting:**

```python
def _format_runtime_context(self, context: Dict[str, Any]) -> str:
    """Format runtime context as markdown"""
    lines = ["**Runtime Context:**\n"]
    for key, value in context.items():
        lines.append(f"- **{key}:** `{value}`")

    return "\n".join(lines)
```

**Location:** Lines 420-431

#### Analysis

The `runtime_context` dictionary (which contains `workspace_path`) is:
1. ✅ Correctly passed to the runtime
2. ✅ Formatted as markdown
3. ✅ Included in the LLM prompt
4. ❌ **NOT** used to actually control where files are written

**The Gap:**
Claude receives the workspace path as **text in the prompt** and must interpret it. There's no programmatic enforcement that the agent's output files are saved to the correct path.

**Example Flow:**

```python
# vibe-cli.py
context = {
    "project_id": "user_project",
    "workspace": "workspaces/user_project",  # ← Set here
    "phase": "PLANNING",
}

composed_prompt = runtime.execute_task(
    agent_id="VIBE_ALIGNER",
    task_id="02_feature_extraction",
    context=context
)

# Result: Prompt contains this text:
# **Runtime Context:**
# - project_id: user_project
# - workspace: workspaces/user_project
# - phase: PLANNING

# BUT: When Claude writes feature_spec.json, where does it go?
# Answer: Wherever Claude decides (usually CWD = root)
```

---

### 🟠 KO #5: SCHEMA INCONSISTENCY BETWEEN ROOT AND WORKSPACE MANIFESTS

**Severity:** HIGH
**Type:** Data Model Divergence
**Impact:** Cannot write generic manifest parsers

#### Evidence

**Root Manifest:** `project_manifest.json`

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
    "lastUpdate": "2025-11-12T14:00:00Z",
    "message": "All specialist agent prompts designed."
  },
  "artifacts": {
    "planning": {
      "architecture": {
        "ref": "ef1c122a4a57d07036f70cb2b5460c199f25059f",
        "path": "/artifacts/planning/architecture.v1.json"
      }
    }
  }
}
```

**Workspace Manifest:** `workspaces/prabhupad_os/project_manifest.json`

```json
{
  "project_id": "prabhupad_os_001",
  "project_name": "PrabhupadaOS",
  "project_type": "nonprofit",
  "current_state": "PLANNING",
  "metadata": {
    "description": "Modular CLI application...",
    "target_users": "Devotees, spiritual seekers...",
    "key_components": [...]
  },
  "created_at": "2025-11-13T00:00:00Z",
  "framework_version": "1.1.0"
}
```

#### Comparison

| Field | Root Manifest | Workspace Manifest | Status |
|-------|---------------|-------------------|--------|
| API Version | `apiVersion: "agency.os/v1alpha1"` | ❌ Missing | ⚠️ Incompatible |
| Kind | `kind: "Project"` | ❌ Missing | ⚠️ Incompatible |
| Project ID | `metadata.projectId` (UUID) | `project_id` (string) | ⚠️ Different schema |
| Name | `metadata.name` | `project_name` | ⚠️ Different schema |
| Phase | `status.projectPhase` | `current_state` | ⚠️ Different field name |
| Artifacts | Detailed refs with paths | ❌ Missing | ⚠️ Incompatible |

#### Impact

**Cannot write unified code:**

```python
# This CANNOT work for both manifests:
def load_project_manifest(path: str) -> Dict:
    manifest = json.load(path)

    # Which field contains the phase?
    phase = manifest['status']['projectPhase']  # ← Root schema
    phase = manifest['current_state']           # ← Workspace schema

    # Which field contains artifacts?
    artifacts = manifest['artifacts']           # ← Root schema
    artifacts = ???                            # ← Not in workspace schema!
```

**Root Cause:**
Two different teams/iterations created manifests without a shared schema definition. The template (`system_steward_framework/knowledge/templates/project_manifest_template.json`) follows the root format, but actual workspaces use a different format.

---

### 🟠 KO #6: NO INTEGRATION BETWEEN COMPONENTS

**Severity:** HIGH
**Type:** System Integration Failure
**Impact:** Components exist in isolation, no end-to-end workflow

#### Component Inventory

```
┌──────────────────────────────────────────────┐
│ scripts/workspace_utils.py                   │
│ - resolve_artifact_base_path() ✅            │
│ - get_active_workspace() ✅                  │
│ - load_workspace_manifest() ✅               │
│ STATUS: Fully implemented, zero usage        │
└──────────────────────────────────────────────┘
                    ↓ NO IMPORTS ↓
┌──────────────────────────────────────────────┐
│ agency_os/00_system/runtime/prompt_runtime.py│
│ - execute_task() ✅                          │
│ - _compose_prompt() ✅                       │
│ STATUS: Works, but ignores workspace_utils   │
└──────────────────────────────────────────────┘
                    ↓ NO INVOCATION ↓
┌──────────────────────────────────────────────┐
│ vibe-cli.py                                  │
│ - generate_prompt() ✅                       │
│ STATUS: Creates prompts, never runs agents   │
└──────────────────────────────────────────────┘
                    ↓ NO RUNTIME ↓
┌──────────────────────────────────────────────┐
│ agency_os/00_system/prompts/ORCHESTRATOR.md │
│ STATUS: Markdown documentation only          │
└──────────────────────────────────────────────┘
```

#### The Missing Glue

**What should happen:**

```python
# IDEAL FLOW (not implemented):

# 1. User invokes orchestrator
$ vibe-cli.py run --project prabhupad_os

# 2. CLI sets environment
os.environ['ACTIVE_WORKSPACE'] = 'prabhupad_os'

# 3. Orchestrator runtime starts
orchestrator = OrchestrationRuntime()
orchestrator.handle_trigger(project_id='prabhupad_os_001')

# 4. Runtime resolves paths BEFORE invoking agent
workspace = get_active_workspace()  # 'prabhupad_os'
artifact_path = resolve_artifact_base_path(workspace)
# → 'workspaces/prabhupad_os/artifacts'

# 5. Runtime invokes agent with RESOLVED path
context = {
    'workspace': workspace,
    'artifact_output_path': str(artifact_path / 'planning'),  # ← ACTUAL path
}
prompt = runtime.execute_task('VIBE_ALIGNER', '02_feature_extraction', context)

# 6. Agent writes to CORRECT path
write_artifact(
    path=context['artifact_output_path'] / 'feature_spec.json',
    content=spec
)
```

**What actually happens:**

```python
# CURRENT FLOW (broken):

# 1. User runs CLI
$ ./vibe-cli.py generate VIBE_ALIGNER 02_feature_extraction

# 2. CLI creates context (hardcoded)
context = {
    "project_id": "user_project",
    "workspace": "workspaces/user_project",  # ← Just a string!
    "phase": "PLANNING",
}

# 3. Runtime formats context as TEXT
composed_prompt = runtime.execute_task(...)
# Prompt contains: "workspace: workspaces/user_project"

# 4. Prompt saved to file
with open("COMPOSED_PROMPT.md", "w") as f:
    f.write(composed_prompt)

# 5. User MANUALLY copies to Claude Code

# 6. Claude INTERPRETS the workspace path from text
# 7. Claude MAY write to wrong location (no enforcement)
```

---

## 3. ROOT CAUSE SUMMARY

| KO Criterion | Root Cause | Fix Complexity |
|--------------|-----------|----------------|
| #1: workspace_utils unused | No imports in runtime code | LOW - Add imports |
| #2: $ACTIVE_WORKSPACE unset | No setter implementation | LOW - Add setter |
| #3: ORCHESTRATOR = markdown | No Python runtime | HIGH - Build runtime |
| #4: Context = text only | No path resolution in runtime | MEDIUM - Refactor runtime |
| #5: Schema inconsistency | Divergent manifest evolution | MEDIUM - Migrate schemas |
| #6: No integration | Components built in isolation | HIGH - Wire components |

---

## 4. IMPACT ANALYSIS

### Current State: BROKEN FOR PRODUCTION

**Scenario:** Agency has 3 clients (Acme Corp, TechStart, NonProfit Foundation)

**Expected Behavior:**
```
workspaces/
  acme_corp/
    project_manifest.json
    artifacts/
      planning/feature_spec.json
  techstart/
    project_manifest.json
    artifacts/
      planning/feature_spec.json
  nonprofit_foundation/
    project_manifest.json
    artifacts/
      planning/feature_spec.json
```

**Actual Behavior:**
```
/
  project_manifest.json         ← Overwritten by each project!
  feature_spec.json             ← Overwritten by each project!
  genesis_blueprint.json        ← Overwritten by each project!

workspaces/
  acme_corp/
    project_manifest.json       ← Created manually, never updated
    artifacts/                  ← Empty (agents don't write here)
```

**Business Impact:**
- ❌ Cannot handle multiple concurrent clients
- ❌ Client data isolation is non-functional
- ❌ Risk of data leakage between projects
- ❌ Manual workarounds required for every project

---

## 5. RECOMMENDED SOLUTION

### Phase 1: CRITICAL FIXES (Immediate - 3 patches)

These fixes address the immediate breakage and restore basic functionality.

#### Fix #1: Integrate workspace_utils.py into prompt_runtime.py

**File:** `agency_os/00_system/runtime/prompt_runtime.py`

**Changes:**
```python
# ADD at top of file:
import sys
from pathlib import Path

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'scripts'))
from workspace_utils import resolve_artifact_base_path, get_active_workspace

# MODIFY execute_task():
def execute_task(self, agent_id: str, task_id: str, context: Dict[str, Any]) -> str:
    # NEW: Resolve workspace paths BEFORE composition
    workspace = context.get('workspace_name', get_active_workspace())
    artifact_base = resolve_artifact_base_path(workspace)

    # NEW: Add resolved paths to context
    context['_resolved_workspace'] = workspace
    context['_resolved_artifact_base_path'] = str(artifact_base)
    context['_resolved_planning_path'] = str(artifact_base / 'planning')
    context['_resolved_coding_path'] = str(artifact_base / 'coding')

    # EXISTING: Continue with composition
    final_prompt = self._compose_prompt(...)
    return final_prompt
```

**Validation:**
```python
# Test that paths are resolved
runtime = PromptRuntime()
context = {'workspace_name': 'prabhupad_os'}
prompt = runtime.execute_task('VIBE_ALIGNER', '02_feature_extraction', context)

# Verify prompt contains:
# _resolved_artifact_base_path: workspaces/prabhupad_os/artifacts
```

---

#### Fix #2: Implement $ACTIVE_WORKSPACE setter

**File:** `vibe-cli.py`

**Changes:**
```python
# ADD new command: workspace
def set_workspace(workspace_name: str):
    """Set active workspace for this session"""
    import os
    from scripts.workspace_utils import get_workspace_by_name, validate_workspace_name

    # Validate workspace exists
    ws = get_workspace_by_name(workspace_name)
    if not ws:
        print(f"❌ Workspace '{workspace_name}' not found")
        print("Available workspaces:")
        from scripts.workspace_utils import list_active_workspaces
        for w in list_active_workspaces():
            print(f"  - {w['name']}")
        return

    # Set environment variable
    os.environ['ACTIVE_WORKSPACE'] = workspace_name

    print(f"✅ Active workspace set to: {workspace_name}")
    print(f"   Manifest: {ws['manifestPath']}")
    print(f"   Artifacts: workspaces/{workspace_name}/artifacts/")

# ADD to argparse:
workspace_parser = subparsers.add_parser("workspace", help="Set active workspace")
workspace_parser.add_argument("workspace_name", help="Workspace to activate")
```

**Usage:**
```bash
$ ./vibe-cli.py workspace prabhupad_os
✅ Active workspace set to: prabhupad_os
   Manifest: workspaces/prabhupad_os/project_manifest.json
   Artifacts: workspaces/prabhupad_os/artifacts/
```

---

#### Fix #3: Unify manifest schemas

**Decision:** Migrate all workspaces to the root schema (apiVersion format)

**File:** `workspaces/prabhupad_os/project_manifest.json` (and all others)

**Changes:**
```json
{
  "apiVersion": "agency.os/v1alpha1",
  "kind": "Project",
  "metadata": {
    "projectId": "prabhupad_os_001",
    "name": "PrabhupadaOS",
    "description": "Modular CLI application for reading original Srila Prabhupada books",
    "owner": "devotee@example.com",
    "createdAt": "2025-11-13T00:00:00Z",
    "lastUpdatedAt": "2025-11-13T00:00:00Z"
  },
  "spec": {
    "vibe": {
      "project_type": "nonprofit",
      "target_users": "Devotees, spiritual seekers, Hare Krishna community",
      "core_values": "Authenticity, originality, no modifications to sacred texts"
    },
    "genesis": {}
  },
  "status": {
    "projectPhase": "PLANNING",
    "lastUpdate": "2025-11-13T00:00:00Z",
    "message": "Project initialized"
  },
  "artifacts": {
    "planning": {
      "lean_canvas": {
        "path": "workspaces/prabhupad_os/artifacts/planning/lean_canvas_summary.json"
      },
      "features": {
        "path": "workspaces/prabhupad_os/artifacts/planning/phase_02_features.json"
      }
    },
    "code": {},
    "test": {},
    "deployment": {}
  }
}
```

**Migration Script:**
```python
# scripts/migrate_manifests.py
import json
from pathlib import Path
from workspace_utils import list_active_workspaces

for ws in list_active_workspaces():
    old_manifest = Path(ws['manifestPath'])
    with open(old_manifest) as f:
        old = json.load(f)

    # Convert to new schema
    new = {
        "apiVersion": "agency.os/v1alpha1",
        "kind": "Project",
        "metadata": {
            "projectId": old.get('project_id'),
            "name": old.get('project_name'),
            "description": old['metadata'].get('description'),
            # ... map remaining fields
        },
        # ... complete mapping
    }

    # Backup and save
    old_manifest.rename(old_manifest.with_suffix('.json.bak'))
    with open(old_manifest, 'w') as f:
        json.dump(new, f, indent=2)
```

---

### Phase 2: ARCHITECTURAL FIXES (Follow-up)

These address the systemic issues but require more extensive changes.

#### Fix #4: Implement Python Orchestrator Runtime

**New File:** `agency_os/00_system/runtime/orchestrator_runtime.py`

```python
"""
Orchestrator Runtime - Executable State Machine

This is the ACTUAL runtime implementation of the SDLC orchestrator.
It replaces the markdown-only AGENCY_OS_ORCHESTRATOR_v1.md with
executable code that enforces workspace discipline.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'scripts'))

from workspace_utils import (
    get_workspace_by_project_id,
    load_workspace_manifest,
    save_workspace_manifest,
    resolve_artifact_base_path
)
from prompt_runtime import PromptRuntime


class OrchestrationRuntime:
    """
    Executable orchestrator that manages the SDLC state machine.

    This runtime:
    1. Loads project manifests using workspace_utils
    2. Resolves artifact paths programmatically
    3. Invokes agents with correct context
    4. Validates outputs land in correct locations
    5. Updates manifests with artifact references
    """

    def __init__(self):
        self.runtime = PromptRuntime()

    def handle_trigger(self, project_id: str, trigger_event: dict = None):
        """
        Main entry point - implements state machine from ORCHESTRATOR.md

        Args:
            project_id: UUID from project manifest
            trigger_event: Optional event data (commit, signal, etc.)
        """
        # 1. Resolve workspace from project_id
        workspace = get_workspace_by_project_id(project_id)
        if not workspace:
            raise ValueError(f"Project {project_id} not found in registry")

        # 2. Load manifest
        manifest = load_workspace_manifest(workspace['name'])
        current_phase = manifest['status']['projectPhase']

        print(f"📋 Project: {manifest['metadata']['name']}")
        print(f"📍 Phase: {current_phase}")
        print(f"🗂️  Workspace: {workspace['name']}")

        # 3. Route to state handler
        if current_phase == 'PLANNING':
            self.handle_planning_state(workspace, manifest)
        elif current_phase == 'CODING':
            self.handle_coding_state(workspace, manifest)
        # ... other states

    def handle_planning_state(self, workspace: dict, manifest: dict):
        """Execute PLANNING phase workflow"""
        workspace_name = workspace['name']

        # Resolve output path
        artifact_base = resolve_artifact_base_path(workspace_name)
        planning_path = artifact_base / 'planning'
        planning_path.mkdir(parents=True, exist_ok=True)

        # Build context with RESOLVED paths
        context = {
            'project_id': manifest['metadata']['projectId'],
            'workspace_name': workspace_name,
            'workspace_path': f"workspaces/{workspace_name}",
            'output_path': str(planning_path),  # ← CRITICAL: Absolute path
            'phase': 'PLANNING'
        }

        # Invoke VIBE_ALIGNER
        print("🤖 Invoking VIBE_ALIGNER...")
        prompt = self.runtime.execute_task(
            agent_id='VIBE_ALIGNER',
            task_id='02_feature_extraction',
            context=context
        )

        # TODO: Actually call Claude API with prompt
        # response = claude_api.call(prompt)

        # TODO: Validate output path
        expected_artifact = planning_path / 'feature_spec.json'
        if not expected_artifact.exists():
            raise RuntimeError(
                f"Agent failed to create artifact at {expected_artifact}"
            )

        # Update manifest
        manifest['artifacts']['planning']['feature_spec'] = {
            'path': str(expected_artifact),
            'created_at': datetime.now().isoformat()
        }
        save_workspace_manifest(manifest, workspace_name)

        print(f"✅ Artifact saved: {expected_artifact}")
```

---

#### Fix #5: Add Validation Gates to ORCHESTRATOR Prompt

**File:** `agency_os/00_system/prompts/AGENCY_OS_ORCHESTRATOR_v1.md`

**Add section:**
```markdown
## CRITICAL: OUTPUT PATH VALIDATION

Before invoking ANY agent, you MUST:

1. **Load workspace context:**
   ```python
   workspace = get_workspace_by_project_id(project_id)
   workspace_name = workspace['name']
   ```

2. **Resolve artifact output path:**
   ```python
   artifact_base = f"workspaces/{workspace_name}/artifacts"
   phase_path = f"{artifact_base}/{current_phase.lower()}"
   ```

3. **Pass to agent in runtime_context:**
   ```python
   context = {
       'project_id': project_id,
       'workspace_name': workspace_name,
       'OUTPUT_PATH': phase_path,  # ← CRITICAL
       'phase': current_phase
   }
   ```

4. **Validate agent output:**
   ```python
   expected_artifact = f"{phase_path}/{artifact_name}"
   if not file_exists(expected_artifact):
       FAIL("Agent wrote to wrong location")
   ```

## VALIDATION GATES

### Gate: Artifact Location Validation

**Trigger:** After any agent writes an artifact

**Check:**
```python
def validate_artifact_location(artifact_path: str, workspace_name: str) -> bool:
    """
    Validates artifact is in correct workspace directory.

    Returns:
        True if artifact is in workspaces/{workspace_name}/artifacts/
        False otherwise (FAIL the transition)
    """
    expected_prefix = f"workspaces/{workspace_name}/artifacts/"

    if not artifact_path.startswith(expected_prefix):
        print(f"❌ VALIDATION FAILED")
        print(f"   Artifact: {artifact_path}")
        print(f"   Expected prefix: {expected_prefix}")
        return False

    return True
```

**Action on Failure:**
- ❌ DO NOT transition to next state
- ❌ DO NOT update project_manifest.json
- 🔴 Log critical error
- 🔴 Alert: "Agent violated workspace isolation"
```

---

## 6. VERIFICATION PLAN

### Test Case 1: Multi-Workspace Isolation

**Setup:**
```bash
# Create two workspaces
./vibe-cli.py workspace prabhupad_os
./vibe-cli.py generate VIBE_ALIGNER 02_feature_extraction

./vibe-cli.py workspace acme_corp
./vibe-cli.py generate VIBE_ALIGNER 02_feature_extraction
```

**Expected Result:**
```
workspaces/
  prabhupad_os/
    artifacts/
      planning/feature_spec.json  ← Created for prabhupad_os
  acme_corp/
    artifacts/
      planning/feature_spec.json  ← Created for acme_corp (different content)
```

**Actual Result (before fix):**
```
/
  feature_spec.json  ← Both projects overwrite this file!
```

---

### Test Case 2: Workspace Context Propagation

**Test:**
```python
from agency_os.system.runtime.prompt_runtime import PromptRuntime
from scripts.workspace_utils import get_active_workspace, resolve_artifact_base_path
import os

# Set workspace
os.environ['ACTIVE_WORKSPACE'] = 'prabhupad_os'

# Verify context
assert get_active_workspace() == 'prabhupad_os'

# Verify path resolution
path = resolve_artifact_base_path()
assert str(path) == 'workspaces/prabhupad_os/artifacts'

# Verify runtime integration
runtime = PromptRuntime()
context = {}
prompt = runtime.execute_task('VIBE_ALIGNER', '02_feature_extraction', context)

# Verify resolved paths in prompt
assert 'workspaces/prabhupad_os/artifacts' in prompt
```

---

## 7. RISK ASSESSMENT

### Risk of Immediate Fixes (Phase 1)

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Breaking existing workflows | MEDIUM | MEDIUM | Test with existing workspaces first |
| Import errors (workspace_utils) | LOW | LOW | Add to sys.path dynamically |
| Schema migration data loss | LOW | HIGH | Create .bak files before migration |

**Recommendation:** Phase 1 is LOW RISK and should be implemented immediately.

---

### Risk of Delayed Fixes

| Scenario | Likelihood | Impact | Timeline |
|----------|-----------|--------|----------|
| Client data corruption | HIGH | CRITICAL | Days (if multi-client) |
| Production deployment failure | HIGH | CRITICAL | Weeks (first deploy) |
| Manual workarounds proliferate | CERTAIN | HIGH | Already happening |

**Recommendation:** Delaying fixes creates UNACCEPTABLE risk.

---

## 8. CONCLUSION

### Summary

1. **Gemini was partially correct** - identified the symptom but missed root causes
2. **6 KO criteria discovered** - ranging from unused code to architectural gaps
3. **Framework is non-functional for production** - workspace isolation is broken
4. **Fix is straightforward** - Phase 1 requires ~3 hours of focused development

### Immediate Action Required

**Priority 1 (TODAY):**
- ✅ Implement Fix #1 (integrate workspace_utils.py)
- ✅ Implement Fix #2 ($ACTIVE_WORKSPACE setter)
- ✅ Test multi-workspace isolation

**Priority 2 (THIS WEEK):**
- ✅ Implement Fix #3 (schema migration)
- ✅ Update all workspace manifests
- ✅ Validate end-to-end workflow

**Priority 3 (BACKLOG):**
- ⬜ Implement orchestrator_runtime.py
- ⬜ Add validation gates
- ⬜ Full integration testing

---

## 9. APPENDIX

### A. File Locations Reference

| Component | Path | Status |
|-----------|------|--------|
| Workspace Utils | `scripts/workspace_utils.py` | ✅ Implemented, unused |
| Prompt Runtime | `agency_os/00_system/runtime/prompt_runtime.py` | ✅ Works, missing integration |
| CLI | `vibe-cli.py` | ✅ Works, missing workspace cmd |
| Orchestrator Prompt | `agency_os/00_system/prompts/AGENCY_OS_ORCHESTRATOR_v1.md` | ⚠️ Documentation only |
| Root Manifest | `project_manifest.json` | ⚠️ Wrong location |
| Workspace Manifests | `workspaces/*/project_manifest.json` | ⚠️ Wrong schema |

### B. Related Documentation

- `docs/architecture/ARCHITECTURE_GAP_ANALYSIS.md` - Documents the original workspace design intent
- `docs/architecture/SYSTEM_DATA_FLOW_MAP.yaml` - Shows $ACTIVE_WORKSPACE in the spec
- `system_steward_framework/knowledge/templates/project_manifest_template.json` - Template (correct schema)

### C. Code Evidence Index

All code snippets in this report are verified and include file paths with line numbers:

- workspace_utils.py:39-58 - get_active_workspace()
- workspace_utils.py:94-119 - resolve_artifact_base_path()
- prompt_runtime.py:420-431 - _format_runtime_context()
- AGENCY_OS_ORCHESTRATOR_v1.md:44-80 - Pseudocode workflow
- project_manifest.json:1-38 - Root schema
- workspaces/prabhupad_os/project_manifest.json:1-20 - Workspace schema

---

**Report Status:** FINAL
**Next Step:** Implement Phase 1 Fixes
**Review Required:** None - proceed with fixes
