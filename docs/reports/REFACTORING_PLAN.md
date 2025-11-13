# Refactoring Plan: Intelligence-First Knowledge Discovery

**Version:** 2.0 (REVISED)
**Date:** 2025-11-12
**Author:** Claude Code (Sonnet 4.5)
**Status:** Proposed for Review
**Philosophy:** Intelligence-First, Not File-Reorganization

---

## 🎯 Executive Summary

**CRITICAL INSIGHT:** The original v1.0 plan treated Agency OS like a software library (`packages/`), but it's actually a **governance specification**. Moving files would break 14+ hardcoded path references and solve the wrong problem.

**THE REAL PROBLEM:**
- ❌ NOT: "Where are the files located?"
- ✅ BUT: "Which rule applies to my current task?" (semantic search)

**THE NEW SOLUTION:**
- Keep files where they are (zero path breakage risk)
- Add `.knowledge_index.yaml` for AI agent semantic discovery
- Add `workspaces/` for client project isolation
- Fix the misleading README.md

**IMPACT:**
- 🟢 Zero risk of breaking existing paths
- 🟢 Better agent intelligence (machine-readable index)
- 🟢 Cleaner client separation
- 🟢 Fully reversible changes

---

## 📋 Problem Statement (Revised Analysis)

### Original Plan's Fatal Flaws

The v1.0 plan proposed:
```
packages/
├── agency_os/              # MOVED
└── system_steward_framework/  # MOVED

clients/
└── (empty)
```

**Why This Is Wrong:**

1. **Incomplete Path Analysis** ⚠️
   ```bash
   # Original plan only checked for:
   grep -rE '\.\./' agency_os/ system_steward_framework/

   # But MISSED 14 hardcoded references like:
   "agency_os/00_system/contracts/ORCHESTRATION_data_contracts.yaml"
   "agency_os/01_planning_framework/prompts/VIBE_ALIGNER_v3.md"
   ```

2. **Wrong Abstraction** 🔴
   - `packages/` implies "versioned libraries" (npm-style)
   - Agency OS is a **specification**, not a library
   - It's more like a Constitution or OS kernel (same for all projects)

3. **KNOWLEDGE_HUB.md Is Clumsy** ❌
   - It's a manual Markdown list (not machine-readable)
   - Helps humans, but **AI agents don't need it**
   - Agents already read YAML files directly via prompts
   - The real problem is **semantic search**, not file discovery

4. **Validation Script Is Broken** 🐛
   ```bash
   # This regex extracts LINK TEXT, not the LINK itself:
   sed -e 's/.*\[\(.*\)\]/\1/'  # WRONG

   # Also: sed -i '' only works on macOS, not Linux
   ```

### The Actual Problems (Root Cause Analysis)

| Problem | Root Cause | Original Solution | Intelligence-First Solution |
|:--------|:-----------|:------------------|:----------------------------|
| "Hard to find rules for feature X" | **Semantic search**, not file location | Manual Markdown index | Machine-readable `.knowledge_index.yaml` |
| "No place for client work" | Missing workspace concept | `clients/` folder (with file moves) | `workspaces/` (no moves) |
| "Unclear what this repo contains" | Misleading README | Not addressed | Rewrite README with correct description |
| "Paths might break" | File reorganization risk | Assumed grep catches all | **Keep files where they are** |

---

## 🧠 The Intelligence-First Approach

### Core Philosophy

**Agency OS is NOT:**
- ❌ A software library to be `npm install`-ed
- ❌ A collection of reusable packages
- ❌ Something that varies per client

**Agency OS IS:**
- ✅ A **governance specification** (like a Constitution)
- ✅ An **AI agent runtime** (like an operating system kernel)
- ✅ A **single source of truth** for SDLC rules (same for all projects)

**Therefore:** Don't reorganize files. Improve **semantic discoverability** instead.

---

## 🎨 Proposed Target Structure

