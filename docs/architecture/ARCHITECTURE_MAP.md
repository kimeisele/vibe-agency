# VIBE AGENCY: Complete Architecture Map

**STATUS: IMPLEMENTATION PHASE (Kernel Complete, Post-Split)**
**LAST UPDATED: 2025-11-21 (Updated for ARCH-021 to ARCH-025 + Split)**
**PURPOSE: Bird's Eye View of Entire System + Implementation Status**
**AUDIENCE: Architects, Developers, Stakeholders**
**DRIFT ASSESSMENT: ✅ CURRENT - Reflects post-split, post-kernel reality**

---

## 🔴 GAD-000: THE LAW - OPERATOR INVERSION PRINCIPLE

**STATUS:** FOUNDATIONAL LAW | **PRECEDENCE:** ABSOLUTE | **DATE:** 2025-11-21

> **"The end user is NOT the operator. The LLM is the operator. The human is the director."**

### The Core Principle

**Traditional Software:**
```
Human → Operates System → Gets Result
```

**AI-Native Software (Vibe OS):**
```
Human → Describes Intent → AI Operates System → Human Validates Result
```

### What This Means

**Every component in Vibe OS must be designed for AI operation, not human operation:**

| Aspect | Traditional (Human-Operated) | AI-Native (LLM-Operated) |
|--------|------------------------------|---------------------------|
| **Interface** | Buttons, menus, forms | Tool signatures, APIs |
| **Documentation** | Human-readable prose | Structured, machine-parseable |
| **Errors** | "Something went wrong" | Error codes + context |
| **State** | Hidden internal state | Always observable |
| **Operations** | One-off commands | Composable, chainable |

### The Five Requirements

Every tool, interface, and component must provide:

1. **🔍 Discoverability** - Can AI find and understand this tool?
2. **👁️ Observability** - Can AI see current system state?
3. **📋 Parseability** - Can AI understand errors and responses?
4. **🔗 Composability** - Can AI chain this with other operations?
5. **🔄 Idempotency** - Can AI safely retry operations?

### Impact on Architecture

**This principle affects ALL GADs (1-9):**
- **GAD-5** (Runtime): State must be AI-observable
- **GAD-6** (Knowledge): Queries must be AI-composable
- **GAD-7** (STEWARD): Governance must be AI-queryable
- **GAD-8** (Integration): Must include LLM operator interface
- **GAD-9** (Orchestration): Workflows must be AI-executable

### Validation Test

```python
# GOOD: AI-Native Design ✅
{
  "status": "success",
  "cartridges": ["feature-implement", "coder-mode"],
  "next_actions": [
    {"command": "vibe run", "purpose": "Launch cartridge"}
  ]
}

# BAD: Human-Native Design ❌
"🟢 System OK! Run 'vibe --help' for more info"
```

**→ Full documentation: [GAD-000_OPERATOR_INVERSION.md](GAD-000_OPERATOR_INVERSION.md)**

---

## THE CORE PHILOSOPHY: The 6D Hexagon

**Vibe Agency = Vibe-Studio running on Vibe-OS**

Just as Photoshop runs on an operating system, **Vibe-Studio (the interface: agents, specialists, workflows) runs on Vibe-OS (the system: runtime, knowledge, governance, orchestration)**.

The architecture follows a **6D Hexagon model** that provides a complete dimensional framework:

| Dimension | Name | Function | Status |
|-----------|------|----------|--------|
| **1-3D: GAD/LAD/VAD** | **The Body** | Structure, Rules, Verification | ✅ Exists |
| **4D: PAD** | **The Action** | Workflows & Time | ✅ Operational |
| **5D: MAD** | **The Soul** | Context & Intention | ⚠️ Emerging |
| **6D: EAD** | **The Mind** | Evolution & Memory | 🔮 Planned |

**→ See [VISION_6D_HEXAGON.md](VISION_6D_HEXAGON.md) for the complete philosophical foundation.**

This model ensures completeness:
- **Static** (Body): Code and structure
- **Kinetic** (Action): Workflows through time
- **Dynamic** (Soul): Context and purpose
- **Cybernetic** (Mind): Learning and evolution

---

## 1. The Complete Picture (CURRENT STATE)

