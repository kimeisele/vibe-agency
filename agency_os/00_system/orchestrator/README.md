# AGENCY OS ORCHESTRATOR
**Hybrid State Machine for SDLC Workflows**

**Version:** 2.0 (Phase 2 Implementation)
**Architecture Decision:** See [GAD-001](../../../docs/architecture/GAD-001_Research_Integration.md)

---

## Overview

The Orchestrator is a **hybrid system** that manages the Software Development Lifecycle (SDLC) state machine:

- **`orchestrator.py`** (Python) - State machine logic, routing, artifact management
- **`ORCHESTRATOR_PROMPT.md`** (Markdown) - AI personality, human communication, error handling

This separation implements GAD-001's architectural principle:
> "Python handles state machine logic (testable, maintainable). Prompts handle AI behavior (flexible, human-friendly)."

---

## Components

### 1. State Machine Loader

Reads `ORCHESTRATION_workflow_design.yaml` and parses:
- States (PLANNING, CODING, TESTING, etc.)
- Sub-states (RESEARCH, BUSINESS_VALIDATION, FEATURE_SPECIFICATION)
- Transitions (T0a_ResearchToBusiness, T0_BusinessToFeatures, etc.)
- Optional flags (RESEARCH is optional)

### 2. Agent Invoker

Loads agent prompts and executes them:
- Loads `_prompt_core.md` for agent personality
- Composes with tasks and knowledge bases
- Invokes LLM (Anthropic Claude API) - *Phase 3*
- Parses agent output (JSON)

**Phase 2 Status:** Uses mock data. Phase 3 will implement actual LLM invocation.

### 3. Artifact Manager

Reads and writes workflow artifacts:
- `research_brief.json` (from RESEARCH phase)
- `lean_canvas_summary.json` (from BUSINESS_VALIDATION phase)
- `feature_spec.json` (from FEATURE_SPECIFICATION phase)

Artifacts are stored in: `workspaces/{project_name}/artifacts/planning/`

### 4. Quality Gate Validator

Enforces blocking quality gates:
- **FACT_VALIDATOR blocking:** If quality_score < 50, blocks RESEARCH phase
- **Transition validation:** Checks required artifacts before state transitions
- **Error handling:** Raises exceptions with clear messages

### 5. Project Manifest Management

Single Source of Truth (SSoT) for project state:
- Reads/writes `project_manifest.json`
- Tracks current phase and sub-state
- Stores artifact references
- Updates on every state transition

---

## Usage

### Basic Usage

```bash
python3 agency_os/00_system/orchestrator/orchestrator.py <repo_root> <project_id>
```

**Example:**
```bash
python3 agency_os/00_system/orchestrator/orchestrator.py /home/user/vibe-agency my-project-001
```

### Workflow

The orchestrator will:

1. **Ask about RESEARCH phase** (optional):
   ```
   Do you want to run the Research phase? (y/n):
   ```

2. **Execute RESEARCH phase** (if enabled):
   - MARKET_RESEARCHER → competitor analysis, pricing, market size
   - TECH_RESEARCHER → API evaluation, library comparison, feasibility
   - FACT_VALIDATOR → citation enforcement, quality validation (BLOCKING)
   - USER_RESEARCHER (optional) → personas, interview scripts

3. **Execute BUSINESS_VALIDATION**:
   - LEAN_CANVAS_VALIDATOR → Lean Canvas interview
   - Uses research_brief.json (if available) to enrich Lean Canvas

4. **Execute FEATURE_SPECIFICATION**:
   - VIBE_ALIGNER → Feature extraction, validation, complexity estimation
   - Generates feature_spec.json

5. **Transition to CODING phase**

---

## Architecture

### Hybrid Design

```
orchestrator.py (Python)
├── Loads: ORCHESTRATION_workflow_design.yaml
├── Manages: State transitions, artifact I/O
├── Invokes: Agent prompts (via LLM)
└── Validates: Quality gates, transitions

ORCHESTRATOR_PROMPT.md (Markdown)
├── Provides: User-facing messages
├── Explains: Errors, decisions, progress
└── Guides: User through workflow
```

### Data Flow

```
User Input
    ↓
orchestrator.py
    ↓
[Optional] RESEARCH Phase
    ├─→ MARKET_RESEARCHER → market_analysis
    ├─→ TECH_RESEARCHER → tech_analysis
    ├─→ FACT_VALIDATOR → fact_validation (BLOCKING if quality < 50)
    └─→ USER_RESEARCHER → user_insights (optional)
    ↓
research_brief.json
    ↓
BUSINESS_VALIDATION
    └─→ LEAN_CANVAS_VALIDATOR (uses research_brief if available)
    ↓
lean_canvas_summary.json
    ↓
FEATURE_SPECIFICATION
    └─→ VIBE_ALIGNER
    ↓
feature_spec.json
    ↓
CODING Phase (next)
```

---

## Quality Gates

### FACT_VALIDATOR Blocking

The FACT_VALIDATOR enforces research quality:

**Blocking Conditions:**
- `quality_score < 50` → Blocks RESEARCH phase
- `issues_critical > 0` → Blocks RESEARCH phase

**Example:**
```
🚨 Quality Gate Failed: FACT_VALIDATOR

Quality score (42) is below threshold (50)

Critical problems:
- 3 competitor claims lack source URLs
- Market size estimate has no methodology
- 2 pricing claims reference outdated data

The orchestrator will NOT proceed to BUSINESS_VALIDATION.
```

### Transition Validation

State transitions are validated:
- Required artifacts must exist
- Previous phase must be complete
- State machine rules must be followed

**Example:**
```
⚠️  Missing Artifact: lean_canvas_summary.json

Cannot transition to FEATURE_SPECIFICATION.
BUSINESS_VALIDATION phase must complete first.
```

---

## Project Manifest

The orchestrator uses `project_manifest.json` as the Single Source of Truth (SSoT):

```json
{
  "metadata": {
    "projectId": "my-project-001",
    "name": "My Project"
  },
  "status": {
    "projectPhase": "PLANNING",
    "planningSubState": "RESEARCH",
    "message": "Executing RESEARCH phase"
  },
  "artifacts": {
    "research_brief": { ... },
    "lean_canvas_summary": { ... },
    "feature_spec": { ... }
  }
}
```

**Key Fields:**
- `projectPhase`: Current lifecycle phase (PLANNING, CODING, TESTING, etc.)
- `planningSubState`: Current sub-state within PLANNING (RESEARCH, BUSINESS_VALIDATION, FEATURE_SPECIFICATION)
- `artifacts`: References to generated artifacts

---

## Testing

### Test 1: Skip Research Phase

```bash
echo "n" | python3 agency_os/00_system/orchestrator/orchestrator.py /home/user/vibe-agency test-project-001
```

**Expected:**
- Skips RESEARCH phase
- Executes BUSINESS_VALIDATION → lean_canvas_summary.json
- Executes FEATURE_SPECIFICATION → feature_spec.json
- Transitions to CODING

### Test 2: Enable Research Phase

```bash
printf "y\ny\n" | python3 agency_os/00_system/orchestrator/orchestrator.py /home/user/vibe-agency test-project-002
```

**Expected:**
- Executes RESEARCH phase → research_brief.json
- Executes BUSINESS_VALIDATION (uses research_brief)
- Executes FEATURE_SPECIFICATION
- Transitions to CODING

### Test 3: FACT_VALIDATOR Blocking

```bash
TEST_FACT_VALIDATOR_FAILURE=1 printf "y\nn\n" | python3 agency_os/00_system/orchestrator/orchestrator.py /home/user/vibe-agency test-project-003
```

**Expected:**
- Starts RESEARCH phase
- FACT_VALIDATOR returns quality_score = 42 (< 50)
- QualityGateFailure exception raised
- Execution stops (does not proceed to BUSINESS_VALIDATION)

---

## Phase 2 Status

**Implemented:**
- ✅ State machine loader (YAML parsing)
- ✅ Project manifest management (SSoT)
- ✅ Artifact I/O (research_brief.json, lean_canvas_summary.json, feature_spec.json)
- ✅ RESEARCH phase handler (4 agents: MARKET, TECH, FACT, USER)
- ✅ FACT_VALIDATOR blocking logic (quality gate)
- ✅ Optional phase handling (user can skip RESEARCH)
- ✅ State transitions (PLANNING → CODING)
- ✅ Mock agent execution (for testing)

**Phase 3 TODO:**
- ⏳ Real LLM invocation (Anthropic Claude API)
- ⏳ Agent prompt loading and composition
- ⏳ Advanced error handling and retry logic
- ⏳ Progress indicators for long-running agents
- ⏳ Integration with ORCHESTRATOR_PROMPT.md for rich user communication

---

## Dependencies

Install dependencies:

```bash
pip install -r requirements.txt
```

**Requirements:**
- `PyYAML>=6.0` - YAML parsing for workflow design
- `anthropic>=0.18.0` - Anthropic Claude API (Phase 3)

---

## File Structure

```
agency_os/00_system/orchestrator/
├── orchestrator.py              # Python orchestrator (Phase 2)
├── ORCHESTRATOR_PROMPT.md       # AI personality and communication
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

---

## Related Documentation

- **Architecture Decision:** [GAD-001](../../../docs/architecture/GAD-001_Research_Integration.md)
- **Workflow Design:** [ORCHESTRATION_workflow_design.yaml](../state_machine/ORCHESTRATION_workflow_design.yaml)
- **Research Workflow:** [RESEARCH_workflow_design.yaml](../../01_planning_framework/state_machine/RESEARCH_workflow_design.yaml)
- **Research Agents:** [01_planning_framework/agents/research/](../../01_planning_framework/agents/research/)

---

**Version:** 2.0
**Status:** Phase 2 Complete (Mock execution)
**Next:** Phase 3 (Real LLM invocation)
