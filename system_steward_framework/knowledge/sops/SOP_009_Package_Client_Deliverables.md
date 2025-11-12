# SOP-009: Package Client Deliverables

**PURPOSE:** To package completed project artifacts for client delivery, generate delivery receipt, and optionally archive the workspace.

**PRE-CONDITION:**
- A workspace context is active (`$ACTIVE_WORKSPACE` is set and NOT ROOT)
- Project phase is `PRODUCTION` or later
- Required artifacts exist (planning, code, test, deployment)

**POST-CONDITION:**
1. A complete `DELIVERY_PACKAGE/` directory is created in the workspace
2. All artifacts are copied to the delivery package
3. Documentation files are generated (README, SETUP_GUIDE)
4. A `delivery_receipt.json` is created with package metadata
5. Package is exported via selected delivery method (repo, ZIP, PR)
6. Workspace is optionally archived in the registry

---

## STEPS (Executed by Steward):

### PHASE 1: PRE-FLIGHT VALIDATION

1. **(Steward) [Acknowledge]** State to user: "Acknowledged. We are initiating SOP_009_Package_Client_Deliverables for the current workspace."

2. **(Steward) [Validate Workspace Context]**
   - Check: Is `$ACTIVE_WORKSPACE` set?
   - IF NOT set OR == "ROOT":
     - State: "ERROR: SOP_009 requires an active client workspace context. You are currently in ROOT context."
     - State: "To package deliverables, first switch to a client workspace using SOP_008."
     - ABORT SOP execution.
   - IF set: Proceed to Step 3.

3. **(Steward) [Load Workspace Manifest]**
   - Load: `workspaces/{$ACTIVE_WORKSPACE}/project_manifest.json`
   - Extract:
     - `project_name`
     - `projectId`
     - `current_state` (project phase)
     - `owner` (client email)
     - `createdAt`
   - Announce:
     ```
     Preparing deliverables for:
     Workspace:  {$ACTIVE_WORKSPACE}
     Project:    {project_name}
     Owner:      {owner}
     Status:     {current_state}
     ```

4. **(Steward) [Validate Project Phase]**
   - Check: `current_state` must be one of: `PRODUCTION`, `MAINTENANCE`
   - IF NOT:
     - State: "WARNING: Project is in '{current_state}' phase. Deliverables are typically packaged after PRODUCTION."
     - Ask: "Do you want to proceed anyway? (YES/NO)"
     - IF NO: ABORT SOP execution.
     - IF YES: Proceed with warning logged.

5. **(Steward) [Validate Required Artifacts]**
   - Check for presence of the following artifact files:
     ```
     Required:
     - artifacts/planning/feature_spec.json OR architecture.json (at least one)
     - artifacts/code/ (must contain at least one code file or archive)

     Optional (check but don't block):
     - artifacts/test/qa_report.json
     - artifacts/deployment/deploy_receipt.json
     ```
   - IF required artifacts missing:
     - State: "ERROR: Required artifacts missing. Found: {list_found}. Missing: {list_missing}."
     - State: "Cannot package incomplete deliverables. Please complete the SDLC workflow first."
     - ABORT SOP execution.
   - IF optional artifacts missing:
     - State: "WARNING: Optional artifacts missing ({list_missing}). Deliverable package will be incomplete."
     - Ask: "Proceed anyway? (YES/NO)"
     - IF NO: ABORT.
     - IF YES: Continue with warning.

---

### PHASE 2: PACKAGE ASSEMBLY

6. **(Steward) [Create Delivery Package Directory]**
   - Announce: "Creating delivery package structure..."
   - Create directory: `workspaces/{$ACTIVE_WORKSPACE}/DELIVERY_PACKAGE/`
   - Create subdirectories:
     ```
     DELIVERY_PACKAGE/
     ├── artifacts/
     │   ├── planning/
     │   ├── code/
     │   ├── test/
     │   └── deployment/
     ├── documentation/
     └── metadata/
     ```

