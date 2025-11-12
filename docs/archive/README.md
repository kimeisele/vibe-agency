# The Foundation of the Agency Operating System, v1.0

This document defines the four core concepts that form the foundation of the Agency Operating System (Agency OS). These meta-frameworks guide the architecture and implementation of a closed-loop, automated system for managing the entire software development lifecycle (SDLC).

---

### 1. The Hybrid SSoT (Single Source of Truth) Model: "The Truth"

The foundation of the Agency OS is a hybrid model for the Single Source of Truth, resolving the "Git vs. Manifest" debate by combining their strengths.

*   **Concept:** Git serves as the versioned **storage** (the immutable history), while a central `project_manifest.json` file acts as the declarative **state anchor** (the current status).

*   **Application:**
    *   **Git (The Store):** Every change to a project, its artifacts, or its status is a commit. This provides a robust, auditable history of who changed what, and when.
    *   **`project_manifest.json` (The State):** This file, versioned within Git, is the primary entry point for the OS. It declares the project's metadata, its current phase in the SDLC, and contains references (paths and commit SHAs) to all other versioned data artifacts. All automated frameworks read from and write to this manifest.

---

### 2. The "Artifact-First" Data Model: "The Glue"

The workflow is defined and connected by the data it produces, not by the agents that produce it. This artifact-centric philosophy ensures a modular, decoupled, and testable system.

*   **Concept:** Each stage of the SDLC is a pure function that transforms an input artifact into an output artifact: `Output_Artifact = Framework(Input_Artifact)`.

*   **Application:**
    *   **Data Contracts:** Standardized JSON Schemas define the structure of each artifact (e.g., `architecture.json`, `test_plan.json`). These schemas act as formal "data contracts" between the different frameworks.
    *   **Modularity:** Any agent or framework can be swapped out or upgraded as long as it adheres to the data contracts of its input and output artifacts. This prevents monolithic agent design and promotes independent development and testing of each component.

---

### 3. The Hybrid Orchestration Architecture: "The Conductor"

The three primary orchestration patterns (Human, Agent, Git) are not mutually exclusive alternatives but are assigned specific, complementary roles within a hybrid architecture.

*   **Concept:** The system is composed of a Trigger, an Executor, and a Validator.

*   **Application:**
    1.  **The Trigger (Git-based):** A GitOps controller or webhook acts as the reactive trigger. A `git push` that modifies a `project_manifest.json` initiates or continues a workflow.
    2.  **The Executor (Automated Agent):** A durable execution system (e.g., Temporal) acts as the stateful orchestrator. It executes the long-running SDLC workflow, managing state, retries, and pauses. It is explicitly designed to handle processes that can last for days, such as waiting for human approval.
    3.  **The Validator (Human-in-the-Loop):** The human is not the orchestrator but a blocking task type *within* the automated workflow. The Executor calls the human for high-stakes approvals (e.g., QA sign-off), pauses the workflow, and waits for an external signal to proceed.

---

### 4. The "Closed-Loop" Design: "The Feedback Loop"

The Agency OS operates in two primary modes: "Project Mode" (for new client work) and "Product Mode" (for maintenance and iteration). The system architecture must connect these two modes into a seamless, closed loop.

*   **Concept:** Feedback from the maintenance phase must be programmatically fed back into the planning phase.

*   **Application:**
    *   A `standardized_bug_report.json` artifact is generated during the maintenance phase.
    *   This artifact is semantically equivalent to a new feature request. Its structure mirrors the inputs required by the initial planning framework.
    *   By committing this bug report artifact to the project's repository, the GitOps Trigger automatically initiates a new `PLANNING` cycle. The VIBE/GENESIS framework consumes the bug report, generates a "patch" specification, and the entire SDLC process begins again to develop, test, and deploy the fix.
