# Boot Sequence Kernel Redesign

**Status:** PROPOSAL - Immediate Implementation  
**Date:** 2025-11-18  
**Priority:** P0 (User Experience)  
**Related:** Playbook AOS Integration

---

## Problem

Current boot output:
- **WALL OF TEXT** - agents overwhelmed
- System prompt buried after 100+ lines
- No visual hierarchy/scanning support
- Context isn't actionable
- Repeats same info multiple times

**Effect:** Agents don't read it. Playbook routing is invisible.

---

## Solution: Kernel-Style Boot

Take inspiration from Linux kernel boot:
- **Clear phases** with status indicators
- **Visual scan-ability** (symbols, spacing)
- **One actionable task** front and center
- **Context only if needed**
- **No repetition**

---

## Proposed Output Format

```
╔════════════════════════════════════════════════════════════╗
║                    VIBE AGENCY STEWARD                    ║
║                      System Boot v1.1                      ║
╚════════════════════════════════════════════════════════════╝

[BOOT SEQUENCE]

  [✓] Integrity verified
  [✓] Context loaded (git, tests, manifest, env)
  [✓] Route detected: TASK=debug REASON=1_test_failing
  [✓] Playbook composed
  
[SYSTEM STATUS]

  Git:     ✓ clean (feature/playbook-aos-integration)
  Tests:   ⚠ 1 failing (E2E - known issue)
  Sync:    ✓ up to date
  Env:     ✓ ready

[NEXT ACTION]

  TASK:    DEBUG - Fix failing tests
  REASON:  1 test failing (E2E fixture schema)
  STATUS:  READY TO EXECUTE

[EXECUTION PROTOCOL]

  1. READ task (DEBUG playbook)
  2. IDENTIFY failing test
  3. FIX with minimal changes
  4. VERIFY (run tests, confirm green)
  5. COMMIT with clear message
  6. UPDATE .session_handoff.json
  7. REPORT completion

[SYSTEM PROMPT]

  You are STEWARD...
  [rest of prompt]

════════════════════════════════════════════════════════════

🚀 Ready to execute. What's your intent?
```

---

## Key Changes

### 1. **Boot Phases (Clear, Scannable)**
```
[✓] Phase Name
  - Compact status indicators
  - One line per major step
  - No redundant detail
```

### 2. **System Status (Concise)**
```
[SYSTEM STATUS]
  Git:   ✓ clean (branch)
  Tests: ⚠ 1 failing (reason)
  Sync:  ✓ up to date
  Env:   ✓ ready
```

No duplication, just facts.

### 3. **Next Action (Highlighted)**
```
[NEXT ACTION]
  TASK:    ACTION_NAME
  REASON:  Why this task (from context)
  STATUS:  Ready / Blocked / Waiting
```

This is the **actionable insight** - agents immediately know what to do.

### 4. **Execution Protocol (Clear Steps)**
```
[EXECUTION PROTOCOL]
  1. READ task
  2. PLAN steps
  3. EXECUTE
  4. VERIFY
  5. COMMIT
  6. HANDOFF
  7. REPORT
```

Agents follow this, not vague guidance.

### 5. **System Prompt (Moved Down)**
```
[SYSTEM PROMPT]
  You are STEWARD...
```

Still there, but not drowning the output.

---

## Implementation

### File Changes
- `agency_os/core_system/runtime/boot_sequence.py` - redesign `_display_dashboard()`
- New method: `_format_kernel_boot()` - compose output

### Output Flow

```python
def run(self, user_input=None):
    # Pre-checks
    git_status = self._check_uncommitted_changes()
    if git_status['has_uncommitted']:
        self._display_commit_warning(git_status)
        return
    
    # Load context + route
    context = self.context_loader.load()
    route = self.playbook_engine.route(user_input or "", context)
    
    # KERNEL-STYLE OUTPUT
    self._display_kernel_boot(context, route)
    
    # System prompt
    system_prompt = self._get_system_prompt(route)
    task_prompt = self.prompt_composer.compose(route.task, context)
    
    print(system_prompt)
    print("\n" + task_prompt)
```

### Display Methods

```python
def _display_kernel_boot(self, context, route):
    """Kernel-style boot output"""
    print(self._format_header())
    print(self._format_boot_phases(context, route))
    print(self._format_system_status(context))
    print(self._format_next_action(route, context))
    print(self._format_execution_protocol())

def _format_header():
    return """
╔════════════════════════════════════════════════════════════╗
║                    VIBE AGENCY STEWARD                    ║
║                      System Boot v1.1                      ║
╚════════════════════════════════════════════════════════════╝
"""

def _format_boot_phases(context, route):
    """Show boot progress as phases"""
    return """
[BOOT SEQUENCE]
  [✓] Integrity verified
  [✓] Context loaded
  [✓] Route detected
  [✓] Playbook composed
"""

def _format_system_status(context):
    """Concise status display"""
    git = context.get('git', {})
    tests = context.get('tests', {})
    sync = self._check_git_sync()
    env = context.get('environment', {})
    
    return f"""
[SYSTEM STATUS]
  Git:   {'✓' if git.get('uncommitted', 0) == 0 else '⚠'} {git.get('branch', 'unknown')}
  Tests: {'✓' if tests.get('failing_count', 0) == 0 else '⚠'} {tests.get('failing_count', 0)} failing
  Sync:  {'✓' if not sync.get('behind') else '⚠'} {sync.get('commits_behind', 0)} behind
  Env:   {'✓' if env.get('status') == 'ready' else '⚠'} {env.get('status')}
"""

def _format_next_action(route, context):
    """Highlight the actionable task"""
    return f"""
[NEXT ACTION]
  TASK:    {route.task.upper()}
  REASON:  {route.source}
  STATUS:  READY TO EXECUTE
"""

def _format_execution_protocol():
    return """
[EXECUTION PROTOCOL]
  1. READ task completely
  2. PLAN steps
  3. EXECUTE changes
  4. VERIFY with tests
  5. COMMIT with message
  6. UPDATE .session_handoff.json
  7. REPORT completion
"""
```

---

## Visual Hierarchy

**Immediately visible (no scrolling):**
1. Header - what system this is
2. Boot phases - what completed
3. System status - is system healthy?
4. **NEXT ACTION** - what to do NOW

**Below fold (if agent wants detail):**
- Execution protocol
- System prompt
- Task playbook

---

## Effectiveness Metrics

✅ Agent can understand task in **< 5 seconds**  
✅ No information loss (all data still present)  
✅ Clear visual scanning (symbols, sections)  
✅ One actionable task highlighted  
✅ No repetition  
✅ Kernel-style professionalism  

---

## Implementation Checklist

- [ ] Redesign `_display_kernel_boot()` method
- [ ] Add `_format_*` helper methods
- [ ] Test output readability
- [ ] Update boot output in `run()`
- [ ] Remove old `_display_dashboard()`
- [ ] Verify playbook routing is visible
- [ ] Update CLAUDE.md with new boot format
- [ ] Commit as "refactor: Kernel-style boot redesign"

---

## Related

- **Current boot output:** Unclear, verbose, not actionable
- **Playbook integration:** Invisible in current output
- **STEWARD effectiveness:** Blocked by unclear instructions
- **User experience:** Needs kernel-style clarity

---

## Next Steps

Implement immediately to fix UX:
1. Redesign output format
2. Test with fresh boot
3. Verify playbook routing visible
4. Make agents actually understand what to do

This will make STEWARD:
- More proactive (clear what to do)
- More effective (no confusion)
- More professional (kernel aesthetic)
