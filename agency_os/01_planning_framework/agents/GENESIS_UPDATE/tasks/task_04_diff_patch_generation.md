# Task 04: Diff Patch Generation

**TASK_ID:** task_04_diff_patch_generation
**PHASE:** PHASE 4
**PURPOSE:** Output surgical, minimal changes (NOT full files)

---

## GOAL

Generate unified diff patches that represent the minimal changes needed to implement the requested modification.

---

## DIFF FORMAT: UNIFIED DIFF

```diff
--- a/architecture.json
+++ b/architecture.json
@@ -45,6 +45,15 @@
     "extensions": [
       {
         "name": "blog_posts",
         ...
       },
+      {
+        "name": "comments",
+        "purpose": "Allow users to comment on blog posts",
+        "implements_feature": "feature_comments",
+        "uses_core": ["storage", "validation", "config"],
+        "external_deps": [],
+        "api": ["add_comment", "get_comments", "delete_comment"],
+        "file_path": "extensions/comments.py"
+      }
     ]
```

---

## DIFF GENERATION RULES

1. **Only changed lines:** Don't output unchanged lines (except context)
2. **Show context:** Include 3 lines before/after change for clarity
3. **One diff per file:** Separate diffs for each modified file
4. **Explain each diff:** Add comment explaining WHY this change

---

## EXAMPLE: ADDING COMMENTS FEATURE

**Diff 1: architecture.json**
```diff
--- a/architecture.json
+++ b/architecture.json
@@ -45,6 +45,15 @@
     ],
     "extensions": [
       ...existing extensions...,
+      {
+        "name": "comments",
+        "purpose": "User comments on blog posts",
+        "uses_core": ["storage", "validation"],
+        "external_deps": [],
+        "estimated_loc": 150
+      }
     ]
```

**Diff 2: config/_schema.yaml**
```diff
--- a/config/_schema.yaml
+++ b/config/_schema.yaml
@@ -12,6 +12,14 @@
   blog_posts:
     fields: [...]

+  comments:
+    description: "Comment system configuration"
+    fields:
+      - name: "max_comment_length"
+        type: "int"
+        default: 1000
+      - name: "moderation_enabled"
+        type: "bool"
+        default: false
```

**Diff 3: requirements.txt**
```diff
--- a/requirements.txt
+++ b/requirements.txt
@@ -2,3 +2,4 @@
 pillow==10.0.0
 pyyaml==6.0
 requests==2.31.0
+(no changes - comments needs no external deps)
```

---

## SUCCESS CRITERIA

- ✅ Diffs are minimal and surgical
- ✅ Context lines included (3 before/after)
- ✅ Each diff has an explanation
- ✅ No full file regeneration
- ✅ Changes are reversible
