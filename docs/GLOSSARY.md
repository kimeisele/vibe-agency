# Vibe Agency Glossary - Ubiquitous Language

**Version:** 1.0
**Last Updated:** 2025-11-13
**Purpose:** Define canonical terminology for the Vibe Agency system to ensure consistent communication across team members, documentation, and code.

---

## Core Concepts

### Prompt Template Agent
**Definition:** A collection of markdown prompt templates, YAML configurations, and knowledge bases that together define a specialized role in the system.

**Examples:** VIBE_ALIGNER, GENESIS_BLUEPRINT, CODE_GENERATOR, QA_VALIDATOR, DEPLOY_MANAGER, BUG_TRIAGE

**NOT:** An autonomous software agent that executes code independently. Our "agents" are passive templates that require human execution via Claude.

**Structure:**
```
{AGENT_NAME}/
├── _prompt_core.md       # Personality and role definition
├── _composition.yaml     # How to assemble the prompt
├── _knowledge_deps.yaml  # Which knowledge to inject
├── tasks/               # Individual task prompts
└── gates/               # Validation rules
```

**Usage in Code:**
- Variable name: `agent_id` (e.g., "VIBE_ALIGNER")
- File path: `agency_os/{framework}/agents/{AGENT_NAME}/`

---

### Prompt Composition System
**Definition:** A system that assembles prompts from modular components (personality, knowledge, tasks, gates, context) for LLM processing.

**NOT:** A "multi-agent system" (implies autonomous agents communicating)
**NOT:** An "orchestration system" (implies automated execution)

**How It Works:**
1. User specifies `agent_id` and `task_id`
2. System loads and combines:
   - Agent's personality (`_prompt_core.md`)
   - Task instructions (`task_*.md`)
   - Relevant knowledge bases (`*.yaml`)
   - Validation gates (`gate_*.md`)
   - Runtime context (user input)
3. Output: Single composed prompt string
4. Execution: User manually provides prompt to Claude AI

**Implementation:** `agency_os/core_system/runtime/prompt_runtime.py` (319 lines)

**Key Principle:** Single-LLM, manual execution (not autonomous)

---

### Framework
**Definition:** A collection of agents organized around a software development lifecycle phase.

**The 5 Frameworks:**
1. **01_planning_framework** - Requirements to architecture (VIBE_ALIGNER, GENESIS_BLUEPRINT)
2. **02_code_gen_framework** - Architecture to code (CODE_GENERATOR)
3. **03_qa_framework** - Testing and validation (QA_VALIDATOR)
4. **04_deploy_framework** - Deployment execution (DEPLOY_MANAGER)
5. **05_maintenance_framework** - Bug triage and hotfixes (BUG_TRIAGE)

**Naming Convention:** `{number}_{phase}_framework`

**Directory Structure:**
```
agency_os/{framework}/
├── agents/          # Prompt template agents for this phase
└── knowledge/       # Phase-specific knowledge bases
```

---

### Task
**Definition:** A single, atomic unit of work executed by an agent.

**Format:**
- **Markdown prompt:** `task_{number}_{name}.md` (instructions for Claude)
- **YAML metadata:** `task_{number}_{name}.meta.yaml` (dependencies, inputs, outputs)

**Execution:** Manual - user loads composed prompt into Claude, processes it, saves output as artifact.

**Example:**
```
task_01_select_core_modules.md
task_01_select_core_modules.meta.yaml
```

**Metadata Structure:**
```yaml
task_id: "01_select_core_modules"
phase: 1
description: "Identify shared functionality for core modules"
dependencies: ["feature_spec.json"]
inputs: [{artifact: "feature_spec", required: true}]
outputs: [{artifact: "core_modules_list", schema: "array"}]
validation_gates: ["gate_stdlib_only_core", "gate_module_count_range"]
```

---

### Knowledge Base
**Definition:** Curated YAML files containing domain expertise, patterns, rules, and templates that inform agent behavior.

**Types:**
- **Constraints:** Rules and limits (e.g., FAE_constraints.yaml - feasibility rules)
- **Patterns:** Proven solutions (e.g., TECH_STACK_PATTERNS.yaml - 8 battle-tested stacks)
- **Templates:** Reusable structures (e.g., PROJECT_TEMPLATES.yaml - 18 project types)
- **Dependencies:** Feature relationships (e.g., FDG_dependencies.yaml - 2,546 rules)

**Current Size:** 6,409 lines (271 KB total)