```
STATUS: GAD-5 (Runtime) ✅ LIVE | GAD-6 (Knowledge) ✅ LIVE | GAD-7 (Steward) ✅ LIVE
        GAD-906 (Semantic Lenses) 🔬 PROTOTYPE | GAD-9 (Semantic Orchestration) ✅ OPERATIONAL
NEXT:   GAD-3 (Agents/Legs) ⏳ READY | GAD-4 (QA/Feet) ⏳ PLANNED
┌────────────────────────────────────────────────────────────┐
│                    VIBE AGENCY ARCHITECTURE                │
│                                                            │
│  ┌──────────────────────────────────────────────────────┐ │
│  │ GAD-5: RUNTIME ENGINEERING (FOUNDATION) ✅ LIVE     │ │
│  │ • GAD-501: Shell Kernel (bin/vibe-shell)           │ │
│  │ • GAD-502: Context Projection (VIBE_CONTEXT)       │ │
│  │ • GAD-503: Logging Kernel (.vibe/logs)             │ │
│  │ • GAD-509: Circuit Breaker (Iron Dome) 🛡️         │ │
│  │ • GAD-510: Quota Manager (Cost Control) 💰         │ │
│  │ • GAD-511: Neural Adapter (Multi-Provider LLM) 🧠  │ │
│  │ • Anti-Decay: Health check (--health flag)         │ │
│  │ Status: Production-Grade, Sealed, Tested           │ │
│  └──────────────────────────────────────────────────────┘ │
│                          ↕                                 │
│  ┌──────────────────────────────────────────────────────┐ │
│  │ GAD-6: KNOWLEDGE FOUNDATION (ARMS) ✅ LIVE          │ │
│  │ • GAD-601: Knowledge Scaffold (4 domains)          │ │
│  │ • GAD-602: Semantic Search (Phase 1: keyword)      │ │
│  │ • GAD-906: Semantic Lenses (Intelligence Injection)│ │
│  │ • bin/vibe-knowledge CLI (search/list/read)        │ │
│  │ Status: Initialized & Operational, Phase 1 Done   │ │
│  └──────────────────────────────────────────────────────┘ │
│                          ↕                                 │
│  ┌──────────────────────────────────────────────────────┐ │
│  │ GAD-7: STEWARD (BRAIN) ✅ LIVE                      │ │
│  │ • Mission Control & Task Orchestration              │ │
│  │ • Playbook Routing System                           │ │
│  │ • Delegation & Validation                           │ │
│  │ Status: Fully Operational                           │ │
│  └──────────────────────────────────────────────────────┘ │
│                          ↕                                 │
│  ┌──────────────────────────────────────────────────────┐ │
│  │ GAD-906: SEMANTIC LENSES 🔬 PROTOTYPE               │ │
│  │ • Mental Model Injection (Worker → Engineer)        │ │
│  │ • Context Enrichment Before Execution               │ │
│  │ • First Principles Thinking (v1.0)                  │ │
│  │ • Location: knowledge/lenses/*.yaml                 │ │
│  │ Status: Prototype, Data Structure Designed          │ │
│  └──────────────────────────────────────────────────────┘ │
│                          ↕                                 │
│  ┌──────────────────────────────────────────────────────┐ │
│  │ GAD-9: SEMANTIC ORCHESTRATION (ENGINE) ✅ LIVE      │ │
│  │ • GAD-902: Graph Executor (Topology & Dependencies)│ │
│  │ • GAD-903: Workflow Loader (Data → Logic)          │ │
│  │ • Playbook Engine (Task Routing & Validation)      │ │
│  │ Status: Operational, v0.5 Foundation Complete      │ │
│  └──────────────────────────────────────────────────────┘ │
│                          ↕                                 │
│  ┌──────────────────────────────────────────────────────┐ │
│  │ GAD-3: AGENTS (LEGS) ⏳ READY                        │ │
│  │ • Agent Personas (Coder, Researcher, Reviewer)      │ │
│  │ • Prompt Specialization                             │ │
│  │ • Domain-Specific Task Execution                    │ │
│  │ Status: Architecture Ready, Implementation Pending  │ │
│  └──────────────────────────────────────────────────────┘ │
│                          ↕                                 │
│  ┌──────────────────────────────────────────────────────┐ │
│  │ GAD-4: QUALITY ASSURANCE (FEET) ⏳ PLANNED           │ │
│  │ • Test Execution Framework                          │ │
│  │ • Code Quality Validation                           │ │
│  │ • Deployment Verification                           │ │
│  │ Status: Requirements Gathering Phase                │ │
│  └──────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────┘
```

---

## 2. The Three Deployment Layers

### Layer 1: Browser-Only (Prompt-Based)

```yaml
what_works:
  - All agents (prompt mode)
  - STEWARD (guidance mode)
  - Knowledge access (manual)
  - Static YAML files
  - Markdown documentation
  - Manual governance compliance

what_doesnt_work:
  - No automated tools
  - No APIs
  - No runtime enforcement
  - No receipt generation
  - No integrity verification
  - No federated research

hosting:
  - GitHub Pages
  - Netlify
  - Any static host
  - Even local filesystem

cost: "$0"
setup: "5 minutes"
use_case: "Solo developer, quick prototyping, learning"
```

### Layer 2: Claude Code (Tool-Based)

