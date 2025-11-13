# Gate: NFR Reliability Validation

**Gate ID:** gate_nfr_reliability
**Type:** Quality Gate
**Scope:** All runtime operations
**Enforcement:** BLOCKING (must pass before release)

---

## Rule

All runtime operations must meet reliability requirements defined in `docs/requirements/NFR_RELIABILITY.yaml`:

1. **Clear Error Messages:** All errors provide actionable fix suggestions
2. **Graceful Degradation:** Optional features fail without breaking core functionality
3. **Idempotency:** Repeated operations produce same result (no side effects)
4. **No Silent Failures:** All errors logged with full context
5. **Recovery Procedures:** Documented recovery for all failure modes

---

## Rationale

**Why this rule exists:**

- **User Experience:** Generic errors frustrate users. "File not found" is useless; "File not found: /path/to/file - Fix: Check path" is helpful.
- **System Resilience:** Missing optional knowledge should warn, not crash. Core functionality must work even when optional components fail.
- **Predictability:** `compose(agent, task, context)` should always produce the same prompt given same inputs. No hidden state.
- **Debuggability:** Silent failures make bugs impossible to diagnose. All failures must leave audit trail.
- **Operational Excellence:** When things break (and they will), teams need clear recovery procedures.

**Impact of violations:**
- 🔴 Poor error messages → Users can't self-recover, support burden increases
- 🔴 Silent failures → Bugs go undetected, data loss
- 🟡 Non-idempotent operations → Unpredictable behavior, hard to test
- 🟡 Missing recovery docs → Extended downtime, confused operators

---

## Validation

### Automated Checks

**1. Error Message Quality (IMPLEMENTED ✅)**

**Standard:** All custom exceptions include:
- What went wrong (error type)
- Where it happened (file path, agent_id, task_id)
- Why it failed (root cause)
- How to fix it (actionable guidance)

**Example from `prompt_runtime.py`:**
```python
raise TaskNotFoundError(
    f"Task metadata not found: {task_id}\n"
    f"Agent: {agent_id}\n"
    f"Searched:\n"
    f"  - {agent_path}/tasks/task_{task_id}.meta.yaml\n"
    f"  - {agent_path}/tasks/{task_id}.meta.yaml\n"
    f"Available tasks: {', '.join(available_tasks) if available_tasks else 'none'}\n"
    f"Fix: Check task_id spelling or create task metadata file"
)
```

**Validation:**
```bash
# Test error messages manually
python3 << 'EOF'
from agency_os.runtime.prompt_runtime import *

runtime = PromptRuntime()

# Test 1: Invalid agent
try:
    runtime.execute_task("INVALID_AGENT", "task", {})
except AgentNotFoundError as e:
    print(f"✓ Error message quality: {len(str(e)) > 100}")
    print(str(e))

# Test 2: Invalid task
try:
    runtime.execute_task("VIBE_ALIGNER", "invalid_task", {})
except TaskNotFoundError as e:
    print(f"✓ Lists available tasks: {'Available tasks:' in str(e)}")
    print(str(e))
EOF
```

**Status:** IMPLEMENTED ✅

---

**2. Graceful Degradation (PARTIAL ⚠️)**

**Requirement:** Optional knowledge bases missing should LOG WARNING, not FAIL.

**Current Implementation:**
```python
# From _resolve_knowledge_deps()
for opt in deps.get("optional_knowledge", []):
    try:
        content = self._load_knowledge_file(opt["path"])
        knowledge_files.append(content)
    except FileNotFoundError:
        # ✅ GOOD: Log warning, continue
        logger.warning(f"Optional knowledge not found: {opt['path']}")
```

**Test Cases:**
```python
# Test graceful degradation
def test_missing_optional_knowledge():
    runtime = PromptRuntime()

    # Remove optional knowledge file temporarily
    backup_file("optional_knowledge.yaml")

    # Should succeed with warning
    result = runtime.execute_task("AGENT", "task", {})
    assert result is not None
    assert "WARNING" in get_last_log()

    restore_file("optional_knowledge.yaml")
```

**Status:** IMPLEMENTED ✅ (optional knowledge)
**TO DO:** Validate gates can also be optional

---

**3. Idempotency (IMPLEMENTED ✅)**

**Requirement:** Same inputs always produce same output (no hidden state).

