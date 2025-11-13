# Validation Gate: All Features Mapped

**GATE ID:** gate_all_features_mapped
**TRIGGER:** After task_02_design_extensions
**SEVERITY:** CRITICAL (blocks if failed)

---

## RULE

**Every feature** from `feature_spec.json` MUST have **exactly one** corresponding extension.

**1:1 mapping required.** No orphaned features, no missing extensions.

---

## VALIDATION PROCESS

```python
def validate_all_features_mapped(feature_spec, extensions):
    """Ensure every feature has one extension, and vice versa."""
    violations = []

    # Get feature IDs from spec
    feature_ids = {f.id for f in feature_spec.features}

    # Get feature IDs from extensions
    extension_feature_ids = {ext.feature_id for ext in extensions}

    # Check for unmapped features (in spec, but no extension)
    unmapped_features = feature_ids - extension_feature_ids
    for feature_id in unmapped_features:
        feature = next(f for f in feature_spec.features if f.id == feature_id)
        violations.append({
            "type": "UNMAPPED_FEATURE",
            "feature_id": feature_id,
            "feature_name": feature.name,
            "error": f"Feature '{feature.name}' (ID: {feature_id}) has no extension"
        })

    # Check for orphaned extensions (extension exists, but no feature)
    orphaned_extensions = extension_feature_ids - feature_ids
    for feature_id in orphaned_extensions:
        ext = next(e for e in extensions if e.feature_id == feature_id)
        violations.append({
            "type": "ORPHANED_EXTENSION",
            "extension_name": ext.name,
            "feature_id": feature_id,
            "error": f"Extension '{ext.name}' maps to feature '{feature_id}' which doesn't exist in spec"
        })

    # Check for duplicate mappings (multiple extensions for one feature)
    from collections import Counter
    feature_counts = Counter(ext.feature_id for ext in extensions)
    duplicates = {fid: count for fid, count in feature_counts.items() if count > 1}

    for feature_id, count in duplicates.items():
        ext_names = [e.name for e in extensions if e.feature_id == feature_id]
        violations.append({
            "type": "DUPLICATE_MAPPING",
            "feature_id": feature_id,
            "extensions": ext_names,
            "error": f"Feature '{feature_id}' has {count} extensions: {ext_names}. Must be exactly 1."
        })

    return violations
```

---

## ERROR MESSAGE TEMPLATE

### Unmapped Feature
```
❌ VALIDATION FAILED: All Features Mapped

Type: UNMAPPED_FEATURE
Feature: {feature_name} (ID: {feature_id})

This feature exists in feature_spec.json but has no corresponding extension.

**FIX:** Create an extension for this feature in task_02_design_extensions.

Example:
  If feature_id = "F003" (User Login):
  Create extension:
  {
    "name": "user_login",
    "feature_id": "F003",
    "purpose": "Handle user authentication",
    ...
  }
```

### Orphaned Extension
```
❌ VALIDATION FAILED: All Features Mapped

Type: ORPHANED_EXTENSION
Extension: {extension_name}
Feature ID: {feature_id}

This extension references a feature that doesn't exist in feature_spec.json.

**FIX:** Either:
  1. Remove this extension (if not needed)
  2. Update feature_id to match an existing feature
  3. Add missing feature to feature_spec.json (then restart workflow)
```

### Duplicate Mapping
```
❌ VALIDATION FAILED: All Features Mapped

Type: DUPLICATE_MAPPING
Feature ID: {feature_id}
Extensions: {extension_names}

Multiple extensions map to the same feature. Must be exactly 1:1.

**FIX:** Merge these extensions into a single extension.

Example:
  If you have:
  - extension: "user_login_frontend" (feature_id: "F003")
  - extension: "user_login_backend" (feature_id: "F003")

  **Merge into:**
  - extension: "user_login" (feature_id: "F003")
    - Contains both frontend and backend logic
```

---

## EXAMPLE VALIDATION

### ✅ PASS
```json
{
  "feature_spec": {
    "features": [
      {"id": "F001", "name": "User Registration"},
      {"id": "F002", "name": "User Login"},
      {"id": "F003", "name": "Booking System"}
    ]
  },

  "extensions": [
    {"name": "user_registration", "feature_id": "F001"},
    {"name": "user_login", "feature_id": "F002"},
    {"name": "booking_manager", "feature_id": "F003"}
  ]
}
```
**Result:** Perfect 1:1 mapping. All 3 features have extensions.

### ❌ FAIL - Unmapped Feature
```json
{
  "feature_spec": {
    "features": [
      {"id": "F001", "name": "User Registration"},
      {"id": "F002", "name": "User Login"},
      {"id": "F003", "name": "Payment Processing"}
    ]
  },

  "extensions": [
    {"name": "user_registration", "feature_id": "F001"},
    {"name": "user_login", "feature_id": "F002"}
  ]
}
```
**Error:** Feature F003 (Payment Processing) has no extension.
**Fix:** Add `payment_handler` extension for F003.

### ❌ FAIL - Orphaned Extension
```json
{
  "feature_spec": {
    "features": [
      {"id": "F001", "name": "User Registration"}
    ]
  },

  "extensions": [
    {"name": "user_registration", "feature_id": "F001"},
    {"name": "admin_dashboard", "feature_id": "F999"}
  ]
}
```
**Error:** Extension 'admin_dashboard' references F999 which doesn't exist.
**Fix:** Either remove extension or add F999 to feature_spec.

### ❌ FAIL - Duplicate Mapping
```json
{
  "feature_spec": {
    "features": [
      {"id": "F001", "name": "User Management"}
    ]
  },

  "extensions": [
    {"name": "user_create", "feature_id": "F001"},
    {"name": "user_update", "feature_id": "F001"},
    {"name": "user_delete", "feature_id": "F001"}
  ]
}
```
**Error:** 3 extensions map to F001.
**Fix:** Merge into single "user_management" extension.

---

## WHY THIS MATTERS

**1:1 mapping ensures:**
- Complete feature coverage (nothing forgotten)
- No redundant extensions (no waste)
- Clear traceability (feature → extension → code)
- Easy validation (can check completeness)

**If mapping is broken:**
- Features might not get implemented (unmapped)
- Extensions with no purpose (orphaned)
- Confusion about what each extension does (duplicates)
- Can't validate architecture completeness

---

## SPECIAL CASES

### Multi-Feature Extensions (NOT ALLOWED)

**Bad:**
```json
{
  "name": "user_system",
  "feature_id": ["F001", "F002", "F003"]
}
```

**Why Bad:** One extension can't map to multiple features.

**Fix:** Split into separate extensions:
- `user_registration` (F001)
- `user_login` (F002)
- `user_profile` (F003)

### Sub-Features (Allowed)

If feature has sub-tasks, they still map to ONE extension:

```json
{
  "feature_spec": {
    "features": [{
      "id": "F001",
      "name": "Booking System",
      "sub_features": ["create booking", "cancel booking", "view bookings"]
    }]
  },

  "extensions": [{
    "name": "booking_manager",
    "feature_id": "F001",
    "handles_all_sub_features": true
  }]
}
```

**Still 1:1:** One feature (with sub-features) → One extension.

---

## CHECKLIST

Before passing this gate, verify:

- [ ] Every feature in feature_spec.json has an extension
- [ ] Every extension maps to a valid feature
- [ ] No feature has multiple extensions
- [ ] Feature IDs match exactly (case-sensitive)
- [ ] No typos in feature_id references