```yaml
what_works:
  - Layer 1 +
  - Automated knowledge queries
  - Receipt generation
  - System integrity checks
  - STEWARD validation
  - Local semantic search
  - File system operations

what_doesnt_work:
  - No external APIs
  - No federated research
  - No runtime enforcement
  - No CI/CD integration
  - No client research access

hosting:
  - Local machine
  - Claude Code environment
  - File system + Python

cost: "various options, also free, works currently best with Claude Code"
setup: "1 minutes"
use_case: "Individual developer, small teams, most projects"
```

### Layer 3: Full Runtime (API-Based)

```yaml
what_works:
  - Layer 1 + Layer 2 +
  - ResearchEngine (multi-source)
  - Client research APIs
  - Web search integration
  - Vector DB semantic search
  - Runtime governance enforcement
  - CI/CD integration
  - Audit logging
  - Alert systems

hosting:
  - Cloud server (AWS, GCP, Azure)
  - Backend services
  - Database systems
  - External API integrations

cost: "$50-200/month"
setup: "2-4 hours"
use_case: "Agencies, teams, production deployments, client work"
```

---

## 3. GAD Dependency Graph

```
┌─────────────┐
│   GAD-5     │  ← Foundation (must exist first)
│  Runtime    │     (Docs: GAD-5XX/ - includes Iron Dome)
└─────────────┘
       ↓ provides context to
┌─────────────┐     ┌─────────────┐
│   GAD-6     │     │   GAD-7     │
│  Knowledge  │  ←→ │  STEWARD    │
│(GAD-6XX/)   │     │ (GAD-7XX/)  │
│ + GAD-906   │     │             │
└─────────────┘     └─────────────┘
       ↓                   ↓
       └────────┬──────────┘
                ↓
        ┌─────────────┐
        │  GAD-906    │  ← Intelligence Injection (NEW)
        │  Semantic   │     (Mental Models / Lenses)
        │   Lenses    │     Worker → Engineer Mode
        └─────────────┘
                ↓ enriches context for
        ┌─────────────┐
        │   GAD-9     │  ← Playbook Engine
        │  Semantic   │     (Docs: GAD-9XX/)
        │Orchestration│     Executor + Loader
        └─────────────┘
                ↓
        ┌─────────────┐
        │   GAD-8     │  ← Orchestrates all
        │ Integration │     (Docs: GAD-8XX/)
        └─────────────┘

Dependencies:
- GAD-6 needs GAD-5 (uses receipts, integrity)
- GAD-7 needs GAD-5 (governs context layers)
- GAD-6 ↔ GAD-7 (bidirectional - knowledge needs governance, governance uses knowledge)
- GAD-906 needs GAD-6 (lenses stored in knowledge department)
- GAD-906 feeds GAD-9 (enriches agent context before execution)
- GAD-9 needs GAD-5 (safety layer: circuit breaker, quota manager)
- GAD-8 needs all (orchestrates everything)
```

---

## 4. Component Classification

### Intelligent Components (Have State, Make Decisions)

```yaml
intelligent_components:
  
  - name: "VIBE_ALIGNER"
    system: "Agency OS"
    layers: [1, 2, 3]
    purpose: "Feature specification and validation"
    
  - name: "GENESIS_BLUEPRINT"
    system: "Agency OS"
    layers: [1, 2, 3]
    purpose: "Architecture generation"
    
  - name: "ResearchEngine"
    system: "Knowledge Department"
    layers: [3]
    purpose: "Multi-source research aggregation"
    
  - name: "STEWARD"
    system: "Governance"
    layers: [1, 2, 3]
    purpose: "Hybrid governance decision-making"
```

### Semi-Intelligent Components (Have Logic, No State)

```yaml
semi_intelligent_components:
  
  - name: "CoreOrchestrator"
    system: "Agency OS"
    layers: [2, 3]
    purpose: "State management and prompt composition"
  
  - name: "GraphExecutor"
    system: "GAD-9 (Semantic Orchestration)"
    layers: [2, 3]
    purpose: "Workflow graph execution with dependency resolution"
    
  - name: "WorkflowLoader"
    system: "GAD-9 (Semantic Orchestration)"
    layers: [2, 3]
    purpose: "Load and validate YAML workflows"
    
  - name: "ReceiptManager"
    system: "GAD-5 (Runtime Engineering)"
    layers: [2, 3]
    purpose: "Receipt generation and validation"
  
  - name: "CircuitBreaker"
    system: "GAD-5 (Runtime Engineering)"
    layers: [2, 3]
    purpose: "Cascading failure protection (Iron Dome)"
    
  - name: "QuotaManager"
    system: "GAD-5 (Runtime Engineering)"
    layers: [2, 3]
    purpose: "API cost control and quota enforcement"

  - name: "NeuralAdapter"
    system: "GAD-5 (Runtime Engineering)"
    layers: [2, 3]
    purpose: "Multi-provider LLM abstraction (Anthropic, Google, OpenAI)"

  - name: "IntegrityChecker"
    system: "GAD-5 (Runtime Engineering)"
    layers: [2, 3]
    purpose: "System integrity verification"
    
  - name: "KnowledgeQuery"
    system: "Knowledge Department"
    layers: [2, 3]
    purpose: "Knowledge retrieval"
    
  - name: "ModRegistry"
    system: "STEWARD"
    layers: [2, 3]
    purpose: "Extension management"
```