**Verification:**
```python
def test_composition_idempotency():
    runtime = PromptRuntime()
    context = {"project_id": "test_001"}

    # Compose twice
    result1 = runtime.execute_task("VIBE_ALIGNER", "task_01", context)
    result2 = runtime.execute_task("VIBE_ALIGNER", "task_01", context)

    # Should be identical
    assert result1 == result2
```

**Current Status:** IMPLEMENTED ✅
- Knowledge cache doesn't affect output (only performance)
- No global state mutated during composition
- File reads are pure (no writes)

**Exception:** Runtime context may include timestamps
```python
# If context includes dynamic data
context = {
    "project_id": "test_001",
    "timestamp": datetime.now()  # Different each run
}
# Then outputs will differ - document this in context schema
```

---

**4. Logging All Errors (IMPLEMENTED ✅)**

**Requirement:** All errors logged with full context before raising.

**Implementation:**
```python
# From execute_task()
except (AgentNotFoundError, TaskNotFoundError, MalformedYAMLError) as e:
    logger.error(f"Composition failed: {e}")  # ✅ Logged
    raise  # ✅ Then raised

except Exception as e:
    logger.error(f"Unexpected error: {e}", exc_info=True)  # ✅ With stack trace
    raise CompositionError(...) from e
```

**Log Format (JSON):**
```json
{
  "timestamp": "2025-11-13T10:30:00Z",
  "level": "ERROR",
  "logger": "prompt_runtime",
  "message": "Composition failed: Agent not found: 'INVALID_AGENT'",
  "context": {
    "agent_id": "INVALID_AGENT",
    "task_id": "task_01",
    "project_id": "test_001"
  },
  "exception": {
    "type": "AgentNotFoundError",
    "message": "Agent not found: 'INVALID_AGENT'...",
    "traceback": "..."
  }
}
```

**Current Status:** IMPLEMENTED ✅ (basic logging)
**TO DO:** Structured JSON logging, log rotation

---

**5. Documented Recovery Procedures (PARTIAL ⚠️)**

**Requirement:** Each failure mode has documented recovery in NFR_RELIABILITY.yaml.

**Implemented Scenarios:**
- ✅ Complete system loss → Reinstall + restore workspaces
- ✅ Workspace corruption → Restore from backup
- ✅ Knowledge base corruption → `git checkout <file>`
- ❌ Composition failure mid-flight → No documented recovery
- ❌ Corrupted cache → How to clear?
- ❌ Permissions error → How to fix?

**Status:** PARTIAL ⚠️

**TO DO:** Add troubleshooting guide (`docs/TROUBLESHOOTING.md`)

---

### Manual Checks

**Pre-Release Reliability Checklist:**

```markdown
## Reliability Validation (Before v1.0)

### Error Handling
- [ ] All custom exceptions implemented (Agent/Task/YAML/Composition)
- [ ] All errors include fix suggestions
- [ ] No generic exceptions without context
- [ ] Error messages tested manually

### Logging
- [ ] All errors logged before raising
- [ ] Stack traces included for unexpected errors
- [ ] Sensitive data NOT in logs (API keys, user data)
- [ ] Log rotation configured (30 days)

### Graceful Degradation
- [ ] Missing optional knowledge logs warning, doesn't fail
- [ ] Missing optional gates logs warning, doesn't fail
- [ ] File corruption handled gracefully
- [ ] Out-of-disk-space handled

### Idempotency
- [ ] Composition is idempotent (same inputs = same output)
- [ ] Knowledge cache doesn't affect output
- [ ] No side effects during composition

### Recovery
- [ ] Backup/restore procedures documented
- [ ] Troubleshooting guide created
- [ ] Incident response plan defined
- [ ] Recovery tested manually
```

---

## Failure Guidance

### If Composition Fails Mid-Flight

**Scenario:** Composition starts but fails halfway through (e.g., YAML parse error in gate file).

**Current Behavior:**
```python
# Composition is atomic - all-or-nothing
try:
    prompt = compose(...)  # Either succeeds or raises exception
except CompositionError:
    # No partial prompt returned
    pass
```

**Recovery:**
1. Check error message for root cause
2. Fix the issue (e.g., fix YAML syntax)
3. Retry composition (safe - idempotent)

**No Cleanup Needed:** Composition is stateless, no rollback required.

---

### If Knowledge Cache Corrupted

**Symptoms:**
- Composition uses stale knowledge
- Changes to YAML not reflected in prompts

**Root Cause:** Knowledge cache (`self.knowledge_cache`) persists across runs.

