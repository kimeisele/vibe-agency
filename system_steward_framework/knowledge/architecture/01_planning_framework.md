
# 01_planning_framework.md

## Purpose

This document describes the `agency_os/01_planning_framework/`, which is responsible for the initial "ideation to specification" phase of a project. It takes a user's vague idea and transforms it into a concrete, validated, and buildable technical plan. This framework is composed of three specialist agents, each with a distinct role and knowledge base.

---

## Components

### 1. `VIBE_ALIGNER_v3.md` (The Product Manager)

*   **Role:** This agent acts as a Senior Product Manager. Its primary goal is to guide a user from a vague concept to a validated feature list. It is the first point of contact in the planning process.
*   **Process:**
    1.  **Education:** It first calibrates the user's expectations by explaining the difference between a Prototype, an MVP, and a v1.0 product.
    2.  **Extraction:** It asks targeted questions to extract concrete features from the user's idea.
    3.  **Validation & Negotiation:** It uses its knowledge base to validate the feasibility of each feature, reject impossible requests, suggest alternatives, and negotiate the final scope to ensure it's realistic for a v1.0 launch.
*   **Knowledge Base:**
    *   **`FAE_constraints.yaml` (Feasibility Analysis Engine):** A database of technical constraints used to identify features that are too complex or expensive for a v1.0 project (e.g., "real-time video streaming," "self-hosted full-text search").
    *   **`FDG_dependencies.yaml` (Feature Dependency Graph):** A knowledge graph that defines the logical dependencies between features (e.g., "a shopping cart requires a product catalog"). This is used to proactively identify and suggest missing components.
    *   **`APCE_rules.yaml` (Automated Prioritization & Complexity Engine):** A rule set for scoring feature complexity and value. This is used to calculate the total effort for a project and trigger scope negotiation if the project becomes too large.
*   **Output:** A validated `feature_spec.json` file that is ready for the next agent.

### 2. `GENESIS_BLUEPRINT_v5.md` (The Architect)

*   **Role:** This agent acts as a Senior Software Architect. It takes the validated `feature_spec.json` from the `VIBE_ALIGNER` and generates a complete, production-ready software architecture.
*   **Process:**
    1.  **Core Module Selection:** It algorithmically selects a minimal set of core, standard-library-only modules based on the capabilities required by the feature list.
    2.  **Extension Design:** It maps each feature to a single, isolated "extension" module that depends on the core but not on other extensions.
    3.  **Validation:** It performs a final validation check using the `FAE_constraints.yaml` to ensure the complete architecture is sound.
*   **Knowledge Base:**
    *   It primarily uses the same `FAE_constraints.yaml` and `ORCHESTRATION_data_contracts.yaml` to ensure its output is feasible and conforms to the system's data structures.
*   **Output:** An `architecture.json` file detailing the complete software plan, including directory structure, module APIs, dependencies, and an implementation guide.

### 3. `GENESIS_UPDATE.md` (The Refactorer)

*   **Role:** This agent acts as an Incremental Architecture Refinement specialist. Its purpose is to handle changes to an *existing* architecture without causing "architecture drift."
*   **Process:**
    1.  **Analyze Change:** It takes an existing `architecture.json` and a natural language change request (e.g., "Add comments to blog posts").
    2.  **Calculate Ripple Effects:** It uses the `FDG_dependencies.yaml` to determine all other parts of the system that will be affected by the change (e.g., adding comments requires database schema changes, new API endpoints, and new tests).
    3.  **Generate Diff Patch:** Instead of regenerating the entire architecture, it outputs a set of minimal `diff` patches that can be surgically applied to the existing files.
*   **Knowledge Base:**
    *   It relies heavily on `FDG_dependencies.yaml` to understand the ripple effects of any given change.
*   **Output:** An `update_spec.json` file containing the diff patches and an explanation of the changes.
