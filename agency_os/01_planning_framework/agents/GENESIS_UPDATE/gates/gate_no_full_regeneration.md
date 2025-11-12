# Gate: No Full File Regeneration

**GATE_ID:** gate_no_full_regeneration
**SEVERITY:** CRITICAL
**PURPOSE:** Prevent full file regeneration to avoid architecture drift

---

## VALIDATION RULE

**CRITICAL:** You MUST output DIFF PATCHES only, NOT full files.

### What This Gate Checks:

1. **Diff Format:** All changes must be in unified diff format (`--- a/file` / `+++ b/file`)
2. **Context Lines:** Changes must include context lines (3 before/after)
3. **No Full Files:** No output should contain an entire file's contents
4. **Surgical Changes:** Only changed lines plus context should be included

---

## PASS CRITERIA

✅ All patches use unified diff format
✅ Each patch has `---` and `+++` headers
✅ Context lines are present
✅ No patch contains more than 50% of a file's lines

---

## FAIL CRITERIA

❌ Full file contents are output
❌ No diff headers present
❌ Missing context lines
❌ Changes represent more than 50% of file

---

## WHY THIS MATTERS

Full file regeneration causes:
- **Architecture Drift:** LLM might make different decisions than original
- **Lost Context:** Existing decisions get overwritten
- **Merge Conflicts:** Hard to review and integrate changes
- **Inconsistency:** Can't guarantee compatibility with existing code

**Diffs force surgical, explicit, reviewable changes.**
