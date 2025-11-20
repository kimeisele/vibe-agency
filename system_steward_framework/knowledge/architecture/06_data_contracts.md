
# 06_data_contracts.md

## Purpose

This document provides a summary of the 6 central data contracts that govern the flow of information between the different frameworks of the Agency Operating System (AOS). These schemas are the "lingua franca" of the system, ensuring that each specialist agent produces and consumes data in a predictable and validated format. They are defined in `agency_os/core_system/contracts/ORCHESTRATION_data_contracts.yaml`.

---

## Core Schemas

### 1. `project_manifest.schema.json`

*   **Purpose:** This is the single source of truth for a project. It's the central contract that tracks the project's current state (`current_state`) and contains links to all other important artifacts generated during the lifecycle.
*   **Key Fields:**
    *   `project_id`: A unique identifier for the project.
    *   `current_state`: An enum representing the project's current phase (e.g., `CODING`, `TESTING`).
    *   `links`: An object containing URIs to other critical artifacts like the `code_gen_spec`, `qa_report`, etc.

### 2. `code_gen_spec.schema.json`

*   **Purpose:** This artifact is the primary **input** for the `CODING` state. It provides the `CODE_GENERATOR` agent with a detailed, four-layered context of what needs to be built.
*   **Key Fields:**
    *   `structured_specification` (L1): A reference to the high-level software architecture.
    *   `database_context` (L2): A reference to the database schema, defining business logic and data constraints.
    *   `task_context` (L3): The specific task details, including intent, scope, and acceptance criteria.
    *   `system_context` (L4): A query to the codebase's knowledge graph for understanding internal dependencies.

### 3. `test_plan.schema.json`

*   **Purpose:** This artifact is the primary **input** for the `TESTING` state. It defines the scope and nature of the tests that the `QA_VALIDATOR` agent needs to run.
*   **Key Fields:**
    *   `test_pyramid_config`: Defines the scope for unit, integration, and E2E tests.
    *   `deferred_tests_v1`: Explicitly lists test types (like "Load" or "Penetration" testing) that are out of scope for v1.0.
    *   `hitl_requirements`: Describes the criteria for manual Human-in-the-Loop usability and acceptance testing.

### 4. `qa_report.schema.json`

*   **Purpose:** This artifact is the primary **output** of the `TESTING` state. It serves as the critical "exit gate" that determines if a feature is ready for human approval before deployment.
*   **Key Fields:**
    *   `status`: The final result of the QA phase (e.g., `PASSED`, `FAILED`).
    *   `critical_path_pass_rate`: The success rate of tests covering the most important user flows.
    *   `blocker_bugs_open`: A count of open bugs that are severe enough to block a release.
    *   `sast_check_passed` / `sca_check_passed`: Boolean flags indicating if the code passed security scans.

### 5. `deploy_receipt.schema.json`

*   **Purpose:** This artifact is the primary **output** of the `DEPLOYMENT` state. It acts as the immutable "proof" that a specific version of the code was successfully deployed to production.
*   **Key Fields:**
    *   `status`: The final outcome of the deployment (e.g., `SUCCESS`, `ROLLED_BACK`).
    *   `artifact_version_deployed`: The specific version or commit SHA of the code that was deployed.
    *   `health_check_status`: The status of the application's health checks after deployment.
    *   `golden_signal_values`: Key performance metrics (like latency and error rate) measured during the post-deployment "soak time."

### 6. `bug_report.schema.json`

*   **Purpose:** This artifact is the primary **input** for the `MAINTENANCE` state. It provides a structured format for reporting a bug, which triggers the `BUG_TRIAGE` agent.
*   **Key Fields:**
    *   `severity`: The severity of the bug, from `P1_Critical` to `P5_Cosmetic`.
    *   `category`: The type of bug (e.g., `Security`, `Performance`, `UI`).
    *   `reproducible`: A boolean indicating if the bug can be consistently reproduced.
    *   `correlated_trace_id`: An optional ID that links the bug report to specific logs and traces for easier debugging.
