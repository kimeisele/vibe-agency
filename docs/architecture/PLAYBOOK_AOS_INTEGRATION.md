# PLAYBOOK AOS INTEGRATION - Lean MVP Plan

## PHASE 1: Structure Migration (30min)

### Move Playbook into AOS
```bash
# Create structure
mkdir -p agency_os/core_system/playbook/{tasks,templates}

# Move registry
mv docs/playbook/_registry.yaml agency_os/core_system/playbook/

# Keep docs/playbook for reference/vision docs only
# (ENTRY_POINTS.md, VISION.md stay as documentation)
```

### Create Task Playbooks (Based on VIBE_ALIGNER pattern)
```
tasks/
├── debug.md          # Tests failing → Fix
├── implement.md      # Code new feature
├── test.md           # Run test suite
├── plan.md           # Architecture/design
├── document.md       # Update docs
└── analyze.md        # Explore codebase
```

Each follows _composition.yaml pattern:
- Base mission
- Context injection points
- Success criteria
- Anti-slop rules

---

## PHASE 2: Context Loader (45min)

### agency_os/core_system/runtime/context_loader.py

**Purpose:** Conveyor Belt #1 - Collect ALL signals

```python
class ContextLoader:
    """Loads project context from multiple sources"""
    
    def load(self) -> Dict[str, Any]:
        return {
            'session': self._load_session_handoff(),
            'git': self._load_git_status(),
            'tests': self._load_test_status(),
            'manifest': self._load_project_manifest(),
            'environment': self._load_environment(),
        }
    
    def _load_session_handoff(self):
        # Read .session_handoff.json
        # Extract: phase, last_task, blockers, backlog
        
    def _load_git_status(self):
        # git status --porcelain
        # git log -3 --oneline
        # git branch --show-current
        
    def _load_test_status(self):
        # pytest --collect-only --quiet (fast!)
        # Check for .pytest_cache/v/cache/lastfailed
        
    def _load_project_manifest(self):
        # Read project_manifest.json
        # Extract: project_type, phase, focus_area
        
    def _load_environment(self):
        # Check: .venv exists, dependencies installed
        # Quick pre-flight checks
```

**Output:** Rich context dict (NO complex scoring yet!)

---

## PHASE 3: Playbook Engine (1h)

### agency_os/core_system/runtime/playbook_engine.py

**Purpose:** Conveyor Belt #2 - Route to task

```python
class PlaybookEngine:
    """Routes user intent + context → task playbook"""
    
    def route(self, user_input: str, context: Dict) -> PlaybookRoute:
        # TIER 1: Explicit user intent
        if explicit_match := self._match_keywords(user_input):
            return explicit_match
        
        # TIER 2: Context inference (SIMPLE!)
        if context_match := self._infer_from_context(context):
            return context_match
        
        # TIER 3: Inspire mode
        return self._suggest_options(context)
    
    def _match_keywords(self, user_input):
        # Match against _registry.yaml intent_patterns
        # Return first match (simple!)
        
    def _infer_from_context(self, context):
        # LEAN RULES (not 5-tier scoring!):
        # - IF tests_failing: → "debug"
        # - IF uncommitted_changes + no_failures: → "test"
        # - IF backlog_item: → "implement"
        # - IF phase=planning: → "plan"
        # Simple if/else, no ML!
        
    def _suggest_options(self, context):
        # Show 3-5 relevant tasks based on context
        # Return as "inspiration menu"
```

**Key:** LEAN logic, not enterprise scoring!

---

## PHASE 4: Prompt Composer (45min)

### agency_os/core_system/runtime/prompt_composer.py

**Purpose:** Conveyor Belt #3 - Compose final prompt

```python
class PromptComposer:
    """Composes task playbook + context → enriched prompt"""
    
    def compose(self, task: str, context: Dict) -> str:
        # Load base task playbook
        task_md = self._load_task(task)
        
        # Inject context (like VIBE_ALIGNER does)
        enriched = self._inject_context(task_md, context)
        
        # Add STEWARD boot prompt
        final = self._add_boot_prompt(enriched)
        
        return final
    
    def _inject_context(self, task_md, context):
        # Replace placeholders:
        # ${session.phase} → "CODING"
        # ${git.uncommitted} → "5 files"
        # ${tests.failing} → "test_x, test_y"
        
        # Add context section:
        """
        ## CURRENT CONTEXT
        Phase: ${session.phase}
        Last: ${session.last_task}
        Tests: ${tests.status}
        Git: ${git.uncommitted} uncommitted
        """
```