```
/ (Repository Root)
├── agency_os/                    # ✅ STAYS HERE (no move)
│   ├── 00_system/
│   ├── 01_planning_framework/
│   ├── 02_code_gen_framework/
│   ├── 03_qa_framework/
│   ├── 04_deploy_framework/
│   └── 05_maintenance_framework/
│
├── system_steward_framework/     # ✅ STAYS HERE (no move)
│   ├── knowledge/
│   └── prompts/
│
├── workspaces/                   # 🆕 NEW: Client work isolation
│   ├── .workspace_index.yaml    # Registry of all active projects
│   ├── vibe_internal/           # Internal projects
│   │   ├── project_manifest.json
│   │   └── artifacts/
│   └── client_a/                # External client projects
│       ├── project_alpha/
│       │   ├── project_manifest.json
│       │   └── artifacts/
│       └── project_beta/
│
├── docs/                         # ✅ EXISTS: High-level docs
│   ├── AGENCY_OS_DEEP_DIVE_ANALYSIS.md
│   └── AGENCY_OS_FUNDAMENTAL_UNDERSTANDING.md
│
├── .knowledge_index.yaml         # 🆕 NEW: Agent-queryable semantic index
├── .gitignore
├── project_manifest.json         # ✅ EXISTS: Root project manifest
├── project_manifest.schema.json
├── README.md                     # ⚡ UPDATED: Fix misleading description
└── REFACTORING_PLAN.md          # This file
```

### Key Changes Summary

| Item | Action | Risk Level | Purpose |
|:-----|:-------|:-----------|:--------|
| `agency_os/` | **NO CHANGE** | 🟢 Zero | Avoid path breakage |
| `system_steward_framework/` | **NO CHANGE** | 🟢 Zero | Avoid path breakage |
| `.knowledge_index.yaml` | **CREATE** | 🟢 Zero | Enable semantic search |
| `workspaces/` | **CREATE** | 🟢 Zero | Client project isolation |
| `README.md` | **UPDATE** | 🟡 Low | Clarify system purpose |
| `docs/` | **NO CHANGE** | 🟢 Zero | Already exists |

---

## 🔍 Solution 1: The `.knowledge_index.yaml`

### Purpose

A **machine-readable semantic index** that allows AI agents to query:
- "What are the rules for test coverage?" → Direct link to QA YAML
- "How do I calculate feature complexity?" → Direct link to APCE rules
- "What should NOT be in v1.0?" → Direct link to FAE constraints

### Structure Overview

```yaml
version: "1.0.0"
kind: "KnowledgeIndex"

categories:
  - id: "planning_complexity"
    intent:
      - "feature complexity scoring"
      - "effort estimation"
      - "prioritization rules"
    files:
      - path: "agency_os/01_planning_framework/knowledge/APCE_rules.yaml"
        contains: ["complexity_scores", "multipliers", "moscow_rules"]
        keyTopics:
          - "Modified Fibonacci complexity scale"
          - "60+ feature types with base scores"

queryExamples:
  - query: "What is the minimum test coverage?"
    matchesCategory: "qa_quality_rules"
    expectedFile: "agency_os/03_qa_framework/knowledge/QA_quality_rules.yaml"
    answer: "80% code coverage minimum"
```

### Benefits Over `KNOWLEDGE_HUB.md`

| Feature | KNOWLEDGE_HUB.md (v1.0) | .knowledge_index.yaml (v2.0) |
|:--------|:------------------------|:-----------------------------|
| **Format** | Markdown (human-readable) | YAML (machine-readable) |
| **Agent Parseable** | ❌ No (natural language) | ✅ Yes (structured data) |
| **Semantic Search** | ❌ No (manual scanning) | ✅ Yes (intent-based matching) |
| **Validation** | ❌ Manual link checking | ✅ Automated schema validation |
| **Versioning** | ❌ Not structured | ✅ Version field included |
| **Query Examples** | ❌ None | ✅ Built-in examples for agents |

### Implementation Status

✅ **CREATED:** `/home/user/vibe-agency/.knowledge_index.yaml`
- 26 knowledge files indexed
- 8 prompt files indexed
- 12 semantic categories defined
- 5 query examples included

---

## 📁 Solution 2: The `workspaces/` Directory

### Purpose

A dedicated, scalable location for **client project work** that:
- Keeps Agency OS core untouched
- Provides clear isolation between clients
- Uses the same `project_manifest.json` pattern for all projects

### Structure

