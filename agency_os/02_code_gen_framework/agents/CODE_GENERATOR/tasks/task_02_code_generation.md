# Task: Code Generation

## Objective
Generate production-ready source code for all modules and API endpoints specified in the validated code_gen_spec.json.

---

## Goal
Transform specification into functional, well-structured source code following the Genesis Core Pattern.

---

## Input Artifacts
- `validation_result.json` (from Task 01)
- `code_gen_spec.json`
- `CODE_GEN_quality_rules.yaml` (from knowledge base)

---

## Process

### Step 1: Module Generation
Based on `architectureRef` and `features` in the spec:
- Generate necessary **Core modules** (stdlib-only, business logic)
- Generate **Extension modules** (feature implementations, external libs allowed)
- Enforce **Genesis Core Pattern**:
  - Extensions → Core (one-way dependency)
  - Extensions never import each other
  - Core never imports Extensions

### Step 2: API Implementation
Implement API endpoints and functions from `apiDefinitions`:
- Parse OpenAPI/REST specifications
- Generate endpoint handlers
- Implement request/response validation
- Add error handling

### Step 3: Contextual Integration
Integrate with existing code from `contextualAwareness`:
- Respect existing project conventions
- Import and use existing modules (`relevantFiles`)
- Match existing code style
- Preserve existing patterns

---

## Code Generation Rules

### Structure:
```
src/
├── core/                    # Core modules (stdlib-only)
│   ├── auth.py
│   └── database.py
├── extensions/              # Feature modules (external libs OK)
│   ├── user_management/
│   └── api_endpoints/
└── config/                  # Configuration (PyYAML allowed)
    └── settings.yaml
```

### Quality Standards:
- **Modularity:** One feature = one extension module
- **Type Hints:** Use Python type annotations everywhere
- **Docstrings:** Every function/class documented
- **Error Handling:** Explicit exception handling (no bare `except`)
- **Security:** No hardcoded secrets, use environment variables

---

## Output

Generated source code structure:

```json
{
  "generated_modules": [
    {
      "file_path": "src/core/auth.py",
      "content": "...",
      "module_type": "core",
      "dependencies": ["hashlib", "os"]
    },
    {
      "file_path": "src/extensions/user_management/user_service.py",
      "content": "...",
      "module_type": "extension",
      "dependencies": ["fastapi", "sqlalchemy", "src.core.auth"]
    }
  ],
  "api_endpoints": [
    {
      "path": "/auth/login",
      "method": "POST",
      "handler": "src/extensions/api_endpoints/auth_routes.py::login"
    }
  ]
}
```

---

## Success Criteria

- ✅ All features from spec have corresponding code
- ✅ Genesis Core Pattern enforced
- ✅ All API endpoints implemented
- ✅ Code follows quality rules
- ✅ Contextual integration successful
- ✅ No syntax errors

---

## Validation Gates

- `gate_genesis_pattern_enforced.md` - Ensures Core/Extensions separation
- `gate_all_features_implemented.md` - Ensures no missing features