### Mechanical Components (Data Only, No Logic)

```yaml
mechanical_components:
  
  - name: "project_manifest.json"
    system: "Agency OS"
    layers: [1, 2, 3]
    purpose: "Project state storage"
    
  - name: "system_integrity_manifest.json"
    system: "GAD-5 (Runtime Engineering)"
    layers: [1, 2, 3]
    purpose: "Trusted baseline checksums"
    
  - name: "knowledge_graph.yaml"
    system: "Knowledge Department"
    layers: [1, 2, 3]
    purpose: "Concept relationships"
    
  - name: "governance_rules.yaml"
    system: "STEWARD"
    layers: [1, 2, 3]
    purpose: "Policy definitions"
    
  - name: "receipts/*.json"
    system: "GAD-5 (Runtime Engineering)"
    layers: [2, 3]
    purpose: "Work accountability"
```

---

## 5. Complete Directory Structure (Post-Split: Nov 2025)

**✅ CURRENT STATE** (after ARCH-021 to ARCH-025 + Kernel/Agency Split)

```
vibe-agency/
│
├── .vibe/                              # GAD-5 Runtime artifacts
│   ├── system_integrity_manifest.json  # Layer 0
│   ├── state/
│   │   └── vibe_agency.db              # SQLite state (ARCH-002)
│   ├── receipts/                       # Layer 2+3
│   └── audit/                          # Layer 3 only
│
├── vibe_core/                          # ✅ KERNEL (domain-agnostic OS)
│   ├── kernel.py                       # ARCH-022: Kernel Loop
│   ├── ledger.py                       # ARCH-024: Task Execution Ledger
│   ├── agent_protocol.py               # Agent interface contract
│   │
│   ├── scheduling/                     # ARCH-021: FIFO Scheduler
│   │   ├── scheduler.py
│   │   └── task.py
│   │
│   ├── agents/                         # Internal agent layer
│   │   └── llm_agent.py                # SimpleLLMAgent
│   │
│   ├── llm/                            # ARCH-025: The Cortex (LLM Integration)
│   │   └── provider.py                 # LLMProvider (Anthropic/OpenAI/Google)
│   │
│   ├── specialists/                    # ARCH-005: HAP Pattern Base
│   │   ├── base_specialist.py          # BaseSpecialist abstract class
│   │   └── registry.py                 # AgentRegistry
│   │
│   ├── runtime/                        # Runtime infrastructure
│   │   ├── llm_client.py
│   │   ├── tool_safety_guard.py        # ARCH-011: Iron Dome
│   │   ├── boot_sequence.py
│   │   ├── context_loader.py
│   │   └── prompt_composer.py
│   │
│   ├── playbook/                       # ARCH-013: Playbook Engine
│   │   ├── playbook_engine.py
│   │   ├── router_bridge.py            # ✅ Playbook → Specialist bridge
│   │   └── schema_validator.py
│   │
│   ├── store/                          # ARCH-002: Persistence Layer
│   │   └── sqlite_store.py             # SQLite CRUD operations
│   │
│   ├── config/                         # Configuration management
│   │   └── phoenix.py
│   │
│   └── task_management/                # Roadmap & task system
│       ├── roadmap_manager.py
│       └── task_execution.py
│
├── apps/agency/                        # ✅ APPLICATION (software development domain)
│   ├── orchestrator/                   # Core orchestration logic
│   │   ├── core_orchestrator.py
│   │   └── handlers/                   # Phase handlers
│   │
│   ├── specialists/                    # SDLC-specific specialists (ARCH-006 to ARCH-008)
│   │   ├── planning.py                 # PlanningSpecialist
│   │   ├── coding.py                   # CodingSpecialist
│   │   ├── testing.py                  # TestingSpecialist
│   │   ├── deployment.py               # DeploymentSpecialist
│   │   └── maintenance.py              # MaintenanceSpecialist
│   │
│   └── personas/                       # ⚠️ Legacy (scheduled for removal)
│
├── bin/                                # Executable scripts
│   ├── vibe                            # ARCH-015: Main CLI entry point
│   ├── system-boot.sh                  # System bootstrap
│   └── ...
│
├── docs/                               # Documentation
│   ├── architecture/                   # Architectural decisions
│   │   ├── ADR/                        # Architectural Decision Records
│   │   ├── ARCH/                       # ARCH-001 to ARCH-025 tracking
│   │   ├── GAD-0XX/                    # GAD 000-099 range
│   │   ├── GAD-4XX/ to GAD-9XX/        # GAD ranges
│   │   ├── LAD/                        # Layer Architecture Dimension
│   │   ├── VAD/                        # Verification Architecture Dimension
│   │   └── archive/                    # Historical documents
│   ├── playbook/                       # Operational playbooks
│   └── roadmap/                        # Phase roadmaps
│
├── tests/                              # Test suite (631 tests, 96.3% passing)
│   ├── core/                           # vibe_core tests
│   ├── architecture/                   # VAD tests (architecture verification)
│   └── test_*_workflow.py              # Smoke tests
│
├── knowledge_department/               # GAD-6 (Knowledge Department)
│   ├── domain_knowledge/
│   │   ├── industry_patterns/
│   │   ├── client_domains/            # Confidential
│   │   └── cross_project_learnings/
│   │
│   ├── research_division/
│   │   ├── tools/                     # Layer 2
│   │   └── services/                  # Layer 3
│   │
│   └── knowledge_services/
│       ├── access_control/
│       ├── indexing/                  # Layer 3
│       └── query_interface/
│
├── steward/                            # GAD-7 (STEWARD Governance)
│   ├── core/
│   │   ├── _steward_prompt_core.md    # Layer 1
│   │   ├── decision_engine.py         # Layer 2+3
│   │   └── governance_engine.py       # Layer 3
│   │
│   ├── governance/
│   │   ├── layer1_rules.yaml
│   │   ├── layer2_rules.yaml
│   │   └── layer3_rules.yaml
│   │
│   ├── policies/
│   └── integrations/
│       └── mod_registry/
│
├── integration/                        # GAD-8 (Integration Matrix)
│   ├── config/
│   │   ├── integration_config.yaml
│   │   └── degradation_rules.yaml
│   │
│   ├── protocols/
│   │   ├── agent_to_knowledge.yaml
│   │   ├── agent_to_steward.yaml
│   │   └── knowledge_to_steward.yaml
│   │
│   └── layer_detection/
│       └── detector.py
│
├── workspaces/                         # Project workspaces
│   └── {client}/{project}/
│       ├── project_manifest.json
│       └── artifacts/
│
├── scripts/                            # GAD-5 scripts
│   ├── verify-system-integrity.py
│   ├── generate-integrity-manifest.py
│   ├── update-system-status.sh
│   ├── validate_receipts.py
│   └── check_watermarks.py
│
├── .git/hooks/                         # GAD-5 Layer 3
│   └── pre-commit
│
├── .github/workflows/                  # GAD-5 Layer 4
│   └── pr-validation.yml
│
├── config/                             # System-wide config
│   ├── deployment/
│   │   ├── layer1_browser.yaml
│   │   ├── layer2_claudecode.yaml
│   │   └── layer3_runtime.yaml
│   │
│   └── kernel_rules.yaml
│
└── vibe-cli                            # GAD-5 Session Shell
```

