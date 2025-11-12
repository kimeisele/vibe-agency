# SOP-008: Switch Workspace Context

**PURPOSE:** To change the active workspace context, redirecting all subsequent SSF operations to a specific client workspace or back to ROOT.

**PRE-CONDITION:** User indicates intent to switch workspace context.

**POST-CONDITION:**
1. Environment variable `$ACTIVE_WORKSPACE` is set to the target workspace name (or unset for ROOT)
2. All subsequent SOP executions operate on the selected workspace's `project_manifest.json`
3. Artifact paths are resolved relative to the active workspace

---

## STEPS (Executed by Steward):

1. **(Steward) [Acknowledge]** State to user: "Acknowledged. We are initiating SOP_008_Switch_Workspace to change the active workspace context."

2. **(Steward) [Show Current Context]**
   - Read current value of `$ACTIVE_WORKSPACE` environment variable
   - IF set:
     - State: "Current workspace context: **{$ACTIVE_WORKSPACE}**"
   - IF not set (or empty):
     - State: "Current workspace context: **ROOT** (monorepo root)"

3. **(Steward) [List Available Workspaces]**
   - Announce: "Loading workspace registry..."
   - Read `workspaces/.workspace_index.yaml`
   - Display active workspaces in a formatted list:

     ```
     AVAILABLE WORKSPACES:
     ---------------------
     [ROOT]       Monorepo root (vibe-agency)
     [1]  acme_corp        - Booking Tool for Acme (external, active)
     [2]  globex_inc       - CRM System (external, active)
     [3]  vibe_internal    - Internal Vibe Agency projects (internal, active)

     ARCHIVED WORKSPACES: 2 (use SOP_009 to view details)
     ```

4. **(Steward) [Prompt for Target Workspace]**
   - Ask: "Please specify the workspace to switch to:"
     - Options:
       - Enter workspace name (e.g., "acme_corp")
       - Enter number from list (e.g., "1")
       - Enter "ROOT" or "0" to return to monorepo root
       - Enter "CANCEL" to abort

5. **(Steward) [Validate Target Workspace]**
   - IF user input == "ROOT" OR "0":
     - Set target = "ROOT"
     - Proceed to Step 6.
   - IF user input == "CANCEL":
     - State: "Workspace switch cancelled. Remaining in current context."
     - ABORT SOP execution.
   - IF user input is a number (1, 2, 3, etc.):
     - Map number to workspace name from list in Step 3
     - Set target = workspace_name
   - IF user input is a workspace name:
     - Set target = user input
   - Validate:
     - Check if `target` exists in `workspaces/.workspace_index.yaml` (active workspaces)
     - Check if `workspaces/{target}/project_manifest.json` exists
   - IF validation fails:
     - State: "ERROR: Workspace '{target}' not found or is archived. Please choose from the active workspaces list."
     - Retry from Step 4 (max 3 attempts, then abort)
   - IF validation passes: Proceed to Step 6.

6. **(Steward) [Confirm Switch]**
   - IF target == "ROOT":
     - State: "You are about to switch workspace context to: **ROOT** (monorepo root)"
   - ELSE:
     - Load target manifest: `workspaces/{target}/project_manifest.json`
     - Extract: `project_name`, `current_state`, `owner`
     - State:
       ```
       You are about to switch workspace context to:

       Workspace:    {target}
       Project:      {project_name}
       Owner:        {owner}
       Status:       {current_state}
       Manifest:     workspaces/{target}/project_manifest.json
       ```
   - Ask: "Confirm workspace switch? (YES/NO)"
   - IF NO: ABORT SOP execution, state "Workspace switch cancelled."
   - IF YES: Proceed to Step 7.

7. **(Steward) [Execute Context Switch]**
   - IF target == "ROOT":
     - Unset environment variable: `unset ACTIVE_WORKSPACE`
     - Announce: "Workspace context reset to ROOT."
   - ELSE:
     - Set environment variable: `export ACTIVE_WORKSPACE={target}`
     - Announce: "Workspace context switched to: **{target}**"

8. **(Steward) [Verify Switch]**
   - Read `$ACTIVE_WORKSPACE` and confirm value matches target
   - Load the corresponding `project_manifest.json` to verify accessibility:
     - IF target == "ROOT": Load `project_manifest.json`
     - ELSE: Load `workspaces/{target}/project_manifest.json`
   - IF load fails:
     - State: "ERROR: Failed to load manifest for workspace '{target}'. Context switch incomplete."
     - ABORT.
   - IF load succeeds: Proceed to Step 9.

