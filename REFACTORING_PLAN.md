# Refactoring Plan: Monorepo Structure & Knowledge Hub

**Version:** 1.0
**Date:** 2025-11-12
**Author:** Gemini Code Assistant
**Status:** Proposed

## 1. Objective

This document outlines a plan to refactor the `vibe-agency` repository from a single-project structure into a scalable, multi-client monorepo. It also introduces a solution to improve the searchability and discoverability of the core knowledge within the system.

The primary goals are:
1.  To create a clean, intuitive, and scalable directory structure for managing multiple clients and projects.
2.  To clearly separate the core "Agency OS" from the client-specific work.
3.  To improve the maintainability and searchability of the knowledge base without introducing complex new technologies.
4.  To execute this refactoring safely, without breaking the integrity of the existing specification ("the AI's implementation").

## 2. Current State Analysis & Problem Definition

The current repository structure is the result of organic growth focused on defining the Agency OS itself. This has led to several challenges:

-   **Flat & Unscalable Structure:** The core logic (`agency_os`, `system_steward_framework`) co-exists in the root directory with operational folders like `artifacts` and project-specific `docs`.
-   **No Client Separation:** There is no designated place to manage work for different clients. The question "Where do I create a new project for a new client?" has no clear answer.
-   **Poor Discoverability:** The system's intelligence is distributed across numerous YAML files. Finding a specific rule (e.g., "What is the test coverage requirement for v1.0?") requires searching through multiple files, making the system difficult for humans to navigate.

## 3. Proposed "Grand Plan"

### 3.1. Target Monorepo Structure

The proposed structure separates the core **packages** of the agency from the **clients** it serves.

```
/
├── packages/
│   ├── agency_os/              # The core operating system (MOVED)
│   └── system_steward_framework/ # The meta-governance (MOVED)
│
├── clients/
│   └── (empty)                 # Future home for all client projects
│
├── docs/                       # Agency-level documentation
│   ├── AGENCY_OS_DEEP_DIVE_ANALYSIS.md
│   └── AGENCY_OS_FUNDAMENTAL_UNDERSTANDING.md
│
└── README.md                   # Main monorepo README (updated)
```

**Rationale:**
-   **`packages/`**: Contains the reusable "software" of the agency. This isolates the core OS from specific project work, allowing it to be versioned and updated independently.
-   **`clients/`**: A dedicated, scalable directory to house all client work. Each sub-directory will represent a client, with further sub-directories for each of their projects (e.g., `clients/client-a/project-alpha/`).
-   **`docs/`**: A centralized location for high-level documentation pertaining to the entire monorepo and the Agency OS itself.

### 3.2. The Knowledge Hub Concept

To solve the searchability problem, a new file, `KNOWLEDGE_HUB.md`, will be created in the root directory. This file will serve as a manually curated "master index" or table of contents for the entire knowledge base.

-   **No Code, No RAG:** It is a simple Markdown file with semantic headings and direct links to the relevant sections in the YAML files.
-   **Lean & Maintainable:** It only needs to be updated when new knowledge files are added, not when individual rules change.
-   **Playbook Character:** It acts as the central entry point for any human (or agent) wanting to understand the system's rules, perfectly fitting the "playbook" nature of the project.

---

## 4. Detailed Execution & Validation Plan

This plan follows a safe, three-phase approach: **Plan -> Execute -> Validate**.

### Phase 1: Planning & Risk Analysis

**Objective:** To identify any hardcoded relative paths that could break during the file move.

**Action:** Execute the following command from the repository root:

```bash
grep -rE '\.\./' agency_os/ system_steward_framework/
```

**Expected Result:** The command should return no results. The current specification files do not appear to use relative paths for cross-references.

**Contingency:** If any paths are found, they must be manually documented and corrected in Phase 2 after the move.

### Phase 2: Execution

**Objective:** To perform the file and directory moves and create the new knowledge hub. All `mv` operations **must** use `git mv` to preserve file history.

**Action:** Execute the following commands sequentially from the repository root:

```bash
# 1. Create the new top-level directories
mkdir packages
mkdir clients

# 2. Move the core frameworks into 'packages/'
# Using git mv is crucial to preserve history
git mv agency_os packages/
git mv system_steward_framework packages/

# 3. Move the existing analysis documents into the top-level 'docs/'
# Note: The root 'docs' folder might already exist. This command moves the files into it.
git mv AGENCY_OS_DEEP_DIVE_ANALYSIS.md docs/
git mv AGENCY_OS_FUNDAMENTAL_UNDERSTANDING.md docs/

# 4. Remove the now-empty, project-specific 'artifacts' directory
# This will be created inside client project folders in the future.
# Ensure it is empty before removing.
rmdir artifacts

# 5. Create the new KNOWLEDGE_HUB.md file
# The paths in this file reflect the NEW target structure.
cat << 'EOF' > KNOWLEDGE_HUB.md
# Agency OS Knowledge Hub

This is the central index to quickly find rules, concepts, and specifications within the Agency OS.

## 1. Core Concepts
- **Workflow State Machine:** [View Definition](packages/agency_os/00_system/state_machine/ORCHESTRATION_workflow_design.yaml)
- **Data Contracts (Schemas):** [View All Schemas](packages/agency_os/00_system/contracts/ORCHESTRATION_data_contracts.yaml)
- **Recommended Tech Stack:** [View Analysis](packages/agency_os/00_system/knowledge/ORCHESTRATION_technology_comparison.yaml)

## 2. Governance Rules

### Planning & Scope
- **v1.0 Feature Constraints (What we don't build):** [FAE_constraints.yaml](packages/agency_os/01_planning_framework/knowledge/FAE_constraints.yaml)
- **Complexity & Prioritization Rules:** [APCE_rules.yaml](packages/agency_os/01_planning_framework/knowledge/APCE_rules.yaml)
- **Feature Dependency Graph:** [FDG_dependencies.yaml](packages/agency_os/01_planning_framework/knowledge/FDG_dependencies.yaml)

### Code & Quality
- **Code Generation Constraints:** [CODE_GEN_constraints.yaml](packages/agency_os/02_code_gen_framework/knowledge/CODE_GEN_constraints.yaml)
- **Code Quality Gates & Rules:** [CODE_GEN_quality_rules.yaml](packages/agency_os/02_code_gen_framework/knowledge/CODE_GEN_quality_rules.yaml)

### QA & Testing
- **QA Constraints (incl. HITL):** [QA_constraints.yaml](packages/agency_os/03_qa_framework/knowledge/QA_constraints.yaml)
- **QA Quality Rules (Release Criteria):** [QA_quality_rules.yaml](packages/agency_os/03_qa_framework/knowledge/QA_quality_rules.yaml)

### Deployment
- **Deployment Constraints (Strategies & Platforms):** [DEPLOY_constraints.yaml](packages/agency_os/04_deploy_framework/knowledge/DEPLOY_constraints.yaml)
- **Deployment Quality Rules (Rollback Triggers):** [DEPLOY_quality_rules.yaml](packages/agency_os/04_deploy_framework/knowledge/DEPLOY_quality_rules.yaml)

### Maintenance
- **Maintenance Constraints (Bug Severity):** [MAINTENANCE_constraints.yaml](packages/agency_os/05_maintenance_framework/knowledge/MAINTENANCE_constraints.yaml)
- **Maintenance Triage Rules (SLAs):** [MAINTENANCE_triage_rules.yaml](packages/agency_os/05_maintenance_framework/knowledge/MAINTENANCE_triage_rules.yaml)
EOF

# 6. Update the main README.md
# This command uses 'sed' to replace the old links with the new 'docs/' path.
sed -i '' 's|(\./AGENCY_OS_FUNDAMENTAL_UNDERSTANDING.md)|(docs/AGENCY_OS_FUNDAMENTAL_UNDERSTANDING.md)|g' README.md
sed -i '' 's|(\./AGENCY_OS_DEEP_DIVE_ANALYSIS.md)|(docs/AGENCY_OS_DEEP_DIVE_ANALYSIS.md)|g' README.md
```

### Phase 3: Validation

**Objective:** To programmatically verify that the refactoring was successful and did not introduce errors.

**Action 1: Automated Link Checking**
Run the following validation script from the repository root. It will parse the two key Markdown files and check that all local links point to existing files.

```bash
#!/bin/bash
set -e
echo "INFO: Starting validation..."
FILES_TO_CHECK=("README.md" "KNOWLEDGE_HUB.md")
EXIT_CODE=0

for markdown_file in "${FILES_TO_CHECK[@]}"; do
  echo "INFO: Checking links in ${markdown_file}..."
  # Extract markdown links like [text](path) but ignore http links
  links=$(grep -o '\[.*\]([^)]*)' "${markdown_file}" | grep -v 'http' | sed -e 's/.*\[\(.*\)\]/\1/')
  
  if [ -z "${links}" ]; then
    echo "WARN: No local links found in ${markdown_file}."
    continue
  fi

  for link in ${links}; do
    # Remove potential anchor from link
    link_path=$(echo "${link}" | cut -d'#' -f1)
    if [ -e "${link_path}" ]; then
      echo "  ✅ OK: ${link_path}"
    else
      echo "  ❌ FAILED: ${link_path} in ${markdown_file} does not exist."
      EXIT_CODE=1
    fi
  done
done

if [ "${EXIT_CODE}" -eq 0 ]; then
  echo "INFO: Validation successful. All local links are valid."
else
  echo "ERROR: Validation failed. Broken links found."
fi

exit ${EXIT_CODE}
```

**Expected Result:** The script should run and exit with code 0, printing "Validation successful."

**Action 2: Git Status Review**
Run `git status`. The output should show a list of `renamed:` files and one `new file:` (`KNOWLEDGE_HUB.md`), plus the modified `README.md`. This confirms Git has correctly tracked the move operations.

## 5. Commit Strategy

Once validation is successful, the changes should be committed.

**Action:** Stage all changes and use the following commit message to provide clear history.

```bash
git add .
git commit -m "refactor(repo): Establish monorepo structure and add knowledge hub" \
           -m "Restructures the repository to support multiple clients and projects by separating core 'packages' from future 'clients' work."
           -m "- Moves 'agency_os' and 'system_steward_framework' into a 'packages/' directory."
           -m "- Moves high-level analysis documents into a top-level 'docs/' directory."
           -m "Adds a central KNOWLEDGE_HUB.md file to act as a master index for all YAML-based knowledge, improving discoverability."
```

This concludes the refactoring plan. Upon successful execution, the repository will be in a clean, scalable state, ready for future work.
