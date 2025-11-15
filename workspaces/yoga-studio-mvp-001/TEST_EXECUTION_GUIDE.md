# Test Execution Guide - Yoga Studio MVP Portfolio Test

## Prerequisites

### 1. Environment Setup

Ensure UV and all dependencies are installed:

```bash
# Install dependencies
make install

# Verify installation
uv --version
python --version  # Should be 3.12+
```

### 2. Research Tools Validation

Run the validation script to check research tools setup:

```bash
python scripts/validate_research_tools.py
```

**Expected output:**
```
✅ Web Fetch Client: WORKS
✅ Tool Executor: WORKS
⏭️  Google Search API: NOT CONFIGURED (using Claude Code WebSearch)
   OR
✅ Google Search API: WORKS
```

### 3. Google API Keys (Optional but Recommended)

Google API keys are **optional** but enable faster research:

**Option 1: .env file**
```bash
cat > .env <<EOF
GOOGLE_SEARCH_API_KEY=your-api-key-here
GOOGLE_SEARCH_ENGINE_ID=your-cse-id-here
EOF
```

**Option 2: Claude Code settings**
```bash
mkdir -p .claude
cat > .claude/settings.local.json <<EOF
{
  "environment": {
    "GOOGLE_SEARCH_API_KEY": "your-api-key-here",
    "GOOGLE_SEARCH_ENGINE_ID": "your-cse-id-here"
  }
}
EOF
```

**Fallback behavior:**
If keys are not configured, the system automatically uses Claude Code's built-in WebSearch tool. The test will still pass.

### 4. Claude Code Operator

Ensure Claude Code operator is running and ready to respond to delegation requests.

---

## Execution Steps

### Step 1: Verify Environment

```bash
# Check workspace exists
ls -la workspaces/yoga-studio-mvp-001/

# Verify project manifest
cat workspaces/yoga-studio-mvp-001/project_manifest.json | jq .status.projectPhase
# Should output: "PLANNING"
```

### Step 2: Run Validation Script

```bash
python scripts/validate_research_tools.py
```

**Expected result:** All tools marked as ✅ or ⏭️ (skipped with fallback)

### Step 3: Execute Test

```bash
./vibe-cli run yoga-studio-mvp-001
```

**What happens:**
1. Orchestrator reads `project_manifest.json`
2. Enters PLANNING phase
3. Delegates to VIBE_ALIGNER, LEAN_CANVAS_VALIDATOR, GENESIS_BLUEPRINT
4. Transitions to RESEARCH (if research enabled)
5. Research agents query Google API or delegate to Claude Code WebSearch
6. Transitions to CODING phase
7. Code generation with quality gates
8. Artifacts saved to `workspaces/yoga-studio-mvp-001/artifacts/`

### Step 4: Monitor Progress

**Terminal 1: Run vibe-cli**
```bash
./vibe-cli run yoga-studio-mvp-001
```

**Terminal 2: Monitor logs** (optional)
```bash
# Watch execution trace
tail -f workspaces/yoga-studio-mvp-001/logs/execution_trace.json

# Check current phase
watch -n 5 'cat workspaces/yoga-studio-mvp-001/project_manifest.json | jq .status.projectPhase'

# List artifacts as they're created
watch -n 10 'ls -la workspaces/yoga-studio-mvp-001/artifacts/'
```

### Step 5: Verify Artifacts

After test completes (3-4 hours), verify all artifacts were created:

```bash
ls -la workspaces/yoga-studio-mvp-001/artifacts/

# Expected files:
# lean_canvas.json
# feature_spec.json
# research_summary.json (if research ran)
# code_gen_spec.json
# artifact_bundle.json
```

---

## Expected Timeline

### PLANNING Phase (30-45 minutes)

**Sub-states:**
1. **RESEARCH** (5-10 min) - Initial business research
2. **BUSINESS_VALIDATION** (10-15 min) - LEAN_CANVAS_VALIDATOR
3. **FEATURE_SPECIFICATION** (10-15 min) - GENESIS_BLUEPRINT
4. **ARCHITECTURE_DESIGN** (5-10 min) - Technical decisions

**Artifacts created:**
- `lean_canvas.json`
- `feature_spec.json`

**Expected delegations to Claude Code:**
- "Validate this lean canvas against market research"
- "Generate detailed feature specifications"
- "Assess technical feasibility of requirements"

### RESEARCH Phase (15-20 minutes)

**Research agents triggered:**
1. **MARKET_RESEARCHER** (5 min) - Market size, competitors, pricing
2. **TECH_RESEARCHER** (5 min) - Payment gateways, architecture patterns
3. **USER_RESEARCHER** (3 min) - User behavior, pain points
4. **FACT_VALIDATOR** (2-5 min) - Cross-validate findings

**Artifacts created:**
- `research_summary.json`

**Expected behavior:**
- Google API calls (if configured) or
- WebSearch delegations to Claude Code (fallback)
- Web content extraction with BeautifulSoup
- Research insights integrated into feature_spec

### CODING Phase (60-90 minutes)

