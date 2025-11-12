
# 04_deploy_framework.md

## Purpose

This document describes the `agency_os/04_deploy_framework/`, which is responsible for the safe, reliable, and traceable deployment of validated code to production environments. This framework is centered around a single specialist agent, the `DEPLOY_MANAGER`, which acts as an automated DevOps Engineer, executing the deployment process according to a strict set of rules.

---

## Components

### 1. `DEPLOY_MANAGER_v1.md` (The AI DevOps Engineer)

*   **Role:** This agent acts as a highly responsible AI DevOps Engineer. Its sole purpose is to take a `qa_report.json` that has been explicitly marked as `APPROVED` by a human and deploy the corresponding code artifact to the target environment.
*   **Process:**
    1.  **Pre-Flight Checks:** It first validates that the QA report is indeed approved and that all deployment dependencies (e.g., cloud provider access, CI/CD tools) are ready.
    2.  **Deployment Execution:** It follows a strict sequence of operations: backing up the database, running database migrations, and then performing a "Rolling Update" of the application.
    3.  **Post-Deployment Validation:** After the application is deployed, it performs a "soak time" where it monitors the system's "Golden Signals" (latency, traffic, errors, saturation) to ensure the new version is stable.
    4.  **Reporting:** It generates a final `deploy_receipt.json` artifact that serves as a permanent record of the deployment's outcome (success or failure).
*   **Key Principle:** The agent's primary directive is safety. It is designed to fail fast and automatically roll back if any of its quality rules are breached during or after the deployment.

### 2. Knowledge Base

The `DEPLOY_MANAGER` relies on three critical knowledge files to ensure safe and reliable deployments:

*   **`DEPLOY_dependencies.yaml` (The Deployment Plan):** This file defines the mandatory sequence of events for any deployment. It specifies:
    *   **The QA Handoff:** A deployment can *only* be triggered by a manual, human approval of a QA report.
    *   **The Critical Path:** The exact order of operations (Backup -> Migrate DB -> Rollout App -> Monitor) that must be followed to prevent outages.
    *   **Rollback Prerequisites:** The requirements for a safe rollback, such as maintaining an immutable artifact registry and designing database migrations to be backward-compatible.
    *   **Observability Prerequisites:** The monitoring capabilities (Golden Signals, centralized logging) that must be in place *before* a deployment can even start.

*   **`DEPLOY_constraints.yaml` (The Environment Rules):** This file defines the hard limits and non-negotiable rules of the production environment. It specifies:
    *   **Deployment Strategy:** For v1.0, only "RollingUpdate" is permitted for production to ensure zero-downtime.
    *   **Infrastructure Ceiling:** For v1.0, only managed platforms (like Google Cloud Run or AWS Fargate) are allowed, explicitly forbidding the complexity of self-managed Kubernetes.
    *   **Automation Boundaries:** It defines what must be automated (e.g., SSL certificates) and what must be a manual gate (e.g., the final QA sign-off).

*   **`DEPLOY_quality_rules.yaml` (The Success/Failure Criteria):** This file provides the measurable, real-time rules that determine if a deployment is successful. It defines:
    *   **Definition of Done:** A 7-point checklist that must be fully completed for a deployment to be marked as "Done." This goes beyond just copying code and includes health checks and monitoring.
    *   **Health Checks:** The specific `liveness` and `readiness` probes the application must expose.
    *   **Automated Rollback Triggers:** The precise conditions that will trigger an automatic rollback to the previous stable version. This includes synchronous failures (like a failed health check) and asynchronous failures (like a spike in the error rate during the "soak time").
