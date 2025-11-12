# SOP-007: Create Client Workspace

**PURPOSE:** To onboard a new client by creating an isolated workspace with proper directory structure, manifest, and registry entry.

**PRE-CONDITION:** User has indicated intent to onboard a new client or create a workspace.

**POST-CONDITION:**
1. A new workspace directory is created at `workspaces/client_name/`
2. A validated `project_manifest.json` is initialized for the client
3. The workspace is registered in `workspaces/.workspace_index.yaml`
4. Required artifact directories are created
5. Optional documentation files are initialized

---

## STEPS (Executed by Steward):

1. **(Steward) [Acknowledge]** State to user: "Acknowledged. We are initiating SOP_007_Create_Client_Workspace to onboard a new client."

2. **(Steward) [Collect Required Information]** Ask the user for the following inputs:
   - **Client Name**: "Please provide the client identifier in snake_case (e.g., 'acme_corp', 'globex_inc'):"
     - Validate: Must match pattern `^[a-z][a-z0-9_]*$` (lowercase, underscores only)
   - **Project Name**: "Please provide a human-readable project name (e.g., 'Booking Tool for Acme'):"
   - **Project Description**: "Please provide a brief project description (1-2 sentences):"
   - **Owner Email**: "Please provide the client contact email:"
   - **Workspace Type**: "Is this an 'internal' or 'external' client workspace?"
     - Validate: Must be either "internal" or "external"

3. **(Steward) [Validate Workspace Does Not Exist]**
   - Check: Does `workspaces/{client_name}/` already exist?
   - IF YES:
     - State: "ERROR: Workspace '{client_name}' already exists. Please choose a different client identifier or use SOP_008 to switch to the existing workspace."
     - ABORT SOP execution.
   - IF NO: Proceed to Step 4.

4. **(Steward) [Create Directory Structure]**
   - Announce: "Creating workspace directory structure for '{client_name}'..."
   - Create the following directories:
     ```
     workspaces/{client_name}/
     ├── artifacts/
     │   ├── planning/
     │   ├── code/
     │   ├── test/
     │   └── deployment/
     ```
   - Announce: "Directory structure created."

5. **(Steward) [Initialize Project Manifest]**
   - Announce: "Initializing project manifest..."
   - Generate a new UUID for `projectId` (use: `uuidgen` or `python -c "import uuid; print(uuid.uuid4())"`)
   - Create `workspaces/{client_name}/project_manifest.json` with the following structure:

     ```json
     {
       "apiVersion": "agency.os/v1alpha1",
       "kind": "Project",
       "metadata": {
         "projectId": "{generated_uuid}",
         "name": "{project_name}",
         "description": "{project_description}",
         "owner": "{owner_email}",
         "createdAt": "{current_timestamp_iso8601}",
         "lastUpdatedAt": "{current_timestamp_iso8601}"
       },
       "spec": {
         "vibe": {},
         "genesis": {}
       },
       "status": {
         "projectPhase": "INITIALIZING",
         "lastUpdate": "{current_timestamp_iso8601}",
         "message": "Workspace created via SOP_007. Ready for project planning."
       },
       "artifacts": {
         "planning": {},
         "code": {},
         "test": {},
         "deployment": {}
       }
     }
     ```
   - Announce: "Project manifest initialized at `workspaces/{client_name}/project_manifest.json`."

6. **(Steward) [Validate Manifest Against Data Contract]**
   - Announce: "Validating manifest structure..."
   - Validate the generated manifest against `agency_os/00_system/contracts/ORCHESTRATION_data_contracts.yaml`.
   - Required fields check:
     - `metadata.projectId` (UUID format)
     - `metadata.name` (non-empty string)
     - `metadata.owner` (valid email format)
     - `status.projectPhase` (must be valid enum value)
   - IF validation fails:
     - State: "ERROR: Generated manifest does not conform to data contract. Aborting workspace creation."
     - ABORT and clean up created directories.
   - IF validation passes: Proceed to Step 7.

7. **(Steward) [Register Workspace]**
   - Announce: "Registering workspace in `.workspace_index.yaml`..."
   - Generate a unique workspace ID:
     - Pattern: `{client_name}-001`
     - If `{client_name}-001` already exists in registry, increment counter to `-002`, `-003`, etc.
   - Append the following entry to `workspaces/.workspace_index.yaml` under the `workspaces:` array:

     ```yaml
     - id: "{workspace_id}"
       name: "{client_name}"
       type: "{workspace_type}"
       description: "{project_description}"
       manifestPath: "workspaces/{client_name}/project_manifest.json"
       status: "active"
       createdAt: "{current_date_yyyy_mm_dd}"
       lastUpdated: "{current_date_yyyy_mm_dd}"
       metadata:
         owner: "{owner_email}"
         tags: ["{workspace_type}"]
     ```

   - Update `metadata.totalWorkspaces` in `.workspace_index.yaml` (increment by 1)
   - Update `metadata.lastUpdated` to current date
   - Announce: "Workspace registered successfully."