**Naming Convention:** `{ACRONYM}_{purpose}.yaml`
- **FAE:** Feasibility Analysis Engine
- **FDG:** Feature Dependency Graph
- **APCE:** Anticipated Project Complexity Estimator

**Usage:** Knowledge bases are injected into prompts based on `_knowledge_deps.yaml` configuration.

---

### Validation Gate
**Definition:** A markdown file defining a quality constraint that must be satisfied for a task to be considered complete.

**Purpose:** Enforce quality standards, prevent common mistakes, ensure consistency.

**Examples:**
- `gate_stdlib_only_core.md` - Core modules must use standard library only
- `gate_module_count_range.md` - Core modules must be 3-8 (not too few, not too many)
- `gate_fae_validation_passed.md` - Feasibility checks must pass

**Format:**
```markdown
# Gate: {Name}

## Rule
[Clear description of what must be true]

## Rationale
[Why this rule exists]

## Validation
[How to check if rule is satisfied]

## Failure Guidance
[What to do if validation fails]
```

**Usage:** Listed in task metadata (`validation_gates: [...]`), loaded during composition.

---

### Artifact
**Definition:** A structured data file (usually JSON) produced by a task and consumed by subsequent tasks.

**Purpose:** Single source of truth for project state, enables task handoff, supports traceability.

**Core Artifacts:**
- `project_manifest.json` - Project state, artifact links, metadata
- `feature_spec.json` - Extracted features, validation results
- `architecture.json` - Generated architecture blueprint
- `code_gen_spec.json` - Code generation plan
- `qa_report.json` - Test results, quality metrics
- `deploy_receipt.json` - Deployment proof, environment details

**Schema Enforcement:** All artifacts have JSON schemas (e.g., `project_manifest.schema.json`)

**Location:** `workspaces/{client}/{project}/artifacts/{phase}/`

---

### Workspace
**Definition:** A directory structure containing all files for a single client project.

**Structure:**
```
workspaces/
└── {client_name}/              # Client grouping
    └── {project_name}/         # Project directory
        ├── project_manifest.json   # Single source of truth
        └── artifacts/              # Generated outputs
            ├── planning/           # feature_spec.json, architecture.json
            ├── code/               # Source code artifacts
            ├── test/               # QA reports, test results
            └── deployment/         # Deploy receipts
```

**Purpose:** Isolate client projects, organize artifacts, enable version control.

**Naming Convention:** Lowercase, underscores (e.g., `yoga_studio_booking`)

---

### Composition Order
**Definition:** A sequence of steps defining how to assemble a prompt from fragments.

**Specified In:** `_composition.yaml` for each agent

**Example:**
```yaml
composition_order:
  - source: _prompt_core.md
    type: base
  - source: ${knowledge_files}     # Variable substitution
    type: knowledge
  - source: ${task_prompt}         # Variable substitution
    type: task
  - source: ${gate_prompts}        # Variable substitution
    type: validation
  - source: ${runtime_context}     # Variable substitution
    type: context
```

**Execution:** `prompt_runtime.py` processes this order, resolves variables, concatenates fragments.

---

### Runtime Context
**Definition:** Dynamic data provided when executing a task (project ID, current phase, artifact paths, user input).

**Structure:**
```python
context = {
    "project_id": "test_project_001",
    "current_phase": "PLANNING",
    "artifacts": {
        "feature_spec": "workspaces/test/artifacts/planning/feature_spec.json"
    },
    "workspace_path": "workspaces/test/",
    "user_input": "I want a booking system for yoga classes..."
}
```

**Purpose:** Inject real-time, project-specific data into composed prompts.

---

### State Machine (SDLC Workflow)
**Definition:** A formal model of the software development lifecycle, defining valid states and transitions.

**Specification:** `ORCHESTRATION_workflow_design.yaml`

**States:**
- PLANNING → CODING → TESTING → AWAITING_QA_APPROVAL → DEPLOYMENT → PRODUCTION → MAINTENANCE

**Transitions:** Triggered by artifact creation (e.g., `qa_approved_signal` moves to DEPLOYMENT)

**Loops:**
- L1_TestFailed (TESTING → CODING if QA rejected)
- L2_DeployFailed (DEPLOYMENT → CODING if rollback)

**Status in v1.0:** DESIGNED but NOT IMPLEMENTED (no executor code)

---

## Technical Terms

### Prompt Runtime
**Definition:** The Python module responsible for composing prompts from fragments.

**Implementation:** `agency_os/core_system/runtime/prompt_runtime.py` (319 lines)