7. **(Steward) [Copy Artifacts]**
   - Announce: "Copying artifacts to delivery package..."
   - Copy the following with preserved structure:
     ```bash
     # Planning artifacts
     cp -r workspaces/{$ACTIVE_WORKSPACE}/artifacts/planning/* \
           workspaces/{$ACTIVE_WORKSPACE}/DELIVERY_PACKAGE/artifacts/planning/

     # Code artifacts
     cp -r workspaces/{$ACTIVE_WORKSPACE}/artifacts/code/* \
           workspaces/{$ACTIVE_WORKSPACE}/DELIVERY_PACKAGE/artifacts/code/

     # Test artifacts (if exist)
     cp -r workspaces/{$ACTIVE_WORKSPACE}/artifacts/test/* \
           workspaces/{$ACTIVE_WORKSPACE}/DELIVERY_PACKAGE/artifacts/test/

     # Deployment artifacts (if exist)
     cp -r workspaces/{$ACTIVE_WORKSPACE}/artifacts/deployment/* \
           workspaces/{$ACTIVE_WORKSPACE}/DELIVERY_PACKAGE/artifacts/deployment/
     ```
   - Announce: "Artifacts copied successfully."

8. **(Steward) [Generate Documentation]**
   - Announce: "Generating client documentation..."

   **8a. Create README.md:**
   ```markdown
   # {project_name} - Delivery Package

   **Delivered By:** Vibe Agency
   **Client:** {owner}
   **Delivery Date:** {current_date}
   **Project ID:** {projectId}
   **Workspace:** {$ACTIVE_WORKSPACE}

   ---

   ## Project Overview

   {description from manifest}

   ## Package Contents

   This delivery package contains:

   - ✅ **Planning Artifacts**: Feature specifications and architecture documents
   - ✅ **Source Code**: Complete application codebase (see `artifacts/code/`)
   - ✅ **Test Reports**: QA validation results (see `artifacts/test/`)
   - ✅ **Deployment Receipts**: Production deployment records (see `artifacts/deployment/`)

   ## Documentation

   - [Setup Guide](documentation/SETUP_GUIDE.md) - How to run and deploy the application
   - [API Documentation](documentation/API_DOCUMENTATION.md) - API endpoints and usage (if applicable)

   ## Project Metadata

   See `metadata/delivery_receipt.json` for complete delivery information.

   ---

   **For questions or support, contact:** agent@vibe.agency
   ```

   **8b. Create SETUP_GUIDE.md:**
   ```markdown
   # Setup Guide - {project_name}

   ## Prerequisites

   [Auto-detect from architecture.json or provide template]

   ## Installation

   [Extract from code artifacts or provide template]

   ## Running Locally

   [Extract from deploy_receipt.json or provide template]

   ## Deployment

   [Extract from deployment artifacts]

   ## Environment Variables

   See `.env.example` in the code directory for required environment variables.

   ---

   **For assistance, contact:** agent@vibe.agency
   ```

   **8c. Create API_DOCUMENTATION.md (if applicable):**
   - Check if `architecture.json` indicates a REST API or GraphQL API
   - IF YES: Generate API documentation template
   - IF NO: Skip this file

9. **(Steward) [Generate Delivery Receipt]**
   - Announce: "Generating delivery receipt..."
   - Create `DELIVERY_PACKAGE/metadata/delivery_receipt.json`:

     ```json
     {
       "deliveryId": "{$ACTIVE_WORKSPACE}-delivery-{timestamp}",
       "workspaceId": "{workspace_id from registry}",
       "projectId": "{projectId}",
       "projectName": "{project_name}",
       "deliveryDate": "{current_timestamp_iso8601}",
       "deliveredBy": "agent@vibe.agency",
       "deliveredTo": "{owner}",
       "deliveryMethod": "PENDING_SELECTION",
       "artifactsIncluded": [
         "feature_spec.json",
         "architecture.json",
         "source_code (see artifacts/code/)",
         "qa_report.json (if available)",
         "deploy_receipt.json (if available)"
       ],
       "projectStatus": "{current_state}",
       "packageVersion": "1.0.0",
       "maintenanceSupport": "6 months included (default)",
       "deliveryNotes": "Complete project deliverables as of {current_date}.",
       "accessInstructions": "TO_BE_UPDATED_AFTER_EXPORT"
     }
     ```

10. **(Steward) [Generate Package Inventory]**
    - Create `.delivery_manifest.yaml`:

      ```yaml
      version: "1.0.0"
      package_id: "{deliveryId}"
      created_at: "{current_timestamp}"
      workspace: "{$ACTIVE_WORKSPACE}"

      contents:
        artifacts:
          - path: "artifacts/planning/feature_spec.json"
            size: "{file_size}"
            checksum: "{sha256_hash}"
          - path: "artifacts/code/src.zip"
            size: "{file_size}"
            checksum: "{sha256_hash}"
          # ... (auto-generate for all files)

        documentation:
          - "documentation/README.md"
          - "documentation/SETUP_GUIDE.md"

      total_files: {count}
      total_size_bytes: {sum}
      ```

---

