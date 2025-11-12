# Gate: Diff Format Valid

**GATE_ID:** gate_diff_format_valid
**SEVERITY:** HIGH
**PURPOSE:** Ensure all diffs follow unified diff format

---

## VALIDATION RULE

All diff patches must follow the standard unified diff format.

### What This Gate Checks:

1. **Header Lines:** Each diff must start with `--- a/filename` and `+++ b/filename`
2. **Hunk Headers:** Change blocks must have `@@ -line,count +line,count @@` headers
3. **Line Prefixes:** Lines must be prefixed with ` ` (context), `+` (add), or `-` (remove)
4. **Context Lines:** Must include 3 lines of context before and after changes

---

## UNIFIED DIFF FORMAT

```diff
--- a/path/to/file.py
+++ b/path/to/file.py
@@ -10,7 +10,8 @@ def function_name():
     context_line_1
     context_line_2
     context_line_3
-    old_line_to_remove
+    new_line_to_add
+    another_new_line
     context_line_4
     context_line_5
     context_line_6
```

---

## VALIDATION CHECKLIST

✅ **Header Check:**
   - Starts with `--- a/`
   - Followed by `+++ b/`
   - File paths match

✅ **Hunk Check:**
   - Has `@@` markers
   - Line numbers present
   - Format: `@@ -old_start,old_count +new_start,new_count @@`

✅ **Line Prefix Check:**
   - Context lines start with ` ` (space)
   - Removed lines start with `-`
   - Added lines start with `+`

✅ **Context Check:**
   - At least 3 context lines before changes
   - At least 3 context lines after changes

---

## PASS CRITERIA

✅ All diffs have proper headers
✅ All hunks are correctly formatted
✅ Line prefixes are correct
✅ Context lines are present

---

## FAIL CRITERIA

❌ Missing headers
❌ Malformed hunk markers
❌ Incorrect line prefixes
❌ No context lines
❌ Full file output instead of diff

---

## WHY THIS MATTERS

Valid diff format enables:
- **Automated Application:** `patch` command can apply changes
- **Version Control:** Git can merge changes correctly
- **Code Review:** Humans can understand what changed
- **Reversibility:** Changes can be undone cleanly