**Key Methods:**
- `execute_task(agent_id, task_id, context)` - Main entry point
- `_compose_prompt(...)` - Assembles fragments according to composition_order
- `_load_knowledge_file(path)` - Loads and caches YAML knowledge

**Dependencies:** `pyyaml`, `pathlib` (standard library)

---

### Knowledge Cache
**Definition:** In-memory storage of loaded YAML files to avoid re-parsing.

**Implementation:** `self.knowledge_cache` dict in `PromptRuntime`

**Purpose:** Performance optimization (file I/O is slow)

**Invalidation:** Cache persists for lifetime of PromptRuntime instance (cleared on restart)

---

### SDLC
**Definition:** Software Development Lifecycle - the process of planning, creating, testing, deploying, and maintaining software.

**Vibe Agency SDLC Phases:**
1. PLANNING (requirements → architecture)
2. CODING (architecture → source code)
3. TESTING (validation, QA)
4. AWAITING_QA_APPROVAL (human review)
5. DEPLOYMENT (to production)
6. PRODUCTION (live system)
7. MAINTENANCE (bug fixes, updates)

---

### Data Contract
**Definition:** A formal specification of data structure (JSON schema) enforced between tasks.

**Purpose:** Ensure tasks can interoperate, prevent schema drift, enable validation.

**Specification:** `ORCHESTRATION_data_contracts.yaml`

**Examples:**
- `project_manifest.schema.json`
- `code_gen_spec.schema.json`
- `qa_report.schema.json`

**Governance:** Schema evolution must be backward-compatible (no breaking changes)

---

## Anti-Patterns (What NOT to Say)

### ❌ "Multi-Agent System"
**Why Wrong:** Implies autonomous agents communicating and collaborating independently.

**Reality:** Single LLM (Claude) processes composed prompts manually.

**Use Instead:** "Prompt Composition System" or "Single-LLM Planning Tool"

---

### ❌ "Orchestration" (for current v1.0)
**Why Wrong:** Implies automated execution of workflows.

**Reality:** Manual execution - user runs each task, saves output, proceeds to next.

**Use Instead:** "Manual workflow" or "Task composition"

**Exception:** Future versions may implement true orchestration (with Temporal/Prefect)

---

### ❌ "Agent Communication"
**Why Wrong:** Implies agents send messages to each other.

**Reality:** Tasks pass artifacts (JSON files) as input/output.

**Use Instead:** "Task handoff via artifacts" or "File-based data flow"

---

### ❌ "AI Agents"
**Why Wrong:** Implies autonomous decision-making software.

**Reality:** Passive prompt templates executed by human via Claude.

**Use Instead:** "Prompt Template Agents" or "Specialized Prompt Modules"

---

## Acronyms

- **AOS:** Agency Operating System (the full system)
- **APCE:** Anticipated Project Complexity Estimator (knowledge base)
- **DDD:** Domain-Driven Design (design philosophy)
- **FAE:** Feasibility Analysis Engine (knowledge base)
- **FDG:** Feature Dependency Graph (knowledge base)
- **FMA:** Failure Mode Analysis (risk identification technique)
- **HITL:** Human-In-The-Loop (manual approval required)
- **LLM:** Large Language Model (Claude AI)
- **MVP:** Minimum Viable Product
- **NFR:** Non-Functional Requirement (quality attribute)
- **SDLC:** Software Development Lifecycle
- **UL:** Ubiquitous Language (DDD concept)
- **YAGNI:** You Ain't Gonna Need It (lean principle)

---

## Usage Guidelines

### For Developers
- Use exact agent names from `AGENT_REGISTRY` in code
- Follow naming conventions for tasks (`task_{number}_{name}.md`)
- Reference artifacts by canonical names (`feature_spec.json`, not `features.json`)
- Use this glossary when writing documentation

### For Documentation
- Link to glossary entries when introducing new terms
- Use consistent terminology (don't invent synonyms)
- Avoid anti-patterns (multi-agent, orchestration for v1.0)
- Update glossary when adding new concepts

### For Communication
- Use "Prompt Template Agent" not "AI Agent" when explaining to users
- Be clear about manual execution (not autonomous)
- Explain "composition" concept (assembling prompts from parts)
- Reference this glossary in onboarding materials

---

**Maintenance:** This glossary is a living document. Update whenever:
- New concepts are introduced
- Terminology evolves
- Anti-patterns are discovered
- User feedback indicates confusion

**Governance:** All changes to glossary must be reviewed and approved by project lead.
