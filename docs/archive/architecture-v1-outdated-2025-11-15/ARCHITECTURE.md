# VIBE-AGENCY SYSTEM ARCHITECTURE

**Document Status:** Definitive Technical Reference
**Last Updated:** 2025-11-15
**Scope:** Complete system architecture as implemented in v2.0

---

## EXECUTIVE SUMMARY

The vibe-agency is a **hierarchical AI-driven SDLC orchestration system** that manages complete software project workflows from planning through production. It consists of:

- **Core Orchestrator** (1,252 lines) - State machine controller
- **5 Phase Frameworks** - Planning, Coding, Testing, Deployment, Maintenance
- **System Steward Framework** - Governance and auditing
- **Prompt Runtime** (660 lines) - Dynamic prompt composition engine
- **Tool Integration Layer** - Research tools (google_search, web_fetch)
- **37 Specialized Agents** - Domain experts for each workflow phase

**Current Status:** ⚠️ **STRUCTURALLY COMPLETE, FUNCTIONALLY INCOMPLETE**
- Core architecture implemented and tested
- GAD-003 identified critical integration gaps preventing tool execution
- Delegated execution mode (default) will deadlock on STDIN/STDOUT handoff

---

## CORE COMPONENTS

### 1. Core Orchestrator (`core_orchestrator.py`)

**Location:** `agency_os/core_system/orchestrator/core_orchestrator.py` (1,252 lines)

**Responsibilities:**
- Manages SDLC state machine across 7 phases
- Loads/persists ProjectManifest (Single Source of Truth)
- Routes to phase-specific handlers via lazy loading
- Validates artifacts against schemas
- Enforces quality gates (blocking/async)
- Tracks costs and budget
- Implements delegated execution mode (STDOUT/STDIN protocol)

**Key Classes:**
```python
class CoreOrchestrator:
    def __init__(repo_root, workflow_yaml, contracts_yaml, execution_mode)
    def load_project_manifest(project_id) → ProjectManifest
    def save_project_manifest(manifest)
    def execute_phase(manifest) → executes phase handler
    def execute_agent(agent_name, task_id, inputs, manifest) → delegates to handler
    def apply_quality_gates(transition_name, manifest) → invokes AUDITOR
    def invoke_auditor(check_type, manifest, severity, blocking)
    def _request_intelligence(agent_name, task_id, prompt, manifest) → STDIN/STDOUT protocol
    def _parse_tool_use(text) → extracts <tool_use> XML
```

**Execution Modes:**
- `delegated` (default): Sends `INTELLIGENCE_REQUEST` to STDOUT, reads responses from STDIN ⚠️ **BROKEN**
- `autonomous` (legacy): Direct Anthropic API calls via LLMClient ✅ **WORKS**

**Data Structures:**
```python
@dataclass
class ProjectManifest:
    project_id: str
    name: str
    current_phase: ProjectPhase  # PLANNING | CODING | TESTING | AWAITING_QA_APPROVAL | DEPLOYMENT | PRODUCTION | MAINTENANCE
    current_sub_state: PlanningSubState  # For PLANNING phase: RESEARCH | BUSINESS_VALIDATION | FEATURE_SPECIFICATION | ARCHITECTURE_DESIGN
    artifacts: Dict[str, Any]  # All phase outputs (research_brief.json, feature_spec.json, etc.)
    budget: Dict[str, Any]  # {max_cost_usd, current_cost_usd, cost_breakdown}
    metadata: Dict[str, Any]  # {projectId, name, owner, createdAt, updatedAt}
```

---

### 2. Phase Handlers

**Location:** `agency_os/core_system/orchestrator/handlers/`

Each handler executes a phase by invoking agents sequentially:

#### a) PlanningHandler (`planning_handler.py`)
**Workflow:**
1. **RESEARCH** (optional) → `research_brief.json`
   - MARKET_RESEARCHER → market_analysis
   - TECH_RESEARCHER → tech_analysis
   - FACT_VALIDATOR → fact_validation
   - USER_RESEARCHER (optional) → user_insights
2. **BUSINESS_VALIDATION** → `lean_canvas_summary.json`
   - LEAN_CANVAS_VALIDATOR validates business model
3. **FEATURE_SPECIFICATION** → `feature_spec.json`
   - VIBE_ALIGNER extracts features from vision
4. **ARCHITECTURE_DESIGN** → `architecture.json`, `code_gen_spec.json`
   - GENESIS_BLUEPRINT designs system architecture

**Quality Gates:** Prompt security scan, data privacy scan (blocking)

#### b) CodingHandler (`coding_handler.py`)
- Invokes CODE_GENERATOR (5-phase sequential workflow)
- Input: `feature_spec.json`
- Output: `artifact_bundle` (code files)
- Quality Gates: Code security, license compliance

#### c) TestingHandler (`testing_handler.py`)
- Invokes QA_VALIDATOR
- Executes test pyramid (unit → integration → e2e)
- Output: `qa_report.json`
- Transitions to **AWAITING_QA_APPROVAL** (durable wait state)

