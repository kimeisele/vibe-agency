# Task: Generate Final Architecture Output

**PHASE:** 5
**TASK ID:** handoff
**TRIGGER:** validation_result.json available AND fae_passed == true

---

## OBJECTIVE

Combine all previous task outputs into final `architecture.json` and `code_gen_spec.json` for handoff to CODE_GENERATOR.

---

## INPUT ARTIFACTS

### Required:
1. **feature_spec.json** (original input)
2. **core_modules_selection.json** (from task_01)
3. **extensions_design.json** (from task_02)
4. **config_system.json** (from task_03)
5. **validation_result.json** (from task_04)

---

## OUTPUT GENERATION

### 1. architecture.json (Complete architecture specification)

```json
{
  "genesis_architecture": {
    "project": {
      "name": "from feature_spec",
      "category": "from feature_spec",
      "scale": "from feature_spec",
      "version": "v1.0"
    },

    "core_modules": [
      // FROM task_01: core_modules_selection.json
      {
        "name": "io",
        "purpose": "File I/O for CSV, JSON, images",
        "why_core": "Needed by 3 features: feature_1, feature_2, feature_3",
        "dependencies": ["pathlib", "csv", "json"],
        "used_by": ["feature_1_extension", "feature_2_extension"],
        "api": [...],
        "estimated_loc": 120,
        "test_coverage_target": "100%",
        "file_path": "core/io.py"
      }
    ],

    "extensions": [
      // FROM task_02: extensions_design.json
      {
        "name": "feature_1_extension",
        "purpose": "Feature 1 description",
        "implements_feature": "feature_1",
        "uses_core": ["io", "config", "validation"],
        "external_deps": ["pillow"],
        "why_external_dep": "Image manipulation not in stdlib",
        "api": [...],
        "estimated_loc": 200,
        "test_coverage_target": "90%",
        "file_path": "extensions/feature_1_extension.py"
      }
    ],

    "config_system": {
      // FROM task_03: config_system.json
      "mandatory": true,
      "reason": "Project is production-ready",
      "schema_location": "config/_schema.yaml",
      "schema": {...}
    },

    "directory_structure": {
      // FROM task_03: config_system.json
      "root": "{project_name}/",
      "core": "core/ (Foundation modules, stdlib only except config)",
      "extensions": "extensions/ (Feature implementations)",
      ...
    },

    "dependencies": {
      "core": ["pyyaml"],  // Only if config module exists
      "extensions": ["pillow", "requests", ...]
    },

    "validation": {
      // FROM task_04: validation_result.json
      "fae_passed": true,
      "checks": [...]
    }
  },

  "implementation_guide": {
    "build_order": [
      "1. Create directory structure",
      "2. Implement core modules (bottom-up: schema → entity → ...)",
      "3. Write unit tests for each core module",
      "4. Create config schema + example configs",
      "5. Implement extensions (one at a time, test each)",
      "6. Wire up entry points (main.py, cli.py)",
      "7. Integration tests",
      "8. Documentation"
    ],
    "estimated_time": "8-12 hours for v1.0",
    "next_steps": [
      "1. Generate directory structure: mkdir -p {project_name}/{core,extensions,config,tests}",
      "2. Start with core/schema.py (define data models)",
      "3. Follow build_order above",
      "4. Use GENESIS_UPDATE for any changes after initial build"
    ]
  },

  "metadata": {
    "genesis_version": "6.0",
    "created_at": "2025-11-12T...",
    "input_source": "VIBE_ALIGNER v3.0",
    "fae_validation": "passed"
  }
}
```

### 2. code_gen_spec.json (Input for CODE_GENERATOR)

This is a transformation of architecture.json into the format expected by CODE_GENERATOR.

```json
{
  "project_id": "from feature_spec",
  "architecture_source": "GENESIS_BLUEPRINT v6.0",

  "modules_to_generate": [
    {
      "module_type": "core",
      "name": "io",
      "file_path": "core/io.py",
      "purpose": "File I/O operations",
      "api": [...],
      "dependencies": ["pathlib", "csv", "json"],
      "test_coverage_target": 100
    },
    {
      "module_type": "extension",
      "name": "feature_1_extension",
      "file_path": "extensions/feature_1_extension.py",
      "purpose": "...",
      "api": [...],
      "uses_core": ["io", "config"],
      "external_deps": ["pillow"],
      "test_coverage_target": 90
    }
  ],

  "config_files": [
    {
      "file_path": "config/_schema.yaml",
      "content": "..."
    },
    {
      "file_path": "config/config.yaml",
      "content": "..."
    }
  ],

  "entry_points": [
    {
      "file_path": "main.py",
      "purpose": "Main entry point"
    }
  ],

  "quality_gates": {
    "min_test_coverage": 80,
    "linting": true,
    "type_hints": true
  }
}
```

---

## SUCCESS MESSAGE

After generating outputs, display success message:

```
✅ GENESIS ARCHITECTURE COMPLETE

Project: {project_name}
Core Modules: {count}
Extensions: {count}
Estimated Build Time: {estimated_time}

Architecture outputs:
- architecture.json (Human-readable specification)
- code_gen_spec.json (CODE_GENERATOR input)

Next step: CODE_GENERATOR will implement the architecture.

Use GENESIS_UPDATE for any changes after initial build.
```

---

## EXECUTION INSTRUCTIONS

1. Load all input artifacts
2. Verify validation_result.fae_passed == true
3. Combine all artifacts into architecture.json
4. Transform architecture.json into code_gen_spec.json
5. Write both files to artifacts/planning/
6. Display success message
7. Mark PLANNING phase complete

**This is the final handoff to CODE_GENERATOR.**