9. **(Steward) [Present Workspace Summary]**
   - Announce: "Workspace switch complete. Summary:"
   - Display workspace information:

     ```
     ✅ ACTIVE WORKSPACE: {target}
     ✅ Project Manifest: {manifest_path}
     ✅ Project Phase: {current_state}
     ✅ Last Updated: {lastUpdatedAt}

     WORKSPACE OPERATIONS:
     - All artifact reads/writes will now target: workspaces/{target}/artifacts/
     - All SOP executions will reference: workspaces/{target}/project_manifest.json
     - To return to ROOT context, run SOP_008 again and select "ROOT"
     ```

10. **(Steward) [Context Guidance]**
    - Based on `current_state`, provide proactive next step guidance:
      - IF state == "INITIALIZING":
        - Suggest: "This workspace is newly created. To begin project planning, use SOP_001 (Start New Project)."
      - IF state == "PLANNING":
        - Suggest: "Project is in PLANNING phase. Continue working with VIBE_ALIGNER or use SOP_001 to refine scope."
      - IF state == "CODING":
        - Suggest: "Project is in CODING phase. AOS agents are generating code."
      - IF state == "AWAITING_QA_APPROVAL":
        - Suggest: "QA approval required. SOP_003 will be triggered automatically."
      - IF state == "PRODUCTION":
        - Suggest: "Project is in PRODUCTION. To package deliverables, use SOP_009."

---

## SESSION PERSISTENCE

**Important:** The `$ACTIVE_WORKSPACE` environment variable is **session-scoped**.

- ✅ Persists for the duration of the current terminal/agent session
- ❌ Does NOT persist across new sessions (intentional design)
- ✅ Applies to ALL SOP executions within the session

**To switch workspaces in a new session:**
- Re-run SOP_008 at the start of each new session
- OR: Add to shell profile for persistent default (advanced users only)

**Example:**
```bash
# Session 1:
export ACTIVE_WORKSPACE=acme_corp
# (Work on acme_corp project...)

# Session 2 (new terminal):
# $ACTIVE_WORKSPACE is NOT set → defaults to ROOT
# Must run SOP_008 again to set context
```

---

## ANTI-SLOP ENFORCEMENT

- **MUST NOT** allow switching to non-existent workspace
- **MUST NOT** allow switching to archived workspace (unless explicitly enabled via future SOP)
- **MUST** verify manifest accessibility before confirming switch
- **MUST** provide clear feedback on current vs. target context

---

## ERROR HANDLING

**Error 1: Workspace Not Found**
- Message: "ERROR: Workspace '{target}' not found in registry."
- Resolution: User must choose from active workspaces OR create new workspace via SOP_007.

**Error 2: Manifest Inaccessible**
- Message: "ERROR: Cannot load manifest at `workspaces/{target}/project_manifest.json`. File may be corrupted or deleted."
- Resolution: Manual investigation required. Check file permissions and integrity.

**Error 3: Invalid Workspace Name Format**
- Message: "WARNING: Workspace name '{target}' contains uppercase or special characters. Expected: snake_case."
- Resolution: Auto-normalize OR reject (based on strictness setting).

---

## GOVERNANCE CHECKPOINTS

**HITL Required:** NO (workspace switching is non-destructive)

**HITL Recommended:** YES (for external client workspaces)
- Recommendation: Log workspace switches for audit trail
- Audit entry:
  ```
  [2025-11-12 10:45:30] SOP_008 | SWITCH | from: ROOT | to: acme_corp | user: agent@vibe.agency
  ```

---

## INTEGRATION WITH OTHER SOPS

After executing SOP_008, all subsequent SOPs operate in the new context:

**Example Flow:**
```bash
# 1. Switch to client workspace
run_sop('SOP_008', target='acme_corp')

# 2. Start new project (operates on acme_corp manifest)
run_sop('SOP_001', user_input='Build booking system')

# 3. Bug report (files bug for acme_corp project)
run_sop('SOP_002', bug_description='Login broken')

# 4. Query status (reads acme_corp status)
run_sop('SOP_005')

# All operations above target: workspaces/acme_corp/
```

---

## QUICK REFERENCE

**Switch to client workspace:**
```
User: "Switch to workspace acme_corp"
→ SOP_008 executes
→ $ACTIVE_WORKSPACE = acme_corp
```

**Return to ROOT:**
```
User: "Switch to ROOT"
→ SOP_008 executes
→ $ACTIVE_WORKSPACE unset
```

**List workspaces without switching:**
```
User: "List workspaces"
→ SOP_008 executes Steps 1-3, then cancels at Step 4
```

---

## RELATED SOPS

- **SOP_007:** Create Client Workspace (use before first switch to new client)
- **SOP_001-006:** All SOPs respect `$ACTIVE_WORKSPACE` context
- **SOP_009:** Package Client Deliverables (requires active workspace context)

---

**SOP_008 Definition Complete.**