#### d) DeploymentHandler (`deployment_handler.py`)
- Invokes DEPLOY_MANAGER
- Requires `qa_approved` flag (HITL approval via `vibe-cli approve-qa`)
- Output: `deploy_receipt.json`

#### e) MaintenanceHandler (`maintenance_handler.py`)
- Event-driven (triggered by bug reports)
- Invokes BUG_TRIAGE
- Loops back to CODING for fixes

---

### 3. Prompt Runtime (`prompt_runtime.py`)

**Location:** `agency_os/core_system/runtime/prompt_runtime.py` (660 lines)

**Purpose:** Dynamically compose prompts from modular fragments

**Composition Pipeline:**
1. Load `_composition.yaml` - Define composition order
2. Load task metadata - `task_*.meta.yaml` (phase, description, gates, dependencies)
3. Resolve knowledge dependencies - Load YAML knowledge bases based on task
4. Compose final prompt in order:
   - Core personality (`_prompt_core.md`)
   - Tool definitions (if GAD-003 enabled)
   - Knowledge base files
   - Task instructions
   - Validation gates
   - Runtime context

**Key Methods:**
```python
class PromptRuntime:
    def execute_task(agent_id, task_id, context) → str  # Composed prompt
    def _load_composition_spec(agent_id) → CompositionSpec
    def _load_task_metadata(agent_id, task_id) → TaskMetadata
    def _resolve_knowledge_deps(agent_id, task_meta) → List[str]
    def _compose_prompt(...) → str
    def _compose_tools_section(...) → str  # GAD-003: Formats tool definitions as markdown
```

**Agent Registry (37 agents):**
- Planning: LEAN_CANVAS_VALIDATOR, VIBE_ALIGNER, GENESIS_BLUEPRINT, GENESIS_UPDATE
- Research: MARKET_RESEARCHER, TECH_RESEARCHER, FACT_VALIDATOR, USER_RESEARCHER
- Code Gen: CODE_GENERATOR
- QA: QA_VALIDATOR
- Deployment: DEPLOY_MANAGER
- Maintenance: BUG_TRIAGE
- System: AUDITOR, LEAD_ARCHITECT, SSF_ROUTER
- System Orchestrator: AGENCY_OS_ORCHESTRATOR

---

### 4. LLM Client (`llm_client.py`)

**Location:** `agency_os/core_system/runtime/llm_client.py`

**Features:**
- Graceful failover (NoOpClient if no API key)
- Retry logic with exponential backoff (up to 3 attempts)
- Cost tracking by invocation
- Budget enforcement (optional per-project limits)
- Token counting (input/output)
- Pricing: Claude 3.5 Sonnet $3/M input, $15/M output

**Modes:**
- `anthropic` - Uses Anthropic API ✅
- `noop` - Returns empty JSON when API key missing (knowledge-only mode) ✅

---

### 5. Tool Infrastructure (GAD-003 Phase 1 & 2)

**Location:** `agency_os/core_system/orchestrator/tools/`

#### Tool Definitions (`tool_definitions.yaml`)
Defines 2 research tools:

1. **google_search**
   - Parameters: `query` (string, required), `num_results` (int, optional, default 10)
   - Returns: List of `{title, snippet, url}`

2. **web_fetch**
   - Parameters: `url` (string, required)
   - Returns: `{url, title, content, error}`

#### Tool Clients
- `google_search_client.py` - Google Custom Search API wrapper
- `web_fetch_client.py` - HTML content extraction with BeautifulSoup

#### Tool Executor (`tool_executor.py`)
```python
class ToolExecutor:
    def execute(tool_name: str, parameters: Dict) → Dict
```
Routes tool calls to appropriate client. Used by orchestrator in STDIN/STDOUT protocol.

