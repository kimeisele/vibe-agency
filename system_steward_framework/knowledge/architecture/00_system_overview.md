
# 00_system_overview.md

## Purpose

This document provides a high-level overview of the `agency_os/core_system/` directory, which forms the core governance and orchestration layer of the Agency Operating System (AOS). This directory contains the "brain" of the entire system, defining the rules, states, data structures, and recommended technology for the master SDLC workflow.

---

## Components

### 1. `AGENCY_OS_ORCHESTRATOR_v1.md` (The Orchestrator)

*   **Role:** This is the master conductor of the software development process. It is a stateful agent whose sole responsibility is to execute the SDLC state machine.
*   **Function:** It does not perform any specialist tasks like coding or testing. Instead, it reads the `project_manifest.json` to determine the current state of a project and invokes the correct specialist agent (e.g., `CODE_GENERATOR`, `QA_VALIDATOR`) for that state.
*   **Core Principle:** It is artifact-centric, meaning its actions are driven by the creation and status of data artifacts (like `qa_report.json`), not by direct human commands. It is governed by the state machine and data contracts.

### 2. `ORCHESTRATION_workflow_design.yaml` (The State Machine)

*   **Role:** This file defines the official Software Development Lifecycle (SDLC) for the AOS. It is the single source of truth for the workflow logic.
*   **Structure:**
    *   **States:** Defines the core phases of the workflow, such as `PLANNING`, `CODING`, `TESTING`, `AWAITING_QA_APPROVAL`, `DEPLOYMENT`, `PRODUCTION`, and `MAINTENANCE`. Each state is mapped to a responsible framework.
    *   **Transitions:** Defines the valid, automated, or Human-in-the-Loop (HITL) triggers that allow a project to move from one state to the next (e.g., `T4_StartDeployment` is triggered by a `qa_approved_signal`).
    *   **Loops:** Defines the official feedback and error-handling loops, such as `L1_TestFailed` (when QA is rejected) and `L2_DeployFailed` (when a deployment is rolled back).

### 3. `ORCHESTRATION_data_contracts.yaml` (The Contracts)

*   **Role:** This file defines the JSON schemas for all data artifacts that are passed between the different states of the workflow. It ensures data integrity and consistency across the entire system.
*   **Key Schemas Defined:**
    *   `project_manifest.schema.json`: The central manifest tracking project state and artifact links.
    *   `code_gen_spec.schema.json`: The input for the coding phase.
    *   `test_plan.schema.json`: The input for the testing phase.
    *   `qa_report.schema.json`: The output of the testing phase, acting as a gate for deployment.
    *   `deploy_receipt.schema.json`: The proof of a successful deployment.
    *   `bug_report.schema.json`: The input for the maintenance workflow.
*   **Governance:** It also includes strict rules for schema evolution to prevent breaking changes.

### 4. `ORCHESTRATION_technology_comparison.yaml` (The Recommended Engine)

*   **Role:** This document analyzes and recommends the underlying orchestration engine technology required to run the AOS state machine, particularly focusing on the critical v1.0 requirements.
*   **Critical Requirements Analyzed:**
    *   **Durable Execution:** The ability for workflows to survive for days or weeks, especially while waiting for human approval.
    *   **HITL Support:** Native ability to pause a workflow for human input without consuming resources.
    *   **Observability:** The ability to query and visualize the state of any given workflow.
*   **Recommendation:** Based on a trade-off analysis, **Temporal (Cloud)** is the recommended engine for v1.0 due to its excellent support for all critical requirements at the lowest initial setup cost. Prefect (Self-Hosted) is listed as an acceptable alternative, while GitHub Actions is explicitly rejected as architecturally unsuitable for this kind of durable orchestration.