**Recovery:**
```python
# Option 1: Restart runtime (clears cache)
runtime = PromptRuntime()  # Fresh cache

# Option 2: Manual cache clear
runtime.knowledge_cache.clear()

# Option 3: Disable caching (for debugging)
def _load_knowledge_file(self, path):
    # Skip cache, always read from disk
    with open(path) as f:
        return f.read()
```

**Prevention:**
- Cache invalidation on file modification (TO DO)
- TTL for cache entries (TO DO)

---

### If File Permissions Error

**Scenario:**
```
PermissionError: [Errno 13] Permission denied: '/home/user/vibe-agency/workspaces/project/artifact.json'
```

**Root Cause:** Incorrect file permissions (e.g., file created by root, accessed by user).

**Recovery:**
```bash
# Check permissions
ls -la workspaces/project/artifact.json

# Fix permissions (owner read/write)
chmod 600 workspaces/project/artifact.json

# Fix ownership (if file owned by wrong user)
chown $USER:$USER workspaces/project/artifact.json
```

**Prevention:**
- Always use user's permissions (not root)
- Document required permissions in deployment docs

---

### If Disk Space Full

**Scenario:**
```
OSError: [Errno 28] No space left on device
```

**Root Cause:** Workspace or logs consuming all disk space.

**Recovery:**
```bash
# Check disk usage
df -h
du -sh workspaces/ ~/.vibe_agency/logs/

# Free up space
# Option 1: Archive old workspaces
tar -czf old-projects-$(date +%Y%m%d).tar.gz workspaces/old_projects/
rm -rf workspaces/old_projects/

# Option 2: Rotate logs manually
rm ~/.vibe_agency/logs/*.log.old

# Option 3: Clean knowledge cache (if implemented)
rm -rf ~/.vibe_agency/cache/
```

**Prevention:**
- Implement log rotation (30 days)
- Monitor disk usage (warn at 80%)
- Document cleanup procedures

---

## Monitoring

### Reliability Metrics

**Track per Composition:**
- Success/failure rate (target: 99%)
- Error types frequency
- Recovery time (error → fix → success)

**Aggregate Weekly:**
- Most common errors (prioritize fixes)
- Mean Time To Recovery (MTTR)
- P95 composition time (detect performance regressions)

### Alerts

**Trigger Conditions:**
- Composition failure rate > 5%
- Disk space < 1 GB
- Logs not rotating (> 10 GB)
- Same error > 10 times in 1 hour

**Action:**
- Log alert
- Send notification (if email configured)
- Document incident

---

## Implementation Status

- [x] Custom exceptions with fix suggestions
- [x] Logging all errors with context
- [x] Graceful degradation (optional knowledge)
- [x] Idempotent composition
- [ ] Structured JSON logging
- [ ] Log rotation (30 days)
- [ ] Troubleshooting guide
- [ ] Cache invalidation
- [ ] Disk space monitoring

**Next Steps:**
1. Implement log rotation
2. Create `docs/TROUBLESHOOTING.md`
3. Add disk space check before composition
4. Implement structured JSON logging
5. Test all recovery procedures

---

## Testing

### Reliability Test Suite

```python
# test_reliability.py

def test_error_message_quality():
    """All errors must have fix suggestions"""
    runtime = PromptRuntime()

    try:
        runtime.execute_task("INVALID", "task", {})
    except AgentNotFoundError as e:
        assert "Fix:" in str(e)
        assert "Available agents:" in str(e)

def test_graceful_degradation():
    """Missing optional knowledge should warn, not fail"""
    # Temporarily remove optional knowledge
    # Composition should succeed with warning

def test_idempotency():
    """Same inputs produce same output"""
    runtime = PromptRuntime()
    context = {"project_id": "test"}

    result1 = runtime.execute_task("AGENT", "task", context)
    result2 = runtime.execute_task("AGENT", "task", context)

    assert result1 == result2

def test_no_silent_failures():
    """All errors are logged"""
    with capture_logs() as logs:
        try:
            runtime.execute_task("INVALID", "task", {})
        except:
            pass

    assert any("ERROR" in log for log in logs)
```

---

## References

- `docs/requirements/NFR_RELIABILITY.yaml` - Full reliability requirements
- `prompt_runtime.py:174-181` - Error handling implementation
- `prompt_runtime.py:32-54` - Custom exception definitions
- Well-Architected Framework (AWS) - Reliability pillar
