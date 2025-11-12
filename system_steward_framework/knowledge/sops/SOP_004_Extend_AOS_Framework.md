
# SOP-004: Extend AOS Framework (Governance)

**PURPOSE:** To guide a developer through the architectural requirements for adding a new specialist framework (e.g., '06_xx_framework') to the 'agency_os', ensuring modular integrity.

**PRE-CONDITION:** User indicates intent to "add a new framework" or "extend the AOS".

**POST-CONDITION:** Developer is provided with a validated checklist, ensuring their plan conforms to AOS architecture before implementation begins.

---

## STEPS (Executed by Steward):

1.  **(Steward) [Acknowledge]** State: "Acknowledged. SOP_004 initiated. Extending the `agency_os` is a critical operation that must adhere to its core modular design."
2.  **(Steward) [Present Principles]** State: "The AOS architecture is based on 'Modular Extensibility'.27 Any new framework must be 'highly cohesive' (does one thing well), 'loosely coupled' (communicates only via artifacts), and expose 'standardized interfaces' (data contracts).25"
3.  **(Steward) [Checklist - Interface]** Ask: "Please define the 'Provided Interface' of your new framework. What new artifacts will it produce?"
4.  **(Steward) [Checklist - Interface]** Ask: "Please define the 'Required Interface'. What existing artifacts (e.g., `architecture.v1.json`, `qa_report.json`) will it consume?"
5.  **(Steward) [Checklist - Contract]** State: "You MUST define all new artifacts in the central `agency_os/00_system/contracts/ORCHESTRATION_data_contracts.yaml`. Have you done this?"
6.  **(Steward) Ask:** "Please define the 'Single Responsibility' of this new framework. What is the one SDLC phase it manages?" (Ref: 1)
7.  **(Steward) State:** "You MUST update the `agency_os/00_system/state_machine/ORCHESTRATION_workflow_design.yaml`. Please define the new STATE (e.g., 'ANALYTICS'), the TRANSITIONS leading into it, and the TRANSITIONS leading out of it."
8.  **(Steward) State:** "Your new framework MUST follow the standard directory structure: `06_xx_framework/prompts/` and `06_xx_framework/knowledge/`."
9.  **(Steward) [Validate]** (Steward reviews the user's answers against the checklist).
10. **(Steward) State:** "Your extension plan has been validated against SOP_004. You may proceed with implementation. Ensure all new components are registered with the `AGENCY_OS_ORCHESTRATOR_v1`."