---

## 6. Data Flow Diagram

```
┌─────────────┐
│    User     │
└─────────────┘
       ↓ interacts with
┌─────────────┐
│  vibe-cli   │  (GAD-5 Layer 1)
│ Session     │
│  Shell      │
└─────────────┘
       ↓ boots system
┌─────────────┐
│  Layer 0    │  (GAD-5)
│  Integrity  │
│   Check     │
└─────────────┘
       ↓ if verified
┌─────────────┐     ┌─────────────┐
│   Agent     │────▶│  STEWARD    │  (GAD-7)
│VIBE_ALIGNER │     │ Governance  │
└─────────────┘     └─────────────┘
       ↓                   ↓
       │ asks "Can I?"     │ validates
       └──────────┬────────┘
                  ↓
          ┌─────────────┐
          │  Decision   │
          │  (allow/    │
          │   block)    │
          └─────────────┘
                  ↓
       ┌──────────┴──────────┐
       ↓                     ↓
┌─────────────┐      ┌─────────────┐
│  Knowledge  │      │   Receipt   │  (GAD-5)
│   Query     │      │   Create    │
└─────────────┘      └─────────────┘
       ↓                     ↓
┌─────────────┐      ┌─────────────┐
│  Knowledge  │      │  .vibe/     │
│  Department │      │  receipts/  │
└─────────────┘      └─────────────┘
       ↓
       │ returns knowledge
       ↓
┌─────────────┐
│   Agent     │
│  processes  │
│   & works   │
└─────────────┘
       ↓
┌─────────────┐
│   Commit    │
└─────────────┘
       ↓
┌─────────────┐
│  Pre-commit │  (GAD-5 Layer 3)
│    Hook     │
└─────────────┘
       ↓
┌─────────────┐
│  Watermark  │
│    Added    │
└─────────────┘
       ↓
┌─────────────┐
│     Git     │
│   History   │
└─────────────┘
       ↓
┌─────────────┐
│   PR Push   │
└─────────────┘
       ↓
┌─────────────┐
│   CI/CD     │  (GAD-5 Layer 4)
│ Validation  │
└─────────────┘
       ↓
┌─────────────┐
│   Merge to  │
│     main    │
└─────────────┘
```

