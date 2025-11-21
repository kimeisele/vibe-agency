# DOCUMENTATION CLEANUP PLAN
**Date:** 2025-11-21
**Status:** 🔥 EMERGENCY - Fix Documentation Contamination
**Branch:** `claude/fix-vibe-core-steward-01GaxFiZ5PSAzy9eTXogKyU3`

---

## EXECUTIVE SUMMARY

**Problem:** 30+ files reference non-existent documentation
**Impact:** New agents get confused, broken links everywhere
**Root Cause:** ARCHITECTURE_V2.md and SSOT.md deleted but references remain
**Solution:** Fix references + create missing foundational docs

---

## PRIORITIES

### P0 - Fix CLAUDE.md (CRITICAL - Operations Manual)
**File:** `CLAUDE.md`
**Problem:** References ARCHITECTURE_V2.md and SSOT.md (both non-existent)
**Impact:** Primary operations manual has broken links
**Fix:**
```diff
- **ARCHITECTURE_V2.md** — Conceptual model (the "should be")
- **SSOT.md** — Implementation decisions (the "is")
+ **docs/STRATEGY_SHIFT.md** — Theater → Engineering Era pivot
+ **docs/architecture/ARCHITECTURE_V3_OS.md** — Current OS architecture
+ **docs/architecture/ARCHITECTURE_MAP.md** — GAD-based architecture map
```

**Time:** 5 minutes
**Test:** Open CLAUDE.md, click all links, verify they exist

---

### P1 - Create OPERATOR_MANUAL.md (HIGH - Missing Foundation)
**File:** `docs/OPERATOR_MANUAL.md` (NEW)
**Problem:** STEWARD role never explicitly documented
**Impact:** Role confusion (Claude Code vs STEWARD vs Kernel)
**Content:**
```markdown
# OPERATOR MANUAL: The STEWARD Role

## What is STEWARD?

STEWARD is the ROLE that Claude Code assumes when operating vibe-agency.

It is NOT:
- ❌ A Python class
- ❌ An agent in vibe_core/
- ❌ A specialist

It IS:
- ✅ A role assignment (like "root" in Unix)
- ✅ The operator in Layer 7 (GAD-000)
- ✅ Claude Code when it runs ./bin/system-boot.sh

## The 8-Layer Stack

Layer 8: Human Intent → Natural language goals
Layer 7: OPERATOR (STEWARD) → Claude Code executing vibe-agency
Layer 6: Tools → vibe_core (Kernel, Agents, Specialists)
Layer 5: State → SQLite, Ledger, JSON
Layer 4: Data → Mission, Tasks, Decisions
Layer 3: Infrastructure → File system, Python runtime
Layer 2: Network → API calls (Anthropic, OpenAI)
Layer 1: Hardware → Compute, storage

## STEWARD's Responsibilities

1. Read mission context
2. Execute playbook workflows
3. Operate vibe_core tools
4. Delegate to specialists
5. Update state/session handoff
6. Report results to human
```

**Time:** 30 minutes
**Test:** New agent reads it, understands STEWARD role immediately

---

### P2 - Fix All Broken References (MEDIUM - Quality)
**Files:** 30+ across codebase
**Problem:** References to ARCHITECTURE_V2.md and SSOT.md
**Fix Strategy:**

1. **Find all references:**
```bash
grep -r "ARCHITECTURE_V2.md" . --exclude-dir=node_modules > /tmp/refs_v2.txt
grep -r "SSOT.md" . --exclude-dir=node_modules > /tmp/refs_ssot.txt
```

2. **Replace with correct targets:**
```bash
# ARCHITECTURE_V2.md → ARCHITECTURE_V3_OS.md
sed -i 's|ARCHITECTURE_V2\.md|docs/architecture/ARCHITECTURE_V3_OS.md|g' <file>

# SSOT.md → STRATEGY_SHIFT.md (closest equivalent)
sed -i 's|SSOT\.md|docs/STRATEGY_SHIFT.md|g' <file>
```

**Time:** 1 hour
**Test:** `grep -r "ARCHITECTURE_V2.md" .` returns 0 results

---

### P3 - Update INDEX.md Navigation (MEDIUM - Usability)
**File:** `INDEX.md`
**Problem:** May contain outdated links
**Fix:** Audit all links in INDEX.md, update to current docs

**Time:** 20 minutes
**Test:** Click every link in INDEX.md, all resolve

---

### P4 - Create ARCHITECTURE_LAYERS.md (LOW - Nice to Have)
**File:** `docs/architecture/ARCHITECTURE_LAYERS.md` (NEW)
**Purpose:** Visual diagram of 8-layer stack
**Content:**
- ASCII diagram of layers
- Description of each layer
- Examples of components in each layer
- Relationship to GAD-000 (Operator Inversion)

