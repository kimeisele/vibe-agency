# GAD-502 Semantic Clarification: "Haiku API" vs "Claude Code Operator Using Haiku"

**Date:** 2025-11-17
**Issue:** [GAD-005 haiku misunderstanding](https://github.com/kimeisele/vibe-agency/issues/XXX)
**Status:** ✅ RESOLVED

---

## 🎯 THE SEMANTIC PROBLEM

**GAD-502.md contains ambiguous language that conflicts with established architecture.**

### What GAD-502 Says (Problematic):

**Line 540:** "Test with REAL Haiku API to validate hardening works"
**Line 543:** "Use Haiku API to execute PLANNING workflow"
**Line 559:** `result = haiku_api.complete(planning_prompt)`

### Why This Is Problematic:

1. **Suggests Direct API Integration**
   - "Haiku API" sounds like vibe-cli/orchestrator would call Anthropic API directly
   - This violates the MVP architecture (DELEGATION ONLY)
   
2. **Conflicts with EXECUTION_MODE_STRATEGY.md**
   - Per EXECUTION_MODE_STRATEGY.md: vibe-cli MUST NOT make API calls in MVP
   - API calls are explicitly FORBIDDEN
   - Only delegation to Claude Code operator is allowed

3. **Creates Architectural Confusion**
   - Developers might implement direct Anthropic API integration
   - Would reintroduce the nested API calls problem (Claude Code → vibe-cli → Anthropic API)
   - Violates the "single mode for MVP" principle

---

## ✅ THE CORRECT UNDERSTANDING

### What "Haiku" Actually Means in Context:

**Haiku** = A model option for the Claude Code operator (like Sonnet or Opus)

**NOT:** A separate API that vibe-agency calls directly

### Architecture Clarity:

```
┌─────────────────────────────────────────────────────────┐
│ CLAUDE CODE OPERATOR                                    │
│ ↓ Can use different models:                            │
│   - claude-sonnet-4-20250514 (current default)         │
│   - claude-opus-4-20250514 (for complex tasks)         │
│   - claude-haiku-3-5-20241022 (for simple tasks)       │
│                                                         │
│ The OPERATOR chooses the model, not vibe-agency        │
└───────────────────┬─────────────────────────────────────┘
                    │ uses
                    ▼
┌─────────────────────────────────────────────────────────┐
│ vibe-cli (DELEGATION BRIDGE - NO API CALLS)            │
│ - Prints prompts to operator                           │
│ - Reads operator responses                             │
│ - NO knowledge of which model operator is using        │
│ - NO Anthropic SDK imports                             │
│ - NO API calls                                         │
└─────────────────────────────────────────────────────────┘
```

### What GAD-502 Phase 6 ACTUALLY Means:

**Original (Ambiguous):**
> "Use Haiku API to execute PLANNING workflow"

**Corrected (Clear):**
> "Have the Claude Code operator use Haiku model to execute PLANNING workflow"

**Original (Suggests API):**
```python
result = haiku_api.complete(planning_prompt)
```

**Corrected (Delegation):**
```python
# Claude Code operator (you!) runs this with Haiku model selected
result = anthropic.messages.create(
    model="claude-haiku-3-5-20241022",  # Operator chooses model
    messages=[{"role": "user", "content": planning_prompt}]
)
```

---

## 🔍 EVIDENCE FROM ARCHITECTURE DOCS

### From EXECUTION_MODE_STRATEGY.md:

```python
### ❌ FORBIDDEN in vibe-cli (MVP)

# NO Anthropic SDK imports
import anthropic  # ❌ FORBIDDEN

# NO API clients
self.client = anthropic.Anthropic(api_key=...)  # ❌ FORBIDDEN

# NO prompt execution
response = client.messages.create(...)  # ❌ FORBIDDEN
```

**Line 104-105:** "Why Forbidden: Claude Code (the operator) IS the intelligence layer"

### From CLAUDE.md:

**Line 28:** `Claude Code (operator) ← STDOUT/STDIN → vibe-cli → Core Orchestrator`

**Line 31:** "vibe-cli delegates intelligence requests to Claude Code operator"

### From ARCHITECTURE_V2.md:

**Delegation Flow:**
```
Orchestrator → INTELLIGENCE_REQUEST
             ↓
         vibe-cli prints DELEGATION_REQUEST to STDOUT
             ↓
         Claude Code operator reads request
             ↓
         Claude Code executes via Anthropic API (with tools if needed)
             ↓
         Claude Code sends response to vibe-cli via STDIN
```

**Key:** "Claude Code executes via Anthropic API" - NOT vibe-cli!

---

## 🎯 THE CORRECT INTERPRETATION

### What GAD-502 Is Really About:

**Goal:** Make vibe-agency safe for less capable operators

**Less Capable Operator Options:**
1. **Junior developer** (human with limited context)
2. **Claude Haiku model** (cheaper, faster, less capable AI)
3. **Other AI assistants** (GitHub Copilot, etc.)

**Protection Strategy:**
- Kernel checks prevent dangerous operations
- Clear error messages help less capable operators recover
- MOTD provides critical context upfront
- Escalation guidance ("ask operator") handles edge cases

### Phase 6 Validation - Correct Approach:

**Test:** Can a Claude Code operator using Haiku model successfully complete PLANNING workflow?

**Implementation:**
1. Human operator (you!) switches Claude Code to use Haiku model
2. Operator executes: `./vibe-cli run test-project`
3. vibe-cli delegates prompts to operator (via file-based handoff)
4. Operator responds using Haiku model
5. Measure: Did kernel prevent mistakes? Did errors help recovery?

**NO direct API integration needed!**

---

## 📝 REQUIRED CORRECTIONS IN GAD-502.md

### Change 1: Phase 6 Title
```diff
-### Phase 6: Validation (Week 5) - OPTIONAL
+### Phase 6: Operator Model Validation (Week 5) - OPTIONAL
```

### Change 2: Goal Statement
```diff
-**Goal:** Test with REAL Haiku API to validate hardening works.
+**Goal:** Test with Claude Code operator using Haiku model to validate hardening works.
```

### Change 3: Approach Description
```diff
-1. Use Haiku API to execute PLANNING workflow
+1. Have operator use Haiku model to execute PLANNING workflow (via delegation)
```

### Change 4: Why Optional
```diff
-- Requires Haiku API access
+- Requires operator to manually switch to Haiku model
```

### Change 5: Code Example
```diff
-class HaikuSimulator:
-    """Simulate Haiku executing tasks, measure protection."""
+class OperatorModelValidator:
+    """Validate system works with less capable operator models (e.g., Haiku)."""

     def test_planning_workflow(self):
-        # Run REAL Haiku through PLANNING
-        result = haiku_api.complete(planning_prompt)
+        # Operator (you!) should switch Claude Code to Haiku model
+        # Then execute: ./vibe-cli run test-project
+        # This test just validates the delegation works
+        result = run_delegated_workflow("test-project")
```

### Change 6: Deliverables
```diff
-- Haiku API integration (~50 LOC)
+- Delegation test harness (~50 LOC)
 - Planning workflow test (~30 LOC)
 - Metrics report (prevention rate, common mistakes)
+
+NOTE: No API integration needed - validation is manual (operator switches model)
```

### Change 7: Add Clarifying Note
```diff
+**IMPORTANT:** This is NOT about adding Haiku API integration to vibe-agency.
+Per EXECUTION_MODE_STRATEGY.md, vibe-cli MUST NOT make API calls in MVP.
+
+This phase validates that the DELEGATION architecture works when the 
+Claude Code operator chooses to use a less capable model (Haiku instead of Sonnet).
+
+The operator controls model selection, not vibe-agency.
```

---

## 🚫 WHAT NOT TO DO

### ❌ Don't Add Direct API Integration
```python
# WRONG - violates MVP architecture
import anthropic
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
response = client.messages.create(model="claude-haiku-3-5-20241022", ...)
```

### ❌ Don't Create "Haiku Mode" in vibe-cli
```python
# WRONG - model selection belongs to operator
if args.model == "haiku":
    model = "claude-haiku-3-5-20241022"
```

### ❌ Don't Implement Model Detection
```python
# WRONG - vibe-cli shouldn't know which model operator is using
detected_model = detect_operator_model()
```

---

## ✅ WHAT TO DO INSTEAD

### Phase 6 Manual Validation Procedure:

1. **Setup:** Create a test project
   ```bash
   ./vibe-cli init haiku-validation-test
   ```

2. **Switch Operator Model:**
   - In Claude Code settings, change model to Haiku
   - Or use API directly with model="claude-haiku-3-5-20241022"

3. **Execute Workflow:**
   ```bash
   ./vibe-cli run haiku-validation-test
   ```

4. **Respond to Delegation Requests:**
   - vibe-cli will create request files in `.delegation/`
   - You (operator) read request, respond using Haiku model
   - Write response file
   - Repeat for all PLANNING phases

5. **Measure Results:**
   - Count kernel violations prevented
   - Note error messages that helped vs confused
   - Document recovery patterns
   - Assess if Haiku completed workflow successfully

6. **Report Metrics:**
   ```
   Results:
   - Workflow completion: ✅ Success / ❌ Failed
   - Kernel violations prevented: 3 (overwrite manifest, skip lint, etc.)
   - Error messages helpful: 2/3 (67%)
   - Operator escalations needed: 1 (git conflict)
   - Time vs Sonnet: +40% (acceptable for cost savings)
   ```

---

## 📊 IMPLICATIONS

### For GAD-502 Implementation:

**No changes needed to Phases 2-5!**

Phases 2-5 are correct as written:
- Shell guardrails (Phase 2): ✅ Correct
- Error messages (Phase 3): ✅ Correct  
- MOTD alerts (Phase 4): ✅ Correct
- Recovery playbooks (Phase 5): ✅ Correct

**Only Phase 6 needs clarification:**
- Change "Haiku API" → "Operator using Haiku model"
- Emphasize manual validation, not automated API testing
- Align with delegation-only architecture

### For Future Work (v2+):

**IF we later add standalone mode (v2):**

Then vibe-cli WOULD have model selection:
```python
# vibe-cli v2 (future - not MVP)
if execution_mode == "standalone":
    model = args.model or "claude-sonnet-4-20250514"
    response = client.messages.create(model=model, ...)
```

**But for MVP:** This is explicitly deferred per EXECUTION_MODE_STRATEGY.md

---

## ✅ APPROVAL & SIGN-OFF

**Reviewed By:** Claude Code (Sonnet 4.5)
**Date:** 2025-11-17
**Conclusion:** 

✅ GAD-502 has a **semantic issue, not architectural issue**

✅ Solution: **Clarify language** (not code changes)

✅ Changes needed: **Documentation only** (update GAD-502.md wording)

✅ Architecture remains sound: **Delegation-only in MVP**

**Next Action:** Update GAD-502.md with corrections listed above