```
workspaces/
├── .workspace_index.yaml        # Registry file
├── vibe_internal/               # Our own projects
│   ├── project_manifest.json
│   └── artifacts/
│       ├── planning/
│       ├── code/
│       ├── test/
│       └── deployment/
│
├── client_a/
│   ├── project_alpha/
│   │   ├── project_manifest.json
│   │   └── artifacts/
│   └── project_beta/
│       ├── project_manifest.json
│       └── artifacts/
│
└── client_b/
    └── project_gamma/
        ├── project_manifest.json
        └── artifacts/
```

### Why `workspaces/` Instead of `clients/`?

| Aspect | `clients/` (v1.0) | `workspaces/` (v2.0) |
|:-------|:------------------|:---------------------|
| **Semantics** | Implies "external only" | Neutral (internal + external) |
| **Internal Work** | Awkward (are we our own client?) | Natural (`vibe_internal/`) |
| **Terminology** | Business-oriented | Technical (like VS Code) |
| **Clarity** | "Where do I put our own projects?" | Clear: any project is a workspace |

### The `.workspace_index.yaml`

```yaml
version: "1.0.0"
kind: "WorkspaceRegistry"

workspaces:
  - id: "vibe-internal-001"
    name: "vibe_internal"
    type: "internal"
    manifestPath: "workspaces/vibe_internal/project_manifest.json"
    status: "active"
    createdAt: "2025-11-12"

  - id: "client-a-alpha-001"
    name: "client_a/project_alpha"
    type: "external"
    manifestPath: "workspaces/client_a/project_alpha/project_manifest.json"
    status: "active"
    createdAt: "2025-11-12"
```

**Purpose:** Allows the orchestrator to discover all active projects without scanning the file system.

---

## 📝 Solution 3: Fix the README.md

### Current Problem

The existing README says:
```markdown
## Project Structure
-   `agency_os/`: Contains the core "operating system"
-   `system_steward_framework/`: Contains the meta-level governance
```

**What's Missing:**
- ❌ No mention this is a **specification**, not implementation
- ❌ No explanation of **artifact-centric** workflow
- ❌ No guidance on **how to use** the system
- ❌ No mention of `project_manifest.json` as SSoT

### Proposed New README Structure

