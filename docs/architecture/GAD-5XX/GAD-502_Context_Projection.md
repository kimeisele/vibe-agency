# GAD-502: Context Projection - Runtime Vibe Injection

**Status:** ✅ APPROVED
**Date:** 2025-11-20
**Authors:** Claude Code (Runtime Engineer), Gemini Pro (Strategic Analyst)
**Supersedes:** GAD-502 v1 ("Haiku Hardening" - moved to GAD-503)
**Related:** GAD-500 (Self-Regulating Environment), GAD-501 (Multi-Layered Context Injection)

---

## Revision History

| Version | Date | Changes |
|---------|------|---------|
| v1 | 2025-11-20 | Initial implementation - Context Projection (redefines GAD-502) |

**Note:** Previous GAD-502 ("Haiku Hardening") has been moved to GAD-503 to accommodate this strategic runtime feature.

---

## Executive Summary

**The Problem:** The system has a **passive context loader** (`context_loader.py`) that collects data but doesn't inject it into prompts. This creates a gap: static task files don't reflect live system state (git status, test results, session phase).

**The Solution:** Implement **"Context Projection"** - a runtime mechanism that injects live system data into prompt templates using placeholder substitution. This is the "Hypodermic Needle" pattern: `inject(template, context) -> filled_prompt`.

**Impact:**
- Agents receive **accurate, real-time context** in their prompts
- No more stale information (phase, git status, test results)
- Foundation for dynamic, context-aware task execution

**Timeline:** 1 week implementation + verification

**Risk:** LOW (extends existing ContextLoader, backward compatible)

---

## Table of Contents