**5-phase workflow:**
1. **CODE_GEN_INIT** (10 min) - Setup project structure
2. **CODE_GEN_CORE** (30 min) - Core components
3. **CODE_GEN_INTEGRATION** (20 min) - API integrations
4. **CODE_GEN_TESTING** (15 min) - Test suite
5. **CODE_GEN_FINALIZE** (5-15 min) - Documentation, deployment

**Artifacts created:**
- `code_gen_spec.json`
- `artifact_bundle.json`

**Quality gates applied:**
1. Business viability check
2. Technical feasibility check
3. Budget alignment
4. Timeline realism
5. Compliance requirements (GDPR, PCI DSS)
6. Scalability assessment
7. Security review
8. User experience validation
9. Market fit analysis

---

## Monitoring Commands

### Check Current Phase
```bash
cat workspaces/yoga-studio-mvp-001/project_manifest.json | jq .status.projectPhase
cat workspaces/yoga-studio-mvp-001/project_manifest.json | jq .status.planningSubState
```

### View Real-time Logs
```bash
tail -f workspaces/yoga-studio-mvp-001/logs/execution_trace.json | jq .
```

### List Generated Artifacts
```bash
ls -lah workspaces/yoga-studio-mvp-001/artifacts/
```

### Check Budget Usage
```bash
cat workspaces/yoga-studio-mvp-001/project_manifest.json | jq .budget
```

### View Research Results
```bash
cat workspaces/yoga-studio-mvp-001/artifacts/research_summary.json | jq .
```

---

## Troubleshooting

### Issue: Test Hangs or Appears Stuck

**Symptoms:**
- No progress for >10 minutes
- No delegation requests in STDOUT
- Logs show same phase repeatedly

**Solutions:**
1. Check if Claude Code operator is waiting for input
2. Review STDOUT for delegation requests
3. Check logs: `tail -f workspaces/yoga-studio-mvp-001/logs/execution_trace.json`
4. Verify phase transition logic in orchestrator

**Emergency stop:**
```bash
# Gracefully stop vibe-cli
Ctrl+C

# Check current state
cat workspaces/yoga-studio-mvp-001/project_manifest.json | jq .status
```

### Issue: Google API Fails

**Symptoms:**
- Errors mentioning "Google API"
- Research phase fails to complete
- No research_summary.json created

**Solutions:**
1. **Expected behavior:** System should auto-fallback to Claude Code WebSearch
2. Check logs for "using Claude Code WebSearch" message
3. Verify fallback is working: Look for WebSearch delegations in STDOUT
4. Test should continue WITHOUT failure

**Manual fallback test:**
```bash
# Temporarily unset Google API keys
unset GOOGLE_SEARCH_API_KEY
unset GOOGLE_SEARCH_ENGINE_ID

# Re-run test - should use WebSearch fallback
./vibe-cli run yoga-studio-mvp-001
```

### Issue: Artifacts Missing

**Symptoms:**
- Expected artifacts not in `workspaces/yoga-studio-mvp-001/artifacts/`
- Phase completed but no files created

**Solutions:**
1. Check quality gates: Did any validation fail?
   ```bash
   grep -i "quality gate" workspaces/yoga-studio-mvp-001/logs/execution_trace.json
   ```
2. Verify phase transitions completed:
   ```bash
   cat workspaces/yoga-studio-mvp-001/project_manifest.json | jq .status
   ```
3. Check for error messages in logs:
   ```bash
   grep -i "error\|failed" workspaces/yoga-studio-mvp-001/logs/execution_trace.json
   ```

### Issue: Phase Transitions Don't Work

**Symptoms:**
- Stuck in one phase indefinitely
- `planningSubState` doesn't progress

**Solutions:**
1. Verify state machine logic in orchestrator
2. Check transition conditions in handlers
3. Review delegation responses from Claude Code
4. Ensure all quality gates are passing

---

## Validation Checklist

After test completes, verify:

- [ ] All 5 artifacts created in `workspaces/yoga-studio-mvp-001/artifacts/`
- [ ] `lean_canvas.json` contains valid business model
- [ ] `feature_spec.json` has detailed feature breakdown (15-25 features)
- [ ] `research_summary.json` includes market/tech/user insights
- [ ] `code_gen_spec.json` has complete technical architecture
- [ ] `artifact_bundle.json` contains production-ready code
- [ ] All JSON files pass schema validation
- [ ] Research insights visible in feature specifications
- [ ] Quality gates all passed (check logs)
- [ ] Budget tracked correctly (< $100 USD)
- [ ] Total execution time: 3-4 hours

---

## Next Steps

After successful test:

1. **Review artifacts:** Examine quality of generated outputs
2. **Validate research:** Check if research insights were integrated
3. **Test code:** Deploy artifact_bundle to test environment
4. **Document findings:** Update test reports with results
5. **Iterate:** Use learnings to improve prompts/agents

---

## Support

If you encounter issues not covered in troubleshooting:

1. Review [ARCHITECTURE_V2.md](../../ARCHITECTURE_V2.md)
2. Check [CLAUDE.md](../../CLAUDE.md) for operational status
3. Consult [docs/testing/](../../docs/testing/) for testing guides
4. File issue with:
   - Execution logs
   - Error messages
   - Steps to reproduce