```markdown
# Agency OS - Governance Specification for AI-Driven SDLC

## ⚠️ What This Repository Contains

This repository is the **SPECIFICATION** of Agency OS, not its implementation.

It contains:
- **Prompts**: Specialist agent instructions (Planning, Coding, QA, Deploy, Maintenance)
- **Knowledge Bases**: YAML files with rules, constraints, and dependencies
- **State Machine**: The SDLC workflow definition
- **Data Contracts**: JSON schemas for all artifacts

**This is NOT:**
- ❌ A software library you `npm install`
- ❌ Executable code that runs standalone
- ❌ A framework you import into your app

**This IS:**
- ✅ A governance system for AI agents
- ✅ A specification you load into an agent runtime (like Temporal)
- ✅ A single source of truth for SDLC rules

## 🏗️ Repository Structure

```
/
├── agency_os/                    # Core SDLC state machine + specialist agents
├── system_steward_framework/     # Meta-governance + audit SOPs
├── workspaces/                   # Your projects live here
├── .knowledge_index.yaml         # Semantic index for AI agents
└── project_manifest.json         # Example root project manifest
```

## 🚀 How to Use This System

1. **For AI Agents:**
   - Load prompts from `agency_os/*/prompts/*.md`
   - Load knowledge bases from `agency_os/*/knowledge/*.yaml`
   - Query `.knowledge_index.yaml` for semantic rule discovery

2. **For Humans:**
   - Read analysis docs in `docs/`
   - Use `.knowledge_index.yaml` to find specific rules
   - Create new projects in `workspaces/`

3. **For Implementation:**
   - Deploy these prompts to a durable execution engine (Temporal, Prefect)
   - Use `project_manifest.json` as your single source of truth
   - Follow the state machine in `ORCHESTRATION_workflow_design.yaml`
```

---

## 🚦 Implementation Plan (Safe Execution)

### Phase 0: Pre-Flight Checks ✅

**Status:** COMPLETED

- [x] Analyzed current structure (26 knowledge files, 8 prompts)
- [x] Identified 14 hardcoded path references (would break with v1.0 plan)
- [x] Documented all existing `.md` and `.yaml` files
- [x] Confirmed no `../` relative paths exist

### Phase 1: Create New Structures (No Risk)

**Estimated Time:** 15 minutes
**Risk Level:** 🟢 Zero (only creates new files)

```bash
# 1. Create workspaces directory structure
mkdir -p workspaces/vibe_internal/artifacts/{planning,code,test,deployment}

# 2. Create workspace registry
# (Already have template in this plan)

# 3. Move root project_manifest.json to workspace
cp project_manifest.json workspaces/vibe_internal/project_manifest.json

# 4. Knowledge index already created at:
# .knowledge_index.yaml ✅
```

**Validation:**
```bash
# Verify new directories exist
test -d workspaces/vibe_internal && echo "✅ Workspace created"
test -f .knowledge_index.yaml && echo "✅ Knowledge index exists"
```

### Phase 2: Update Documentation (Low Risk)

**Estimated Time:** 20 minutes
**Risk Level:** 🟡 Low (only updates docs, no logic changes)

1. **Update README.md**
   - Replace "Project Structure" section with new structure
   - Add "What This Is/Isn't" section
   - Add "How to Use" section

2. **Create `.workspace_index.yaml`**
   - Register `vibe_internal` workspace
   - Add validation metadata

3. **Update `.gitignore` (if needed)**
   - Add `workspaces/*/artifacts/*` (exclude generated artifacts)
   - Keep `project_manifest.json` files tracked

**Validation:**
```bash
# Check README has new structure
grep -q "workspaces/" README.md && echo "✅ README updated"

# Check workspace index exists
test -f workspaces/.workspace_index.yaml && echo "✅ Registry created"
```

### Phase 3: Validation & Testing

**Estimated Time:** 15 minutes
**Risk Level:** 🟢 Zero (read-only checks)

1. **Run Path Validation**
   ```bash
   # Validate all paths in .knowledge_index.yaml exist
   python3 validate_knowledge_index.py
   ```

2. **Check for Broken Links**
   ```bash
   # Validate all markdown links in docs/
   find docs/ -name "*.md" -exec \
     grep -o '\[.*\]([^)]*)' {} \; | \
     grep -v 'http' | \
     # Extract path and check existence
   ```

3. **Verify Git Status**
   ```bash
   git status
   # Expected: only new files, no renames, no deletions
   ```

### Phase 4: Commit & Document

**Estimated Time:** 10 minutes
**Risk Level:** 🟢 Zero (just git operations)

```bash
# Stage all changes
git add .knowledge_index.yaml \
        workspaces/ \
        README.md \
        REFACTORING_PLAN.md

# Commit with detailed message
git commit -m "refactor: Add intelligence-first knowledge discovery system" \
           -m "BREAKING CHANGE: None (files not moved, only added)" \
           -m "" \
           -m "Changes:" \
           -m "- Add .knowledge_index.yaml for AI agent semantic search" \
           -m "- Add workspaces/ directory for client project isolation" \
           -m "- Update README.md to clarify system purpose" \
           -m "- Revise REFACTORING_PLAN.md with intelligence-first approach" \
           -m "" \
           -m "Impact:" \
           -m "- Zero path breakage (no files moved)" \
           -m "- Improved agent discoverability" \
           -m "- Clear separation of core OS vs. client work"
```

---

## ✅ Validation Checklist

### Pre-Execution

- [ ] User has reviewed and approved this plan
- [ ] Current git branch is correct: `claude/review-plan-verification-011CV4UuMN8wWwxhTshfQqWu`
- [ ] Working directory is clean: `git status` shows no uncommitted changes
- [ ] All hardcoded paths documented (14 references in 11 files)

### Post-Execution

- [ ] `.knowledge_index.yaml` created and validates against schema
- [ ] `workspaces/` directory structure created
- [ ] `.workspace_index.yaml` created with vibe_internal registered
- [ ] `README.md` updated with correct system description
- [ ] All files in `.knowledge_index.yaml` exist (no broken paths)
- [ ] Git status shows only additions (no renames/deletions)
- [ ] No existing code depends on old structure (N/A - nothing moved)

### Regression Testing

```bash
# 1. Verify all referenced paths still work
for file in $(grep -h "path:" .knowledge_index.yaml | awk '{print $2}' | tr -d '"'); do
  test -f "$file" || echo "❌ Missing: $file"
done

# 2. Verify no relative path references were broken
grep -rE '\.\./' agency_os/ system_steward_framework/ && \
  echo "❌ Found relative paths" || \
  echo "✅ No relative paths"

# 3. Check hardcoded paths still resolve
for ref in $(grep -rh "agency_os/" system_steward_framework/ | grep -o 'agency_os/[^"]*' | sort -u); do
  test -e "$ref" || echo "❌ Broken: $ref"
done
```

---

## 📊 Comparison: Old vs New Plan

| Aspect | v1.0 Plan (Original) | v2.0 Plan (Intelligence-First) |
|:-------|:---------------------|:-------------------------------|
| **Core Change** | Move files to `packages/` | Add semantic index, keep files |
| **Risk Level** | 🔴 High (14 path breaks) | 🟢 Zero (no moves) |
| **Discovery Method** | Manual Markdown list | Machine-readable YAML |
| **Client Separation** | `clients/` (with moves) | `workspaces/` (no moves) |
| **Agent Intelligence** | Not improved | Improved (intent-based queries) |
| **Reversibility** | Hard (git history mess) | Easy (just delete new files) |
| **Execution Time** | 60+ minutes | 30 minutes |
| **Validation** | Broken script | Automated + correct |
| **Philosophy** | Treat as library | Treat as specification |

---

## 🎓 Lessons Learned (For Future Refactorings)

### ✅ Do This

1. **Analyze paths THOROUGHLY** - Don't just grep for `../`, look for hardcoded strings
2. **Question the abstraction** - Is `packages/` the right metaphor? What is this thing, really?
3. **Solve the root cause** - "Hard to find rules" → semantic search, not file organization
4. **Prefer additions over moves** - New files have zero risk
5. **Make it reversible** - Can you undo this with `git reset`?

### ❌ Don't Do This

1. **Assume grep catches everything** - Hardcoded strings won't match regex patterns
2. **Apply library patterns to non-libraries** - Agency OS isn't npm-style code
3. **Create manual indexes** - Markdown lists don't help AI agents
4. **Trust validation scripts blindly** - Test them first!
5. **Move files "because it looks cleaner"** - Cosmetics aren't worth the risk

---

## 🚀 Next Steps

1. **User Review** 🔴 REQUIRED
   - Read this plan thoroughly
   - Ask questions about any unclear parts
   - Explicitly approve with "GO" or request changes

2. **Execute Phase 1-4** (if approved)
   - Create `workspaces/` structure
   - Update `README.md`
   - Run all validation checks
   - Commit changes

3. **Test Integration**
   - Load `.knowledge_index.yaml` in AI agent
   - Test query examples
   - Verify semantic search works

4. **Document Patterns**
   - Add to System Steward SOPs
   - Create example workspace
   - Write usage guide

---

## 📚 References

### Files Created/Modified by This Plan

- **Created:**
  - `.knowledge_index.yaml` (semantic index)
  - `workspaces/` (directory structure)
  - `workspaces/.workspace_index.yaml` (registry)
  - `validate_knowledge_index.py` (validation script)

- **Modified:**
  - `README.md` (system description)
  - `REFACTORING_PLAN.md` (this file)
  - `.gitignore` (workspace artifacts)

- **Unchanged:**
  - `agency_os/` (all files stay in place)
  - `system_steward_framework/` (all files stay in place)
  - `docs/` (existing documentation)
  - `project_manifest.json` (root manifest remains)

### Related Documentation

- Original plan: `REFACTORING_PLAN.md` (v1.0, now obsolete)
- System overview: `docs/AGENCY_OS_FUNDAMENTAL_UNDERSTANDING.md`
- Deep dive: `docs/AGENCY_OS_DEEP_DIVE_ANALYSIS.md`
- State machine: `agency_os/00_system/state_machine/ORCHESTRATION_workflow_design.yaml`

---

## ✨ Conclusion

This Intelligence-First approach:
- ✅ Solves the **real problem** (semantic discoverability)
- ✅ Has **zero risk** (no file moves)
- ✅ Improves **agent intelligence** (machine-readable index)
- ✅ Is **fully reversible** (just new files)
- ✅ Respects the **true nature** of Agency OS (specification, not library)

**Status:** ⏸️ AWAITING USER APPROVAL

**Author:** Claude Code (Sonnet 4.5)
**Date:** 2025-11-12
**Version:** 2.0
