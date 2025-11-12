
# 03_qa_framework.md

## Purpose

This document describes the `agency_os/03_qa_framework/`, which is responsible for the automated validation of code quality, correctness, and adherence to project standards. This framework is centered around a single specialist agent, the `QA_VALIDATOR`, which acts as an impartial judge, executing a battery of tests and producing a definitive quality report.

---

## Components

### 1. `QA_VALIDATOR_v1.md` (The AI QA Engineer)

*   **Role:** This agent acts as a meticulous AI Quality Assurance Engineer. Its sole purpose is to take a code `artifact_bundle` (from the `CODE_GENERATOR`) and a `test_plan.json`, execute a comprehensive validation process, and produce a `qa_report.json` that determines if the code is "Ready for Human Approval."
*   **Process:**
    1.  **Setup:** It first unpacks the code into a clean, isolated testing environment.
    2.  **Test Execution:** It runs the full suite of automated tests provided in the bundle, including unit and integration tests.
    3.  **Static Analysis:** It performs static analysis for security vulnerabilities (SAST), vulnerable dependencies (SCA), and general code quality (linting, complexity).
    4.  **Evaluation:** It compares the results of all checks against the quality gates and rules defined in its knowledge base.
    5.  **Reporting:** It generates a final `qa_report.json` with a clear `PASSED` or `FAILED` status, which serves as the input for the next workflow state (`AWAITING_QA_APPROVAL`).
*   **Key Principle:** The agent is an impartial validator. It does not fix code or make subjective judgments; it only executes tests and compares the results against pre-defined rules.

### 2. Knowledge Base

The `QA_VALIDATOR` relies on three critical knowledge files to govern its validation process:

*   **`QA_dependencies.yaml` (The Test Plan):** This file defines the structure and sequence of the entire validation process. It maps out:
    *   **The Test Pyramid:** The dependencies for each level of testing (Unit, Integration, E2E), specifying what environment and data each level requires.
    *   **The CI/CD Pipeline:** The "Fail-Fast" sequence of testing stages, from fast pre-commit checks to full E2E suites in staging.
    *   **The Testability Contract:** A set of requirements that the `CODE_GENERATOR` *must* fulfill to make its code testable, such as generating stable `data-testid` attributes for all UI elements.

*   **`QA_constraints.yaml` (The Boundaries):** This file defines what the QA framework *does not* do. It explicitly lists:
    *   **Non-Automatable Areas:** Subjective aspects like user experience (UX) or aesthetics that require mandatory Human-in-the-Loop (HITL) testing.
    *   **Deferred Tests:** High-effort tests like Load Testing and Penetration Testing that are explicitly excluded from the v1.0 scope.
    *   **Mandatory Security Tests:** It clarifies that while some tests are deferred, SAST and SCA are non-negotiable and must be run.

*   **`QA_quality_rules.yaml` (The Definition of Done):** This file quantifies "quality" into a set of measurable business rules. It defines:
    *   **Coverage Strategy:** The specific code coverage targets (e.g., "90% coverage on all new code").
    *   **Test Prioritization:** A risk-based model that categorizes tests from P0 ("Test First") to P3 ("Test Last") to ensure the most critical paths are always validated.
    *   **Release Criteria:** The formal, binary checklist that must be met for a release to be considered "QA Approved" (e.g., `blocker_bugs_open == 0`).
    *   **Flaky Test Policy:** A systematic process for detecting, quarantining, and fixing unstable tests to maintain trust in the CI/CD pipeline.