**Output:** Ready-to-execute STEWARD prompt with full context!

---

## PHASE 5: Boot Sequence (30min)

### agency_os/core_system/runtime/boot_sequence.py

**Purpose:** Orchestrate the conveyor belt

```python
class BootSequence:
    """Main entry point for system-boot.sh → vibe-cli boot"""
    
    def run(self, user_input: Optional[str] = None):
        # Conveyor Belt 1: Context
        context = ContextLoader().load()
        
        # Conveyor Belt 2: Route
        route = PlaybookEngine().route(user_input or "", context)
        
        # Conveyor Belt 3: Compose
        prompt = PromptComposer().compose(route.task, context)
        
        # Output to STEWARD
        self._display_dashboard(context, route)
        self._output_prompt(prompt)
    
    def _display_dashboard(self, context, route):
        # Pretty print:
        # - System status
        # - Recommended task
        # - Context highlights
        
    def _output_prompt(self, prompt):
        # Output enriched prompt for Claude Code STEWARD
        # Ready to execute!
```

---

## PHASE 6: Integration (30min)

### Update vibe-cli

```python
# vibe-cli (main script)
elif mode == "boot":
    from agency_os.runtime.boot_sequence import BootSequence
    BootSequence().run(user_input=args.input)
```

### Update system-boot.sh

```bash
# After pre-flight checks:
python3 ./vibe-cli boot "$@"
```

**DONE!** No breaking changes, lean integration.

---

## SUCCESS CRITERIA

✅ Playbook is part of AOS (agency_os/core_system/playbook/)
✅ Context flows from system → STEWARD (no information loss)
✅ User can: explicit intent OR context-driven OR inspiration mode
✅ Boot sequence < 3 seconds
✅ Follows VIBE_ALIGNER composition patterns
✅ No enterprise bloat (simple if/else routing, not ML)

---

## TIMELINE

- Phase 1-6: ~4 hours
- Testing: 1 hour
- Documentation: 30min
- **Total: ~5.5 hours (one afternoon!)**

---

## ANTI-BLOAT CHECKLIST

❌ NO 5-tier confidence scoring
❌ NO new complex classes (reuse prompt_registry patterns)
❌ NO 3D matrix abstractions (GAD/LAD/VAD stay conceptual)
❌ NO ML/embeddings for MVP
✅ YES simple keyword + context matching
✅ YES composition patterns from VIBE_ALIGNER
✅ YES lean Python (~300 LOC total for 4 new files)
✅ YES testable, clear, maintainable


---

## CRITICAL ADDITION: THE 1% - FEEDBACK LOOP & STATE MANAGEMENT

**Credit:** Expert review identified the missing closed-loop mechanism.

### The Missing Piece: Bi-Directional Data Flow

The plan above focuses on **INPUT** (Context → Route → Compose → Output).
But a real AOS needs **FEEDBACK** (STEWARD executes → Updates State → Next boot sees changes).

### Handoff Contract (STDOUT → STEWARD)

**BootSequence._output_prompt():**
```python
def _output_prompt(self, prompt: str):
    """Output enriched prompt to STEWARD via STDOUT."""
    print("=" * 64)
    print("🎯 STEWARD OPERATIONAL PROMPT")
    print("=" * 64)
    print(prompt)
    print()
    print("📋 AFTER EXECUTION:")
    print("1. Update .session_handoff.json")
    print("2. Commit changes to git")
    print("3. Next boot auto-detects your changes")
    print("=" * 64)
```

### Error Handling (Robust Fallbacks)

**All ContextLoader methods must have try/except:**
- Missing `.session_handoff.json` → Return safe defaults (phase=PLANNING)
- Git command fails → Return `{status: 'git_unavailable'}`
- Pytest fails → Return `{status: 'pytest_not_available'}`

**No crashes on missing context sources!**

### Updated Success Criteria

✅ **STEWARD output updates state for next boot (feedback loop closed)**
✅ **Robust error handling (missing files → sensible defaults)**
✅ **Clear handoff contract (STDOUT with instructions)**

### Updated Timeline

- Phase 1-6: ~4 hours
- **Error Handling: +1 hour**
- **Handoff Contract: +30min**
- Testing: 1 hour
- **Total: ~6.5 hours**

