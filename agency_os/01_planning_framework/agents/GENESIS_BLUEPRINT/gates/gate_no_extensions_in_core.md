# Validation Gate: No Extensions in Core

**GATE ID:** gate_no_extensions_in_core
**TRIGGER:** After task_02_design_extensions
**SEVERITY:** CRITICAL (blocks if failed)

---

## RULE

Core modules MUST NOT contain feature-specific logic. Core is for **shared, reusable utilities only**.

---

## VALIDATION PROCESS

```python
def validate_no_extensions_in_core(core_modules, extensions):
    """Ensure core modules don't contain extension-specific logic."""
    violations = []

    # Get feature names from extensions
    feature_names = {ext.feature_id for ext in extensions}

    for core_module in core_modules:
        # Check if core module name or purpose mentions features
        for feature_id in feature_names:
            if feature_id in core_module.name or feature_id in core_module.purpose:
                violations.append({
                    "core_module": core_module.name,
                    "feature_id": feature_id,
                    "error": f"Core module '{core_module.name}' appears to be feature-specific (mentions '{feature_id}')"
                })

        # Check if core module is only used by ONE extension
        if len(core_module.used_by) == 1:
            violations.append({
                "core_module": core_module.name,
                "used_by": core_module.used_by[0],
                "error": f"Core module '{core_module.name}' only used by one extension - should be IN that extension"
            })

    return violations
```

---

## ERROR MESSAGE TEMPLATE

If violation detected:

```
❌ VALIDATION FAILED: No Extensions in Core Rule

Core Module: {core_module_name}
Problem: {violation_type}

Core modules should contain SHARED logic used by multiple features.
Feature-specific logic belongs in Extensions.

**FIX:**
- If only used by one extension: Move this to that extension's code
- If mentions feature name: Rename to generic name (e.g., "pdf_parser" not "invoice_pdf_parser")

Example:
  - BAD: core/invoice_validator.py (feature-specific)
  - GOOD: core/validation.py with generic validators

  - BAD: core/user_auth.py used only by 'user_login' extension
  - GOOD: Move to extensions/user_login/auth.py
```

---

## EXAMPLE VALIDATION

### ✅ PASS
```json
{
  "core_modules": [
    {
      "name": "validation",
      "purpose": "Generic validation utilities (email, phone, etc.)",
      "used_by": ["user_registration", "user_login", "booking_form"]
    },
    {
      "name": "storage",
      "purpose": "Database CRUD operations (generic)",
      "used_by": ["user_registration", "booking_manager", "payment_handler"]
    }
  ]
}
```
All core modules are generic and used by multiple extensions.

### ❌ FAIL - Feature-Specific Core
```json
{
  "core_modules": [
    {
      "name": "booking_calculator",
      "purpose": "Calculate booking prices",
      "used_by": ["booking_form", "booking_confirmation"]
    }
  ]
}
```
**Error:** Core module is feature-specific (booking logic)
**Fix:** This is booking-specific logic → should be in extensions/booking_manager/

### ❌ FAIL - Only One User
```json
{
  "core_modules": [
    {
      "name": "pdf_generator",
      "purpose": "Generate PDF invoices",
      "used_by": ["invoice_generator"]
    }
  ]
}
```
**Error:** Only used by one extension
**Fix:** Move to extensions/invoice_generator/pdf_utils.py

---

## WHY THIS MATTERS

**Keeping Core clean ensures:**
- Core stays small and focused (easier to understand/test)
- Features are self-contained (no hidden dependencies)
- Easy to remove features (just delete extension)
- Clear separation (Core = infrastructure, Extensions = features)

**If you put extensions in Core:**
- Core becomes bloated
- Hard to remove features (logic scattered)
- Violates Genesis pattern (Core should be minimal)
- Creates hidden coupling

---

## CORE MODULE CRITERIA

A module belongs in Core if:
- ✅ Used by **3+ extensions**
- ✅ Generic/reusable (not feature-specific)
- ✅ Infrastructure-level (storage, validation, error handling)
- ✅ No business logic (just utilities)

A module belongs in Extension if:
- ✅ Used by **1-2 extensions** (or just one)
- ✅ Feature-specific logic
- ✅ Business rules
- ✅ Workflow/orchestration

---

## EXAMPLES

### Good Core Modules:
- `core/validation.py` - Email, phone, URL validators (used by many)
- `core/storage.py` - Generic CRUD operations (used by many)
- `core/error.py` - Error handling utilities (used by all)
- `core/config.py` - Configuration loading (used by all)

### Bad Core Modules (should be Extensions):
- `core/booking_logic.py` - Feature-specific
- `core/payment_processor.py` - Feature-specific
- `core/invoice_generator.py` - Feature-specific
- `core/user_dashboard.py` - Feature-specific