**Status:** ✅ **Implementation complete** | ❌ **Integration incomplete** (GAD-003 Gap #1)

---

## DATA FLOWS

### Flow 1: Manifest Lifecycle

```
1. [Init] User creates project via vibe-cli or orchestrator
   ↓
2. [Create] project_manifest.json written to workspaces/{project_id}/
   ├── status.projectPhase = "PLANNING"
   ├── status.planningSubState = (optional)
   ├── artifacts = {} (empty)
   ├── budget = {max_cost_usd, current_cost_usd, ...}
   └── metadata = {projectId, name, owner, createdAt}
   ↓
3. [Load] CoreOrchestrator.load_project_manifest(project_id)
   ├── Validates manifest structure
   ├── Parses projectPhase enum
   ├── Returns ProjectManifest object
   ↓
4. [Execute] CoreOrchestrator.execute_phase(manifest)
   ├── Gets phase handler via get_phase_handler(phase)
   ├── Handler executes agents & creates artifacts
   ├── Saves artifacts to workspaces/{project_id}/artifacts/{phase}/
   ↓
5. [Persist] CoreOrchestrator.save_project_manifest(manifest)
   ├── Updates manifest.current_phase
   ├── Updates manifest.artifacts
   ├── Updates manifest.budget
   ├── Writes to disk as JSON
   ↓
6. [Repeat] Until phase = PRODUCTION or error
```

---

### Flow 2: Agent Execution (Delegated Mode - BROKEN)

```
1. Phase Handler calls:
   orchestrator.execute_agent(
       agent_name="VIBE_ALIGNER",
       task_id="02_feature_extraction",
       inputs={project_id, artifacts, ...},
       manifest=ProjectManifest
   )
   ↓
2. CoreOrchestrator.execute_agent():
   a. Calls PromptRuntime.execute_task(agent_id, task_id, inputs)
      → Returns composed prompt (1000-5000 lines markdown)
   ↓
   b. Routes to execution mode:

      IF execution_mode == "delegated":  ← DEFAULT MODE
         Call _request_intelligence(agent_name, task_id, prompt, manifest)

      IF execution_mode == "autonomous":
         Call _execute_autonomous(agent_name, prompt, manifest)
   ↓
3. Delegated Mode (_request_intelligence):  ⚠️ BROKEN - NO CONSUMER

   a. Build INTELLIGENCE_REQUEST JSON:
      {
        "type": "INTELLIGENCE_REQUEST",
        "agent": "VIBE_ALIGNER",
        "task_id": "02_feature_extraction",
        "prompt": "... composed prompt ...",
        "context": {
          "project_id": "...",
          "phase": "PLANNING",
          "sub_state": null
        },
        "wait_for_response": true
      }

   b. Write to STDOUT (with markers to stderr):
      print("---INTELLIGENCE_REQUEST_START---") [stderr]
      print(JSON) [stdout]
      print("---INTELLIGENCE_REQUEST_END---") [stderr]

   c. BLOCKING LOOP ❌ DEADLOCK - NO CONSUMER READS STDOUT:
      while True:
         response_line = sys.stdin.readline()  ← BLOCKS FOREVER

         IF "<tool_use>" in response:
            tool_call = _parse_tool_use(response)
            result = tool_executor.execute(tool['name'], tool['params'])

            Send TOOL_RESULT to stdout:
            {
              "type": "TOOL_RESULT",
              "tool": "google_search",
              "result": {...}
            }

            Continue loop (wait for next response)

         ELIF response is INTELLIGENCE_RESPONSE:
            Extract result field
            Return to handler

         ELSE:
            Pass through to stderr
   ↓
4. Autonomous Mode (_execute_autonomous):  ✅ WORKS

   a. Initialize LLMClient(budget_limit=manifest.budget['max_cost_usd'])
   b. Call client.invoke(prompt, model, max_tokens)
   c. Update manifest.budget with usage costs
   d. Parse JSON response
   e. Return to handler
```

---

### Flow 3: Prompt Composition

```
1. Phase Handler calls: orchestrator.execute_agent()
   ↓
2. PromptRuntime.execute_task(agent_id="VIBE_ALIGNER", task_id="02_feature_extraction", context)
   ↓
3. _load_composition_spec("VIBE_ALIGNER")
   └─ Read: agency_os/01_planning_framework/agents/VIBE_ALIGNER/_composition.yaml
   └─ Returns CompositionSpec with composition_order:
      [
        {source: "_prompt_core.md", type: "base"},
        {source: "${knowledge_files}", type: "knowledge"},
        {source: "${task_prompt}", type: "task"},
        {source: "${gate_prompts}", type: "validation"},
        {source: "${runtime_context}", type: "context"}
      ]
   ↓
4. _load_task_metadata("VIBE_ALIGNER", "02_feature_extraction")
   └─ Read: agency_os/01_planning_framework/agents/VIBE_ALIGNER/tasks/task_02_feature_extraction.meta.yaml
   └─ Returns TaskMetadata with gates, phase, complexity
   ↓
5. _resolve_knowledge_deps("VIBE_ALIGNER", task_meta)
   └─ Read: agency_os/01_planning_framework/agents/VIBE_ALIGNER/_knowledge_deps.yaml
   └─ For each knowledge file in used_in_tasks:
      └─ Load YAML (cached)
      └─ Returns list of knowledge file contents
   ↓
6. _compose_prompt(agent_id, comp_spec, task_id, task_meta, knowledge, runtime_context)
   └─ For each step in composition_order:
      - If type="base": Load _prompt_core.md
      - If type="tools" (GAD-003): Call _compose_tools_section()
        └─ Load tool_definitions.yaml
        └─ Filter to tools specified in composition_spec
        └─ Format as markdown with XML usage instructions
      - If type="knowledge": Append all knowledge files
      - If type="task": Load task_*.md instructions
      - If type="validation": Load gate_*.md files
      - If type="context": Format runtime_context as markdown
   ↓
7. Return composed_prompt (markdown, 2000-10000 chars)
```

---

### Flow 4: Quality Gates & Auditing

```
1. Phase handler completes execution
   ↓
2. CoreOrchestrator.run_horizontal_audits(manifest)
   ├─ Finds current phase in workflow YAML
   ├─ Reads horizontal_audits section
   ├─ For each audit:
   │  └─ invoke_auditor(check_type, manifest, severity, blocking)
   │     └─ execute_agent("AUDITOR", "semantic_audit", audit_context, manifest)
   │        └─ AUDITOR scans artifacts/code/prompts for issues
   │        └─ Returns audit_report {status, findings, timestamp}
   ├─ If blocking audit fails → raise QualityGateFailure
   ├─ If async audit fails → log warning, continue
   └─ Store results in manifest.artifacts['horizontal_audits']
   ↓
3. Before state transitions:
   apply_quality_gates(transition_name, manifest)
   ├─ Looks up transition in workflow YAML
   ├─ Runs blocking gates first (must pass)
   └─ Runs async gates (fire & forget)
```

---

## INTEGRATION POINTS

### 1. Orchestrator ↔ Phase Handlers
**Mechanism:** Lazy-loaded handler classes with orchestrator reference

```python
# In CoreOrchestrator.__init__
self._handlers = {}  # Lazy cache

# In CoreOrchestrator.get_phase_handler(phase)
from handlers.planning_handler import PlanningHandler
self._handlers[ProjectPhase.PLANNING] = PlanningHandler(self)
```

**Data Passed:** ProjectManifest (mutable reference)

---

### 2. Orchestrator ↔ PromptRuntime
**Mechanism:** Direct method calls

```python
# In CoreOrchestrator.execute_agent()
prompt = self.prompt_runtime.execute_task(
    agent_name=agent_name,
    task_id=task_id,
    inputs=inputs
)
```

**Data Passed:** Composed prompt string (markdown)

---

### 3. Orchestrator ↔ LLMClient (Autonomous Mode Only)
**Mechanism:** Direct instantiation with budget

```python
# In CoreOrchestrator._execute_autonomous()
self.llm_client = LLMClient(budget_limit=manifest.budget['max_cost_usd'])
response = self.llm_client.invoke(prompt, model, max_tokens)
```

**Status:** ✅ **WORKS**

---

### 4. Orchestrator ↔ Claude Code (Delegated Mode - BROKEN)
**Mechanism:** STDOUT/STDIN protocol with JSON messages

```
Orchestrator (stdout) ─→ INTELLIGENCE_REQUEST → ??? (NO CONSUMER)
                                                       ↓
Orchestrator (stdin) ←── INTELLIGENCE_RESPONSE ← ??? (NO SENDER)
                    ←──── TOOL_RESULT ──────────
```

**Protocol Messages:**
- `INTELLIGENCE_REQUEST`: `{type, agent, task_id, prompt, context, wait_for_response}`
- `TOOL_RESULT`: `{type, tool, result}`
- `INTELLIGENCE_RESPONSE`: `{type, result}`

**Status:** ❌ **NO INTEGRATION LAYER EXISTS**

**Critical Problem (GAD-003 Gap #1):**
- Orchestrator writes to STDOUT → **No process reads it**
- Orchestrator blocks on STDIN → **No process writes to it**
- **Result: DEADLOCK on `sys.stdin.readline()` at line 631**

**Required to Fix:**
- Integration script (e.g., `claude_code_bridge.py`) that:
  1. Launches orchestrator as subprocess
  2. Pipes STDOUT/STDIN for communication
  3. Reads INTELLIGENCE_REQUEST from orchestrator
  4. Calls Anthropic API with composed prompt
  5. Sends response to orchestrator's stdin
  6. Handles tool execution loop
  7. Manages process lifecycle

**Alternative (Recommended):**
- Remove STDIN/STDOUT protocol entirely
- Use Anthropic native tool use API directly
- Simplify to single-process execution

---

### 5. Orchestrator ↔ Workspace
**Mechanism:** Artifact persistence

```
workspaces/{project_id}/
├── project_manifest.json (ProjectManifest)
└── artifacts/
    ├── planning/
    │   ├── research_brief.json
    │   ├── lean_canvas_summary.json
    │   └── feature_spec.json
    ├── coding/
    │   ├── code_gen_spec.json
    │   └── artifact_bundle/
    ├── testing/
    │   ├── test_plan.json
    │   └── qa_report.json
    └── deployment/
        └── deploy_receipt.json
```

**Status:** ✅ **WORKS**

---

### 6. Orchestrator ↔ Tool Executor (GAD-003)
**Mechanism:** Direct instantiation in delegated mode

```python
# In CoreOrchestrator._request_intelligence()
tool_executor = ToolExecutor() if TOOLS_AVAILABLE else None

if tool_call and tool_executor:
    result = tool_executor.execute(tool_call['name'], tool_call['parameters'])
```

**Status:** ✅ **Implementation complete** | ❌ **Integration incomplete**

---

## TOOL EXECUTION MODEL

### Tool Definition (YAML)
```yaml
tools:
  google_search:
    name: google_search
    description: "Search Google..."
    parameters:
      query: {type: string, required: true}
      num_results: {type: integer, required: false, default: 10}
    returns: {type: array, description: "List of results"}
```

### Tool Usage Flow

1. **PromptRuntime loads tool definitions**
   - Reads `tool_definitions.yaml`
   - Filters to tools specified in `_composition.yaml`

2. **Formats as markdown section in composed prompt**
   ```markdown
   # === AVAILABLE TOOLS ===

   You have access to the following research tools:

   ## Tool: `google_search`
   **Description:** Search Google using Custom Search API...
   **Parameters:**
   - `query` (string) (required): Search query
   ...

   ### How to use tools:
   To call a tool, use the following XML format:
   <tool_use name="tool_name">
     <parameters>
       <param_name>value</param_name>
     </parameters>
   </tool_use>
   ```

3. **Agent receives prompt with tool section**
   - Agent reads tool definitions
   - Agent includes tool calls in response via XML

4. **Orchestrator detects & executes tools** (GAD-003 Phase 2)
   - `_parse_tool_use(response_text)` extracts `<tool_use>` XML
   - Calls `tool_executor.execute(tool_name, parameters)`
   - Routes to appropriate client (GoogleSearchClient or WebFetchClient)
   - Returns result as JSON

**Status:** ✅ **Implementation complete** | ❌ **No consumer for STDOUT protocol**

---

## AGENT INVOCATION MODEL

### Agent Structure
Each agent (e.g., VIBE_ALIGNER) follows a standard structure:

```
agency_os/01_planning_framework/agents/VIBE_ALIGNER/
├── _composition.yaml          # How to compose this agent's prompt
├── _prompt_core.md            # Core personality & responsibilities
├── _knowledge_deps.yaml       # Which YAML knowledge files to load
├── tasks/
│   ├── task_01_*.md           # Task instructions
│   ├── task_01_*.meta.yaml    # Task metadata (phase, gates, etc.)
│   ├── task_02_*.md
│   ├── task_02_*.meta.yaml
│   └── ...
└── gates/
    ├── gate_*.md              # Validation gate prompts
    └── ...
```

### Agent Invocation Sequence

1. **Handler initiates agent execution**
   ```python
   result = orchestrator.execute_agent(
       agent_name="VIBE_ALIGNER",
       task_id="02_feature_extraction",
       inputs={project_id, artifacts, ...},
       manifest=ProjectManifest
   )
   ```

2. **Orchestrator composes prompt**
   - Calls PromptRuntime.execute_task()
   - Returns markdown prompt (2000-5000 lines)

3. **Routes to execution mode**

   **Delegated Mode (DEFAULT):** ❌ **BROKEN**
   - Sends INTELLIGENCE_REQUEST to STDOUT
   - Reads response from STDIN → **DEADLOCKS**
   - Executes tools if agent requests them
   - Returns parsed result

   **Autonomous Mode (LEGACY):** ✅ **WORKS**
   - Creates LLMClient instance
   - Calls Anthropic API directly
   - Tracks costs
   - Returns parsed JSON

4. **Handler processes result**
   - Validates result structure
   - Saves artifacts
   - Updates manifest
   - Proceeds to next task/phase

---

### Research Agent Example (MARKET_RESEARCHER)

```
_composition.yaml defines:
  - _prompt_core.md (core personality)
  - tool_definitions.yaml (google_search, web_fetch) ← GAD-003
  - knowledge_files (market sizing formulas, templates)
  - task_prompt (specific task: competitor identification)
  - gate_prompts (citation requirements)
  - runtime_context (user vision, previous results)

Execution:
  1. Load research_brief.json or create empty
  2. Execute 6 sequential tasks:
     - task_01_competitor_identification → competitor_list.json
     - task_02_pricing_analysis → pricing_data.json
     - task_03_market_sizing → market_size_estimate.json
     - task_04_positioning_map → positioning_map.json
     - task_05_risk_assessment → risk_assessment.json
     - task_06_market_analysis → update research_brief.json
  3. Each task:
     - Loads previous task's output as input
     - Agent can use google_search to research competitors ⚠️ BROKEN in delegated mode
     - Agent can use web_fetch to read competitor websites ⚠️ BROKEN in delegated mode
     - Returns structured JSON output
  4. Final research_brief.json is input to LEAN_CANVAS_VALIDATOR
```

---

## STATE MANAGEMENT

### ProjectManifest (Single Source of Truth)
```python
@dataclass
class ProjectManifest:
    project_id: str
    name: str
    current_phase: ProjectPhase          # Main state
    current_sub_state: PlanningSubState  # PLANNING has substates
    artifacts: Dict[str, Any]            # All outputs
    budget: Dict[str, Any]               # Cost tracking
    metadata: Dict[str, Any]             # Full manifest JSON
```

### Workflow State Machine (YAML)
```yaml
states:
  - name: PLANNING
    sub_states:
      - RESEARCH (optional)
      - BUSINESS_VALIDATION
      - FEATURE_SPECIFICATION
      - ARCHITECTURE_DESIGN
  - CODING
  - TESTING
  - AWAITING_QA_APPROVAL (durable wait)
  - DEPLOYMENT
  - PRODUCTION
  - MAINTENANCE

transitions:
  - name: T1_StartCoding
    from_state: PLANNING.FEATURE_SPECIFICATION
    to_state: CODING
    quality_gates:
      - check: prompt_security_scan
        blocking: true
      - check: data_privacy_scan
        blocking: true
```

### Budget Tracking
```python
manifest.budget = {
    'max_cost_usd': 10.0,
    'current_cost_usd': 0.0,
    'alert_threshold': 0.80,  # 80% triggers warning
    'cost_breakdown': {
        'planning': 0.15,
        'coding': 0.45,
        'testing': 0.30
    }
}

# Updated after each LLM call
cost = (input_tokens / 1M) * 3 + (output_tokens / 1M) * 15  # Sonnet pricing
manifest.budget['current_cost_usd'] += cost
```

---

## CRITICAL GAPS (GAD-003 ASSESSMENT)

### Gap #1: Missing Claude Code Integration Layer ❌ **CRITICAL BLOCKER**

**Problem:**
```python
# core_orchestrator.py:631
response_line = sys.stdin.readline()  # ← BLOCKS FOREVER
```

**Root Cause:**
- Orchestrator implements **sender** of STDIN/STDOUT protocol
- **No code implements receiver** (consumer side)
- Orchestrator writes INTELLIGENCE_REQUEST → STDOUT
- **No process reads from orchestrator's STDOUT**
- Orchestrator blocks on STDIN
- **No process writes to orchestrator's STDIN**
- **Result: DEADLOCK**

**Evidence:**
- File: `agency_os/core_system/orchestrator/core_orchestrator.py:631`
- Status: **NO INTEGRATION LAYER EXISTS**

**Impact:**
- Delegated mode (default) cannot work
- System will hang indefinitely
- Research agents cannot execute with tools
- **vibe-agency is BROKEN in default configuration**

**Fix Options:**

**Option A: Build Integration Layer (4-6 hours)**
- Create `claude_code_bridge.py`:
  1. Launch orchestrator as subprocess
  2. Pipe STDOUT/STDIN for communication
  3. Read INTELLIGENCE_REQUEST from orchestrator
  4. Call Anthropic API with composed prompt
  5. Send response to orchestrator's stdin
  6. Handle tool execution loop
  7. Manage process lifecycle

**Option B: Switch to Native Anthropic Tool Use (RECOMMENDED, 2-3 hours)**
- Remove STDIN/STDOUT protocol entirely
- Update `_execute_autonomous()` to use Anthropic native tool API:
  ```python
  client.messages.create(
      model="claude-3-5-sonnet-20241022",
      messages=[...],
      tools=[{
          "name": "google_search",
          "description": "...",
          "input_schema": {...}
      }],
      tool_choice={"type": "auto"}
  )
  ```
- Parse tool use blocks from response
- Execute tools via ToolExecutor
- Continue conversation with tool results
- **Simpler, more reliable, officially supported**

---

### Gap #2: Tool Result Handoff Undefined ❌

**Problem:**
Orchestrator prints TOOL_RESULT but doesn't specify:
1. Who reads the TOOL_RESULT?
2. How to inject it back into Claude API conversation?
3. What format for tool results in API call?
4. How many iterations supported?

**Evidence:**
- File: `core_orchestrator.py:652-663`
- Protocol incomplete: "Continue loop (wait for next response)"
- No spec for multi-turn tool use

**Fix:** Use Anthropic native tool use (handles multi-turn automatically)

---

### Gap #3: No End-to-End Integration Test ❌

**Problem:**
- Unit tests pass (XML parsing, tool execution in isolation)
- No test validates full pipeline
- `tests/test_research_agent_e2e.py` intentionally fails to expose gaps

**Evidence:**
- Test file: `/home/user/vibe-agency/tests/test_research_agent_e2e.py`
- Status: EXPECTED FAILURE (by design)

**Fix:** Add e2e test that runs real research agent with tool use

---

### Gap #4: Custom XML Protocol vs Anthropic Native Tool Use ❌

**Problem:**
Implementation uses custom XML format:
```xml
<tool_use name="google_search">
  <parameters>
    <query>...</query>
  </parameters>
</tool_use>
```

But Anthropic Claude API has **native tool use** with JSON:
```json
{
  "tools": [{
    "name": "google_search",
    "description": "...",
    "input_schema": {...}
  }]
}
```

**Impact:**
- Reinventing the wheel
- Custom XML parsing adds complexity
- Less reliable than native implementation
- No Anthropic support

**Recommendation:** Switch to native tool use (Option B above)

---

### Additional Gaps

#### Gap #5: State Recovery Undefined
- Orchestrator crashes lose partial progress
- No checkpointing mechanism
- Expensive to re-run from beginning

**Fix:** Add checkpoint/resume capability

#### Gap #6: Knowledge Lifecycle Undefined
- Knowledge bases (YAML files) have no versioning
- No freshness tracking
- No update mechanism
- Agents get stale data

**Fix:** Add knowledge versioning + update workflow

#### Gap #7: Multi-Project Concurrency
- Handlers are stateless but orchestrator is singleton
- No locking mechanism
- Multiple projects might corrupt shared state

**Fix:** Add file-based locking or move to multi-instance architecture

#### Gap #8: Async Quality Gates Fire-and-Forget
- Async audits don't report back to manifest
- Results might be lost
- No retry if audit service fails

**Fix:** Add async audit result collection

---

## ARCHITECTURAL PATTERNS

### Pattern 1: Hierarchical Orchestrator
- CoreOrchestrator (state machine, routing)
- Phase Handlers (framework-specific logic)
- Each handler is independently testable

### Pattern 2: Prompt Composition
- Modular fragments (_prompt_core.md, knowledge, tasks, gates)
- YAML-driven composition order
- Runtime variable substitution
- Reusable across all agents

### Pattern 3: Artifact Contracts
- `ORCHESTRATION_data_contracts.yaml` defines schemas
- Artifacts are JSON with strict schemas
- Validation before saving (opt-in)

### Pattern 4: Durable Wait States
- AWAITING_QA_APPROVAL pauses workflow
- External actor (user) resumes via CLI
- Persisted to manifest (survives crashes)

### Pattern 5: Delegation of Intelligence (INCOMPLETE)
- Orchestrator is state machine (testable, maintainable)
- Claude Code is intelligence provider (flexible, powerful)
- STDOUT/STDIN protocol connects them ❌ **Not implemented**

---

## FILE INVENTORY

### Core System (2,328+ lines)
```
agency_os/core_system/
├── orchestrator/
│   ├── core_orchestrator.py (1,252 lines) - Main orchestrator
│   ├── state_manager.py - State persistence
│   ├── handlers/
│   │   ├── planning_handler.py - PLANNING phase
│   │   ├── coding_handler.py - CODING phase
│   │   ├── testing_handler.py - TESTING phase
│   │   ├── deployment_handler.py - DEPLOYMENT phase
│   │   └── maintenance_handler.py - MAINTENANCE phase
│   └── tools/
│       ├── tool_executor.py (50 lines) - Tool routing
│       ├── tool_definitions.yaml - google_search, web_fetch
│       ├── google_search_client.py - Google API wrapper
│       └── web_fetch_client.py - HTML extraction
├── runtime/
│   ├── prompt_runtime.py (660 lines) - Prompt composition
│   └── llm_client.py (400+ lines) - Anthropic API client
└── schemas/
    └── ORCHESTRATION_data_contracts.yaml - Artifact schemas
```

### Agent Frameworks
```
agency_os/
├── 01_planning_framework/agents/
│   ├── VIBE_ALIGNER/
│   ├── LEAN_CANVAS_VALIDATOR/
│   ├── GENESIS_BLUEPRINT/
│   ├── GENESIS_UPDATE/
│   └── research/
│       ├── MARKET_RESEARCHER/ (with tools)
│       ├── TECH_RESEARCHER/ (with tools)
│       ├── FACT_VALIDATOR/ (with tools)
│       └── USER_RESEARCHER/
├── 02_code_gen_framework/agents/
│   └── CODE_GENERATOR/
├── 03_qa_framework/agents/
│   └── QA_VALIDATOR/
├── 04_deploy_framework/agents/
│   └── DEPLOY_MANAGER/
└── 05_maintenance_framework/agents/
    └── BUG_TRIAGE/
```

### System Steward Framework
```
system_steward_framework/agents/
├── AUDITOR/ - Quality audits
├── LEAD_ARCHITECT/ - Architecture decisions
└── SSF_ROUTER/ - System governance
```

### Entry Points
```
vibe-cli.py (416 lines) - CLI for project management
  Commands:
    - list: Show all projects
    - tasks <agent>: List agent tasks
    - generate <agent> <task>: Generate composed prompt
    - workspaces: List workspaces
    - workspace <id>: Show workspace details
    - approve-qa <id>: Approve QA report (unblock deployment)
    - reject-qa <id>: Reject QA report (loop back to CODING)
```

### Tests
```
tests/
├── test_core_orchestrator_tools.py (147 lines) ✅ PASS
│   - XML parsing
│   - Tool executor routing
│   - Error handling
└── test_research_agent_e2e.py (100+ lines) ❌ EXPECTED FAILURE
    - Exposes GAD-003 integration gaps
```

---

## TEST COVERAGE

### What Works ✅
- XML parsing of tool use: `test_xml_parsing()` PASS
- Tool executor routing: `test_tool_executor()` PASS
- Error handling: `test_tool_executor_error_handling()` PASS
- Prompt composition: PromptRuntime executes without errors
- Agent registry: All 37 agents findable
- Workspace management: Projects persist correctly
- Manifest validation: Structure checks work
- Quality gates: Blocking/async gates execute
- Autonomous mode: Direct API calls work

### What Fails ❌
- End-to-end delegated mode: Never tested (would hang on stdin.readline())
- Tool execution with real Claude: Never tested
- Multi-turn tool use: Not implemented
- Research agents with tools: Can't execute in delegated mode
- Integration with Claude Code: No bridge layer

---

## SUMMARY TABLE

| Component | Status | Lines | Notes |
|-----------|--------|-------|-------|
| CoreOrchestrator | ⚠️ Partial | 1,252 | Autonomous ✅ / Delegated ❌ |
| PromptRuntime | ✅ Complete | 660 | Works |
| LLMClient | ✅ Complete | 400+ | Works |
| PlanningHandler | ✅ Complete | 150+ | Works in autonomous mode |
| CodingHandler | ✅ Complete | 150+ | Works |
| TestingHandler | ⚠️ Partial | - | AWAITING_QA_APPROVAL incomplete |
| DeploymentHandler | ⚠️ Partial | - | HITL integration incomplete |
| MaintenanceHandler | ⚠️ Minimal | - | Event listener missing |
| Tool Infrastructure | ⚠️ Partial | 100+ | Implementation ✅ / Integration ❌ |
| Agents (37) | ✅ Structured | - | Prompts complete |
| Workspace Mgmt | ✅ Complete | - | Works |
| Quality Gates | ✅ Framework | - | Works (async reporting incomplete) |
| State Machine | ✅ YAML | - | Works (recovery missing) |
| CLI (vibe-cli) | ✅ Complete | 416 | Works (delegated mode broken) |
| **OVERALL** | **⚠️ 60% FUNCTIONAL** | **2,328+** | **Autonomous mode works / Delegated mode broken** |

---

## WORKAROUND (CURRENT)

**To use the system NOW:**

1. **Set execution mode to autonomous:**
   ```python
   orchestrator = CoreOrchestrator(
       repo_root=".",
       workflow_yaml="agency_os/core_system/schemas/ORCHESTRATION_workflow.yaml",
       contracts_yaml="agency_os/core_system/schemas/ORCHESTRATION_data_contracts.yaml",
       execution_mode="autonomous"  # ← Force autonomous mode
   )
   ```

2. **Set ANTHROPIC_API_KEY:**
   ```bash
   export ANTHROPIC_API_KEY="sk-..."
   ```

3. **Run orchestrator directly:**
   ```bash
   python -c "
   from agency_os.core_system.orchestrator.core_orchestrator import CoreOrchestrator
   orch = CoreOrchestrator('.', execution_mode='autonomous')
   manifest = orch.load_project_manifest('my_project')
   orch.execute_phase(manifest)
   "
   ```

**Limitation:** Research agents cannot use tools (google_search, web_fetch) because tool execution is only implemented in delegated mode.

---

## RECOMMENDED FIX PATH

**Switch to Anthropic Native Tool Use (2-3 hours):**

1. **Update `_execute_autonomous()` in `core_orchestrator.py`:**
   - Add tools parameter to API call
   - Parse tool use blocks from response
   - Execute tools via ToolExecutor
   - Continue conversation with tool results

2. **Remove STDIN/STDOUT protocol:**
   - Delete `_request_intelligence()`
   - Remove delegated execution mode
   - Simplify to single-process execution

3. **Update tool definitions to Anthropic format:**
   - Convert `tool_definitions.yaml` to Anthropic input schema
   - Remove custom XML instructions from prompts

4. **Add end-to-end test:**
   - Test research agent with real tool use
   - Validate multi-turn tool execution

**Result:**
- ✅ Research agents can use tools
- ✅ Simpler codebase (remove 300+ lines of protocol code)
- ✅ More reliable (official Anthropic support)
- ✅ Single-process execution (easier debugging)

---

## CONCLUSION

**What Works:**
- Architecture is sound and complete at design level ✅
- All 5 SDLC phases have handlers ✅
- All agents properly structured ✅
- Tool infrastructure implemented ✅
- Prompt composition system elegant ✅
- State machine well-defined ✅
- **Autonomous mode functional ✅**

**What's Broken:**
- Delegated mode will deadlock on `sys.stdin.readline()` ❌
- No integration layer between orchestrator and Claude Code ❌
- Research agents cannot execute with tools ❌
- Tool execution loop has no consumer ❌
- No end-to-end tests validate pipeline ❌

**Root Cause:**
GAD-003 designed a STDIN/STDOUT protocol but only implemented the sender side. The receiver side (integration layer) was never built, making delegated mode non-functional.

**Path Forward:**
Switch to Anthropic native tool use. Estimated effort: 2-3 hours. System will then be fully functional in single-process autonomous mode with tool support.

---

**Document Version:** 1.0
**Author:** System Architecture Analysis
**Next Review:** After GAD-003 integration completion
