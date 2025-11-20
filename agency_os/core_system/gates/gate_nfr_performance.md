# Gate: NFR Performance Validation

**Gate ID:** gate_nfr_performance
**Type:** Quality Gate
**Scope:** All composed prompts
**Enforcement:** WARNING (non-blocking)

---

## Rule

All composed prompts must meet performance requirements defined in `docs/requirements/NFR_PERFORMANCE.yaml`:

1. **Prompt Size:** Final composed prompt < 200,000 characters (LLM context window limit)
2. **Composition Time:** Prompt composition completes in < 500ms (fast file I/O)
3. **Knowledge Base Size:** Individual knowledge files < 5 MB (parsing performance)
4. **Memory Usage:** Runtime process < 512 MB RAM (laptop-friendly)

---

## Rationale

**Why this rule exists:**

- **LLM Context Limits:** Claude Sonnet has a 200k token limit (~200k chars). Exceeding this causes API errors.
- **User Experience:** Slow composition (> 500ms) degrades developer experience, especially during rapid iteration.
- **Parsing Performance:** Large YAML files (> 5 MB) significantly slow down yaml.safe_load().
- **Resource Efficiency:** System should run comfortably on developer laptops (8 GB RAM).

**Impact of violations:**
- ❌ Prompt too large → LLM API rejection
- ⚠️ Composition too slow → Developer frustration
- ⚠️ Knowledge base too large → Slow startup, memory pressure

---

## Validation

### Automated Checks

**1. Prompt Size Validation (IMPLEMENTED ✅)**

Location: `prompt_runtime.py:156-160`

```python
if prompt_size > 200000:
    logger.warning(
        f"Prompt size ({prompt_size:,} chars) exceeds recommended limit (200,000 chars). "
        "This may cause LLM context window issues."
    )
```

**2. Knowledge Base Size Check (TO IMPLEMENT ❌)**

```python
# Add to prompt_runtime.py
def _validate_knowledge_size(self, filepath: Path):
    size_bytes = filepath.stat().st_size
    size_mb = size_bytes / (1024 * 1024)

    if size_mb > 5:
        logger.warning(
            f"Knowledge base {filepath.name} is large ({size_mb:.1f} MB). "
            "Consider splitting into smaller files for better performance."
        )
    elif size_mb > 1:
        logger.info(f"Knowledge base {filepath.name}: {size_mb:.1f} MB")
```

**3. Composition Time Tracking (TO IMPLEMENT ❌)**

```python
# Add to prompt_runtime.py
import time

def execute_task(self, agent_id, task_id, context):
    start_time = time.time()

    # ... existing composition logic ...

    composition_time = time.time() - start_time

    if composition_time > 0.5:
        logger.warning(
            f"Composition took {composition_time:.2f}s (> 500ms target). "
            "Check knowledge base sizes."
        )

    logger.debug(f"Composition time: {composition_time:.3f}s")
```

### Manual Checks

**Pre-Release Checklist:**

- [ ] Run full workflow (all 23 tasks) and measure total composition time (target: < 12s)
- [ ] Check largest knowledge base file size: `du -sh agency_os/*/knowledge/*.yaml | sort -h`
- [ ] Profile memory usage: `python3 -m memory_profiler prompt_runtime.py`
- [ ] Test with worst-case scenario (all knowledge loaded simultaneously)

### Performance Targets

| Metric | Target | Warning | Critical |
|---|---|---|---|
| **Prompt Size** | < 100k chars | 100-200k chars | > 200k chars |
| **Composition Time** | < 200ms | 200-500ms | > 500ms |
| **Knowledge Base** | < 500 KB | 500 KB - 5 MB | > 5 MB |
| **Memory Usage** | < 128 MB | 128-512 MB | > 512 MB |

---

## Failure Guidance

### If Prompt Size Exceeds 200k

**Root Causes:**
1. Too many knowledge bases loaded for single task
2. Knowledge bases contain redundant content
3. Task prompt itself is too verbose

**Resolution Steps:**

1. **Review `_knowledge_deps.yaml`:**
   ```bash
   # Check which knowledge bases are loaded for this task
   cat agency_os/XX_framework/agents/AGENT/_knowledge_deps.yaml
   ```
   - Remove unnecessary knowledge bases from `used_in_tasks`
   - Split required knowledge if it's optional

