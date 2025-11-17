# VIBE AGENCY: Complete Architecture Map

**STATUS: VISION OVERVIEW**  
**PURPOSE: Bird's Eye View of Entire System**  
**AUDIENCE: Architects, Developers, Stakeholders**

---

## 1. The Complete Picture

```
-> status TODO: GAD-001 to GAD-004 need REFRAMING to fit into "PILLARS of GAD" (add to `ARCHITECTURE_MAP.md` when approved) 
-> fit into `Dependency Graph`
-> GAD-005 as FOUNDATION is SECURED
┌────────────────────────────────────────────────────────────┐
│                    VIBE AGENCY ARCHITECTURE                │
│                                                            │
│  ┌──────────────────────────────────────────────────────┐ │
│  │ GAD-005: CONTEXT INJECTION (Foundation)             │ │
│  │ • Layer 0: System Integrity                         │ │
│  │ • Layer 1: Session Shell                            │ │
│  │ • Layer 2: Ambient Context                          │ │
│  │ • Layer 3: Commit Watermarking                      │ │
│  │ • Layer 4: Remote Validation                        │ │
│  └──────────────────────────────────────────────────────┘ │
│                          ↕                                 │
│  ┌──────────────────────────────────────────────────────┐ │
│  │ GAD-006: KNOWLEDGE DEPARTMENT (Knowledge Services)  │ │
│  │ • Research Division                                 │ │
│  │ • Domain Knowledge                                  │ │
│  │ • Semantic Graph                                    │ │
│  │ • 3-Layer Deployment                                │ │
│  └──────────────────────────────────────────────────────┘ │
│                          ↕                                 │
│  ┌──────────────────────────────────────────────────────┐ │
│  │ GAD-007: STEWARD (Governance)                       │ │
│  │ • Hybrid Governance (Prompt + Runtime)              │ │
│  │ • Policy Management                                 │ │
│  │ • Access Control                                    │ │
│  │ • Mod Registry                                      │ │
│  └──────────────────────────────────────────────────────┘ │
│                          ↕                                 │
│  ┌──────────────────────────────────────────────────────┐ │
│  │ GAD-008: INTEGRATION MATRIX (Orchestration)         │ │
│  │ • Cross-System Communication                        │ │
│  │ • Graceful Degradation                              │ │
│  │ • Component Compatibility                           │ │
│  │ • Knowledge Graph Binding                           │ │
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
│  GAD-005    │  ← Foundation (must exist first)
│  Context    │
└─────────────┘
       ↓ provides context to
┌─────────────┐     ┌─────────────┐
│  GAD-006    │     │  GAD-007    │
│  Knowledge  │  ←→ │  STEWARD    │
└─────────────┘     └─────────────┘
       ↓                   ↓
       └────────┬──────────┘
                ↓
        ┌─────────────┐
        │  GAD-008    │  ← Orchestrates all
        │ Integration │
        └─────────────┘

Dependencies:
- GAD-006 needs GAD-005 (uses receipts, integrity)
- GAD-007 needs GAD-005 (governs context layers)
- GAD-006 ↔ GAD-007 (bidirectional - knowledge needs governance, governance uses knowledge)
- GAD-008 needs all (orchestrates everything)
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
    
  - name: "ReceiptManager"
    system: "GAD-005"
    layers: [2, 3]
    purpose: "Receipt generation and validation"
    
  - name: "IntegrityChecker"
    system: "GAD-005"
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
    system: "GAD-005"
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
    system: "GAD-005"
    layers: [2, 3]
    purpose: "Work accountability"
```

---

## 5. Complete Directory Structure

```
vibe-agency/
│
├── .vibe/                              # GAD-005 Runtime artifacts
│   ├── system_integrity_manifest.json  # Layer 0
│   ├── state.json                      # Symbiotic state
│   ├── receipts/                       # Layer 2+3
│   └── audit/                          # Layer 3 only
│
├── agency_os/                          # Core Agency
│   ├── 01_planning_framework/
│   │   ├── agents/
│   │   │   ├── VIBE_ALIGNER/
│   │   │   ├── GENESIS_BLUEPRINT/
│   │   │   └── LEAN_CANVAS_VALIDATOR/
│   │   └── knowledge/                  # Being migrated to Knowledge Dept
│   │
│   ├── 02_code_gen_framework/
│   ├── 03_qa_framework/
│   ├── 04_deploy_framework/
│   └── 05_maintenance_framework/
│
├── knowledge_department/               # GAD-006
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
├── steward/                            # GAD-007
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
├── integration/                        # GAD-008
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
├── scripts/                            # GAD-005 scripts
│   ├── verify-system-integrity.py
│   ├── generate-integrity-manifest.py
│   ├── update-system-status.sh
│   ├── validate_receipts.py
│   └── check_watermarks.py
│
├── .git/hooks/                         # GAD-005 Layer 3
│   └── pre-commit
│
├── .github/workflows/                  # GAD-005 Layer 4
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
└── vibe-cli                            # GAD-005 Session Shell
```

---

## 6. Data Flow Diagram

```
┌─────────────┐
│    User     │
└─────────────┘
       ↓ interacts with
┌─────────────┐
│  vibe-cli   │  (GAD-005 Layer 1)
│ Session     │
│  Shell      │
└─────────────┘
       ↓ boots system
┌─────────────┐
│  Layer 0    │  (GAD-005)
│  Integrity  │
│   Check     │
└─────────────┘
       ↓ if verified
┌─────────────┐     ┌─────────────┐
│   Agent     │────▶│  STEWARD    │  (GAD-007)
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
│  Knowledge  │      │   Receipt   │  (GAD-005)
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
│  Pre-commit │  (GAD-005 Layer 3)
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
│   CI/CD     │  (GAD-005 Layer 4)
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
**Goal:** GAD-005 Layer 1-2 working

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
**Goal:** GAD-006 Layer 1-2 working

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
**Goal:** GAD-007 Layer 1-2 working

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
**Goal:** GAD-008 working, all systems integrated

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
2. GAD-005 (Context Injection)
3. GAD-006 (Knowledge Department)
4. GAD-007 (STEWARD Governance)
5. GAD-008 (Integration Matrix)
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

**Four GADs:**
- GAD-005: Context injection & integrity
- GAD-006: Knowledge department & research
- GAD-007: STEWARD governance
- GAD-008: Integration & orchestration

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

1. ✅ **Review all 4 GAD vision documents**
2. **Approve or revise architecture**
3. **Begin Phase 1 implementation** (GAD-005 Layer 1-2)
4. **Iterate based on learnings**

---

**END OF ARCHITECTURE MAP**

*This map provides the complete overview. Each GAD has its own detailed vision document.*

**Documents:**
- GAD-005: Context Injection (FINAL v2.0)
- GAD-006: Knowledge Department (VISION)
- GAD-007: STEWARD Governance (VISION)
- GAD-008: Integration Matrix (VISION)
- ARCHITECTURE_MAP: This document
