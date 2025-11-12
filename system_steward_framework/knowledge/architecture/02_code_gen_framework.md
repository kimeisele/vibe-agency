
# 02_code_gen_framework.md

## Purpose

This document describes the `agency_os/02_code_gen_framework/`, which is responsible for the automated generation of source code based on a detailed technical specification. This framework is centered around a single specialist agent, the `CODE_GENERATOR`, which uses a rich knowledge base to translate architectural plans into functional, high-quality, and testable code.

---

## Components

### 1. `CODE_GENERATOR_v1.md` (The AI Engineer)

*   **Role:** This agent acts as a highly skilled AI Software Engineer. Its sole purpose is to take a `code_gen_spec.json` artifact (produced by the Planning Framework) and generate a complete "artifact bundle" containing source code, unit tests, and documentation.
*   **Process:**
    1.  **Analysis:** It first parses the input specification and validates it against its knowledge base to ensure the request is feasible and complete.
    2.  **Generation:** It generates the required code, adhering to the specified architecture, dependencies, and quality rules. This includes creating unit tests alongside the source code.
    3.  **Self-Correction:** It applies linting, formatting, and basic security checks to the code it has written, correcting issues as it finds them.
    4.  **Packaging:** It bundles all the generated files into a single, structured output artifact that is ready for the next phase (QA & Testing).
*   **Key Principle:** The agent does not orchestrate or manage state; it is a pure "translator" that converts a specification into code.

### 2. Knowledge Base

The `CODE_GENERATOR` relies on three critical knowledge files to govern its behavior and ensure the quality of its output:

*   **`CODE_GEN_dependencies.yaml` (The Manifest):** This file acts as an input/output manifest. It defines the four layers of context (`L1` to `L4`) that the agent requires to generate code, from the high-level architecture down to the codebase's knowledge graph. It also specifies the required outputs (source code, unit tests, documentation) that constitute a "complete" job.

*   **`CODE_GEN_constraints.yaml` (The Guardrails):** This file defines the "safe operating boundaries" for the agent. It lists:
    *   **Global Exclusions:** Technologies or domains (like cryptography or legacy mainframes) where autonomous generation is forbidden.
    *   **Hallucination Triggers:** Known patterns in input that lead to errors, such as ambiguous requirements or missing context.
    *   **Known Error Patterns:** A taxonomy of common AI-generated code flaws (e.g., missing corner-case error handling, API misuse) that the quality rules engine should check for.

*   **`CODE_GEN_quality_rules.yaml` (The Definition of Done):** This file defines the automated governance and quality standards. It specifies:
    *   **Quality Gates:** A series of automated checks that the generated code must pass, including functional correctness (unit tests pass), test coverage, maintainability (low complexity, no duplication), and security (no critical vulnerabilities).
    *   **Quality Profiles:** Specific, measurable thresholds for the quality gates. For example, the `v1.0_gate_profile` requires >70% test coverage and zero critical vulnerabilities to consider the code "Ready for QA".