**Time:** 45 minutes
**Test:** New agent can explain the stack after reading

---

## EXECUTION SEQUENCE

### Phase 1: Critical Fixes (30 minutes)
```bash
# 1. Fix CLAUDE.md
vim CLAUDE.md  # Update references manually

# 2. Commit immediately
git add CLAUDE.md
git commit -m "fix: Update CLAUDE.md broken references (ARCHITECTURE_V2 → V3)"
```

### Phase 2: Create Missing Docs (1 hour)
```bash
# 3. Create OPERATOR_MANUAL.md
vim docs/OPERATOR_MANUAL.md

# 4. Commit
git add docs/OPERATOR_MANUAL.md
git commit -m "docs: Add OPERATOR_MANUAL.md - Define STEWARD role"
```

### Phase 3: Mass Reference Fix (1 hour)
```bash
# 5. Find and replace all broken references
grep -r "ARCHITECTURE_V2.md" . --exclude-dir=node_modules -l | \
  xargs sed -i 's|ARCHITECTURE_V2\.md|docs/architecture/ARCHITECTURE_V3_OS.md|g'

grep -r "SSOT.md" . --exclude-dir=node_modules -l | \
  xargs sed -i 's|SSOT\.md|docs/STRATEGY_SHIFT.md|g'

# 6. Verify
grep -r "ARCHITECTURE_V2.md" . --exclude-dir=node_modules  # Should be empty
grep -r "SSOT.md" . --exclude-dir=node_modules  # Should be empty

# 7. Commit
git add .
git commit -m "fix: Replace all broken doc references (V2→V3, SSOT→STRATEGY_SHIFT)"
```

### Phase 4: Verification (30 minutes)
```bash
# 8. Test all critical paths
cat CLAUDE.md  # Check references manually
cat INDEX.md  # Check navigation
./bin/system-boot.sh  # Verify boot still works

# 9. Push
git push -u origin claude/fix-vibe-core-steward-01GaxFiZ5PSAzy9eTXogKyU3
```

---

## SUCCESS CRITERIA

- [ ] CLAUDE.md has no broken references
- [ ] OPERATOR_MANUAL.md exists and defines STEWARD clearly
- [ ] `grep -r "ARCHITECTURE_V2.md"` returns 0 results
- [ ] `grep -r "SSOT.md"` returns 0 results
- [ ] INDEX.md navigation 100% working
- [ ] ./bin/system-boot.sh runs without errors
- [ ] New agent can onboard using docs alone

---

## ROLLBACK PLAN

If anything breaks:
```bash
# Rollback to current HEAD
git reset --hard HEAD

# Or rollback specific commits
git revert <commit-hash>
```

---

## RISK ASSESSMENT

**Low Risk:**
- Fixing references (non-functional changes)
- Creating new documentation (additive)

**Medium Risk:**
- Mass sed replacements (could affect code comments)
- Mitigation: Exclude code files, only target .md files

**High Risk:**
- None (this is documentation only)

---

## POST-CLEANUP VALIDATION

After cleanup, run these checks:

```bash
# 1. Documentation health check
find . -name "*.md" -type f | while read f; do
  echo "Checking $f..."
  # Extract markdown links
  grep -o '\[.*\](.*\.md)' "$f" | while read link; do
    target=$(echo "$link" | sed 's/.*(\(.*\))/\1/')
    if [ ! -f "$target" ]; then
      echo "  ❌ Broken link: $target"
    fi
  done
done

# 2. Boot sequence health
./bin/system-boot.sh

# 3. Critical docs exist
test -f CLAUDE.md && echo "✅ CLAUDE.md"
test -f INDEX.md && echo "✅ INDEX.md"
test -f docs/OPERATOR_MANUAL.md && echo "✅ OPERATOR_MANUAL.md"
test -f docs/architecture/ARCHITECTURE_V3_OS.md && echo "✅ ARCHITECTURE_V3_OS.md"
```

---

## TIMELINE

**Total Time:** ~3 hours
**Can be split across multiple sessions**

**Session 1 (30 min):** P0 - Fix CLAUDE.md
**Session 2 (1 hour):** P1 - Create OPERATOR_MANUAL.md
**Session 3 (1 hour):** P2 - Fix all broken references
**Session 4 (30 min):** Verification + push

---

## RELATED ISSUES

- ARCHITECTURE_V2.md deleted (when? why? git log should show)
- SSOT.md never existed (or deleted very early)
- Documentation drift identified in ARCHITECTURE_V3_OS.md
- STRATEGY_SHIFT.md explains Theater → Engineering Era pivot

---

**END OF CLEANUP PLAN**

*This plan fixes the documentation contamination systematically.*