---

## 7. Feature Matrix

| Feature | Layer 1 | Layer 2 | Layer 3 | GAD |
|---------|---------|---------|---------|-----|
| **Circuit Breaker** | ❌ N/A | ✅ Active | ✅ Active | 509 |
| **Quota Manager** | ❌ N/A | ✅ Active | ✅ Active | 510 |
| **Neural Adapter** | ❌ N/A | ✅ Active | ✅ Active | 511 |
| **Graph Executor** | ❌ N/A | ✅ Active | ✅ Active | 902 |
| **Workflow Loader** | ❌ N/A | ✅ Active | ✅ Active | 903 |
| **System Integrity** | ⚠️ Manual | ✅ Auto | ✅ Auto | 005 |
| **Session Shell** | ❌ N/A | ✅ Active | ✅ Active | 005 |
| **Receipts** | ❌ N/A | ✅ Created | ✅ Managed | 005 |
| **Commit Watermarks** | ❌ N/A | ✅ Added | ✅ Validated | 005 |
| **Knowledge Query** | ✅ Manual | ✅ Auto | ✅ Multi-source | 006 |
| **Semantic Search** | ❌ N/A | ✅ Basic | ✅ Vector | 006 |
| **Client Research** | ❌ N/A | ❌ N/A | ✅ Federated | 006 |
| **STEWARD Guidance** | ✅ Prompts | ✅ Validation | ✅ Enforcement | 007 |
| **Access Control** | ⚠️ Voluntary | ✅ Validated | ✅ Enforced | 007 |
| **Mod Registry** | ❌ N/A | ✅ Managed | ✅ Full | 007 |
| **Layer Detection** | Manual | ✅ Auto | ✅ Auto | 008 |
| **Graceful Degrade** | N/A | ✅ Auto | ✅ Auto | 008 |
| **Knowledge Graph** | ✅ YAML | ✅ Python | ✅ Vector DB | 008 |

---

## 8. Implementation Roadmap

### Phase 1: Foundation (Weeks 1-2)
**Goal:** GAD-5 (Runtime Engineering) Layer 1-2 working

```yaml
deliverables:
  - ✅ System integrity manifest
  - ✅ Verify-integrity script
  - ✅ Session Shell prototype
  - ✅ Receipt generation
  - ✅ Pre-commit hook
  
completion_criteria:
  - Agent can work in Layer 1 (prompt mode)
  - Agent can work in Layer 2 (with tools)
  - System boots with integrity check
  - Receipts created for all tasks
```

### Phase 2: Knowledge Foundation (Weeks 3-4)
**Goal:** GAD-6 (Knowledge Department) Layer 1-2 working

```yaml
deliverables:
  - ✅ Knowledge YAML structure
  - ✅ knowledge_query tool
  - ✅ Basic semantic search
  - ✅ Knowledge graph (YAML)
  - ✅ Access control rules
  
completion_criteria:
  - Agents can query knowledge (Layer 1 manual)
  - Agents can query knowledge (Layer 2 auto)
  - Knowledge graph enables better queries
  - Public/internal/confidential separation
```

### Phase 3: Governance Foundation (Weeks 5-6)
**Goal:** GAD-7 (STEWARD Governance) Layer 1-2 working

```yaml
deliverables:
  - ✅ STEWARD personality prompts
  - ✅ Governance rules (Layer 1-2)
  - ✅ steward_validate tool
  - ✅ Decision engine
  - ✅ Mod registry
  
completion_criteria:
  - STEWARD provides guidance (Layer 1)
  - STEWARD validates operations (Layer 2)
  - Access control enforced
  - Mod installation governed
```

### Phase 4: Integration (Weeks 7-8)
**Goal:** GAD-8 (Integration Matrix) working, all systems integrated

```yaml
deliverables:
  - ✅ Layer detection
  - ✅ Integration protocols
  - ✅ Cross-system tests
  - ✅ Degradation tests
  - ✅ Complete documentation
  
completion_criteria:
  - All systems communicate correctly
  - Graceful degradation works
  - Tests pass at all layers
  - Documentation complete
```

### Phase 5: Runtime Services (Weeks 9-12)
**Goal:** Layer 3 operational

```yaml
deliverables:
  - ✅ ResearchEngine API
  - ✅ Client research connectors
  - ✅ Vector DB integration
  - ✅ CI/CD enforcement
  - ✅ Audit logging
  - ✅ Production deployment
  
completion_criteria:
  - Full runtime services operational
  - Federated research working
  - CI/CD blocking bad PRs
  - Production-ready
```