2. **Split Large Knowledge Bases:**
   ```bash
   # Find large files
   find agency_os/ -name "*.yaml" -size +1M -exec du -h {} \;

   # Split by category (example: FDG_dependencies.yaml)
   FDG_dependencies.yaml (2.5 MB) →
     ├── FDG_dependencies_web.yaml (800 KB)
     ├── FDG_dependencies_mobile.yaml (600 KB)
     └── FDG_dependencies_api.yaml (500 KB)
   ```

3. **Optimize Task Prompts:**
   - Remove examples if too verbose
   - Move detailed instructions to knowledge bases
   - Use references instead of inline content

### If Composition Time Exceeds 500ms

**Root Causes:**
1. Large YAML files (slow parsing)
2. Too many file I/O operations
3. Knowledge cache not working

**Resolution Steps:**

1. **Profile Composition:**
   ```python
   # Add to prompt_runtime.py for debugging
   import cProfile
   import pstats

   profiler = cProfile.Profile()
   profiler.enable()

   # ... execute_task logic ...

   profiler.disable()
   stats = pstats.Stats(profiler)
   stats.sort_stats('cumulative')
   stats.print_stats(10)  # Top 10 slowest operations
   ```

2. **Check Knowledge Cache:**
   - Verify `self.knowledge_cache` is being used
   - Confirm files aren't being re-parsed unnecessarily

3. **Reduce File Count:**
   - Consolidate small files (< 10 KB) if too many
   - Use fewer, larger knowledge bases

### If Knowledge Base Exceeds 5 MB

**Root Causes:**
1. Too much data in single file
2. Verbose formatting (excessive whitespace, comments)
3. Duplicated content across files

**Resolution Steps:**

1. **Split by Category:**
   ```yaml
   # Bad: Everything in one file
   TECH_STACK_PATTERNS.yaml (8 MB)

   # Good: Split by technology
   TECH_STACK_web_frontend.yaml (1.5 MB)
   TECH_STACK_web_backend.yaml (1.8 MB)
   TECH_STACK_mobile.yaml (1.2 MB)
   TECH_STACK_database.yaml (900 KB)
   ```

2. **Remove Redundancy:**
   - Check for duplicate entries
   - Extract common patterns to separate base file
   - Use YAML anchors for reuse

3. **Compress Formatting:**
   ```yaml
   # Verbose (takes more space)
   - constraint:
       type: "incompatibility"
       condition: "vercel AND websocket"
       reason: "Vercel does not support persistent WebSocket connections"

   # Compact (same information, less space)
   - {type: "incompatibility", condition: "vercel AND websocket", reason: "No WebSocket support"}
   ```

---

## Monitoring

### Metrics to Track

**Per Composition:**
- Prompt size (chars)
- Composition time (ms)
- Knowledge files loaded (count)
- Total knowledge size (KB)

**Aggregate (Weekly):**
- Average composition time
- P95 composition time
- Largest prompt size
- Slowest task

### Logging

**Log Format (JSON):**
```json
{
  "timestamp": "2025-11-13T10:30:00Z",
  "event": "composition_complete",
  "agent_id": "GENESIS_BLUEPRINT",
  "task_id": "01_select_core_modules",
  "prompt_size": 45678,
  "composition_time_ms": 234,
  "knowledge_files": 3,
  "knowledge_size_kb": 850,
  "status": "success"
}
```

**Log Location:** `~/.vibe_agency/logs/performance.log`

---

## Implementation Status

- [x] Prompt size validation (IMPLEMENTED in prompt_runtime.py)
- [ ] Composition time tracking (TO DO)
- [ ] Knowledge base size validation (TO DO)
- [ ] Memory profiling (TO DO)
- [ ] Performance logging (TO DO)

**Next Steps:**
1. Implement composition time tracking
2. Add knowledge base size checks
3. Set up performance logging
4. Create dashboard for metrics visualization (optional)

---

## References

- `docs/requirements/NFR_PERFORMANCE.yaml` - Full performance requirements
- `prompt_runtime.py:156-160` - Current size validation implementation
- Claude API Docs - Context window limits