### PHASE 3: DELIVERY METHOD SELECTION

11. **(Steward) [Prompt for Delivery Method]**
    - Announce: "Delivery package assembled. Please select delivery method:"
    - Display options:
      ```
      DELIVERY METHOD OPTIONS:
      [1] GitHub Repository Export (create new private repo)
      [2] ZIP Archive (for secure file transfer)
      [3] Pull Request to Client Repo (requires client repo URL)
      [4] Local Package Only (no export, keep in workspace)

      Enter selection (1-4):
      ```

12. **(Steward) [Execute Selected Delivery Method]**

    **Option 1: GitHub Repository Export**
    ```bash
    # Step 12a: Create new repo
    cd workspaces/{$ACTIVE_WORKSPACE}/DELIVERY_PACKAGE
    gh repo create {$ACTIVE_WORKSPACE}_deliverables --private --source=. --remote=origin

    # Step 12b: Initialize git and push
    git init
    git add .
    git commit -m "Initial delivery package for {project_name}"
    git branch -M main
    git push -u origin main

    # Step 12c: Invite client as collaborator
    gh repo add-collaborator {$ACTIVE_WORKSPACE}_deliverables {owner_github_username}

    # Update delivery_receipt.json:
    "deliveryMethod": "github_repo_export"
    "accessInstructions": "https://github.com/vibe-agency/{$ACTIVE_WORKSPACE}_deliverables"
    ```

    **Option 2: ZIP Archive**
    ```bash
    # Step 12a: Create timestamped ZIP
    cd workspaces/{$ACTIVE_WORKSPACE}
    zip -r DELIVERY_PACKAGE_$(date +%Y%m%d_%H%M%S).zip DELIVERY_PACKAGE/

    # Step 12b: Announce location
    State: "ZIP archive created at: workspaces/{$ACTIVE_WORKSPACE}/DELIVERY_PACKAGE_{timestamp}.zip"
    State: "Upload to secure transfer service (Dropbox, Google Drive, etc.) and share link with client."

    # Update delivery_receipt.json:
    "deliveryMethod": "zip_archive"
    "accessInstructions": "ZIP file location: workspaces/{$ACTIVE_WORKSPACE}/DELIVERY_PACKAGE_{timestamp}.zip"
    ```

    **Option 3: Pull Request to Client Repo**
    ```bash
    # Step 12a: Prompt for client repo URL
    Ask: "Please provide the client's GitHub repository URL:"

    # Step 12b: Add remote and push
    cd workspaces/{$ACTIVE_WORKSPACE}/DELIVERY_PACKAGE
    git init
    git add .
    git commit -m "Vibe Agency delivery: {project_name}"
    git remote add client_repo {client_repo_url}
    git checkout -b vibe_agency_delivery_{timestamp}
    git push client_repo vibe_agency_delivery_{timestamp}

    # Step 12c: Create PR
    gh pr create --repo {client_repo} \
                 --title "Project Delivery: {project_name}" \
                 --body "Complete deliverables from Vibe Agency. See README.md for details."

    # Update delivery_receipt.json:
    "deliveryMethod": "pull_request"
    "accessInstructions": "Pull request created at {client_repo}/pulls"
    ```

    **Option 4: Local Package Only**
    ```bash
    # No export action
    State: "Delivery package created locally at: workspaces/{$ACTIVE_WORKSPACE}/DELIVERY_PACKAGE/"
    State: "Manual delivery required. Package contents ready for transfer."

    # Update delivery_receipt.json:
    "deliveryMethod": "local_package_only"
    "accessInstructions": "Local directory: workspaces/{$ACTIVE_WORKSPACE}/DELIVERY_PACKAGE/"
    ```

---

### PHASE 4: FINALIZATION

13. **(Steward) [Update Delivery Receipt]**
    - Update `delivery_receipt.json` with selected delivery method and access instructions
    - Save final version to `DELIVERY_PACKAGE/metadata/delivery_receipt.json`

14. **(Steward) [Prompt for Workspace Archival]**
    - Ask: "Do you want to archive this workspace now? (YES/NO)"
    - Explain: "Archiving moves the workspace from 'active' to 'archived' in the registry. The workspace files remain intact but will not appear in active workspace lists."
    - IF NO: Skip to Step 16.
    - IF YES: Proceed to Step 15.