8. **(Steward) [Create Optional Documentation Files]**
   - Announce: "Creating optional documentation files..."
   - Create `workspaces/{client_name}/README.md`:

     ```markdown
     # {project_name}

     **Client:** {client_name}
     **Owner:** {owner_email}
     **Created:** {current_date}

     ## Project Description
     {project_description}

     ## Status
     - **Phase:** INITIALIZING
     - **Last Updated:** {current_timestamp}

     ## Workspace Structure
     - `project_manifest.json` - Project SSoT
     - `artifacts/` - Generated artifacts (planning, code, test, deployment)

     ## Next Steps
     1. Switch to this workspace: Use SOP_008
     2. Start project planning: Use SOP_001 (Start New Project)
     ```

   - Create `workspaces/{client_name}/.env.example` (if applicable):

     ```bash
     # Environment variables for {project_name}
     # Copy this file to .env and fill in values

     # Example:
     # DATABASE_URL=postgresql://localhost/db_name
     # API_KEY=your_api_key_here
     ```

   - Announce: "Documentation files created."

9. **(Steward) [Final Summary]**
   - Announce: "SOP_007 complete. Client workspace created successfully."
   - Present the following summary:

     ```
     ✅ Workspace Created: workspaces/{client_name}/
     ✅ Project Manifest: workspaces/{client_name}/project_manifest.json
     ✅ Workspace ID: {workspace_id}
     ✅ Registry Entry: Added to workspaces/.workspace_index.yaml
     ✅ Status: ACTIVE
     ✅ Project Phase: INITIALIZING

     NEXT STEPS:
     1. Switch to this workspace using SOP_008:
        "Switch to workspace {client_name}"

     2. Start project planning using SOP_001:
        "Start new project"
     ```

10. **(Steward) [Context Reminder]**
    - State: "NOTE: You are still operating in the ROOT context. To work on this client project, use SOP_008 to switch workspace context."

---

## ANTI-SLOP ENFORCEMENT

- **MUST NOT** create workspace if `client_name` already exists
- **MUST NOT** proceed if manifest validation fails
- **MUST NOT** skip registry update (would break workspace discovery)
- **MUST** generate valid UUID for `projectId`
- **MUST** use exact directory structure as defined in `workspaces/.workspace_index.yaml:58-74`

---

## ERROR HANDLING

**Error 1: Workspace Already Exists**
- Message: "ERROR: Workspace '{client_name}' already exists at `workspaces/{client_name}/`."
- Resolution: User must choose different `client_name` OR use SOP_008 to switch to existing workspace.

**Error 2: Invalid Client Name Format**
- Message: "ERROR: Client name '{client_name}' does not match required pattern (snake_case, lowercase only)."
- Resolution: User must provide valid identifier (e.g., 'acme_corp', not 'Acme Corp' or 'acme-corp')

**Error 3: Manifest Validation Failure**
- Message: "ERROR: Generated manifest failed validation against data contract."
- Resolution: Steward must check ORCHESTRATION_data_contracts.yaml and retry with corrected structure.

**Error 4: Registry Update Failure**
- Message: "ERROR: Failed to update `.workspace_index.yaml`. Workspace created but not registered."
- Resolution: Manual fix required - either complete registry update OR delete workspace directory.

---

## GOVERNANCE CHECKPOINTS

**HITL Required:** NO (workspace creation is automated once inputs collected)

**HITL Recommended:** YES (for external clients)
- Recommendation: For `workspace_type: "external"`, require human approval before workspace creation.
- Approval Gate: "This is an external client workspace. Do you approve creation? (YES/NO)"
- If NO: Abort SOP execution.

**Audit Trail:**
- Log workspace creation to `system_steward_framework/logs/workspace_operations.log`:
  ```
  [2025-11-12 10:30:15] SOP_007 | CREATED | workspace_id: acme-corp-001 | user: agent@vibe.agency
  ```

---

## RELATED SOPS

- **SOP_008:** Switch Workspace Context (use after creating workspace)
- **SOP_001:** Start New Project (use after switching to new workspace)
- **SOP_009:** Package Client Deliverables (use when project complete)

---

**SOP_007 Definition Complete.**