---

## 9. Success Metrics (Overall)

```yaml
technical_metrics:
  - system_uptime: ">99.5%"
  - boot_time_layer1: "<2 seconds"
  - boot_time_layer2: "<5 seconds"
  - boot_time_layer3: "<10 seconds"
  - integrity_check_pass_rate: "100%"
  - knowledge_query_success: ">95%"
  - governance_compliance: ">98%"
  - degradation_success: ">99%"

user_metrics:
  - agent_satisfaction: ">4.5/5"
  - setup_difficulty: "<3/5"
  - documentation_clarity: ">4/5"
  - issue_resolution_time: "<24 hours"

business_metrics:
  - project_delivery_time: "-30%"
  - specification_accuracy: "+40%"
  - client_satisfaction: ">4.5/5"
  - cost_per_project: "-25%"
```

---

## 10. Key Architectural Decisions

### Decision 1: Three-Layer Architecture

**Rationale:**
- Graceful degradation from day one
- Each layer fully functional
- Clear upgrade path
- No vendor lock-in

### Decision 2: Separate Knowledge Department

**Rationale:**
- Knowledge persists across projects
- Different access patterns
- Can serve multiple agencies
- Reusable asset

### Decision 3: Hybrid Governance (STEWARD)

**Rationale:**
- Works without runtime
- Prompt-based guidance everywhere
- Runtime enforcement where available
- Constitutional approach

### Decision 4: Knowledge Graph as Glue

**Rationale:**
- Binds all concepts together
- Enables better queries
- Semantic relationships
- Works at all layers (YAML → Vector DB)

### Decision 5: Receipt-Based Accountability

**Rationale:**
- Audit trail for all work
- CI/CD can validate
- Traceable compliance
- No trust, verify

---

## 11. What Makes This Unique

```yaml
unique_selling_points:
  
  graceful_degradation:
    description: "Works from browser to full runtime"
    competitors: "Require backend from day one"
    advantage: "Zero setup cost, instant start"
    
  hybrid_governance:
    description: "Prompt + Runtime governance"
    competitors: "Runtime enforcement only"
    advantage: "Works everywhere, even browser"
    
  knowledge_as_service:
    description: "Separate knowledge department"
    competitors: "Knowledge embedded in code"
    advantage: "Reusable, federated, scalable"
    
  semantic_graph:
    description: "Concept relationships"
    competitors: "Flat file structures"
    advantage: "Better queries, discovery"
    
  receipt_accountability:
    description: "All work traceable"
    competitors: "Trust-based systems"
    advantage: "Audit trail, CI/CD validation"
```

---

## 12. Open Questions & Future Work

```yaml
short_term:
  - Q: "Which Layer 2 tools to implement first?"
    A: "knowledge_query, steward_validate, receipt_create"
  
  - Q: "YAML or JSON for knowledge bases?"
    A: "YAML (more readable), can convert to JSON if needed"
  
  - Q: "Pre-commit: block or watermark?"
    A: "Watermark (default), block (opt-in strict mode)"

medium_term:
  - Q: "Which vector DB for Layer 3?"
    A: "TBD - Qdrant, Pinecone, or Weaviate"
  
  - Q: "Client research API standard?"
    A: "TBD - REST vs GraphQL"
  
  - Q: "Mod registry compatibility checks?"
    A: "TBD - define mod spec format"

long_term:
  - Q: "Multi-agency knowledge sharing?"
    A: "TBD - federated knowledge network"
  
  - Q: "AI-assisted governance evolution?"
    A: "TBD - STEWARD learns from precedents"
  
  - Q: "Cross-project ML insights?"
    A: "TBD - anonymized learning corpus"
```

---

## 13. Getting Started

### For Developers

```bash
# 1. Clone repository
git clone https://github.com/kimeisele/vibe-agency
cd vibe-agency

# 2. Initialize Layer 1 (browser mode)
# Just open in browser - works immediately!

# 3. Upgrade to Layer 2 (Claude Code)
python scripts/setup-layer2.py

# 4. Upgrade to Layer 3 (full runtime)
python scripts/setup-layer3.py
# (Requires backend setup)
```

### For Architects

```
Read order:
1. This document (ARCHITECTURE_MAP.md)
2. GAD-5XX/ (Runtime Engineering - GAD-500, GAD-501, GAD-502)
3. GAD-6XX/ (Knowledge Department - GAD-600)
4. GAD-7XX/ (STEWARD Governance - GAD-700)
5. GAD-8XX/ (Integration Matrix - GAD-800)
```

### For Users

```
Start here:
1. QUICK_START_SESSION.md
2. USER_EXPERIENCE_GUIDE.md
3. SESSION_EXAMPLES.md
```

---

## 14. Summary

