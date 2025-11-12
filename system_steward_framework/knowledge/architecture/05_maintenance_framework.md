
# 05_maintenance_framework.md

## Purpose

This document describes the `agency_os/05_maintenance_framework/`, which is responsible for the systematic analysis, classification, and remediation of bugs, alerts, and other production issues. This framework is centered around a single specialist agent, the `BUG_TRIAGE`, which acts as an AI Maintenance Engineer to ensure that issues are handled according to their severity and impact.

---

## Components

### 1. `BUG_TRIAGE_v1.md` (The AI Maintenance Engineer)

*   **Role:** This agent acts as a highly analytical AI Maintenance Engineer. Its sole purpose is to take a `bug_report.json` artifact, analyze it, and determine the correct remediation path.
*   **Process:**
    1.  **Analysis & Classification:** It first parses the bug report and uses its knowledge base to classify the bug's severity (from P1_Critical to P5_Cosmetic) and category (e.g., Security, Performance).
    2.  **Path Determination:** Based on the classification, it decides whether the issue requires an immediate "Hotfix" or can be handled as a "Regular Fix" in the standard development cycle.
    3.  **Output Generation:**
        *   If a **Hotfix** is required, it generates a new, minimal `code_gen_spec.json` that contains only the information needed to fix that specific bug.
        *   If it's a **Regular Fix**, it signals the orchestrator to add the bug report to the project's planning backlog.
*   **Key Principle:** The agent's primary function is to act as a decision engine, preventing low-priority issues from disrupting the development flow while ensuring critical issues are addressed immediately.

### 2. Knowledge Base

The `BUG_TRIAGE` agent relies on three critical knowledge files to make its decisions:

*   **`MAINTENANCE_dependencies.yaml` (The Process Map):** This file defines the two distinct workflows for fixing bugs:
    *   **Hotfix Workflow:** Triggered by P1_Critical bugs, this path branches directly from `main`, uses an accelerated testing protocol, and merges back into both `main` (for immediate deployment) and `develop` (to prevent regressions).
    *   **Regular Fix Workflow:** For all other bugs (P2-P5), this path follows the standard development process, branching from `develop` and going through the full QA and release cycle.
    *   It also defines the dependency on the Agile planning loop, ensuring that all non-critical work is properly prioritized against new features.

*   **`MAINTENANCE_constraints.yaml` (The Rulebook):** This file defines the hard rules and boundaries of the maintenance process. It specifies:
    *   **Bug Severity Levels:** A clear, unambiguous taxonomy for classifying bugs from P1_Critical (system down) to P5_Cosmetic (visual tweak).
    *   **Non-Automatable Bug Classes:** It explicitly forbids the AI from attempting to automatically fix certain high-risk issues, such as those requiring database schema changes or complex architectural refactoring.
    *   **Mandatory HITL Triggers:** A list of conditions that *must* halt the automated process and escalate to a human for review, such as security-related bugs, issues involving PII data, or fixes that have a large "blast radius" (affecting many files).

*   **`MAINTENANCE_triage_rules.yaml` (The Decision Engine):** This file contains the specific, measurable rules for prioritizing and handling bugs. It defines:
    *   **Prioritization Matrix:** A matrix that combines technical `Severity` and business `Impact` to produce a final priority score (P1-P5). This is the core heuristic for the initial triage.
    *   **RICE Scoring:** A quantitative model (`Reach * Impact * Confidence / Effort`) used for comparing and prioritizing P2-P5 bugs against each other in the backlog.
    *   **Definition of Done:** A formal checklist that must be completed for any bug fix to be considered "Done," including the mandatory creation of a new regression test.
    *   **SLAs and Escalation:** Defines the target response/resolution times for each priority level and the rules for automatically escalating an issue if those SLAs are breached.