15. **(Steward) [Archive Workspace]**
    - Announce: "Archiving workspace..."
    - Read `workspaces/.workspace_index.yaml`
    - Find workspace entry for `{$ACTIVE_WORKSPACE}`
    - Move entry from `workspaces:` array to `archived:` array
    - Add archival metadata:
      ```yaml
      archived:
        - id: "{workspace_id}"
          name: "{$ACTIVE_WORKSPACE}"
          type: "{workspace_type}"
          archivedAt: "{current_timestamp}"
          archivedReason: "Project delivered via SOP_009"
          deliveryReceiptPath: "workspaces/{$ACTIVE_WORKSPACE}/DELIVERY_PACKAGE/metadata/delivery_receipt.json"
          originalCreatedAt: "{createdAt}"
          metadata:
            owner: "{owner}"
            tags: ["archived", "{workspace_type}"]
      ```
    - Update `metadata.totalWorkspaces` (decrement by 1)
    - Save updated registry
    - Announce: "Workspace archived successfully."

16. **(Steward) [Final Summary]**
    - Announce: "SOP_009 complete. Client deliverables packaged and exported."
    - Display summary:

      ```
      ✅ DELIVERY PACKAGE CREATED

      Workspace:         {$ACTIVE_WORKSPACE}
      Project:           {project_name}
      Delivery ID:       {deliveryId}
      Delivery Method:   {deliveryMethod}
      Access:            {accessInstructions}

      PACKAGE CONTENTS:
      - Planning artifacts: {count}
      - Code artifacts: {count}
      - Test reports: {count}
      - Deployment receipts: {count}
      - Documentation files: 3

      WORKSPACE STATUS:
      - Archived: {YES/NO}
      - Registry status: {active/archived}

      CLIENT NEXT STEPS:
      1. Access deliverables at: {accessInstructions}
      2. Review README.md for project overview
      3. Follow SETUP_GUIDE.md for deployment
      4. Contact agent@vibe.agency for support
      ```

17. **(Steward) [Context Reset Recommendation]**
    - IF workspace was archived:
      - State: "RECOMMENDATION: This workspace has been archived. To continue working on other projects, switch workspace context using SOP_008."
      - State: "To return to ROOT context: 'Switch to ROOT'"

---

## ANTI-SLOP ENFORCEMENT

- **MUST NOT** package deliverables from ROOT context (client-specific operation only)
- **MUST NOT** proceed if required artifacts are missing
- **MUST** validate project phase (warn if not PRODUCTION)
- **MUST** generate delivery_receipt.json with complete metadata
- **MUST** update registry if workspace is archived

---

## ERROR HANDLING

**Error 1: No Active Workspace**
- Message: "ERROR: SOP_009 requires an active client workspace. Current context: ROOT."
- Resolution: Run SOP_008 to switch to target client workspace first.

**Error 2: Missing Required Artifacts**
- Message: "ERROR: Required artifacts missing: {list}. Cannot package incomplete deliverables."
- Resolution: Complete SDLC workflow to generate missing artifacts OR override with explicit approval.

**Error 3: Delivery Method Execution Failure**
- Message: "ERROR: Failed to execute delivery method '{method}'. Error: {error_details}"
- Resolution: Retry with different method OR export locally (Option 4) and deliver manually.

**Error 4: Workspace Already Archived**
- Message: "WARNING: This workspace is already archived. Deliverables may be outdated."
- Resolution: Un-archive workspace if needed (future SOP) OR proceed with warning.

---

## GOVERNANCE CHECKPOINTS

**HITL Required:** YES (for delivery method selection)

**HITL Recommended:** YES (for archival decision)

**Audit Trail:**
- Log delivery package creation:
  ```
  [2025-11-12 15:00:00] SOP_009 | PACKAGED | workspace: acme_corp | method: github_repo_export | user: agent@vibe.agency
  ```

---

## RELATED SOPS

- **SOP_008:** Switch Workspace (required before SOP_009)
- **SOP_007:** Create Client Workspace (initial onboarding)
- **SOP_001-006:** Project execution SOPs (generate artifacts for delivery)

---

## MAINTENANCE PERIOD SUPPORT

**Post-Delivery Support:**

If client contract includes maintenance period:

1. **DO NOT archive workspace** immediately
2. Leave workspace in `active` status
3. Set project phase to `MAINTENANCE`
4. Continue using workspace for bug fixes (SOP_002)
5. Archive workspace only after maintenance period expires

**Example Flow:**
```bash
# Delivery with maintenance support:
run_sop('SOP_009', delivery_method='github_repo_export', archive=False)

# 6 months later (maintenance period complete):
run_sop('SOP_009', archive_only=True)  # Archive without re-packaging
```

---

**SOP_009 Definition Complete.**