Vibe Agency is a **three-layer, gracefully degrading, hybrid-governance software specification system** that:

1. **Works everywhere** - Browser to full runtime
2. **Knows everything** - Separate knowledge department
3. **Governs itself** - Hybrid prompt + runtime governance
4. **Connects semantically** - Knowledge graph binds all concepts
5. **Proves its work** - Receipt-based accountability
6. **Degrades gracefully** - Each layer is fully functional

**Four GAD Pillars:**
- GAD-5 (Pillar 5): Runtime Engineering & context integrity (Docs: GAD-5XX/)
- GAD-6 (Pillar 6): Knowledge department & research (Docs: GAD-6XX/)
- GAD-7 (Pillar 7): STEWARD governance (Docs: GAD-7XX/)
- GAD-8 (Pillar 8): Integration & orchestration (Docs: GAD-8XX/)
- GAD-9 (Pillar 9): Semantic Orchestration - The Playbook Engine (Docs: GAD-9XX/)

**Three Layers:**
- Layer 1: Prompt-only (browser, $0)
- Layer 2: Tool-based (Claude Code, $20/mo)
- Layer 3: Runtime (APIs, $50-200/mo)

**Built on:**
- Agency OS (existing)
- Knowledge graph (semantic)
- Graceful degradation (core principle)
- Receipt accountability (trust, but verify)

---

## 15. Next Steps

1. ✅ **Review all 4 GAD vision documents** (GAD-5XX, GAD-6XX, GAD-7XX, GAD-8XX)
2. **Approve or revise architecture**
3. **Begin Phase 1 implementation** (GAD-5 Layer 1-2)
4. **Iterate based on learnings**

---

**END OF ARCHITECTURE MAP**

*This map provides the complete overview. Each GAD has its own detailed vision document.*

**Documents:**
- GAD-500: Runtime Engineering EPIC (COMPLETE v2.0)
- GAD-501: Layer 0 and Layer 1 (COMPLETE)
- GAD-502: Haiku Hardening (PLAN)
- GAD-509: Circuit Breaker (COMPLETE - Iron Dome)
- GAD-510: Quota Manager (COMPLETE - Cost Control)
- GAD-511: Neural Adapter Strategy (COMPLETE - Multi-Provider LLM)
- GAD-600: Knowledge Department (VISION)
- GAD-700: STEWARD Governance (VISION)
- GAD-800: Integration Matrix (VISION)
- GAD-902: Graph Executor (COMPLETE - Topology & Dependencies)
- GAD-903: Workflow Loader (COMPLETE - Data → Logic)
- GAD-906: Semantic Lenses (PROTOTYPE - Intelligence Injection)
- ARCHITECTURE_MAP: This document

---

## 6. Recent Kernel Implementation (ARCH-021 to ARCH-025)

**Date:** November 20-21, 2025
**Status:** ✅ COMPLETE

### ARCH-021: FIFO Scheduler (Engine Block Phase 1)
**File:** `vibe_core/scheduling/scheduler.py`
**Purpose:** Task queue management with FIFO ordering
**Status:** ✅ Operational

### ARCH-022: Kernel Loop (Engine Block Phase 2)
**File:** `vibe_core/kernel.py`
**Purpose:** Central kernel with agent registry, task scheduling, tick-based execution
**Features:**
- Agent registration and dispatch
- Task scheduling integration
- Tick-based execution loop
- Ledger integration for all operations
**Status:** ✅ Operational

### ARCH-023: Agent Dispatch (The Synapse)
**File:** `vibe_core/kernel.py` (dispatch logic)
**Purpose:** Route tasks to appropriate agents based on agent_id
**Status:** ✅ Operational

### ARCH-024: Task Execution Ledger (The Black Box)
**File:** `vibe_core/ledger.py`
**Purpose:** SQLite-based task execution tracking
**Features:**
- Automatic success/failure recording
- Queryable execution history
- Performance metrics
**Status:** ✅ Operational

### ARCH-025: The Cortex (LLM Integration)
**File:** `vibe_core/llm/provider.py`
**Purpose:** Abstract LLM provider interface for multi-provider support
**Providers:** Anthropic (Claude), OpenAI (GPT), Google (Gemini)
**Status:** ✅ Operational

### Integration Flow

```
STEWARD (Claude Code)
    ↓
Playbook Engine (ARCH-013)
    ↓
RouterBridge (connects playbook → specialists)
    ↓
Specialist (e.g., PlanningSpecialist)
    ↓
Kernel.submit(task) (ARCH-022)
    ↓
Scheduler.add(task) (ARCH-021)
    ↓
Kernel.tick() → dispatch task (ARCH-023)
    ↓
Agent executes (uses LLMProvider from ARCH-025)
    ↓
Ledger.record_success/failure (ARCH-024)
```

**→ Full implementation details: See `docs/architecture/ARCH/README.md`**