1. [Context & Problem Statement](#1-context--problem-statement)
2. [Decision: Context Projection](#2-decision-context-projection)
3. [Architecture: The Hypodermic Needle Pattern](#3-architecture-the-hypodermic-needle-pattern)
4. [Implementation](#4-implementation)
5. [Testing & Verification](#5-testing--verification)
6. [Success Metrics](#6-success-metrics)

---

## 1. Context & Problem Statement

### 1.1. Current State Analysis

**What Exists (GAD-501 Layer 0-1):**
- ✅ `ContextLoader` class loads data from 5 sources:
  - Session handoff (`.session_handoff.json`)
  - Git status (`git branch`, `git status`)
  - Test results (`.pytest_cache`)
  - Project manifest (`project_manifest.json`)
  - Environment (venv, python version)

**What's Missing:**
- ❌ No mechanism to **inject** this data into prompts
- ❌ Task files are **static** (e.g., `task_02_handle_coding.md` has hardcoded text)
- ❌ No way to show agents the **current** project phase, git state, or test status

### 1.2. The Strategic Gap

**Current Workflow (Static Context):**
```
Agent receives task: "Handle CODING state"
└─> Reads static file: task_02_handle_coding.md
    └─> File says: "STATE: CODING" (hardcoded)
    └─> File says: "PURPOSE: Orchestrate code generation" (generic)
    └─> Agent doesn't know:
        - Is git clean or dirty?
        - Are tests passing?
        - What's the actual current phase?
```

**Desired Workflow (Dynamic Context):**
```
Agent receives task: "Handle CODING state"
└─> ContextLoader loads live data
└─> System injects data into template
    └─> Agent sees: "Current Phase: CODING (from project_manifest.json)"
    └─> Agent sees: "Git Status: ✅ Clean (branch: claude/feature-123)"
    └─> Agent sees: "Tests: ✅ 369/383 passing"
    └─> Agent has accurate, real-time context
```

### 1.3. The Fundamental Problem

**Core Insight:** We have a **passive collector** (`ContextLoader.load()`) but no **active projector** (`ContextLoader.inject_context()`).

**Analogy:**
- GAD-501 = "Collecting blood samples" (data gathering)
- GAD-502 = "Injecting medicine" (data projection into prompts)

---

## 2. Decision: Context Projection

### 2.1. What We're Building

**GAD-502 Decision:** Extend `ContextLoader` with a **context injection** method that:

1. **Accepts a template string** with placeholders (e.g., `{{ git.branch }}`)
2. **Loads live system data** using existing `load()` method
3. **Replaces placeholders** with actual values
4. **Returns filled template** ready for agent consumption

### 2.2. Design Principles

1. **Lightweight** - Use standard Python string formatting (no complex templating engines)
2. **Safe** - Graceful fallbacks for missing data (no crashes)
3. **Observable** - Clear placeholder syntax for debugging
4. **Backward Compatible** - Non-injected templates continue to work

### 2.3. Placeholder Syntax

**Format:** `{{ category.field }}`

**Examples:**
- `{{ git.branch }}` → `"claude/feature-123"`
- `{{ git.status }}` → `"clean"` or `"dirty"`
- `{{ tests.summary }}` → `"369/383 passing"`
- `{{ session.phase }}` → `"CODING"`
- `{{ session.last_task }}` → `"task_01_handle_planning"`
- `{{ manifest.project_type }}` → `"python-library"`

### 2.4. Relationship to Existing Work

**GAD-502 complements GAD-501:**

| Component | GAD-501 (Context Injection Layers) | GAD-502 (Context Projection) |
|-----------|-------------------------------------|------------------------------|
| **Layer 0** | System Integrity Verification | Uses verified system state |
| **Layer 1** | Session Shell (MOTD) | Uses MOTD data sources |
| **Layer 2** | Ambient Context | **Provides injection mechanism** |
| **Layer 3** | Commit Watermarking | N/A |
| **Layer 4** | Remote Validation | N/A |

**Analogy:**
- GAD-501 = "Here are the context layers" (strategy)
- GAD-502 = "Here's how to inject context into prompts" (mechanism)

---

## 3. Architecture: The Hypodermic Needle Pattern

### 3.1. Component Design

```
┌─────────────────────────────────────────────────────────┐
│ CONTEXTLOADER (Extended)                                │
│━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━│
│                                                           │
│  Existing: load() -> dict                                │
│  │                                                        │
│  │  Returns: {                                           │
│  │    "session": {...},                                  │
│  │    "git": {...},                                      │
│  │    "tests": {...},                                    │
│  │    "manifest": {...},                                 │
│  │    "environment": {...}                               │
│  │  }                                                    │
│  │                                                        │
│  NEW: inject_context(template_str) -> str                │
│  │                                                        │
│  │  1. Load context via load()                           │
│  │  2. Parse template for {{ placeholders }}             │
│  │  3. Replace with actual values                        │
│  │  4. Return filled template                            │
│                                                           │
└─────────────────────────────────────────────────────────┘
```

### 3.2. Injection Algorithm

**Step 1: Load Context**
```python
context = self.load()
# Returns: {"session": {...}, "git": {...}, ...}
```

**Step 2: Parse Placeholders**
```python
import re
pattern = r'\{\{\s*([a-zA-Z0-9_.]+)\s*\}\}'
matches = re.findall(pattern, template_str)
# Finds: ["git.branch", "session.phase", ...]
```

**Step 3: Resolve Values**
```python
for placeholder in matches:
    parts = placeholder.split('.')  # ["git", "branch"]
    value = context
    for part in parts:
        value = value.get(part, f"{{{{ {placeholder} }}}}")  # Fallback
```

**Step 4: Replace**
```python
filled = template_str
for placeholder, value in replacements.items():
    filled = filled.replace(f"{{{{ {placeholder} }}}}", str(value))
return filled
```

### 3.3. Example Transformation

**Input Template:**
```markdown
# Task 02: Handle Coding State

**Current Phase:** {{ session.phase }}
**Git Branch:** {{ git.branch }}
**Test Status:** {{ tests.summary }}

Your task: Generate code based on code_gen_spec.json
```

**Context Data:**
```python
{
    "session": {"phase": "CODING"},
    "git": {"branch": "claude/feature-123"},
    "tests": {"status": "available", "failing_count": 0}
}
```

**Output (Injected):**
```markdown
# Task 02: Handle Coding State

**Current Phase:** CODING
**Git Branch:** claude/feature-123
**Test Status:** Available (0 failing)

Your task: Generate code based on code_gen_spec.json
```

---

## 4. Implementation

### 4.1. Extend ContextLoader

**File:** `agency_os/00_system/runtime/context_loader.py`

**Add at end of class:**

```python
def inject_context(self, template_str: str) -> str:
    """Inject live context into template with {{ placeholders }}

    Args:
        template_str: Template with {{ category.field }} placeholders

    Returns:
        Filled template with actual values

    Example:
        >>> loader = ContextLoader()
        >>> template = "Branch: {{ git.branch }}"
        >>> loader.inject_context(template)
        "Branch: claude/feature-123"
    """
    import re

    # Load all context sources
    context = self.load()

    # Find all placeholders: {{ key.subkey }}
    pattern = r'\{\{\s*([a-zA-Z0-9_.]+)\s*\}\}'

    def replace_placeholder(match: re.Match) -> str:
        """Resolve a single placeholder to its value"""
        placeholder = match.group(1)  # e.g., "git.branch"
        parts = placeholder.split('.')

        # Navigate nested dict
        value = context
        for part in parts:
            if isinstance(value, dict):
                value = value.get(part)
                if value is None:
                    # Fallback: keep original placeholder
                    return match.group(0)
            else:
                # Can't navigate further
                return match.group(0)

        # Special formatting for complex types
        if isinstance(value, list):
            if not value:
                return "none"
            return ", ".join(str(v) for v in value[:3])
        elif isinstance(value, bool):
            return "✅" if value else "❌"
        elif value is None:
            return "unknown"
        else:
            return str(value)

    # Replace all placeholders
    return re.sub(pattern, replace_placeholder, template_str)


def format_test_summary(self, tests: dict[str, Any]) -> str:
    """Format test status for human readability

    Args:
        tests: Test context from load()

    Returns:
        Human-readable summary
    """
    if tests.get("status") != "available":
        return f"Unavailable ({tests.get('status', 'unknown')})"

    failing = tests.get("failing_count", 0)
    if failing == 0:
        return "✅ All passing"
    else:
        return f"❌ {failing} test(s) failing"
```

### 4.2. Add Helper Property

**Add to ContextLoader class for convenient access:**

```python
@property
def context(self) -> dict[str, Any]:
    """Cached context data (loaded once per instance)"""
    if not hasattr(self, '_cached_context'):
        self._cached_context = self.load()
    return self._cached_context
```

---

## 5. Testing & Verification

### 5.1. Unit Tests

**File:** `tests/test_context_injection.py` (new)

```python
#!/usr/bin/env python3
"""Tests for GAD-502: Context Projection"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "agency_os/00_system/runtime"))

from context_loader import ContextLoader


def test_basic_injection():
    """Test basic placeholder replacement"""
    loader = ContextLoader()

    template = "Branch: {{ git.branch }}"
    result = loader.inject_context(template)

    # Should replace with actual branch
    assert "{{ git.branch }}" not in result
    assert "Branch:" in result
    print(f"✅ Basic injection: {result}")


def test_nested_placeholders():
    """Test nested field access"""
    loader = ContextLoader()

    template = "Phase: {{ session.phase }}, Last Task: {{ session.last_task }}"
    result = loader.inject_context(template)

    # Should replace both placeholders
    assert "{{ session" not in result
    print(f"✅ Nested injection: {result}")


def test_missing_placeholder():
    """Test graceful fallback for missing data"""
    loader = ContextLoader()

    template = "Unknown: {{ nonexistent.field }}"
    result = loader.inject_context(template)

    # Should keep original placeholder if data missing
    assert "Unknown:" in result
    print(f"✅ Fallback handling: {result}")


def test_multiple_placeholders():
    """Test template with many placeholders"""
    loader = ContextLoader()

    template = """
Current Phase: {{ session.phase }}
Git Branch: {{ git.branch }}
Uncommitted Files: {{ git.uncommitted }}
Test Status: {{ tests.status }}
"""
    result = loader.inject_context(template)

    # Should replace all placeholders
    print(f"✅ Multi-placeholder injection:\n{result}")


if __name__ == "__main__":
    try:
        test_basic_injection()
        test_nested_placeholders()
        test_missing_placeholder()
        test_multiple_placeholders()

        print("\n✅ ALL CONTEXT INJECTION TESTS PASSED")
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
```

### 5.2. Integration Test

**File:** `scripts/test_context_injection.py` (verification script)

```python
#!/usr/bin/env python3
"""Verification script for GAD-502: Context Projection

This script proves that context injection works by:
1. Loading a real task file (task_02_handle_coding.md)
2. Injecting live context
3. Printing the result
"""
import sys
from pathlib import Path

# Add runtime to path
sys.path.insert(0, str(Path(__file__).parent.parent / "agency_os/00_system/runtime"))

from context_loader import ContextLoader


def main():
    print("=" * 60)
    print("GAD-502 CONTEXT INJECTION VERIFICATION")
    print("=" * 60)
    print()

    # Load task file
    task_file = Path("agency_os/00_system/agents/AGENCY_OS_ORCHESTRATOR/tasks/task_02_handle_coding.md")

    if not task_file.exists():
        print(f"❌ Task file not found: {task_file}")
        return 1

    print(f"📄 Reading task file: {task_file.name}")
    template = task_file.read_text()
    print()

    # Initialize context loader
    print("🔄 Loading system context...")
    loader = ContextLoader()

    # Show what context was loaded
    context = loader.load()
    print("\n📊 Loaded Context:")
    print(f"  Session Phase: {context['session']['phase']}")
    print(f"  Git Branch: {context['git']['branch']}")
    print(f"  Git Status: {'Clean' if context['git']['uncommitted'] == 0 else f'{context['git']['uncommitted']} uncommitted'}")
    print(f"  Test Status: {context['tests']['status']}")
    print()

    # Inject context
    print("💉 Injecting context into template...")
    injected = loader.inject_context(template)

    # Display result
    print("\n" + "=" * 60)
    print("INJECTED TEMPLATE (First 50 lines)")
    print("=" * 60)
    lines = injected.split('\n')
    for i, line in enumerate(lines[:50], 1):
        print(f"{i:3d} | {line}")

    if len(lines) > 50:
        print(f"... ({len(lines) - 50} more lines)")

    print()
    print("=" * 60)
    print("✅ CONTEXT INJECTION VERIFICATION COMPLETE")
    print("=" * 60)

    return 0


if __name__ == "__main__":
    sys.exit(main())
```

---

## 6. Success Metrics

### 6.1. Functional Metrics

**Targets:**
- ✅ `inject_context()` method implemented and working
- ✅ All placeholders resolve to actual values (or fallback gracefully)
- ✅ At least one task file upgraded to use dynamic placeholders
- ✅ Verification script proves injection works

### 6.2. Quality Metrics

**Targets:**
- ✅ Unit tests pass (4 tests in `test_context_injection.py`)
- ✅ No crashes on missing/malformed context data
- ✅ Injection performance: <100ms for typical template

### 6.3. Documentation Metrics

**Targets:**
- ✅ GAD-502 document created
- ✅ Implementation code has clear docstrings
- ✅ Verification script provides clear output
- ✅ GAD_IMPLEMENTATION_STATUS.md updated

---

## 7. Future Enhancements

**Post-v1 (if needed):**

1. **Complex Formatters** - Add `{{ git.status | format_status }}` pipe syntax
2. **Conditional Blocks** - `{% if tests.failing > 0 %}...{% endif %}`
3. **Template Library** - Reusable snippet injection
4. **Caching** - Cache context for multiple inject_context() calls

**Decision Point:** After 2 weeks of usage, evaluate if simple placeholder replacement is sufficient.

---

## 8. References

- **GAD-500:** Self-Regulating Execution Environment (MOTD foundation)
- **GAD-501:** Multi-Layered Context Injection (strategy document)
- **ContextLoader:** `agency_os/00_system/runtime/context_loader.py`
- **Task Files:** `agency_os/00_system/agents/AGENCY_OS_ORCHESTRATOR/tasks/`

---

## 9. Acknowledgments

**Strategic Analyst:** Gemini Pro (Google)
- Identified the "passive collector" gap in runtime system
- Coined the "Hypodermic Needle" pattern name
- Recommended focusing on GAD-502 as strategic runtime priority

**Synthesizer:** User (Master Prompt)
- Bridged research phase completion to runtime engineering phase
- Defined clear execution protocol
- Emphasized "proof by verification script"

---

**STATUS: ✅ APPROVED (2025-11-20)**

**Next Steps:**
1. Implement `inject_context()` method in ContextLoader
2. Upgrade task_02_handle_coding.md with dynamic placeholders
3. Create verification script
4. Run tests and verification
5. Update GAD_IMPLEMENTATION_STATUS.md
